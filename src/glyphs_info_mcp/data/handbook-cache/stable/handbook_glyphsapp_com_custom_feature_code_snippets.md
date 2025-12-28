## [Custom Feature Code Snippets](#custom-feature-code-snippets)

When editing [OpenType layout feature code](https://handbook.glyphsapp.com/single-page/#layout/manual-code "Font Info ⯈ Features ⯈ Manual Feature Code"), click the snippets ![](https://handbook.glyphsapp.com/v/content/icons/snippets-button.svg) button located in the bottom-right of the window.
Choose `Show Snippet Folder` to reveal the folder in which additional snippets can be placed.
Snippets are defined in property list files (.plist) named `FeatureSnippetsNAME.plist` where `NAME` is the name of the snippets group.
For example, create a file named `FeatureSnippetsDecomposition.plist`:

```python
(
  {
    title = "Soft Dotted";
    code = "lookupflag UseMarkFilteringSet @TopMark;
sub @SoftDotted' @TopMark by @Dotless;";
  },
  {
    title = "Decompose Precomposed";
    code = "sub @Precomp' lookup decomp @Mark;";
  }
)

```