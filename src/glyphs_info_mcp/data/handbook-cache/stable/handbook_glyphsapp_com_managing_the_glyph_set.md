## [Managing the Glyph Set](#glyph-set)

### [Adding New Glyphs](#glyph-set/adding)

New glyphs can be added to a font in various ways:

##### [Adding Multiple Glyphs](#glyph-set/adding/multiple)

`Glyph → Add Glyphs…` (`Cmd-Shift-G`) opens a dialog window for adding glyphs.
Write glyph names (`Aacute`, `ampersand`, `noon-ar.init`), characters (Á, &, ﻧ), or Unicode values (`uni00C1`, `uni0026`, `uni0646`) separated by spaces into the text field.
Specify character ranges by placing a colon between two glyphs: `uni01FC`:`uni01FF` or `Abold-math`:`Zbold-math`.
The text field also accepts [glyph recipes](https://handbook.glyphsapp.com/single-page/#recipes "Reusing Shapes ⯈ Components ⯈ Recipes").

![](https://handbook.glyphsapp.com/v/content/images/root/add-glyphs.png)

![](https://handbook.glyphsapp.com/v/content/images/root/duplicate-glyphs-alert.png)

When adding glyphs that are already in the font, they will not be added again.
Instead, a dialog is shown listing the glyphs that are already part of the font.
Choose `Replace` to replace the existing glyphs with new, empty glyphs.
`Keep Existing` ignores the duplicate glyphs and only adds the new glyphs.
Choose `Cancel` to not add any new glyphs.

##### [Adding a Single Glyph](#glyph-set/adding/single)

`Glyph → New Glyph` (`Cmd-Opt-Shift-N`) or the plus ![](https://handbook.glyphsapp.com/v/content/icons/plus.svg) button located in the bottom-left of Font View adds a new empty glyph named `newGlyph`.

##### [Adding From the Glyph Info Database](#glyph-set/adding/glyph-info-database)

Choose `Window → Glyph Info` to show a list of all glyphs known to Glyphs.
Click `Add to Font` to add the selected glyphs to the current font.
See [Glyph Info Database](https://handbook.glyphsapp.com/single-page/#glyph-info-database "Font View ⯈ Names & Unicode ⯈ Glyph Info Database") for details.

##### [Adding From the Sidebar](#glyph-set/adding/sidebar)

Some entries in the sidebar show a badge with the total glyph count for the entry and the count of glyphs that are already part of the font.
`Control`-click or right-click a sidebar entry to show a list with the missing glyphs.
Select glyphs from the list individually, or select all by pressing `Cmd-A`.
Add the selected glyphs to the font by clicking `Generate`.

![](https://handbook.glyphsapp.com/v/content/images/root/add-glyphs-from-filter.png)

### [Copying Glyphs Between Files](#glyph-set/copying)

Glyphs can be copied across font files.
In Font View, copy the selected glyphs with `Edit → Copy` (`Cmd-C`) and paste them into another file with `Edit → Paste` (`Cmd-V`).

![](https://handbook.glyphsapp.com/v/content/images/root/no-base-glyph.svg)

Components are re-linked to the glyphs in the target font.
When a linked glyph does not exist in the target font, the component cannot be re-linked and displays as a `no base glyph` triangle placeholder instead.
If a glyph with the same name already exists in the target font, an incrementing suffix like `A.001`, `A.002`, … will be added to the name of the pasted glyph.

![](https://handbook.glyphsapp.com/v/content/images/root/paste-special.png)

Overwrite existing glyphs with `Edit → Paste Special` (hold down `Option` while the menu is open or press `Cmd-Opt-V`).
The `Paste Special` dialog presents three paste modes:

`Glyphs With Same Name`
:   overwrites the glyphs that have the same names as the copied glyphs.
    Any glyphs that do not yet exist in the target font are also added.

`Selected Glyphs`
:   overwrites all currently selected glyphs in the target font with the glyphs copied from the source font.
    The names of the selected glyphs are kept.
    If more glyphs were copied, then there are selected glyphs in the target font, the additional glyphs are ignored.

`As Components`
:   pastes the copied glyphs as components into the selected glyphs.
    Choose `All Masters` to paste on all masters.
    Existing paths and components are preserved.

For the options `Glyphs With Same Name` and `Selected Glyphs`, glyphs can be partially pasted by selecting the desired parts:

`All Data`
:   pastes the entire glyph, including shapes, anchors, layer attributes, and metrics.
    This option includes all the options below it.

`Content of Active Layer`
:   pastes the currently displayed layer.

`Kerning Groups`
:   pastes the left and right kerning groups.
    This option is useful for reduplicating kerning between similar fonts.

`Metric Keys`
:   pastes the sidebearing and width formulas.
    Recalculate them after pasting with `Glyph → Update Metrics` (`Cmd-Ctrl-M`) or across all masters with `Glyph → Update Metrics for all Masters` (`Cmd-Opt-Ctrl-M`).

`LSB`, `RSB`, `Width`
:   paste the left sidebearing, right sidebearing, and width metrics of a glyph.
    If both `RSB` and `Width` are selected, the right sidebearing value takes precedence.

### [Deleting Glyphs](#glyph-set/removing)

`Glyph → Remove Glyph` (`Cmd-Delete`) deletes the selected glyphs from the font.
This command also works on the current glyph in Edit View and selected glyphs with the Text tool active.
In Font View, the minus ![](https://handbook.glyphsapp.com/v/content/icons/minus.svg) button in the lower-left of the window does the same.
Before the selected glyphs are deleted, a confirmation dialog is shown.
Confirm with `Remove` or keep the glyphs with `Cancel`.

If some of the glyphs are used as components, the dialog offers to decompose the components before deleting the glyphs.
Click `Remove` to delete the glyphs and all components referencing them, or click `Decompose` to delete the glyphs after decomposing all components of those glyphs to outlines.

![](https://handbook.glyphsapp.com/v/content/images/root/remove-metric-keys-dialog.png)

If the metrics keys of other glyphs were linked to the metrics of a deleted glyph, a dialog offers to unlink those metrics.
For example, in a font with two glyphs `A` and `AE` (`Æ`), where the left sidebearing of `AE` is linked to the one of `A`, deleting `A` means that `AE` can no longer reference the metrics of `A`.
The dialog appears with two choices:
`Remove` dissolves the metrics keys linked to the deleted glyphs.
`Cancel` keeps the metrics keys, even though they are no longer linked to a glyph.
Such unlinked keys are set in a turquoise color:

![](https://handbook.glyphsapp.com/v/content/images/root/info-box-unlinked-metric-keys.svg)

Fix unlinked metrics keys by linking them to a different glyph, replacing the keys with numeric values, or creating the glyph they are pointing to.
See [Metrics Keys](https://handbook.glyphsapp.com/single-page/#metrics-keys "Spacing & Kerning ⯈ Spacing ⯈ Metrics Keys") for more details.