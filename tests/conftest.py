"""Pytest configuration file

設定測試環境，包括 sys.path 配置。
"""

import sys
from pathlib import Path

# 添加 src/shared 到 Python 路徑
project_root = Path(__file__).parent.parent
shared_path = project_root / "src" / "shared"

if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))
