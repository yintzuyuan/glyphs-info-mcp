"""Pytest configuration file

設定測試環境，包括 sys.path 配置和條件式測試跳過。
"""

import os
import sys
from pathlib import Path

import pytest

# 添加 src/shared 到 Python 路徑
project_root = Path(__file__).parent.parent
shared_path = project_root / "src" / "shared"

if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))


# =============================================================================
# 條件式測試跳過邏輯
# =============================================================================

def pytest_configure(config):
    """檢測本地資源可用性"""
    # 檢測 Glyphs 3 app
    config.glyphs_app_available = Path("/Applications/Glyphs 3.app").exists()

    # 檢測 Repositories 目錄
    config.repositories_available = (
        Path.home() / "Library" / "Application Support" / "Glyphs 3" / "Repositories"
    ).exists()

    # 檢測 CI 環境
    config.is_ci = os.getenv("CI") == "true"


def pytest_collection_modifyitems(config, items):
    """根據資源可用性自動跳過測試"""
    for item in items:
        # 需要 Glyphs 3 app 的測試
        if "requires_glyphs_app" in item.keywords and not config.glyphs_app_available:
            item.add_marker(
                pytest.mark.skip(reason="Glyphs 3 app not installed")
            )

        # 需要 Repositories 目錄的測試
        if "requires_repositories" in item.keywords and not config.repositories_available:
            item.add_marker(
                pytest.mark.skip(reason="Glyphs Repositories directory not found")
            )
