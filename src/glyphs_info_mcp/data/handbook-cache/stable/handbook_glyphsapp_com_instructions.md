## [Instructions](#truetype-hinting/instructions)

Add TrueType instructions by selecting nodes and choosing one of the available instruction types from the context menu.
Click and drag to reposition instructions.

Choose `Autohint` from the context menu to add some instructions automatically.
This action will add Snap and Stem hints, but not Shift, Interpolate, or Delta hints.
The result can be useful as a starting point for manual TT hinting.
Some glyphs cannot be autohinted.
In that case, the error message `There was a problem compiling TrueType instructions` appears.
Autohint the current glyph by pressing `Cmd-Opt-Ctrl-Shift-I` (configure the shortcut in the `Commands` section in the [app settings](https://handbook.glyphsapp.com/single-page/#settings/shortcuts "Settings ⯈ Shortcuts")).
This shortcut also works when multiple glyphs are selected in Edit View.

Remove all glyph-level hints from the current glyph by choosing `Remove Hints` from the context menu.

### [Snap (A)](#truetype-hinting/instructions/snap)

![](https://handbook.glyphsapp.com/v/content/images/root/hint-truetype-snap.svg)

Snap instructions ![](https://handbook.glyphsapp.com/v/content/icons/hint-truetype-snap-badge.svg) (shortcut `A`) round the position of previously untouched points to the nearest pixel edge.
Apply a Snap instruction by selecting one or more untouched points and pressing `A` or selecting `Snap Point` from the context menu.

Select a Snap instruction by clicking its purple badge.
The Info box (`View → Show Info`, `Cmd-Shift-I`) shows configuration options for the selected instructions.
From the pop-up menu located at the top of the Info box, choose one of the following options:

- `Auto`: In vertical ![](https://handbook.glyphsapp.com/v/content/icons/arrow-wave-vertical.svg) mode, the point will snap onto the pixel edge the zone is rounding to if it is inside a zone.
  Configure the zone rounding with the `TTFZones` custom parameter.
  `Auto` is typically the best option.
- `No Zone`: Tells the instruction to ignore zones altogether.
  In that case, it will only look for the nearest pixel edge.
- The other options are the named zones (see [TrueType Zones](https://handbook.glyphsapp.com/single-page/#truetype-hinting/zones "TrueType Hinting ⯈ Font-level Hints ⯈ TrueType Zones")).
  Choosing a zone will keep the node at a constant distance to the selected zone and ensure that the snapped node will not fall on the other side of the zone.
  Note that these zone options are not intended for snapping a node to a zone.
  Instead, it works similarly to the alignment of one zone with another zone in the [`TTFZones` custom parameter](https://handbook.glyphsapp.com/single-page/#truetype-hinting/zones "TrueType Hinting ⯈ Font-level Hints ⯈ TrueType Zones").

The icon buttons on the bottom of the Info box indicate the rounding that the instruction triggers:

![](https://handbook.glyphsapp.com/v/content/images/root/info-box-truetype-instructor-snap-point.svg)

- `Round` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round.svg) (default) rounds the point to the nearest pixel edge.
- `Round up` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round-up.svg) rounds the point to the nearest pixel edge above (in vertical ![](https://handbook.glyphsapp.com/v/content/icons/arrow-wave-vertical.svg) mode) or right (in horizontal ![](https://handbook.glyphsapp.com/v/content/icons/arrow-wave-horizontal.svg) mode).
- `Round down` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round-down.svg) rounds the point to the nearest pixel edge below (in vertical ![](https://handbook.glyphsapp.com/v/content/icons/arrow-wave-vertical.svg) mode) or left (in horizontal ![](https://handbook.glyphsapp.com/v/content/icons/arrow-wave-horizontal.svg) mode).
- `No rounding` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-none.svg) keeps the point at its original position.
  Useful for suppressing the effects of IUP.
- `Round only in GDI ClearType` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round-cleartype.svg) works like `Round`, but only in the ClearType rendering intent.
  Useful for antialiasing in the Grayscale and DirectWrite intents, while ClearType has to round to the full pixel.
  This mode is only effective when hinting horizontal stems because GDI ClearType has no vertical oversampling.

### [Stem (S)](#truetype-hinting/instructions/stem)

![](https://handbook.glyphsapp.com/v/content/images/root/hint-truetype-stem.svg)

Stem instructions ![](https://handbook.glyphsapp.com/v/content/icons/hint-truetype-stem-badge.svg) (shortcut `S`) round the positions of either two previously untouched points or one touched and one untouched point to a distance determined by the TT stem.
A Stem hint has an originating point and a target point (indicated by the arrowhead).
The target point is moved to follow the distortion of the originating point.
Stem hints can be added to multiple point pairs at the same time, provided an even number of points is selected.
Flip the origin and target points by choosing `Reverse` from the context menu on the Stem hint.

If a Stem hint starts in a zone, it will automatically snap the originating point in the zone.
A Snap instruction is therefore not needed for the originating node.

Select a Stem hint by clicking its sky-blue ![](https://handbook.glyphsapp.com/v/content/icons/hint-truetype-stem-badge-knob.svg) badge.
Configure the selected Stem hint in its Info box.
From the pop-up menu located at the top of the Info box, choose one of the
following options:

- *Auto*: The hint will use the closest stem as defined in the `TTFStems` parameter.
  This is the best mode, provided the stems are clearly distinct.
- *No Stem*: The target points are not snapped to the grid; only their distance to the originating node is kept.
  This means that the target point is moved only if the originating point is moved as well.
  This is the best mode for higher shape fidelity in medium-range pixel sizes (not too small) or if the distortions in the resulting rendering environment are otherwise too important.
- The other options are the [named stems](https://handbook.glyphsapp.com/single-page/#truetype-hinting/stems "TrueType Hinting ⯈ Font-level Hints ⯈ TrueType Stems").
  Select one of these options only if the auto mode would give the wrong results.

The icon buttons on the bottom of the Info box indicate the rounding that the instruction triggers:

![](https://handbook.glyphsapp.com/v/content/images/root/info-box-truetype-instructor-stem-hint.svg)

- `Round` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round.svg) rounds the target point to the nearest pixel edge.
- `Round up` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round-up.svg) rounds the stem size up.
  This will snap the target point to the pixel edge that is further away from the originating point.
  If the Stem hint is pointing downwards, that will be below.
- `Round down` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round-down.svg) rounds the stem size down.
  This will snap the target point to the pixel edge that is closer to the originating point.
  If the Stem hint is pointing downwards, that will be above.
- `No rounding` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-none.svg) (default) does not round the stem to any pixel edge, but will still round its size to the oversampling edges provided by the current rendering intent.
- `Round only in GDI ClearType` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round-cleartype.svg) works like the `Round` mode, but only for the GDI ClearType rendering intent.
  If a stem is not adjacent to a zone, this mode can help keep at least one edge of the stem aligned with the closest pixel boundary.
  This is useful for the middle bars in `E` and `e`, and best if combined with an [Interpolate instruction](https://handbook.glyphsapp.com/single-page/#truetype-hinting/instructions/interpolate "TrueType Hinting ⯈ Instructions ⯈ Interpolate (G)"):

  ![](https://handbook.glyphsapp.com/v/content/images/root/hint-truetype-stem-cleartype.svg)

The stem widths taken from the `TTFStems` parameter are rounded according to the oversampling of the respective rendering intent.
Stems should not be rounded (with the default `No rounding` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-none.svg) mode) not to overwrite that.
Having stems that are not rounded to full pixel edges means that at least one side of the stem will get a gray border.
The resulting rendering is a little less sharp but much better preserves the details of the design.
It also produces fewer problems with distorted outlines, for example, fewer collapsed counters.

If there are three horizontal stems, select all three Stem hints by consecutively `Shift`-clicking them, then choose `Make Triple Hint` from the context menu.
The Stem hints will turn purple ![](https://handbook.glyphsapp.com/v/content/icons/hint-truetype-stem-triple-badge.svg), indicating they are connected and will try to preserve at least one-pixel distance even in the worst of circumstances:

![](https://handbook.glyphsapp.com/v/content/images/root/hint-truetype-stem-triple.svg)

### [Shift (F)](#truetype-hinting/instructions/shift)

![](https://handbook.glyphsapp.com/v/content/images/root/hint-truetype-shift.svg)

Shift instructions ![](https://handbook.glyphsapp.com/v/content/icons/hint-truetype-shift-badge.svg) (shortcut `F`) transfer the movement of a touched (originating) point to an untouched (target) point.
This shifts the target point the same way the originating point is shifted.
Use Shift instructions to make sure that two parts of a glyph implement the same distortion.

Apply a Shift instruction by selecting a touched and an untouched point, and press `F` or choose `Shift Points` from the context menu.
Multiple Shift instructions with the same originating point can be added simultaneously, provided only one of the selected points is touched (originating point), and all others are untouched (target points).

Select a Shift hint by clicking its dark blue ![](https://handbook.glyphsapp.com/v/content/icons/hint-truetype-shift-badge-knob.svg) badge.
The icon buttons in the Info box indicate the rounding that the instruction triggers:

![](https://handbook.glyphsapp.com/v/content/images/root/info-box-truetype-instructor-blank-no-rounding.svg)

- `Round` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round.svg) rounds the target point to the nearest pixel edge.
- `Round up` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round-up.svg) rounds the target point to the nearest pixel edge above.
- `Round down` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round-down.svg) rounds the target point to the nearest pixel edge below.
- `No rounding` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-none.svg) (default) keeps the transferred movement exactly as it is without any additional rounding.
  This is typically the best mode for Shift instructions.
- `Round only in GDI ClearType` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round-cleartype.svg) works like `Round`, but only for GDI ClearType.

For example, consider the two legs of a Latin lowercase sans-serif `n`.
The left leg should get snapped in the baseline zone.
But, after adding a Stem hint for the shoulder between the two legs, the right leg is out of sync with the left leg.

This happens because, along the line of the path, the effect of the Snap instruction in the lower left is interrupted by the Stem instruction on the top.
Therefore, for the right leg, the ensuing IUP (interpolation of untouched points) can only extrapolate the distortion caused by the Stem instruction, not the Snap instruction.
Effectively, the Snap instruction is confined to the left leg.
Mitigate this by adding a Shift instruction from the touched (snapped) point on the left leg to one of the points on the right leg:

![](https://handbook.glyphsapp.com/v/content/images/root/hint-truetype-shift-Latin-small-n.svg)

The Shift instruction duplicates the movement of the left leg to the right leg, making the target point a touched point.
This way, the right leg will always perform the same movement as the left leg.
The lowercase Latin `m` may use multiple Shift instructions:

![](https://handbook.glyphsapp.com/v/content/images/root/hint-truetype-shift-Latin-small-m.svg)

### [Interpolate (G)](#truetype-hinting/instructions/interpolate)

Interpolate instructions ![](https://handbook.glyphsapp.com/v/content/icons/hint-truetype-interpolate-badge.svg) (shortcut `G`) keep a previously untouched point at the same relative position to two touched points as in the original uninstructed outline.
Apply an Interpolate instruction by selecting two touched points and a third, untouched point.
Then press the `G` key or choose `Interpolate` from the context menu.

The main intention of Interpolate hints is to remedy unwanted side effects of IUP.
For example, use an Interpolate instruction to keep a middle stem at the same relative distance from the (already touched) outer stems, as in this lowercase `e`:

![](https://handbook.glyphsapp.com/v/content/images/root/hint-truetype-interpolate.svg)

Select a Shift hint by clicking its green ![](https://handbook.glyphsapp.com/v/content/icons/hint-truetype-interpolate-badge-knob.svg) badge.
The icon buttons in the Info box indicate the rounding that the instruction triggers:

![](https://handbook.glyphsapp.com/v/content/images/root/info-box-truetype-instructor-blank-no-rounding.svg)

- `Round` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round.svg) snaps the target point to the nearest pixel edge.
  Choose this mode when adding a Stem hint on top of the target point.
- `Round up` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round-up.svg) snaps the target point to the next pixel edge above.
- `Round down` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round-down.svg) snaps the target point to the next pixel edge below.
- `No rounding` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-none.svg) (default) keeps the interpolated position and does not round it.
  This is typically the best mode for Interpolate instructions.
- `Round only in GDI ClearType` ![](https://handbook.glyphsapp.com/v/content/icons/rounding-round-cleartype.svg) will snap to the nearest pixel edge for the GDI ClearType rendering intent; the others should remain unaffected.

### [Delta (E)](#truetype-hinting/instructions/delta)

![](https://handbook.glyphsapp.com/v/content/images/root/hint-truetype-delta.svg)

Delta instructions ![](https://handbook.glyphsapp.com/v/content/icons/hint-truetype-delta-badge.svg) (shortcut `E`) move a point up or down by exactly one pixel, but only in a specific static instance and a specific PPM size.
Delta hints are intended as final pixel corrections after all other hints have been applied.
Add a Delta hint by selecting any number of points and pressing `E` or choosing `Delta` from the context menu.
Select one or more Delta hints, click the Delta ![](https://handbook.glyphsapp.com/v/content/icons/delta.svg) icon in the Info box, and configure them like the deltas of a TT zone.
See [TrueType Zones: Deltas](https://handbook.glyphsapp.com/single-page/#truetype-hinting/zones/deltas "TrueType Hinting ⯈ Font-level Hints ⯈ TrueType Zones ⯈ Deltas") for details.

Delta hints should be used sparsely, if at all, and should be added last, after all other hints.
Delta hints are only available for vertical ![](https://handbook.glyphsapp.com/v/content/icons/arrow-wave-vertical.svg) hinting and are ignored in variable fonts.

### [Points in Overlapping Intersections](#truetype-hinting/points-in-overlapping-intersections)

Instructions may be placed on any node shown in the TrueType Instructor tool.
However, path intersections are handled separately.
When a font is exported with the `Remove Overlaps` option selected, overlapping intersections are reduced to a single point.
Glyphs will move any hints on points that are removed as part of the overlap removal to the nearest resulting intersection point.
Thus, the following two hints are equivalent in *non-variable fonts*:

![](https://handbook.glyphsapp.com/v/content/images/root/hint-truetype-intersection.svg)

In *variable fonts*, overlaps are not removed.
Hints added to extra nodes, such as the right hint in the image above, are ignored.
When exporting variable fonts, only add hints to normal nodes, like the left hint in the image above.