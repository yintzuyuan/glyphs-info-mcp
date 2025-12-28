#!/usr/bin/env python3
"""
Test LightTableNativeAccessor API parsing functionality
"""

import sys
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

# Add module path
project_root = Path(__file__).parent.parent.parent.parent
shared_core_path = str(project_root / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.repository_scanner import RepositoryScanner
sys.path.insert(0, str(project_root / "modules" / "light_table_api"))
from accessors.light_table_native_accessor import LightTableNativeAccessor


class TestLightTableNativeAccessor:
    """Test Light Table Native Accessor"""

    @pytest.fixture
    def temp_fallback_paths(self) -> Generator[dict[str, Path], None, None]:
        """Create temporary Submodule fallback paths"""
        with tempfile.TemporaryDirectory() as tmpdir:
            submodule_base = Path(tmpdir) / "data" / "official"
            submodule_base.mkdir(parents=True)

            # Create light-table submodule structure
            light_table_sub = submodule_base / "light-table" / "Python API" / "lighttable"
            light_table_sub.mkdir(parents=True)

            # Create API file
            api_content = '''from enum import Enum

class DocumentState(Enum):
    UNKNOWN = 0
    NO_FILE = 1
    NO_REPOSITORY = 2
'''
            (light_table_sub / "__init__.py").write_text(api_content)

            yield {
                "light-table": submodule_base / "light-table",
            }

    def test_detect_lighttable_submodule(self, temp_fallback_paths: dict[str, Path]) -> None:
        """Test Submodule fallback path detection"""
        # Use nonexistent local path
        nonexistent_repo = Path("/nonexistent/plugins")
        scanner = RepositoryScanner(nonexistent_repo, temp_fallback_paths)
        scanner.scan_repositories()

        # Create accessor
        accessor = LightTableNativeAccessor(scanner)

        # Should find submodule path
        assert accessor.is_available()
        assert accessor.api_path is not None
        assert "light-table" in str(accessor.api_path)

    def test_parse_enums(self, temp_fallback_paths: dict[str, Path]) -> None:
        """Test parsing enum types"""
        nonexistent_repo = Path("/nonexistent/plugins")
        scanner = RepositoryScanner(nonexistent_repo, temp_fallback_paths)
        scanner.scan_repositories()

        accessor = LightTableNativeAccessor(scanner)
        accessor.parse_api()

        # Check enums
        enums = accessor.get_enums()
        assert "DocumentState" in enums

        # Check enum values
        doc_state = enums["DocumentState"]
        assert "UNKNOWN" in doc_state["values"]
        assert "NO_FILE" in doc_state["values"]

    def test_search_api_methods(self, temp_fallback_paths: dict[str, Path]) -> None:
        """Test searching API methods"""
        nonexistent_repo = Path("/nonexistent/plugins")
        scanner = RepositoryScanner(nonexistent_repo, temp_fallback_paths)
        scanner.scan_repositories()

        accessor = LightTableNativeAccessor(scanner)
        accessor.parse_api()

        # Search DocumentState
        results = accessor.search("DocumentState")
        assert len(results) > 0
        assert any("DocumentState" in r["name"] for r in results)

    def test_get_enum_details(self, temp_fallback_paths: dict[str, Path]) -> None:
        """Test getting enum detailed information"""
        nonexistent_repo = Path("/nonexistent/plugins")
        scanner = RepositoryScanner(nonexistent_repo, temp_fallback_paths)
        scanner.scan_repositories()

        accessor = LightTableNativeAccessor(scanner)
        accessor.parse_api()

        # Get DocumentState details
        details = accessor.get_enum_details("DocumentState")
        assert details is not None
        assert details["type"] == "enum"
        assert "values" in details
        assert len(details["values"]) >= 2  # At least UNKNOWN and NO_FILE

    def test_list_all_api_items(self, temp_fallback_paths: dict[str, Path]) -> None:
        """Test listing all API items"""
        nonexistent_repo = Path("/nonexistent/plugins")
        scanner = RepositoryScanner(nonexistent_repo, temp_fallback_paths)
        scanner.scan_repositories()

        accessor = LightTableNativeAccessor(scanner)
        accessor.parse_api()

        # List all items
        all_items = accessor.list_all()
        assert len(all_items) > 0
        assert any(item["type"] == "enum" for item in all_items)
