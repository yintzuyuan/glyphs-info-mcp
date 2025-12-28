"""
FileClassifier - File type classifier

Used to identify plugin file types:
- Text files vs binary files
- Code classification (Python/Objective-C/resources)
- Markdown syntax highlighting tags
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FileClassifier:
    """File type classifier"""

    # Text file extension whitelist
    TEXT_EXTENSIONS = {
        ".py",
        ".h",
        ".m",
        ".mm",
        ".c",
        ".cpp",
        ".swift",
        ".md",
        ".txt",
        ".plist",
        ".xib",
        ".xml",
        ".json",
        ".yaml",
        ".yml",
        ".sh",
        ".bash",
    }

    # Binary file extension blacklist
    BINARY_EXTENSIONS = {
        ".pyc",
        ".pyo",
        ".so",
        ".dylib",
        ".nib",
        ".icns",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".pdf",
        ".zip",
        ".tar",
        ".gz",
    }

    # Binary file Magic Numbers
    BINARY_SIGNATURES = [
        b"\xcf\xfa\xed\xfe",  # Mach-O 64-bit
        b"\xce\xfa\xed\xfe",  # Mach-O 32-bit
        b"\xfe\xed\xfa\xce",  # Mach-O reverse
        b"\xfe\xed\xfa\xcf",  # Mach-O reverse
        b"\x42\x0d\x0d\x0a",  # Python .pyc
        b"NIBArchive",  # NIB file
        b"\x89PNG",  # PNG
        b"\xff\xd8\xff",  # JPEG
        b"GIF8",  # GIF
        b"%PDF",  # PDF
    ]

    def is_text_file(self, file_path: Path) -> bool:
        """
        Check if file is a readable text file

        Check strategy:
        1. File doesn't exist → False
        2. Extension in binary blacklist → False
        3. Extension in text whitelist → True
        4. Check Magic Number → matches binary signature → False
        5. Check null bytes → has null bytes → False
        6. Try UTF-8 decode → success → True

        Args:
            file_path: File path

        Returns:
            True for text file, False for binary file
        """
        if not file_path.exists() or not file_path.is_file():
            return False

        suffix = file_path.suffix.lower()

        # 1. Extension blacklist check
        if suffix in self.BINARY_EXTENSIONS:
            return False

        # 2. Extension whitelist check
        if suffix in self.TEXT_EXTENSIONS:
            # Still need to check content (prevent masquerading)
            try:
                content = file_path.read_bytes()

                # 3. Magic Number check
                for signature in self.BINARY_SIGNATURES:
                    if content.startswith(signature):
                        return False

                # 4. Null bytes check
                if b"\x00" in content[:1024]:  # Only check first 1KB
                    return False

                # 5. UTF-8 decode test
                content.decode("utf-8")
                return True
            except (UnicodeDecodeError, OSError):
                return False

        # 3. Unknown extension: try decoding
        try:
            content = file_path.read_bytes()

            # Magic Number check
            for signature in self.BINARY_SIGNATURES:
                if content.startswith(signature):
                    return False

            # Null bytes check
            if b"\x00" in content[:1024]:
                return False

            # UTF-8 decode test
            content.decode("utf-8")
            return True
        except (UnicodeDecodeError, OSError):
            return False

    def get_file_category(self, file_path: Path) -> str:
        """
        Get file category

        Categories:
        - python_source: Python source code (.py)
        - objc_header: Objective-C header (.h)
        - objc_impl: Objective-C implementation (.m, .mm)
        - ui_xib: UI definition file (.xib)
        - resource: Resource file (.plist, .md, .txt, .json, etc.)
        - binary_stub: Binary executable (Mach-O)
        - compiled: Compiled file (.pyc, .nib)
        - unknown: Unknown type

        Args:
            file_path: File path

        Returns:
            File category string
        """
        if not file_path.exists() or not file_path.is_file():
            return "unknown"

        suffix = file_path.suffix.lower()

        # Python source code
        if suffix == ".py":
            return "python_source"

        # Objective-C header
        if suffix == ".h":
            return "objc_header"

        # Objective-C implementation
        if suffix in {".m", ".mm"}:
            return "objc_impl"

        # UI definition file
        if suffix == ".xib":
            return "ui_xib"

        # Text resource files
        if suffix in {".plist", ".md", ".txt", ".json", ".yaml", ".yml", ".xml"}:
            return "resource"

        # Compiled files
        if suffix in {".pyc", ".pyo", ".nib"}:
            return "compiled"

        # Binary file detection
        if not self.is_text_file(file_path):
            # Check if Mach-O
            try:
                content = file_path.read_bytes()
                for signature in self.BINARY_SIGNATURES[:4]:  # Mach-O signatures
                    if content.startswith(signature):
                        return "binary_stub"
                return "compiled"  # Other binary files
            except OSError:
                return "unknown"

        # Other text files treated as resources
        return "resource"

    def get_language_tag(self, file_path: Path) -> str:
        """
        Get Markdown syntax highlighting tag

        Args:
            file_path: File path

        Returns:
            Syntax highlighting tag (e.g., "python", "objc", "xml")
            Returns empty string for binary files
        """
        category = self.get_file_category(file_path)

        # No syntax highlighting for binary/compiled files
        if category in {"binary_stub", "compiled", "unknown"}:
            return ""

        suffix = file_path.suffix.lower()

        # Python
        if suffix == ".py":
            return "python"

        # Objective-C
        if suffix in {".h", ".m", ".mm"}:
            return "objc"

        # XML-based
        if suffix in {".plist", ".xib", ".xml"}:
            return "xml"

        # Markdown
        if suffix == ".md":
            return "markdown"

        # JSON
        if suffix == ".json":
            return "json"

        # YAML
        if suffix in {".yaml", ".yml"}:
            return "yaml"

        # Shell
        if suffix in {".sh", ".bash"}:
            return "bash"

        # Swift
        if suffix == ".swift":
            return "swift"

        # C/C++
        if suffix in {".c", ".cpp", ".h"}:
            return "c"

        # Default: no specific syntax
        return ""
