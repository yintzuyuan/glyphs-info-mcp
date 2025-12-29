[English](README.md) | **繁體中文**

# Glyphs info MCP

整合 [Glyphs](https://glyphsapp.com/) 手冊查詢和 API 查詢功能的統一 MCP 伺服器。

## 🚀 快速開始

### 環境需求

- **Python 3.10+**
- **uv 套件管理器** - MCP 官方建議
- **Claude Desktop** - 用於執行 MCP 伺服器
- **macOS**

### 安裝方式

#### 方法 1：使用 uvx（推薦）

**步驟 1：安裝 uv**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**步驟 2：配置 Claude Desktop**

編輯 `~/Library/Application Support/Claude/claude_desktop_config.json`：

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

重啟 Claude Desktop 即可使用！

---

#### 方法 2：從原始碼安裝（開發者）

**前置條件**：已安裝 uv（見方法 1 步驟 1）

```bash
# Clone 專案（含 submodules）
git clone --recursive https://github.com/yintzuyuan/glyphs-info-mcp.git
cd glyphs-info-mcp

# 安裝相依套件
uv sync
```

配置 Claude Desktop（`~/Library/Application Support/Claude/claude_desktop_config.json`）：

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
> 請將 `/Users/username/glyphs-info-mcp` 替換為你的實際**絕對路徑**。

---

### 驗證安裝

```bash
uv run glyphs-info-mcp
```

應該看到：

```
✅ Glyphs info MCP Server initialized with 8 modules and 53 tools
```

## ✨ 特色功能

- 🔍 **統一搜尋** - 智慧查詢路由，自動識別內容類型
- 🌏 **多語系介面術語** - 支援 Glyphs 14 種語言的 UI 術語查詢
- 📚 **完整手冊查詢** - 涵蓋所有 Glyphs 官方手冊內容
- 🔌 **全面 API 參考** - Python 和 Objective-C API 完整文件
- 🧠 **智慧交叉引用** - 自動關聯相關內容
- 🛠️ **MCP 協議相容** - 標準化工具介面

## 📋 功能總覽

### 運作條件一覽

| 功能模組 | 開箱即用 | 需網路 | 需安裝 Glyphs |
|---------|:-------:|:------:|:------------:|
| Handbook 手冊查詢 | ✅ | 初次建立快取 | - |
| API 參考（Python） | ✅ | - | - |
| API 參考（Obj-C Headers） | - | - | ✅ |
| SDK 文件與範本 | ✅ | - | - |
| mekkablue Scripts | ✅ | - | - |
| Light Table API | ✅ | - | - |
| Vocabulary 術語翻譯 | - | - | ✅ |
| Plugins 本地外掛 | - | - | ✅ |
| Plugins 官方外掛 | - | ✅ | - |
| News 論壇/教學 | - | ✅ | - |

> [!TIP]
> **開箱即用**：使用內建 GlyphsSDK 子模組資料，無需額外設定。
> **需網路**：Handbook 僅初次需要網路建立快取，之後可離線使用。
> **需安裝 Glyphs**：從本機 Glyphs 應用程式讀取資料（Headers 來自 GlyphsCore.framework）。

### MCP 工具（共 53 個）

伺服器提供 8 個模組：

- **Handbook** - 手冊內容搜尋與查詢
- **Vocabulary** - 14 種語言 UI 術語翻譯
- **API (Python)** - Python API 類別與方法查詢
- **API (Obj-C)** - Objective-C Headers 與協定
- **SDK** - SDK 文件與 Xcode 模板
- **Plugins** - 本地與官方外掛搜尋
- **Scripts** - mekkablue 腳本集（358+）
- **News** - 論壇、教學文章搜尋

<details>
<summary>展開完整工具列表</summary>

#### Handbook 模組

| 工具 | 描述 |
|------|------|
| `handbook_search_content` | 搜尋手冊內容 |
| `handbook_get_content` | 取得特定章節內容 |
| `handbook_get_custom_parameter` | 取得 Custom Parameter 詳情 |
| `handbook_list_parameters` | 列出所有參數 |

#### Vocabulary 模組

| 工具 | 描述 |
|------|------|
| `vocab_search_ui_term` | 搜尋 UI 術語 |
| `vocab_get_translation` | 取得術語翻譯 |
| `vocab_translate_term` | 翻譯 UI 術語 |
| `vocab_list_ui_categories` | 列出 UI 術語分類 |

#### API 模組 - Python

| 工具 | 描述 |
|------|------|
| `api_search_python` | 搜尋 Python API |
| `api_get_python_class` | 取得 Python 類別資訊 |
| `api_get_python_member` | 取得 Python 成員資訊 |

#### API 模組 - Objective-C

| 工具 | 描述 |
|------|------|
| `api_search_objc_headers` | 搜尋 Obj-C Headers |
| `api_get_objc_header` | 取得 Obj-C Header 內容 |
| `api_list_plugin_protocols` | 列出外掛協定 |
| `api_get_protocol_methods` | 取得協定方法 |

#### SDK 模組

| 工具 | 描述 |
|------|------|
| `sdk_search_content` | 搜尋 SDK 內容 |
| `sdk_get_content` | 取得 SDK 內容 |
| `sdk_list_xcode_templates` | 列出 Xcode 模板 |
| `sdk_get_xcode_template` | 取得 Xcode 模板 |

#### Plugins 模組

| 工具 | 描述 |
|------|------|
| `plugins_search_local` | 搜尋本地外掛 |
| `plugins_search_official` | 搜尋官方外掛 |
| `plugins_get_info` | 取得外掛資訊 |

#### Scripts 模組 (mekkablue)

| 工具 | 描述 |
|------|------|
| `scripts_search` | 搜尋腳本 |
| `scripts_get` | 取得腳本內容 |
| `scripts_list_categories` | 列出腳本分類 |

#### News 模組

| 工具 | 描述 |
|------|------|
| `news_search_forum` | 搜尋論壇 |
| `news_search_tutorials` | 搜尋教學文章 |
| `news_fetch_tutorial` | 取得教學內容 |

</details>

## 📖 使用指南

### 使用範例

```python
# 手冊查詢
handbook_search_content("kerning")
handbook_get_content("anchors")

# API 查詢
api_search_python("GSFont")
api_get_python_class("GSGlyph")

# UI 術語翻譯
vocab_translate_term("Cancel", "zh-Hant")
```

### 搜尋最佳實踐

- 使用英文術語的核心詞彙
- 優先選擇單一概念關鍵字
- 利用自動查詢類型檢測
- 參考術語對照表進行中英轉換

## 🛠️ 開發

### 環境設定

```bash
# 安裝開發依賴
uv sync --extra dev

# 安裝測試依賴
uv sync --extra test
```

### 程式碼品質

```bash
uv run black src/ tests/      # 格式化
uv run ruff check src/ --fix  # 語法檢查
uv run mypy src/              # 型別檢查
```

### 測試

```bash
uv run pytest                              # 所有測試
uv run pytest tests/test_specific.py       # 特定測試
uv run pytest --cov=src/glyphs_info_mcp    # 覆蓋率
```

## 📚 背景說明

### 開發方式

本專案大部分採用 **Vibe Coding** 方式迭代建造完成，專注於快速功能實現和實用性。

### 資料來源

- **API 參考資料**：從 [Glyphs 官方 GitHub SDK](https://github.com/schriftgestalt/GlyphsSDK) 程式碼轉換而來
- **手冊內容**：從 [Glyphs 官方手冊](https://handbook.glyphsapp.com/) 使用內部解析器抓取整理
- **術語翻譯**：從 Glyphs 應用程式本地化字串檔案（.strings）擷取

### 最佳搭配模型

經過測試，本專案與 **Claude 模型搭配使用效果最佳**，建議在 Claude Desktop 環境中使用。

## ❓ 常見問題

<details>
<summary>找不到 uv 命令</summary>

重啟終端機，或執行 `source ~/.zshrc`

</details>

<details>
<summary>Claude Desktop 無法載入 MCP 伺服器</summary>

1. 確認使用**絕對路徑**（不可使用相對路徑或 `~`）
2. 檢查 JSON 格式是否有語法錯誤
3. 重啟 Claude Desktop

</details>

<details>
<summary>伺服器啟動失敗</summary>

```bash
uv sync --reinstall
python --version  # 需要 3.10+
```

</details>

## ⚙️ 配置

### 環境變數

所有路徑皆會自動偵測，通常無需配置。僅在使用非標準位置時才需設定：

```bash
# export GLYPHS_APP_PATH=/Applications/Glyphs 3.app
# export GLYPHS_APP_HEADERS_PATH=/Applications/Glyphs\ 3.app/Contents/Frameworks/GlyphsCore.framework/Versions/A/Headers
# export GLYPHS_REPOSITORIES_PATH=~/Library/Application\ Support/Glyphs\ 3/Repositories
```

## 🔗 相關資源

- [Glyphs 官方網站](https://glyphsapp.com/)
- [Glyphs 官方手冊](https://handbook.glyphsapp.com/)
- [Glyphs 官方論壇](https://forum.glyphsapp.com/)
- [GlyphsSDK](https://github.com/schriftgestalt/GlyphsSDK)
- [MCP 協議文件](https://modelcontextprotocol.io/)
- [回報問題](https://github.com/yintzuyuan/glyphs-info-mcp/issues)

## 📄 授權

MIT License - 詳見 [LICENSE](LICENSE) 檔案。

---

**Glyphs info MCP** - 讓 Glyphs 知識查詢變得簡單而強大

*最後更新：2025-12-29*
