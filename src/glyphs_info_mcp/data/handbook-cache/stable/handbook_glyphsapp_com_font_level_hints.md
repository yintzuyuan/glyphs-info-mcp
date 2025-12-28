## [Font-level Hints](#truetype-hinting/font-level-hints)

TrueType hinting uses standard stem values and TT zones on each master.
Glyphs uses these font-level hints to replicate the [glyph-level hints](https://handbook.glyphsapp.com/single-page/#truetype-hinting/glyph-level-hints "TrueType Hinting ⯈ Glyph-level Hints") from the main master to all other masters.

### [TrueType Zones](#truetype-hinting/zones)

Zones help unify the vertical alignment of shapes throughout the font.
When outlines are grid-fitted onto the screen pixels, vertical shape extrema that live in the same zone will be rounded to the same height, typically a pixel edge.
Place the zones at vertical metrics such as the baseline, descender, ascender, shoulder height, figure height, nabira height, cap height, rekha height, small caps height, or whatever else makes sense for the design.

A typical TrueType zones setup: top zones with positive sizes at ascender, cap height and x-height; bottom zones with negative sizes at baseline and descender.

![](https://handbook.glyphsapp.com/v/content/images/root/latin-alignment-zone-setup.svg)

By default, TT hinting uses the main [alignment zones](https://handbook.glyphsapp.com/single-page/#masters/metrics "Font Info ⯈ Masters ⯈ Metrics & Alignment Zones") defined in `File → Font Info… → Masters → Metrics`.
Set up zones specific to TT hinting by adding the `TTFZones` custom parameter in `File → Font Info… → Masters`:

![](https://handbook.glyphsapp.com/v/content/images/root/zones-truetype.png)

If the font already contains PostScript hinting zones, choose `Get PS zones` from the actions ![](https://handbook.glyphsapp.com/v/content/icons/actions.svg) menu at the bottom-left of the window to import them as TT zones.
Add additional zones with the plus ![](https://handbook.glyphsapp.com/v/content/icons/plus-button.svg) button and remove any selected zone with the minus ![](https://handbook.glyphsapp.com/v/content/icons/minus-button.svg) button.
A font can have any number of TT zones.
Zones have the following properties:

##### [Name](#truetype-hinting/zones/name)

The name identifies a zone in the list.
It can be arbitrary text, and each name must be unique.
The `xHeight` name is special: it is used for the x-height zone, which is treated differently in grid-fitting.
A zone with that name has a higher probability than other zones of rounding up at small sizes.
Names are shown in the Info box when using the TT Instructor tool and a Snap hint is selected.

##### [Position](#truetype-hinting/zones/position)

The position determines the emplacement of the flat edge of the zone.
The flat edge is the offset from the baseline from which the zone is extending.
Negative positions are placed below the baseline.

##### [Size](#truetype-hinting/zones/size)

The size defines the value of the flattening zone during the overshoot suppression.
A top zone has a positive size; a bottom zone has a negative size.
Top zones are meant for the top vertical extremes of shapes, like the x-height, shoulder height, cap height, or nabira height.
Bottom zones are meant for catching the bottom ends of shapes, like the baseline, the descender, or the bottoms of small figures such as numerators, inferiors, and superiors.

Ensure that the area defined by the position and the size encompasses all overshoots that are supposed to be flattened to the zone position by the rasterizer.
For instance, at the x-height, put the `Position` to the height of the lowercase `x`, and make sure the `Size` is large enough to catch all overshoots, like in the lowercase `o`.
This works similarly to [PostScript alignment zones](https://handbook.glyphsapp.com/single-page/#postscript-hinting/alignment-zones "PostScript Hinting ⯈ Font-Wide Hints ⯈ Alignment Zones").

##### [Alignment](#truetype-hinting/zones/alignment)

Link a zone to another zone with the `Align` option.
If a zone is aligned to another, the distance between the zone positions is rounded and applied to the zone.

PPM (*pixels per em*) is a font size measurement.
See [Pixel Size](https://handbook.glyphsapp.com/single-page/#truetype-hinting/pixel-size "TrueType Hinting ⯈ Glyph-level Hints ⯈ Pixel Size") for details.

This will result in more consistent transitions from one PPM size to the next.
Use this for zones that are very close to each other, perhaps even overlapping, and where it may be problematic if the zones diverge too far at low-resolution pixel renderings.
Aligned zones are displayed at the same height if their distance is less than half a pixel, one pixel apart if their distance is half a pixel, and so on.

##### [Deltas](#truetype-hinting/zones/deltas)

(This property only applies to the main master.)
Click the delta ![](https://handbook.glyphsapp.com/v/content/icons/delta.svg) button to fine-tune a zone at specific PPM sizes.
A table of buttons will be shown.
The columns of the table are the masters of the font, and the rows are PPM sizes.
Click a button to switch between rounding up ![](https://handbook.glyphsapp.com/v/content/icons/hinting-truetype-rounding-up.svg), down ![](https://handbook.glyphsapp.com/v/content/icons/hinting-truetype-rounding-down.svg), or no rounding ![](https://handbook.glyphsapp.com/v/content/icons/hinting-truetype-rounding-none.svg).
The delta ![](https://handbook.glyphsapp.com/v/content/icons/delta.svg) icon in the zones list is filled with the accent color if any button is set to rounding up or down.

Rounding is helpful if a zone is one pixel too low or too high at a given PPM size.
If it is too low, round it up; if it is too high, round it down.
Use the [Hinting Preview](https://handbook.glyphsapp.com/single-page/#truetype-hinting/preview "TrueType Hinting ⯈ Glyph-level Hints ⯈ Hinting Preview") to check for any zones that need to be rounded up or down.

##### [Filter](#truetype-hinting/zones/filter)

(This property only applies to the main master.)
Click the globe ![](https://handbook.glyphsapp.com/v/content/icons/globe.svg) button to limit the zone to a subset of glyphs.
The subset is defined like a Smart Filter.
See [Smart Filters](https://handbook.glyphsapp.com/single-page/#filtering/smart-filters "Font View ⯈ Filtering Font View ⯈ Smart Filters") for details.
The globe ![](https://handbook.glyphsapp.com/v/content/icons/globe.svg) icon in the stems list is filled with the accent color if any filters are set.

![](https://handbook.glyphsapp.com/v/content/images/root/predicate-lining-numbers.png)

### [TrueType Stems](#truetype-hinting/stems)

Stems help unify the displayed size of stroke thicknesses at low resolutions.
By default, TrueType hinting uses the [standard stems of a master](https://handbook.glyphsapp.com/single-page/#masters/stems "Font Info ⯈ Masters ⯈ Stems").
Define stems specifically for TT hinting by adding the `TTFStems` custom parameter in `File → Font Info… → Masters`.
Click the value field of the parameter to edit the stems:

![](https://handbook.glyphsapp.com/v/content/images/root/stems-truetype.png)

If the font already contains PostScript stems, choose `Get PS stems` from the actions ![](https://handbook.glyphsapp.com/v/content/icons/actions.svg) menu to import them as TT stems.
Add additional stems with the plus ![](https://handbook.glyphsapp.com/v/content/icons/plus-button.svg) button and remove a selected stem with the minus ![](https://handbook.glyphsapp.com/v/content/icons/minus-button.svg) button.
The following stem properties can be edited:

##### [Orientation](#truetype-hinting/stems/orientation)

![](https://handbook.glyphsapp.com/v/content/images/root/stem-orientations.svg)

A hint is oriented in the X-direction ![](https://handbook.glyphsapp.com/v/content/icons/arrow-wave-horizontal.svg) or Y-direction ![](https://handbook.glyphsapp.com/v/content/icons/arrow-wave-vertical.svg).
Click the double arrow icon to switch between the two orientations.

The orientation of a hint describes the direction in which its points are moved.
An X-direction ![](https://handbook.glyphsapp.com/v/content/icons/arrow-wave-horizontal.svg) hint spans the thickness of a vertical stem.
A Y-direction ![](https://handbook.glyphsapp.com/v/content/icons/arrow-wave-vertical.svg) hint spans the thickness of a horizontal stem.

##### [Name](#truetype-hinting/stems/name)

The name labels the stem.
It can be arbitrary text, but it is a good idea to use descriptive names.

##### [Size](#truetype-hinting/stems/size)

The average stem thickness.
In screen rendering, similarly-sized stems will be unified and displayed with the same number of pixels.

##### [Deltas](#truetype-hinting/stems/deltas)

(This property only applies to the main master.)
Click the delta ![](https://handbook.glyphsapp.com/v/content/icons/delta.svg) button to fine-tune a stem at specific PPM sizes.
This property works like [the `Deltas` of TT zones](https://handbook.glyphsapp.com/single-page/#truetype-hinting/zones/deltas "TrueType Hinting ⯈ Font-level Hints ⯈ TrueType Zones ⯈ Deltas").
Note that stem deltas are only applied for ClearType-style rendering modes (also referred to as Windows GDI).

##### [Filter](#truetype-hinting/stems/filter)

(This property only applies to the main master.)
Click the globe ![](https://handbook.glyphsapp.com/v/content/icons/globe.svg) button to limit the zone to a subset of glyphs.
This property works like [the `Filter` of TT zones](https://handbook.glyphsapp.com/single-page/#truetype-hinting/zones/filter "TrueType Hinting ⯈ Font-level Hints ⯈ TrueType Zones ⯈ Filter").

### [TrueType BlueFuzz](#truetype-hinting/bluefuzz)

Use the `TTFBlueFuzz` custom parameter to extend all TT zones by a certain amount.
The specified amount will be added both above and below to each zone.
It defaults to 1 unit.

The parameter is helpful for testing stem values or for fixing imprecisions in interpolation:
Even if the drawings end up nicely in the zones in all masters, they may still drop out of them in interpolated instances.
Such imprecisions can occur due to rounding errors.
Test the font using the [Hinting Preview](https://handbook.glyphsapp.com/single-page/#truetype-hinting/preview "TrueType Hinting ⯈ Glyph-level Hints ⯈ Hinting Preview") to see if the zones work in all instances, and if not, increase the `TTFBlueFuzz`.

Add the parameter in `File → Font Info… → Font`, `Masters`, or `Exports`.
Adding it to the `Font` tab applies it to all instances equally.
If the parameter is instead added to the masters, it will be interpolated at export.
Add it to a single instance in `Exports` to overwrite the masters and font settings.