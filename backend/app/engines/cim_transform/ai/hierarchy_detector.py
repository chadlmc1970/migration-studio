"""
Hierarchy Detector: Identify Time/Geography/Organizational Hierarchies

Detects hierarchical relationships among dimensions using pattern matching
and Claude API validation.
"""

import json
import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from anthropic import Anthropic

from app.config import ANTHROPIC_API_KEY, AI_MODEL, AI_MAX_TOKENS, AI_TEMPERATURE
from .prompts import HIERARCHY_DETECTION_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class HierarchyLevel:
    """Single level in a hierarchy."""
    dimension: str
    order: int


@dataclass
class Hierarchy:
    """Detected hierarchy."""
    name: str
    type: str  # Time, Geography, Organization, Product, Custom
    confidence: float
    levels: List[HierarchyLevel]
    warnings: List[str]
    missing_levels: List[str]


class HierarchyDetector:
    """Detects dimensional hierarchies using pattern matching + AI validation."""

    # Pattern-based hierarchy templates
    TIME_PATTERNS = {
        "year": ["year", "yr", "fiscal_year", "fy"],
        "quarter": ["quarter", "qtr", "fiscal_quarter", "fq"],
        "month": ["month", "mon", "fiscal_month"],
        "week": ["week", "wk", "week_num"],
        "day": ["day", "date", "day_num"],
    }

    GEO_PATTERNS = {
        "country": ["country", "nation", "country_code"],
        "region": ["region", "territory", "area"],
        "state": ["state", "province", "state_code"],
        "city": ["city", "town", "municipality"],
        "postal": ["postal", "zip", "postcode", "zip_code"],
    }

    ORG_PATTERNS = {
        "company": ["company", "corporation", "enterprise"],
        "division": ["division", "business_unit", "bu"],
        "department": ["department", "dept", "function"],
        "team": ["team", "group", "squad"],
        "employee": ["employee", "person", "staff", "emp"],
    }

    PRODUCT_PATTERNS = {
        "category": ["category", "product_category", "cat"],
        "subcategory": ["subcategory", "subcat", "product_subcategory"],
        "brand": ["brand", "manufacturer", "make"],
        "product": ["product", "item", "sku", "product_name"],
    }

    def __init__(self):
        """Initialize hierarchy detector."""
        if ANTHROPIC_API_KEY:
            self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
            self.model = AI_MODEL
            self.ai_enabled = True
        else:
            self.client = None
            self.ai_enabled = False
            logger.warning("AI disabled for HierarchyDetector - using pattern matching only")

    def detect_hierarchies(self, dimensions: List[Dict[str, Any]]) -> List[Hierarchy]:
        """
        Detect hierarchies from dimension list.

        Args:
            dimensions: List of dimension dicts

        Returns:
            List of detected Hierarchy objects
        """
        logger.info(f"Detecting hierarchies from {len(dimensions)} dimensions...")

        # Pattern-based pre-detection
        candidate_hierarchies = []
        candidate_hierarchies.extend(self._detect_time_hierarchy(dimensions))
        candidate_hierarchies.extend(self._detect_geo_hierarchy(dimensions))
        candidate_hierarchies.extend(self._detect_org_hierarchy(dimensions))
        candidate_hierarchies.extend(self._detect_product_hierarchy(dimensions))

        if not candidate_hierarchies:
            logger.info("No candidate hierarchies found via pattern matching")
            return []

        # AI validation (if enabled)
        if self.ai_enabled:
            validated_hierarchies = self._validate_hierarchies_with_ai(
                dimensions, candidate_hierarchies
            )
            return validated_hierarchies
        else:
            logger.info(f"Returning {len(candidate_hierarchies)} pattern-matched hierarchies (no AI validation)")
            return candidate_hierarchies

    def _detect_time_hierarchy(self, dimensions: List[Dict[str, Any]]) -> List[Hierarchy]:
        """Detect time hierarchies (Year/Quarter/Month/Week/Day)."""
        time_dims = {}

        for dim in dimensions:
            dim_name = dim.get("name", "").lower()
            for level, patterns in self.TIME_PATTERNS.items():
                if any(p in dim_name for p in patterns):
                    time_dims[level] = dim.get("name")
                    break

        if not time_dims:
            return []

        # Build hierarchy from detected levels
        level_order = ["year", "quarter", "month", "week", "day"]
        levels = []
        for order, level_name in enumerate(level_order, start=1):
            if level_name in time_dims:
                levels.append(HierarchyLevel(
                    dimension=time_dims[level_name],
                    order=order
                ))

        if len(levels) >= 2:  # At least 2 levels for valid hierarchy
            return [Hierarchy(
                name="Time Hierarchy",
                type="Time",
                confidence=0.8,  # Pattern matching confidence
                levels=levels,
                warnings=[],
                missing_levels=[]
            )]

        return []

    def _detect_geo_hierarchy(self, dimensions: List[Dict[str, Any]]) -> List[Hierarchy]:
        """Detect geography hierarchies (Country/State/City)."""
        geo_dims = {}

        for dim in dimensions:
            dim_name = dim.get("name", "").lower()
            for level, patterns in self.GEO_PATTERNS.items():
                if any(p in dim_name for p in patterns):
                    geo_dims[level] = dim.get("name")
                    break

        if not geo_dims:
            return []

        # Build hierarchy
        level_order = ["country", "region", "state", "city", "postal"]
        levels = []
        for order, level_name in enumerate(level_order, start=1):
            if level_name in geo_dims:
                levels.append(HierarchyLevel(
                    dimension=geo_dims[level_name],
                    order=order
                ))

        if len(levels) >= 2:
            return [Hierarchy(
                name="Geography Hierarchy",
                type="Geography",
                confidence=0.8,
                levels=levels,
                warnings=[],
                missing_levels=[]
            )]

        return []

    def _detect_org_hierarchy(self, dimensions: List[Dict[str, Any]]) -> List[Hierarchy]:
        """Detect organizational hierarchies (Company/Division/Department)."""
        org_dims = {}

        for dim in dimensions:
            dim_name = dim.get("name", "").lower()
            for level, patterns in self.ORG_PATTERNS.items():
                if any(p in dim_name for p in patterns):
                    org_dims[level] = dim.get("name")
                    break

        if not org_dims:
            return []

        # Build hierarchy
        level_order = ["company", "division", "department", "team", "employee"]
        levels = []
        for order, level_name in enumerate(level_order, start=1):
            if level_name in org_dims:
                levels.append(HierarchyLevel(
                    dimension=org_dims[level_name],
                    order=order
                ))

        if len(levels) >= 2:
            return [Hierarchy(
                name="Organization Hierarchy",
                type="Organization",
                confidence=0.8,
                levels=levels,
                warnings=[],
                missing_levels=[]
            )]

        return []

    def _detect_product_hierarchy(self, dimensions: List[Dict[str, Any]]) -> List[Hierarchy]:
        """Detect product hierarchies (Category/Subcategory/Brand/Product)."""
        product_dims = {}

        for dim in dimensions:
            dim_name = dim.get("name", "").lower()
            for level, patterns in self.PRODUCT_PATTERNS.items():
                if any(p in dim_name for p in patterns):
                    product_dims[level] = dim.get("name")
                    break

        if not product_dims:
            return []

        # Build hierarchy
        level_order = ["category", "subcategory", "brand", "product"]
        levels = []
        for order, level_name in enumerate(level_order, start=1):
            if level_name in product_dims:
                levels.append(HierarchyLevel(
                    dimension=product_dims[level_name],
                    order=order
                ))

        if len(levels) >= 2:
            return [Hierarchy(
                name="Product Hierarchy",
                type="Product",
                confidence=0.8,
                levels=levels,
                warnings=[],
                missing_levels=[]
            )]

        return []

    def _validate_hierarchies_with_ai(
        self,
        dimensions: List[Dict[str, Any]],
        candidates: List[Hierarchy]
    ) -> List[Hierarchy]:
        """Validate candidate hierarchies using Claude API."""
        logger.info(f"Validating {len(candidates)} candidate hierarchies with AI...")

        # Format dimensions for prompt
        dim_list = "\n".join([
            f"{i+1}. {dim.get('name', 'Unknown')} (type: {dim.get('data_type', 'unknown')})"
            for i, dim in enumerate(dimensions)
        ])

        prompt = HIERARCHY_DETECTION_PROMPT.format(dimensions=dim_list)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=AI_MAX_TOKENS,
                temperature=AI_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text
            result_data = json.loads(response_text)

            # Parse AI-validated hierarchies
            validated = []
            for h_data in result_data.get("hierarchies", []):
                levels = [
                    HierarchyLevel(dimension=lvl["dimension"], order=lvl["order"])
                    for lvl in h_data.get("levels", [])
                ]

                validated.append(Hierarchy(
                    name=h_data.get("name", "Unknown"),
                    type=h_data.get("type", "Custom"),
                    confidence=h_data.get("confidence", 0.5),
                    levels=levels,
                    warnings=h_data.get("warnings", []),
                    missing_levels=h_data.get("missing_levels", [])
                ))

            logger.info(f"AI validated {len(validated)} hierarchies")
            return validated

        except Exception as e:
            logger.error(f"AI validation failed: {e} - returning pattern-matched hierarchies")
            return candidates
