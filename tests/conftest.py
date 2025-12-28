"""Pytest configuration file

設定測試環境，包括 sys.path 配置和條件式測試跳過。
"""

import os
import sys
from pathlib import Path
from typing import Any

import pytest
from _pytest.config import Config
from _pytest.nodes import Item

# 添加 src/shared 到 Python 路徑
project_root = Path(__file__).parent.parent
shared_path = project_root / "src" / "shared"

if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))


# =============================================================================
# 條件式測試跳過邏輯
# =============================================================================

# 跳過條件定義：(marker 名稱, 環境變數, 預設路徑, 跳過原因)
SKIP_CONDITIONS = [
    (
        "requires_glyphs_app",
        "GLYPHS_APP_PATH",
        "/Applications/Glyphs 3.app",
        "Glyphs 3 app not installed",
    ),
    (
        "requires_repositories",
        "GLYPHS_REPOSITORIES_PATH",
        str(Path.home() / "Library" / "Application Support" / "Glyphs 3" / "Repositories"),
        "Glyphs Repositories directory not found",
    ),
]


def pytest_configure(config: Config) -> None:
    """檢測本地資源可用性（支援環境變數覆蓋）"""
    for marker, env_var, default_path, _ in SKIP_CONDITIONS:
        path = os.getenv(env_var, default_path)
        setattr(config, f"{marker}_available", Path(path).exists())


def pytest_collection_modifyitems(config: Config, items: list[Item]) -> None:
    """根據資源可用性自動跳過測試"""
    for item in items:
        for marker, _, _, reason in SKIP_CONDITIONS:
            if marker in item.keywords and not getattr(config, f"{marker}_available"):
                item.add_marker(pytest.mark.skip(reason=reason))
                break
