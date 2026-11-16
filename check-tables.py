"""Check that every Markdown pipe table renders with its rows and columns intact."""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "_site"
SEPARATOR = re.compile(r"^\s*\|?\s*:?\-+:?\s*(?:\|\s*:?\-+:?\s*)+\|?\s*$")
FRONTMATTER_DELIMITER = re.compile(r"^\s*(?:---|\.\.\.)\s*$")


def cells(line):
    parts = re.split(r"(?<!\\)\|", line.strip())
    if not parts[0]:
        parts.pop(0)
    if not parts[-1]:
        parts.pop()
    return len(parts)


def source_tables(text):
    lines = text.splitlines()
    tables = []
    fence = None
    in_frontmatter = bool(lines and FRONTMATTER_DELIMITER.fullmatch(lines[0]) and lines[0].strip() == "---")
    for index, line in enumerate(lines):
        if in_frontmatter:
            if index and FRONTMATTER_DELIMITER.fullmatch(line):
                in_frontmatter = False
            continue

        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            character = marker.group(1)[0]
            fence = None if fence == character else character
            continue
        if fence or not SEPARATOR.fullmatch(line):
            continue

        shape = [cells(lines[index - 1])]
        for row in lines[index + 1:]:
            if not row.lstrip().startswith("|"):
                break
            shape.append(cells(row))
        tables.append(shape)
    return tables


class RenderedTables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.current = None
        self.row = None

    def handle_starttag(self, tag, attributes):
        if tag == "table":
            self.current = []
        elif tag == "tr" and self.current is not None:
            self.row = 0
        elif tag in {"th", "td"} and self.row is not None:
            self.row += int(dict(attributes).get("colspan", "1"))

    def handle_endtag(self, tag):
        if tag == "tr" and self.row is not None:
            self.current.append(self.row)
            self.row = None
        elif tag == "table" and self.current is not None:
            self.tables.append(self.current)
            self.current = None


sources = [ROOT / "index.qmd", *sorted(ROOT.glob("appendix_*.qmd"))]
if not sources[0].is_file():
    raise SystemExit("Missing index.qmd")
if len(sources) != 12:
    raise SystemExit(f"Expected index.qmd and 11 appendix .qmd files, found {len(sources)} files.")

total = 0
for source in sources:
    rendered_path = SITE / source.with_suffix(".html").name
    if not rendered_path.is_file():
        raise SystemExit(f"Missing rendered page: {rendered_path.relative_to(ROOT)}")
    expected = source_tables(source.read_text(encoding="utf-8"))
    rendered = RenderedTables()
    rendered.feed(rendered_path.read_text(encoding="utf-8"))
    if expected != rendered.tables:
        raise SystemExit(
            f"Table rendering differs in {source.name}:\n"
            f"Expected rows/columns: {expected}\nRendered rows/columns: {rendered.tables}"
        )
    total += len(expected)

print(f"Verified {total} tables, including every row and column.")
