#!/usr/bin/env python3
"""
Objective-C API Module for Glyphs.app
Handles Objective-C Headers queries and documentation

This is a lightweight wrapper for APIModule, exposing only Objective-C Headers related functionality.
"""

import logging
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

# Use shared core library
project_root = Path(__file__).parent.parent.parent.parent
shared_core_path = str(project_root / "src" / "shared")
if shared_core_path not in sys.path:
    sys.path.insert(0, shared_core_path)

from glyphs_info_mcp.shared.core.base_module import BaseMCPModule

logger = logging.getLogger(__name__)

# Dynamically import APIModule
import importlib.util

def import_api_module(module_path: str, class_name: str) -> Any:
    """Dynamically import API module"""
    spec = importlib.util.spec_from_file_location(class_name.lower(), module_path)
    if spec is None:
        raise ImportError(f"Cannot find module spec for {module_path}")
    module: ModuleType = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise ImportError(f"Module spec has no loader for {module_path}")
    spec.loader.exec_module(module)
    return getattr(module, class_name)

# Get APIModule
api_module_path = Path(__file__).parent.parent / "api" / "api_module.py"
APIModule = import_api_module(str(api_module_path), "APIModule")

# Import naming conversion tools
from glyphs_info_mcp.modules.glyphs_api.objc_api.pyobjc_converter import PyObjCConverter
from glyphs_info_mcp.modules.glyphs_api.objc_api.glyphs_sdk_mapper import GlyphsSDKMapper, MethodType


