### Text Tokens

Text tokens provide a way of inserting information dynamically into text fields.
A text token is written as `{{{token}}}` where `token` is one of the following patterns:

versionString

The version number of Glyphs. For example: “3.4”

buildNumber

The build number of Glyphs. For example: “3435”

In the context of a font or instance, `token` can be a key path.
A key path is an expression that uses the Core API to access values of a font (`GSFont`) or instance (`GSInstance`).
For example, the token `{{{fullName}}}` expands a text like “Some Family Regular”.

In the context of a font master, `token` can be the name of a number value.
See Number Values for details.

Properties of glyphs and glyph layer can also be accessed.
First, write the name of the glyph and then the key path for a layer.
For example, `{{{zero:width}}}` expands to a unit width of the glyph zero like “600”.
See Glyph Property Tokens for details.