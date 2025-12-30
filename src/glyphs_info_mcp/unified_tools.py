#!/usr/bin/env python3
"""
Unified Tool Entry Points

Issue #19: Consolidate 60 tools into 8 unified entry points
to reduce context token cost by ~85%.

This module provides a facade layer that routes requests to
the underlying module implementations.
"""

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class UnifiedToolsRouter:
    """Routes unified tool calls to underlying module implementations.

    Consolidates 60 individual tools into 8 unified entry points:
    - handbook: 8 tools -> 1 entry point
    - vocabulary: 4 tools -> 1 entry point
    - api: 16 tools -> 1 entry point
    - plugins: 5 tools -> 1 entry point
    - scripts: 4 tools -> 1 entry point
    - sdk: 6 tools -> 1 entry point
    - news: 6 tools -> 1 entry point
    - lighttable: 4 tools -> 1 entry point
    """

    def __init__(self) -> None:
        # Use Any type for modules since we call methods dynamically
        self._modules: dict[str, Any] = {}

    def set_module(self, name: str, module: Any) -> None:
        """Register a module for routing.

        Args:
            name: Module name (e.g., 'handbook', 'vocabulary')
            module: Module instance (BaseMCPModule subclass)
        """
        self._modules[name] = module

    def get_tools(self) -> dict[str, Callable[..., Any]]:
        """Get all unified tool entry points.

        Returns:
            Dictionary of tool_name -> callable
        """
        return {
            "handbook": self.handbook,
            "vocabulary": self.vocabulary,
            "api": self.api,
            "plugins": self.plugins,
            "scripts": self.scripts,
            "sdk": self.sdk,
            "news": self.news,
            "lighttable": self.lighttable,
        }

    # ========== Handbook Entry Point ==========

    def handbook(
        self,
        action: str,
        query: str = "",
        filename: str = "",
        chapter: str = "",
        name: str = "",
        search_scope: str = "all",
        max_results: int = 5,
        force: bool = False,
        operation: str = "info",
    ) -> str:
        """
        [HANDBOOK] Glyphs Handbook operations

        Actions:
        - search: Search handbook content (query, search_scope, max_results)
        - get: Get chapter content (filename)
        - toc: Get table of contents (chapter)
        - children: Get chapter children (chapter)
        - parameter: Get custom parameter details (name)
        - list_parameters: List all custom parameters
        - cache: Cache management (operation: info|update, force)

        Args:
            action: Operation to perform
            query: Search keywords (for search action)
            filename: Chapter filename (for get action)
            chapter: Chapter name (for toc/children action)
            name: Parameter name (for parameter action)
            search_scope: Search scope - titles, content, all (default: all)
            max_results: Maximum results (default: 5)
            force: Force cache update (for cache action)
            operation: Cache operation - info or update (default: info)

        Examples:
            handbook(action="search", query="interpolation")
            handbook(action="get", filename="anchors.md")
            handbook(action="toc", chapter="Interpolation")
            handbook(action="parameter", name="ascender")
        """
        module = self._modules.get("handbook")
        if not module:
            return "## Error\n\nHandbook module not initialized or not available."

        try:
            if action == "search":
                return module.handbook_search(
                    query=query,
                    search_scope=search_scope,
                    max_results=max_results,
                )
            elif action == "get":
                return module.handbook_fetch(filename=filename)
            elif action == "toc":
                return module.get_toc(chapter=chapter)
            elif action == "children":
                return module.get_chapter_children(chapter_title=chapter)
            elif action == "parameter":
                return module.fetch_custom_parameter(parameter_name=name)
            elif action == "list_parameters":
                return module.get_custom_parameters_list()
            elif action == "cache":
                if operation == "update":
                    # Note: This is async in the original, but we handle it synchronously
                    import asyncio
                    return asyncio.get_event_loop().run_until_complete(
                        module.update_cache(force=force)
                    )
                else:
                    import asyncio
                    return asyncio.get_event_loop().run_until_complete(
                        module.get_cache_info()
                    )
            else:
                return f"## Invalid Action\n\nUnknown action: `{action}`\n\nAvailable actions: search, get, toc, children, parameter, list_parameters, cache"

        except Exception as e:
            logger.error(f"Handbook action '{action}' failed: {e}")
            return f"## Error\n\nFailed to execute action '{action}': {str(e)}"

    # ========== Vocabulary Entry Point ==========

    def vocabulary(
        self,
        action: str,
        term: str = "",
        target: str = "auto",
        locale: str = "zh-Hant",
        source_locale: str = "en",
        target_locales: str = "zh-Hant",
    ) -> str:
        """
        [VOCABULARY] Glyphs UI terminology translation

        Actions:
        - translate: Translate UI term (term, target)
        - search: Search UI terms (term, locale)
        - mapping: Get multi-locale translations (term, source_locale, target_locales)
        - categories: List vocabulary file categories

        Args:
            action: Operation to perform
            term: Term to translate or search
            target: Target locale for translation (default: auto -> English)
            locale: Search locale (default: zh-Hant)
            source_locale: Source locale for mapping (default: en)
            target_locales: Comma-separated target locales (default: zh-Hant)

        Examples:
            vocabulary(action="translate", term="取消")
            vocabulary(action="search", term="Cancel", locale="zh-Hant")
            vocabulary(action="mapping", term="Cancel", target_locales="zh-Hant,ja,ko")
        """
        module = self._modules.get("vocabulary")
        if not module:
            return "## Error\n\nVocabulary module not initialized or not available."

        try:
            if action == "translate":
                return module.translate_term_tool(term=term, target_locale=target)
            elif action == "search":
                return module.search_ui_term(term=term, locale=locale)
            elif action == "mapping":
                return module.get_ui_translation(
                    term=term,
                    source_locale=source_locale,
                    target_locales=target_locales,
                )
            elif action == "categories":
                return module.list_ui_categories()
            else:
                return f"## Invalid Action\n\nUnknown action: `{action}`\n\nAvailable actions: translate, search, mapping, categories"

        except Exception as e:
            logger.error(f"Vocabulary action '{action}' failed: {e}")
            return f"## Error\n\nFailed to execute action '{action}': {str(e)}"

    # ========== API Entry Point ==========

    def api(
        self,
        action: str,
        query: str = "",
        class_name: str = "",
        member_name: str = "",
        member_type: str = "property",
        scope: str = "auto",
        detail_level: str = "overview",
        header_query: str = "",
        protocol_name: str = "",
        objc_signature: str = "",
        python_name: str = "",
        method_name: str = "",
        plugin_type: str = "reporter",
        ui_item: str = "",
        start_class: str = "",
        relationship: str = "parent",
        depth: int = 1,
        format: str = "tree",
        max_results: int = 5,
        show_details: bool = False,
        show_deprecated: bool = True,
        show_optional_only: bool = False,
        include_source: bool = True,
        include_examples: bool = True,
        show_path: bool = True,
    ) -> str:
        """
        [API] Glyphs Python/Objective-C API reference

        Actions:
        - search_python: Search Python API (query, scope, max_results)
        - get_class: Get Python class info (class_name, detail_level)
        - get_member: Get class member info (class_name, member_name, member_type)
        - search_objc: Search Obj-C headers (query, max_results)
        - get_header: Get Obj-C header content (header_query)
        - list_protocols: List plugin protocols (show_details)
        - get_protocol: Get protocol methods (protocol_name, show_deprecated)
        - convert_objc: Convert Obj-C to Python name (objc_signature)
        - convert_python: Convert Python to Obj-C name (python_name)
        - identify_method: Identify method type (method_name, plugin_type)
        - get_template: Get method implementation template (method_name, plugin_type)
        - search_vanilla: Search Vanilla UI components (query, max_results)
        - get_vanilla: Get Vanilla UI component (ui_item, include_source)
        - list_vanilla: List all Vanilla UI components
        - hierarchy: Get class hierarchy (format)
        - relationships: Get class relationships (class_name, include_examples)
        - navigate: Navigate class structure (start_class, relationship, depth)

        Examples:
            api(action="search_python", query="GSLayer")
            api(action="get_class", class_name="GSFont", detail_level="detailed")
            api(action="get_protocol", protocol_name="GlyphsReporter")
        """
        module = self._modules.get("api")
        if not module:
            return "## Error\n\nAPI module not initialized or not available."

        try:
            if action == "search_python":
                return module.python_api_search(
                    query=query, scope=scope, max_results=max_results
                )
            elif action == "get_class":
                return module.python_api_class_info(
                    class_name=class_name, detail_level=detail_level
                )
            elif action == "get_member":
                return module.python_api_member_info(
                    class_name=class_name,
                    member_name=member_name,
                    member_type=member_type,
                )
            elif action == "search_objc":
                return module.search_objc_headers(query=query, max_results=max_results)
            elif action == "get_header":
                return module.get_objc_header(header_query=header_query)
            elif action == "list_protocols":
                return module.list_plugin_protocols(show_details=show_details)
            elif action == "get_protocol":
                return module.get_protocol_methods(
                    protocol_name=protocol_name,
                    show_deprecated=show_deprecated,
                    show_optional_only=show_optional_only,
                )
            elif action == "convert_objc":
                return module.convert_objc_to_python(objc_signature=objc_signature)
            elif action == "convert_python":
                return module.convert_python_to_objc(python_name=python_name)
            elif action == "identify_method":
                return module.identify_method_type(
                    method_name=method_name, plugin_type=plugin_type
                )
            elif action == "get_template":
                return module.get_method_template(
                    method_name=method_name, plugin_type=plugin_type
                )
            elif action == "search_vanilla":
                return module.search_vanilla_ui(query=query, max_results=max_results)
            elif action == "get_vanilla":
                return module.get_vanilla_ui(ui_item=ui_item, include_source=include_source)
            elif action == "list_vanilla":
                return module.list_vanilla_ui()
            elif action == "hierarchy":
                return module.api_get_class_hierarchy(format=format)
            elif action == "relationships":
                return module.api_get_class_relationships(
                    class_name=class_name, include_examples=include_examples
                )
            elif action == "navigate":
                return module.api_navigate_structure(
                    start_class=start_class,
                    relationship=relationship,
                    depth=depth,
                    show_path=show_path,
                )
            else:
                return f"## Invalid Action\n\nUnknown action: `{action}`\n\nAvailable actions: search_python, get_class, get_member, search_objc, get_header, list_protocols, get_protocol, convert_objc, convert_python, identify_method, get_template, search_vanilla, get_vanilla, list_vanilla, hierarchy, relationships, navigate"

        except Exception as e:
            logger.error(f"API action '{action}' failed: {e}")
            return f"## Error\n\nFailed to execute action '{action}': {str(e)}"

    # ========== Plugins Entry Point ==========

    def plugins(
        self,
        action: str,
        query: str = "",
        name: str = "",
        category: str = "all",
        source: str = "local",
        filter_by_author: str = "",
        include_files: bool = False,
        include_source: bool = False,
    ) -> str:
        """
        [PLUGINS] Glyphs plugins management

        Actions:
        - search_local: Search local plugins (query, category)
        - search_official: Search official registry (query, filter_by_author)
        - get_info: Get plugin details (name, source, include_files, include_source)
        - scan: Scan repositories directory
        - categories: List plugin categories

        Args:
            action: Operation to perform
            query: Search keywords
            name: Plugin name (for get_info)
            category: Category filter (default: all)
            source: Data source - local or official (default: local)
            filter_by_author: Filter by author name
            include_files: Include file list (default: False)
            include_source: Include source code (default: False)

        Examples:
            plugins(action="search_local", query="reporter")
            plugins(action="get_info", name="ShowAnchors", source="local")
        """
        module = self._modules.get("glyphs_plugins")
        if not module:
            return "## Error\n\nPlugins module not initialized or not available."

        try:
            if action == "search_local":
                return module._search_local_tool(query=query, category=category)
            elif action == "search_official":
                return module._search_official_tool(
                    query=query,
                    filter_by_author=filter_by_author if filter_by_author else None,
                )
            elif action == "get_info":
                return module._get_info_tool(
                    name=name,
                    source=source,
                    include_files=include_files,
                    include_source=include_source,
                )
            elif action == "scan":
                return module._scan_repository_tool()
            elif action == "categories":
                return module._list_categories_tool()
            else:
                return f"## Invalid Action\n\nUnknown action: `{action}`\n\nAvailable actions: search_local, search_official, get_info, scan, categories"

        except Exception as e:
            logger.error(f"Plugins action '{action}' failed: {e}")
            return f"## Error\n\nFailed to execute action '{action}': {str(e)}"

    # ========== Scripts Entry Point ==========

    def scripts(
        self,
        action: str,
        query: str = "",
        script_id: str = "",
        category: str = "",
        max_results: int = 10,
        include_source: bool = True,
    ) -> str:
        """
        [SCRIPTS] mekkablue Scripts collection

        Actions:
        - search: Search scripts (query, category, max_results)
        - get: Get script details (script_id, include_source)
        - categories: List script categories
        - list: List scripts in category (category)

        Args:
            action: Operation to perform
            query: Search keywords
            script_id: Script ID (format: category/filename)
            category: Category name
            max_results: Maximum results (default: 10)
            include_source: Include source code (default: True)

        Examples:
            scripts(action="search", query="anchor")
            scripts(action="get", script_id="Anchors/Anchor Mover")
            scripts(action="list", category="Interpolation")
        """
        module = self._modules.get("mekkablue_scripts")
        if not module:
            return "## Error\n\nScripts module not initialized or not available."

        try:
            if action == "search":
                return module._search_scripts_tool(
                    query=query,
                    category=category if category else None,
                    max_results=max_results,
                )
            elif action == "get":
                return module._get_script_tool(
                    script_id=script_id, include_source=include_source
                )
            elif action == "categories":
                return module._list_categories_tool()
            elif action == "list":
                return module._list_scripts_tool(category=category if category else None)
            else:
                return f"## Invalid Action\n\nUnknown action: `{action}`\n\nAvailable actions: search, get, categories, list"

        except Exception as e:
            logger.error(f"Scripts action '{action}' failed: {e}")
            return f"## Error\n\nFailed to execute action '{action}': {str(e)}"

    # ========== SDK Entry Point ==========

    def sdk(
        self,
        action: str,
        query: str = "",
        file_path: str = "",
        template_name: str = "",
        sample_name: str = "",
        max_results: int = 5,
    ) -> str:
        """
        [SDK] Glyphs SDK documentation and templates

        Actions:
        - search: Search SDK content (query, max_results)
        - get: Get SDK file content (file_path)
        - list_templates: List Xcode templates
        - get_template: Get Xcode template (template_name)
        - list_samples: List Xcode samples
        - get_sample: Get Xcode sample (sample_name)

        Args:
            action: Operation to perform
            query: Search keywords
            file_path: SDK file path
            template_name: Xcode template name
            sample_name: Xcode sample name
            max_results: Maximum results (default: 5)

        Examples:
            sdk(action="search", query="reporter plugin")
            sdk(action="get_template", template_name="Glyphs Reporter")
        """
        module = self._modules.get("glyphs_sdk")
        if not module:
            return "## Error\n\nSDK module not initialized or not available."

        try:
            if action == "search":
                return module._sdk_search_tool(query=query, max_results=max_results)
            elif action == "get":
                return module._fetch_sdk_content_tool(file_path=file_path)
            elif action == "list_templates":
                return module._list_xcode_templates_tool()
            elif action == "get_template":
                return module._get_xcode_template_tool(template_name=template_name)
            elif action == "list_samples":
                return module._list_xcode_samples_tool()
            elif action == "get_sample":
                return module._get_xcode_sample_tool(sample_name=sample_name)
            else:
                return f"## Invalid Action\n\nUnknown action: `{action}`\n\nAvailable actions: search, get, list_templates, get_template, list_samples, get_sample"

        except Exception as e:
            logger.error(f"SDK action '{action}' failed: {e}")
            return f"## Error\n\nFailed to execute action '{action}': {str(e)}"

    # ========== News Entry Point ==========

    async def news(
        self,
        action: str,
        query: str = "",
        url: str = "",
        topic: str = "all",
        collection: str = "all",
        post_number: int | None = None,
        start_position: int = 0,
    ) -> str:
        """
        [NEWS] Glyphs tutorials, forum, and news

        Actions:
        - search_forum: Search forum discussions (query)
        - search_tutorials: Search tutorials (query, topic, collection)
        - fetch_tutorial: Fetch tutorial content (url)
        - fetch_forum: Fetch forum post (url, post_number, start_position)
        - search_posts: Search news posts (query)
        - fetch_content: Fetch news content (url)

        Args:
            action: Operation to perform
            query: Search keywords
            url: Content URL
            topic: Tutorial topic filter (default: all)
            collection: Tutorial collection filter (default: all)
            post_number: Specific post number
            start_position: Starting position (default: 0)

        Examples:
            news(action="search_forum", query="variable font")
            news(action="search_tutorials", query="kerning")
        """
        module = self._modules.get("glyphs_news")
        if not module:
            return "## Error\n\nNews module not initialized or not available."

        try:
            if action == "search_forum":
                return await module.web_search_forum(query=query)
            elif action == "search_tutorials":
                return await module.web_search_tutorials(
                    query=query, topic=topic, collection=collection
                )
            elif action == "fetch_tutorial":
                return await module.web_get_tutorial_content(url=url)
            elif action == "fetch_forum":
                return await module.web_get_forum_post_content(
                    url=url, post_number=post_number, start_position=start_position
                )
            elif action == "search_posts":
                return await module.web_search_news_posts(query=query)
            elif action == "fetch_content":
                return await module.web_fetch_news_content(url=url)
            else:
                return f"## Invalid Action\n\nUnknown action: `{action}`\n\nAvailable actions: search_forum, search_tutorials, fetch_tutorial, fetch_forum, search_posts, fetch_content"

        except Exception as e:
            logger.error(f"News action '{action}' failed: {e}")
            return f"## Error\n\nFailed to execute action '{action}': {str(e)}"

    # ========== Light Table Entry Point ==========

    def lighttable(
        self,
        action: str,
        query: str = "",
        enum_name: str = "",
        max_results: int = 10,
    ) -> str:
        """
        [LIGHTTABLE] Light Table version control API

        Actions:
        - search: Search Light Table API (query, max_results)
        - get_enum: Get enum details (enum_name)
        - list_enums: List all enums
        - list_all: List all API items

        Args:
            action: Operation to perform
            query: Search keywords
            enum_name: Enum name (e.g., DocumentState, ObjectStatus)
            max_results: Maximum results (default: 10)

        Examples:
            lighttable(action="search", query="DocumentState")
            lighttable(action="get_enum", enum_name="ObjectStatus")
        """
        module = self._modules.get("light_table_api")
        if not module:
            return "## Error\n\nLight Table module not initialized or not available."

        try:
            if action == "search":
                return module._search_api_tool(query=query, max_results=max_results)
            elif action == "get_enum":
                return module._get_enum_tool(enum_name=enum_name)
            elif action == "list_enums":
                return module._list_enums_tool()
            elif action == "list_all":
                return module._list_all_tool()
            else:
                return f"## Invalid Action\n\nUnknown action: `{action}`\n\nAvailable actions: search, get_enum, list_enums, list_all"

        except Exception as e:
            logger.error(f"Light Table action '{action}' failed: {e}")
            return f"## Error\n\nFailed to execute action '{action}': {str(e)}"
