#!/usr/bin/env python3
"""Test real AI enhancement with Claude API"""
import sys
import os
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from anthropic import Anthropic

# Load the extracted CIM
with open('/tmp/ai_test_output/enhanced_cim.json') as f:
    cim = json.load(f)

print('='*80)
print('AI SEMANTIC ENHANCEMENT - REAL OUTPUT')
print('='*80)

# Get dimensions and measures
dimensions = cim.get('metadata', {}).get('dimension_details', [])
measures = cim.get('metadata', {}).get('measure_details', [])

print(f'\nUniverse: {cim["universe_name"]}')
print(f'Dimensions: {len(dimensions)}')
print(f'Measures: {len(measures)}')

# Initialize Claude client
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# 1. CLASSIFY DIMENSIONS
print('\n' + '='*80)
print('🧠 STEP 1: CLASSIFYING DIMENSIONS WITH AI')
print('='*80)

prompt = f'''Analyze these dimensions from a Business Objects universe and classify each by semantic type.

Dimensions:
{json.dumps(dimensions, indent=2)}

For each dimension, determine its semantic type:
- Time: dates, timestamps, years, quarters, months, days
- User: usernames, user IDs, person names
- System: servers, applications, hosts, services
- Object: document names, object types, artifacts
- Event: event types, actions, activities, operations
- KPI: calculated metrics
- Attribute: other descriptive fields

Return ONLY a JSON object in this exact format (no markdown, no extra text):
{{
  "Event Type": {{"semantic_type": "Event", "confidence": 0.95, "reasoning": "..."}},
  "Event Action": {{"semantic_type": "Event", "confidence": 0.92, "reasoning": "..."}}
}}'''

response = client.messages.create(
    model='claude-sonnet-4-6',
    max_tokens=2000,
    temperature=0.0,
    messages=[{'role': 'user', 'content': prompt}]
)

classifications_text = response.content[0].text.strip()
# Remove markdown code blocks if present
if classifications_text.startswith('```'):
    classifications_text = '\n'.join(classifications_text.split('\n')[1:-1])

classifications = json.loads(classifications_text)

print('\n📊 DIMENSION CLASSIFICATIONS:')
for dim_name, classification in sorted(classifications.items()):
    sem_type = classification['semantic_type']
    conf = classification['confidence']
    print(f'   • {dim_name:20s} → {sem_type:12s} ({conf:.0%} confidence)')
    reasoning = classification["reasoning"]
    if len(reasoning) > 70:
        reasoning = reasoning[:67] + "..."
    print(f'     Reasoning: {reasoning}')

# 2. DETECT HIERARCHIES
print('\n' + '='*80)
print('🧠 STEP 2: DETECTING HIERARCHIES WITH AI')
print('='*80)

prompt2 = f'''Analyze these classified dimensions and detect any natural drill-down hierarchies.

Classified Dimensions:
{json.dumps(classifications, indent=2)}

Look for these hierarchy types:
- Time: Year → Quarter → Month → Day
- Event: Event Type → Event Action
- Object: Object Type → Object Name
- System: Server → Service

Return ONLY a JSON array in this format (no markdown):
[
  {{
    "name": "Event_Hierarchy",
    "type": "Event",
    "confidence": 0.85,
    "levels": [
      {{"dimension": "Event Type", "order": 1}},
      {{"dimension": "Event Action", "order": 2}}
    ]
  }}
]'''

response2 = client.messages.create(
    model='claude-sonnet-4-6',
    max_tokens=2000,
    temperature=0.0,
    messages=[{'role': 'user', 'content': prompt2}]
)

hierarchies_text = response2.content[0].text.strip()
if hierarchies_text.startswith('```'):
    hierarchies_text = '\n'.join(hierarchies_text.split('\n')[1:-1])

hierarchies = json.loads(hierarchies_text)

print(f'\n🏗️ DETECTED HIERARCHIES: {len(hierarchies)} found')
for hierarchy in hierarchies:
    levels = ' → '.join([l['dimension'] for l in hierarchy['levels']])
    print(f'   • {hierarchy["name"]} ({hierarchy["type"]}):')
    print(f'     {levels}')
    print(f'     Confidence: {hierarchy["confidence"]:.0%}')

# 3. TRANSLATE FORMULAS (measures)
print('\n' + '='*80)
print('🧠 STEP 3: TRANSLATING FORMULAS WITH AI')
print('='*80)

formulas = {}
if measures:
    prompt3 = f'''Translate these BusinessObjects measure definitions to SAC (SAP Analytics Cloud) syntax.

Measures:
{json.dumps(measures, indent=2)}

Convert BOBJ aggregation types to SAC syntax:
- COUNT → COUNT([column])
- COUNT_DISTINCT → DISTINCTCOUNT([column])
- SUM → SUM([column])
- AVG → AVERAGE([column])

Return ONLY a JSON object (no markdown):
{{
  "Event Count": {{
    "original": "COUNT(SI_EVENT_ID)",
    "translated": "COUNT([Event_ID])",
    "confidence": 0.95
  }}
}}'''

    response3 = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=2000,
        temperature=0.0,
        messages=[{'role': 'user', 'content': prompt3}]
    )

    formulas_text = response3.content[0].text.strip()
    if formulas_text.startswith('```'):
        formulas_text = '\n'.join(formulas_text.split('\n')[1:-1])

    formulas = json.loads(formulas_text)

    print(f'\n🔄 TRANSLATED FORMULAS: {len(formulas)} measures')
    for formula_name, translation in sorted(formulas.items()):
        print(f'   • {formula_name}:')
        print(f'     Original:   {translation["original"]}')
        print(f'     Translated: {translation["translated"]}')
        print(f'     Confidence: {translation["confidence"]:.0%}')
        print()

print('='*80)
print('✅ AI ENHANCEMENT COMPLETE')
print('='*80)
print(f'\nSummary:')
print(f'   • {len(classifications)} dimensions classified')
print(f'   • {len(hierarchies)} hierarchies detected')
print(f'   • {len(formulas) if measures else 0} formulas translated')
print(f'\n📊 API Usage: ~3 Claude API calls (~$0.02-0.04 cost)')
