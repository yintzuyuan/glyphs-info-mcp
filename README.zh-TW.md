[English](README.md) | **繁體中文**

# Glyphs info MCP

整合 Glyphs 手冊查詢和 API 查詢功能的統一 MCP 伺服器。

## 📋 專案概述

Glyphs info MCP 是一個專為 Glyphs 字型設計軟體開發的統一 MCP (Model Context Protocol) 伺服器，為開發者和設計師提供整合的知識查詢平台。

## ⚠️ 重要說明

在使用本專案前，請注意以下幾點重要說明：

### 🏗️ 專案建造方式
- 本專案大部分採用 **Vibe Coding** 方式迭代建造完成，專注於快速功能實現和實用性

### 🌐 網路連線需求
- **論壇搜尋工具**、**教學文章搜尋工具**和**官方新聞搜尋工具**僅能在**聯網狀態下**正常運作
- 本地快取工具可在離線狀態下作為備用選項使用

### 🤖 最佳搭配模型
- 經過測試，本專案與 **Claude 模型搭配使用效果最佳**
- 建議在 Claude Desktop 環境中使用以獲得最佳體驗

### 📊 資料來源說明
- **API 參考資料**：從 Glyphs 官方 GitHub SDK 程式碼轉換而來
- **手冊內容**：從 Glyphs 官方網站使用內部解析器抓取整理
- **術語翻譯**：從 Glyphs 應用程式本地化字串檔案（.strings）擷取，確保用詞與軟體介面一致

### 💡 使用建議
- 優先使用網路搜尋工具獲取最新資訊
- 需要離線使用時可依賴本地快取資料
- 建議配合 Claude 的對話能力進行複雜查詢

## ✨ 特色功能

- 🔍 **統一搜尋** - 智慧查詢路由，自動識別內容類型
- 🌏 **多語系介面術語** - 支援 Glyphs 14 種語言的 UI 術語查詢與對照
- 📚 **完整手冊查詢** - 涵蓋所有 Glyphs 官方手冊內容
- 🔌 **全面 API 參考** - Python 和 Objective-C API 完整文件
- 🧠 **智慧交叉引用** - 自動關聯相關內容和術語
- 🛠️ **MCP 協議相容** - 標準化工具介面，易於整合

## 🚀 快速開始

### 環境需求

- **Python 3.10+** - 必須安裝
- **uv 套件管理器** - MCP 官方建議的套件管理工具
- **Claude Desktop** - 用於執行 MCP 伺服器
- **作業系統**：macOS

### 📦 安裝方式

#### 方法 1：使用 uvx（推薦）

這是最簡單的安裝方式，無需手動下載專案。

**步驟 1：安裝 uv**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**步驟 2：配置 Claude Desktop**

編輯 Claude Desktop 配置檔案（路徑見下方），添加以下內容：

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

適合需要自訂或開發的使用者。

**步驟 1：安裝 uv 套件管理器**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

安裝後重啟終端機以確保 `uv` 命令生效。

**步驟 2：下載專案**

**方法一：Clone 並同時初始化 submodules（推薦）**

```bash
git clone --recursive https://github.com/yintzuyuan/glyphs-info-mcp.git
cd glyphs-info-mcp
```

**方法二：先 Clone 再初始化 submodules**

```bash
git clone https://github.com/yintzuyuan/glyphs-info-mcp.git
cd glyphs-info-mcp
git submodule update --init --recursive
```

> **📦 Git Submodules 說明**：
> 本專案使用 Git Submodule 管理外部資源，包含：
> - **GlyphsSDK**：官方 SDK 文件和範例
> - **mekkablue-scripts**：358+ 實戰腳本集（開箱即用）
> - **vanilla**：UI 框架文件（開箱即用）
>
> 動態路徑切換特色：
> - 優先使用本機安裝（`~/Library/Application Support/Glyphs 3/Repositories/`）
> - 未安裝時自動使用內建 Submodule（無需額外設定）
> - 提供開箱即用體驗，同時保持彈性

#### 步驟 3：安裝相依套件

```bash
# 安裝基本相依套件
uv sync

# （可選）安裝開發相依套件
uv sync --extra dev
```

#### 步驟 4：測試伺服器

```bash
# 測試伺服器是否正常啟動
uv run glyphs-info-mcp
```

如果看到伺服器成功啟動的訊息，表示安裝完成！

要在 Claude Desktop 中使用此 MCP 伺服器，需要編輯配置檔案。

