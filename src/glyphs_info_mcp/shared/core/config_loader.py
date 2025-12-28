"""YAML Configuration File Loader

Provides configuration file loading, parsing, and validation functionality.
"""

import logging
from pathlib import Path

import yaml
from pydantic import ValidationError

from glyphs_info_mcp.shared.core.module_config import ServerConfig

logger = logging.getLogger(__name__)


class ConfigLoadError(Exception):
    """Configuration load error"""

    pass


class ConfigLoader:
    """YAML configuration file loader"""

    @staticmethod
    def load_from_yaml(config_path: Path) -> ServerConfig:
        """Load configuration from YAML file

        Args:
            config_path: YAML configuration file path

        Returns:
            Validated ServerConfig instance

        Raises:
            ConfigLoadError: Configuration load or validation failed
        """
        try:
            # 1. Check file exists
            if not config_path.exists():
                raise ConfigLoadError(f"Configuration file not found: {config_path}")

            # 2. Read YAML
            with open(config_path, encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            if not config_data:
                raise ConfigLoadError("Configuration file is empty")

            # 3. Pydantic validation
            server_config = ServerConfig(**config_data)

            logger.info(f"✅ Configuration loaded successfully: {len(server_config.modules)} modules")
            return server_config

        except yaml.YAMLError as e:
            raise ConfigLoadError(f"YAML parse error: {e}") from e
        except ValidationError as e:
            # Pydantic validation error
            error_details = "\n".join(
                [
                    f"  - {'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
                    for err in e.errors()
                ]
            )
            raise ConfigLoadError(f"Configuration validation failed:\n{error_details}") from e
        except Exception as e:
            raise ConfigLoadError(f"Configuration load failed: {e}") from e

    @staticmethod
    def validate_config(config_path: Path) -> tuple[bool, str]:
        """Validate configuration file (without loading modules)

        Args:
            config_path: YAML configuration file path

        Returns:
            (is_valid, error message or success message)
        """
        try:
            config = ConfigLoader.load_from_yaml(config_path)
            enabled_count = len(config.get_enabled_modules())
            return True, f"✅ Configuration valid ({enabled_count} enabled modules)"
        except ConfigLoadError as e:
            return False, f"❌ {str(e)}"
