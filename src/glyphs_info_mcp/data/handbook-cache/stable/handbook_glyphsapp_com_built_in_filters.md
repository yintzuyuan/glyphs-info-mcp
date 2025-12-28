## [Built-in Filters](#filters/built-in)

### [Shape Order](#filters/shape-order)

**`Shape Order` dialog window:**

One column per master/alternate/intermediate layer.
Drag to reorder shapes within a column.
The insertion position is highlighted in blue.

![](https://handbook.glyphsapp.com/v/content/images/root/shape-order-incompatible.png)

The `Shape Order` filter lists all shapes (paths and components) of a glyph across all layers.
Paths are shown in navy blue; components in brown.
Each column lists the shapes of a master/alternate/intermediate layer.
Click and drag a shape to reorder it within its column.
Confirm the chosen shape order with `OK`, or revert to the original shape order with `Cancel`.

Columns are separated by a gray gutter if there are multiple independent interpolations for the glyph.
That might be the case when using [intermediate layers](https://handbook.glyphsapp.com/single-page/#intermediate-layers "Interpolation ⯈ Intermediate Layers") or when employing a complex master setup (for example, when condensed masters interpolate independently of extended masters).

The `Shape Order` filter is useful when `Path → Correct Path Directions for all Masters` (`Cmd-Opt-Shift-R`) does not yield the desired master compatibility.

### [Extrude](#filters/extrude)

![](https://handbook.glyphsapp.com/v/content/images/root/extrude-dialog.png)

![](https://handbook.glyphsapp.com/v/content/images/root/extrude.svg)

`Filter → Extrude` will create a solid shadow offset for the shape of the glyph.
The following parameters are configurable:

`Offset`
:   Controls the length of the shadow in font units.

`Angle`
:   The direction of the extrusion in counterclockwise degrees from a right horizontal stretch.

`Don’t Subtract`
:   By default, the original shape will be subtracted from the extruded shape.
    Suppress such a subtraction by enabling this option.

**From left to right:**

1 normal glyph   
2 standard extrude   
3 composition of 1 and 2   
4 `Don’t subtract` enabled

![](https://handbook.glyphsapp.com/v/content/images/root/extrude-samples.svg)

The custom parameter rule is as follows:

```python
Extrude; Offset; Angle; Don’t Subtract

```

For example, to offset by 100 units at an angle of −30 degrees:

```python
Extrude; 100; -30

```

Don’t Subtract is disabled by default.
Enable the option by setting its value to `1`:

```python
Extrude; 100; -30; 1

```

### [Hatch Outline](#filters/hatch-outline)

![](https://handbook.glyphsapp.com/v/content/images/root/hatch-outline-dialog.png)

![](https://handbook.glyphsapp.com/v/content/images/root/hatch-outline-samples.svg)

`Filter → Hatch Outline` creates hatched glyphs.
The following parameters are configurable:

`Origin`
:   Defines the origin point (`X` and `Y` coordinates) where the hatching pattern begins.

`Step Width`
:   The distance between the strokes.

`Angle`
:   The angle at which the strokes are drawn.
    0° is horizontal, 90° is vertical.

`Offset Path`
:   The thickness of the strokes.
    Disable this option to create open paths instead (which may be useful in combination with other filters or plug-ins).

The custom parameter rule is as follows:

```python
HatchOutlineFilter; OriginX:X; OriginY:Y; StepWidth:Distance; Angle:Angle; Offset:Offset

```

The arguments are all optional and can be written in any order.
If left out, the argument of an option will assume its default value.
For instance, for strokes, a thickness of 5 inclined at a 40° angle and placed at every 20 units:

```python
HatchOutlineFilter; StepWidth:20; Angle:40; Offset:5

```

The hatch origin will default to X = `0`, Y = `0`.

### [Offset Curve](#filters/offset-curve)

![](https://handbook.glyphsapp.com/v/content/images/root/offset-curve-dialog.png)

![](https://handbook.glyphsapp.com/v/content/images/root/offset-curve-standard.svg)

`Filter → Offset Curve` changes the thickness of stems horizontally and vertically.
The following parameters are configurable:

`Horizontal`, `Vertical`
:   Define the horizontal and vertical offset from the current outline.
    Positive values expand the outline; negative values contract the outline.
    Click the lock ![](https://handbook.glyphsapp.com/v/content/icons/lock-locked.svg) button to use the horizontal field for both values.

`Make Stroke`
:   Offsets the outline in both directions to form a stroke along the outline.
    This is useful for creating outlines from closed paths.
    See [Creating Strokes](https://handbook.glyphsapp.com/single-page/#graphic-attributes/strokes "Edit View ⯈ Graphic Attributes ⯈ Creating Strokes") for creating non-destructive strokes.

`Auto Stroke`
:   Offsets the outline in both directions while maintaining the vertical dimensions intact when making a stroke.
    If enabled, it assumes a position of 50 %.

`Position`
:   Controls the distribution of the stroke.
    0 % places the stroke to the left of the path, 100 % places it to the right.
    At 50 %, the stroke is evenly distributed along the path.

    **From left to right:**

    `Make Stroke` with `Position` of 100 %, 50 %, 0 %, and 0 % with `Keep Compatible` enabled.

    ![](https://handbook.glyphsapp.com/v/content/images/root/offset-curve-positions.svg)

`Keep Compatible`
:   Keeps the offset curve compatible across masters by not introducing any new nodes or handles.
    Enabling this option might reduce the offset accuracy.

Cap Style
:   Defines the stroke endings style when making a stroke from an open path.
    Choose from flat ![](https://handbook.glyphsapp.com/v/content/icons/line-cap-style-butt.svg), square ![](https://handbook.glyphsapp.com/v/content/icons/line-cap-style-square.svg), round ![](https://handbook.glyphsapp.com/v/content/icons/line-cap-style-round.svg), round inset ![](https://handbook.glyphsapp.com/v/content/icons/line-cap-style-round-inset.svg), and aligned to the vertical and horizontal axes ![](https://handbook.glyphsapp.com/v/content/icons/line-cap-style-align-to-axis.svg).

    ![](https://handbook.glyphsapp.com/v/content/images/root/offset-curve-cap-styles.svg)

The custom parameter rule is as follows:

```python
OffsetCurve; Horizontal; Vertical; Make Stroke; Position; Keep Compatible; cap:Cap Style

```

The Horizontal and Vertical offsets are in font units.
Make Stroke is `0` for false or `1` for true.
Position is either a percentage (for example, `0.5` for 50 %) or `auto` for the `Auto Stroke` option.
Set Keep Compatible to `keep` to enable the option or leave the argument off to disable it.
Cap Style is `1` for ![round](https://handbook.glyphsapp.com/v/content/icons/line-cap-style-round.svg), `2` for ![round inset](https://handbook.glyphsapp.com/v/content/icons/line-cap-style-round-inset.svg), `3` for ![flat](https://handbook.glyphsapp.com/v/content/icons/line-cap-style-square.svg), `4` for ![aligned to axes](https://handbook.glyphsapp.com/v/content/icons/line-cap-style-align-to-axis.svg), and `0` or left off for ![flat](https://handbook.glyphsapp.com/v/content/icons/line-cap-style-butt.svg).
For example, for a stroke with thickness 20 (10 units on either side) and a cap style of ![round](https://handbook.glyphsapp.com/v/content/icons/line-cap-style-round.svg):

```python
OffsetCurve; 10; 10; 1; 0.5; cap:1

```

Curves can be offset non-destructively [using stroke styles](https://handbook.glyphsapp.com/single-page/#graphic-attributes/strokes "Edit View ⯈ Graphic Attributes ⯈ Creating Strokes").

### [Roughen](#filters/roughen)

![](https://handbook.glyphsapp.com/v/content/images/root/roughen-dialog.png)

![](https://handbook.glyphsapp.com/v/content/images/root/roughen-samples.svg)

`Filter → Roughen` segments an outline into straight line segments and randomly moves all resulting nodes within a given limit.
Control the size of the line segments with the `Segment Length` field.
The `Horizontal` and `Vertical` values control the maximum offset for each node.
The custom parameter rule is as follows:

```python
Roughenizer; Length; Horizontal; Vertical

```

For example, the following rule would match the `Roughen` dialog window shown above:

```python
Roughenizer; 15; 15; 10

```

### [Round Corners](#filters/round-corners)

![](https://handbook.glyphsapp.com/v/content/images/root/round-corners-dialog.png)

`Filter → Round Corners` rounds all selected corners of a path.
The filter is only applied to outwards pointing corners if nothing is selected.
The `Radius` is defined in font units.
Choose `Visual corrections` to balance the rounding of acute and obtuse corners using smaller and larger radii, respectively.
Such visual corrections tend to create more natural-looking rounding.

**From left to right:**

No filter, without visual correction, with visual correction, filter applied to outwards and inwards pointing corners.

![](https://handbook.glyphsapp.com/v/content/images/root/round-corners-samples.svg)

The custom parameter rule is as follows:

```python
RoundCorner; Radius; Visual Corrections

```

If Radius is positive, it is applied to outwards pointing corners;
if it is negative, it is applied to inwards pointing corners.
Add multiple `RoundCorner` custom parameter filters to control both.
Set Visual Corrections to `1` to enable it or `0` to disable it.
For example, the following rule settings apply a corner radius of 55 to outwards pointing corners with visual corrections enabled:

```python
RoundCorner; 55; 1

```

When used on a [variable font setting](https://handbook.glyphsapp.com/single-page/#interpolation/setup-instances/variable "Interpolation ⯈ Setting up Instances ⯈ Variable Font Settings"), add the keyword `compatible` at the end to improve the compatibility of the resulting rounded outlines, like so:

```python
RoundCorner; 55; 1; compatible

```

### [Rounded Font](#filters/rounded-font)

![](https://handbook.glyphsapp.com/v/content/images/root/rounded-font-samples.svg)

`Filter → Rounded Font` rounds the stem endings with appropriate overshoots.
For this, it uses the vertical stem metrics as defined in `File → Font Info… → Masters → Stems`.
The custom parameter rule is as follows:

```python
RoundedFont; Vertical Stem Width

```

If a Vertical Stem Width argument is set, its value is used instead of the vertical stem width from the master metrics.
Such an override can be helpful when combined with the `include` and `exclude` arguments to define a different stem width for a subset of glyphs.
For example, consider three `Filter` custom parameters for an instance:

```python
RoundedFont; exclude: f, k, t, dollar, percent
RoundedFont; 74; include: f, k, t
RoundedFont; 86; include: dollar, percent

```

Here, the glyphs `f`, `k`, `t`, `dollar` ($), and `percent` (%) would be processed with special Vertical Stem Width values.
See [Filters as Custom Parameters](https://handbook.glyphsapp.com/single-page/#filters/custom-parameters "Filters ⯈ Applying Filters ⯈ Filters as Custom Parameters") for details on `include` and `exclude`.

### [Transformations](#transformations)

The Transformations filter is split into three dialogs: `Transform Metrics`, `Transformations`, and `Interpolate with Background`.

##### [Transform Metrics](#transform-metrics)

`Glyph → Transform Metrics` assigns either a new width or new sidebearings to the selected glyph layers.

![](https://handbook.glyphsapp.com/v/content/images/root/transform-metrics-dialog.png)

Enable `Width` to assign a new width to all selected glyphs.
Check `on both sides` to modify both sides equally to match the new width.
Otherwise, the points on the layer keep their original coordinates.

Uncheck `Width` to set new sidebearings.
Control whether the left sidebearing (`LSB`), the right sidebearing (`RSB`), or both should be changed using the checkboxes next to their fields.
If `Relative` is selected, the `LSB` and `RSB` values are added to the current sidebearings (or subtracted if the entered values are negative).
Otherwise, the `LSB` and `RSB` values overwrite the existing sidebearings.

##### [Transformations](#transformations-dialog)

This type of transformation is also known as an *affine transformation*.

`Path → Transformations` applies a linear transformation to the selected points or selected layers.

![](https://handbook.glyphsapp.com/v/content/images/root/transformations-dialog.png)

`Translate` moves points by a given `X` and `Y` value.
`Origin` defines the point from which the transformation originates.
`Scale` scales the selection along the ![](https://handbook.glyphsapp.com/v/content/icons/horizontal-arrow.svg) horizontal and ![](https://handbook.glyphsapp.com/v/content/icons/vertical-arrow.svg) vertical axis.
If the lock button is locked ![](https://handbook.glyphsapp.com/v/content/icons/lock-locked.svg), the horizontal value is used for both axes.
`Slant` skews the selection without optical correction.
Click the `Slant` label and choose `Cursivy` for an optically corrected skew.
Note that `Cursivy` requires horizontal and vertical metrics to be set in `File → Font Info… → Masters → Stems`.

##### [Interpolate with Background](#interpolate-with-background)

`Path → Interpolate with Background` results in an [interpolation](https://handbook.glyphsapp.com/single-page/#interpolation "Interpolation") of the foreground and background layers.

![](https://handbook.glyphsapp.com/v/content/images/root/interpolate-with-background-dialog.png)

A value of 0 % leaves the foreground unchanged; 100 % replaces the foreground with the background, and values in-between result in an interpolated shape.
Use a value below 0 % or above 100 % to extrapolate.
Note that this filter does not work if the foreground and background are not compatible.

##### [Custom Parameter](#transformations/custom-parameter)

The custom parameter rule is as follows:

```python
Transformations; LSB:LSB, RSB:RSB; Width:Width; ScaleX:Scale X; ScaleY:Scale Y; Slant:Slant; SlantCorrection:Cursivy; OffsetX:X; OffsetY:Y; Origin:Origin Metric

```

LSB and RSB set the left and right sidebearings.
Prefix these values with a `+` (plus), `-` (minus), `*` (asterisk, multiply), or `/` (forward slash, divide) symbol to change the sidebearings relative to their current values.
Width can be prefixed by `+` or `-`.
For example, to multiply the LSB by 2 and add 15 to the RSB, use the following filter rule:

```python
Transformations; LSB:*2; RSB:+15

```

Scale X and Scale Y are percentages where a value of 100 does not scale, < 100 scales down, and > 100 scales up.
Set Cursivy to `0` to disable slant correction;
it is `1` by default.
Set Origin Metric to `0` for cap height, `1` for ½ cap height, `2` for x-height, `3` for ½ x-height (default), or `4` for baseline.

For example, the following rule sets the width of all glyphs to 700, scales the glyph outlines to 120 % (both horizontally and vertically), cursivies the outlines to a 14° angle (adding `SlantCorrection:0` would use normal slanting), and moves the outlines by 8 units to the right and 22 units down such that all these transformations originate from the x-height:

```python
Transformations; Width:700; ScaleX:120; ScaleY:120; Slant:14; OffsetX:8; OffsetY:-22; Origin:2

```

### [Add Extremes](#filters/add-extremes)

`Path → Add Extremes` adds missing nodes on [extrema](https://handbook.glyphsapp.com/single-page/#extremes-and-inflections "Edit View ⯈ Editing Paths ⯈ Extremes & Inflections").
The custom parameter rule is the filter name `AddExtremes` without any arguments.

### [Remove Overlap](#filters/remove-overlap)

`Path → Remove Overlap` removes the overlap of the selected paths, or all paths if none are selected, or multiple glyphs are selected.
It also clears the selected glyphs of all open paths and stray nodes.
The filter expects all outline orientations to be set correctly (see [Controlling Path Direction](https://handbook.glyphsapp.com/single-page/#controlling-path-direction "Edit View ⯈ Editing Paths ⯈ Controlling Path Direction")).

Apply this filter as a custom parameter with the `RemoveOverlap` name and no arguments.
Alternatively, apply `Remove Overlap` by checking [its checkbox in the export dialog](https://handbook.glyphsapp.com/single-page/#export/opentype/options "Import & Export ⯈ Exporting Font Files ⯈ OpenType Export ⯈ Options").

# [Feature Code](#layout/feature-code)

Glyphs extends the [AFDKO feature syntax](https://adobe-type-tools.github.io/afdko/OpenTypeFeatureFileSpecification.html) with a number of additional capabilities.