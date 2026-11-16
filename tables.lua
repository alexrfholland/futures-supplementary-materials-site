-- Preserve table layout and contain wide tables within a keyboard-scrollable region.
function Table(table)
  if quarto.doc.is_format("html") then
    return pandoc.Div({table}, pandoc.Attr("", {"table-scroll"}, {
      {"style", "--table-columns: " .. #table.colspecs},
      {"role", "region"},
      {"aria-label", "Scrollable table"},
      {"tabindex", "0"}
    }))
  end
end
