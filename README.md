**English** | [繁體中文](README.zh-TW.md)

# Glyphs info MCP

A unified MCP server integrating Glyphs handbook queries and API reference lookups.

## 📋 Project Overview

Glyphs info MCP is a unified MCP (Model Context Protocol) server specifically designed for Glyphs font design software, providing developers and designers with an integrated knowledge query platform.

## ⚠️ Important Notes

Please note the following important points before using this project:

### 🏗️ Development Approach
- This project was largely built using **Vibe Coding** iterative development, focusing on rapid feature implementation and practicality

### 🌐 Network Requirements
- **Forum search tools**, **tutorial search tools**, and **official news search tools** only work **when connected to the internet**
- Local cache tools can be used as a fallback option when offline

### 🤖 Recommended Model
- After testing, this project works best with **Claude models**
- We recommend using it in the Claude Desktop environment for the best experience

### 📊 Data Sources
- **API Reference**: Converted from Glyphs official GitHub SDK code
- **Handbook Content**: Scraped and organized from Glyphs official website using an internal parser
- **Terminology Translation**: Extracted from Glyphs application localization string files (.strings), ensuring consistency with the software interface

### 💡 Usage Tips
- Prioritize using network search tools to get the latest information
- Rely on local cache data when offline usage is needed
- Recommended to use Claude's conversational capabilities for complex queries

## ✨ Features

- 🔍 **Unified Search** - Smart query routing with automatic content type detection
- 🌏 **Multilingual UI Terms** - Support for Glyphs UI terminology in 14 languages
- 📚 **Complete Handbook Queries** - Covers all Glyphs official handbook content
- 🔌 **Comprehensive API Reference** - Full documentation for Python and Objective-C APIs
- 🧠 **Smart Cross-referencing** - Automatic linking of related content and terminology
- 🛠️ **MCP Protocol Compatible** - Standardized tool interface, easy to integrate

## 🚀 Quick Start

### Requirements

- **Python 3.10+** - Must be installed
- **uv package manager** - MCP officially recommended package management tool
- **Claude Desktop** - For running the MCP server
- **Operating System**: macOS

### 📦 Installation

#### Method 1: Using uvx (Recommended)

This is the simplest installation method, no manual project download required.

**Step 1: Install uv**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Step 2: Configure Claude Desktop**

Edit the Claude Desktop configuration file (path shown below) and add the following:

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

Suitable for users who need customization or development.

**Step 1: Install uv package manager**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your terminal after installation to ensure the `uv` command is available.

**Step 2: Download the Project**

**Option 1: Clone with submodules (recommended)**

```bash
git clone --recursive https://github.com/yintzuyuan/glyphs-info-mcp.git
cd glyphs-info-mcp
```

**Option 2: Clone and then initialize submodules**

```bash
git clone https://github.com/yintzuyuan/glyphs-info-mcp.git
cd glyphs-info-mcp
git submodule update --init --recursive
```

> **📦 Git Submodules Note**:
> This project uses Git Submodules to manage external resources, including:
> - **GlyphsSDK**: Official SDK documentation and examples
> - **mekkablue-scripts**: 358+ production scripts (ready to use)
> - **vanilla**: UI framework documentation (ready to use)
>
> Dynamic path switching feature:
> - Prioritizes local installation (`~/Library/Application Support/Glyphs 3/Repositories/`)
> - Automatically uses built-in Submodule when not installed (no additional setup needed)
> - Provides out-of-the-box experience while maintaining flexibility

#### Step 3: Install Dependencies

```bash
# Install basic dependencies
uv sync

# (Optional) Install development dependencies
uv sync --extra dev
```

#### Step 4: Test the Server

```bash
# Test if the server starts correctly
uv run glyphs-info-mcp
```

If you see the server startup success message, installation is complete!

To use this MCP server in Claude Desktop, you need to edit the configuration file.

#### Configuration File Location

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### Configuration Content

Add the following to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "glyphs-info-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/glyphs-info-mcp",
        "run",
        "glyphs-info-mcp"
      ]
    }
  }
}
```

**⚠️ Important Notes:**
- Replace `/ABSOLUTE/PATH/TO/glyphs-info-mcp` with your actual project path
- You must use an **absolute path**, relative paths or `~` symbol are not supported

#### Configuration Example

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

#### 🔧 Troubleshooting

If you encounter issues with the server not starting, check:

1. **Path correctness**: Ensure the `--directory` parameter uses an absolute path
2. **JSON format**: Ensure there are no syntax errors in the configuration file
3. **Dependencies**: Run `uv sync` to reinstall dependencies
4. **Restart application**: You must restart Claude Desktop after modifying the configuration

#### Apply Configuration

1. Save the `claude_desktop_config.json` file
2. **Restart Claude Desktop**
3. Test if MCP tools are available in the conversation

### 📋 Usage Examples

After configuration, you can use the following features directly in Claude Desktop:

```python
# Query using MCP tools
search_glyphs("GSFont")          # API class query
search_glyphs("4.1")             # Handbook chapter query
search_glyphs("edit view")       # Feature query
get_class_overview("GSFont")     # Detailed class information
get_handbook_toc()               # Handbook table of contents
```

### 🛠️ Installation Verification

#### Verify uv installation
```bash
uv --version
```
Should display version number, e.g., `uv 0.1.x`

#### Verify project dependencies
```bash
cd glyphs-info-mcp
uv run python -c "import mcp; print('MCP package is working')"
```

#### Verify MCP server
```bash
uv run glyphs-info-mcp
```
You should see output similar to:
```
✅ Vocabulary module loaded successfully
✅ Handbook module loaded successfully
✅ API module loaded successfully
✅ Glyphs info MCP Server initialized with 8 modules and 53 tools
```

### ❓ FAQ

#### Q: Cannot find uv command
**A:** Make sure you've restarted your terminal. If the issue persists, run `source ~/.bashrc` or `source ~/.zshrc`

#### Q: Claude Desktop cannot load the MCP server
**A:** Check the following:
1. Is the configuration file path correct?
2. Is there a JSON syntax error?
3. Is the project path an absolute path?
4. Have you restarted Claude Desktop?

#### Q: Server fails to start
**A:** Common solutions:
```bash
# Reinstall dependencies
uv sync --reinstall

