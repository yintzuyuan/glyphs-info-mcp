"""測試配置載入器"""

import tempfile
from pathlib import Path

import pytest
from glyphs_info_mcp.shared.core.config_loader import ConfigLoader, ConfigLoadError


class TestConfigLoader:
    """ConfigLoader 功能測試"""

    @pytest.fixture
    def valid_config_yaml(self) -> str:
        """有效的配置 YAML"""
        return """
modules:
  - name: handbook
    enabled: true
    module_path: modules/glyphs_handbook
    python_file: handbook/unified_handbook_module.py
    class_name: UnifiedHandbookModule
    description: 手冊模組
    search_types:
      - handbook
      - documentation

  - name: api
    enabled: true
    module_path: modules/glyphs_api
    python_file: unified_api_module.py
    class_name: UnifiedAPIModule
    description: API 模組
    search_types:
      - python
      - api

search_engine:
  enabled: true
  default_strategy: hybrid
  max_results: 20

features:
  plugin_templates: true
  unified_prompts: true
  character_limit: 25000

server_name: Test Server
log_level: INFO
"""

    def test_load_valid_yaml(self, valid_config_yaml: str) -> None:
        """測試載入有效的 YAML 配置"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(valid_config_yaml)
            config_path = Path(f.name)

        try:
            config = ConfigLoader.load_from_yaml(config_path)

            assert config is not None
            assert len(config.modules) == 2
            assert config.modules[0].name == "handbook"
            assert config.modules[1].name == "api"
            assert config.search_engine.enabled is True
            assert config.search_engine.default_strategy == "hybrid"
            assert config.features.character_limit == 25000
            assert config.server_name == "Test Server"
            assert config.log_level == "INFO"
        finally:
            config_path.unlink()

    def test_load_minimal_config(self) -> None:
        """測試載入最小配置（只有必填欄位）"""
        minimal_yaml = """
modules:
  - name: test
    module_path: modules/test
    python_file: test.py
    class_name: TestModule
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(minimal_yaml)
            config_path = Path(f.name)

        try:
            config = ConfigLoader.load_from_yaml(config_path)

            assert config is not None
            assert len(config.modules) == 1
            assert config.modules[0].name == "test"
            # 驗證預設值
            assert config.modules[0].enabled is True
            assert config.modules[0].internal_service is False
            assert config.search_engine.enabled is True
            assert config.features.character_limit == 25000
        finally:
            config_path.unlink()

    def test_load_nonexistent_file(self) -> None:
        """測試載入不存在的檔案"""
        with pytest.raises(ConfigLoadError, match="Configuration file not found"):
            ConfigLoader.load_from_yaml(Path("/nonexistent/config.yaml"))

    def test_load_invalid_yaml_syntax(self) -> None:
        """測試載入無效的 YAML 語法"""
        invalid_yaml = "invalid: yaml: content: ["

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(invalid_yaml)
            config_path = Path(f.name)

        try:
            with pytest.raises(ConfigLoadError, match="YAML parse error"):
                ConfigLoader.load_from_yaml(config_path)
        finally:
            config_path.unlink()

    def test_load_empty_file(self) -> None:
        """測試載入空檔案"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            config_path = Path(f.name)

        try:
            with pytest.raises(ConfigLoadError, match="Configuration file is empty"):
                ConfigLoader.load_from_yaml(config_path)
        finally:
            config_path.unlink()

    def test_validation_error_missing_required_field(self) -> None:
        """測試缺少必填欄位的驗證錯誤"""
        invalid_yaml = """
modules:
  - name: test
    module_path: modules/test
    # 缺少 python_file 和 class_name
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(invalid_yaml)
            config_path = Path(f.name)

        try:
            with pytest.raises(ConfigLoadError, match="Configuration validation failed"):
                ConfigLoader.load_from_yaml(config_path)
        finally:
            config_path.unlink()

    def test_validation_error_duplicate_module_names(self) -> None:
        """測試重複模組名稱的驗證錯誤"""
        invalid_yaml = """
modules:
  - name: test
    module_path: modules/test1
    python_file: test.py
    class_name: Test1
  - name: test
    module_path: modules/test2
    python_file: test.py
    class_name: Test2
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(invalid_yaml)
            config_path = Path(f.name)

        try:
            with pytest.raises(ConfigLoadError, match="Configuration validation failed"):
                ConfigLoader.load_from_yaml(config_path)
        finally:
            config_path.unlink()

    def test_validation_error_absolute_path(self) -> None:
        """測試絕對路徑被拒絕"""
        invalid_yaml = """
modules:
  - name: test
    module_path: /absolute/path
    python_file: test.py
    class_name: TestModule
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(invalid_yaml)
            config_path = Path(f.name)

        try:
            with pytest.raises(ConfigLoadError, match="Configuration validation failed"):
                ConfigLoader.load_from_yaml(config_path)
        finally:
            config_path.unlink()

    def test_validate_config_success(self, valid_config_yaml: str) -> None:
        """測試配置驗證成功"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(valid_config_yaml)
            config_path = Path(f.name)

        try:
            is_valid, message = ConfigLoader.validate_config(config_path)

            assert is_valid is True
            assert "Configuration valid" in message
            assert "2" in message  # 2 個已啟用模組
        finally:
            config_path.unlink()

    def test_validate_config_failure(self) -> None:
        """測試配置驗證失敗"""
        invalid_yaml = "invalid: yaml: ["

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(invalid_yaml)
            config_path = Path(f.name)

        try:
            is_valid, message = ConfigLoader.validate_config(config_path)

            assert is_valid is False
            assert "❌" in message
        finally:
            config_path.unlink()

    def test_load_with_disabled_modules(self) -> None:
        """測試載入包含停用模組的配置"""
        yaml_with_disabled = """
modules:
  - name: enabled
    enabled: true
    module_path: modules/enabled
    python_file: enabled.py
    class_name: EnabledModule

  - name: disabled
    enabled: false
    module_path: modules/disabled
    python_file: disabled.py
    class_name: DisabledModule
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_with_disabled)
            config_path = Path(f.name)

        try:
            config = ConfigLoader.load_from_yaml(config_path)

            assert len(config.modules) == 2
            enabled_modules = config.get_enabled_modules()
            assert len(enabled_modules) == 1
            assert enabled_modules[0].name == "enabled"
        finally:
            config_path.unlink()

    def test_load_with_internal_service(self) -> None:
        """測試載入包含內部服務的配置"""
        yaml_with_internal = """
modules:
  - name: vocabulary
    enabled: true
    internal_service: true
    module_path: modules/vocabulary
    python_file: vocab.py
    class_name: VocabModule

  - name: public
    enabled: true
    internal_service: false
    module_path: modules/public
    python_file: public.py
    class_name: PublicModule
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_with_internal)
            config_path = Path(f.name)

        try:
            config = ConfigLoader.load_from_yaml(config_path)

            internal = config.get_internal_services()
            public = config.get_public_modules()

            assert len(internal) == 1
            assert internal[0].name == "vocabulary"
            assert len(public) == 1
            assert public[0].name == "public"
        finally:
            config_path.unlink()
