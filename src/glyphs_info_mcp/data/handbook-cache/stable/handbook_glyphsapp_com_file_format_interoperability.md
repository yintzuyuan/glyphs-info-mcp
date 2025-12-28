## [File Format Interoperability](#file-format-interoperability)

The UFO format is generally used when exchanging files with other font editors.
See [Unified Font Object](https://handbook.glyphsapp.com/single-page/#source-formats/ufo "Import & Export ⯈ Source Formats ⯈ Unified Font Object") for details.

FontLab 7 imports and exports Glyphs files natively.
This will preserve more details than exchanging UFO files with FontLab.
For FontLab Studio 5, use the [*Glyphs Import*](https://github.com/schriftgestalt/Glyphs-Scripts/blob/master/Glyphs%20Import.py) and [*Glyphs Export*](https://github.com/schriftgestalt/Glyphs-Scripts/blob/master/Glyphs%20Export.py) macros.
Install them in FontLab Studio 5 by opening Finder and choosing `Go → Go to Folder`.
Enter the path of the FontLab Studio 5 macros folder `~/Library/Application Support/FontLab/Studio 5/Macros/` and press `Return`.
Place the two macro files there and relaunch FontLab Studio 5.
The macros will be available in the macro toolbar.

Note that not all Glyphs features are supported in other font editors.
Exchanging files may thus result in simplified data (for example, decomposed outlines) or missing font information.
Consider keeping a copy of the original Glyphs file for safety.