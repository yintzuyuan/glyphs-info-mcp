#!/usr/bin/env python3
"""
Glyphs SDK Method Mapper (Abstraction Layer)

Handles Glyphs SDK specific naming rules and abstraction layer mapping.

SDK Abstraction Levels:
1. Protocol required methods (require PyObjC conversion):
   - drawForegroundForLayer_options_ (PyObjC)
   - → drawForegroundForLayer:options: (Objective-C)

2. @objc.python_method decorated helper methods (keep Python style):
   - drawTextAtPoint (Python)
   - getHandleSize (Python)
   - activeLayer (Python)

3. python_method() wrapper functions:
   - ReporterPlugin.logToConsole = python_method(LogToConsole_AsClassExtension)
"""

import os
from typing import Optional, Any, TYPE_CHECKING
from enum import Enum
from pathlib import Path

if TYPE_CHECKING:
    from glyphs_info_mcp.modules.glyphs_api.objc_api.protocol_registry import ProtocolRegistry


class MethodType(Enum):
    """Method type classification"""
    PROTOCOL_METHOD = "protocol"      # Protocol required/optional methods (require PyObjC conversion)
    PYTHON_HELPER = "python_helper"   # @objc.python_method decorated helper methods
    PYTHON_WRAPPED = "python_wrapped"  # python_method() wrapped methods
    UNKNOWN = "unknown"


