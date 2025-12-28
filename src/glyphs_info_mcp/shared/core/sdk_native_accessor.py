#!/usr/bin/env python3
"""
SDK Native Accessor - Simplified Version (Option B)

Only handles direct reading of Plugin Templates, not Python API.
Python API continues to use existing JSON data.
"""

# mypy: ignore-errors

import ast
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SDKNativeAccessor:
    """SDK Native Accessor - Focused on Plugin Templates.

    Only implements Plugin Template related functionality:
    1. Scan Python Templates/ directory
    2. Directly read template files
    3. Simple AST parsing
    4. Return complete source code

    Python API functionality is not implemented here (continues using JSON).
    """

    def __init__(self, sdk_root: Path):
        """Initialize SDK Native Accessor.

        Args:
            sdk_root: GlyphsSDK root directory path
        """
        self.sdk_root = Path(sdk_root)
        self.templates_path = self.sdk_root / "Python Templates"
        self.plugins_py_path = (
            self.sdk_root / "ObjectWrapper" / "GlyphsApp" / "plugins.py"
        )
        self.drawing_tools_py_path = (
            self.sdk_root / "ObjectWrapper" / "GlyphsApp" / "drawingTools.py"
        )

        # Add Xcode resource paths
        self.xcode_templates_path = self.sdk_root / "Xcode Templates"
        self.xcode_samples_path = self.sdk_root / "Xcode Samples"

        # Validate paths
        if not self.templates_path.exists():
            logger.warning(f"Python Templates not found: {self.templates_path}")
        if not self.plugins_py_path.exists():
            logger.warning(f"plugins.py not found: {self.plugins_py_path}")
        if not self.drawing_tools_py_path.exists():
            logger.warning(f"drawingTools.py not found: {self.drawing_tools_py_path}")
        if not self.xcode_templates_path.exists():
            logger.warning(f"Xcode Templates not found: {self.xcode_templates_path}")
        if not self.xcode_samples_path.exists():
            logger.warning(f"Xcode Samples not found: {self.xcode_samples_path}")

        # Cache
        self._plugin_templates_cache: list[dict[str, Any]] | None = None
        self._plugin_classes_cache: list[dict[str, Any]] | None = None
        self._drawing_tools_cache: list[dict[str, Any]] | None = None
        self._xcode_templates_cache: list[dict[str, Any]] | None = None
        self._xcode_samples_cache: list[dict[str, Any]] | None = None

    # ============================================================================
    # Plugin Template Access Methods
    # ============================================================================

    def list_plugin_templates(self) -> list[dict[str, Any]]:
        """List all plugin templates.

        Scans Python Templates/ directory, returns all template info.
        Structure: Python Templates/{Type}/____PluginName____.glyphs{Type}/Contents/Resources/plugin.py

        Returns:
            Template info list, each containing:
            - name: Template name (identifier)
            - path: File path
            - source: Complete source code
            - type: Plugin type
            - base_class: Base class
            - doc: Docstring
            - subtype: Subtype (dialog/vanilla, etc.)
        """
        # Return cached results
        if self._plugin_templates_cache is not None:
            return self._plugin_templates_cache

        if not self.templates_path.exists():
            logger.warning("Templates path not found, returning empty list")
            return []

        templates = []

        # Scan all plugin.py files
        for plugin_py in self.templates_path.glob("**/plugin.py"):
            # Filter out unrelated directories
            if "_Readme_Images" in str(plugin_py) or "PluginMaker" in str(plugin_py):
                continue

            try:
                template_info = self._parse_template_file(plugin_py)
                templates.append(template_info)
            except Exception as e:
                logger.error(f"Error parsing template {plugin_py}: {e}")
                continue

        # Cache results
        self._plugin_templates_cache = templates
        logger.info(f"Loaded {len(templates)} plugin templates")

        return templates

    def _parse_template_file(self, file_path: Path) -> dict[str, Any]:
        """Parse a single template file.

        Structure: Python Templates/{Type}/{SubType}/____PluginName____.glyphs{Type}/Contents/Resources/plugin.py

        Args:
            file_path: Template file path (plugin.py)

        Returns:
            Template info dict
        """
        # Read complete source code
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        # Infer type and subtype from path
        # Example: .../Python Templates/Filter/dialog with xib/____PluginName____.glyphsFilter/Contents/Resources/plugin.py
        parts = file_path.parts

        # Find Python Templates position
        try:
            templates_idx = parts.index("Python Templates")
            plugin_type = parts[templates_idx + 1]  # Filter, Reporter, etc.
            subtype = parts[templates_idx + 2] if len(parts) > templates_idx + 2 else ""
        except (ValueError, IndexError):
            plugin_type = "Unknown"
            subtype = ""

        # Build unique identifier name
        # Format: {Type}_{Subtype} (e.g., Filter_dialog_with_xib)
        clean_subtype = subtype.replace(" ", "_").replace("/", "_")
        if clean_subtype:
            template_name = f"{plugin_type}_{clean_subtype}"
        else:
            template_name = plugin_type

        # Simple AST parsing (only extract basic info)
        try:
            tree = ast.parse(source)

            # Find first class definition
            main_class = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    main_class = node
                    break

            # Extract basic info
            if main_class:
                base_class = self._extract_base_class(main_class)
                doc = ast.get_docstring(main_class) or ""
            else:
                base_class = ""
                doc = ""

        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            base_class = ""
            doc = ""

        return {
            "name": template_name,
            "path": str(file_path),
            "source": source,  # Complete source code (most important!)
            "type": plugin_type,
            "subtype": subtype,
            "base_class": base_class,
            "doc": doc,
        }

    def _infer_plugin_type(self, path_or_name: str) -> str:
        """Infer plugin type from path or name (deprecated, use path analysis).

        Args:
            path_or_name: Path or name

        Returns:
            Plugin type string
        """
        name_lower = path_or_name.lower()

        if "filter" in name_lower:
            return "Filter"
        elif "reporter" in name_lower:
            return "Reporter"
        elif "tool" in name_lower:
            return "Tool"
        elif "palette" in name_lower:
            return "Palette"
        elif "fileformat" in name_lower or "file" in name_lower:
            return "FileFormat"
        elif "general" in name_lower:
            return "General"
        else:
            return "Unknown"

    def _extract_base_class(self, class_node: ast.ClassDef) -> str:
        """Extract base class name.

        Args:
            class_node: Class AST node

        Returns:
            Base class name string
        """
        if not class_node.bases:
            return ""

        # Get first base class
        base = class_node.bases[0]

        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        else:
            return ""

    def get_plugin_template(self, template_name: str) -> dict[str, Any] | None:
        """Get specific plugin template.

        Args:
            template_name: Template name (without .py extension)

        Returns:
            Template info dict or None
        """
        templates = self.list_plugin_templates()
        return next((t for t in templates if t["name"] == template_name), None)

    def search_templates(self, query: str) -> list[dict[str, Any]]:
        """Search templates.

        Search in template names and documentation.

        Args:
            query: Search keyword

        Returns:
            List of matching templates
        """
        query_lower = query.lower()
        templates = self.list_plugin_templates()

        results = []
        for template in templates:
            # Search name
            if query_lower in template["name"].lower():
                results.append({**template, "score": 1.0})  # Name match
                continue

            # Search documentation
            if query_lower in template.get("doc", "").lower():
                results.append({**template, "score": 0.5})  # Doc match
                continue

            # Search type
            if query_lower in template.get("type", "").lower():
                results.append({**template, "score": 0.3})  # Type match

        # Sort by score
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results

    # ============================================================================
    # Plugin API Access Methods (parsed from plugins.py)
    # ============================================================================

    def list_plugin_classes(self) -> list[dict[str, Any]]:
        """List all plugin base classes.

        Parse all plugin classes from plugins.py:
        - FileFormatPlugin
        - FilterWithDialog
        - FilterWithoutDialog
        - GeneralPlugin
        - PalettePlugin
        - ReporterPlugin
        - SelectTool

        Returns:
            Plugin class info list
        """
        # Return cached results
        if self._plugin_classes_cache is not None:
            return self._plugin_classes_cache

        if not self.plugins_py_path.exists():
            logger.warning("plugins.py not found, returning empty list")
            return []

        try:
            # Read complete file
            with open(self.plugins_py_path, encoding="utf-8") as f:
                source = f.read()

            # AST parsing
            tree = ast.parse(source)

            plugin_classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Only process known plugin classes
                    if node.name in [
                        "FileFormatPlugin",
                        "FilterWithDialog",
                        "FilterWithoutDialog",
                        "GeneralPlugin",
                        "PalettePlugin",
                        "ReporterPlugin",
                        "SelectTool",
                    ]:
                        class_info = self._parse_plugin_class(node, source)
                        plugin_classes.append(class_info)

            self._plugin_classes_cache = plugin_classes
            logger.info(f"Loaded {len(plugin_classes)} plugin classes from plugins.py")

            return plugin_classes

        except Exception as e:
            logger.error(f"Error parsing plugins.py: {e}")
            return []

    def _parse_plugin_class(
        self, class_node: ast.ClassDef, source: str
    ) -> dict[str, Any]:
        """Parse a single plugin class.

        Args:
            class_node: Class AST node
            source: Complete source code

        Returns:
            Plugin class info
        """
        # Extract base class
        base_class = self._extract_base_class(class_node)

        # Extract class documentation
        doc = ast.get_docstring(class_node) or ""

        # Extract method info
        methods = {}
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._parse_method(item)
                methods[item.name] = method_info

        # Extract class source segment (for display)
        class_source = ast.get_source_segment(source, class_node)

        return {
            "name": class_node.name,
            "base_class": base_class,
            "doc": doc,
            "methods": methods,
            "source": class_source,  # Complete class source code
            "line_number": class_node.lineno,
        }

    def _parse_method(self, method_node: ast.FunctionDef) -> dict[str, Any]:
        """Parse method info.

        Args:
            method_node: Method AST node

        Returns:
            Method info dictionary
        """
        # Extract docstring
        doc = ast.get_docstring(method_node) or ""

        # Extract parameters
        parameters = []
        for arg in method_node.args.args:
            if arg.arg != "self":  # Skip self
                parameters.append(arg.arg)

        # Check for decorators (to determine if it's an Objective-C method)
        is_objc = any(
            isinstance(dec, ast.Name) and dec.id == "objc"
            for dec in method_node.decorator_list
        )

        return {
            "name": method_node.name,
            "doc": doc,
            "parameters": parameters,
            "is_objc": is_objc,
            "line_number": method_node.lineno,
        }

    def get_plugin_class(self, class_name: str) -> dict[str, Any] | None:
        """Get specific plugin class info.

        Args:
            class_name: Class name

        Returns:
            Plugin class info or None
        """
        classes = self.list_plugin_classes()
        return next((c for c in classes if c["name"] == class_name), None)

    def search_plugin_classes(self, query: str) -> list[dict[str, Any]]:
        """Search plugin classes.

        Args:
            query: Search keyword

        Returns:
            List of matching plugin classes
        """
        query_lower = query.lower()
        classes = self.list_plugin_classes()

        results = []
        for plugin_class in classes:
            # Search class name
            if query_lower in plugin_class["name"].lower():
                results.append({**plugin_class, "score": 1.0, "match_type": "name"})
                continue

            # Search documentation
            if query_lower in plugin_class.get("doc", "").lower():
                results.append({**plugin_class, "score": 0.8, "match_type": "doc"})
                continue

            # Search method names
            matching_methods = []
            for method_name in plugin_class.get("methods", {}).keys():
                if query_lower in method_name.lower():
                    matching_methods.append(method_name)

            if matching_methods:
                results.append(
                    {
                        **plugin_class,
                        "score": 0.6,
                        "match_type": "methods",
                        "matching_methods": matching_methods,
                    }
                )

        # Sort by score
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results

    # ============================================================================
    # Drawing Tools API Access Methods (parsed from drawingTools.py)
    # ============================================================================

    def list_drawing_functions(self) -> list[dict[str, Any]]:
        """List all drawing functions.

        Parse all module-level functions from drawingTools.py

        Returns:
            Drawing function info list
        """
        # Return cached results
        if self._drawing_tools_cache is not None:
            return self._drawing_tools_cache

        if not self.drawing_tools_py_path.exists():
            logger.warning("drawingTools.py not found, returning empty list")
            return []

        try:
            # Read complete file
            with open(self.drawing_tools_py_path, encoding="utf-8") as f:
                source = f.read()

            # AST parsing
            tree = ast.parse(source)

            functions = []
            for node in ast.walk(tree):
                # Only process module-level functions (not methods inside classes)
                if isinstance(node, ast.FunctionDef):
                    # Ensure it's a top-level function
                    if isinstance(node, ast.FunctionDef):
                        func_info = self._parse_drawing_function(node)
                        functions.append(func_info)

            self._drawing_tools_cache = functions
            logger.info(
                f"Loaded {len(functions)} drawing functions from drawingTools.py"
            )

            return functions

        except Exception as e:
            logger.error(f"Error parsing drawingTools.py: {e}")
            return []

    def _parse_drawing_function(self, func_node: ast.FunctionDef) -> dict[str, Any]:
        """Parse drawing function.

        Args:
            func_node: Function AST node

        Returns:
            Function info dictionary
        """
        # Extract docstring
        doc = ast.get_docstring(func_node) or ""

        # Extract parameters
        parameters = []
        defaults = {}

        # Process parameters and default values
        args_list = func_node.args.args
        defaults_list = func_node.args.defaults

        # Calculate starting position of parameters with default values
        num_defaults = len(defaults_list)
        num_args = len(args_list)
        defaults_start = num_args - num_defaults

        for i, arg in enumerate(args_list):
            param_name = arg.arg
            parameters.append(param_name)

            # Check if it has a default value
            if i >= defaults_start:
                default_idx = i - defaults_start
                default_node = defaults_list[default_idx]
                defaults[param_name] = ast.unparse(default_node)

        return {
            "name": func_node.name,
            "doc": doc,
            "parameters": parameters,
            "defaults": defaults,
            "line_number": func_node.lineno,
        }

    def get_drawing_function(self, function_name: str) -> dict[str, Any] | None:
        """Get specific drawing function info.

        Args:
            function_name: Function name

        Returns:
            Function info or None
        """
        functions = self.list_drawing_functions()
        return next((f for f in functions if f["name"] == function_name), None)

    def search_drawing_functions(self, query: str) -> list[dict[str, Any]]:
        """Search drawing functions.

        Args:
            query: Search keyword

        Returns:
            List of matching functions
        """
        query_lower = query.lower()
        functions = self.list_drawing_functions()

        results = []
        for func in functions:
            # Search function name
            if query_lower in func["name"].lower():
                results.append({**func, "score": 1.0, "match_type": "name"})
                continue

            # Search documentation
            if query_lower in func.get("doc", "").lower():
                results.append({**func, "score": 0.7, "match_type": "doc"})

        # Sort by score
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results

    def get_drawing_tools_source(self) -> str:
        """Get complete drawingTools.py source code.

        Returns:
            Complete source code string
        """
        if not self.drawing_tools_py_path.exists():
            return ""

        with open(self.drawing_tools_py_path, encoding="utf-8") as f:
            return f.read()

    # ============================================================================
    # Python API Related (not implemented)
    # ============================================================================

    def get_python_api_module(self):
        """Python API does not use this Accessor.

        Python API continues to use existing JSON data.

        Raises:
            NotImplementedError: Always raises this exception
        """
        raise NotImplementedError(
            "Python API uses existing JSON data. "
            "SDKNativeAccessor is only for Plugin Templates."
        )

    def get_python_class_info(self, class_name: str):
        """Python API does not use this Accessor."""
        raise NotImplementedError(
            "Use PythonAPIManager with JSON data for Python API queries."
        )

    def search_python_api(self, query: str):
        """Python API does not use this Accessor."""
        raise NotImplementedError(
            "Use PythonAPIManager with JSON data for Python API search."
        )

    # ============================================================================
    # Xcode Templates Access Methods
    # ============================================================================

    def list_xcode_templates(self) -> list[dict[str, Any]]:
        """List all Xcode plugin templates.

        Scans Xcode Templates/Glyphs Dev/ directory, returns all template info.

        Returns:
            Template info list, each containing:
            - name: Template name
            - type: Template type (Reporter, Filter, Tool, etc.)
            - path: Template directory path
            - files: List of included files
            - description: Template description
        """
        # Return cached results
        if self._xcode_templates_cache is not None:
            return self._xcode_templates_cache

        if not self.xcode_templates_path.exists():
            logger.warning("Xcode Templates path not found, returning empty list")
            return []

        templates = []
        glyphs_dev_path = self.xcode_templates_path / "Glyphs Dev"

        if not glyphs_dev_path.exists():
            logger.warning(f"Glyphs Dev path not found: {glyphs_dev_path}")
            return []

        # Scan all .xctemplate directories
        for template_dir in glyphs_dev_path.glob("*.xctemplate"):
            try:
                template_info = self._parse_xcode_template(template_dir)
                templates.append(template_info)
            except Exception as e:
                logger.error(f"Error parsing Xcode template {template_dir}: {e}")
                continue

        # Cache results
        self._xcode_templates_cache = templates
        logger.info(f"Loaded {len(templates)} Xcode templates")

        return templates

    def _parse_xcode_template(self, template_dir: Path) -> dict[str, Any]:
        """Parse a single Xcode template.

        Args:
            template_dir: Template directory path (.xctemplate)

        Returns:
            Template info dictionary
        """
        # Template name (remove .xctemplate suffix)
        template_name = template_dir.name.replace(".xctemplate", "")

        # Infer template type
        template_type = self._infer_xcode_template_type(template_name)

        # Collect file list
        files = []
        for file_path in template_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                relative_path = file_path.relative_to(template_dir)
                files.append(
                    {
                        "name": file_path.name,
                        "path": str(relative_path),
                        "type": file_path.suffix,
                    }
                )

        # Try to read TemplateInfo.plist for description
        description = ""
        plist_path = template_dir / "TemplateInfo.plist"
        if plist_path.exists():
            try:
                with open(plist_path, encoding="utf-8") as f:
                    plist_content = f.read()
                    # Simple extraction of Description (without using plistlib to avoid dependency)
                    if "<key>Description</key>" in plist_content:
                        start = plist_content.find(
                            "<string>", plist_content.find("<key>Description</key>")
                        )
                        end = plist_content.find("</string>", start)
                        if start != -1 and end != -1:
                            description = plist_content[start + 8 : end].strip()
            except Exception as e:
                logger.debug(f"Could not parse TemplateInfo.plist: {e}")

        return {
            "name": template_name,
            "type": template_type,
            "path": str(template_dir),
            "files": files,
            "file_count": len(files),
            "description": description,
        }

    def _infer_xcode_template_type(self, template_name: str) -> str:
        """Infer type from template name.

        Args:
            template_name: Template name

        Returns:
            Template type
        """
        name_lower = template_name.lower()

        if "reporter" in name_lower:
            return "Reporter"
        elif "filter" in name_lower:
            return "Filter"
        elif "tool" in name_lower:
            return "Tool"
        elif "palette" in name_lower:
            return "Palette"
        elif "file format" in name_lower or "fileformat" in name_lower:
            return "File Format"
        elif "base" in name_lower:
            return "Base"
        else:
            return "Plugin"

    def get_xcode_template(self, template_name: str) -> dict[str, Any] | None:
        """Get complete content of a specific Xcode template.

        Args:
            template_name: Template name

        Returns:
            Template info including complete source code, or None
        """
        templates = self.list_xcode_templates()
        template = next((t for t in templates if t["name"] == template_name), None)

        if not template:
            return None

        # Load all source code file contents
        template_path = Path(template["path"])
        source_files = {}

        for file_info in template["files"]:
            file_path = template_path / file_info["path"]
            if file_path.suffix in [".h", ".m", ".plist", ".strings"]:
                try:
                    with open(file_path, encoding="utf-8") as f:
                        source_files[file_info["path"]] = f.read()
                except Exception as e:
                    logger.error(f"Error reading {file_path}: {e}")
                    source_files[file_info["path"]] = f"<Error reading file: {e}>"

        return {
            **template,
            "source_files": source_files,
        }

    def search_xcode_templates(self, query: str) -> list[dict[str, Any]]:
        """Search Xcode templates.

        Args:
            query: Search keyword

        Returns:
            List of matching templates
        """
        query_lower = query.lower()
        templates = self.list_xcode_templates()

        results = []
        for template in templates:
            # Search name
            if query_lower in template["name"].lower():
                results.append({**template, "score": 1.0})
                continue

            # Search type
            if query_lower in template["type"].lower():
                results.append({**template, "score": 0.8})
                continue

            # Search description
            if query_lower in template.get("description", "").lower():
                results.append({**template, "score": 0.6})

        # Sort by score
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results

    # ============================================================================
    # Xcode Samples Access Methods
    # ============================================================================

    def list_xcode_samples(self) -> list[dict[str, Any]]:
        """List all Xcode sample projects.

        Scans Xcode Samples/ directory, returns all sample project info.

        Returns:
            Sample project info list, each containing:
            - name: Sample name
            - path: Project directory path
            - files: List of included files
            - readme: README content (if available)
            - has_xcode_project: Whether it contains .xcodeproj
        """
        # Return cached results
        if self._xcode_samples_cache is not None:
            return self._xcode_samples_cache

        if not self.xcode_samples_path.exists():
            logger.warning("Xcode Samples path not found, returning empty list")
            return []

        samples = []

        # Scan all sample project directories (one level subdirectory)
        for sample_dir in self.xcode_samples_path.iterdir():
            if sample_dir.is_dir() and not sample_dir.name.startswith("."):
                try:
                    sample_info = self._parse_xcode_sample(sample_dir)
                    samples.append(sample_info)
                except Exception as e:
                    logger.error(f"Error parsing Xcode sample {sample_dir}: {e}")
                    continue

        # Cache results
        self._xcode_samples_cache = samples
        logger.info(f"Loaded {len(samples)} Xcode samples")

        return samples

    def _parse_xcode_sample(self, sample_dir: Path) -> dict[str, Any]:
        """Parse a single Xcode sample project.

        Args:
            sample_dir: Sample project directory path

        Returns:
            Sample project info dictionary
        """
        sample_name = sample_dir.name

        # Check if .xcodeproj exists
        has_xcode_project = any(sample_dir.glob("*.xcodeproj"))

        # Try to read README
        readme_content = ""
        for readme_file in ["readme.md", "README.md", "Readme.md"]:
            readme_path = sample_dir / readme_file
            if readme_path.exists():
                try:
                    with open(readme_path, encoding="utf-8") as f:
                        readme_content = f.read()
                    break
                except Exception as e:
                    logger.debug(f"Could not read {readme_file}: {e}")

        # Collect main files (.h, .m)
        source_files = []
        for file_path in sample_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".h", ".m"]:
                relative_path = file_path.relative_to(sample_dir)
                source_files.append(
                    {
                        "name": file_path.name,
                        "path": str(relative_path),
                        "type": file_path.suffix,
                    }
                )

        return {
            "name": sample_name,
            "path": str(sample_dir),
            "has_xcode_project": has_xcode_project,
            "readme": readme_content,
            "source_files": source_files,
            "source_file_count": len(source_files),
        }

    def get_xcode_sample(self, sample_name: str) -> dict[str, Any] | None:
        """Get complete content of a specific Xcode sample.

        Args:
            sample_name: Sample name

        Returns:
            Sample info including complete source code, or None
        """
        samples = self.list_xcode_samples()
        sample = next((s for s in samples if s["name"] == sample_name), None)

        if not sample:
            return None

        # Load all source code file contents
        sample_path = Path(sample["path"])
        source_code = {}

        for file_info in sample["source_files"]:
            file_path = sample_path / file_info["path"]
            try:
                with open(file_path, encoding="utf-8") as f:
                    source_code[file_info["path"]] = f.read()
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
                source_code[file_info["path"]] = f"<Error reading file: {e}>"

        return {
            **sample,
            "source_code": source_code,
        }

    def search_xcode_samples(self, query: str) -> list[dict[str, Any]]:
        """Search Xcode sample projects.

        Args:
            query: Search keyword

        Returns:
            List of matching samples
        """
        query_lower = query.lower()
        samples = self.list_xcode_samples()

        results = []
        for sample in samples:
            # Search name
            if query_lower in sample["name"].lower():
                results.append({**sample, "score": 1.0})
                continue

            # Search README content
            if query_lower in sample.get("readme", "").lower():
                results.append({**sample, "score": 0.7})

        # Sort by score
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results
