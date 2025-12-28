## [Filtering Font View](#filtering)

Font View can be filtered only to show a subset of glyphs.
Filter glyphs using search, glyph categories, scripts, languages, and custom filter rules.

At the bottom-center of Font View, the number of selected, visible, and total glyphs is shown.
The number of visible glyphs depends on the selected sidebar filter and the search query.
Select `All` at the top of the left sidebar and clear the search field to show all glyphs of the font.

### [Search Field](#filtering/search-field)

![](https://handbook.glyphsapp.com/v/content/images/root/search-field.png)

In the top-left of Font View is the glyph search field (`Cmd-F`).
Enter text to search by glyph name (`thorn`), Unicode value (`00FE`), Unicode character (`þ`), or [glyph note](https://handbook.glyphsapp.com/single-page/#glyph/note "Font View ⯈ Glyph Properties ⯈ Note").
Click the search glass ![](https://handbook.glyphsapp.com/v/content/icons/search-with-menu.svg) icon to search only by name, Unicode value, or note.

Select `Match Case` to search only for glyphs matching the capitalization of the search term.
With this option selected, searching for `Aring` would find `Aring` and `Aringacute`, but not `aring` or `aringacute`.

Select `Regex` to search using regular expressions.
Regular expressions match patterns of characters.

Examples

- `.` matches any character and thereby finds all glyphs with a single character name
- `..` finds glyphs with two-character names
- `.*\.sc` finds glyphs ending in `.sc`
- `[Aa].*-cy` finds glyphs starting with `A` or `a` and ending in `-cy`

See [Regular Expressions](https://handbook.glyphsapp.com/single-page/#regular-expressions "Appendix ⯈ Regular Expressions") for details.

### [Categories](#filtering/categories)

Select a category filter in the left sidebar to show only the glyphs belonging to the selected category.
Click the disclosure chevron ![](https://handbook.glyphsapp.com/v/content/icons/disclosure-chevron.svg) next to a category name to show its subcategories.
Select a subcategory to show only those glyphs.
The number of glyphs in a subcategory is shown next to the subcategory name.
If Glyphs can infer that some glyphs in the subcategory might be missing, the count is replaced by a gray badge ![](https://handbook.glyphsapp.com/v/content/icons/subcategory-badge.svg) showing both the current count ![](https://handbook.glyphsapp.com/v/content/icons/subcategory-badge-font-count.svg) and the total count ![](https://handbook.glyphsapp.com/v/content/icons/subcategory-badge-total-count.svg) of glyphs in the subcategory.
Add the missing glyphs as described in [Adding From the Sidebar](https://handbook.glyphsapp.com/single-page/#glyph-set/adding/sidebar "Font View ⯈ Managing the Glyph Set ⯈ Adding New Glyphs ⯈ Adding From the Sidebar").
If all glyphs have been added, a checkmark ![](https://handbook.glyphsapp.com/v/content/icons/checkmark.svg) is displayed instead of a gray badge.

When multiple categories are selected by `Command`-clicking, glyphs from any of the selected categories are shown.
If a `Categories` entry is selected together with a `Languages` or `Filters` entry, only glyphs that are part of both are displayed.

### [Languages](#filtering/languages)

The `Languages` section contains script and language filters.
Expand a language filter by clicking the disclosure chevron ![](https://handbook.glyphsapp.com/v/content/icons/disclosure-chevron.svg) next to the filter name.
Glyph counts, badges, and checkmarks appear the same as in categories (see above).
`Command`-click script names to filter for multiple scripts at the same time, or `Command`-click other filters to combine them with the selected language filters.

Only a few scripts are shown by default in the sidebar to keep the list short and tidy.
Click the plus ![](https://handbook.glyphsapp.com/v/content/icons/plus.svg) button next to the `Languages` label to edit the default list of scripts.
A list opens where individual scripts can be shown or hidden by toggling the checkbox next to their name.
A script entry is automatically added to the sidebar if the font contains glyphs of that script.

### [Smart Filters](#filtering/smart-filters)

Smart filters show glyphs that match a set of rules.
They appear in the `Filters` section of the left sidebar and are identified by a gear ![](https://handbook.glyphsapp.com/v/content/icons/predicate-filter.svg) icon.
Add a Smart Filter by clicking the actions menu ![](https://handbook.glyphsapp.com/v/content/icons/actions.svg) button located in the bottom-left of the font window and choosing `Add Smart Filter`.
Edit an existing Smart Filter by double-clicking its gear icon, or choose `Edit Filter` from the actions menu for a selected filter.

Adding or editing a Smart Filter opens the Smart Filter editor window.
It controls the name and the rules of a Smart Filter.
The name of the Smart Filter will appear in the `Filters` sidebar.
The rules define which glyphs to include in the filtered group.

When adding a new filter, only one rule is shown in the editor.
Add additional rules by clicking a plus ![](https://handbook.glyphsapp.com/v/content/icons/plus-button.svg) button, and remove a rule by clicking the minus ![](https://handbook.glyphsapp.com/v/content/icons/minus-button.svg) button next to it.

![](https://handbook.glyphsapp.com/v/content/images/root/edit-smart-filter.png)

The following filter rules are available:

Glyph Name
:   The [name](https://handbook.glyphsapp.com/single-page/#glyph/name "Font View ⯈ Glyph Properties ⯈ Glyph Name") of the glyph.

Count of Paths
:   The number of paths of the first master layer.

Count of Components
:   The number of [components](https://handbook.glyphsapp.com/single-page/#components "Reusing Shapes ⯈ Components") of the first master layer.

Tags
:   The [tags](https://handbook.glyphsapp.com/single-page/#glyph/tags "Font View ⯈ Glyph Properties ⯈ Tags") of the glyph.

Script
:   The [script](https://handbook.glyphsapp.com/single-page/#glyph/script "Font View ⯈ Glyph Properties ⯈ Script") to which the glyph belongs.

Category & Subcategory
:   The [category and subcategory](https://handbook.glyphsapp.com/single-page/#glyph/category-and-subcategory "Font View ⯈ Glyph Properties ⯈ Category & Subcategory") of the glyph.

Case
:   Whether the glyph is uppercase, lowercase, small capital, or has no associated case.

Master Compatible
:   Whether the masters [can be interpolated](https://handbook.glyphsapp.com/single-page/#interpolation "Interpolation").

Export Glyph
:   Whether the glyph is included in [exported font files](https://handbook.glyphsapp.com/single-page/#exports "Font Info ⯈ Exports").

Has Unicode
:   Whether the glyph has at least one [Unicode value](https://handbook.glyphsapp.com/single-page/#glyph/unicode "Font View ⯈ Glyph Properties ⯈ Unicode").

Has Components
:   Whether the layer of the selected master of the glyph contains [components](https://handbook.glyphsapp.com/single-page/#components "Reusing Shapes ⯈ Components").
    Use `Contains Component` to check if a specific component is on the layer.

Has Hints
:   Whether the layer of the selected master has any manually placed hints.

Has PostScript Hints
:   Whether the layer of the selected master has any manually placed [PostScript hints](https://handbook.glyphsapp.com/single-page/#postscript-hinting "PostScript Hinting").

Has TrueType Hints
:   Whether the layer of the selected master has any manually placed [TrueType hints](https://handbook.glyphsapp.com/single-page/#truetype-hinting "TrueType Hinting").

Has Corners
:   Whether the layer of the selected master contains [corner components](https://handbook.glyphsapp.com/single-page/#components/corner "Reusing Shapes ⯈ Corner Components").

Has Anchors
:   Whether the layer of the selected master contains any [anchors](https://handbook.glyphsapp.com/single-page/#anchors "Edit View ⯈ Anchors").

Contains Component
:   Whether the layer of the selected master contains a specific [component](https://handbook.glyphsapp.com/single-page/#components "Reusing Shapes ⯈ Components").
    Use `Has Components` to check whether there are any components on the layer.

Has Special Layers
:   Whether the glyph has any [special layers](https://handbook.glyphsapp.com/single-page/#special-layers "Palette ⯈ Layers ⯈ Special Layers").

Has Custom Glyph Info
:   Whether the glyph uses custom glyph info deviating from the [glyph info database](https://handbook.glyphsapp.com/single-page/#glyph-info-database "Font View ⯈ Names & Unicode ⯈ Glyph Info Database").

Has Annotations
:   Whether the layer of the selected master contains [annotations](https://handbook.glyphsapp.com/single-page/#annotation-tool "Edit View ⯈ Annotating").

Is Auto-Aligned
:   Whether the layer of the selected master is [automatically aligned](https://handbook.glyphsapp.com/single-page/#automatic-alignment "Reusing Shapes ⯈ Components ⯈ Automatic Alignment").

Has Metrics Keys
:   Whether any of the glyph metrics use [metrics keys](https://handbook.glyphsapp.com/single-page/#metrics-keys "Spacing & Kerning ⯈ Spacing ⯈ Metrics Keys").

Metrics Keys Out of Sync
:   Whether any [metrics keys](https://handbook.glyphsapp.com/single-page/#metrics-keys "Spacing & Kerning ⯈ Spacing ⯈ Metrics Keys") are out of sync and need to be updated.

Has Kerning Groups
:   Whether the glyph uses [kerning groups](https://handbook.glyphsapp.com/single-page/#kerning/groups "Spacing & Kerning ⯈ Kerning ⯈ Kerning Groups").

Color Label
:   The [color label](https://handbook.glyphsapp.com/single-page/#glyph/color-label "Font View ⯈ Glyph Properties ⯈ Color Label") of the glyph.
    Compare with `Not Set` to filter for glyphs without a color label.

Layer Color Label
:   The [color label](https://handbook.glyphsapp.com/single-page/#glyph/color-label "Font View ⯈ Glyph Properties ⯈ Color Label") of the layer of the selected master.
    Compare with `Not Set` to filter for layers without a color label.

Is Hangul Key
:   Whether the glyph is a Hangul key, according to the `Hangul Composition Groups` custom parameter.

Custom
:   This filter rule can contain a custom glyph predicate expression.
    Such an expression is formulated like a glyph predicate token; see [Glyph Predicate Tokens](https://handbook.glyphsapp.com/single-page/#layout/tokens/glyph-predicate "Feature Code ⯈ Tokens ⯈ Glyph Predicate Tokens") for details.

Rules can also be nested, such that *all* of the rules in a group must apply, *at least one* of the rules in a group must apply, or *none* of the rules in a group may apply for a glyph to be included in the filter.
Create a group of rules by holding down the `Option` key and clicking the dots ![](https://handbook.glyphsapp.com/v/content/icons/dots-button.svg) button.
Then, pick `Any` (at least one nested rule must match), `All` (all nested rules must match), or `None` (no nested rule may match).

### [List Filters](#filtering/list-filters)

A list filter shows all glyphs that are specified in a list of glyph names.
List filters appear in the `Filters` section in the left sidebar with a list ![](https://handbook.glyphsapp.com/v/content/icons/list-filter.svg) icon.
Add a list filter by clicking the actions menu ![](https://handbook.glyphsapp.com/v/content/icons/actions.svg) button located in the bottom-left of the font window and choosing `Add List Filter`.
By default, all selected glyphs are added to the list filter.

**Tip:**

In Font View, make a selection of glyphs and then choose `Copy Glyph Names → One per Line` to copy the glyph names in a format suitable for list filters.
See also [Copy Glyph Names](https://handbook.glyphsapp.com/single-page/#glyph-names/copying "Font View ⯈ Names & Unicode ⯈ Copy Glyph Names").

Glyph names are separated by spaces or line breaks.
Edit an existing list filter by double-clicking its list icon or choosing `Edit Filter` from the actions menu.

Change the name of a filter with the `Name` text field at the top of the list field editor window.
Click `OK` to confirm, or click `Cancel` to discard any changes to the list filter.
Select a list filter from the sidebar to see all glyphs of the font that are in the list.
Glyphs are sorted in the order of the list.
See [Adding From the Sidebar](https://handbook.glyphsapp.com/single-page/#glyph-set/adding/sidebar "Font View ⯈ Managing the Glyph Set ⯈ Adding New Glyphs ⯈ Adding From the Sidebar") for details on adding glyphs from a list filter.

### [Managing Filters](#filtering/managing-filters)

Reorder filters by dragging them up and down in the filters list.
Choose `Add Folder` from the actions menu ![](https://handbook.glyphsapp.com/v/content/icons/actions.svg) to create a filter folder ![](https://handbook.glyphsapp.com/v/content/icons/filter-folder.svg).
Click and drag to move a filter into a folder.
Folders can also be put into other folders.
Hold down the `Command` key to select multiple filters, or hold down `Shift` to select a range of filters.
Font View will show only glyphs that are in all of the selected filters.
Select a folder to show all glyphs belonging to any of the contained filters.

Quickly edit a Smart Filter or list filter by double-clicking its gear ![](https://handbook.glyphsapp.com/v/content/icons/predicate-filter.svg) or list ![](https://handbook.glyphsapp.com/v/content/icons/list-filter.svg) icon.
Double-click a filter name to rename it without opening the editor window.
Or, select a filter and press `Return` to rename it.

Delete a filter by choosing `Remove Filter` from the actions menu ![](https://handbook.glyphsapp.com/v/content/icons/actions.svg).
This also works for filter folders.
Note that removing a folder will also remove all filters inside it.

### [Custom Categories & Languages](#filtering/custom-categories-languages)

Custom entries in the `Categories` and `Languages` sections can be added by creating a `Groups.plist` file in the Glyphs `Info` folder.
See [*Custom Sidebar Entries in Font View*](https://glyphsapp.com/learn/custom-sidebar-entries-in-font-view) for details.