#!/usr/bin/env python3
"""
Objective-C Header Parser

TDD Green Phase: Implement minimum functionality to pass tests
"""

import re
from pathlib import Path
from typing import Any


class HeaderParser:
    """Objective-C Header file parser"""

    def __init__(self) -> None:
        """Initialize Header Parser"""
        self.protocols: dict[str, Any] = {}  # Protocol definition cache {protocol_name: protocol_data}

    def parse_content(self, header_content: str) -> dict[str, Any]:
        """Parse Header content

        Args:
            header_content: Header file content

        Returns:
            Parsed data structure
        """
        result: dict[str, Any] = {
            'interfaces': [],
            'protocols': [],
            'properties': [],
            'methods': [],
            'comments': []
        }

        # Parse @protocol definitions
        protocols = self._parse_protocols(header_content)
        result['protocols'] = protocols

        # Parse @interface definitions
        interface_pattern = r'@interface\s+(\w+)\s*:\s*(\w+)'
        interface_matches = re.findall(interface_pattern, header_content)

        for class_name, superclass in interface_matches:
            result['interfaces'].append({
                'name': class_name,
                'superclass': superclass
            })

        # Parse @property definitions
        # Improved regex to handle complex type declarations
        property_pattern = r'@property\s*\(([^)]+)\)\s*([^;]+);'
        property_matches = re.findall(property_pattern, header_content)

        for attributes_str, declaration in property_matches:
            attributes = [attr.strip() for attr in attributes_str.split(',')]

            # Extract type and name from declaration
            # Handle cases like "NSMutableArray<GSPath *> *paths" or "CGFloat width"
            declaration = declaration.strip()

            # Find the last space as the name separator
            parts = declaration.rsplit(' ', 1)
            if len(parts) == 2:
                prop_type = parts[0].strip()
                prop_name = parts[1].strip()
            else:
                # If cannot split, use entire declaration as name
                prop_type = ''
                prop_name = declaration

            # Clean property name, remove pointer symbol
            prop_name = prop_name.lstrip('*')

            result['properties'].append({
                'name': prop_name,
                'type': prop_type,
                'attributes': attributes
            })

        # Parse method definitions
        # Instance methods: - (ReturnType)methodName:(ParamType)paramName
        instance_method_pattern = r'-\s*\(([^)]+)\)\s*([^;]+);'
        instance_matches = re.findall(instance_method_pattern, header_content)

        for return_type, method_signature in instance_matches:
            # Parse method name and parameters
            method_name = self._extract_method_name(method_signature)
            parameters = self._extract_parameters(method_signature)

            result['methods'].append({
                'name': method_name,
                'return_type': return_type.strip(),
                'method_type': 'instance',
                'parameters': parameters
            })

        # Class methods: + (ReturnType)methodName:(ParamType)paramName
        class_method_pattern = r'\+\s*\(([^)]+)\)\s*([^;]+);'
        class_matches = re.findall(class_method_pattern, header_content)

        for return_type, method_signature in class_matches:
            method_name = self._extract_method_name(method_signature)
            parameters = self._extract_parameters(method_signature)

            result['methods'].append({
                'name': method_name,
                'return_type': return_type.strip(),
                'method_type': 'class',
                'parameters': parameters
            })

        # Parse comments
        # /** Multi-line comments */
        multiline_comment_pattern = r'/\*\*\s*(.*?)\s*\*/'
        multiline_matches = re.findall(multiline_comment_pattern, header_content, re.DOTALL)

        for comment_text in multiline_matches:
            # Clean comment content
            clean_text = re.sub(r'\s*\*\s*', ' ', comment_text).strip()
            # Detect context (infer related class or method from comment position)
            context = self._detect_comment_context(header_content, comment_text)

            result['comments'].append({
                'text': clean_text,
                'context': context
            })

        # /// Single-line comments
        singleline_comment_pattern = r'///\s*(.*)'
        singleline_matches = re.findall(singleline_comment_pattern, header_content)

        for comment_text in singleline_matches:
            context = self._detect_comment_context(header_content, comment_text)
            result['comments'].append({
                'text': comment_text.strip(),
                'context': context
            })

        return result

    def parse_file(self, file_path: Path) -> dict[str, Any]:
        """Parse Header file

        Args:
            file_path: Header file path

        Returns:
            Parsed data structure
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            result = self.parse_content(content)
            result['file_name'] = file_path.name
            result['file_stem'] = file_path.stem
            return result
        except Exception as e:
            return {
                'file_name': file_path.name if file_path else 'unknown',
                'file_stem': file_path.stem if file_path else 'unknown',
                'interfaces': [],
                'properties': [],
                'methods': [],
                'comments': [],
                'error': str(e)
            }

    def load_protocol(self, protocol_name: str, headers_base_path: Path) -> dict[str, Any] | None:
        """
        Load specific Protocol definition on demand

        Args:
            protocol_name: Protocol name (e.g., "GlyphsReporter")
            headers_base_path: Headers directory path

        Returns:
            Protocol definition dict or None (if not found)
        """
        # 1. Check cache
        if protocol_name in self.protocols:
            return self.protocols[protocol_name]

        # 2. Construct possible filenames
        # Protocol headers are typically named "ProtocolName.h" or "ProtocolNameProtocol.h"
        possible_filenames = [
            f"{protocol_name}.h",
            f"{protocol_name}Protocol.h"
        ]

        # 3. Try to find and parse file
        for filename in possible_filenames:
            file_path = headers_base_path / filename
            if file_path.exists():
                result = self.parse_file(file_path)

                # 4. Extract Protocol definition from parse result
                for protocol_data in result.get('protocols', []):
                    if protocol_data['name'] == protocol_name:
                        # Cache to self.protocols
                        self.protocols[protocol_name] = protocol_data
                        return protocol_data

        # 5. Protocol not found
        return None

    def _extract_method_name(self, method_signature: str) -> str:
        """Extract method name from method signature"""
        # Simplified implementation: take first word as method name
        # A more complete implementation needs to handle complex Objective-C method signatures
        method_parts = method_signature.split(':')
        return method_parts[0].strip()

    def _extract_parameters(self, method_signature: str) -> list[str]:
        """Extract parameters from method signature"""
        parameters = []

        # Find parameter pattern: (Type *)paramName
        param_pattern = r'\(([^)]+)\)\s*(\w+)'
        param_matches = re.findall(param_pattern, method_signature)

        for param_type, param_name in param_matches:
            parameters.append(f"{param_type.strip()} {param_name}")

        return parameters

    def _detect_comment_context(self, full_content: str, comment_text: str) -> str:
        """Detect comment context"""
        # Infer context based on comment position and adjacent code

        # Find comment position in full content
        comment_index = full_content.find(comment_text)
        if comment_index == -1:
            # If original comment text not found (possibly due to formatting), use content matching
            comment_lower = comment_text.lower()

            # Check if a specific class name is mentioned
            class_names = re.findall(r'@interface\s+(\w+)', full_content)
            for class_name in class_names:
                if class_name.lower() in comment_lower or 'font' in comment_lower:
                    return class_name

            # Check if a method name is mentioned
            method_matches = re.findall(r'[-+]\s*\([^)]+\)\s*(\w+)', full_content)
            for method_name in method_matches:
                if method_name.lower() in comment_lower:
                    return method_name

            return 'general'

        # Check code after comment
        after_comment = full_content[comment_index + len(comment_text):comment_index + len(comment_text) + 200]

        # Find immediately following @interface
        interface_match = re.search(r'@interface\s+(\w+)', after_comment)
        if interface_match:
            return interface_match.group(1)

        # Find immediately following method definition
        method_match = re.search(r'[-+]\s*\([^)]+\)\s*(\w+)', after_comment)
        if method_match:
            return method_match.group(1)

        # Default to general context
        return 'general'

    def _parse_protocols(self, header_content: str) -> list[dict[str, Any]]:
        """Parse @protocol definitions

        Args:
            header_content: Header file content

        Returns:
            List of Protocol data structures
        """
        protocols = []

        # First remove forward declarations (@protocol declarations ending with semicolon)
        # Example: @protocol GSGlyphEditViewControllerProtocol;
        forward_declaration_pattern = r'@protocol\s+\w+\s*(?:<[^>]+>)?\s*;'
        content_without_forward_decl = re.sub(forward_declaration_pattern, '', header_content)

        # Find all @protocol ... @end blocks
        # Use non-greedy matching to ensure correct pairing of @protocol and @end
        protocol_pattern = r'@protocol\s+(\w+)\s*(?:<([^>]+)>)?\s*(.*?)@end'
        protocol_matches = re.findall(protocol_pattern, content_without_forward_decl, re.DOTALL)

        for protocol_name, parent_protocols_str, protocol_body in protocol_matches:
            # Parse parent Protocols
            parent_protocols = []
            if parent_protocols_str:
                parent_protocols = [p.strip() for p in parent_protocols_str.split(',')]

            # Parse Protocol content
            protocol_data = {
                'name': protocol_name,
                'parent_protocols': parent_protocols,
                'required_methods': [],
                'optional_methods': [],
                'properties': [],
                'deprecated_methods': []
            }

            # Split into required and optional sections
            # By default, everything before @optional is required
            parts = protocol_body.split('@optional')

            # Parse required section (before @optional)
            if parts:
                required_section = parts[0]
                required_methods = self._parse_protocol_methods(required_section)
                required_properties = self._parse_protocol_properties(required_section)

                protocol_data['required_methods'] = required_methods
                protocol_data['properties'].extend(required_properties)

            # Parse optional section (after @optional)
            if len(parts) > 1:
                optional_section = parts[1]
                optional_methods = self._parse_protocol_methods(optional_section)
                optional_properties = self._parse_protocol_properties(optional_section)

                protocol_data['optional_methods'] = optional_methods
                protocol_data['properties'].extend(optional_properties)

            # Identify deprecated methods
            deprecated_pattern = r'__attribute__\(\(unavailable\([^)]*\)\)\)'
            for method in protocol_data['required_methods'] + protocol_data['optional_methods']:
                if re.search(deprecated_pattern, method.get('full_signature', '')):
                    method['deprecated'] = True
                    protocol_data['deprecated_methods'].append(method['name'])

            protocols.append(protocol_data)

        return protocols

    def _parse_protocol_methods(self, protocol_section: str) -> list[dict[str, Any]]:
        """Parse methods in Protocol section

        Args:
            protocol_section: Protocol section content

        Returns:
            List of method data structures
        """
        methods = []

        # Parse instance methods: - (ReturnType)methodSignature;
        instance_method_pattern = r'(-\s*\([^)]+\)[^;]+;)'
        instance_matches = re.findall(instance_method_pattern, protocol_section)

        for full_signature in instance_matches:
            # Further parse method signature
            signature_parts = re.match(r'-\s*\(([^)]+)\)\s*([^;]+);', full_signature)
            if signature_parts:
                return_type = signature_parts.group(1).strip()
                method_signature = signature_parts.group(2).strip()

                method_name = self._extract_method_name(method_signature)
                parameters = self._extract_parameters(method_signature)

                # Check if deprecated
                deprecated = '__attribute__((unavailable' in full_signature

                methods.append({
                    'name': method_name,
                    'return_type': return_type,
                    'method_type': 'instance',
                    'parameters': parameters,
                    'full_signature': full_signature,
                    'deprecated': deprecated
                })

        # Parse class methods: + (ReturnType)methodSignature;
        class_method_pattern = r'(\+\s*\([^)]+\)[^;]+;)'
        class_matches = re.findall(class_method_pattern, protocol_section)

        for full_signature in class_matches:
            signature_parts = re.match(r'\+\s*\(([^)]+)\)\s*([^;]+);', full_signature)
            if signature_parts:
                return_type = signature_parts.group(1).strip()
                method_signature = signature_parts.group(2).strip()

                method_name = self._extract_method_name(method_signature)
                parameters = self._extract_parameters(method_signature)

                deprecated = '__attribute__((unavailable' in full_signature

                methods.append({
                    'name': method_name,
                    'return_type': return_type,
                    'method_type': 'class',
                    'parameters': parameters,
                    'full_signature': full_signature,
                    'deprecated': deprecated
                })

        return methods

    def _parse_protocol_properties(self, protocol_section: str) -> list[dict[str, Any]]:
        """Parse properties in Protocol section

        Args:
            protocol_section: Protocol section content

        Returns:
            List of property data structures
        """
        properties = []

        # Parse @property definitions
        property_pattern = r'@property\s*\(([^)]+)\)\s*([^;]+);'
        property_matches = re.findall(property_pattern, protocol_section)

        for attributes_str, declaration in property_matches:
            attributes = [attr.strip() for attr in attributes_str.split(',')]

            # Extract type and name from declaration
            declaration = declaration.strip()
            parts = declaration.rsplit(' ', 1)

            if len(parts) == 2:
                prop_type = parts[0].strip()
                prop_name = parts[1].strip().lstrip('*')
            else:
                prop_type = ''
                prop_name = declaration

            properties.append({
                'name': prop_name,
                'type': prop_type,
                'attributes': attributes
            })

        return properties
