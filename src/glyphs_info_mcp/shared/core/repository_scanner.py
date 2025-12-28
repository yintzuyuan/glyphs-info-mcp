#!/usr/bin/env python3
"""
Repository Scanner - Scans Glyphs Repositories folder

Scans the user's local Glyphs Repositories directory,
identifying installed modules (such as vanilla, drawBot, etc.).
"""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class RepositoryScanner:
    """Scanner for Glyphs Repositories folder"""

    def __init__(
        self, repositories_path: Path, fallback_paths: dict[str, Path] | None = None
    ):
        """Initialize Repository Scanner

        Args:
            repositories_path: Repositories folder path
            fallback_paths: Module fallback path mapping (optional)
                Example: {
                    "mekkablue": Path("data/official/mekkablue-scripts"),
                    "vanilla": Path("data/official/vanilla")
                }
        """
        self.repositories_path = Path(repositories_path)
        self.fallback_paths = fallback_paths or {}
        self._modules_cache: dict[str, Path] | None = None

    def is_available(self) -> bool:
        """Check if Repositories path exists

        Returns:
            True if path exists and is readable
        """
        return self.repositories_path.exists() and self.repositories_path.is_dir()

    def scan_repositories(self, force: bool = False) -> dict[str, Path]:
        """Scan Repositories and build module list

        Scans all subdirectories under the Repositories directory,
        identifying installed Python modules.

        Args:
            force: Whether to force rescan (ignore cache)

        Returns:
            Dictionary mapping module names to paths
        """
        # Use cache (unless force rescan)
        if not force and self._modules_cache is not None:
            return self._modules_cache

        if not self.is_available():
            logger.warning(f"Repositories path not available: {self.repositories_path}")
            self._modules_cache = {}
            return self._modules_cache

        modules = {}

        # Scan all subdirectories
        try:
            for item in self.repositories_path.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    # Check if it's a valid Python module
                    if self._is_python_module(item):
                        modules[item.name] = item
                        logger.debug(f"Found module: {item.name} at {item}")

        except Exception as e:
            logger.error(f"Error scanning repositories: {e}")
            modules = {}

        # Cache results
        self._modules_cache = modules
        logger.info(f"Scanned repositories, found {len(modules)} modules")

        return modules

    def _is_python_module(self, path: Path) -> bool:
        """Check if directory is a valid Python module

        Checks for common Python module structure indicators:
        - Lib/ directory
        - __init__.py file
        - setup.py file

        Args:
            path: Directory path to check

        Returns:
            True if it's a valid Python module
        """
        # Check for Lib/ directory (common in modules like vanilla)
        lib_path = path / "Lib"
        if lib_path.exists() and lib_path.is_dir():
            return True

        # Check if it directly contains __init__.py
        if (path / "__init__.py").exists():
            return True

        # Check for setup.py
        if (path / "setup.py").exists():
            return True

        return False

    def is_module_installed(self, module_name: str) -> bool:
        """Check if specified module is installed

        Args:
            module_name: Module name (e.g., "vanilla")

        Returns:
            True if module is installed
        """
        # Ensure scan has been done
        if self._modules_cache is None:
            self.scan_repositories()

        # Assert: cache must exist after scan
        assert self._modules_cache is not None
        return module_name in self._modules_cache

    def get_module_path(self, module_name: str) -> Path | None:
        """Get path for specified module (with fallback support)

        Priority order:
        1. Local installation (Repositories directory - exact name match)
        2. Local installation (Repositories directory - via scan cache)
        3. Environment variable (GLYPHS_{MODULE}_PATH)
        4. Submodule fallback (fallback_paths)

        Args:
            module_name: Module name (using repo_name from official plugin list)

        Returns:
            Module path, or None if module doesn't exist
        """
        # 1. Prioritize exact name match in Repositories directory
        # This handles plugins that don't meet _is_python_module criteria (e.g., Light-Table)
        if self.is_available():
            direct_path = self.repositories_path / module_name
            if direct_path.exists() and direct_path.is_dir():
                logger.info(f"✅ Using LOCAL {module_name}: {direct_path}")
                return direct_path

        # 2. Check scan cache (modules meeting _is_python_module criteria)
        if self._modules_cache is None:
            self.scan_repositories()

        assert self._modules_cache is not None
        if module_name in self._modules_cache:
            local_path = self._modules_cache[module_name]
            if local_path.exists():
                logger.info(f"✅ Using LOCAL {module_name}: {local_path}")
                return local_path

        # 3. Check environment variable
        env_key = f"GLYPHS_{module_name.upper()}_PATH"
        env_path = os.getenv(env_key)
        if env_path:
            path = Path(env_path)
            if path.exists():
                logger.info(f"✅ Using ENV {module_name}: {path}")
                return path
            else:
                logger.warning(f"⚠️ ENV {env_key} set but path doesn't exist: {path}")

        # 4. Fallback to Submodule
        if module_name in self.fallback_paths:
            fallback = self.fallback_paths[module_name]
            if fallback.exists():
                logger.info(f"✅ Using SUBMODULE {module_name}: {fallback}")
                return fallback
            else:
                logger.warning(
                    f"❌ Submodule not initialized: {fallback}\n"
                    f"Run: git submodule update --init --recursive"
                )

        logger.error(f"❌ {module_name} not found in any location")
        return None

    def get_installed_modules(self) -> list[str]:
        """List all installed module names

        Returns:
            List of module names
        """
        # Ensure scan has been done
        if self._modules_cache is None:
            self.scan_repositories()

        # Assert: cache must exist after scan
        assert self._modules_cache is not None
        return list(self._modules_cache.keys())

    @classmethod
    def auto_detect(cls) -> Optional["RepositoryScanner"]:
        """Auto-detect Glyphs Repositories path

        Priority order:
        1. Environment variable GLYPHS_REPOSITORIES_PATH
        2. Glyphs 3: ~/Library/Application Support/Glyphs 3/Repositories
        3. Glyphs 2: ~/Library/Application Support/Glyphs/Repositories
        4. Legacy Glyphs: ~/Library/Application Support/Glyphs 2/Repositories

        Returns:
            RepositoryScanner instance, or None if not found
        """
        # 1. Check environment variable
        env_path = os.getenv("GLYPHS_REPOSITORIES_PATH")
        if env_path:
            path = Path(env_path)
            if path.exists():
                logger.info(f"Using GLYPHS_REPOSITORIES_PATH: {path}")
                return cls(path)
            else:
                logger.warning(
                    f"GLYPHS_REPOSITORIES_PATH set but path doesn't exist: {path}"
                )

        # 2. Try common paths
        home = Path.home()
        common_paths = [
            home / "Library/Application Support/Glyphs 3/Repositories",
            home / "Library/Application Support/Glyphs/Repositories",
            home / "Library/Application Support/Glyphs 2/Repositories",
        ]

        for path in common_paths:
            if path.exists():
                logger.info(f"Auto-detected Repositories path: {path}")
                return cls(path)

        logger.warning("Could not auto-detect Glyphs Repositories path")
        return None
