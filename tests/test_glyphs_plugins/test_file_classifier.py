"""
測試 FileClassifier - 檔案類型分類器

TDD 紅燈階段：先撰寫測試，預期失敗
"""

from pathlib import Path

import pytest

from glyphs_info_mcp.modules.glyphs_plugins.accessors.file_classifier import FileClassifier


class TestFileClassifier:
    """測試檔案類型分類器"""

    @pytest.fixture
    def temp_files(self, tmp_path: Path) -> Path:
        """建立測試用的各種檔案"""
        test_dir = tmp_path / "test_files"
        test_dir.mkdir()

        # Python 檔案
        (test_dir / "plugin.py").write_text(
            "# encoding: utf-8\nclass MyPlugin:\n    pass\n", encoding="utf-8"
        )

        # Objective-C header
        (test_dir / "Plugin.h").write_text(
            "#import <Cocoa/Cocoa.h>\n@interface Plugin : NSObject\n@end\n",
            encoding="utf-8",
        )

        # Objective-C implementation
        (test_dir / "Plugin.m").write_text(
            '#import "Plugin.h"\n@implementation Plugin\n@end\n', encoding="utf-8"
        )

        # XIB file (XML text)
        (test_dir / "View.xib").write_text(
            '<?xml version="1.0"?>\n<document type="com.apple.InterfaceBuilder3.Cocoa.XIB">\n</document>\n',
            encoding="utf-8",
        )

        # Plist file (XML text)
        (test_dir / "Info.plist").write_text(
            '<?xml version="1.0"?>\n<!DOCTYPE plist>\n<plist version="1.0">\n</plist>\n',
            encoding="utf-8",
        )

        # Markdown file
        (test_dir / "README.md").write_text("# Test Plugin\n\nDescription here.\n")

        # Binary file (Mach-O magic number)
        (test_dir / "plugin_binary").write_bytes(
            b"\xcf\xfa\xed\xfe" + b"\x00" * 100  # Mach-O 64-bit magic number
        )

        # Compiled Python
        (test_dir / "module.pyc").write_bytes(b"\x42\x0d\x0d\x0a" + b"\x00" * 50)

        # NIB file (binary)
        (test_dir / "Menu.nib").write_bytes(b"NIBArchive" + b"\x00" * 50)

        # Text file with null bytes (should be treated as binary)
        (test_dir / "corrupted.txt").write_bytes(b"Some text\x00with null bytes\x00")

        return test_dir

    def test_is_text_file_python(self, temp_files: Path) -> None:
        """測試識別 Python 文字檔案"""
        classifier = FileClassifier()
        assert classifier.is_text_file(temp_files / "plugin.py") is True

    def test_is_text_file_objc_header(self, temp_files: Path) -> None:
        """測試識別 Objective-C header"""
        classifier = FileClassifier()
        assert classifier.is_text_file(temp_files / "Plugin.h") is True

    def test_is_text_file_objc_impl(self, temp_files: Path) -> None:
        """測試識別 Objective-C implementation"""
        classifier = FileClassifier()
        assert classifier.is_text_file(temp_files / "Plugin.m") is True

    def test_is_text_file_xib(self, temp_files: Path) -> None:
        """測試識別 XIB 檔案"""
        classifier = FileClassifier()
        assert classifier.is_text_file(temp_files / "View.xib") is True

    def test_is_text_file_plist(self, temp_files: Path) -> None:
        """測試識別 plist 檔案"""
        classifier = FileClassifier()
        assert classifier.is_text_file(temp_files / "Info.plist") is True

    def test_is_text_file_markdown(self, temp_files: Path) -> None:
        """測試識別 Markdown 檔案"""
        classifier = FileClassifier()
        assert classifier.is_text_file(temp_files / "README.md") is True

    def test_is_text_file_binary(self, temp_files: Path) -> None:
        """測試識別二進位檔案（Mach-O）"""
        classifier = FileClassifier()
        assert classifier.is_text_file(temp_files / "plugin_binary") is False

    def test_is_text_file_pyc(self, temp_files: Path) -> None:
        """測試識別編譯的 Python 檔案"""
        classifier = FileClassifier()
        assert classifier.is_text_file(temp_files / "module.pyc") is False

    def test_is_text_file_nib(self, temp_files: Path) -> None:
        """測試識別 NIB 檔案"""
        classifier = FileClassifier()
        assert classifier.is_text_file(temp_files / "Menu.nib") is False

    def test_is_text_file_with_null_bytes(self, temp_files: Path) -> None:
        """測試包含 null bytes 的檔案應被視為二進位"""
        classifier = FileClassifier()
        assert classifier.is_text_file(temp_files / "corrupted.txt") is False

    def test_get_file_category_python_source(self, temp_files: Path) -> None:
        """測試分類 Python 原始碼"""
        classifier = FileClassifier()
        assert classifier.get_file_category(temp_files / "plugin.py") == "python_source"

    def test_get_file_category_objc_header(self, temp_files: Path) -> None:
        """測試分類 Objective-C header"""
        classifier = FileClassifier()
        assert classifier.get_file_category(temp_files / "Plugin.h") == "objc_header"

    def test_get_file_category_objc_impl(self, temp_files: Path) -> None:
        """測試分類 Objective-C implementation"""
        classifier = FileClassifier()
        assert classifier.get_file_category(temp_files / "Plugin.m") == "objc_impl"

    def test_get_file_category_ui_xib(self, temp_files: Path) -> None:
        """測試分類 XIB UI 檔案"""
        classifier = FileClassifier()
        assert classifier.get_file_category(temp_files / "View.xib") == "ui_xib"

    def test_get_file_category_resource(self, temp_files: Path) -> None:
        """測試分類資源檔案（plist, markdown）"""
        classifier = FileClassifier()
        assert classifier.get_file_category(temp_files / "Info.plist") == "resource"
        assert classifier.get_file_category(temp_files / "README.md") == "resource"

    def test_get_file_category_binary_stub(self, temp_files: Path) -> None:
        """測試分類二進位檔案（Mach-O）"""
        classifier = FileClassifier()
        assert (
            classifier.get_file_category(temp_files / "plugin_binary") == "binary_stub"
        )

    def test_get_file_category_compiled(self, temp_files: Path) -> None:
        """測試分類編譯檔案（pyc, nib）"""
        classifier = FileClassifier()
        assert classifier.get_file_category(temp_files / "module.pyc") == "compiled"
        assert classifier.get_file_category(temp_files / "Menu.nib") == "compiled"

    def test_get_language_tag_python(self, temp_files: Path) -> None:
        """測試 Python 的語法高亮標籤"""
        classifier = FileClassifier()
        assert classifier.get_language_tag(temp_files / "plugin.py") == "python"

    def test_get_language_tag_objc(self, temp_files: Path) -> None:
        """測試 Objective-C 的語法高亮標籤"""
        classifier = FileClassifier()
        assert classifier.get_language_tag(temp_files / "Plugin.h") == "objc"
        assert classifier.get_language_tag(temp_files / "Plugin.m") == "objc"

    def test_get_language_tag_xml(self, temp_files: Path) -> None:
        """測試 XML 的語法高亮標籤"""
        classifier = FileClassifier()
        assert classifier.get_language_tag(temp_files / "View.xib") == "xml"
        assert classifier.get_language_tag(temp_files / "Info.plist") == "xml"

    def test_get_language_tag_markdown(self, temp_files: Path) -> None:
        """測試 Markdown 的語法高亮標籤"""
        classifier = FileClassifier()
        assert classifier.get_language_tag(temp_files / "README.md") == "markdown"

    def test_get_language_tag_binary(self, temp_files: Path) -> None:
        """測試二進位檔案無語法高亮標籤"""
        classifier = FileClassifier()
        assert classifier.get_language_tag(temp_files / "plugin_binary") == ""
        assert classifier.get_language_tag(temp_files / "module.pyc") == ""

    def test_is_text_file_nonexistent(self, tmp_path: Path) -> None:
        """測試不存在的檔案"""
        classifier = FileClassifier()
        assert classifier.is_text_file(tmp_path / "nonexistent.py") is False

    def test_get_file_category_nonexistent(self, tmp_path: Path) -> None:
        """測試不存在的檔案分類"""
        classifier = FileClassifier()
        assert classifier.get_file_category(tmp_path / "nonexistent.py") == "unknown"