class GlyphsSDKMapper:
    """Glyphs SDK method mapper"""

    # Protocol Registry (dynamically loaded)
    _registry: Optional["ProtocolRegistry"] = None

    # Glyphs Headers path (supports environment variable)
    GLYPHS_HEADERS_PATH = Path(
        os.getenv(
            "GLYPHS_HEADERS_PATH",
            "/Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework/Versions/A/Headers"
        )
    )

    # GlyphsReporter Protocol required and optional methods (require PyObjC conversion)
    # Note: This list now serves as fallback, ProtocolRegistry dynamic loading is preferred
    REPORTER_PROTOCOL_METHODS = {
        # Required methods
        "interfaceVersion",  # No parameter method
        "title",             # No parameter method

        # Optional methods (require PyObjC conversion)
        "drawForegroundForLayer_options_",
        "drawBackgroundForLayer_options_",
        "drawForegroundForInactiveLayer_options_",
        "drawBackgroundForInactiveLayer_options_",
        "drawTextAtPoint_alignment_",
        "willActivate",
        "willDeactivate",
        "keyEquivalent",
        "modifierMask",
        "addMenuItemsForEvent_toMenu_",
        "addMenuItemsForEvent_controller_toMenu_",
        "foregroundInViewCoords",
        "backgroundInViewCoords",
        "inactiveLayerForeground",
        "inactiveLayerBackground",
        "preview",
        "needsExtraMainOutlineDrawingForInactiveLayers",
        "getScale_",
        "setController_",
    }

    # @objc.python_method decorated helper methods (keep Python style)
    PYTHON_HELPER_METHODS = {
        "drawTextAtPoint",  # SDK provided helper method
        "getHandleSize",    # SDK provided helper method
        "getScale",         # SDK provided helper method
        "activeLayer",      # SDK provided helper method
        "activePosition",   # SDK provided helper method
        # User-defined helper methods also use this decorator
    }

    # python_method() wrapped methods (function to method conversion)
    PYTHON_WRAPPED_METHODS = {
        "logToConsole",
        "logError",
        "loadNib",
    }

    @classmethod
    def initialize(cls, headers_path: Path) -> None:
        """
        Initialize Protocol Registry

        Args:
            headers_path: Headers directory path
        """
        try:
            from glyphs_info_mcp.modules.glyphs_api.objc_api.protocol_registry import ProtocolRegistry
            cls._registry = ProtocolRegistry(headers_path)
        except Exception:
            # If initialization fails, keep None (use fallback mode)
            cls._registry = None

    @classmethod
    def _initialize_if_needed(cls) -> None:
        """Auto-initialize (if not already initialized)"""
        if cls._registry is None:
            # Try using default Glyphs 3 Headers path
            if cls.GLYPHS_HEADERS_PATH.exists():
                cls.initialize(cls.GLYPHS_HEADERS_PATH)

    @classmethod
    def identify_method_type(cls, method_name: str, plugin_type: str = "reporter") -> MethodType:
        """
        Identify method type

        Args:
            method_name: Method name
            plugin_type: Plugin type (reporter, filter, palette, etc.)

        Returns:
            Method type
        """
        # Auto-initialize (if not already initialized)
        cls._initialize_if_needed()

        # Currently only implements Reporter, can be extended for other types
        if plugin_type == "reporter":
            # Prefer ProtocolRegistry (dynamically loaded)
            if cls._registry and cls._registry.is_protocol_method("GlyphsReporter", method_name):
                return MethodType.PROTOCOL_METHOD

            # Fallback: use manual list
            if method_name in cls.REPORTER_PROTOCOL_METHODS:
                return MethodType.PROTOCOL_METHOD

            # Check other method types
            if method_name in cls.PYTHON_HELPER_METHODS:
                return MethodType.PYTHON_HELPER
            elif method_name in cls.PYTHON_WRAPPED_METHODS:
                return MethodType.PYTHON_WRAPPED

        return MethodType.UNKNOWN

    @classmethod
    def needs_pyobjc_conversion(cls, method_name: str, plugin_type: str = "reporter") -> bool:
        """
        Determine if method needs PyObjC naming conversion

        Args:
            method_name: Method name
            plugin_type: Plugin type

        Returns:
            Whether PyObjC conversion is needed
        """
        method_type = cls.identify_method_type(method_name, plugin_type)
        return method_type == MethodType.PROTOCOL_METHOD

    @staticmethod
    def get_method_description(method_name: str, plugin_type: str = "reporter") -> str:
        """
        Get method description and usage suggestions

        Args:
            method_name: Method name
            plugin_type: Plugin type

        Returns:
            Method description
        """
        method_type = GlyphsSDKMapper.identify_method_type(method_name, plugin_type)

        if method_type == MethodType.PROTOCOL_METHOD:
            return (
                f"Protocol method (requires implementation)\n"
                f"- Uses PyObjC naming rules\n"
                f"- This is a {plugin_type.capitalize()} Protocol method"
            )
        elif method_type == MethodType.PYTHON_HELPER:
            return (
                f"SDK helper method\n"
                f"- Uses @objc.python_method decorator\n"
                f"- Keeps Python style naming\n"
                f"- Optional implementation"
            )
        elif method_type == MethodType.PYTHON_WRAPPED:
            return (
                f"Python wrapped method\n"
                f"- Uses python_method() function wrapper\n"
                f"- SDK predefined helper functionality"
            )
        else:
            return "Unknown method type"

    @staticmethod
    def get_implementation_template(
        method_name: str,
        plugin_type: str = "reporter",
        method_info: dict | None = None
    ) -> Optional[str]:
        """
        Get method implementation template

        Args:
            method_name: Method name
            plugin_type: Plugin type
            method_info: Protocol method info (optional)
                Contains: parameters, return_type, etc.

        Returns:
            Implementation template or None
        """
        method_type = GlyphsSDKMapper.identify_method_type(method_name, plugin_type)

        if method_type == MethodType.PROTOCOL_METHOD:
            # If Protocol data available, generate enhanced template
            if method_info:
                if method_info.get('parameters'):
                    # Has parameters: generate complete parameter list and docstring
                    param_names = GlyphsSDKMapper._extract_parameter_names(method_info['parameters'])
                    params_str = ', '.join(['self'] + param_names)

                    # Generate docstring
                    docstring = GlyphsSDKMapper._generate_docstring(
                        plugin_type,
                        method_info.get('parameters'),
                        method_info.get('return_type')
                    )

                    return f"def {method_name}({params_str}):\n    {docstring}\n    pass"
                else:
                    # No parameters: only generate docstring
                    docstring = GlyphsSDKMapper._generate_docstring(
                        plugin_type,
                        None,
                        method_info.get('return_type')
                    )

                    return f"def {method_name}(self):\n    {docstring}\n    return ..."
            else:
                # Fallback: use legacy template
                if '_' in method_name:
                    return f"def {method_name}(self, ...):\n    # Implement Protocol method\n    pass"
                else:
                    return f"def {method_name}(self):\n    # Implement Protocol method\n    return ..."

        elif method_type == MethodType.PYTHON_HELPER:
            return f"@objc.python_method\ndef {method_name}(self, ...):\n    # Implement helper method\n    pass"

        elif method_type == MethodType.PYTHON_WRAPPED:
            return f"# {method_name} is predefined by SDK\n# Use directly: self.{method_name}(...)"

        return None

    @classmethod
    def list_protocol_methods(cls, plugin_type: str = "reporter") -> dict[str, list[str]]:
        """
        List all Protocol methods for specific plugin type

        Args:
            plugin_type: Plugin type

        Returns:
            Categorized method list
        """
        # Auto-initialize (if not already initialized)
        cls._initialize_if_needed()

        # Protocol name mapping
        protocol_map = {
            "reporter": "GlyphsReporter",
            "filter": "GlyphsFilter",
            "palette": "GlyphsPalette",
        }

        # Prefer ProtocolRegistry (dynamically loaded)
        if cls._registry:
            protocol_name = protocol_map.get(plugin_type)
            if protocol_name:
                return cls._registry.get_categorized_methods(protocol_name)

        # Fallback: use manual list (reporter only)
        if plugin_type == "reporter":
            return {
                "required": ["interfaceVersion", "title"],
                "optional": [
                    m for m in cls.REPORTER_PROTOCOL_METHODS
                    if m not in ["interfaceVersion", "title"]
                ]
            }

        return {"required": [], "optional": []}

    @staticmethod
    def _extract_parameter_names(parameters: list[str]) -> list[str]:
        """
        Extract Python parameter names from Objective-C parameter list

        Supports two formats:
        1. Objective-C full signature: ["(GSLayer *)layer", "(NSDictionary *)options"]
        2. HeaderParser format: ["GSLayer * layer", "NSDictionary * options"]

        Args:
            parameters: Objective-C parameter list

        Returns:
            Python parameter name list
                Example: ["layer", "options"]
        """
        import re

        names = []
        for param in parameters:
            # Try format 1: (Type *)name or (Type)name
            match = re.search(r'\([^)]*\)\s*\*?\s*(\w+)', param)
            if match:
                names.append(match.group(1))
                continue

            # Try format 2: Type * name or Type name (HeaderParser format)
            # Last word is the parameter name
            parts = param.strip().split()
            if parts:
                # Remove possible pointer symbol (*)
                param_name = parts[-1].strip('*')
                if param_name:
                    names.append(param_name)

        return names

    @staticmethod
    def _generate_docstring(
        plugin_type: str,
        parameters: list[str] | None = None,
        return_type: str | None = None
    ) -> str:
        """
        Generate basic docstring

        Args:
            plugin_type: Plugin type
            parameters: Objective-C parameter list
            return_type: Return type

        Returns:
            Basic docstring string
        """
        protocol_name = f"{plugin_type.capitalize()}Plugin Protocol" if plugin_type != "reporter" else "GlyphsReporter Protocol"

        docstring = f'"""\n    {protocol_name} method\n'

        # If has parameters, add Args section
        if parameters:
            param_names = GlyphsSDKMapper._extract_parameter_names(parameters)
            if param_names:
                docstring += '    \n    Args:\n'
                for i, param_name in enumerate(param_names):
                    # Extract type info from original parameter
                    param = parameters[i]

                    # Try two formats to extract type
                    if '(' in param:
                        # Format 1: (Type *)name
                        param_type = param.split(')')[0].strip('(').strip()
                    else:
                        # Format 2: Type * name (HeaderParser format)
                        # Remove parameter name, keep only type part
                        parts = param.strip().rsplit(maxsplit=1)
                        param_type = parts[0].strip() if len(parts) > 1 else "id"

                    docstring += f'        {param_name}: {param_type} object\n'

        docstring += '    """'
        return docstring
