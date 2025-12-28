"""Unified Module Loader

Provides configuration-driven dynamic module loading functionality.
"""

import importlib.util
import logging
import sys
from pathlib import Path

from glyphs_info_mcp.shared.core.base_module import BaseMCPModule
from glyphs_info_mcp.shared.core.module_config import ModuleConfig

logger = logging.getLogger(__name__)


class ModuleLoadError(Exception):
    """Module load error"""

    pass


class ModuleLoader:
    """Unified module loader"""

    def __init__(self, base_dir: Path):
        """Initialize loader

        Args:
            base_dir: Project root directory
        """
        self.base_dir = base_dir
        self._loaded_modules: dict[str, BaseMCPModule] = {}
        self._sys_path_additions: list[str] = []

    def load_module(self, config: ModuleConfig) -> BaseMCPModule | None:
        """Load a single module based on configuration

        Args:
            config: Module configuration

        Returns:
            Module instance on success, None on failure

        Raises:
            ModuleLoadError: Detailed error when loading fails
        """
        module_name = config.name

        try:
            # 1. Verify module path exists
            module_path = self.base_dir / config.module_path
            if not module_path.exists():
                raise ModuleLoadError(f"Module directory not found: {module_path}")

            # 2. Verify Python file exists
            python_file_path = module_path / config.python_file
            if not python_file_path.exists():
                raise ModuleLoadError(f"Python file not found: {python_file_path}")

            # 3. Add module path to sys.path
            module_root = str(module_path)
            if module_root not in sys.path:
                sys.path.insert(0, module_root)
                self._sys_path_additions.append(module_root)

            # 4. Dynamically load module
            spec = importlib.util.spec_from_file_location(
                f"mcp_module_{module_name}",  # Unique module name
                python_file_path,
            )

            if spec is None or spec.loader is None:
                raise ModuleLoadError(f"Cannot create module spec: {python_file_path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 5. Instantiate module class
            if not hasattr(module, config.class_name):
                raise ModuleLoadError(
                    f"Class '{config.class_name}' not found in module: {python_file_path}"
                )

            module_class = getattr(module, config.class_name)
            module_instance = module_class()

            # 6. Validate module instance
            if not isinstance(module_instance, BaseMCPModule):
                raise ModuleLoadError(
                    f"Module class must inherit from BaseMCPModule: {config.class_name}"
                )

            # 7. Initialize module
            if not module_instance.initialize():
                raise ModuleLoadError(f"Module initialization failed: {module_name}")

            # 8. Record successful load
            self._loaded_modules[module_name] = module_instance
            logger.info(
                f"✅ Module loaded successfully: {module_name} "
                f"({config.class_name} from {config.python_file})"
            )

            return module_instance

        except ModuleLoadError:
            # Re-raise known errors
            raise
        except Exception as e:
            # Wrap unknown errors
            import traceback

            logger.error(f"Module load exception: {module_name}\n{traceback.format_exc()}")
            raise ModuleLoadError(
                f"Error loading module '{module_name}': {str(e)}"
            ) from e

    def load_all_modules(
        self, configs: list[ModuleConfig], fail_on_error: bool = False
    ) -> dict[str, BaseMCPModule]:
        """Batch load all modules

        Args:
            configs: Module configuration list
            fail_on_error: Whether to stop on first error

        Returns:
            Successfully loaded modules dict {module_name: module_instance}
        """
        loaded = {}
        errors = []

        for config in configs:
            if not config.enabled:
                logger.info(f"⏭️  Skipping disabled module: {config.name}")
                continue

            try:
                module = self.load_module(config)
                if module:
                    loaded[config.name] = module
            except ModuleLoadError as e:
                error_msg = str(e)
                errors.append((config.name, error_msg))
                logger.error(f"❌ {error_msg}")

                if fail_on_error:
                    break

        # Report loading results
        total_enabled = sum(1 for c in configs if c.enabled)
        logger.info(
            f"📦 Module loading complete: {len(loaded)}/{total_enabled} succeeded, "
            f"{len(errors)} failed"
        )

        if errors:
            logger.warning("Failed modules:")
            for module_name, error in errors:
                logger.warning(f"  - {module_name}: {error}")

        return loaded

    def cleanup(self) -> None:
        """Clean up sys.path modifications"""
        for path in self._sys_path_additions:
            if path in sys.path:
                sys.path.remove(path)
        self._sys_path_additions.clear()
        logger.debug("Cleaned up sys.path modifications")

    def get_loaded_modules(self) -> dict[str, BaseMCPModule]:
        """Get loaded modules

        Returns:
            Copy of loaded modules dictionary
        """
        return self._loaded_modules.copy()
