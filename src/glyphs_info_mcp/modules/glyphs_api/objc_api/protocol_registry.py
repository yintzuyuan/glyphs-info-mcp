#!/usr/bin/env python3
"""
Protocol Registry - Dynamic Protocol Method Registry

Automatically loads and manages Objective-C Protocol definitions,
providing zero-maintenance Protocol method query service.
"""

from pathlib import Path
from typing import Any, Optional
from glyphs_info_mcp.modules.glyphs_api.api.objc_header_parser import HeaderParser
from glyphs_info_mcp.modules.glyphs_api.objc_api.pyobjc_converter import PyObjCConverter


class ProtocolRegistry:
    """Dynamic Protocol method registry"""

    def __init__(self, headers_path: Path):
        """
        Initialize Protocol Registry

        Args:
            headers_path: Headers file directory path
        """
        self.headers_path = headers_path
        self.parser = HeaderParser()
        self.converter = PyObjCConverter()

        # Cache: {protocol_name: set[python_method_names]}
        self._method_cache: dict[str, set[str]] = {}

        # Cache: {protocol_name: {python_method_name: method_info}}
        self._method_info_cache: dict[str, dict[str, dict]] = {}

    def get_protocol_methods(self, protocol_name: str) -> set[str]:
        """
        Get all PyObjC method names for a Protocol

        Args:
            protocol_name: Protocol name (e.g., "GlyphsReporter")

        Returns:
            Set of method names in PyObjC format
        """
        # Check cache
        if protocol_name in self._method_cache:
            return self._method_cache[protocol_name]

        # Load Protocol definition
        protocol_def = self.parser.load_protocol(protocol_name, self.headers_path)

        if not protocol_def:
            # Protocol doesn't exist, return empty set
            self._method_cache[protocol_name] = set()
            return set()

        # Collect all methods (required + optional)
        all_methods = (
            protocol_def.get('required_methods', []) +
            protocol_def.get('optional_methods', [])
        )

        # Convert to PyObjC format and filter deprecated methods
        python_methods = set()
        method_info_map = {}

        for method in all_methods:
            # Skip deprecated methods
            if method.get('deprecated', False):
                continue

            # Skip properties (may need special handling)
            # Currently skipping, can add support in the future
            if method.get('is_property', False):
                continue

            # Convert Objective-C method name to PyObjC format
            # Prefer full_signature (contains complete method labels)
            if 'full_signature' in method:
                python_name = self.converter.objc_to_python(method['full_signature'])
            else:
                # Fallback: construct from name and parameters
                objc_name = method['name']
                python_name = self._convert_to_python_name(objc_name, method.get('parameters', []))

            python_methods.add(python_name)
            method_info_map[python_name] = method

        # Cache results
        self._method_cache[protocol_name] = python_methods
        self._method_info_cache[protocol_name] = method_info_map

        return python_methods

    def _convert_to_python_name(self, objc_name: str, parameters: list) -> str:
        """
        Convert Objective-C method name to PyObjC format

        Args:
            objc_name: First part of Objective-C method name (e.g., "drawForegroundForLayer")
            parameters: HeaderParser format parameter list
                       Example: ['GSLayer * layer', 'NSDictionary * options']

        Returns:
            Method name in PyObjC format (e.g., "drawForegroundForLayer_options_")
        """
        # If no parameters, return method name directly
        if not parameters:
            return objc_name

        # Construct complete Objective-C signature
        # Objective-C rules:
        # - First parameter: methodName:(Type *)param
        # - Subsequent parameters: label:(Type *)param
        # HeaderParser returns parameter format: 'Type * paramName'

        # Extract parameter names from parameters
        param_labels = []
        for param_str in parameters:
            # HeaderParser format: 'GSLayer * layer' or 'NSDictionary * options'
            # Extract last word as parameter name
            parts = param_str.strip().split()
            if parts:
                param_name = parts[-1].strip('*')
                param_labels.append(param_name)

        # Construct Objective-C signature
        # First parameter: drawForegroundForLayer:
        # Subsequent parameters: options:, etc.
        if len(param_labels) == 1:
            # Single parameter: drawForegroundForLayer:
            objc_signature = f"{objc_name}:"
        else:
            # Multiple parameters: drawForegroundForLayer:options:
            objc_signature = f"{objc_name}:{':'.join(param_labels[1:])}:"

        # Use PyObjCConverter to convert to Python format
        python_name = self.converter.objc_to_python(objc_signature)

        return python_name

    def validate_against_manual_list(
        self,
        protocol_name: str,
        manual_set: set[str]
    ) -> dict[str, Any]:
        """
        Validate differences between manual list and auto-loaded methods

        Args:
            protocol_name: Protocol name
            manual_set: Manually maintained method name set

        Returns:
            Difference report:
            {
                'missing_in_manual': set[str],  # Methods in auto-load but missing in manual list
                'extra_in_manual': set[str],    # Methods in manual list but not in auto-load
                'match_rate': float             # Match rate (0.0-1.0)
            }
        """
        auto_methods = self.get_protocol_methods(protocol_name)

        missing = auto_methods - manual_set
        extra = manual_set - auto_methods

        # Calculate match rate
        total = len(auto_methods | manual_set)
        matched = len(auto_methods & manual_set)
        match_rate = matched / total if total > 0 else 0.0

        return {
            'missing_in_manual': missing,
            'extra_in_manual': extra,
            'match_rate': match_rate
        }

    def get_method_info(
        self,
        protocol_name: str,
        method_name: str
    ) -> Optional[dict]:
        """
        Get detailed information for a method

        Args:
            protocol_name: Protocol name
            method_name: Python method name

        Returns:
            Method info dict or None
        """
        # Ensure Protocol is loaded
        self.get_protocol_methods(protocol_name)

        # Get method info from cache
        protocol_cache = self._method_info_cache.get(protocol_name, {})
        return protocol_cache.get(method_name)

    def is_protocol_method(self, protocol_name: str, method_name: str) -> bool:
        """
        Check if method is a Protocol method

        Args:
            protocol_name: Protocol name
            method_name: Python method name

        Returns:
            Whether it's a Protocol method
        """
        methods = self.get_protocol_methods(protocol_name)
        return method_name in methods

    def get_categorized_methods(self, protocol_name: str) -> dict[str, list[str]]:
        """
        Get Protocol methods categorized (required/optional)

        Args:
            protocol_name: Protocol name

        Returns:
            Categorized method list
            {
                'required': ['method1', 'method2'],
                'optional': ['method3', 'method4']
            }
        """
        # Load Protocol definition
        protocol_def = self.parser.load_protocol(protocol_name, self.headers_path)

        if not protocol_def:
            return {"required": [], "optional": []}

        result: dict[str, list[str]] = {"required": [], "optional": []}

        # Process required methods
        for method in protocol_def.get('required_methods', []):
            if method.get('deprecated', False) or method.get('is_property', False):
                continue

            if 'full_signature' in method:
                python_name = self.converter.objc_to_python(method['full_signature'])
            else:
                python_name = self._convert_to_python_name(method['name'], method.get('parameters', []))

            result["required"].append(python_name)

        # Process optional methods
        for method in protocol_def.get('optional_methods', []):
            if method.get('deprecated', False) or method.get('is_property', False):
                continue

            if 'full_signature' in method:
                python_name = self.converter.objc_to_python(method['full_signature'])
            else:
                python_name = self._convert_to_python_name(method['name'], method.get('parameters', []))

            result["optional"].append(python_name)

        return result
