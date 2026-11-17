-- Preserve table layout and contain wide tables within a keyboard-scrollable region.
function Table(table)
  if quarto.doc.is_format("html") then
    -- Pipe tables receive equal inferred widths from Pandoc. Clear those
    -- hints so the browser can size columns from their contents.
    local uniform_widths = true
    local first_width = table.colspecs[1] and table.colspecs[1][2]
    for _, colspec in ipairs(table.colspecs) do
      if colspec[2] ~= first_width then
        uniform_widths = false
        break
      end
    end

    if uniform_widths then
      for i, colspec in ipairs(table.colspecs) do
        table.colspecs[i] = {colspec[1], nil}
      end
    end

    return pandoc.Div({table}, pandoc.Attr("", {"table-scroll"}, {
      {"style", "--table-columns: " .. #table.colspecs},
      {"role", "region"},
      {"aria-label", "Scrollable table"},
      {"tabindex", "0"}
    }))
  end
end
