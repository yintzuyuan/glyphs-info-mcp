"""
測試 SourceCollector - 原始碼收集器

TDD 紅燈階段:先撰寫測試,預期失敗
"""

import plistlib
from pathlib import Path

import pytest

from glyphs_info_mcp.modules.glyphs_plugins.accessors.file_classifier import FileClassifier
from glyphs_info_mcp.modules.glyphs_plugins.accessors.source_collector import SourceCollector


class TestSourceCollector:
    """測試原始碼收集器"""

    @pytest.fixture
    def python_plugin(self, tmp_path: Path) -> Path:
        """建立 Python 外掛結構"""
        plugin_dir = tmp_path / "PythonPlugin"
        plugin_dir.mkdir()

        bundle_dir = plugin_dir / "PythonPlugin.glyphsReporter"
        bundle_dir.mkdir()
        contents_dir = bundle_dir / "Contents"
        contents_dir.mkdir()
        resources_dir = contents_dir / "Resources"
        resources_dir.mkdir()

        # Info.plist
        info_plist = {
            "CFBundleName": "PythonPlugin",
            "CFBundleIdentifier": "com.test.PythonPlugin",
            "CFBundleShortVersionString": "1.0",
        }
        with open(contents_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist, f)

        # plugin.py
        (resources_dir / "plugin.py").write_text(
            "# encoding: utf-8\nclass PythonPlugin:\n    pass\n", encoding="utf-8"
        )

        # helper.py
        (resources_dir / "helper.py").write_text(
            "def helper_function():\n    return True\n", encoding="utf-8"
        )

        # README.md
        (plugin_dir / "README.md").write_text("# Python Plugin\n")

        # Binary stub (Mach-O)
        (resources_dir / "PythonPlugin").write_bytes(
            b"\xcf\xfa\xed\xfe" + b"\x00" * 100
        )

        return plugin_dir

    @pytest.fixture
    def objc_plugin(self, tmp_path: Path) -> Path:
        """建立 Objective-C 外掛結構"""
        plugin_dir = tmp_path / "ObjCPlugin"
        plugin_dir.mkdir()

        bundle_dir = plugin_dir / "ObjCPlugin.glyphsReporter"
        bundle_dir.mkdir()
        contents_dir = bundle_dir / "Contents"
        contents_dir.mkdir()
        resources_dir = contents_dir / "Resources"
        resources_dir.mkdir()

        # Info.plist
        info_plist = {
            "CFBundleName": "ObjCPlugin",
            "CFBundleIdentifier": "com.test.ObjCPlugin",
            "CFBundleShortVersionString": "1.0",
        }
        with open(contents_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist, f)

        # ObjCPlugin.h
        (resources_dir / "ObjCPlugin.h").write_text(
            "#import <Cocoa/Cocoa.h>\n@interface ObjCPlugin : NSObject\n@end\n",
            encoding="utf-8",
        )

        # ObjCPlugin.m
        (resources_dir / "ObjCPlugin.m").write_text(
            '#import "ObjCPlugin.h"\n@implementation ObjCPlugin\n@end\n',
            encoding="utf-8",
        )

        # README.md
        (plugin_dir / "README.md").write_text("# ObjC Plugin\n")

        return plugin_dir

    @pytest.fixture
    def mixed_plugin(self, tmp_path: Path) -> Path:
        """建立混合外掛結構（Python + Objective-C）"""
        plugin_dir = tmp_path / "MixedPlugin"
        plugin_dir.mkdir()

        bundle_dir = plugin_dir / "MixedPlugin.glyphsReporter"
        bundle_dir.mkdir()
        contents_dir = bundle_dir / "Contents"
        contents_dir.mkdir()
        resources_dir = contents_dir / "Resources"
        resources_dir.mkdir()

        # Info.plist
        info_plist = {
            "CFBundleName": "MixedPlugin",
            "CFBundleIdentifier": "com.test.MixedPlugin",
            "CFBundleShortVersionString": "1.0",
        }
        with open(contents_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist, f)

        # Python files
        (resources_dir / "plugin.py").write_text(
            "# encoding: utf-8\nclass MixedPlugin:\n    pass\n", encoding="utf-8"
        )

        # Objective-C files
        (resources_dir / "Helper.h").write_text(
            "#import <Cocoa/Cocoa.h>\n@interface Helper : NSObject\n@end\n",
            encoding="utf-8",
        )
        (resources_dir / "Helper.m").write_text(
            '#import "Helper.h"\n@implementation Helper\n@end\n', encoding="utf-8"
        )

        # UI file
        (resources_dir / "View.xib").write_text(
            '<?xml version="1.0"?>\n<document type="com.apple.InterfaceBuilder3.Cocoa.XIB">\n</document>\n',
            encoding="utf-8",
        )

        # README.md
        (plugin_dir / "README.md").write_text("# Mixed Plugin\n")

        return plugin_dir

    @pytest.fixture
    def binary_only_plugin(self, tmp_path: Path) -> Path:
        """建立純二進位外掛（無原始碼）"""
        plugin_dir = tmp_path / "BinaryOnlyPlugin"
        plugin_dir.mkdir()

        bundle_dir = plugin_dir / "BinaryOnlyPlugin.glyphsReporter"
        bundle_dir.mkdir()
        contents_dir = bundle_dir / "Contents"
        contents_dir.mkdir()
        macos_dir = contents_dir / "MacOS"
        macos_dir.mkdir()

        # Info.plist
        info_plist = {
            "CFBundleName": "BinaryOnlyPlugin",
            "CFBundleIdentifier": "com.test.BinaryOnlyPlugin",
            "CFBundleShortVersionString": "1.0",
        }
        with open(contents_dir / "Info.plist", "wb") as f:
            plistlib.dump(info_plist, f)

        # Binary executable only
        (macos_dir / "BinaryOnlyPlugin").write_bytes(
            b"\xcf\xfa\xed\xfe" + b"\x00" * 1000
        )

        return plugin_dir

    def test_collect_python_plugin_sources(self, python_plugin: Path) -> None:
        """測試收集 Python 外掛原始碼"""
        classifier = FileClassifier()
        collector = SourceCollector(classifier)

        result = collector.collect_source_files(python_plugin)

        # 應該包含 Python 原始碼
        assert "python_source" in result
        assert len(result["python_source"]) == 2  # plugin.py, helper.py

        # 應該識別二進位檔案
        assert "binary_stub" in result
        assert len(result["binary_stub"]) >= 1

        # 應該包含資源檔案
        assert "resource" in result
        assert any("README.md" in str(f) for f in result["resource"])

    def test_collect_objc_plugin_sources(self, objc_plugin: Path) -> None:
        """測試收集 Objective-C 外掛原始碼"""
        classifier = FileClassifier()
        collector = SourceCollector(classifier)

        result = collector.collect_source_files(objc_plugin)

        # 應該包含 Objective-C 原始碼
        assert "objc_header" in result
        assert len(result["objc_header"]) == 1
        assert "objc_impl" in result
        assert len(result["objc_impl"]) == 1

        # 應該包含資源檔案
        assert "resource" in result

    def test_collect_mixed_plugin_sources(self, mixed_plugin: Path) -> None:
        """測試收集混合外掛原始碼"""
        classifier = FileClassifier()
        collector = SourceCollector(classifier)

        result = collector.collect_source_files(mixed_plugin)

        # 應該同時包含 Python 和 Objective-C
        assert "python_source" in result
        assert "objc_header" in result
        assert "objc_impl" in result

        # 應該包含 UI 檔案
        assert "ui_xib" in result
        assert len(result["ui_xib"]) == 1

    def test_collect_respects_file_size_limit(self, tmp_path: Path) -> None:
        """測試檔案大小限制"""
        plugin_dir = tmp_path / "LargePlugin"
        plugin_dir.mkdir()

        # 建立超大檔案（150KB）
        large_file = plugin_dir / "large.py"
        large_file.write_text("# " + "x" * 150_000, encoding="utf-8")

        # 建立正常檔案（50KB）
        normal_file = plugin_dir / "normal.py"
        normal_file.write_text("# " + "x" * 50_000, encoding="utf-8")

        classifier = FileClassifier()
        collector = SourceCollector(classifier, max_file_size=100_000)

        result = collector.collect_source_files(plugin_dir)

        # 應該只包含 normal.py
        assert "python_source" in result
        assert len(result["python_source"]) == 1
        assert result["python_source"][0].name == "normal.py"

    def test_collect_respects_total_size_limit(self, tmp_path: Path) -> None:
        """測試總大小限制"""
        plugin_dir = tmp_path / "ManyFilesPlugin"
        plugin_dir.mkdir()

        # 建立 10 個 60KB 的檔案（總共 600KB）
        for i in range(10):
            (plugin_dir / f"file{i}.py").write_text(
                f"# File {i}\n" + "x" * 60_000, encoding="utf-8"
            )

        classifier = FileClassifier()
        collector = SourceCollector(
            classifier, max_file_size=100_000, max_total_size=500_000
        )

        result = collector.collect_source_files(plugin_dir)

        # 應該收集到限制為止（約 8 個檔案）
        assert "python_source" in result
        total_files = len(result["python_source"])
        assert total_files < 10  # 不會全部收集
        assert total_files >= 8  # 至少收集 8 個 (480KB < 500KB)

    def test_collect_excludes_hidden_files(self, tmp_path: Path) -> None:
        """測試排除隱藏檔案"""
        plugin_dir = tmp_path / "HiddenFilesPlugin"
        plugin_dir.mkdir()

        # 正常檔案
        (plugin_dir / "visible.py").write_text("# Visible\n", encoding="utf-8")

        # 隱藏檔案
        (plugin_dir / ".hidden.py").write_text("# Hidden\n", encoding="utf-8")

        # 隱藏目錄
        hidden_dir = plugin_dir / ".hidden_dir"
        hidden_dir.mkdir()
        (hidden_dir / "file.py").write_text("# In hidden dir\n", encoding="utf-8")

        classifier = FileClassifier()
        collector = SourceCollector(classifier)

        result = collector.collect_source_files(plugin_dir)

        # 應該只包含 visible.py
        assert "python_source" in result
        assert len(result["python_source"]) == 1
        assert result["python_source"][0].name == "visible.py"

    def test_collect_excludes_pycache(self, tmp_path: Path) -> None:
        """測試排除 __pycache__ 目錄"""
        plugin_dir = tmp_path / "PyCachePlugin"
        plugin_dir.mkdir()

        # 正常檔案
        (plugin_dir / "plugin.py").write_text("# Plugin\n", encoding="utf-8")

        # __pycache__ 目錄
        pycache_dir = plugin_dir / "__pycache__"
        pycache_dir.mkdir()
        (pycache_dir / "plugin.cpython-312.pyc").write_bytes(
            b"\x42\x0d\x0d\x0a" + b"\x00" * 50
        )

        classifier = FileClassifier()
        collector = SourceCollector(classifier)

        result = collector.collect_source_files(plugin_dir)

        # 應該只包含 plugin.py
        assert "python_source" in result
        assert len(result["python_source"]) == 1
        assert "__pycache__" not in str(result["python_source"][0])

    def test_collect_binary_only_plugin(self, binary_only_plugin: Path) -> None:
        """測試純二進位外掛（無原始碼）"""
        classifier = FileClassifier()
        collector = SourceCollector(classifier)

        result = collector.collect_source_files(binary_only_plugin)

        # 不應該有原始碼分類
        assert "python_source" not in result or len(result["python_source"]) == 0
        assert "objc_header" not in result or len(result["objc_header"]) == 0

        # 應該有二進位檔案
        assert "binary_stub" in result
        assert len(result["binary_stub"]) >= 1

    def test_collect_empty_directory(self, tmp_path: Path) -> None:
        """測試空目錄"""
        empty_dir = tmp_path / "EmptyPlugin"
        empty_dir.mkdir()

        classifier = FileClassifier()
        collector = SourceCollector(classifier)

        result = collector.collect_source_files(empty_dir)

        # 應該返回空字典
        assert result == {}

    def test_collect_nonexistent_directory(self, tmp_path: Path) -> None:
        """測試不存在的目錄"""
        classifier = FileClassifier()
        collector = SourceCollector(classifier)

        result = collector.collect_source_files(tmp_path / "nonexistent")

        # 應該返回空字典
        assert result == {}

    def test_collect_with_ui_files_excluded(self, mixed_plugin: Path) -> None:
        """測試排除 UI 檔案選項"""
        classifier = FileClassifier()
        collector = SourceCollector(classifier, include_ui_files=False)

        result = collector.collect_source_files(mixed_plugin)

        # 不應該包含 UI 檔案
        assert "ui_xib" not in result or len(result["ui_xib"]) == 0

        # 仍應該包含其他原始碼
        assert "python_source" in result
        assert "objc_header" in result

    def test_collect_returns_sorted_files(self, tmp_path: Path) -> None:
        """測試返回的檔案已排序"""
        plugin_dir = tmp_path / "SortedPlugin"
        plugin_dir.mkdir()

        # 以非字母順序建立檔案
        (plugin_dir / "z_file.py").write_text("# Z\n", encoding="utf-8")
        (plugin_dir / "a_file.py").write_text("# A\n", encoding="utf-8")
        (plugin_dir / "m_file.py").write_text("# M\n", encoding="utf-8")

        classifier = FileClassifier()
        collector = SourceCollector(classifier)

        result = collector.collect_source_files(plugin_dir)

        # 檔案應該按名稱排序
        assert "python_source" in result
        files = result["python_source"]
        assert files[0].name == "a_file.py"
        assert files[1].name == "m_file.py"
        assert files[2].name == "z_file.py"
