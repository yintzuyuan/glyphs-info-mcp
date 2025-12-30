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
✅ Glyphs info MCP Server initialized with 8 unified tools
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

### MCP Tools (8 Unified Entry Points)

The server provides 8 unified tools with action-based routing, reducing context token cost by ~85%:

- **handbook** - Glyphs Handbook operations
- **vocabulary** - UI terminology translation (14 languages)
- **api** - Python and Objective-C API reference
- **plugins** - Local and official plugin management
- **scripts** - mekkablue script collection (358+)
- **sdk** - SDK documentation and Xcode templates
- **news** - Forum, tutorials, and news search
- **lighttable** - Light Table version control API

<details>
<summary>Expand full tool list</summary>

#### handbook

| Action | Description |
|--------|-------------|
| `search` | Search handbook content |
| `get` | Get chapter content by filename |
| `toc` | Get table of contents |
| `children` | Get chapter children |
| `parameter` | Get custom parameter details |
| `list_parameters` | List all custom parameters |
| `cache` | Cache management (info/update) |

#### vocabulary

| Action | Description |
|--------|-------------|
| `translate` | Translate UI term |
| `search` | Search UI terms |
| `mapping` | Get multi-locale translations |
| `categories` | List vocabulary categories |

#### api

| Action | Description |
|--------|-------------|
| `search_python` | Search Python API |
| `get_class` | Get Python class info |
| `get_member` | Get class member info |
| `search_objc` | Search Obj-C headers |
| `get_header` | Get Obj-C header content |
| `list_protocols` | List plugin protocols |
| `get_protocol` | Get protocol methods |
| `convert_objc` | Convert Obj-C to Python name |
| `convert_python` | Convert Python to Obj-C name |
| `identify_method` | Identify method type |
| `get_template` | Get method implementation template |
| `search_vanilla` | Search Vanilla UI components |
| `get_vanilla` | Get Vanilla UI component |
| `list_vanilla` | List all Vanilla UI components |
| `hierarchy` | Get class hierarchy |
| `relationships` | Get class relationships |
| `navigate` | Navigate class structure |

#### plugins

| Action | Description |
|--------|-------------|
| `search_local` | Search local plugins |
| `search_official` | Search official registry |
| `get_info` | Get plugin details |
| `scan` | Scan repositories directory |
| `categories` | List plugin categories |

#### scripts

| Action | Description |
|--------|-------------|
| `search` | Search scripts |
| `get` | Get script details |
| `categories` | List script categories |
| `list` | List scripts in category |

#### sdk

| Action | Description |
|--------|-------------|
| `search` | Search SDK content |
| `get` | Get SDK file content |
| `list_templates` | List Xcode templates |
| `get_template` | Get Xcode template |
| `list_samples` | List Xcode samples |
| `get_sample` | Get Xcode sample |

#### news

| Action | Description |
|--------|-------------|
| `search_forum` | Search forum discussions |
| `search_tutorials` | Search tutorials |
| `fetch_tutorial` | Fetch tutorial content |
| `fetch_forum` | Fetch forum post |
| `search_posts` | Search news posts |
| `fetch_content` | Fetch news content |

#### lighttable

| Action | Description |
|--------|-------------|
| `search` | Search Light Table API |
| `get_enum` | Get enum details |
| `list_enums` | List all enums |
| `list_all` | List all API items |

</details>

## 📖 Usage Guide

### Usage Examples

```python
# Handbook queries
handbook(action="search", query="kerning")
handbook(action="get", filename="anchors.md")

# API queries
api(action="search_python", query="GSFont")
api(action="get_class", class_name="GSGlyph")

# UI terminology
vocabulary(action="translate", term="Cancel", target="zh-Hant")
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

*Last updated: 2025-12-30*
