## [Lookup Flags](#layout/lookup-flags)

The `lookupflag` keyword resets any previous lookup flags and sets a new set of flags.
For example, to reset the previous flags and ignore marks in the current lookup, the following code line can be placed at the start of a lookup definition:

```python
lookupflag IgnoreMarks;

```

When writing lookups, it is common to ignore any prior flags without setting new ones.
In the standard feature syntax this is done by using the special flag `0`:

```python
lookupflag 0;

```

As an alternative, Glyphs allows resetting lookup flags without setting new flags by simply defining an empty `lookupflag` statement:

```python
lookupflag;

```

# [PostScript Hinting](#postscript-hinting)

PostScript hinting is a method to improve display at low resolutions for fonts with PostScript/CFF outlines.
TrueType flavor OpenType fonts use a different method for hinting; see [TrueType Hinting](https://handbook.glyphsapp.com/single-page/#truetype-hinting "TrueType Hinting") for details.

The eventual picture on the screen is created by a software called the rasterizer.
Hints help the rasterizer to create a more even glyph image.
Especially stems are harmonized to look similar across a line of text.
PostScript hints are simpler but also less flexible than TrueType hints.

Most hinting information revolves around determining which part of a letter is a necessary stroke element and should not be omitted at small sizes.
There are two kinds of hints.

*Font-level hints* or *font-wide hints* store general information that applies to the entire font and encompasses standard stems and alignment zones.

*Glyph-level hints* are little pieces of information placed inside a glyph that help the rasterizer stretch the outline across the pixel grid.
They can either be *stem hints* or *ghost hints*.

The best practice is choosing good font-level hints and letting an algorithm called the *autohinter* find the glyph-level hints.

Hinting only makes sense if the font has repeated regular features.
If the font is very irregular, like many handwritten fonts are, or like ornamental and grunge fonts, then hinting cannot help to improve the rendering.
Also, suppose a font is intended for exclusive use in environments where hinting information is ignored, like displays with a very high resolution, or on Apple hardware running macOS or iOS.
In that case, the hinting information is not used and will only make the font file larger.
Consider not hinting or disabling any existing hinting for such projects.

Note that PostScript hinting intends to create a sharper, more consistent pixel image at low resolutions.
That means that the outline will be distorted to achieve a better fitting on the pixel grid.
In other words, hinting *does not preserve shapes*; on the contrary.
Hinting does not make sense for fonts where the preservation of the shape is more important than a crisp pixel image, such as in connecting script typefaces and icon fonts.