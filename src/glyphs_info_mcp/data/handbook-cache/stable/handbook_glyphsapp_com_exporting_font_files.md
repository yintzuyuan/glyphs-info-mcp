## [Exporting Font Files](#export)

Choose `File → Export…` (`Cmd-E`) to show the export dialog for the currently open Glyphs file.
Hold down the `Option` key and choose `Export All` (`Cmd-Opt-E`) to export all open Glyphs files without showing an export dialog.
Exported files overwrite existing files.

The export dialog offers different export formats.
These are described in the following sections.

### [OpenType Export](#export/opentype)

![](https://handbook.glyphsapp.com/v/content/images/root/export-dialog-opentype.png)

The `OTF` tab exports static OpenType fonts.
This export option uses the [font instances](https://handbook.glyphsapp.com/single-page/#interpolation/setup-instances/static "Interpolation ⯈ Setting up Instances ⯈ Static Instances") or, if none are configured, a default instance based on the first master.

#### [Outline Flavor](#export/opentype/outline-flavor)

There are two flavors of OpenType fonts.
Their main difference is the types of glyph outlines that they contain.

- PostScript/CFF flavor files containing a `CFF` (Compact Font Format) table storing glyph outlines as cubic Bézier curves.
  Font files with this flavor typically end in `.otf`.
- TrueType flavor files containing a `glyf` table storing glyph outlines as quadratic Bézier curves and other tables related to the TrueType format.
  Font files with this flavor typically end in `.ttf`.

Pick one of the two outline flavors.
Paths drawn in Glyphs are cubic, but Glyphs can also edit quadratic paths.
When exporting to TrueType, Glyphs creates quadratic paths from the cubic paths stored in the Glyphs file.
This might introduce minuscule differences between the drawn and the exported glyph outlines.

Besides the paths, the two flavors differ in their hinting capabilities; see [PostScript Hinting](https://handbook.glyphsapp.com/single-page/#postscript-hinting "PostScript Hinting") and [TrueType Hinting](https://handbook.glyphsapp.com/single-page/#truetype-hinting "TrueType Hinting") for details.
Exporting to TrueType keeps components without converting them to outlines; see [Reusing Shapes: Components](https://handbook.glyphsapp.com/single-page/#components "Reusing Shapes ⯈ Components") for details.

#### [File Format](#export/opentype/file-format)

The first option (`.otf` or `.ttf`) is generally used to install a font in an operating system and use the font in graphic design and word-processing applications.
WOFF (`.woff`) and WOFF2 (`.woff2`) are intended for usage on the web (Web Open Font Format).
Check all formats that should be exported.

#### [Options](#export/opentype/options)

The `Remove Overlap` option unifies all paths and components in glyph layers as not to include overlapping paths.
This is the same operation as `Path → Remove Overlap`; see [Remove Overlap](https://handbook.glyphsapp.com/single-page/#filters/remove-overlap "Filters ⯈ Built-in Filters ⯈ Remove Overlap") for details.
Release versions of fonts should have this option checked; uncheck it only during development for faster exports or if the `Remove Overlap` filter is already applied using custom parameters.

Check the `Autohint` option to apply automatic hinting.
If the `PostScript/CFF` flavor is selected, autohinting is applied to all glyphs that do not contain manual PostScript hints; see [PostScript Hinting: Autohinting](https://handbook.glyphsapp.com/single-page/#postscript-hinting/autohinting "PostScript Hinting ⯈ Autohinting").
For the `TrueType` flavor, autohinting is applied to the entire font, and any manually added TT hints will be ignored; see [TrueType Hinting: Autohinting](https://handbook.glyphsapp.com/single-page/#truetype-hinting/autohinting "TrueType Hinting ⯈ Autohinting").

#### [Export Destination](#export/opentype/export-destination)

The export dialog offers two possible export destinations.

- Select the checkbox next to the file path to export to the chosen folder.
  Choose a different folder by clicking the file path and picking a folder from the file browser dialog.
  Common destinations are the system font library `Username → Library → Fonts` and the Adobe fonts folder `Username → Library → Application Support → Adobe → Fonts`.
- Select the `Test Install` checkbox to install the fonts directly on the Mac without exporting any font files.
  This writes the font data directly into the Mac font system.
  The exported fonts will be available in apps using the system font framework Core Text (such as Pages, Final Cut, and Pixelmator, but not Adobe or Affinity apps).
  Test installed fonts bypass many font caching issues, but they need to be re-installed after a reboot.

Click the `Next…` button to export to the selected destination.
If neither export destination is checked, Glyphs will prompt for an export folder.

The export destination can be customized per instance in `File → Font Info… → Exports` by adding an `Export Folder` custom parameter.
The instance will be exported to that this folder relative to the selected export destination.
The export folder may contain slashes (`/`) to export to a nested folder structure (such as `Trial Versions/Webfonts`).
Place the export folder outside the export destination by going up folder levels with two dots (`..`, such as `../Trial Versions`).

### [Exporting Variable Fonts](#export/variable-fonts)

![](https://handbook.glyphsapp.com/v/content/images/root/export-dialog-variable-fonts.png)

The `Variable Fonts` tab exports variable OpenType fonts.
This export option uses the [variable font settings](https://handbook.glyphsapp.com/single-page/#interpolation/setup-instances/variable "Interpolation ⯈ Setting up Instances ⯈ Variable Font Settings") or, if none are configured, a default variable font setting.

Set the desired file formats and export destination like in the `OTF` tab.
Variable fonts are always exported in the TrueType flavor.

### [Exporting UFO](#export/ufo)

![](https://handbook.glyphsapp.com/v/content/images/root/export-dialog-ufo.png)

The `UFO` tab exports the selected masters as UFO (Unified Font Object) files.
Select one or multiple masters to be exported to UFO by `Command`-clicking entries in the masters list.
Select a range of masters by `Shift`-clicking or all by choosing `Edit → Select All` (`Cmd-A`).

Check `Convert Glyph Names to Production Names` to use the glyph production names instead of the nice names used inside Glyphs.
This option is helpful when working on the exported UFO files with tools expecting a simplified naming scheme compared to the more expressive names used by Glyphs.
See [Glyph Name](https://handbook.glyphsapp.com/single-page/#glyph/name "Font View ⯈ Glyph Properties ⯈ Glyph Name") for more on the difference between nice names and production names.

`Decompose Smart Stuff` handles Glyphs-specific features such as smart components or corner components to regular paths.
The UFO format does not support these smart components.
Check this option to convert unsupported Glyphs features to regular paths or leave it unchecked to remove them.

Click `Next…` to choose an export destination.
UFO files are exported in the UFO version 3 format.
See [Unified Font Object](https://handbook.glyphsapp.com/single-page/#source-formats/ufo "Import & Export ⯈ Source Formats ⯈ Unified Font Object") for details on working with UFO files.

### [Exporting Metrics](#export/metrics)

![](https://handbook.glyphsapp.com/v/content/images/root/export-dialog-metrics.png)

The `Metrics` tab exports the font metrics of the current master.
The current master is the master that is [currently selected in the toolbar](https://handbook.glyphsapp.com/single-page/#previewing-masters "Edit View ⯈ Previewing & Testing ⯈ Previewing Masters").

Click `Next…` to choose the export destination and the export format.
There are two metrics formats to choose from:

- Metrics File is a proprietary Glyphs metrics format containing all spacing and kerning information of the master.
- AFM File (Adobe Font Metrics) is an old-style format that is compatible with other font editors.
  However, it cannot contain all types of metrics information.
  For instance, AFM does not support group kerning or metrics keys.

See [Importing Metrics](https://handbook.glyphsapp.com/single-page/#import/metrics "Import & Export ⯈ Importing Font Data ⯈ Importing Metrics") for details on importing these metrics files into a Glyphs file.