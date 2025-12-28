## [Layers](#palette/layers)

A layer contains the outline of a glyph.
A single glyph can have multiple layers, at least one for each master.

![](https://handbook.glyphsapp.com/v/content/images/root/palette-layers.svg)

Layers are shown in the `Layers` section of the Palette.
The layers are sorted by their master.
Drag the handle at the bottom of the `Layers` section to resize it.
Click the eye symbol ![](https://handbook.glyphsapp.com/v/content/icons/invisible.svg) next to a layer to toggle its display.
A visible ![](https://handbook.glyphsapp.com/v/content/icons/visible.svg) layer is displayed with a faint blue line when a different layer of the glyph is active.
Change the color [in the settings](https://handbook.glyphsapp.com/single-page/#settings/appearance "Settings ⯈ Appearance").
Use the [Select All Layers tool](https://handbook.glyphsapp.com/single-page/#select-all-layers-tool "Interpolation ⯈ Editing Multiple Masters ⯈ Select All Layers Tool") ![](https://handbook.glyphsapp.com/v/content/icons/select-all-tool.svg) (shortcut `Shift-V`) to edit all visible layers at once.

`Shift`-click to select a range of layers, or `Command`-click to make a non-contiguous selection.
Reorder layers by dragging a layer to a new position.
Layers can only be reordered within a master.

Glyphs differentiates between three types of layers: *master* layers, *backup* layers, and *special* layers.

### [Master Layers](#master-layers)

Master layers are required for [interpolating](https://handbook.glyphsapp.com/single-page/#interpolation "Interpolation") instances.
Every glyph has a master layer for every font master.
In the `Layers` palette, master layers are labeled with the master name and are set in bold.
Master layers cannot be added, deleted, or renamed from the `Layers` section.
Instead, open `File → Font Info… → Masters` to manage font masters.

Choose `Only Show Layers from Current Master` from the filter ![](https://handbook.glyphsapp.com/v/content/icons/filter.svg) menu to hide all layers not belonging to the current master.
This option can clean up the layers list and is particularly helpful when working on fonts with many masters.

### [Backup Layers](#backup-layers)

Backup layers are used to keep a copy of previous drawings.
Click the plus ![](https://handbook.glyphsapp.com/v/content/icons/plus.svg) button in the bottom-left of the `Layers` section to create a new backup layer.
By default, a backup layer is labeled with its creation date and time.
Double-click the layer name to rename it.
Click the minus ![](https://handbook.glyphsapp.com/v/content/icons/minus.svg) button to delete the selected layer.
Backup layers are indented below their master layer and set in a regular weight.
A glyph can have any number of backup layers.
Choose `Hide Backup Layers` from the filter ![](https://handbook.glyphsapp.com/v/content/icons/filter.svg) menu to hide all backup layers.

Revert to a backup layer by choosing `Use as Master` from the actions ![](https://handbook.glyphsapp.com/v/content/icons/actions.svg) menu.
The backup layer will be deleted, its contents will be placed on the master layer, and the contents of the current master layer will be placed on a new backup layer.
Alternatively, drag a backup layer onto a master layer to use it instead as a master layer.

### [Special Layers](#special-layers)

Special layers can be intermediate and alternate layers for interpolation or any kind of color layer.
Special layers are indented below their master layer.
The label reflects their type and is set in bold.

Intermediate and alternate layers are used in [Multiple Master setups](https://handbook.glyphsapp.com/single-page/#interpolation "Interpolation").
Color layers are used for [color fonts](https://handbook.glyphsapp.com/single-page/#color-fonts "Color Fonts").
Plug-ins may define their own special layers.
Refer to their documentation for more information.