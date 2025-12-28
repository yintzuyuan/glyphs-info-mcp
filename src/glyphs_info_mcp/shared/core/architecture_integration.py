"""
🏗️ Glyphs Architecture Awareness Integration Module

Unifies all architecture awareness features, providing complete architecture understanding
and code assistance capabilities for MCP tools.
This is the unified entry point for all AI assistance features.
"""

# mypy: ignore-errors

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Try to import all architecture-related modules
try:
    from .architecture_context import (
        ArchitectureContextEnhancer,
        enhance_api_response,
        get_architecture_hints,
    )

    ARCHITECTURE_CONTEXT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Architecture context not available: {e}")
    ARCHITECTURE_CONTEXT_AVAILABLE = False

try:
    from .id_connection_guide import (
        IDConnectionGuide,
        get_id_connection_guidance,
        get_smart_connection_suggestions,
    )

    ID_GUIDE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ID connection guide not available: {e}")
    ID_GUIDE_AVAILABLE = False

try:
    from .glyphs_patterns import (
        ArchitectureAwarePatterns,
        GlyphsArchitectureValidator,
        GlyphsCodeTemplates,
    )

    PATTERNS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Glyphs patterns not available: {e}")
    PATTERNS_AVAILABLE = False

try:
    from .code_assistant import (
        GlyphsCodeAssistant,
        analyze_glyphs_code,
        generate_architecture_aware_code,
        suggest_code_improvements,
    )

    CODE_ASSISTANT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Code assistant not available: {e}")
    CODE_ASSISTANT_AVAILABLE = False


