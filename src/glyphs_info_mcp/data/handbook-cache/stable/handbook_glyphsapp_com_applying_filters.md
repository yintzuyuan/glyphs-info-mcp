## [Applying Filters](#filters/applying)

### [Filter Menu](#filters/menus)

Apply a filter by choosing `Filter → (name of the filter)`.
The filter will be applied to all selected glyphs in Font View.
In Edit View, the filter will be applied to a selection of glyphs made with the Text tool or to the current glyph with any other tool.

Filters usually affect only the currently visible layer.
Applying a filter to all masters of a glyph may therefore require re-running the filter on all other masters.
Quickly apply the last used filter by pressing `Cmd-R`.

### [Filters as Custom Parameters](#filters/custom-parameters)

Most filters can be applied to an instance on export using custom parameters.
However, some filters cannot be used for variable fonts as they would produce incompatible outlines.

Add a custom parameter by navigating to `File → Font Info… → Exports → Custom Parameters`.
Click the plus ![](https://handbook.glyphsapp.com/v/content/icons/plus.svg) button, choose `Filter`, and click `Add`.
A `Filter` parameter with a text field will be added to the list of custom parameters.

Write the name of the filter followed by its arguments into the text field.
Arguments are separated by semicolons (`;`).
Some argument values have a specific position in the arguments list, and some are named.
Named arguments begin with their name and a colon (`:`) followed by their value.

```python
FilterName; value1; value2; someName: value3

```

For example, the following line would apply the `RoundCorner` filter with a radius of `15` and visual corrections activated (`1` for active, `0` for inactive):

```python
RoundCorner; 15; 1

```

The order and meaning of arguments depend on the filter.
See [Built-in Filters](https://handbook.glyphsapp.com/single-page/#filters/built-in "Filters ⯈ Built-in Filters") for details on the filters included in Glyphs.

[Number value tokens](https://handbook.glyphsapp.com/single-page/#layout/tokens/number-value "Feature Code ⯈ Tokens ⯈ Number Value Tokens") can be used to dynamically insert values by writing the name of a token prefixed by a dollar sign:

```python
RoundCorner; $roundRadius; 1

```

When used in a [variable font setting](https://handbook.glyphsapp.com/single-page/#interpolation/setup-instances/variable "Interpolation ⯈ Setting up Instances ⯈ Variable Font Settings"), number value tokens are used to interpolate the filter values.

Limit a filter to a subset of glyphs by adding an `include` argument that lists all glyph names for which the filter should be applied:

```python
RoundCorner; 15; 1; include: a, b, c

```

Similarly, use the `exclude` argument to apply a filter to all glyphs except for the listed glyphs:

```python
RoundCorner; 15; 1; exclude: a, b, c

```

Spaces in filter parameters are optional and may be added to improve legibility.

Multiple `Filter` parameters can be added to a single instance.
They are applied during export in the order of the custom parameters.
`Filter` parameters get applied after the components of a glyph are decomposed.
Use a `PreFilter` custom parameter instead to run a filter before glyph decomposition.
The filter rules in the custom parameter text field are the same for `PreFilter`.
See [Decomposing](https://handbook.glyphsapp.com/single-page/#components/decomposing "Reusing Shapes ⯈ Components ⯈ Decomposing") for more on glyph decomposition.

![](https://handbook.glyphsapp.com/v/content/images/root/filter-custom-parameters.svg)

When applied from the `Filter` menu, many filters have an actions ![](https://handbook.glyphsapp.com/v/content/icons/actions.svg) button in the lower left of their dialog window.
Click the button and choose `Copy Custom Parameter`.
The custom parameter for the filter can now be pasted into an instance.
Open `File → Font Info… → Exports`, choose an instance from the sidebar, click the `Custom Parameters` heading, and paste the filter with `Edit → Paste` (`Cmd-V`).