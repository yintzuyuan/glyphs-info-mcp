**English** | [繁體中文](README.zh-TW.md)

# Glyphs info MCP

A unified MCP server integrating Glyphs handbook queries and API reference lookups for [Glyphs](https://glyphsapp.com/) font design software.

## 🚀 Quick Start

### Requirements

- **Python 3.10+**
- **uv package manager** - MCP officially recommended
- **Claude Desktop** - For running the MCP server
- **macOS**

### Installation

#### Method 1: Using uvx (Recommended)

**Step 1: Install uv**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Step 2: Configure Claude Desktop**

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "glyphs-info": {
      "command": "uvx",
      "args": ["glyphs-info-mcp"]
    }
  }
}
```

Restart Claude Desktop and you're ready to go!

---

#### Method 2: Install from Source (Developers)

**Prerequisites**: uv installed (see Method 1 Step 1)

```bash
# Clone with submodules
git clone --recursive https://github.com/yintzuyuan/glyphs-info-mcp.git
cd glyphs-info-mcp

# Install dependencies
uv sync
```

Configure Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "glyphs-info-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/username/glyphs-info-mcp",
        "run",
        "glyphs-info-mcp"
      ]
    }
  }
}
```

> [!IMPORTANT]
> Replace `/Users/username/glyphs-info-mcp` with your actual **absolute path**.

---

### Verify Installation

```bash
uv run glyphs-info-mcp
```

You should see:

```
✅ Glyphs info MCP Server initialized with 8 modules and 53 tools
```

## ✨ Features

- 🔍 **Unified Search** - Smart query routing with automatic content type detection
- 🌏 **Multilingual UI Terms** - Support for Glyphs UI terminology in 14 languages
- 📚 **Complete Handbook** - All Glyphs official handbook content
- 🔌 **Full API Reference** - Python and Objective-C API documentation
- 🧠 **Smart Cross-referencing** - Automatic linking of related content
- 🛠️ **MCP Protocol Compatible** - Standardized tool interface

## 📋 Feature Overview

### Operating Requirements

| Module | Out-of-box | Network | Glyphs Required |
|--------|:----------:|:-------:|:---------------:|
| Handbook | ✅ | First cache build | - |
| API (Python) | ✅ | - | - |
| API (Obj-C Headers) | - | - | ✅ |
| SDK Documentation | ✅ | - | - |
| mekkablue Scripts | ✅ | - | - |
| Light Table API | ✅ | - | - |
| Vocabulary | - | - | ✅ |
| Plugins (Local) | - | - | ✅ |
| Plugins (Official) | - | ✅ | - |
| News/Tutorials | - | ✅ | - |

> [!TIP]
> **Out-of-box**: Uses bundled GlyphsSDK submodule data, no extra setup needed.
> **Network**: Handbook only needs network for initial cache, then works offline.
> **Glyphs Required**: Reads from local Glyphs app (Headers from GlyphsCore.framework).

### MCP Tools (53 total)

The server provides 8 modules:

- **Handbook** - Search and query handbook content
- **Vocabulary** - UI terminology translation in 14 languages
- **API (Python)** - Python API classes and methods
- **API (Obj-C)** - Objective-C headers and protocols
- **SDK** - SDK documentation and Xcode templates
- **Plugins** - Local and official plugin search
- **Scripts** - mekkablue script collection (358+)
- **News** - Forum and tutorial search

<details>
<summary>Expand full tool list</summary>

#### Handbook Module

| Tool | Description |
|------|-------------|
| `handbook_search_content` | Search handbook content |
| `handbook_get_content` | Get specific chapter content |
| `handbook_get_custom_parameter` | Get Custom Parameter details |
| `handbook_list_parameters` | List all parameters |

#### Vocabulary Module

| Tool | Description |
|------|-------------|
| `vocab_search_ui_term` | Search UI terms |
| `vocab_get_translation` | Get term translation |
| `vocab_translate_term` | Translate UI term |
| `vocab_list_ui_categories` | List UI term categories |

#### API Module - Python

| Tool | Description |
|------|-------------|
| `api_search_python` | Search Python API |
| `api_get_python_class` | Get Python class info |
| `api_get_python_member` | Get Python member info |

#### API Module - Objective-C

