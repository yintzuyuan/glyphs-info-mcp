"""測試模組配置資料模型"""

import pytest
from glyphs_info_mcp.shared.core.module_config import (
    FeaturesConfig,
    ModuleConfig,
    SearchEngineConfig,
    ServerConfig,
)
from pydantic import ValidationError


class TestModuleConfig:
    """ModuleConfig 驗證測試"""

    def test_valid_module_config(self) -> None:
        """測試有效的模組配置"""
        config = ModuleConfig(
            name="handbook",
            module_path="modules/glyphs_handbook",
            python_file="handbook/unified_handbook_module.py",
            class_name="UnifiedHandbookModule",
            description="手冊模組",
            search_types=["handbook", "documentation"],
        )

        assert config.name == "handbook"
        assert config.enabled is True  # 預設值
        assert config.internal_service is False  # 預設值
        assert len(config.search_types) == 2
        assert config.dependencies == []  # 預設值

    def test_module_config_defaults(self) -> None:
        """測試模組配置預設值"""
        config = ModuleConfig(
            name="test",
            module_path="modules/test",
            python_file="test.py",
            class_name="TestModule",
        )

        assert config.enabled is True
        assert config.internal_service is False
        assert config.description == ""
        assert config.search_types == []
        assert config.dependencies == []

    def test_module_name_validation_valid(self) -> None:
        """測試有效的模組名稱"""
        valid_names = [
            "handbook",
            "glyphs-api",
            "code_snippets",
            "glyphs-news",
            "mekkablue-scripts",
        ]

        for name in valid_names:
            config = ModuleConfig(
                name=name,
                module_path="modules/test",
                python_file="test.py",
                class_name="TestModule",
            )
            assert config.name == name

    def test_module_name_validation_empty(self) -> None:
        """測試空模組名稱被拒絕"""
        with pytest.raises(ValidationError, match="Invalid module name format"):
            ModuleConfig(
                name="",
                module_path="modules/test",
                python_file="test.py",
                class_name="TestModule",
            )

    def test_module_name_validation_invalid_chars(self) -> None:
        """測試無效字元的模組名稱"""
        invalid_names = [
            "module@name",
            "module name",
            "module/name",
            "module.name",
        ]

        for name in invalid_names:
            with pytest.raises(ValidationError):
                ModuleConfig(
                    name=name,
                    module_path="modules/test",
                    python_file="test.py",
                    class_name="TestModule",
                )

    def test_absolute_path_rejected_module_path(self) -> None:
        """測試拒絕絕對路徑（module_path）"""
        with pytest.raises(ValidationError, match="must be relative"):
            ModuleConfig(
                name="test",
                module_path="/absolute/path",
                python_file="test.py",
                class_name="TestModule",
            )

    def test_absolute_path_rejected_python_file(self) -> None:
        """測試拒絕絕對路徑（python_file）"""
        with pytest.raises(ValidationError, match="must be relative"):
            ModuleConfig(
                name="test",
                module_path="modules/test",
                python_file="/absolute/test.py",
                class_name="TestModule",
            )

    def test_internal_service_flag(self) -> None:
        """測試內部服務標記"""
        config = ModuleConfig(
            name="vocabulary",
            module_path="modules/glyphs_vocabulary",
            python_file="vocabulary/vocabulary_module.py",
            class_name="VocabularyModule",
            internal_service=True,
        )

        assert config.internal_service is True


class TestSearchEngineConfig:
    """SearchEngineConfig 驗證測試"""

    def test_default_config(self) -> None:
        """測試預設配置"""
        config = SearchEngineConfig()

        assert config.enabled is True
        assert config.default_strategy == "hybrid"
        assert config.max_results == 20

    def test_custom_config(self) -> None:
        """測試自訂配置"""
        config = SearchEngineConfig(
            enabled=False, default_strategy="sequential", max_results=50
        )

        assert config.enabled is False
        assert config.default_strategy == "sequential"
        assert config.max_results == 50

    def test_max_results_constraints(self) -> None:
        """測試 max_results 範圍限制"""
        # 有效範圍
        config = SearchEngineConfig(max_results=1)
        assert config.max_results == 1

        config = SearchEngineConfig(max_results=100)
        assert config.max_results == 100

        # 超出範圍
        with pytest.raises(ValidationError):
            SearchEngineConfig(max_results=0)

        with pytest.raises(ValidationError):
            SearchEngineConfig(max_results=101)

    def test_strategy_enum_validation(self) -> None:
        """測試策略枚舉驗證"""
        # 有效策略
        for strategy in ["hybrid", "sequential", "parallel"]:
            config = SearchEngineConfig(default_strategy=strategy)  # type: ignore[arg-type]
            assert config.default_strategy == strategy

        # 無效策略
        with pytest.raises(ValidationError):
            SearchEngineConfig(default_strategy="invalid")  # type: ignore[arg-type]


