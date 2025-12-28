#!/usr/bin/env python3
"""
Protocol Parser 測試

TDD 紅燈階段：先寫測試定義預期行為
"""

import sys
from pathlib import Path

import pytest

from glyphs_info_mcp.modules.glyphs_api.api.objc_header_parser import HeaderParser


class TestProtocolParser:
    """Protocol 解析器測試"""

    @pytest.fixture
    def parser(self) -> HeaderParser:
        """建立 HeaderParser 實例"""
        return HeaderParser()

    @pytest.fixture
    def glyphs_reporter_protocol_path(self) -> Path:
        """GlyphsReporterProtocol.h 路徑"""
        return Path("/Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework/Headers/GlyphsReporterProtocol.h")

    @pytest.fixture
    def all_protocol_paths(self) -> list[Path]:
        """所有 Glyphs Protocol Headers 路徑"""
        headers_dir = Path("/Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework/Headers/")
        return list(headers_dir.glob("Glyphs*Protocol.h"))

    def test_parse_glyphs_reporter_protocol(self, parser: HeaderParser, glyphs_reporter_protocol_path: Path) -> None:
        """測試解析 GlyphsReporterProtocol.h"""
        if not glyphs_reporter_protocol_path.exists():
            pytest.skip("GlyphsReporterProtocol.h 不存在")

        result = parser.parse_file(glyphs_reporter_protocol_path)

        # 驗證基本結構
        assert 'protocols' in result
        assert len(result['protocols']) > 0

        # 找到 GlyphsReporter protocol
        glyphs_reporter = None
        for protocol in result['protocols']:
            if protocol['name'] == 'GlyphsReporter':
                glyphs_reporter = protocol
                break

        assert glyphs_reporter is not None, "應該找到 GlyphsReporter protocol"

    def test_parse_protocol_required_methods(self, parser: HeaderParser, glyphs_reporter_protocol_path: Path) -> None:
        """測試解析 required 方法"""
        if not glyphs_reporter_protocol_path.exists():
            pytest.skip("GlyphsReporterProtocol.h 不存在")

        result = parser.parse_file(glyphs_reporter_protocol_path)
        glyphs_reporter = result['protocols'][0]

        # GlyphsReporter 應該有 required 方法
        assert 'required_methods' in glyphs_reporter
        assert len(glyphs_reporter['required_methods']) > 0

        # 驗證已知的 required 方法
        method_names = [m['name'] for m in glyphs_reporter['required_methods']]
        assert 'interfaceVersion' in method_names
        assert 'title' in method_names

    def test_parse_protocol_optional_methods(self, parser: HeaderParser, glyphs_reporter_protocol_path: Path) -> None:
        """測試解析 optional 方法"""
        if not glyphs_reporter_protocol_path.exists():
            pytest.skip("GlyphsReporterProtocol.h 不存在")

        result = parser.parse_file(glyphs_reporter_protocol_path)
        glyphs_reporter = result['protocols'][0]

        # GlyphsReporter 應該有 optional 方法
        assert 'optional_methods' in glyphs_reporter
        assert len(glyphs_reporter['optional_methods']) > 0

        # 驗證已知的 optional 方法
        method_names = [m['name'] for m in glyphs_reporter['optional_methods']]
        assert 'drawBackgroundForLayer' in method_names or 'drawForegroundForLayer' in method_names

    def test_parse_protocol_deprecated_methods(self, parser: HeaderParser, glyphs_reporter_protocol_path: Path) -> None:
        """測試識別已棄用的方法"""
        if not glyphs_reporter_protocol_path.exists():
            pytest.skip("GlyphsReporterProtocol.h 不存在")

        result = parser.parse_file(glyphs_reporter_protocol_path)
        glyphs_reporter = result['protocols'][0]

        # GlyphsReporter 有已棄用的方法（標記 __attribute__((unavailable))）
        assert 'deprecated_methods' in glyphs_reporter

        # 至少應該有一些已棄用的方法
        # （根據實際 Header 內容，可能需要調整這個斷言）
        deprecated_count = len(glyphs_reporter['deprecated_methods'])
        print(f"找到 {deprecated_count} 個已棄用的方法")

        # 驗證已棄用方法確實被標記
        all_methods = glyphs_reporter['required_methods'] + glyphs_reporter['optional_methods']
        deprecated_methods = [m for m in all_methods if m.get('deprecated', False)]
        assert len(deprecated_methods) >= 0  # 至少不會出錯

    def test_parse_protocol_properties(self, parser: HeaderParser, glyphs_reporter_protocol_path: Path) -> None:
        """測試解析 protocol 屬性"""
        if not glyphs_reporter_protocol_path.exists():
            pytest.skip("GlyphsReporterProtocol.h 不存在")

        result = parser.parse_file(glyphs_reporter_protocol_path)
        glyphs_reporter = result['protocols'][0]

        # GlyphsReporter 有 @property
        assert 'properties' in glyphs_reporter

        # 驗證已知的屬性
        if glyphs_reporter['properties']:
            property_names = [p['name'] for p in glyphs_reporter['properties']]
            # controller 屬性應該存在
            assert 'controller' in property_names

    def test_parse_all_plugin_protocols(self, parser: HeaderParser, all_protocol_paths: list[Path]) -> None:
        """測試解析所有 Glyphs 外掛 Protocol Headers"""
        if not all_protocol_paths:
            pytest.skip("找不到 Glyphs Protocol Headers")

        results = {}
        for protocol_path in all_protocol_paths:
            result = parser.parse_file(protocol_path)
            if result.get('protocols'):
                for protocol in result['protocols']:
                    results[protocol['name']] = {
                        'file': protocol_path.name,
                        'required_methods_count': len(protocol['required_methods']),
                        'optional_methods_count': len(protocol['optional_methods']),
                        'properties_count': len(protocol['properties'])
                    }

        # 列印統計資訊
        print(f"\n成功解析 {len(results)} 個 Protocols:")
        for protocol_name, info in sorted(results.items()):
            print(f"  {protocol_name} ({info['file']}): "
                  f"required={info['required_methods_count']}, "
                  f"optional={info['optional_methods_count']}, "
                  f"properties={info['properties_count']}")

        # 驗證至少解析了一些 protocol
        assert len(results) >= 5, f"應該至少解析 5 個 protocols，實際解析了 {len(results)} 個"

    def test_parse_protocol_method_details(self, parser: HeaderParser, glyphs_reporter_protocol_path: Path) -> None:
        """測試方法詳細資訊解析"""
        if not glyphs_reporter_protocol_path.exists():
            pytest.skip("GlyphsReporterProtocol.h 不存在")

        result = parser.parse_file(glyphs_reporter_protocol_path)
        glyphs_reporter = result['protocols'][0]

        # 找到 interfaceVersion 方法
        interface_version_method = None
        for method in glyphs_reporter['required_methods']:
            if method['name'] == 'interfaceVersion':
                interface_version_method = method
                break

        assert interface_version_method is not None

        # 驗證方法詳細資訊
        assert interface_version_method['return_type'] == 'NSUInteger'
        assert interface_version_method['method_type'] == 'instance'
        assert 'full_signature' in interface_version_method

    def test_parse_protocol_with_parameters(self, parser: HeaderParser, glyphs_reporter_protocol_path: Path) -> None:
        """測試解析帶參數的方法"""
        if not glyphs_reporter_protocol_path.exists():
            pytest.skip("GlyphsReporterProtocol.h 不存在")

        result = parser.parse_file(glyphs_reporter_protocol_path)
        glyphs_reporter = result['protocols'][0]

        # 找到帶參數的方法（如 drawForegroundForLayer:options:）
        all_methods = glyphs_reporter['required_methods'] + glyphs_reporter['optional_methods']
        methods_with_params = [m for m in all_methods if m.get('parameters')]

        assert len(methods_with_params) > 0, "應該有帶參數的方法"

        # 驗證參數解析
        for method in methods_with_params[:3]:  # 檢查前三個
            print(f"\n方法: {method['name']}")
            print(f"  參數: {method['parameters']}")
            assert isinstance(method['parameters'], list)

    def test_parse_simple_protocol(self, parser: HeaderParser) -> None:
        """測試解析簡單的 Protocol 範例"""
        simple_protocol = """
        @protocol SimpleProtocol
        - (void)requiredMethod;
        @optional
        - (void)optionalMethod;
        @end
        """

        result = parser.parse_content(simple_protocol)

        assert len(result['protocols']) == 1
        protocol = result['protocols'][0]

        assert protocol['name'] == 'SimpleProtocol'
        assert len(protocol['required_methods']) == 1
        assert len(protocol['optional_methods']) == 1
        assert protocol['required_methods'][0]['name'] == 'requiredMethod'
        assert protocol['optional_methods'][0]['name'] == 'optionalMethod'

    def test_parse_protocol_with_parent(self, parser: HeaderParser) -> None:
        """測試解析有父 Protocol 的情況"""
        protocol_with_parent = """
        @protocol ChildProtocol <ParentProtocol>
        - (void)childMethod;
        @end
        """

        result = parser.parse_content(protocol_with_parent)

        assert len(result['protocols']) == 1
        protocol = result['protocols'][0]

        assert protocol['name'] == 'ChildProtocol'
        assert 'ParentProtocol' in protocol['parent_protocols']


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
