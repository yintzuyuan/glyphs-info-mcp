## [SVG Color Fonts](#color-fonts/svg)

![](https://handbook.glyphsapp.com/v/content/images/root/color-font-svg-demo.svg)

There used to be an SVG format for fonts, not images.
That SVG format is now obsolete.
The SVG color fonts in this chapter contain SVG images for their glyphs but are still OpenType fonts.

The Scalable Vector Graphics (SVG) image format can contain both vector and bitmap data.
An SVG color font uses SVG files to display glyphs.
SVG color fonts are also referred to as *OpenType-SVG* or *SVG-in-OpenType*.
Glyphs provides three methods for creating SVG color fonts:

- convert a layered color font, `CPAL`/`COLR` font, or `sbix` font to SVG;
- use SVG files created in a graphic design app;
- create the SVG images inside Glyphs.

### [Converting to SVG](#color-fonts/svg/converting-to-svg)

See the respective sections for details on how to convert other color font formats to SVG:

- Layered color fonts: [Layered Color Fonts: Exporting](https://handbook.glyphsapp.com/single-page/#color-fonts/layered/exporting "Color Fonts ⯈ Layered Color Fonts ⯈ Exporting")
- `CPAL`/`COLR` color fonts: [COLR/CPAL Fonts: Exporting](https://handbook.glyphsapp.com/single-page/#color-fonts/colr-cpal/exporting "Color Fonts ⯈ COLR/CPAL Fonts ⯈ Exporting")
- `sbix` color fonts: [sbix Fonts: Exporting](https://handbook.glyphsapp.com/single-page/#color-fonts/sbix/exporting "Color Fonts ⯈ sbix Fonts ⯈ Exporting")

### [Importing Existing SVG Files](#color-fonts/svg/importing-existing-svg-files)

In Edit View, add an SVG layer by clicking the plus ![](https://handbook.glyphsapp.com/v/content/icons/plus.svg) button in the `Layers` palette (`Window → Palette`, `Cmd-Opt-P`) and choose `svg` from the context menu on the layer.

![](https://handbook.glyphsapp.com/v/content/images/root/color-font-svg-bitmap.png)

An SVG image can also contain bitmap data, which may be useful for fonts imitating handwriting (like the [`sbix` format](https://handbook.glyphsapp.com/single-page/#color-fonts/sbix "Color Fonts ⯈ sbix Fonts")).
Drag an SVG file onto the layer to use it for that glyph.

**Tip:**

For clarity, name image files after their glyph name, such as `A.svg` and place them in a folder named `Images`.

When adding SVG images to a Glyphs file, they are not copied into it, but merely referenced.
Moving, renaming, or deleting the SVG files will break these references.
Therefore, it is best practice to place the files in a folder next to the Glyphs file.

Resize and reposition the SVG image on the glyph layer like any other image.
See [Manipulating Images](https://handbook.glyphsapp.com/single-page/#edit-view/images/manipulating "Edit View ⯈ Images ⯈ Manipulating Images").

Changing the width of the master layer also changes the width of its SVG layer.
In case an app cannot handle the SVG data, it shows the master layer.
The master layer is not shown in apps that support SVG color fonts.

### [Creating SVG Glyphs](#color-fonts/svg/creating-svg-glyphs)

SVG glyphs can be created using color layers.
Add a color layer by clicking the plus ![](https://handbook.glyphsapp.com/v/content/icons/plus.svg) button in the `Layers` palette (`Window → Palette`, `Cmd-Opt-P`) and choose `Color` from the context menu on the layer.
Color layers are named `Color` and display a color spectrum ![](https://handbook.glyphsapp.com/v/content/icons/color-layer.svg) disc.

Draw paths on a color layer like on any other layer.
By default, the drawn shapes are filled with a gray color.
Edit the style of the selected paths in the `Attributes` inspector located at the bottom of the Palette (`Window → Palette`, `Cmd-Opt-P`).
Toggle the display of the `Attributes` inspector with `View → Show Info` (`Cmd-Shift-I`).

By default, the `Attributes` inspector contains controls for the stroke and fill of the selected paths.
Click the plus ![](https://handbook.glyphsapp.com/v/content/icons/plus.svg) button next to the `Attributes` heading to show additional controls.
The `Shadow`, `Inner Shadow`, and `Pattern Image` options cannot be exported to SVG; they are used when exporting to PNG or PDF with `Filter → Glyph as Image`.

Change the color of an attribute by clicking the color ![](https://handbook.glyphsapp.com/v/content/icons/color-swatch.svg) swatch button.
A red stroke through the swatch ![](https://handbook.glyphsapp.com/v/content/icons/color-swatch-empty.svg) indicates a fully transparent color.

#### [Stroke](#color-fonts/svg/creating-svg-images/stroke)

![](https://handbook.glyphsapp.com/v/content/images/root/color-layer-path-attribute-stroke.svg)

Enter a stroke width in the text field next to the `Stroke` heading.
The stroke width is measured in font units.
For example, entering `12` will add a 12 unit wide stroke along the path.
An empty stroke width field assumes a value of 0.
By default, the stroke is centered ![](https://handbook.glyphsapp.com/v/content/icons/line-align-center.svg) on the path.
Choose the left ![](https://handbook.glyphsapp.com/v/content/icons/line-align-left.svg) or right ![](https://handbook.glyphsapp.com/v/content/icons/line-align-right.svg) stroke alignment to move the stroke inside or outside the path.

Change the stroke color by clicking the color ![](https://handbook.glyphsapp.com/v/content/icons/color-swatch.svg) swatch button.
Click the minus ![](https://handbook.glyphsapp.com/v/content/icons/minus.svg) button to remove the stroke by setting the stroke width to 0 and the color to transparent.

#### [Fill](#color-fonts/svg/creating-svg-images/fill)

![](https://handbook.glyphsapp.com/v/content/images/root/color-layer-path-attribute-fill.svg)

Change the fill color by clicking the color ![](https://handbook.glyphsapp.com/v/content/icons/color-swatch.svg) swatch button.
Click the minus ![](https://handbook.glyphsapp.com/v/content/icons/minus.svg) button to remove the fill by setting the color to transparent.
The fill control is not shown when a gradient is added to a path.

#### [Gradient](#color-fonts/svg/creating-svg-images/gradient)

![](https://handbook.glyphsapp.com/v/content/images/root/color-layer-path-attribute-gradient.svg)

Click the plus ![](https://handbook.glyphsapp.com/v/content/icons/plus.svg) button next to the `Attributes` heading to add a `Gradient` effect to the selected paths.
A gradient replaces the `Fill` attribute.
There are two types of gradients: linear ![](https://handbook.glyphsapp.com/v/content/icons/gradient-linear.svg) and radial ![](https://handbook.glyphsapp.com/v/content/icons/gradient-radial.svg) gradients.
Click an icon to change the type.

![](https://handbook.glyphsapp.com/v/content/images/root/gradient-control.svg)

A gradient has at least two color stops.
These are indicated as small ![](https://handbook.glyphsapp.com/v/content/icons/gradient-control-knob.svg) knobs on the bottom of the gradient bar.
Click a knob to edit the stop color.
Add additional color stops by clicking anywhere on the gradient bar.
Remove a color stop by dragging its knob away from the gradient bar.

In Edit View, ![](https://handbook.glyphsapp.com/v/content/icons/gradient-position-knob.svg) knobs control the position of the gradient.
For a linear ![](https://handbook.glyphsapp.com/v/content/icons/gradient-linear.svg) gradient, two knobs control the start and end position of the gradient.
For a radial ![](https://handbook.glyphsapp.com/v/content/icons/gradient-radial.svg) gradient, a single knob controls the origin of the gradient.

#### [Exporting](#color-fonts/svg/creating-svg-images/exporting)

Export color layers with path attributes to SVG by adding the `Color Layers to SVG` custom parameter in `File → Font Info… → Exports`.
If this parameter is checked, Glyphs uses the paths and attributes from the Color layers to produce an `SVG` table and adds it to the exported font file.

# [Extensions](#extensions)

Extend Glyphs with scripts and plug-ins.
There are many existing scripts and plug-ins that can be freely downloaded from the Plugin Manager.
Commercial extensions are also available online.
Write custom extensions to satisfy specific needs.

All scripts and most plug-ins are written in the Python programming language.
For these to run inside Glyphs, ensure that Python [is set up in the settings](https://handbook.glyphsapp.com/single-page/#settings/addons/python-version "Settings ⯈ Addons ⯈ Python version").