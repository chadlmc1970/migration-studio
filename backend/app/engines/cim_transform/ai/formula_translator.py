"""
Formula Translator: BOBJ Expression → SAC/Datasphere/HANA

Translates BusinessObjects formulas to target system syntax using Claude API.
Handles BOBJ-specific functions like @Select, @Prompt, @Aggregate, @Where.
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from anthropic import Anthropic

from app.config import ANTHROPIC_API_KEY, AI_MODEL, AI_MAX_TOKENS, AI_TEMPERATURE, AI_CACHE_TTL
from .prompts import FORMULA_TRANSLATION_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class TranslationResult:
    """Result of formula translation."""
    translated_formula: str
    confidence: float
    warnings: List[str]
    fallback: Optional[str]
    explanation: str
    cache_hit: bool = False


class FormulaTranslator:
    """Translates BOBJ formulas to target system syntax using Claude API."""

    def __init__(self):
        """Initialize formula translator with API client and cache."""
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required for FormulaTranslator")

        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = AI_MODEL
        self.max_tokens = AI_MAX_TOKENS
        self.temperature = AI_TEMPERATURE

        # In-memory cache with TTL
        self._cache: Dict[str, tuple[TranslationResult, float]] = {}
        self._cache_ttl = AI_CACHE_TTL

    def translate_formula(
        self,
        bobj_expression: str,
        context: Dict[str, Any],
        target_system: str = "SAC"
    ) -> TranslationResult:
        """
        Translate BOBJ formula to target system syntax.

        Args:
            bobj_expression: BOBJ formula expression
            context: Context dict with dimensions, measures, joins
            target_system: Target system (SAC, Datasphere, HANA)

        Returns:
            TranslationResult with translated formula and metadata
        """
        # Check cache first
        cache_key = self._get_cache_key(bobj_expression, context, target_system)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            logger.info(f"Cache hit for formula: {bobj_expression[:50]}...")
            cached_result.cache_hit = True
            return cached_result

        # Build prompt
        prompt = self._build_prompt(bobj_expression, context, target_system)

        try:
            logger.info(f"Translating formula via Claude API: {bobj_expression[:50]}...")
            start_time = time.time()

            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            elapsed = time.time() - start_time
            response_text = message.content[0].text

            # Parse JSON response
            result_data = json.loads(response_text)

            result = TranslationResult(
                translated_formula=result_data.get("translated_formula", ""),
                confidence=result_data.get("confidence", 0.0),
                warnings=result_data.get("warnings", []),
                fallback=result_data.get("fallback"),
                explanation=result_data.get("explanation", ""),
                cache_hit=False
            )

            # Log token usage
            logger.info(
                f"Translation complete in {elapsed:.2f}s - "
                f"Tokens: {message.usage.input_tokens} in, {message.usage.output_tokens} out - "
                f"Confidence: {result.confidence:.2f}"
            )

            # Cache result
            self._add_to_cache(cache_key, result)

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude API response: {e}")
            return self._fallback_translation(bobj_expression, str(e))

        except Exception as e:
            logger.error(f"Formula translation failed: {e}")
            return self._fallback_translation(bobj_expression, str(e))

    def _build_prompt(
        self,
        bobj_expression: str,
        context: Dict[str, Any],
        target_system: str
    ) -> str:
        """Build Claude API prompt for formula translation."""
        # Extract context components
        dimensions = context.get("dimensions", [])
        measures = context.get("measures", [])
        joins = context.get("joins", [])

        # Format dimensions for prompt
        dim_list = [f"- {dim.get('name', 'Unknown')}" for dim in dimensions[:10]]
        if len(dimensions) > 10:
            dim_list.append(f"... and {len(dimensions) - 10} more")

        # Format measures for prompt
        measure_list = [f"- {m.get('name', 'Unknown')}" for m in measures[:10]]
        if len(measures) > 10:
            measure_list.append(f"... and {len(measures) - 10} more")

        # Format joins for prompt
        join_list = [
            f"- {j.get('left_table', '?')} → {j.get('right_table', '?')}"
            for j in joins[:5]
        ]
        if len(joins) > 5:
            join_list.append(f"... and {len(joins) - 5} more")

        return FORMULA_TRANSLATION_PROMPT.format(
            target_system=target_system,
            bobj_expression=bobj_expression,
            dimensions="\n".join(dim_list) if dim_list else "None",
            measures="\n".join(measure_list) if measure_list else "None",
            joins="\n".join(join_list) if join_list else "None"
        )

    def _get_cache_key(
        self,
        bobj_expression: str,
        context: Dict[str, Any],
        target_system: str
    ) -> str:
        """Generate cache key for formula translation."""
        # Create deterministic cache key from formula + context
        cache_input = f"{bobj_expression}:{target_system}:{len(context.get('dimensions', []))}:{len(context.get('measures', []))}"
        return hashlib.sha256(cache_input.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[TranslationResult]:
        """Retrieve result from cache if not expired."""
        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return result
            else:
                # Expired, remove from cache
                del self._cache[cache_key]
        return None

    def _add_to_cache(self, cache_key: str, result: TranslationResult):
        """Add result to cache with current timestamp."""
        self._cache[cache_key] = (result, time.time())

    def _fallback_translation(self, bobj_expression: str, error: str) -> TranslationResult:
        """Return fallback result when translation fails."""
        logger.warning(f"Using fallback translation for: {bobj_expression[:50]}...")
        return TranslationResult(
            translated_formula=f"/* Original BOBJ: {bobj_expression} */\n/* Translation failed - manual review required */",
            confidence=0.0,
            warnings=[f"Translation failed: {error}"],
            fallback=None,
            explanation="Automatic translation unavailable, manual review required",
            cache_hit=False
        )
