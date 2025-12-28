## [Fit Curve](#palette/fit-curve)

![](https://handbook.glyphsapp.com/v/content/images/root/fit-curve-20-to-100.svg)

`Fit Curve` from 20 % to 100 %

The `Fit Curve` section helps to create curves with a smooth curvature.
Clicking one of the eight round buttons ![](https://handbook.glyphsapp.com/v/content/icons/fit-curve-button.svg) changes the length of the selected handles.
The leftmost button sets the handles to the length specified in the left field, and the rightmost button matches them to the right field.
The intermediate six buttons set the handles to intervals of even lengths.
Alternatively, activate the eight buttons with the shortcuts `Opt-Ctrl-1` through `Opt-Ctrl-8`.

The plus ![](https://handbook.glyphsapp.com/v/content/icons/plus.svg) and minus ![](https://handbook.glyphsapp.com/v/content/icons/minus.svg) buttons uniformly increase or decrease the handle’s length of the selected curve segments.
`Fit Curve` always works on both handles of a segment, even if only one is selected.

![](https://handbook.glyphsapp.com/v/content/images/root/palette-fit-curve.svg)

When a handle is selected, a small gray indicator located under the buttons shows the current handle length.
The minimum value is 1 percent, the maximum value is 100 percent.
A length of 55 % is the closest approximation to an elliptic curvature or a circle.
Such a curve segment appears equally curved across its entire length.
Curves with longer handle lengths (above 55 %) appear flattened towards their on-curve points, making them more apt for connecting to line segments.
Curves with shorter handle lengths (below 55 %) appear flat in the middle and highly curved towards the ends.

Add a `Fit Curve Panel Settings` custom parameter to the font to set per-document minimum and maximum values.
The value are two numbers, separated by a comma, like `55, 85`.