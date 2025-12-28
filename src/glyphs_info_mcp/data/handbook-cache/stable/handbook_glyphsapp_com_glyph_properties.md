## [Glyph Properties](#glyph)

![](https://handbook.glyphsapp.com/v/content/images/root/glyph-properties.png)

Glyphs have multiple properties associated with them, such as their name, metrics, Unicode values, and whether the glyph will be exported.
In Font View, glyph properties are shown in the bottom-left corner of the window in the glyph inspector.
If the inspector is closed, open it with the disclosure ![](https://handbook.glyphsapp.com/v/content/icons/info-panel-down.svg) button.
Glyph properties are also shown in the columns of [List View](https://handbook.glyphsapp.com/single-page/#list-view "Font View ⯈ Viewing Glyphs ⯈ List View") and the Selection Info window (`Edit → Info for Selection`, `Cmd-Opt-I`).
Some properties are also accessible from the context menu on a glyph in Font View and Edit View.

The glyph inspector and the Selection Info window show the properties of the selected glyphs.
Click the disclosure chevron ![](https://handbook.glyphsapp.com/v/content/icons/disclosure-chevron-closed.svg) next to the `Unicode` field in the glyph inspector to show additional controls for the production name, script, category, and subcategory.

When multiple glyphs are selected with different values for the same property, a mixed value is displayed in the inspector.
For text fields, `Multiple Values` is shown in gray.
Editing such a text field will overwrite the current value for all selected glyphs with the new value.
The export checkbox ![](https://handbook.glyphsapp.com/v/content/icons/checkbox-checked.svg) uses a line icon ![](https://handbook.glyphsapp.com/v/content/icons/checkbox-mixed.svg), indicating that some selected glyphs export and some do not.

### [Glyph Name](#glyph/name)

Glyphs are identified by their name.
Therefore, a font cannot contain two glyphs with the same name.
The glyph name (or *nice name*) is used within Glyphs, while a separate *production name* is used for exported fonts.
See [Production Name](https://handbook.glyphsapp.com/single-page/#glyph/production-name "Font View ⯈ Glyph Properties ⯈ Production Name") for details on production names and [Naming Glyphs](https://handbook.glyphsapp.com/single-page/#glyph-names/introduction "Font View ⯈ Names & Unicode ⯈ Naming Glyphs") for general information about the glyph naming scheme.

Select glyphs one at a time to display and change their names, or batch rename glyphs with `Edit → Find → Find and Replace` (`Cmd-Shift-F`).
See [Batch-Renaming Glyphs](https://handbook.glyphsapp.com/single-page/#batch-renaming-glyphs "Font View ⯈ Batch-Processing ⯈ Batch-Renaming Glyphs") for more details.

### [Metrics](#glyph/metrics)

The metric fields show the horizontal ![](https://handbook.glyphsapp.com/v/content/icons/metrics-horizontal.svg) metrics (LSB, RSB, width) or the vertical ![](https://handbook.glyphsapp.com/v/content/icons/metrics-vertical.svg) metrics (TSB, BSB, vertical origin, vertical width) of a glyph.
Click the icon in the middle to switch between the horizontal and vertical metrics.
See [Spacing & Kerning](https://handbook.glyphsapp.com/single-page/#spacing-and-kerning "Spacing & Kerning") for information on metrics.

### [Kerning Groups](#glyph/kerning-groups)

Use kerning groups to kern multiple glyphs by the same amount.
See [Kerning: Kerning Groups](https://handbook.glyphsapp.com/single-page/#kerning/groups "Spacing & Kerning ⯈ Kerning ⯈ Kerning Groups") for details.

### [Exports](#glyph/exports)

The `Exports` checkbox controls whether or not a glyph should be included in exported font files.
Disable this option for component glyphs and any other glyphs that should not be exported.
Use the `Remove Glyphs` custom parameter on an instance to remove additional glyphs for that instance only.
A glyph is exported by default unless its name starts with an underscore (`_`).

### [Color Label](#glyph/color-label)

**From left to right:**

glyph color only (`schwa`),   
no glyph or layer color (`f`),   
glyph and layer color (`g`),   
layer color only (`gbreve`).

![](https://handbook.glyphsapp.com/v/content/images/root/glyph-cells-colors.svg)

Glyphs and glyph layers can be marked with color labels.
Color labels do not affect the exported fonts but are used to organize glyphs during font development.

![](https://handbook.glyphsapp.com/v/content/images/root/shortcut-menu-dark-green.png)

Control-click or right-click a glyph to apply one of the twelve predefined colors.
Click the cross ![](https://handbook.glyphsapp.com/v/content/icons/xmark.svg) button to remove the color from a label.
Hold down the `Option` key to define or clear the color label of the current layer.

The glyph color spans across the entire glyph cell.
The layer color is drawn on the right half of the cell if a glyph color is set, or across the entire cell with a cut-out in the top-left if no glyph color is set.
Filter glyphs with a particular color using Smart Filters.
See [Smart Filters](https://handbook.glyphsapp.com/single-page/#filtering/smart-filters "Font View ⯈ Filtering Font View ⯈ Smart Filters") for details.

In some cases, such as Smart Filters or scripts, color labels are addressed by name or number.
The following names and numbers are used:
![](https://handbook.glyphsapp.com/v/content/icons/color-label-red.svg) 0 Red,
![](https://handbook.glyphsapp.com/v/content/icons/color-label-orange.svg) 1 Orange,
![](https://handbook.glyphsapp.com/v/content/icons/color-label-brown.svg) 2 Brown,
![](https://handbook.glyphsapp.com/v/content/icons/color-label-yellow.svg) 3 Yellow,
![](https://handbook.glyphsapp.com/v/content/icons/color-label-light-green.svg) 4 Light Green,
![](https://handbook.glyphsapp.com/v/content/icons/color-label-dark-green.svg) 5 Dark Green,
![](https://handbook.glyphsapp.com/v/content/icons/color-label-cyan.svg) 6 Cyan,
![](https://handbook.glyphsapp.com/v/content/icons/color-label-blue.svg) 7 Blue,
![](https://handbook.glyphsapp.com/v/content/icons/color-label-purple.svg) 8 Purple,
![](https://handbook.glyphsapp.com/v/content/icons/color-label-pink.svg) 9 Pink,
![](https://handbook.glyphsapp.com/v/content/icons/color-label-light-gray.svg) 10 Light Gray,
![](https://handbook.glyphsapp.com/v/content/icons/color-label-dark-gray.svg) 11 Dark Gray.

### [Tags](#glyph/tags)

![](https://handbook.glyphsapp.com/v/content/images/root/tags.svg)

Tags are short descriptions that can be attached to a glyph.
A glyph can have multiple tags.
Edit tags in the `Tags` field in the inspector located in the bottom-left of the font window.
Tags can include letters, numbers, spaces, and other punctuation marks.
Only the comma character (`,`) is special:
Typing a comma or pressing `Return` will add the tag to the selected glyphs and display it in a blue capsule shape.
The `Tags` field shows the tags of all selected glyphs if they have the same tags.
Otherwise, the text `Multiple Values` is displayed.

Control-click or right-click a glyph in Font View and choose the `Tags` menu.
It shows all tags used within the font.
If no tags are used in the font, then the `Tags` menu is not shown.
Tags included in any of the selected glyphs are marked with a checkmark ![](https://handbook.glyphsapp.com/v/content/icons/checkmark.svg) next to the tag name.
A dash indicates that only some of the selected glyphs include that tag.
Select a tag from the menu to add it to all selected glyphs.

Tags can be used to filter glyphs, including in [Smart Filters](https://handbook.glyphsapp.com/single-page/#filtering/smart-filters "Font View ⯈ Filtering Font View ⯈ Smart Filters"), [metric scopes](https://handbook.glyphsapp.com/single-page/#masters/metrics "Font Info ⯈ Masters ⯈ Metrics & Alignment Zones"), and in OpenType feature [tokens](https://handbook.glyphsapp.com/single-page/#layout/tokens/glyph-predicate "Feature Code ⯈ Tokens ⯈ Glyph Predicate Tokens").

### [Unicode](#glyph/unicode)

A Unicode value (or *code point*) is a unit of text typed by a user on a keyboard or stored in a text file.
The Unicode standard defines a code point for most written symbols used across the globe.
Unicode values are written as `U+` followed by a hexadecimal number
(digits 0–9 and A–F).

![](https://handbook.glyphsapp.com/v/content/images/root/latin-A-and-adlam-Alif-and-arabic-question.svg)

For example, `U+0041` is the Latin capital letter A, `U+1E900` is the Adlam capital letter Alif, and `U+061F` is the Arabic question mark.
The font defines which glyph is displayed for a specific Unicode value.

Typically, one glyph has one Unicode value.
In an all-caps font without lowercase letters, the `A` glyph might have two Unicode values: `U+0041` and `U+0061` (uppercase and lowercase Latin letter A).
This way, typing either `A` or `a` displays the `A` glyph.
Some glyphs have no Unicode values and are only accessible using [OpenType features](https://handbook.glyphsapp.com/single-page/#layout "Font Info ⯈ Features").
Glyphs that are solely used as [components](https://handbook.glyphsapp.com/single-page/#components "Reusing Shapes ⯈ Components") also have no Unicode values.

Glyphs are assigned Unicode values based on their name.
The mapping from glyph names to Unicode values is stored in the glyph info database.
See [Names & Unicode](https://handbook.glyphsapp.com/single-page/#glyph-names "Font View ⯈ Names & Unicode") for more details.

The Unicode values of a glyph can also be customized per Glyphs file.
Select a glyph and edit Unicode values in the `Unicode` field of the inspector.
In List View, the code points can also be edited in the `Unicode` column.
Alternatively, choose `Edit → Info for Selection` (`Cmd-Opt-I`) and set the Unicode values of the selected glyph there.

For custom glyphs that are not defined in the glyph info database, [choose a fitting name](https://handbook.glyphsapp.com/single-page/#glyph-names/introduction "Font View ⯈ Names & Unicode ⯈ Naming Glyphs"), and set its Unicode value manually.

Unicode defines some ranges (such as `U+E000`–`U+F8FF`) as *Private Use Area* (PUA) where the Unicode values have no predefined meaning.
PUA code points are generally used for languages that are not in Unicode or icon fonts.

If the Unicode standard does not offer a suitable code point for a glyph, consider encoding it with a Private Use Area code point.
When adding a custom glyph, make sure not to use the name of a registered glyph from the glyph info database.

Glyphs without a well-defined name (such as most Chinese characters) are named after their Unicode value:
`uni` followed by four hexadecimal digits or `u` followed by five or six digits.
For example, `uni5B57` for `U+5B57` and `u20547` for `U+20547`.

### [Production Name](#glyph/production-name)

Not all [nice names used within Glyphs](https://handbook.glyphsapp.com/single-page/#glyph/name "Font View ⯈ Glyph Properties ⯈ Glyph Name") are compatible with every app.
Instead, production glyph names are used for exported font files.
These production names are based on the [Adobe Glyph List Specification (AGL)](https://github.com/adobe-type-tools/agl-specification).
Many production names follow the naming scheme as described in [Unicode](https://handbook.glyphsapp.com/single-page/#glyph/unicode "Font View ⯈ Glyph Properties ⯈ Unicode"):
`uni` followed by four hexadecimal digits or `u` followed by five or six digits.

Production names are used automatically on export, while nice names are used in the Glyphs interface.
All glyphs have a default production name, but it can be changed in the expanded inspector (expand it by clicking the ![](https://handbook.glyphsapp.com/v/content/icons/disclosure-chevron-closed.svg) disclosure chevron) or by choosing `Edit → Info for Selection` (`Cmd-Opt-I`).

### [Script](#glyph/script)

The script property defines the writing script the glyph belongs to.
The glyph `G` is `latin`, `Ya-cy` is `cyrillic`, `noon-ar` is `arabic`, `koKai-thai` is `thai`, and so on.
Glyphs belonging to multiple scripts—like digits (`one`, `two`, …), punctuation (`comma`, `hyphen`, …), or spaces—do not have a script value.

### [Category & Subcategory](#glyph/category-and-subcategory)

The category and subcategory of a glyph groups it with related glyphs.
All exporting glyphs belong to a category by default, while non-exporting glyphs such as components do not.
The glyph `T` belongs to the category Letter, `six` to Number, and `plus` to Symbol.
Some glyphs additionally have a subcategory for finer differentiation.

- `guillemetright` (`»`) is defined as Punctuation, Quote
- `parenleft` (`(`) is defined as Punctuation, Parenthesis
- `hyphen` (`-`) is defined as Punctuation, Dash

### [Case](#glyph/case)

Some scripts differentiate glyphs by case.
The case of a glyph can be *uppercase*, *lowercase*, *small capital*, *minor*, or no case.
*Uppercase* and *lowercase* are used for letters in bicameral scripts such as Greek or Latin, but also for punctuation (for example, `question` (`?`) is uppercase and `questiondown` (`¿`) is lowercase) and marks (lowercase: `acutecomb`, uppercase: `acutecomb.case`).
Glyphs ending in `.sc` or `.smcp` are assigned the *small capital* case.
The *minor* case is used for subscript and superscript numbers (`five.sups`), letters (`ainferior`), and punctuation (`equalinferior`).
All other glyphs have no case, including glyphs from scripts without case (Arabic or CJK) and most punctuation glyphs (for instance, `comma` or `euro`).

### [Writing Direction](#glyph/writing-direction)

A glyph has a writing direction of either left to right (LTR), right to left (RTL), or bidirectional (BiDi).
Many punctuation glyphs are bidirectional (for example, `hyphen`, `asterisk`, and `underscore`).
See [Entering Text: Writing Direction](https://handbook.glyphsapp.com/single-page/#writing-direction "Edit View ⯈ Entering Text ⯈ Writing Direction") for setting the writing direction in Edit View.

### [Sort Name](#glyph/sort-name)

The `Sort Name` property of the selected glyph can be edited in the Selection Info window (`Edit → Info for Selection`, `Cmd-Opt-I`).
It defines the name by which the glyph is sorted in Font View and the exported font files.
An empty `Sort Name` field indicates that the glyph name is used for sorting instead.
Select the checkbox next to the sort name field to edit it.
Sort names are not used in [list filters](https://handbook.glyphsapp.com/single-page/#filtering/list-filters "Font View ⯈ Filtering Font View ⯈ List Filters") or when using a custom [glyphs order](https://handbook.glyphsapp.com/single-page/#glyph-order "Font View ⯈ Glyph Order").

### [ID](#glyph/id)

In [List View](https://handbook.glyphsapp.com/single-page/#list-view "Font View ⯈ Viewing Glyphs ⯈ List View"), the `ID` column sorts glyphs in glyph order.
This is the order in which glyphs are sorted in exported fonts.
Change the order by setting the [sort name](https://handbook.glyphsapp.com/single-page/#glyph/sort-name "Font View ⯈ Glyph Properties ⯈ Sort Name") of glyphs or using the `glyphOrder` custom parameter in `File → Font Info… → Font`.

### [Char](#glyph/character)

In [List View](https://handbook.glyphsapp.com/single-page/#list-view "Font View ⯈ Viewing Glyphs ⯈ List View"), the `Char` column displays the Unicode character using the system font.
If a glyph has multiple Unicode values, only the first one is displayed.

### [Note](#glyph/note)

Notes are accessible from [List View](https://handbook.glyphsapp.com/single-page/#list-view "Font View ⯈ Viewing Glyphs ⯈ List View") in the `Note` column.
A glyph note can contain any text.
Search for glyph notes with the [search field in Font View](https://handbook.glyphsapp.com/single-page/#filtering/search-field "Font View ⯈ Filtering Font View ⯈ Search Field").

### [Components](#glyph/components)

In [List View](https://handbook.glyphsapp.com/single-page/#list-view "Font View ⯈ Viewing Glyphs ⯈ List View"), the components column shows a list of the components used in a glyph.
The components cell in List View can be edited to add or remove components to or from a glyph.
See [List View](https://handbook.glyphsapp.com/single-page/#list-view "Font View ⯈ Viewing Glyphs ⯈ List View") for hiding and showing columns.

### [Last Changed](#glyph/last-changed)

The `Last Changed` column in [List View](https://handbook.glyphsapp.com/single-page/#list-view "Font View ⯈ Viewing Glyphs ⯈ List View") is updated every time a glyph is modified.
Add a `Write lastChange` custom parameter in `File → Font Info… → Font` and disable it to prevent Glyphs from updating this property, which might be desirable when keeping the Glyphs file under version control.