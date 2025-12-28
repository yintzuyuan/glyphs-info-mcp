## [Sample Strings](#settings/sample-strings)

![](https://handbook.glyphsapp.com/v/content/images/root/settings-sample-strings.png)

The `Sample Strings` preference stores short pieces of text—sample strings—that can quickly be inserted into Edit View to review and edit glyphs.
Sample strings are organized into groups.
Click the plus ![](https://handbook.glyphsapp.com/v/content/icons/plus-button.svg) button to add a group, and click the minus ![](https://handbook.glyphsapp.com/v/content/icons/minus-button.svg) button to delete the selected group.

Each sample string is written on a separate line in the text field to the right.
The text field is Unicode-savvy and accepts all diacritic marks and non-ASCII characters.
Write `\n` (a backslash followed by a lowercase n) to include a line break in a sample string.
Specify a glyph by typing its character or writing `/` (a forward slash) followed by the glyph name and a space character.
This is useful for glyphs without a Unicode value or glyphs that are difficult to type.
If multiple glyph names follow each other, the space character may be omitted.
Use `/Placeholder` to insert a glyph that mirrors the currently selected glyph.

![](https://handbook.glyphsapp.com/v/content/images/root/edit-view-sample-text.svg)

So, to write `¡Hola`  followed by a placeholder glyph, `!`, then a new line, and the text `second line` write the following line of text into the field:

```python
/exclamdown Hola /Placeholder/exclam\nsecond line

```

Click the `Default` button to reset all sample strings to the default values and delete all custom groups.

See [Entering Text: Sample Strings](https://handbook.glyphsapp.com/single-page/#sample-strings "Edit View ⯈ Entering Text ⯈ Sample Strings") to find out more about the use of sample strings.