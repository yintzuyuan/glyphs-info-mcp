## [Glyph Order](#glyph-order)

Categories, languages, and filters do not influence the glyphs order in the exported font.
Instead, glyphs are ordered by their [sort name](https://handbook.glyphsapp.com/single-page/#glyph/sort-name "Font View ⯈ Glyph Properties ⯈ Sort Name").
Define a custom order for all glyphs of the font with the `glyphOrder` custom parameter in `File → Font Info… → Font` (`Cmd-I`).
The parameter takes a list of glyph names, one name per line.
The order of glyphs is used both in Font View and in exported font files.

When opening an OTF or TTF font file, Glyphs preserves the glyph order of the file by automatically adding a `glyphOrder` custom parameter when `Keep Glyph Names from Imported Files` is selected.
See [User Settings](https://handbook.glyphsapp.com/single-page/#settings/user-settings "Settings ⯈ User Settings") for details.