# Check Python version (requires 3.10+)
python --version

# Check project integrity
uv run python -m pytest tests/ -v
```

## 🔧 Main Features

### MCP Tools

| Tool | Description | Purpose |
|------|-------------|---------|
| `search_glyphs` | Unified search entry | Auto-routes queries to appropriate modules |
| `get_handbook_toc` | Handbook TOC | Browse complete chapter structure |
| `find_chapter_content` | Chapter query | Get specific chapter content |
| `search_handbook` | Handbook search | Search keywords in the handbook |
| `search_api` | API search | Query API classes and methods |
| `get_class_overview` | Class information | Get detailed class documentation |
| `get_api_statistics` | API statistics | Display API coverage statistics |

## 📖 User Guide

### Search Best Practices

- Use core words of English terminology
- Prefer single concept keywords
- Utilize automatic query type detection
- Refer to the terminology reference for translations

#### Common Query Patterns
```bash
# API development
search_glyphs("GSFont")              # Query font class
get_class_overview("GSGlyph")        # Get glyph class details

# Feature learning
search_glyphs("kerning")             # Query kerning feature
find_chapter_content("4.1")          # View specific chapter

# Combined queries
search_glyphs("export")              # Mixed search for export-related content
```

## 🏗️ Project Structure

```
glyphs-info-mcp/
├── src/
│   └── glyphs_info_mcp/                    # 📦 Core package
│       ├── __init__.py                      # Package initialization
│       ├── __main__.py                      # CLI entry point
│       ├── server.py                        # MCP server main program
│       ├── config.py                        # Configuration management
│       ├── modules/                         # Feature modules
│       │   ├── glyphs_handbook/             # Handbook query module
│       │   ├── glyphs_api/                  # API query module
│       │   ├── glyphs_vocabulary/           # Terminology translation module
│       │   ├── glyphs_plugins/              # Plugin information module
│       │   ├── glyphs_news/                 # News and forum module
│       │   ├── glyphs_sdk/                  # SDK documentation module
│       │   ├── light_table_api/             # Light Table API module
│       │   └── mekkablue_scripts/           # Mekkablue scripts module
│       └── data/                            # Data files
│           ├── handbook/                    # Handbook Markdown files
│           ├── api/                         # API JSON files
│           ├── vocab/                       # Terminology reference files
│           └── plugins/                     # Plugin cache data
├── tests/                                   # 🧪 Test files
│   ├── test_glyphs_handbook/                # Handbook module tests
│   ├── test_glyphs_api/                     # API module tests
│   ├── test_glyphs_vocabulary/              # Vocabulary module tests
│   ├── test_glyphs_plugins/                 # Plugin module tests
│   └── test_integration/                    # Integration tests
├── modules_config.yaml                      # Module configuration file
├── pyproject.toml                           # ⚙️ Project configuration
├── README.md                                # 📝 Project documentation
└── uv.lock                                  # 🔒 Dependency lock
```

## 🛠️ Development

### Development Environment Setup

```bash
# Install development dependencies
uv sync --extra dev

# Install test dependencies
uv sync --extra test
```

### Code Quality

```bash
# Code formatting
uv run black src/ tests/

# Linting
uv run ruff check src/ tests/ --fix

# Type checking
uv run mypy src/
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific tests
uv run pytest tests/test_specific.py

# Test coverage
uv run pytest --cov=src/glyphs_info_mcp
```

## 🎯 Use Cases

### Type Designers
- Quickly query Glyphs features and operation instructions
- Learn advanced features and best practices
- Chinese-English terminology reference and understanding

### Plugin Developers
- Query Python/Objective-C API documentation
- Get class method and property details
- Reference plugin development examples and patterns

### Automation Script Developers
- Quickly find APIs and usage examples
- Understand object relationships and inheritance structures
- Get complete code references

### Educators
- Structured teaching content
- Systematic knowledge organization
- Multilingual learning resources

## ⚙️ Configuration

### Environment Variables

```bash
# Data path configuration
export GLYPHS_MCP_DATA_PATH=/custom/path/to/data

# Performance tuning
export GLYPHS_MCP_MAX_SEARCH_RESULTS=100
export GLYPHS_MCP_SEARCH_TIMEOUT=60
export GLYPHS_MCP_ENABLE_CACHE=true

# Logging settings
export GLYPHS_MCP_LOG_LEVEL=INFO
```

## 📊 Project Status

- **Version:** 1.0.0
- **Status:** Stable Release
- **MCP Protocol:** Fully Compatible
- **License:** MIT License

## 🔗 Related Resources

- [Glyphs Official Website](https://glyphsapp.com/)
- [Glyphs Official Documentation](https://handbook.glyphsapp.com/)
- [Glyphs Learning Center](https://glyphsapp.com/learn)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [Report Issues](https://github.com/yintzuyuan/glyphs-info-mcp/issues)

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Glyphs info MCP** - Making Glyphs knowledge queries simple and powerful 🚀

*Last updated: 2025-12-27*