class ObjectiveCAPIModule(BaseMCPModule):
    """Objective-C API Module - Handles Objective-C Headers queries"""

    # Glyphs Headers path (supports environment variable)
    GLYPHS_HEADERS_PATH = Path(
        os.getenv(
            "GLYPHS_HEADERS_PATH",
            "/Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework/Headers/"
        )
    )

    def __init__(self, name: str = "objc-api", data_path: Path | None = None):
        super().__init__(name, data_path)
        # Use APIModule as underlying implementation
        self.api_module = APIModule("api-headers", data_path)
        self.search_engine = None

    def set_search_engine(self, search_engine: Any) -> None:
        """Set unified search engine (called by server.py)"""
        self.search_engine = search_engine
        # Sync to underlying API module
        if hasattr(self.api_module, 'set_search_engine'):
            self.api_module.set_search_engine(search_engine)

    def initialize(self) -> bool:
        """Initialize Objective-C API module"""
        try:
            # Initialize underlying API module
            if not self.api_module.initialize():
                logger.warning("API module initialization failed")
                return False

            self.is_initialized = True

            header_files_count = (
                self.api_module.header_search_engine.get_indexed_files_count()
                if self.api_module.header_search_engine
                else 0
            )

            logger.info(
                f"Objective-C API module initialized with {header_files_count} header files"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Objective-C API module: {e}")
            return False

    def core_search(self, query: str, max_results: int = 5, **kwargs: Any) -> list[dict[str, Any]]:
        """Core search function - exclusively for unified search engine

        Returns structured search results without vocabulary processing or formatting

        Args:
            query: Search query (preprocessed)
            max_results: Maximum number of results
            **kwargs: Additional search parameters (e.g., scope)

        Returns:
            List of structured search results
        """
        if not self.is_initialized:
            return []

        # Delegate to underlying API module's core search
        if hasattr(self.api_module, 'core_search'):
            scope = kwargs.get('scope', 'auto')
            return self.api_module.core_search(query, max_results, scope)

        return []

    def get_tools(self) -> dict[str, Callable[..., Any]]:
        """Get available tools dictionary - Objective-C Headers + naming conversion tools"""
        return {
            # Headers query tools
            'api_search_objc_headers': self.search_objc_headers,
            'api_get_objc_header': self.get_objc_header,
            'api_list_plugin_protocols': self.list_plugin_protocols,
            'api_get_protocol_methods': self.get_protocol_methods,
            # Naming conversion tools
            'api_convert_objc_to_python': self.convert_objc_to_python,
            'api_convert_python_to_objc': self.convert_python_to_objc,
            'api_identify_method_type': self.identify_method_type,
            'api_get_method_template': self.get_method_template
        }

    def get_module_info(self) -> dict[str, Any]:
        """Get module information"""
        return {
            'name': self.name,
            'description': 'Objective-C API Headers query + naming conversion tools',
            'tools_count': 8,
            'status': 'initialized' if self.is_initialized else 'not_initialized'
        }

    # ========== Public Tool Methods ==========

    def search_objc_headers(self, query: str, max_results: int = 5) -> str:
        """
        [OBJECTIVE-C HEADERS] Search Objective-C Header files

        Search within 174 Header files in GlyphsCore.framework. These Headers
        define core protocols and classes for Objective-C plugin development, serving as the foundation for Xcode development.

        Use cases:
        - View Objective-C plugin protocol definitions (e.g., GlyphsReporterProtocol)
        - Confirm complete properties and method signatures of classes
        - API reference for Xcode plugin development

        Related tools:
        - Use sdk_list_xcode_templates to view complete Xcode templates
        - Use sdk_list_xcode_samples to view actual sample projects

        Args:
            query: Search keyword (class name, method name, protocol name)
            max_results: Maximum number of results (default: 5)

        Returns:
            List of matching Header files and related content
        """
        if not self.is_initialized:
            return "API module not initialized"

        # Delegate to underlying API module
        return self.api_module._search_objc_api_headers(query, max_results)

    def get_objc_header(self, header_query: str) -> str:
        """
        [OBJECTIVE-C HEADERS] Get Objective-C Header file content

        Get complete Header content by file name or class name. Header files contain
        Objective-C protocol definitions, class interfaces, and method declarations,
        serving as core reference material for Xcode plugin development.

        Use cases:
        - View complete protocol definitions and method signatures
        - Confirm class properties and method lists
        - API documentation for Xcode plugin development

        Related tools:
        - Use sdk_get_xcode_template to view template code using these Headers
        - Use sdk_get_xcode_sample to view actual usage examples

        Args:
            header_query: Header file name or class name (e.g., "GSFont", "GSFont.h")

        Returns:
            Complete Header file content
        """
        if not self.is_initialized:
            return "API module not initialized"

        # Delegate to underlying API module
        return self.api_module._get_objc_header(header_query)

    def list_plugin_protocols(self, show_details: bool = False) -> str:
        """
        [PROTOCOL QUERY] List all Glyphs plugin Protocols

        List all plugin-related Protocol definitions in GlyphsCore.framework. These Protocols
        define required and optional methods for different plugin types, serving as key reference for Python-to-Objective-C conversion.

        Use cases:
        - View all available plugin Protocol types
        - Understand basic information for each Protocol
        - Confirm Protocol name for specific plugin types

        Related tools:
        - Use api_get_protocol_methods to view detailed methods for specific Protocol
        - Use sdk_list_xcode_templates to view Protocol usage examples

        Args:
            show_details: Whether to show detailed information (method count, properties, etc.)

        Returns:
            List of all plugin protocols with basic information
        """
        if not self.is_initialized:
            return "API module not initialized"

        try:
            # Import HeaderParser
            from glyphs_info_mcp.modules.glyphs_api.api.objc_header_parser import HeaderParser

            parser = HeaderParser()

            # Find all Glyphs*Protocol.h files
            headers_dir = self.GLYPHS_HEADERS_PATH
            protocol_files = list(headers_dir.glob("Glyphs*Protocol.h"))

            if not protocol_files:
                return "❌ Glyphs Protocol Headers not found"

            # Parse all Protocols
            all_protocols = []
            for protocol_file in protocol_files:
                result = parser.parse_file(protocol_file)
                if result.get('protocols'):
                    for protocol in result['protocols']:
                        protocol['source_file'] = protocol_file.name
                        all_protocols.append(protocol)

            if not all_protocols:
                return "❌ No Protocol definitions found"

            # Format output
            output = [f"## 🔌 Glyphs Plugin Protocols ({len(all_protocols)})\n"]

            # Sort by Protocol name
            all_protocols.sort(key=lambda p: p['name'])

            for protocol in all_protocols:
                output.append(f"### {protocol['name']}")
                output.append(f"**Source file**: {protocol['source_file']}\n")

                if show_details:
                    # Show detailed information
                    required_count = len(protocol.get('required_methods', []))
                    optional_count = len(protocol.get('optional_methods', []))
                    properties_count = len(protocol.get('properties', []))
                    deprecated_count = len(protocol.get('deprecated_methods', []))

                    output.append(f"- **Required methods**: {required_count}")
                    output.append(f"- **Optional methods**: {optional_count}")
                    output.append(f"- **Properties**: {properties_count}")
                    if deprecated_count > 0:
                        output.append(f"- **Deprecated methods**: {deprecated_count}")

                    # Show parent Protocols
                    if protocol.get('parent_protocols'):
                        parents = ', '.join(protocol['parent_protocols'])
                        output.append(f"- **Inherits from**: {parents}")

                    output.append("")
                else:
                    # Brief information
                    total_methods = len(protocol.get('required_methods', [])) + len(protocol.get('optional_methods', []))
                    output.append(f"- Method count: {total_methods}")
                    output.append("")

            # Add usage suggestions
            output.append("\n---")
            output.append("\n💡 **Usage suggestions**:")
            output.append("- Use `api_get_protocol_methods(protocol_name)` to view detailed methods for specific Protocol")
            output.append("- Use `api_get_protocol_methods(protocol_name, show_deprecated=False)` to hide deprecated methods")

            return "\n".join(output)

        except Exception as e:
            logger.error(f"Failed to list plugin protocols: {e}")
            return f"❌ Error listing Protocols: {str(e)}"

    def get_protocol_methods(
        self,
        protocol_name: str,
        show_deprecated: bool = True,
        show_optional_only: bool = False
    ) -> str:
        """
        [PROTOCOL QUERY] Get detailed method information for specific Protocol

        Query all methods of a specific Protocol, including required/optional classification, method signatures,
        parameter types, and other detailed information. This is the core tool for Python-to-Objective-C conversion.

        Use cases:
        - Confirm which required methods Python plugins need to implement
        - View Objective-C method signatures for conversion
        - Understand method parameter types and return values

        Related tools:
        - Use api_list_plugin_protocols to view all available Protocols
        - Use sdk_get_xcode_template to view Protocol usage examples

        Args:
            protocol_name: Protocol name (e.g., "GlyphsReporter", "GlyphsFilter")
            show_deprecated: Whether to show deprecated methods (default: True)
            show_optional_only: Show only optional methods (default: False)

        Returns:
            Detailed method information for Protocol, including Python-ObjC mapping
        """
        if not self.is_initialized:
            return "API module not initialized"

        try:
            # Import HeaderParser
            from glyphs_info_mcp.modules.glyphs_api.api.objc_header_parser import HeaderParser

            parser = HeaderParser()

            # Find all Glyphs*Protocol.h files
            headers_dir = self.GLYPHS_HEADERS_PATH
            protocol_files = list(headers_dir.glob("Glyphs*Protocol.h"))

            # Search for specified Protocol
            target_protocol = None
            source_file = None

            for protocol_file in protocol_files:
                result = parser.parse_file(protocol_file)
                for protocol in result.get('protocols', []):
                    if protocol['name'].lower() == protocol_name.lower():
                        target_protocol = protocol
                        source_file = protocol_file.name
                        break
                if target_protocol:
                    break

            if not target_protocol:
                # Provide suggestion
                suggestion = "Use `api_list_plugin_protocols()` to view all available Protocols"
                return f"❌ Protocol not found: {protocol_name}\n\n💡 {suggestion}"

            # Format output
            output = [f"## 🔌 {target_protocol['name']}\n"]
            output.append(f"**Source file**: {source_file}\n")

            # Parent Protocol
            if target_protocol.get('parent_protocols'):
                parents = ', '.join(target_protocol['parent_protocols'])
                output.append(f"**Inherits from**: {parents}\n")

            # Statistics
            required_methods = target_protocol.get('required_methods', [])
            optional_methods = target_protocol.get('optional_methods', [])
            properties = target_protocol.get('properties', [])

            output.append(f"### 📊 Statistics")
            output.append(f"- Required methods: {len(required_methods)}")
            output.append(f"- Optional methods: {len(optional_methods)}")
            output.append(f"- Properties: {len(properties)}")

            if target_protocol.get('deprecated_methods'):
                output.append(f"- Deprecated methods: {len(target_protocol['deprecated_methods'])}")

            output.append("")

            # Required methods
            if not show_optional_only and required_methods:
                output.append("### ✅ Required Methods (@required)\n")
                for method in required_methods:
                    if not show_deprecated and method.get('deprecated'):
                        continue
                    output.append(self._format_method(method))

            # Optional methods
            if optional_methods:
                output.append("### ⭕ Optional Methods (@optional)\n")
                for method in optional_methods:
                    if not show_deprecated and method.get('deprecated'):
                        continue
                    output.append(self._format_method(method))

            # Properties
            if properties and not show_optional_only:
                output.append("### 🔧 Properties (@property)\n")
                for prop in properties:
                    attrs = ', '.join(prop.get('attributes', []))
                    output.append(f"**{prop['name']}**")
                    output.append(f"- Type: `{prop['type']}`")
                    output.append(f"- Modifiers: `{attrs}`")
                    output.append("")

            # Add usage suggestions
            output.append("---")
            output.append("\n💡 **Python Plugin Development Tips**:")
            output.append(f"- Must implement all ✅ required methods ({len(required_methods)})")
            output.append(f"- Can optionally implement ⭕ optional methods ({len(optional_methods)})")
            output.append("- Refer to SDK Templates for Python method naming rules")

            return "\n".join(output)

        except Exception as e:
            logger.error(f"Failed to get protocol methods: {e}")
            return f"❌ Error getting Protocol methods: {str(e)}"

    def _format_method(self, method: dict[str, Any]) -> str:
        """Format single method information"""
        output = []

        # Method name
        name = method['name']
        if method.get('deprecated'):
            output.append(f"**{name}** ⚠️ *deprecated*")
        else:
            output.append(f"**{name}**")

        # Use full signature from HeaderParser directly
        full_signature = method.get('full_signature', '').strip()
        if full_signature:
            output.append(f"- Signature: `{full_signature}`")

        output.append("")
        return "\n".join(output)

    # ========== Naming Conversion Tools ==========

    def convert_objc_to_python(self, objc_signature: str) -> str:
        """
        [NAMING CONVERSION] Convert Objective-C method signature to Python method name

        Uses PyObjC naming rules to convert Objective-C method signatures to corresponding Python method names.
        This is a key tool for understanding Protocol method naming when developing Python plugins.

        Conversion rules:
        - No-parameter methods keep original name: interfaceVersion → interfaceVersion
        - Single-parameter methods: setValue:(id)value → setValue_
        - Multi-parameter methods: doSomething:(id)arg withOther:(id)other → doSomething_withOther_

        Use cases:
        - Confirm Python method name when implementing Objective-C Protocol methods
        - Understand PyObjC bridging naming rules
        - Convert Objective-C signatures from documentation to actual code

        Related tools:
        - Use api_convert_python_to_objc for reverse conversion
        - Use api_identify_method_type to determine method type
        - Use api_get_protocol_methods to view Protocol method signatures

        Args:
            objc_signature: Objective-C method signature
                Examples:
                - "- (void)drawForegroundForLayer:(GSLayer *)layer options:(NSDictionary *)options;"
                - "interfaceVersion"
                - "title"

        Returns:
            Python method name
                Examples:
                - "drawForegroundForLayer_options_"
                - "interfaceVersion"
                - "title"
        """
        try:
            python_name = PyObjCConverter.objc_to_python(objc_signature)
            return f"## Conversion Result\n\n**Objective-C**: `{objc_signature}`\n\n**Python**: `{python_name}`"
        except Exception as e:
            return f"Conversion failed: {str(e)}"

    def convert_python_to_objc(self, python_name: str, param_count: int | None = None) -> str:
        """
        [NAMING CONVERSION] Convert Python method name to Objective-C method signature

        Uses PyObjC naming rules to convert Python method names back to Objective-C method signatures.
        This is helpful for understanding the original Objective-C definition corresponding to a Python method.

        Conversion rules:
        - No-parameter methods: interfaceVersion → interfaceVersion
        - Single-parameter methods: setValue_ → setValue:
        - Multi-parameter methods: doSomething_withOther_ → doSomething:withOther:

        Use cases:
        - Reverse-engineer Objective-C documentation from Python code
        - Confirm the Protocol definition corresponding to a Python method
        - Understand PyObjC bridging mechanism

        Related tools:
        - Use api_convert_objc_to_python for forward conversion
        - Use api_get_protocol_methods to view complete Protocol definitions

        Args:
            python_name: Python method name
                Examples:
                - "drawForegroundForLayer_options_"
                - "interfaceVersion"
            param_count: Parameter count (for validation, optional)

        Returns:
            Objective-C method signature (basic form, without parameter types)
                Examples:
                - "drawForegroundForLayer:options:"
                - "interfaceVersion"
        """
        try:
            objc_name = PyObjCConverter.python_to_objc(python_name, param_count)
            return f"## Conversion Result\n\n**Python**: `{python_name}`\n\n**Objective-C**: `{objc_name}`"
        except ValueError as e:
            return f"Conversion failed: {str(e)}"
        except Exception as e:
            return f"Conversion failed: {str(e)}"

    def identify_method_type(self, method_name: str, plugin_type: str = "reporter") -> str:
        """
        [SDK METHOD ANALYSIS] Identify Glyphs SDK method type

        Analyzes method names and identifies their type within the Glyphs SDK architecture. This helps developers
        understand which methods need PyObjC conversion and which are helper methods provided by the SDK.

        Method types:
        1. Protocol methods (protocol) - Required/optional Protocol methods to implement
           - Uses PyObjC naming rules
           - Examples: drawForegroundForLayer_options_, interfaceVersion

        2. Python helper methods (python_helper) - Helper functions provided by SDK
           - Uses @objc.python_method decorator
           - Keeps Python-style naming
           - Examples: drawTextAtPoint, getHandleSize

        3. Python wrapped methods (python_wrapped) - Pre-defined SDK functions
           - Uses python_method() function wrapper
           - Examples: logToConsole, logError

        Use cases:
        - Confirm whether a method needs PyObjC naming conversion
        - Understand the method's role in the SDK architecture
        - Decide how to correctly implement a specific method

        Related tools:
        - Use api_get_method_template to get implementation templates
        - Use api_convert_objc_to_python to convert Protocol method names

        Args:
            method_name: Method name
            plugin_type: Plugin type (default: "reporter")

        Returns:
            Method type and detailed description
        """
        try:
            method_type = GlyphsSDKMapper.identify_method_type(method_name, plugin_type)
            description = GlyphsSDKMapper.get_method_description(method_name, plugin_type)
            needs_conversion = GlyphsSDKMapper.needs_pyobjc_conversion(method_name, plugin_type)

            output = [
                f"## Method Analysis\n",
                f"**Method name**: `{method_name}`",
                f"**Plugin type**: {plugin_type.capitalize()}",
                f"**Method type**: {method_type.value}\n",
                f"### Description\n",
                description,
                f"\n### PyObjC Conversion",
                f"Needs PyObjC naming conversion: {'✅ Yes' if needs_conversion else '❌ No'}"
            ]

            return "\n".join(output)
        except Exception as e:
            return f"Analysis failed: {str(e)}"

    def _lookup_protocol_method(self, method_name: str, plugin_type: str) -> dict | None:
        """
        Look up Protocol method definition

        Supports two formats:
        1. Python method name (PyObjC format): "drawForegroundForLayer_options_"
        2. Objective-C method name (first part): "drawForegroundForLayer"

        Args:
            method_name: Method name
            plugin_type: Plugin type

        Returns:
            Method info dict or None
        """
        try:
            # Check required components
            if not self.api_module.header_parser or not self.api_module.headers_base_path:
                return None

            # Map plugin type to Protocol name
            protocol_map = {
                "reporter": "GlyphsReporter",
                "filter": "GlyphsFilter",
                "palette": "GlyphsPalette",
                "tool": "GlyphsToolDraw",
                "fileformat": "GlyphsFileFormat"
            }

            protocol_name = protocol_map.get(plugin_type)
            if not protocol_name:
                return None

            # Load Protocol on demand (auto-cached)
            protocol = self.api_module.header_parser.load_protocol(
                protocol_name,
                self.api_module.headers_base_path
            )

            if not protocol:
                return None

            # Normalize method name: convert Python format to Objective-C first part
            search_name = method_name
            is_python_format = method_name.endswith('_')

            if is_python_format:
                # Remove trailing underscores and take first part only
                search_name = method_name.rstrip('_').split('_')[0]

            # Search in required and optional methods
            for method in protocol.get('required_methods', []) + protocol.get('optional_methods', []):
                if method['name'] == search_name:
                    # If Python name passed, validate parameter count
                    if is_python_format:
                        expected_params = len(method.get('parameters', []))
                        actual_params = method_name.count('_')
                        if expected_params != actual_params:
                            continue  # Parameter count mismatch, continue searching

                    return method

            return None

        except Exception as e:
            logger.debug(f"Failed to lookup protocol method: {e}")
            return None

    def get_method_template(self, method_name: str, plugin_type: str = "reporter") -> str:
        """
        [SDK CODE GENERATION] Get method implementation template

        Generates corresponding Python implementation templates based on method name and type. This helps developers
        quickly start implementing plugin methods while ensuring correct decorators and signatures are used.

        Template types:
        1. Protocol method templates - Include correct PyObjC naming and basic structure
        2. Python helper method templates - Include @objc.python_method decorator
        3. Python wrapped method templates - Explain how to use pre-defined SDK methods

        Use cases:
        - Quickly start implementing plugin methods
        - Ensure correct decorators and naming rules are used
        - Learn Glyphs SDK method implementation patterns

        Related tools:
        - Use api_identify_method_type to first identify method type
        - Use api_get_protocol_methods to view complete Protocol definitions
        - Use sdk_list_xcode_templates to view complete template code

        Args:
            method_name: Method name
            plugin_type: Plugin type (default: "reporter")

        Returns:
            Python implementation template code
        """
        try:
            # 1. Look up Protocol definition (if available)
            method_info = self._lookup_protocol_method(method_name, plugin_type)

            # 2. Pass to SDK Mapper to generate template
            template = GlyphsSDKMapper.get_implementation_template(
                method_name,
                plugin_type,
                method_info=method_info
            )
            method_type = GlyphsSDKMapper.identify_method_type(method_name, plugin_type)

            if template is None:
                return f"Cannot generate template: unknown method type\n\nMethod name: `{method_name}`"

            output = [
                f"## Implementation Template\n",
                f"**Method name**: `{method_name}`",
                f"**Method type**: {method_type.value}\n",
                f"```python",
                template,
                f"```"
            ]

            return "\n".join(output)
        except Exception as e:
            return f"Template generation failed: {str(e)}"