#### 配置檔案位置

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### 配置內容

在 `claude_desktop_config.json` 中添加以下內容：

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

**⚠️ 重要提醒：**
- 請將 `/ABSOLUTE/PATH/TO/glyphs-info-mcp` 替換為你的實際專案路徑
- 必須使用**絕對路徑**，不可使用相對路徑或 `~` 符號

#### 配置範例

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

#### 🔧 故障排除

如果遇到伺服器無法啟動的問題，請檢查：

1. **路徑正確性**：確認 `--directory` 參數使用絕對路徑
2. **JSON 格式**：確認配置檔案無語法錯誤
3. **相依套件**：執行 `uv sync` 重新安裝相依套件
4. **重啟應用**：修改配置後必須重啟 Claude Desktop

#### 套用配置

1. 儲存 `claude_desktop_config.json` 檔案
2. **重新啟動 Claude Desktop**
3. 在對話中測試 MCP 工具是否可用

### 📋 使用範例

配置完成後，你可以在 Claude Desktop 中直接使用以下功能：

```python
# 手冊查詢
handbook_search_content("kerning")           # 搜尋手冊內容
handbook_get_content("anchors")              # 取得特定章節

# API 查詢
api_search_python("GSFont")                  # 搜尋 Python API
api_get_python_class("GSGlyph")              # 取得類別詳情

# UI 術語翻譯
vocab_translate_term("Cancel", "zh-Hant")    # 翻譯 UI 術語
```

### 🛠️ 安裝驗證

#### 驗證 uv 安裝
```bash
uv --version
```
應該顯示版本號，如：`uv 0.1.x`

#### 驗證專案相依套件
```bash
cd glyphs-info-mcp
uv run python -c "import mcp; print('MCP 套件正常')"
```

#### 驗證 MCP 伺服器
```bash
uv run glyphs-info-mcp
```
應該看到類似以下的輸出：
```
✅ Vocabulary module loaded successfully
✅ Handbook module loaded successfully
✅ API module loaded successfully
✅ Glyphs info MCP Server initialized with 8 modules and 53 tools
```

### ❓ 常見問題

#### Q: 找不到 uv 命令
**A:** 確認是否已重啟終端機。若仍有問題，執行 `source ~/.bashrc` 或 `source ~/.zshrc`

#### Q: Claude Desktop 無法載入 MCP 伺服器
**A:** 檢查以下項目：
1. 配置檔案路徑是否正確
2. JSON 格式是否有語法錯誤
3. 專案路徑是否為絕對路徑
4. 是否已重新啟動 Claude Desktop

#### Q: 伺服器啟動失敗
**A:** 常見解決方案：
```bash
# 重新安裝相依套件
uv sync --reinstall

# 檢查 Python 版本（需要 3.10+）
python --version

# 檢查專案完整性
uv run python -m pytest tests/ -v
```

## 🔧 主要功能

### MCP 工具

伺服器提供 **53 個工具**，分布於 **8 個模組**：

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

#### API 模組 - Python API

| 工具 | 描述 |
|------|------|
| `api_search_python` | 搜尋 Python API |
| `api_get_python_class` | 取得 Python 類別資訊 |
| `api_get_python_member` | 取得 Python 成員資訊 |

#### API 模組 - Objective-C API

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

## 📖 使用指南

### 搜尋最佳實踐

- 使用英文術語的核心詞彙
- 優先選擇單一概念關鍵字
- 利用自動查詢類型檢測
- 參考術語對照表進行中英轉換

#### 常用查詢模式

```bash
# API 開發
api_search_python("GSFont")              # 搜尋 Python API 字型類別
api_get_python_class("GSGlyph")          # 取得字元類別詳情

# 功能學習
handbook_search_content("kerning")       # 搜尋手冊字距功能
handbook_get_content("anchors")          # 取得錨點章節內容

# 腳本參考
scripts_search("anchor")                 # 搜尋 mekkablue 腳本範例
```

## 🏗️ 專案結構