class TestFeaturesConfig:
    """FeaturesConfig 驗證測試"""

    def test_default_config(self) -> None:
        """測試預設配置"""
        config = FeaturesConfig()

        assert config.plugin_templates is True
        assert config.unified_prompts is True
        assert config.character_limit == 25000

    def test_character_limit_constraints(self) -> None:
        """測試 character_limit 範圍限制"""
        # 有效範圍
        config = FeaturesConfig(character_limit=1000)
        assert config.character_limit == 1000

        config = FeaturesConfig(character_limit=100000)
        assert config.character_limit == 100000

        # 超出範圍
        with pytest.raises(ValidationError):
            FeaturesConfig(character_limit=999)

        with pytest.raises(ValidationError):
            FeaturesConfig(character_limit=100001)


class TestServerConfig:
    """ServerConfig 驗證測試"""

    def test_valid_server_config(self) -> None:
        """測試有效的伺服器配置"""
        modules = [
            ModuleConfig(
                name="handbook",
                module_path="modules/handbook",
                python_file="module.py",
                class_name="HandbookModule",
            ),
            ModuleConfig(
                name="api",
                module_path="modules/api",
                python_file="module.py",
                class_name="APIModule",
            ),
        ]

        config = ServerConfig(modules=modules)

        assert len(config.modules) == 2
        assert config.server_name == "Glyphs info MCP - Modular Architecture"
        assert config.log_level == "INFO"

    def test_unique_module_names(self) -> None:
        """測試模組名稱唯一性驗證"""
        modules = [
            ModuleConfig(
                name="handbook",
                module_path="modules/handbook",
                python_file="module.py",
                class_name="HandbookModule",
            ),
            ModuleConfig(
                name="handbook",  # 重複名稱
                module_path="modules/handbook2",
                python_file="module.py",
                class_name="HandbookModule2",
            ),
        ]

        with pytest.raises(ValidationError, match="must be unique"):
            ServerConfig(modules=modules)

    def test_get_enabled_modules(self) -> None:
        """測試取得已啟用模組"""
        modules = [
            ModuleConfig(
                name="enabled1",
                enabled=True,
                module_path="m1",
                python_file="m.py",
                class_name="M1",
            ),
            ModuleConfig(
                name="disabled",
                enabled=False,
                module_path="m2",
                python_file="m.py",
                class_name="M2",
            ),
            ModuleConfig(
                name="enabled2",
                enabled=True,
                module_path="m3",
                python_file="m.py",
                class_name="M3",
            ),
        ]

        config = ServerConfig(modules=modules)
        enabled = config.get_enabled_modules()

        assert len(enabled) == 2
        assert all(m.enabled for m in enabled)
        assert enabled[0].name == "enabled1"
        assert enabled[1].name == "enabled2"

    def test_get_internal_services(self) -> None:
        """測試取得內部服務模組"""
        modules = [
            ModuleConfig(
                name="vocabulary",
                enabled=True,
                internal_service=True,
                module_path="m1",
                python_file="m.py",
                class_name="M1",
            ),
            ModuleConfig(
                name="public",
                enabled=True,
                internal_service=False,
                module_path="m2",
                python_file="m.py",
                class_name="M2",
            ),
            ModuleConfig(
                name="disabled_internal",
                enabled=False,
                internal_service=True,
                module_path="m3",
                python_file="m.py",
                class_name="M3",
            ),
        ]

        config = ServerConfig(modules=modules)
        internal = config.get_internal_services()

        assert len(internal) == 1
        assert internal[0].name == "vocabulary"
        assert internal[0].internal_service is True

    def test_get_public_modules(self) -> None:
        """測試取得公開工具模組"""
        modules = [
            ModuleConfig(
                name="vocabulary",
                enabled=True,
                internal_service=True,
                module_path="m1",
                python_file="m.py",
                class_name="M1",
            ),
            ModuleConfig(
                name="handbook",
                enabled=True,
                internal_service=False,
                module_path="m2",
                python_file="m.py",
                class_name="M2",
            ),
            ModuleConfig(
                name="disabled_public",
                enabled=False,
                internal_service=False,
                module_path="m3",
                python_file="m.py",
                class_name="M3",
            ),
        ]

        config = ServerConfig(modules=modules)
        public = config.get_public_modules()

        assert len(public) == 1
        assert public[0].name == "handbook"
        assert public[0].internal_service is False

    def test_log_level_validation(self) -> None:
        """測試日誌級別驗證"""
        modules = [
            ModuleConfig(
                name="test",
                module_path="m",
                python_file="m.py",
                class_name="M",
            )
        ]

        # 有效日誌級別
        for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            config = ServerConfig(modules=modules, log_level=level)  # type: ignore[arg-type]
            assert config.log_level == level

        # 無效日誌級別
        with pytest.raises(ValidationError):
            ServerConfig(modules=modules, log_level="INVALID")  # type: ignore[arg-type]

    def test_default_search_engine_and_features(self) -> None:
        """測試搜尋引擎和功能配置預設值"""
        modules = [
            ModuleConfig(
                name="test",
                module_path="m",
                python_file="m.py",
                class_name="M",
            )
        ]

        config = ServerConfig(modules=modules)

        # 驗證搜尋引擎預設值
        assert config.search_engine.enabled is True
        assert config.search_engine.default_strategy == "hybrid"
        assert config.search_engine.max_results == 20

        # 驗證功能配置預設值
        assert config.features.plugin_templates is True
        assert config.features.unified_prompts is True
        assert config.features.character_limit == 25000