class GlyphsArchitectureIntegration:
    """Glyphs architecture awareness integrator"""

    def __init__(self):
        """Initialize integrator"""
        self.capabilities = {
            "architecture_context": ARCHITECTURE_CONTEXT_AVAILABLE,
            "id_connection_guide": ID_GUIDE_AVAILABLE,
            "patterns": PATTERNS_AVAILABLE,
            "code_assistant": CODE_ASSISTANT_AVAILABLE,
        }

        self.full_system_available = all(self.capabilities.values())

        if self.full_system_available:
            logger.info("✅ Glyphs Architecture Integration: Full system available")
        else:
            missing = [k for k, v in self.capabilities.items() if not v]
            logger.warning(f"⚠️  Glyphs Architecture Integration: Missing {missing}")

    def get_system_status(self) -> dict[str, Any]:
        """Get system status"""
        return {
            "full_system_available": self.full_system_available,
            "capabilities": self.capabilities,
            "version": "2.0.0",
            "description": "Glyphs Architecture Awareness System",
        }

    def enhance_api_response_complete(
        self, api_name: str, original_response: str, context: dict | None = None
    ) -> str:
        """
        Fully enhance API response

        Args:
            api_name: API name
            original_response: Original response
            context: Additional context

        Returns:
            Fully enhanced response
        """
        if not ARCHITECTURE_CONTEXT_AVAILABLE:
            return original_response + "\n\n💡 **Architecture awareness system not fully loaded**"

        try:
            enhanced = enhance_api_response(api_name, original_response, context)

            # Add additional feature hints for full system
            if self.full_system_available:
                enhanced += """

---

## 🤖 AI Code Assistance Features

💡 **Smart Tips**: This API has full architecture awareness enabled
- 🏗️ **Architecture Position Awareness**: Understand this API's position in Glyphs object model
- 🔗 **ID Connection Guidance**: Auto-detect and guide masterID/axisID usage
- 🛡️ **Safety Check Mode**: Provide defensive programming suggestions
- 🎯 **Code Generation**: Can generate architecture-aware code templates

📖 **Deep Reference**: See `docs/GLYPHS_ARCHITECTURE.md` for complete architecture
🔧 **Pattern Library**: Use standard patterns in `src/shared/core/glyphs_patterns.py`
"""

            return enhanced

        except Exception as e:
            logger.error(f"Error in complete API enhancement: {e}")
            return original_response

    def get_comprehensive_guidance(
        self, class_name: str, member_name: str | None = None, scenario: str = "general"
    ) -> dict[str, Any]:
        """
        Get comprehensive guidance information

        Args:
            class_name: Class name
            member_name: Member name (optional)
            scenario: Usage scenario

        Returns:
            Comprehensive guidance information
        """
        guidance = {
            "class_name": class_name,
            "member_name": member_name,
            "scenario": scenario,
            "architecture_hints": [],
            "id_connections": [],
            "code_patterns": [],
            "safety_checks": [],
            "system_status": self.capabilities,
        }

        # Architecture hints
        if ARCHITECTURE_CONTEXT_AVAILABLE:
            try:
                hints = get_architecture_hints([class_name])
                guidance["architecture_hints"] = hints[:3]
            except Exception as e:
                logger.error(f"Error getting architecture hints: {e}")

        # ID connection guidance
        if ID_GUIDE_AVAILABLE:
            try:
                smart_suggestions = get_smart_connection_suggestions(
                    class_name, member_name
                )
                guidance["id_connections"] = smart_suggestions[:3]
            except Exception as e:
                logger.error(f"Error getting ID connection guidance: {e}")

        # Programming patterns
        if PATTERNS_AVAILABLE:
            try:
                # Provide relevant patterns based on class
                patterns = []
                if class_name in ["GSGlyph", "GSLayer"]:
                    patterns.append(
                        {
                            "name": "Safe Layer Iteration",
                            "description": "Safe layer iteration pattern",
                        }
                    )

                if "Component" in class_name:
                    patterns.append(
                        {
                            "name": "Component Validation",
                            "description": "Component reference validation pattern",
                        }
                    )

                guidance["code_patterns"] = patterns
            except Exception as e:
                logger.error(f"Error getting patterns: {e}")

        return guidance

    def analyze_and_improve_code(
        self, code: str, task_context: str | None = None
    ) -> dict[str, Any]:
        """
        Analyze and improve code

        Args:
            code: Code to analyze
            task_context: Task context

        Returns:
            Complete analysis and improvement suggestions
        """
        result = {
            "original_code": code,
            "task_context": task_context,
            "analysis_available": CODE_ASSISTANT_AVAILABLE,
            "analysis": None,
            "improvements": None,
            "architecture_validation": None,
        }

        if not CODE_ASSISTANT_AVAILABLE:
            result["message"] = "Code analysis feature not fully available"
            return result

        try:
            # Code quality analysis
            analysis = analyze_glyphs_code(code)
            result["analysis"] = analysis

            # Improvement suggestions
            improvements = suggest_code_improvements(code, {"task": task_context})
            result["improvements"] = improvements

            # Architecture validation
            if hasattr(GlyphsCodeAssistant, "validate_code_architecture"):
                validation = GlyphsCodeAssistant().validate_code_architecture(code)
                result["architecture_validation"] = validation

        except Exception as e:
            logger.error(f"Error in code analysis: {e}")
            result["error"] = str(e)

        return result

    def generate_smart_code(
        self, task_description: str, preferences: dict | None = None
    ) -> dict[str, Any]:
        """
        Smart code generation

        Args:
            task_description: Task description
            preferences: Generation preferences

        Returns:
            Generated code and related information
        """
        if not CODE_ASSISTANT_AVAILABLE:
            return {
                "error": "Code generation not available",
                "fallback_suggestion": "Please check the documentation and patterns manually",
            }

        try:
            # Identify related classes
            involved_classes = self._extract_classes_from_description(task_description)

            # Generate architecture-aware code
            generated = generate_architecture_aware_code(
                task_description, involved_classes
            )

            # Add integration system features
            generated["integration_features"] = {
                "full_system_available": self.full_system_available,
                "enhanced_validation": PATTERNS_AVAILABLE,
                "smart_suggestions": ID_GUIDE_AVAILABLE,
                "architecture_awareness": ARCHITECTURE_CONTEXT_AVAILABLE,
            }

            # Provide additional suggestions if full system available
            if self.full_system_available:
                generated["additional_recommendations"] = [
                    "Use ArchitectureAwarePatterns for advanced pattern matching",
                    "Use GlyphsArchitectureValidator to verify code correctness",
                    "Reference ID connection guidance to ensure correct object associations",
                ]

            return generated

        except Exception as e:
            logger.error(f"Error in smart code generation: {e}")
            return {"error": str(e)}

    def _extract_classes_from_description(self, description: str) -> list[str]:
        """Extract related classes from description"""
        classes = []
        description_lower = description.lower()

        # Class keyword mapping
        class_keywords = {
            "GSFont": ["font", "字型"],
            "GSGlyph": ["glyph", "字符", "字形"],
            "GSLayer": ["layer", "圖層"],
            "GSPath": ["path", "路徑", "輪廓"],
            "GSComponent": ["component", "組件"],
            "GSNode": ["node", "節點", "點"],
            "GSAnchor": ["anchor", "錨點"],
            "GSFontMaster": ["master", "母版"],
            "GSAxis": ["axis", "軸", "變化"],
        }

        for class_name, keywords in class_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                classes.append(class_name)

        return list(set(classes))

    def get_complete_api_enhancement_info(self) -> dict[str, Any]:
        """Get complete API enhancement information"""
        return {
            "system_name": "Glyphs Architecture Awareness System",
            "version": "2.0.0",
            "capabilities": self.capabilities,
            "features": {
                "architecture_context": {
                    "available": ARCHITECTURE_CONTEXT_AVAILABLE,
                    "description": "Add architecture position and related object info to API responses",
                },
                "id_connection_guide": {
                    "available": ID_GUIDE_AVAILABLE,
                    "description": "Provide smart guidance for masterID and axisID connections",
                },
                "patterns_library": {
                    "available": PATTERNS_AVAILABLE,
                    "description": "Provide architecture-aware programming patterns and validation",
                },
                "code_assistant": {
                    "available": CODE_ASSISTANT_AVAILABLE,
                    "description": "Smart code analysis, improvement suggestions, and generation",
                },
            },
            "integration_level": (
                "complete" if self.full_system_available else "partial"
            ),
            "documentation": {
                "architecture": "docs/GLYPHS_ARCHITECTURE.md",
                "patterns": "src/shared/core/glyphs_patterns.py",
                "examples": "Integrated into MCP tool responses",
            },
        }


# Global integrator instance
architecture_integration = GlyphsArchitectureIntegration()


def get_enhanced_api_response(
    api_name: str, original_response: str, context: dict | None = None
) -> str:
    """Convenience function to get fully enhanced API response"""
    return architecture_integration.enhance_api_response_complete(
        api_name, original_response, context
    )


def get_comprehensive_guidance(
    class_name: str, member_name: str | None = None, scenario: str = "general"
) -> dict[str, Any]:
    """Convenience function to get comprehensive guidance"""
    return architecture_integration.get_comprehensive_guidance(
        class_name, member_name, scenario
    )


def analyze_and_improve_code(
    code: str, task_context: str | None = None
) -> dict[str, Any]:
    """Convenience function to analyze and improve code"""
    return architecture_integration.analyze_and_improve_code(code, task_context)


def generate_smart_code(
    task_description: str, preferences: dict | None = None
) -> dict[str, Any]:
    """Convenience function for smart code generation"""
    return architecture_integration.generate_smart_code(task_description, preferences)


def get_system_status() -> dict[str, Any]:
    """Convenience function to get system status"""
    return architecture_integration.get_system_status()
