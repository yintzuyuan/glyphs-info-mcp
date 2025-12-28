## [Viewing Glyphs](#viewing-glyphs)

Font View is available in two viewing modes: Grid View and List View.
Toggle between the modes with the grid ![](https://handbook.glyphsapp.com/v/content/icons/grid-view.svg) and list ![](https://handbook.glyphsapp.com/v/content/icons/list-view.svg) buttons in the top-left of the font window.

### [Grid View](#grid-view)

![](https://handbook.glyphsapp.com/v/content/images/root/font-view-grid.png)

In Grid View ![](https://handbook.glyphsapp.com/v/content/icons/grid-view.svg), the glyphs of the font are displayed in a grid of glyph cells.
The glyph outlines reflect the currently selected master.
Use the slider ![](https://handbook.glyphsapp.com/v/content/icons/slider.svg) in the bottom-right to control the cell size.
Large glyph cells display the glyph outlines, the glyph name, and the Unicode value of the glyph.
Small cells show only the outlines.

![](https://handbook.glyphsapp.com/v/content/images/root/glyph-cell.svg)

The Unicode value is shown in the bottom-right next to the glyph name.
By default, a small Unicode indicator ![](https://handbook.glyphsapp.com/v/content/icons/unicode-indicator.svg) is displayed.
The Unicode indicator is replaced by a small rendering of the glyph set in the system font for CJK glyphs.
Enable `Display Unicode Value` [in settings](https://handbook.glyphsapp.com/single-page/#settings/appearance "Settings ⯈ Appearance") to show the full Unicode value.
Alternatively, select a glyph cell to show its Unicode values in the inspector located in the bottom-left of the window (see [Unicode](https://handbook.glyphsapp.com/single-page/#glyph/unicode "Font View ⯈ Glyph Properties ⯈ Unicode") for details).

A warning ![](https://handbook.glyphsapp.com/v/content/icons/alert.svg) triangle in the top-right corner of a glyph cell indicates that the glyph has [out-of-sync metrics keys](https://handbook.glyphsapp.com/single-page/#metrics-keys "Spacing & Kerning ⯈ Spacing ⯈ Metrics Keys").
A yellow note ![](https://handbook.glyphsapp.com/v/content/icons/note-glyph-cell-indicator.svg) indicates that the glyph has an annotation on the active master layer.
A black info ![i](https://handbook.glyphsapp.com/v/content/icons/info-indicator.svg) indicates that the glyph uses [custom glyph properties](https://handbook.glyphsapp.com/single-page/#glyph "Font View ⯈ Glyph Properties").
A red top-left corner ![](https://handbook.glyphsapp.com/v/content/icons/non-interpolatable-glyph-cell-indicator.svg) in a glyph cell indicates that [not all layers are compatible for interpolation](https://handbook.glyphsapp.com/single-page/#interpolation/outline-compatibility "Interpolation ⯈ Outline Compatibility").
A red ring with stroke ![](https://handbook.glyphsapp.com/v/content/icons/non-exporting-glyph-indicator.svg) marks a [non-exporting glyph](https://handbook.glyphsapp.com/single-page/#exports "Font Info ⯈ Exports").

A glyph cell displays its [glyph and layer colors](https://handbook.glyphsapp.com/single-page/#glyph-and-layer-colors "Edit View ⯈ Glyph Display ⯈ Glyph & Layer Colors").

### [List View](#list-view)

![](https://handbook.glyphsapp.com/v/content/images/root/font-view-list.png)

Switch to List View by selecting the list ![](https://handbook.glyphsapp.com/v/content/icons/list-view.svg) icon located in the top-left of the font window.
List View shows a table where each row corresponds to a glyph and each column to a glyph property.
Click a column header to sort by that column.
Click a header again to reverse the sort order.
Click and drag a column header to rearrange columns.
`Control`-click or right-click a header to hide or show columns.
See [Glyph Properties](https://handbook.glyphsapp.com/single-page/#glyph "Font View ⯈ Glyph Properties") for a description of all glyph properties.