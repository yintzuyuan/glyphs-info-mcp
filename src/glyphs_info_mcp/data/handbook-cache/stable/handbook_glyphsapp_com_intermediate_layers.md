## [Intermediate Layers](#intermediate-layers)

Intermediate layers allow adjustments at a designspace location for a single glyph without adding another master.
This helps fix interpolation issues that occur in a single glyph.
For example, consider a two-master setup, *Thin*–*Black*, where the crossbar of the `e` appears too thin in the regular weights:

Interpolation between two masters: without Intermediate layer (above) and with Intermediate layer at the regular weight (below).

![](https://handbook.glyphsapp.com/v/content/images/root/intermediate-layer-demo.svg)

### [Intermediate Layer Setup](#intermediate-layers/setup)

Firstly, select the master layer in the `Layers` palette most similar to the desired Intermediate layer.
Then, click the plus ![](https://handbook.glyphsapp.com/v/content/icons/plus.svg) button in the `Layers` palette to add a new layer.
`Control`-click or right-click the new layer and choose `Intermediate` from the context menu.
A number field for each axis will appear.

![](https://handbook.glyphsapp.com/v/content/images/root/edit-intermediate-layer-settings-popover.png)

Enter the axis coordinates of the Intermediate, similar to how the `Axes Coordinates` work in `File → Font Info… → Masters`.
Use the axis ranges displayed next to the fields for guidance.
If a field is left empty, then the Intermediate layer uses the axis coordinate from the master layer to which it has been added.
This is why adding an Intermediate to the most similar master layer is helpful.
Confirm the entered values by pressing `Return`.

In the `Layers` palette, Intermediate layers are displayed as the comma-separated axis coordinates between curly braces (for example, `{90}` or `{80, 120}`).
This is why Intermediate layers are also referred to as *brace layers*.

### [Virtual Masters](#virtual-masters)

Intermediate layers allow for *virtual masters*.
A virtual master works like a master in `File → Font Info… → Masters`, but it only affects a small number of glyphs.
Other glyphs do not need to be redrawn, and kerning pairs do not need to be defined for virtual masters.
For example, an axis might control the height of crossbars in glyphs such as `A`, `E`, `F`, and `H`.
All other glyphs, including numbers, punctuation, and symbols, are unaffected by this axis, so it is a good candidate for a virtual master.

![](https://handbook.glyphsapp.com/v/content/images/root/axis-location-dialog-virtual-master.png)

Add an axis as described in [Setting up Axes](https://handbook.glyphsapp.com/single-page/#interpolation/axes "Interpolation ⯈ Setting up Axes").
It can be one of the standard axes or a custom axis.
The virtual master is defined using a `Virtual Master` custom parameter in `File → Font Info… → Font`.
Click the value of the custom parameter and set its axis coordinates like any other master.
Confirm the dialog with `OK`.
Note that coordinates for the new axis must be set for the existing masters in `File → Font Info… → Masters`.

With both the axis and the virtual master setup, add Intermediate layers to the glyphs that need to be adjusted for the virtual master.
When exporting to variable fonts, only deltas for these glyphs are stored, which keeps the font file size small.