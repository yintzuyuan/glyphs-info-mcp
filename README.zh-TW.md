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
✅ Glyphs info MCP Server initialized with 8 unified tools
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

### MCP 工具（8 個統一入口點）

伺服器提供 8 個統一工具，透過 action 參數路由，減少約 85% 的 context token 成本：

- **handbook** - Glyphs 手冊操作
- **vocabulary** - UI 術語翻譯（14 種語言）
- **api** - Python 與 Objective-C API 參考
- **plugins** - 本地與官方外掛管理
- **scripts** - mekkablue 腳本集（358+）
- **sdk** - SDK 文件與 Xcode 模板
- **news** - 論壇、教學與新聞搜尋
- **lighttable** - Light Table 版本控制 API

<details>
<summary>展開完整工具列表</summary>

#### handbook

| Action | 描述 |
|--------|------|
| `search` | 搜尋手冊內容 |
| `get` | 依檔名取得章節內容 |
| `toc` | 取得目錄結構 |
| `children` | 取得子章節 |
| `parameter` | 取得自訂參數詳情 |
| `list_parameters` | 列出所有自訂參數 |
| `cache` | 快取管理（info/update） |

#### vocabulary

| Action | 描述 |
|--------|------|
| `translate` | 翻譯 UI 術語 |
| `search` | 搜尋 UI 術語 |
| `mapping` | 取得多語系翻譯對照 |
| `categories` | 列出詞彙分類 |

#### api

| Action | 描述 |
|--------|------|
| `search_python` | 搜尋 Python API |
| `get_class` | 取得 Python 類別資訊 |
| `get_member` | 取得類別成員資訊 |
| `search_objc` | 搜尋 Obj-C Headers |
| `get_header` | 取得 Obj-C Header 內容 |
| `list_protocols` | 列出外掛協定 |
| `get_protocol` | 取得協定方法 |
| `convert_objc` | 轉換 Obj-C 為 Python 名稱 |
| `convert_python` | 轉換 Python 為 Obj-C 名稱 |
| `identify_method` | 辨識方法類型 |
| `get_template` | 取得方法實作模板 |
| `search_vanilla` | 搜尋 Vanilla UI 元件 |
| `get_vanilla` | 取得 Vanilla UI 元件 |
| `list_vanilla` | 列出所有 Vanilla UI 元件 |
| `hierarchy` | 取得類別階層 |
| `relationships` | 取得類別關係 |
| `navigate` | 導覽類別結構 |

#### plugins

| Action | 描述 |
|--------|------|
| `search_local` | 搜尋本地外掛 |
| `search_official` | 搜尋官方外掛庫 |
| `get_info` | 取得外掛詳情 |
| `scan` | 掃描儲存庫目錄 |
| `categories` | 列出外掛分類 |

#### scripts

| Action | 描述 |
|--------|------|
| `search` | 搜尋腳本 |
| `get` | 取得腳本詳情 |
| `categories` | 列出腳本分類 |
| `list` | 列出分類中的腳本 |

#### sdk

| Action | 描述 |
|--------|------|
| `search` | 搜尋 SDK 內容 |
| `get` | 取得 SDK 檔案內容 |
| `list_templates` | 列出 Xcode 模板 |
| `get_template` | 取得 Xcode 模板 |
| `list_samples` | 列出 Xcode 範例 |
| `get_sample` | 取得 Xcode 範例 |

#### news

| Action | 描述 |
|--------|------|
| `search_forum` | 搜尋論壇討論 |
| `search_tutorials` | 搜尋教學文章 |
| `fetch_tutorial` | 取得教學內容 |
| `fetch_forum` | 取得論壇貼文 |
| `search_posts` | 搜尋新聞文章 |
| `fetch_content` | 取得新聞內容 |

#### lighttable

| Action | 描述 |
|--------|------|
| `search` | 搜尋 Light Table API |
| `get_enum` | 取得列舉詳情 |
| `list_enums` | 列出所有列舉 |
| `list_all` | 列出所有 API 項目 |

</details>

## 📖 使用指南

### 使用範例

```python
# 手冊查詢
handbook(action="search", query="kerning")
handbook(action="get", filename="anchors.md")

# API 查詢
api(action="search_python", query="GSFont")
api(action="get_class", class_name="GSGlyph")

# UI 術語翻譯
vocabulary(action="translate", term="Cancel", target="zh-Hant")
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

*最後更新：2025-12-30*
