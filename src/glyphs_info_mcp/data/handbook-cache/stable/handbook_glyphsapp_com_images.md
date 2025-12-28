## [Images](#font-view/images)

Add an image by dragging it from Finder onto a glyph cell.
The image will be added to the currently active layer.
Alternatively, choose `Glyph → Add Image…` to insert an image file to the selected glyph.

Add images to multiple glyphs at once by choosing `Glyph → Add Image…` and then selecting multiple image files.
The images will be placed on the layer of the current master of the glyphs that correspond to an image name.
For example, `Thorn.png` is added to the glyph `Thorn`, and `Dje-cy.jpeg` is added to `Dje-cy`.

![](https://handbook.glyphsapp.com/v/content/images/root/finder-scans.png)

Note that while glyph names are case-*sensitive* (`A` is different from `a`), file names on macOS are case-*insensitive* by default (`A.png` is considered the same file name as `a.png`).
Uppercase and lowercase files thus cannot coexist in the same folder.
As a workaround, place images for uppercase letters in a different folder than lowercase letters.

Images are shown in Font View when `View → Show Image` is selected.
If a glyph is empty (no paths or components are placed in the glyph), the image is displayed regardless of the `Show Image` option.
See [Edit View: Images](https://handbook.glyphsapp.com/single-page/#edit-view/images "Edit View ⯈ Images") for information on working with images in Edit View.

# [Font Info](#font-info)

The Font Info window contains general information about a Glyphs file, such as the font family name, the masters, the exported font instances, and the OpenType features.
Open Font Info by choosing `File → Font Info…` (`Cmd-I`) or click the Info ![i](https://handbook.glyphsapp.com/v/content/icons/info-indicator.svg) button located in the top-left of the main window.

Font Info is split into multiple tabs.
The [`Font`](https://handbook.glyphsapp.com/single-page/#font "Font Info ⯈ Font"), [`Masters`](https://handbook.glyphsapp.com/single-page/#masters "Font Info ⯈ Masters"), and [`Exports`](https://handbook.glyphsapp.com/single-page/#exports "Font Info ⯈ Exports") tabs control the font metadata with rows of fields.
Click the plus ![](https://handbook.glyphsapp.com/v/content/icons/plus.svg) button to the right of the bold headings to add additional fields.
Click the minus ![](https://handbook.glyphsapp.com/v/content/icons/minus.svg) button to the right of a row to delete it.
For rows with a plus button to the right, hold down the `Option` key to reveal the minus button.
Alternatively, click a row to select it, then delete it by pressing `Cmd-Delete`.

![](https://handbook.glyphsapp.com/v/content/images/root/font-info-font-general.svg)

Some fields can be localized into multiple languages.
These display a language menu and a plus ![](https://handbook.glyphsapp.com/v/content/icons/plus.svg) button to the right of the field.
Click the plus button to add additional localizations and pick the respective language from the languages menu.

Select one or multiple rows by `Command`-clicking and copy them by choosing `Edit → Copy` (`Cmd-C`).
Paste rows with `Edit → Paste` (`Cmd-V`).