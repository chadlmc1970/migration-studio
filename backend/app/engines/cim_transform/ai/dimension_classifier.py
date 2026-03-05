"""
Dimension Classifier: Semantic Type Classification

Classifies dimensions by semantic type (Attribute, Time, Geography, KPI, etc.)
and suggests display formatting using Claude API.
"""

import json
import logging
from dataclasses import dataclass
from typing import Dict, Optional, Any, List
from anthropic import Anthropic

from app.config import ANTHROPIC_API_KEY, AI_MODEL, AI_MAX_TOKENS, AI_TEMPERATURE
from .prompts import DIMENSION_CLASSIFIER_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result of dimension classification."""
    semantic_type: str  # Attribute, Time, Geography, KPI, Organizational
    confidence: float
    display_format: Optional[str]
    sort_order: str  # alphabetical, chronological, numeric, custom
    aggregation_behavior: str  # none, hierarchy, group_by
    warnings: List[str]
    reasoning: str


class DimensionClassifier:
    """Classifies dimensions using pattern matching + Claude API."""

    # Pattern-based hints
    TIME_KEYWORDS = ["date", "time", "year", "month", "quarter", "day", "week", "period", "fiscal"]
    GEO_KEYWORDS = ["country", "state", "city", "region", "territory", "postal", "zip", "location", "address"]
    KPI_KEYWORDS = ["status", "rating", "level", "grade", "score", "priority", "risk", "category"]
    ORG_KEYWORDS = ["company", "department", "division", "team", "employee", "manager", "org"]

    def __init__(self):
        """Initialize dimension classifier."""
        if ANTHROPIC_API_KEY:
            self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
            self.model = AI_MODEL
            self.ai_enabled = True
        else:
            self.client = None
            self.ai_enabled = False
            logger.warning("AI disabled for DimensionClassifier - using heuristics only")

    def classify_dimension(self, dimension: Dict[str, Any]) -> ClassificationResult:
        """
        Classify a dimension by semantic type.

        Args:
            dimension: Dimension dict with name, description, data_type, etc.

        Returns:
            ClassificationResult with semantic type and display hints
        """
        dim_name = dimension.get("name", "").lower()
        description = dimension.get("description", "")
        data_type = dimension.get("data_type", "string")

        # Quick heuristic classification
        heuristic_type = self._heuristic_classification(dim_name, data_type)

        # If AI enabled, get detailed classification
        if self.ai_enabled:
            try:
                return self._classify_with_ai(dimension)
            except Exception as e:
                logger.error(f"AI classification failed for {dimension.get('name')}: {e}")
                # Fall back to heuristic
                return self._heuristic_result(heuristic_type, dim_name)
        else:
            return self._heuristic_result(heuristic_type, dim_name)

    def _heuristic_classification(self, dim_name: str, data_type: str) -> str:
        """Quick heuristic classification."""
        if any(kw in dim_name for kw in self.TIME_KEYWORDS):
            return "Time"
        elif any(kw in dim_name for kw in self.GEO_KEYWORDS):
            return "Geography"
        elif any(kw in dim_name for kw in self.KPI_KEYWORDS):
            return "KPI"
        elif any(kw in dim_name for kw in self.ORG_KEYWORDS):
            return "Organizational"
        else:
            return "Attribute"

    def _heuristic_result(self, semantic_type: str, dim_name: str) -> ClassificationResult:
        """Build classification result from heuristic."""
        return ClassificationResult(
            semantic_type=semantic_type,
            confidence=0.6,  # Lower confidence for heuristic
            display_format=None,
            sort_order="alphabetical",
            aggregation_behavior="group_by",
            warnings=["Classification based on heuristics only - AI unavailable"],
            reasoning=f"Heuristic match based on dimension name: {dim_name}"
        )

    def _classify_with_ai(self, dimension: Dict[str, Any]) -> ClassificationResult:
        """Classify dimension using Claude API."""
        dim_name = dimension.get("name", "Unknown")
        description = dimension.get("description", "")
        source_column = dimension.get("source_column", dimension.get("column", ""))
        data_type = dimension.get("data_type", "string")
        sample_values = dimension.get("sample_values", [])

        logger.info(f"Classifying dimension via AI: {dim_name}")

        prompt = DIMENSION_CLASSIFIER_PROMPT.format(
            dimension_name=dim_name,
            description=description or "No description",
            source_column=source_column or "Unknown",
            data_type=data_type,
            sample_values=", ".join(str(v) for v in sample_values[:5]) if sample_values else "No samples"
        )

        message = self.client.messages.create(
            model=self.model,
            max_tokens=AI_MAX_TOKENS,
            temperature=AI_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text
        result_data = json.loads(response_text)

        return ClassificationResult(
            semantic_type=result_data.get("semantic_type", "Attribute"),
            confidence=result_data.get("confidence", 0.0),
            display_format=result_data.get("display_format"),
            sort_order=result_data.get("sort_order", "alphabetical"),
            aggregation_behavior=result_data.get("aggregation_behavior", "group_by"),
            warnings=result_data.get("warnings", []),
            reasoning=result_data.get("reasoning", "")
        )
