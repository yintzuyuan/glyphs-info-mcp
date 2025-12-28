.PHONY: help install dev clean test lint format type-check run validate

help:
	@echo "Glyphs MCP 開發工具"
	@echo ""
	@echo "可用指令:"
	@echo "  install     安裝專案依賴"
	@echo "  dev         安裝開發依賴"
	@echo "  clean       清理快取檔案"
	@echo "  test        執行測試"
	@echo "  lint        程式碼檢查"
	@echo "  format      格式化程式碼"
	@echo "  type-check  類型檢查"
	@echo "  run         啟動伺服器"
	@echo "  validate    驗證配置"

install:
	uv sync

dev:
	uv sync --extra dev --extra test

clean:
	find . -type d -name "__pycache__" | xargs rm -rf
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/

test:
	uv run pytest

lint:
	uv run ruff check src/ tests/

format:
	uv run black src/ tests/
	uv run ruff check src/ tests/ --fix

type-check:
	uv run mypy src/

run:
	uv run glyphs-info-mcp serve

validate:
	uv run glyphs-info-mcp validate

check: format lint type-check test
	@echo "✅ 所有檢查通過"
