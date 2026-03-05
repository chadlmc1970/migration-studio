"""
Claude API Prompt Templates for Semantic Enhancement

Contains specialized prompts for:
- Formula translation (BOBJ → SAC/Datasphere)
- Hierarchy detection and validation
- Dimension type classification
- Measure format inference
"""

FORMULA_TRANSLATION_PROMPT = """Translate this BusinessObjects formula to {target_system} syntax.

**BOBJ Formula:**
{bobj_expression}

**Available Context:**
- Target System: {target_system} (SAC, Datasphere, or HANA)
- Dimensions: {dimensions}
- Measures: {measures}
- Join Structure: {joins}

**Requirements:**
1. Convert BOBJ functions (@Select, @Prompt, @Aggregate, @Where) to {target_system} equivalents
2. Resolve table.column references to appropriate dimension/measure IDs
3. Handle aggregation context (detail vs aggregate level)
4. Return valid {target_system} expression (MDX for SAC, SQL for Datasphere/HANA)
5. Flag any ambiguities requiring manual review

**Common BOBJ Function Mappings:**
- @Select(Object\\Name) → Reference to dimension/measure
- @Aggregate(expression) → Aggregated calculation
- @Prompt(prompt_text, type) → Parameterized value
- @Where(condition) → Filter expression

**Response Format (JSON only):**
{{
  "translated_formula": "Translated expression in {target_system} syntax",
  "confidence": 0.95,  // 0-1 scale, >0.7 is production-ready
  "warnings": ["List of potential issues"],
  "fallback": "Simpler fallback if low confidence",
  "explanation": "Brief explanation of translation approach"
}}

Only return valid JSON, no additional text."""

HIERARCHY_DETECTION_PROMPT = """Analyze these dimensions and identify hierarchical relationships.

**Dimensions:**
{dimensions}

**Task:**
1. Identify valid hierarchies (time, geography, organizational)
2. Determine drill path order (e.g., Year → Quarter → Month → Day)
3. Flag any missing levels or inconsistencies
4. Suggest appropriate level names for SAC

**Common Hierarchy Types:**
- **Time**: Year/Quarter/Month/Week/Day, Fiscal Year/Period
- **Geography**: Country/Region/State/City/PostalCode
- **Organization**: Company/Division/Department/Team/Employee
- **Product**: Category/Subcategory/Brand/Product

**Response Format (JSON only):**
{{
  "hierarchies": [
    {{
      "name": "Time Hierarchy",
      "type": "Time",  // Time, Geography, Organization, Product, Custom
      "confidence": 0.9,
      "levels": [
        {{"dimension": "Year", "order": 1}},
        {{"dimension": "Quarter", "order": 2}},
        {{"dimension": "Month", "order": 3}}
      ],
      "warnings": ["Quarter values must be Q1-Q4 format"],
      "missing_levels": []
    }}
  ]
}}

Only return valid JSON, no additional text."""

DIMENSION_CLASSIFIER_PROMPT = """Classify this dimension to determine its semantic type and display characteristics.

**Dimension:**
- Name: {dimension_name}
- Description: {description}
- Source Column: {source_column}
- Data Type: {data_type}
- Sample Values: {sample_values}

**Classification Categories:**
1. **Attribute**: Standard descriptive dimension (Product Name, Customer ID)
2. **Time**: Calendar or fiscal time (Order Date, Fiscal Period)
3. **Geography**: Location-based (Country, City, Region)
4. **KPI Dimension**: Threshold-based classification (High/Medium/Low, Red/Yellow/Green)
5. **Organizational**: Company structure (Department, Division, Employee)

**Response Format (JSON only):**
{{
  "semantic_type": "Time",  // Attribute, Time, Geography, KPI, Organizational
  "confidence": 0.95,
  "display_format": "MMM YYYY",  // Suggested display format
  "sort_order": "chronological",  // alphabetical, chronological, numeric, custom
  "aggregation_behavior": "none",  // none, hierarchy, group_by
  "warnings": [],
  "reasoning": "Brief explanation of classification"
}}

Only return valid JSON, no additional text."""

MEASURE_FORMAT_PROMPT = """Determine the appropriate display format for this measure.

**Measure:**
- Name: {measure_name}
- Description: {description}
- Source Column: {source_column}
- Aggregation: {aggregation}
- Data Type: {data_type}

**Format Categories:**
1. **Currency**: Dollar amounts ($#,##0.00, €#,##0.00)
2. **Percentage**: Ratio or percentage (0.00%, #,##0.00%)
3. **Count**: Integer with no decimals (#,##0)
4. **Decimal**: Numeric with precision (#,##0.00, #,##0.000)
5. **Scientific**: Large numbers (0.00E+00)

**Response Format (JSON only):**
{{
  "format_string": "$#,##0.00",
  "format_type": "Currency",  // Currency, Percentage, Count, Decimal, Scientific
  "currency_code": "USD",  // If currency type, otherwise null
  "decimal_places": 2,
  "confidence": 0.9,
  "reasoning": "Measure name contains 'Revenue' and 'Amount', indicating currency"
}}

Only return valid JSON, no additional text."""

CONTEXT_RESOLUTION_PROMPT = """Resolve join ambiguity for this BusinessObjects context.

**Context:**
- Name: {context_name}
- Description: {description}
- Involved Tables: {tables}
- Join Paths: {join_paths}

**Task:**
Recommend the optimal join path for queries involving these tables, considering:
1. Cardinality (one-to-many vs many-to-many)
2. Data integrity (referential integrity, nulls)
3. Performance implications
4. Business logic

**Response Format (JSON only):**
{{
  "recommended_path": ["Table1", "Table2", "Table3"],
  "confidence": 0.85,
  "reasoning": "Explanation of why this path is optimal",
  "alternative_paths": [["Table1", "Table4", "Table3"]],
  "warnings": ["Potential fan trap with Table2-Table3 join"]
}}

Only return valid JSON, no additional text."""
