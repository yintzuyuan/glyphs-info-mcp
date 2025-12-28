## [Projects](#projects)

Projects are collections of instance definitions linked to a Glyphs font file but kept in a separate project file.
This is useful for setting up different font versions without altering or compromising the original Glyphs file.
Project files carry a `.glyphsproject` suffix.

### [Setting up a Project](#projects/setup)

Create a new Glyphs project with `File → New Project`.
Save the newly created project with `File → Save` (`Cmd-S`).

Click the `Choose` button located in the top-right of the project window, select a Glyphs file, and confirm with `Choose`.
The selected font does not need to be open in Glyphs.
This *links* the Glyphs file to the project.
Click the file path to choose a different Glyphs file.
The instances of the font are listed in the sidebar of the project window:

![](https://handbook.glyphsapp.com/v/content/images/root/project-window.png)

Rearrange instances using drag and drop.
Duplicate an instance by `Option`-dragging it to its new location in the list.
Alternatively, copy (`Cmd-C`) and paste (`Cmd-V`) to duplicate the selected instances.
Click the plus ![](https://handbook.glyphsapp.com/v/content/icons/plus-button.svg) button to add new instances and variable font settings.
Delete the selected instances with the minus ![](https://handbook.glyphsapp.com/v/content/icons/minus-button.svg) button.
Revert to the instances of the Glyphs file with the arrow ![](https://handbook.glyphsapp.com/v/content/icons/arrow-update-button.svg) button.

Edit the parameters of instances in the right half of the project window.
See [Font Info: Exports](https://handbook.glyphsapp.com/single-page/#exports "Font Info ⯈ Exports") for details.

### [Exporting a Project](#projects/exporting-a-project)

Ensure that the project is saved (`File → Save`, `Cmd-S`) and that the path to the linked font is valid (a path becomes invalid when the linked file is renamed, moved, or deleted).
Click the `Export Destination` file path to set the export folder.
Instances are exported into this folder.
Customize the export folder of an instance with the `Export Folder` custom parameter (see [Export Destination](https://handbook.glyphsapp.com/single-page/#export/opentype/export-destination "Import & Export ⯈ Exporting Font Files ⯈ OpenType Export ⯈ Export Destination")).
Click the `Export` button located in the bottom-right of the project window to export all configured instances.
The linked Glyphs file does not need to be open for export.

# [Spacing & Kerning](#spacing-and-kerning)

The space between glyphs is controlled by their spacing and kerning.
*Spacing* defines the general white space surrounding a glyph, while *kerning* makes adjustments to specific glyph pairs.