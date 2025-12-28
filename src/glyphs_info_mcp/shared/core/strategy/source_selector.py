#!/usr/bin/env python3
"""
Source Selector - Intelligently selects the most suitable search sources
"""

# mypy: ignore-errors

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class SmartSourceSelector:
    """Smart Source Selector - Intelligently selects the most suitable search sources based on query content"""

    def __init__(self, vocabulary_module=None):
        """Initialize source selector

        Args:
            vocabulary_module: Vocabulary module (for term analysis)
        """
        self.vocabulary_module = vocabulary_module

        # Predefined source characteristics and applicable scenarios
        self.source_profiles = {
            "handbook": {
                "keywords": [
                    "tutorial",
                    "guide",
                    "how to",
                    "step",
                    "process",
                    "workflow",
                    "設定",
                    "教學",
                    "步驟",
                    "流程",
                    "如何",
                    "操作",
                    "feature",
                    "tool",
                    "menu",
                    "panel",
                    "dialog",
                    "功能",
                    "工具",
                    "選單",
                    "面板",
                    "對話框",
                ],
                "weight": 1.0,
                "description": "Glyphs application user manual",
            },
            "api": {
                "keywords": [
                    "class",
                    "method",
                    "property",
                    "function",
                    "attribute",
                    "python",
                    "api",
                    "reference",
                    "documentation",
                    "spec",
                    "類別",
                    "方法",
                    "屬性",
                    "函數",
                    "API",
                    "文件",
                    "規格",
                    "GSFont",
                    "GSGlyph",
                    "GSLayer",
                    "GSPath",
                    "GSNode",
                    "parameter",
                    "return",
                    "type",
                    "signature",
                    "參數",
                    "回傳",
                    "型別",
                    "簽名",
                ],
                "weight": 1.0,  # Increased weight, equal importance to handbook
                "description": "Python API official documentation and specifications",
            },
            "glyphs-sdk": {
                "keywords": [
                    "example",
                    "sample",
                    "code",
                    "implementation",
                    "script",
                    "template",
                    "demo",
                    "practice",
                    "development",
                    "範例",
                    "例子",
                    "程式碼",
                    "實作",
                    "腳本",
                    "模板",
                    "示範",
                    "實踐",
                    "開發",
                    "automation",
                    "macro",
                    "plugin",
                    "workflow",
                    "自動化",
                    "巨集",
                    "外掛",
                    "工作流程",
                    "batch",
                    "process",
                    "generate",
                    "create",
                    "批次",
                    "處理",
                    "生成",
                    "建立",
                ],
                "weight": 0.95,
                "description": "SDK code samples and development guides",
            },
            "news": {
                "keywords": [
                    "new",
                    "update",
                    "version",
                    "release",
                    "announcement",
                    "新",
                    "更新",
                    "版本",
                    "發布",
                    "公告",
                    "blog",
                    "article",
                    "post",
                    "discussion",
                    "部落格",
                    "文章",
                    "貼文",
                    "討論",
                    "community",
                    "forum",
                    "question",
                    "problem",
                    "社群",
                    "論壇",
                    "問題",
                ],
                "weight": 0.7,
                "description": "Official news and community discussions",
            },
        }

        # Query type analysis patterns
        self.query_patterns = {
            "how_to_implement": re.compile(
                r"how\s+to|如何實作|怎麼做|怎样做|實作|implementation", re.IGNORECASE
            ),
            "api_spec": re.compile(
                r"api|method|property|function|class|參數|parameter|type|文檔|documentation|規格|spec",
                re.IGNORECASE,
            ),
            "code_example": re.compile(
                r"example|sample|範例|例子|code|程式碼|script|腳本|template|模板",
                re.IGNORECASE,
            ),
            "development": re.compile(
                r"develop|create|build|generate|automation|外掛|plugin|macro|開發|建立",
                re.IGNORECASE,
            ),
            "problem": re.compile(
                r"error|問題|錯誤|不能|無法|失敗|bug|troubleshoot", re.IGNORECASE
            ),
            "feature": re.compile(
                r"feature|功能|工具|設定|選項|tool|setting", re.IGNORECASE
            ),
            "version": re.compile(
                r"version|版本|更新|new|最新|release|發布", re.IGNORECASE
            ),
        }

    def select_sources(
        self, query: str, available_sources: dict[str, Any], max_sources: int = 3
    ) -> dict[str, tuple[Any, float]]:
        """Intelligently select search sources

        Args:
            query: Search query
            available_sources: Available sources dictionary {name: source_instance}
            max_sources: Maximum number of sources to select

        Returns:
            Selected sources dictionary {name: (source_instance, relevance_score)}
        """
        if not available_sources:
            return {}

        # 1. Analyze query features
        query_features = self._analyze_query(query)

        # 2. Calculate relevance score for each source
        source_scores = {}
        for source_name, source_instance in available_sources.items():
            if source_name in self.source_profiles:
                score = self._calculate_source_score(query, query_features, source_name)
                source_scores[source_name] = (source_instance, score)
                logger.debug(f"Source {source_name} score: {score:.3f}")
            else:
                # Unknown sources get medium score
                source_scores[source_name] = (source_instance, 0.5)

        # 3. Select most relevant sources
        sorted_sources = sorted(
            source_scores.items(), key=lambda x: x[1][1], reverse=True
        )
        selected_sources = {}

        for source_name, (source_instance, score) in sorted_sources[:max_sources]:
            # Only select sources with score above threshold
            if score >= 0.1:
                selected_sources[source_name] = (source_instance, score)

        # 4. Ensure at least one source
        if not selected_sources and available_sources:
            # If no sources selected, use default source
            default_source = self._get_default_source(available_sources)
            if default_source:
                source_name, source_instance = default_source
                selected_sources[source_name] = (source_instance, 0.5)

        logger.info(f"Selected sources for query '{query}': {list(selected_sources.keys())}")
        return selected_sources

    def _analyze_query(self, query: str) -> dict[str, Any]:
        """Analyze query features

        Args:
            query: Search query

        Returns:
            Query features dictionary
        """
        features = {
            "query_type": [],
            "keywords": [],
            "language": "en",
            "complexity": "simple",
        }

        # Detect query type
        for pattern_name, pattern in self.query_patterns.items():
            if pattern.search(query):
                features["query_type"].append(pattern_name)

        # Detect language
        if re.search(r"[\u4e00-\u9fff]", query):
            features["language"] = "zh"

        # Extract keywords
        features["keywords"] = [
            word.strip() for word in query.lower().split() if len(word.strip()) > 2
        ]

        # Determine complexity
        word_count = len(features["keywords"])
        if word_count > 5:
            features["complexity"] = "complex"
        elif word_count > 2:
            features["complexity"] = "medium"

        logger.debug(f"Query features: {features}")
        return features

    def _calculate_source_score(
        self, query: str, query_features: dict[str, Any], source_name: str
    ) -> float:
        """Calculate source relevance score

        Args:
            query: Original query
            query_features: Query features
            source_name: Source name

        Returns:
            Relevance score (0.0-1.0)
        """
        if source_name not in self.source_profiles:
            return 0.5

        profile = self.source_profiles[source_name]
        base_weight = profile["weight"]
        keywords = profile["keywords"]

        score = 0.0

        # 1. Keyword match score
        keyword_matches = 0
        query_lower = query.lower()

        for keyword in keywords:
            if keyword in query_lower:
                keyword_matches += 1

        if keywords:
            keyword_score = (keyword_matches / len(keywords)) * 0.5
            score += keyword_score

        # 2. Query type match score
        type_score = self._calculate_type_score(
            query_features["query_type"], source_name
        )
        score += type_score

        # 3. Language preference score
        language_score = self._calculate_language_score(
            query_features["language"], source_name
        )
        score += language_score

        # 4. Vocabulary translation enhancement (if vocabulary module available)
        vocab_score = self._calculate_vocab_score(query, source_name)
        score += vocab_score

        # 5. Apply base weight
        final_score = score * base_weight

        return min(1.0, max(0.0, final_score))

    def _calculate_type_score(self, query_types: list[str], source_name: str) -> float:
        """Calculate score based on query type"""
        if not query_types:
            return 0.1  # Default score

        type_source_mapping = {
            "how_to_implement": {
                "glyphs-sdk": 0.4,
                "handbook": 0.3,
                "api": 0.2,
                "news": 0.1,
            },
            "api_spec": {"api": 0.5, "handbook": 0.2, "glyphs-sdk": 0.1, "news": 0.1},
            "code_example": {
                "glyphs-sdk": 0.5,
                "api": 0.3,
                "handbook": 0.2,
                "news": 0.1,
            },
            "development": {
                "glyphs-sdk": 0.4,
                "api": 0.3,
                "handbook": 0.2,
                "news": 0.1,
            },
            "problem": {"news": 0.3, "glyphs-sdk": 0.2, "handbook": 0.2, "api": 0.1},
            "feature": {"handbook": 0.3, "api": 0.2, "glyphs-sdk": 0.2, "news": 0.1},
            "version": {"news": 0.3, "handbook": 0.1, "api": 0.1, "glyphs-sdk": 0.1},
        }

        total_score = 0.0
        for query_type in query_types:
            if query_type in type_source_mapping:
                mapping = type_source_mapping[query_type]
                total_score += mapping.get(source_name, 0.0)

        return total_score

    def _calculate_language_score(self, language: str, source_name: str) -> float:
        """Calculate score based on language"""
        # All sources currently support Chinese and English, give small bonus
        if language == "zh":
            return 0.05  # Small bonus for Chinese queries
        return 0.0

    def _calculate_vocab_score(self, query: str, source_name: str) -> float:
        """Calculate score based on vocabulary translation"""
        if not self.vocabulary_module or not self.vocabulary_module.is_initialized:
            return 0.0

        try:
            # Check if query contains Glyphs professional terms
            translated = self.vocabulary_module.translate_to_english(query)
            if translated != query:
                # Contains professional terms, all sources have a chance
                return 0.1

            # Check English professional terms
            zh_translated = self.vocabulary_module.translate_to_chinese(query)
            if zh_translated != query:
                return 0.1
        except Exception as e:
            logger.debug(f"Vocabulary score calculation failed: {e}")

        return 0.0

    def _get_default_source(
        self, available_sources: dict[str, Any]
    ) -> tuple[str, Any] | None:
        """Get default source

        Args:
            available_sources: Available sources

        Returns:
            (source_name, source_instance) or None
        """
        # Priority order: handbook > api > glyphs-sdk > news > others
        priority_order = ["handbook", "api", "glyphs-sdk", "news"]

        for source_name in priority_order:
            if source_name in available_sources:
                return (source_name, available_sources[source_name])

        # If no priority sources, return first available source
        if available_sources:
            first_source = next(iter(available_sources.items()))
            return first_source

        return None

    def get_source_recommendations(
        self, query: str, available_sources: dict[str, Any]
    ) -> dict[str, str]:
        """Get source recommendations

        Args:
            query: Search query
            available_sources: Available sources

        Returns:
            Source recommendations dictionary
        """
        recommendations = {}
        selected_sources = self.select_sources(query, available_sources)

        for source_name, (_, score) in selected_sources.items():
            if source_name in self.source_profiles:
                profile = self.source_profiles[source_name]
                recommendations[source_name] = (
                    f"{profile['description']} (relevance: {score:.2f})"
                )
            else:
                recommendations[source_name] = f"Unknown source (relevance: {score:.2f})"

        return recommendations

    def update_source_profile(self, source_name: str, profile: dict[str, Any]):
        """Update source profile

        Args:
            source_name: Source name
            profile: New source profile
        """
        self.source_profiles[source_name] = profile
        logger.info(f"Updated source profile: {source_name}")

    def add_query_pattern(self, pattern_name: str, pattern: re.Pattern):
        """Add query pattern

        Args:
            pattern_name: Pattern name
            pattern: Regular expression pattern
        """
        self.query_patterns[pattern_name] = pattern
        logger.info(f"Added query pattern: {pattern_name}")


class SourceSelectorFactory:
    """Source Selector Factory"""

    @staticmethod
    def create_smart_selector(vocabulary_module=None) -> SmartSourceSelector:
        """Create smart source selector

        Args:
            vocabulary_module: Vocabulary module

        Returns:
            SmartSourceSelector instance
        """
        return SmartSourceSelector(vocabulary_module)
