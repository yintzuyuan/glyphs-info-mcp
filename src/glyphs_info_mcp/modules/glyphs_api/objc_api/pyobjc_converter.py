#!/usr/bin/env python3
"""
PyObjC Naming Converter (Base Layer)

Handles pure PyObjC naming rule conversion, without Glyphs SDK abstraction layer concerns.

PyObjC naming rules:
- Objective-C: - (void)doSomething:(id)arg1 withSomething:(id)arg2;
- Python: doSomething_withSomething_(arg1, arg2)

Rules:
1. Replace colons (:) with underscores (_)
2. Keep trailing underscores as syntax markers
3. No underscore for parameterless methods
"""

import re
from typing import Optional


class PyObjCConverter:
    """PyObjC naming converter"""

    @staticmethod
    def objc_to_python(objc_signature: str) -> str:
        """
        Convert Objective-C method signature to Python method name

        Args:
            objc_signature: Objective-C method signature
                Examples:
                - "doSomething:(id)arg withOther:(id)other"
                - "title"
                - "interfaceVersion"

        Returns:
            Python method name
                Examples:
                - "doSomething_withOther_"
                - "title"
                - "interfaceVersion"
        """
        # Remove leading - or + symbol and return type
        signature = objc_signature.strip()

        # Remove method type prefix (- or +) and return type
        # Example: - (void)doSomething: → doSomething:
        if signature.startswith(('-', '+')):
            # Remove "- (return_type)" part
            match = re.match(r'[-+]\s*\([^)]+\)\s*(.+)', signature)
            if match:
                signature = match.group(1).strip()

        # Remove __attribute__ and similar markers
        signature = re.sub(r'__attribute__\(\([^)]+\)\)', '', signature)
        signature = signature.strip()

        # If no colon, it's a parameterless method
        if ':' not in signature:
            # Remove possible parameter type declarations
            # Example: interfaceVersion; → interfaceVersion
            method_name = signature.split(';')[0].strip()
            return method_name

        # Extract all method name parts (parts before colons)
        # Example: doSomething:(id)arg withOther:(id)other
        # → ['doSomething', 'withOther']
        parts = []

        # Split into multiple parts
        segments = signature.split(':')

        for i, segment in enumerate(segments[:-1]):  # Last part is parameter or empty
            # Remove parameter types and parameter names, keep only method name parts
            # Example: " withOther(id)arg " → "withOther"
            # Example: " (id)arg doSomething" → "doSomething"

            # Remove parameter types (id), (NSString *), etc.
            segment = re.sub(r'\([^)]*\)\s*\w*', '', segment).strip()

            # Get the last word (method name part)
            words = segment.split()
            if words:
                parts.append(words[-1])

        # Combine into Python method name
        if not parts:
            return signature.split(':')[0].strip()

        # Join with underscores and add trailing underscore
        python_name = '_'.join(parts) + '_'

        return python_name

    @staticmethod
    def python_to_objc(python_name: str, param_count: Optional[int] = None) -> str:
        """
        Convert Python method name to Objective-C method signature (basic form)

        Args:
            python_name: Python method name
                Examples:
                - "doSomething_withOther_"
                - "title"
            param_count: Parameter count (for validation)

        Returns:
            Objective-C method signature (basic form, without parameter types)
                Examples:
                - "doSomething:withOther:"
                - "title"
        """
        # Check if has parameters (check if original name ends with underscore)
        has_params = python_name.endswith('_')

        # Remove trailing underscores
        name = python_name.rstrip('_')

        # If no parameters, return method name directly
        if not has_params:
            return name

        # If no underscore separator (single parameter method like "setValue_")
        if '_' not in name:
            if param_count is not None and param_count != 1:
                raise ValueError(
                    f"Parameter count mismatch: expected 1, got {param_count}"
                )
            return name + ':'

        # Split method name parts (multi-parameter method)
        parts = name.split('_')

        # Combine into Objective-C signature
        # Example: ['doSomething', 'withOther'] → "doSomething:withOther:"
        objc_signature = ':'.join(parts) + ':'

        # Validate parameter count (if provided)
        if param_count is not None:
            expected_count = len(parts)
            if expected_count != param_count:
                raise ValueError(
                    f"Parameter count mismatch: expected {expected_count}, got {param_count}"
                )

        return objc_signature

    @staticmethod
    def extract_method_name(objc_signature: str) -> str:
        """
        Extract method name part from complete Objective-C method signature

        Args:
            objc_signature: Complete Objective-C method signature
                Examples:
                - "- (void)drawForegroundForLayer:(GSLayer *)layer options:(NSDictionary *)options;"
                - "- (NSUInteger)interfaceVersion;"

        Returns:
            Method name (without parameter types)
                Examples:
                - "drawForegroundForLayer:options:"
                - "interfaceVersion"
        """
        # Remove leading method type and return type
        signature = objc_signature.strip()

        # Remove "- (return_type)" or "+ (return_type)" part
        match = re.match(r'[-+]\s*\([^)]+\)\s*(.+)', signature)
        if match:
            signature = match.group(1).strip()

        # Remove trailing semicolon
        signature = signature.rstrip(';').strip()

        # Remove __attribute__ and similar markers
        signature = re.sub(r'__attribute__\(\([^)]+\)\)', '', signature)
        signature = signature.strip()

        # Remove parameter types and parameter names
        # Example: drawForegroundForLayer:(GSLayer *)layer options:(NSDictionary *)options
        # → drawForegroundForLayer:options:

        if ':' not in signature:
            # Parameterless method
            return signature.split()[0] if signature.split() else signature

        # Extract method name parts
        parts = []
        segments = signature.split(':')

        for i, segment in enumerate(segments[:-1]):
            # Remove parameter types and parameter names
            segment = re.sub(r'\([^)]*\)\s*\*?\s*\w*', '', segment).strip()

            # Get the last word
            words = segment.split()
            if words:
                parts.append(words[-1])

        return ':'.join(parts) + ':'

    @staticmethod
    def is_valid_python_name(name: str) -> bool:
        """
        Validate if it's a valid PyObjC Python method name

        Args:
            name: Python method name

        Returns:
            Whether it's valid
        """
        if not name:
            return False

        # Check if it matches Python naming rules
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name.rstrip('_')):
            return False

        return True

    @staticmethod
    def format_full_signature(
        method_name: str,
        parameters: list[tuple[str, str]],
        return_type: str = 'void',
        method_type: str = 'instance'
    ) -> str:
        """
        Format complete Objective-C method signature

        Args:
            method_name: Method name (without parameters)
                Example: "drawForegroundForLayer:options:"
            parameters: Parameter list [(type, name)]
                Example: [("GSLayer *", "layer"), ("NSDictionary *", "options")]
            return_type: Return type
            method_type: Method type ('instance' or 'class')

        Returns:
            Complete Objective-C method signature
                Example: "- (void)drawForegroundForLayer:(GSLayer *)layer options:(NSDictionary *)options"
        """
        prefix = '-' if method_type == 'instance' else '+'

        if ':' not in method_name:
            # Parameterless method
            return f"{prefix} ({return_type}){method_name}"

        # Split method name parts
        name_parts = method_name.rstrip(':').split(':')

        if len(name_parts) != len(parameters):
            raise ValueError(
                f"Method name parts ({len(name_parts)}) doesn't match parameter count ({len(parameters)})"
            )

        # Combine complete signature
        signature_parts = [f"{prefix} ({return_type})"]

        for i, (name_part, (param_type, param_name)) in enumerate(zip(name_parts, parameters)):
            if i == 0:
                signature_parts.append(f"{name_part}:({param_type}){param_name}")
            else:
                signature_parts.append(f" {name_part}:({param_type}){param_name}")

        return ''.join(signature_parts)
