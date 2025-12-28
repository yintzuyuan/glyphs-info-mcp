## [Working with Color Fonts](#color-fonts/general)

Color fonts make use of multiple layers per glyph.
See [Editing Multiple Masters](https://handbook.glyphsapp.com/single-page/#editing-multiple-masters "Interpolation ⯈ Editing Multiple Masters") for general information on working with multiple layers.

### [Keeping the Metrics in Sync](#color-fonts/keeping-the-metrics-in-sync)

When working on a color font project, masters must share the same metrics and kerning pairs so that all color layers align.
Use the `Link Metrics With First Master` custom parameter in `File → Font Info… → Masters` to sync the metrics and kerning of the first master with all masters.
Add this custom parameter to every master except the first one.
Alternatively, add the `Link Metrics With Master` custom parameter, which can be linked to any other master, not just the first one.

### [Previewing Color Fonts](#color-fonts/previewing)

Edit View shows colors for other glyphs when a color layer is selected in the current glyph.
The Preview area at the bottom of Edit View (activated with the eye ![](https://handbook.glyphsapp.com/v/content/icons/preview-eye.svg) button) and the Preview Panel (`Window → Preview Panel`) display a glyph in color when one of its color layers is selected.
The Text Preview (`Window → Text Preview`) displays the font as it would appear in Mac applications using Core Text (such as Text Edit or Pages).

### [Exporting Color Fonts](#color-fonts/exporting)

Color fonts are regular OpenType fonts.
They are compatible with all OpenType flavors supported by Glyphs: PostScript/CFF (`.otf`), TrueType (`.ttf`), and WOFF/WOFF2.
However, color fonts only work in environments that support their display.
For instance, layered color fonts only work in applications that can put pieces of text precisely on top of each other, like most DTP software.