"""
Semantic Enhancer: Main AI Enhancement Orchestrator

Coordinates all AI enhancement services to enrich CIM with semantic intelligence:
- Dimension classification
- Hierarchy detection
- Formula translation
- Measure format inference
"""

import logging
from typing import Dict, Any

from app.config import AI_ENABLED
from .dimension_classifier import DimensionClassifier
from .hierarchy_detector import HierarchyDetector
from .formula_translator import FormulaTranslator

logger = logging.getLogger(__name__)


class SemanticEnhancer:
    """Main orchestrator for AI-powered semantic enhancement."""

    def __init__(self):
        """Initialize semantic enhancer with AI components."""
        self.ai_enabled = AI_ENABLED

        if not self.ai_enabled:
            logger.warning("AI enhancement disabled - ANTHROPIC_API_KEY not configured")
            return

        try:
            self.dimension_classifier = DimensionClassifier()
            self.hierarchy_detector = HierarchyDetector()
            self.formula_translator = FormulaTranslator()
            logger.info("AI semantic enhancement enabled")
        except Exception as e:
            logger.error(f"Failed to initialize AI components: {e}")
            self.ai_enabled = False

    def enhance_cim(self, cim: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance CIM with AI-powered semantic intelligence.

        Args:
            cim: Canonical Intermediate Model dict

        Returns:
            Enhanced CIM with ai_enhancements section
        """
        if not self.ai_enabled:
            logger.info("Skipping AI enhancement (disabled)")
            return cim

        logger.info("Starting AI semantic enhancement...")

        # Initialize enhancement metadata
        cim.setdefault("ai_enhancements", {
            "enabled": True,
            "dimension_classifications": {},
            "detected_hierarchies": [],
            "translated_formulas": {},
            "warnings": [],
            "confidence_scores": {}
        })

        try:
            # 1. Classify dimensions
            self._enhance_dimensions(cim)

            # 2. Detect hierarchies
            self._detect_hierarchies(cim)

            # 3. Translate formulas (if present in metadata)
            self._translate_formulas(cim)

            logger.info("AI semantic enhancement complete")

        except Exception as e:
            logger.error(f"AI enhancement failed: {e}")
            cim["ai_enhancements"]["warnings"].append(f"Enhancement failed: {str(e)}")

        return cim

    def _enhance_dimensions(self, cim: Dict[str, Any]):
        """Classify all dimensions with semantic types."""
        # Support both CIMModel (flat dimensions) and CanonicalModel (nested business_layer)
        dimensions = cim.get("dimensions", []) or cim.get("business_layer", {}).get("dimensions", [])

        logger.info(f"📊 DEBUG: CIM keys: {list(cim.keys())}")
        logger.info(f"📊 DEBUG: Found {len(dimensions)} dimensions to classify")

        if not dimensions:
            logger.info("No dimensions to classify")
            return

        logger.info(f"Classifying {len(dimensions)} dimensions...")

        for dim in dimensions:
            dim_name = dim.get("name", "Unknown")

            try:
                classification = self.dimension_classifier.classify_dimension(dim)

                # Add AI metadata to dimension
                dim["ai_semantic_type"] = classification.semantic_type
                dim["ai_confidence"] = classification.confidence
                dim["ai_display_format"] = classification.display_format
                dim["ai_sort_order"] = classification.sort_order

                # Store in enhancement metadata
                cim["ai_enhancements"]["dimension_classifications"][dim_name] = {
                    "semantic_type": classification.semantic_type,
                    "confidence": classification.confidence,
                    "reasoning": classification.reasoning
                }

                if classification.warnings:
                    cim["ai_enhancements"]["warnings"].extend([
                        f"{dim_name}: {w}" for w in classification.warnings
                    ])

                logger.info(
                    f"  Classified {dim_name} as {classification.semantic_type} "
                    f"(confidence: {classification.confidence:.2f})"
                )

            except Exception as e:
                logger.error(f"Failed to classify dimension {dim_name}: {e}")
                cim["ai_enhancements"]["warnings"].append(
                    f"Failed to classify {dim_name}: {str(e)}"
                )

    def _detect_hierarchies(self, cim: Dict[str, Any]):
        """Detect dimensional hierarchies."""
        # Support both CIMModel (flat dimensions) and CanonicalModel (nested business_layer)
        dimensions = cim.get("dimensions", []) or cim.get("business_layer", {}).get("dimensions", [])

        if not dimensions:
            return

        logger.info("Detecting hierarchies...")

        try:
            hierarchies = self.hierarchy_detector.detect_hierarchies(dimensions)

            # Store detected hierarchies
            for hierarchy in hierarchies:
                hierarchy_def = {
                    "name": hierarchy.name,
                    "type": hierarchy.type,
                    "confidence": hierarchy.confidence,
                    "levels": [
                        {"dimension": level.dimension, "order": level.order}
                        for level in hierarchy.levels
                    ],
                    "warnings": hierarchy.warnings,
                    "missing_levels": hierarchy.missing_levels
                }

                cim["ai_enhancements"]["detected_hierarchies"].append(hierarchy_def)

                logger.info(
                    f"  Detected {hierarchy.type} hierarchy: {' → '.join([lvl.dimension for lvl in hierarchy.levels])} "
                    f"(confidence: {hierarchy.confidence:.2f})"
                )

        except Exception as e:
            logger.error(f"Hierarchy detection failed: {e}")
            cim["ai_enhancements"]["warnings"].append(
                f"Hierarchy detection failed: {str(e)}"
            )

    def _translate_formulas(self, cim: Dict[str, Any]):
        """Translate BOBJ formulas to target system syntax."""
        # Support both CIMModel and CanonicalModel structures
        dimensions = cim.get("dimensions", []) or cim.get("business_layer", {}).get("dimensions", [])
        measures = cim.get("measures", []) or cim.get("business_layer", {}).get("measures", [])
        joins = cim.get("joins", []) or cim.get("data_foundation", {}).get("joins", [])

        metadata = cim.get("metadata", {})

        # Check for formulas in metadata
        formulas = metadata.get("formulas", [])
        prompts = metadata.get("prompts", {})

        if not formulas and not prompts:
            logger.info("No formulas to translate")
            return

        logger.info(f"Translating {len(formulas)} formulas...")

        translation_context = {
            "dimensions": dimensions,
            "measures": measures,
            "joins": joins
        }

        for formula_def in formulas:
            formula_name = formula_def.get("name", "Unknown")
            expression = formula_def.get("expression", "")

            if not expression:
                continue

            try:
                result = self.formula_translator.translate_formula(
                    bobj_expression=expression,
                    context=translation_context,
                    target_system="SAC"  # Default to SAC
                )

                # Store translation result
                cim["ai_enhancements"]["translated_formulas"][formula_name] = {
                    "original": expression,
                    "translated": result.translated_formula,
                    "confidence": result.confidence,
                    "warnings": result.warnings,
                    "explanation": result.explanation,
                    "fallback": result.fallback,
                    "cache_hit": result.cache_hit
                }

                logger.info(
                    f"  Translated formula '{formula_name}' "
                    f"(confidence: {result.confidence:.2f}, cache: {result.cache_hit})"
                )

            except Exception as e:
                logger.error(f"Failed to translate formula {formula_name}: {e}")
                cim["ai_enhancements"]["warnings"].append(
                    f"Failed to translate formula {formula_name}: {str(e)}"
                )
