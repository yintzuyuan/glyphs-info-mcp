## [Kerning](#kerning)

Carefully spaced glyphs should fit together well in words and sentences.
Some glyph combinations, however, need specific adjustments to look good.
Usually, glyphs with a lot of white space (such as `A` and `V`) need to be moved closer together.
In contrast, glyphs that collide (such as `f` and `?`) need to be moved further apart.
Kerning is the adjustment of the distance between glyphs.

Note that left to right kerning is stored separately from right to left kerning.
When working with a font that includes glyphs of both directions, make sure to select the correct writing direction before kerning.
See [Entering Text: Writing Direction](https://handbook.glyphsapp.com/single-page/#writing-direction "Edit View ⯈ Entering Text ⯈ Writing Direction") for details.

With the Text tool active, kerning between glyphs is highlighted in light blue ![](https://handbook.glyphsapp.com/v/content/icons/kerning-negative.svg) for negative kerning and yellow ![](https://handbook.glyphsapp.com/v/content/icons/kerning-positive.svg) for positive kerning.
These colors can be changed in the [Appearance settings](https://handbook.glyphsapp.com/single-page/#settings/appearance "Settings ⯈ Appearance").

### [Kerning Modes](#kerning/modes)

Edit View has three kerning modes: no kerning ![](https://handbook.glyphsapp.com/v/content/icons/kerning-disabled.svg), kerning ![](https://handbook.glyphsapp.com/v/content/icons/kerning.svg), and locked kerning ![](https://handbook.glyphsapp.com/v/content/icons/kerning-no-spacing.svg).
Cycle between the modes by clicking the icon located in the bottom-right of the Edit View canvas.

No kerning ![](https://handbook.glyphsapp.com/v/content/icons/kerning-disabled.svg) disables the preview of kerning in Edit View.
The [kerning shortcuts](https://handbook.glyphsapp.com/single-page/#kerning/shortcuts "Spacing & Kerning ⯈ Kerning ⯈ Kerning Shortcuts") are also disabled in this mode.
Kerning ![](https://handbook.glyphsapp.com/v/content/icons/kerning.svg) previews kerning pairs in Edit View.
Locked kerning ![](https://handbook.glyphsapp.com/v/content/icons/kerning-no-spacing.svg) works like the normal kerning mode but disables the [spacing shortcuts](https://handbook.glyphsapp.com/single-page/#spacing/shortcuts "Spacing & Kerning ⯈ Spacing ⯈ Spacing Shortcuts"), preventing accidental spacing changes while kerning.

### [Info Box](#kerning/info-box)

In Edit View, the Info box (`View → Show Info`, `Cmd-Shift-I`) displays the kerning between the current glyph and the immediate glyph on each side.
When no kerning is set, the gray placeholder `Kern` is visible.

Click a kern field, enter an adjustment value, and confirm by pressing `Return` or by exiting the kern field.
Clear a kern field to remove the kern between the two glyphs.
Activate the Text tool to see a small Info box for the preceding glyph.
The box provides the name of the preceding glyph, its lock status, and kerning group name:

See [Kerning: Kerning Groups](https://handbook.glyphsapp.com/single-page/#kerning/groups "Spacing & Kerning ⯈ Kerning ⯈ Kerning Groups") for details on the `Group` fields in the Info box and [Kerning Group Exceptions](https://handbook.glyphsapp.com/single-page/#kerning/groups/exceptions "Spacing & Kerning ⯈ Kerning ⯈ Kerning Group Exceptions") for working with the kerning ![](https://handbook.glyphsapp.com/v/content/icons/lock-locked.svg) locks.

Editing kerning in the Info box can be handy for quick adjustments.
When kerning many glyph pairs, consider using the kerning shortcuts.

### [Kerning Shortcuts](#kerning/shortcuts)

**Mnemonic:**

the `Control` key is located on the left, and the `Command` on the right.
`Control`: left glyph.
`Command`: right glyph.

The kerning shortcuts can be used with the Text tool.
Type the two glyphs in Edit View, then place the cursor between them and hold down the `Option` and `Control` keys to change the kerning value between the current and the left glyph with the `Left Arrow` and `Right Arrow` keys (⌃⌥⯇ and ⌃⌥⯈).
Hold down `Option` and `Command` to change the kerning between the current and the right glyph (⌥⌘⯇ and ⌥⌘⯈).
Hold down `Shift` for steps of 10.

| Shortcut | Action |
| --- | --- |
| `Opt-Ctrl-Left` | increase kerning on left side |
| `Opt-Ctrl-Shift-Left` | increase kerning on left side by 10 units |
| `Opt-Ctrl-Right` | decrease kerning on left side |
| `Opt-Ctrl-Shift-Right` | decrease kerning on left side by 10 units |
| `Cmd-Opt-Right` | increase kerning on right side |
| `Cmd-Opt-Shift-Right` | increase kerning on right side by 10 units |
| `Cmd-Opt-Left` | decrease kerning on right side |
| `Cmd-Opt-Shift-Left` | decrease kerning on right side by 10 units |

### [Kerning Groups](#kerning/groups)

Many glyphs with similar forms should have the same kerning values.
Kerning groups capture these similarities and reduce the number of pairs that need to be set manually.
Kerning then applies not just to pairs of glyphs, but to groups of pairs of glyphs.
For example, `B`, `D`, `E`, `F`, `H`, and so on may form a left side kerning group.
Also, `V`, `W`, `Ẃ`, `Ŵ`, `Ẅ`, and so on might share both the left and the right kerning groups.
For example, if `A` and `Ä` are in the same kerning group, kerning `A` to `V` also kerns the `Ä`–`V` pair.
Additionally, if `V` is in a group with `W`, `A`–`W` and `Ä`–`W` will also be kerned by the same amount.
All members of a kerning group have the same kerning values unless a kerning exception is defined (see [Kerning Group Exceptions](https://handbook.glyphsapp.com/single-page/#kerning/groups/exceptions "Spacing & Kerning ⯈ Kerning ⯈ Kerning Group Exceptions")).

A glyph can have two kerning groups: one on the left and one on the right.
Glyphs written from top to bottom have a top and bottom group instead.

The name of a kerning group is written into the `Group` fields in the Info box (`View → Show Info`, `Cmd-Shift-I`).
Edit the kerning groups of multiple glyphs in the [inspector in Font View](https://handbook.glyphsapp.com/single-page/#glyph/kerning-groups "Font View ⯈ Glyph Properties ⯈ Kerning Groups"), or select multiple glyphs in Edit View.
Group names can contain the letters a–z and A–Z, the digits 0–9, and an underscore (`_`), period (`.`), or hyphen (`-`).
Rename kerning groups in the [Kerning Window](https://handbook.glyphsapp.com/single-page/#kerning/window "Spacing & Kerning ⯈ Kerning ⯈ Kerning Window").

It is common to name kerning groups after a base glyph.
For example, `R`, `Ŕ`, `Ř`, and `Ŗ` may all have the right kerning group `R`.
The left kerning group might be named `I` or `H`.
However, it can also be named `stem` or any arbitrary name.

Another example: the glyphs `c`, `d`, `e`, `o`, and `q` could share a left kerning group named `o`.
In that case, kerning `To` will also kern all other group members.
However, while `To` might look good, kerning `Tö` by the same amount will probably look too tight.
There are two solutions for this issue:
either `ö` could be placed in a different left kerning group than `o`, or [kerning group exceptions](https://handbook.glyphsapp.com/single-page/#kerning/groups/exceptions "Spacing & Kerning ⯈ Kerning ⯈ Kerning Group Exceptions") could be used for `ö`.

Show all kerning group members in the background by choosing `View → Show Group Members`.
The group members are only shown for the current glyph and the one placed before it on the canvas.
Only members of the respective kerning group are shown.
For example, when editing the `P` glyph, only its left kerning group members are shown in the background.
This display option is helpful to spot possible collisions.

### [Kerning Group Exceptions](#kerning/groups/exceptions)

A kerning group exception overwrites the kerning values of a group for a specific pair.
For example, if `o` and `ö` have the same left kerning group, the kerning value of `To` might be too tight for `Tö`.

Create a group exception for `Tö` by selecting the Text tool, then place the text cursor between `T` and `ö`.
In the Info box (`View → Show Info`, `Cmd-Shift-I`), open the lock ![](https://handbook.glyphsapp.com/v/content/icons/lock-unlocked.svg) of the `ö` to mark it as an exception.
Now, editing the kerning value between `T` and `ö` will not affect any of the other glyphs having the same left kerning group as `ö`.
However, keep the lock of the `T` glyph locked ![](https://handbook.glyphsapp.com/v/content/icons/lock-locked.svg) so that the new `T`–`ö` kerning exception also applies to other group members of the right `T` kerning group, for example, `Ť`–`ö`, `Ţ`–`ö`, and `Ț`–`ö`.
Close the kerning lock to remove an exception.

### [Kerning Window](#kerning/window)

Open the Kerning Window by choosing `Window → Kerning` (`Cmd-Opt-K`).
It provides a list of all kerning pairs for the currently selected writing direction.
See [Entering Text: Writing Direction](https://handbook.glyphsapp.com/single-page/#writing-direction "Edit View ⯈ Entering Text ⯈ Writing Direction") for details on changing the writing direction.

#### [Viewing Kerning Pairs](#kerning/pairs/viewing)

Enter a search term in the search field to filter for kerning pairs containing it.
Click the search icon ![](https://handbook.glyphsapp.com/v/content/icons/magnifying-glass-light.svg) to configure the search options.
Choose how the search term should be applied (kerning pair *contains*, *is exactly*, *begins with*, *ends with*, or *does not contain* the term), which pairs to show (*is a group* or *is not a group*), on which side of the pairs to search (*left* or *right*), or whether or not to show only glyphs that are selected in Font View.
Choose `Reset` to reset all options back to their default.

Kerning groups are shown in blue with an at-sign (`@`) before their name, while single glyphs are shown in gold.
Click a column header (`Left`, `Value`, `Right`) to sort by that column.
Click again to reverse the sort order.
Sorting by value is helpful to spot particularly small or large kerning values.

Click a kerning pair to display it in Edit View.
The current glyph pair in Edit View, if any, will be replaced by the selected pair.
Use the `Up` and `Down` arrow keys to walk through the kerning pairs of the font.
When selecting a row containing one or two kerning groups, only a single example is shown.
Insert all kerning pairs belonging to the selected row into Edit View by choosing `Show All Glyphs` from the actions ![](https://handbook.glyphsapp.com/v/content/icons/actions.svg) menu.

#### [Editing Kerning Pairs](#kerning/pairs/editing)

Double-click an entry in the Kerning Window to edit it.
Edit a value to adjust the kerning between a pair.
Edit a group name to rename the group.
Renaming a group will prompt whether to change the group name for only the selected kerning pair, or rename the group across the entire font.
Since left and right kerning groups are separate, renaming a group in the `Left` column will not affect any entries in the `Right` column and vice versa.

Copy the selected kerning pairs with `Edit → Copy` (`Cmd-C`).
Select all kerning pairs by choosing `Edit → Select All` (`Cmd-A`).
Switch to another font master and paste the copied pairs with `Edit → Paste` (`Cmd-V`).
If pasting would overwrite existing kerning pairs, Glyphs will show a warning.
Choose `Overwrite` to paste the copied pairs and overwrite any the conflicting kerning pairs.
Choose `Keep Existing` to paste only non-conflicting pairs.

Delete all selected kerning pairs by pressing the minus ![](https://handbook.glyphsapp.com/v/content/icons/minus.svg) button in the bottom-left of the Kerning Window.
Hold down the `Option` key to delete the pairs from all masters.

#### [Maintaining Kerning Pairs](#kerning/pairs/maintaining)

Kerning pairs can become obsolete when glyphs are removed from the font, or a kerning group no longer has any members.
Delete all obsolete kerning pairs by choosing `Clean Up` from the actions ![](https://handbook.glyphsapp.com/v/content/icons/actions.svg) menu.

Choose `Compress` from the actions ![](https://handbook.glyphsapp.com/v/content/icons/actions.svg) menu to reduce the number of kerning pairs in the font.
When a few glyphs were kerned with each other before the kerning groups were set, the singleton kerning pairs can be converted into group kerning with the `Compress` action.
Compressing kerning changes kerning pairs between two glyphs or between a glyph and a group such that kerning groups are used wherever possible.
Kerning exceptions are kept unless the exception has the same kerning value as the group kerning (meaning, it’s not a real exception).
The `Compress` action might need to be run multiple times to compress all kerning pairs fully.

For example, consider a kerning pair `T`–`m`, which is a kerning between the glyphs `T` (right group: `@T`) and `m` (left group: `@n`).
Compressing once will turn it into the kerning pair `@T`–`m`.
Compressing a second time will turn it into `@T`–`@n`.
Now, this kerning pair applies to all glyphs in the `@T` right group and the `@n` left group, such as `Ť`–m, `T`–n, `T`–`ŋ`, and `Ť`–`ŋ`.
However, it will keep exceptions such as `T`–`ň`, provided it has a different value than `T`–`n`.

### [Manual Kerning Code](#kerning/manual)

While kerning is implemented as an OpenType feature, it does not appear in the `Features` tab of the Font Info window.
Instead, it is added as an [implicit feature](https://handbook.glyphsapp.com/single-page/#layout/implicit-features "Font Info ⯈ Features ⯈ Implicit Features").
However, an explicit `kern` feature can also be added for performing contextual kerning.

In `File → Font Info… → Features`, add a new feature named `kern`.
The `kern` feature typically uses positioning (`pos`) rules to change the distance between glyphs.

Contextual kerning matches more than two glyphs and can be helpful when dealing with punctuation or spaces.
For example, the `f` might get some extra spacing to the right when it is followed by a `space` glyph and a glyph that extends far to the left on the top, such as `T` or `V`.

```python
pos f' 50 space [T V W Y];

```

Kerning groups can be reused in feature code.
The name of a left kerning group is prefixed by `@MMK_R_` while a right kerning group is prefixed by `@MMK_L_`.
For example, the left kerning group `@H` has the feature class `@MMK_R_H` and the right group `@quote` has the class `@MMK_L_quote`.
Note that the `R` and `L` in the prefixes are with respect to the other glyph of the kerning pair: a left kerning group is used on the *right* (`R`) of a pair while a right kerning group is used on the *left* (`L`) of a pair.

For example, consider the glyph sequence `L`–`quoteright`–`A` (L’A).
With pair kerning, the quote might get pulled into the white space of the `L` and also in the white space of the `A`, making the `L` and `A` collide on the baseline: L’A.
A contextual kern can fix this situation by pulling the `quoteright` into the white space of the `L` (`-50`) while pushing the `A` to the right (`70`):

```python
pos @MMK_L_L' -50 quoteright' 70 @MMK_R_A;

```

Manual kerning code can also make use of [Tokens](https://handbook.glyphsapp.com/single-page/#layout/tokens "Feature Code ⯈ Tokens"), which allow the glyph positioning to be based on Number Values of masters or the sidebearings of glyphs.

# [Reusing Shapes](#reusing-shapes)