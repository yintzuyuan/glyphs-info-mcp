## [Info Box](#info-box)

An Info box is displayed below the current glyph.
The current glyph is the glyph currently being edited on, or, in text mode, the glyph following the text cursor.
The Info box shows general information about the glyph, including as its name, Unicode value, metrics, and kerning.

![](https://handbook.glyphsapp.com/v/content/images/root/info-box-horizontal.svg)

The glyph name is shown centered at the top of the Info box.
Its Unicode value, if any, is shown in the top-right of the box.

![](https://handbook.glyphsapp.com/v/content/images/root/unicodechecker.png)

[*UnicodeChecker*](https://earthlingsoft.net/UnicodeChecker) is a Mac app by earthlingsoft.
Use it to explore and convert Unicode values.

Click the arrow ![](https://handbook.glyphsapp.com/v/content/icons/follow-link.svg) button next to the Unicode value to open it in UnicodeChecker.
If UnicodeChecker is not installed, Glyphs will present a download link.
When opening UnicodeChecker with the arrow button for the first time, the Mac will ask for permission.
Grant it so that Glyphs can launch UnicodeChecker and set the current Unicode value to match the one from Edit View.

### [Horizontal Layout](#info-box/horizontal-layout)

The lower half of the glyph Info box manages metrics and kerning.
To the left and right of the horizontal metrics ![](https://handbook.glyphsapp.com/v/content/icons/metrics-horizontal.svg) icon are left and right sidebearings.
Below the icon is the width of the glyph.
LSB, RSB, and width values can be numbers or metrics keys.
See [Metrics Keys](https://handbook.glyphsapp.com/single-page/#metrics-keys "Spacing & Kerning ⯈ Spacing ⯈ Metrics Keys") for more details.

Kerning values and kerning groups are at the left and right edge of the Info box.
See [Kerning](https://handbook.glyphsapp.com/single-page/#kerning "Spacing & Kerning ⯈ Kerning") for more information.

### [Vertical Layout](#info-box/vertical-layout)

For glyphs written in a [vertical layout](https://handbook.glyphsapp.com/single-page/#writing-direction "Edit View ⯈ Entering Text ⯈ Writing Direction"), the vertical Info box is displayed instead.

![](https://handbook.glyphsapp.com/v/content/images/root/info-box-vertical.svg)

`T` and `B` are the top and bottom sidebearings of the glyph, respectively.
`O` is the vertical origin of the glyph.

`H` is the vertical width (or height) of the glyph.
`K` and `G` define the kerning and kerning groups, both for the top and the bottom of the glyph.