| Tool | Description |
|------|-------------|
| `api_search_objc_headers` | Search Obj-C headers |
| `api_get_objc_header` | Get Obj-C header content |
| `api_list_plugin_protocols` | List plugin protocols |
| `api_get_protocol_methods` | Get protocol methods |

#### SDK Module

| Tool | Description |
|------|-------------|
| `sdk_search_content` | Search SDK content |
| `sdk_get_content` | Get SDK content |
| `sdk_list_xcode_templates` | List Xcode templates |
| `sdk_get_xcode_template` | Get Xcode template |

#### Plugins Module

| Tool | Description |
|------|-------------|
| `plugins_search_local` | Search local plugins |
| `plugins_search_official` | Search official plugins |
| `plugins_get_info` | Get plugin info |

#### Scripts Module (mekkablue)

| Tool | Description |
|------|-------------|
| `scripts_search` | Search scripts |
| `scripts_get` | Get script content |
| `scripts_list_categories` | List script categories |

#### News Module

| Tool | Description |
|------|-------------|
| `news_search_forum` | Search forum |
| `news_search_tutorials` | Search tutorials |
| `news_fetch_tutorial` | Fetch tutorial content |

</details>

## 📖 Usage Guide

### Usage Examples

```python
# Handbook queries
handbook_search_content("kerning")
handbook_get_content("anchors")

# API queries
api_search_python("GSFont")
api_get_python_class("GSGlyph")

# UI terminology
vocab_translate_term("Cancel", "zh-Hant")
```

### Search Best Practices

- Use core English terminology words
- Prefer single concept keywords
- Utilize automatic query type detection
- Refer to the terminology reference for translations

## 🛠️ Development

### Setup

```bash
# Install development dependencies
uv sync --extra dev

# Install test dependencies
uv sync --extra test
```

### Code Quality

```bash
uv run black src/ tests/      # Formatting
uv run ruff check src/ --fix  # Linting
uv run mypy src/              # Type checking
```

### Testing

```bash
uv run pytest                              # All tests
uv run pytest tests/test_specific.py       # Specific tests
uv run pytest --cov=src/glyphs_info_mcp    # Coverage
```

## 📚 Background

### Development Approach

This project was largely built using **Vibe Coding** iterative development, focusing on rapid feature implementation and practicality.

### Data Sources

- **API Reference**: Converted from [Glyphs official GitHub SDK](https://github.com/schriftgestalt/GlyphsSDK) code
- **Handbook Content**: Scraped from [Glyphs official handbook](https://handbook.glyphsapp.com/) using an internal parser
- **Terminology Translation**: Extracted from Glyphs app localization string files (.strings)

### Recommended Model

After testing, this project works best with **Claude models**. We recommend using it in the Claude Desktop environment for the best experience.

## ❓ FAQ

<details>
<summary>Cannot find uv command</summary>

Restart your terminal, or run `source ~/.zshrc`

</details>

<details>
<summary>Claude Desktop cannot load the MCP server</summary>

1. Ensure the path is an **absolute path** (not relative or using `~`)
2. Check for JSON syntax errors
3. Restart Claude Desktop

</details>

<details>
<summary>Server fails to start</summary>

```bash
uv sync --reinstall
python --version  # Requires 3.10+
```

</details>

## ⚙️ Configuration

### Environment Variables

All paths are auto-detected. Only set these if using non-standard locations:

```bash
# export GLYPHS_APP_PATH=/Applications/Glyphs 3.app
# export GLYPHS_APP_HEADERS_PATH=/Applications/Glyphs\ 3.app/Contents/Frameworks/GlyphsCore.framework/Versions/A/Headers
# export GLYPHS_REPOSITORIES_PATH=~/Library/Application\ Support/Glyphs\ 3/Repositories
```

## 🔗 Resources

- [Glyphs Official Website](https://glyphsapp.com/)
- [Glyphs Handbook](https://handbook.glyphsapp.com/)
- [Glyphs Forum](https://forum.glyphsapp.com/)
- [GlyphsSDK](https://github.com/schriftgestalt/GlyphsSDK)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Report Issues](https://github.com/yintzuyuan/glyphs-info-mcp/issues)

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

**Glyphs info MCP** - Making Glyphs knowledge queries simple and powerful

*Last updated: 2025-12-29*