```
glyphs-info-mcp/
├── src/
│   └── glyphs_info_mcp/                    # 📦 核心套件
│       ├── __init__.py                      # 套件初始化
│       ├── __main__.py                      # CLI 入口點
│       ├── server.py                        # MCP 伺服器主程式
│       ├── config.py                        # 配置管理
│       ├── modules_config.yaml              # 模組配置檔案
│       ├── modules/                         # 功能模組
│       │   ├── glyphs_handbook/             # 手冊查詢模組
│       │   ├── glyphs_api/                  # API 查詢模組
│       │   ├── glyphs_vocabulary/           # 術語翻譯模組
│       │   ├── glyphs_plugins/              # 外掛資訊模組
│       │   ├── glyphs_news/                 # 新聞與論壇模組
│       │   ├── glyphs_sdk/                  # SDK 文件模組
│       │   ├── light_table_api/             # Light Table API 模組
│       │   └── mekkablue_scripts/           # Mekkablue 腳本模組
│       ├── shared/                          # 共用模組
│       │   ├── core/                        # 核心工具
│       │   └── fetch/                       # 網路擷取工具
│       └── data/                            # 資料檔案
│           ├── api_structure.json           # API 結構定義
│           ├── handbook-cache/              # 手冊快取
│           │   ├── fresh/                   # 最新快取
│           │   └── stable/                  # 穩定快取
│           └── official/                    # 官方資源
│               └── GlyphsSDK/               # Glyphs SDK
├── tests/                                   # 🧪 測試檔案
│   ├── conftest.py                          # 測試配置
│   ├── test_glyphs_api/                     # API 模組測試
│   ├── test_glyphs_handbook/                # 手冊模組測試
│   ├── test_glyphs_plugins/                 # 外掛模組測試
│   ├── test_glyphs_vocabulary/              # 術語模組測試
│   ├── test_shared_core/                    # 共用核心測試
│   └── test_*.py                            # 其他測試檔案
├── pyproject.toml                           # ⚙️ 專案配置
├── README.md                                # 📝 專案說明
└── uv.lock                                  # 🔒 依賴鎖定
```

## 🛠️ 開發

### 開發環境設定

```bash
# 安裝開發依賴
uv sync --extra dev

# 安裝測試依賴
uv sync --extra test
```

### 程式碼品質

```bash
# 程式碼格式化
uv run black src/ tests/

# 語法檢查
uv run ruff check src/ tests/ --fix

# 型別檢查
uv run mypy src/
```

### 測試

```bash
# 執行所有測試
uv run pytest

# 執行特定測試
uv run pytest tests/test_specific.py

# 測試覆蓋率
uv run pytest --cov=src/glyphs_info_mcp
```

## 🎯 使用場景

### 字型設計師
- 快速查詢 Glyphs 功能和操作說明
- 學習進階功能和最佳實踐
- 中英文術語對照和理解

### 外掛開發者
- 查詢 Python/Objective-C API 文件
- 取得類別方法和屬性詳情
- 參考外掛開發範例和模式

### 自動化腳本開發者
- 快速查找 API 和使用範例
- 理解物件關係和繼承結構
- 取得完整的程式碼參考

### 教育工作者
- 結構化的教學內容
- 系統性的知識組織
- 多語言支援的學習資源

## ⚙️ 配置

### 環境變數

所有路徑皆會自動偵測，通常無需配置。僅在使用非標準位置時才需設定：

```bash
# Glyphs 應用程式路徑（自動偵測）
# export GLYPHS_APP_PATH=/Applications/Glyphs 3.app

# Glyphs Objective-C Headers 路徑（自動偵測）
# export GLYPHS_APP_HEADERS_PATH=/Applications/Glyphs\ 3.app/Contents/Frameworks/GlyphsCore.framework/Versions/A/Headers

# Glyphs Repositories 路徑（自動偵測）
# export GLYPHS_REPOSITORIES_PATH=~/Library/Application\ Support/Glyphs\ 3/Repositories
```

## 📊 專案狀態

- **版本：** 1.0.0
- **狀態：** 穩定發佈
- **MCP 協議：** 完全相容
- **授權：** MIT License

## 🔗 相關資源

- [Glyphs 官方網站](https://glyphsapp.com/)
- [Glyphs 官方文件](https://handbook.glyphsapp.com/)
- [Glyphs 官方論壇](https://forum.glyphsapp.com/)
- [Glyphs 學習中心](https://glyphsapp.com/learn)
- [MCP 協議文件](https://modelcontextprotocol.io/)
- [回報問題](https://github.com/yintzuyuan/glyphs-info-mcp/issues)

## 📄 授權

本專案採用 MIT 授權條款。詳細內容請參閱 [LICENSE](LICENSE) 檔案。

---

**Glyphs info MCP** - 讓 Glyphs 知識查詢變得簡單而強大 🚀

*最後更新：2025-12-27*
