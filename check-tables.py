"""Check that every Markdown pipe table renders with its rows and columns intact."""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "_site"
SEPARATOR = re.compile(r"^\s*\|?\s*:?\-+:?\s*(?:\|\s*:?\-+:?\s*)+\|?\s*$")
FRONTMATTER_DELIMITER = re.compile(r"^\s*(?:---|\.\.\.)\s*$")
COLLAPSED_LIST_MARKER = re.compile(r":\s*[-*+]\s+\S")
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


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


class RenderedParagraphs(HTMLParser):
    """Collect paragraph text while skipping code and math spans."""

    def __init__(self):
        super().__init__()
        self.paragraphs = []
        self.current = None
        self.skipped_tags = []

    def handle_starttag(self, tag, attributes):
        classes = set(dict(attributes).get("class", "").split())
        if self.skipped_tags:
            if tag not in VOID_TAGS:
                self.skipped_tags.append(tag)
            return
        if self.current is None and tag == "p":
            self.current = []
        elif self.current is not None and (
            tag in {"code", "pre", "script", "style"} or "math" in classes
        ):
            self.skipped_tags.append(tag)

    def handle_endtag(self, tag):
        if self.skipped_tags:
            if tag in self.skipped_tags:
                del self.skipped_tags[len(self.skipped_tags) - 1 - self.skipped_tags[::-1].index(tag):]
            return
        if tag == "p" and self.current is not None:
            self.paragraphs.append("".join(self.current))
            self.current = None

    def handle_data(self, data):
        if self.current is not None and not self.skipped_tags:
            self.current.append(data)


sources = [ROOT / "index.qmd", *sorted((ROOT / "appendices").glob("*.qmd"))]
if not sources[0].is_file():
    raise SystemExit("Missing index.qmd")
missing_sources = [source.name for source in sources if not source.is_file()]
if missing_sources:
    raise SystemExit(f"Missing expected source pages: {', '.join(missing_sources)}")
if len(sources) != 16:
    raise SystemExit(f"Expected index.qmd, 12 appendices and 3 pathway submodules, found {len(sources)} files.")

total = 0
for source in sources:
    rendered_path = SITE / source.relative_to(ROOT).with_suffix(".html")
    if not rendered_path.is_file():
        raise SystemExit(f"Missing rendered page: {rendered_path.relative_to(ROOT)}")
    expected = source_tables(source.read_text(encoding="utf-8"))
    rendered = RenderedTables()
    html = rendered_path.read_text(encoding="utf-8")
    rendered.feed(html)
    if expected != rendered.tables:
        raise SystemExit(
            f"Table rendering differs in {source.name}:\n"
            f"Expected rows/columns: {expected}\nRendered rows/columns: {rendered.tables}"
        )
    paragraphs = RenderedParagraphs()
    paragraphs.feed(html)
    for paragraph in paragraphs.paragraphs:
        if COLLAPSED_LIST_MARKER.search(paragraph):
            raise SystemExit(
                f"Possible collapsed Markdown list in {source.name}: "
                f"{paragraph[:180].strip()}"
            )
    total += len(expected)

print(f"Verified {total} tables, including every row and column.")
