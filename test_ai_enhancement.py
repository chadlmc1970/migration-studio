#!/usr/bin/env python3
"""Test AI-powered semantic enhancement"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.engines.cim_transform.ai.semantic_enhancer import SemanticEnhancer
from app.engines.bobj2sac.io.unv import extract_unv
from app.engines.bobj2sac.util.logging import ConversionLogger
import json

def test_ai_enhancement():
    """Test semantic enhancement on Oracle universe"""

    # Extract CIM from BOEXI40-Audit-Oracle
    unv_file = Path("/Users/I870089/pipeline/input/Version 2 - for SAP BI 4.x/BOEXI40-Audit-Oracle.unx")
    output_dir = Path("/tmp/ai_test_output")
    output_dir.mkdir(exist_ok=True)

    logger = ConversionLogger(output_dir / "test.log")

    # Extract CIM
    print("\n" + "="*80)
    print("EXTRACTING UNIVERSE METADATA")
    print("="*80)
    cim = extract_unv(unv_file, output_dir, logger)

    # Convert CIM to dict for enhancement
    cim_dict = cim.model_dump() if hasattr(cim, 'model_dump') else cim.dict()

    # Enhance with AI
    print("\n" + "="*80)
    print("TESTING AI SEMANTIC ENHANCEMENT")
    print("="*80)

    enhancer = SemanticEnhancer()
    enhanced_cim = enhancer.enhance_cim(cim_dict)

    # Display results
    ai = enhanced_cim.get("ai_enhancements", {})

    print(f"\n✓ AI Enhancement Complete")
    print(f"\n📊 Dimension Classifications:")
    for dim_name, classification in ai.get("dimension_classifications", {}).items():
        print(f"   {dim_name}: {classification['semantic_type']} (confidence: {classification['confidence']:.2f})")

    print(f"\n🏗️ Detected Hierarchies: {len(ai.get('detected_hierarchies', []))}")
    for hierarchy in ai.get("detected_hierarchies", []):
        levels = " → ".join([f"{l['dimension']}" for l in hierarchy['levels']])
        print(f"   {hierarchy['name']} ({hierarchy['type']}): {levels}")
        print(f"      Confidence: {hierarchy['confidence']:.2f}")

    print(f"\n🔄 Translated Formulas: {len(ai.get('translated_formulas', {}))}")
    for formula_name, translation in ai.get("translated_formulas", {}).items():
        print(f"   {formula_name}:")
        print(f"      Original: {translation['original']}")
        print(f"      Translated: {translation['translated']}")
        print(f"      Confidence: {translation['confidence']:.2f}")

    # Save enhanced CIM
    output_file = output_dir / "enhanced_cim.json"
    with open(output_file, 'w') as f:
        json.dump(enhanced_cim, f, indent=2)

    print(f"\n✅ Enhanced CIM saved to: {output_file}")

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✓ Dimensions classified: {len(ai.get('dimension_classifications', {}))}")
    print(f"✓ Hierarchies detected: {len(ai.get('detected_hierarchies', []))}")
    print(f"✓ Formulas translated: {len(ai.get('translated_formulas', {}))}")
    print(f"✓ AI enabled: {ai.get('enabled', False)}")

    return True

if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n" + "="*80)
        print("❌ ANTHROPIC_API_KEY not set!")
        print("="*80)
        print("\nPlease set your API key:")
        print("  export ANTHROPIC_API_KEY='sk-ant-api03-...'")
        print("\nGet your API key from: https://console.anthropic.com/")
        print("="*80 + "\n")
        sys.exit(1)

    try:
        success = test_ai_enhancement()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
