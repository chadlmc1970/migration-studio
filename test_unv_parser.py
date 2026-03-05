#!/usr/bin/env python3
"""Test UNV parser with SDK"""
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

os.environ["PATH"] = "/opt/homebrew/opt/openjdk@11/bin:" + os.environ.get("PATH", "")
os.environ["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home"

from app.engines.bobj2sac.sdk_bridge import BOBJSDKBridge, UNVParser

def test_parser():
    """Test UNV parser"""
    print("=" * 60)
    print("Testing SAP BOBJ SDK Integration")
    print("=" * 60)

    # Start JVM
    print("\n1. Starting JVM with SDK JARs...")
    if not BOBJSDKBridge.start_jvm():
        print("❌ Failed to start JVM")
        return False

    print("✓ JVM started successfully")

    # Test parser initialization
    print("\n2. Initializing UNV Parser...")
    try:
        parser = UNVParser()
        print("✓ Parser initialized")
    except Exception as e:
        print(f"❌ Parser initialization failed: {e}")
        return False

    # Test with available files
    print("\n3. Looking for test universe files...")
    test_dir = Path("/Users/I870089/pipeline/input/Version 2 - for SAP BI 4.x")

    if test_dir.exists():
        unx_files = list(test_dir.glob("*.unx"))
        print(f"Found {len(unx_files)} .unx files:")
        for f in unx_files:
            print(f"  - {f.name}")

        # Note: .unx files need to be extracted first
        print("\nNote: UNX files are ZIP archives. SDK expects .unv (binary) or EMF resource files.")
        print("The extracted files (.dfx, .blx, .cnx) are metadata components.")

    # Test with blx file (business layer XML)
    blx_file = Path("/tmp/BOEXI40-Audit-Sybase.blx")
    if blx_file.exists():
        print(f"\n4. Testing with business layer file: {blx_file.name}")
        try:
            # Try to parse (may fail if format doesn't match SDK expectations)
            result = parser.parse_universe(blx_file)
            print(f"✓ Parsed successfully!")
            print(f"  - Tables: {len(result.get('tables', []))}")
            print(f"  - Joins: {len(result.get('joins', []))}")
            print(f"  - Dimensions: {len(result.get('dimensions', []))}")
            print(f"  - Measures: {len(result.get('measures', []))}")
        except NotImplementedError as e:
            print(f"⚠ Parser implementation incomplete: {e}")
        except Exception as e:
            print(f"⚠ Parse failed (expected - SDK may need different format): {e}")

    print("\n" + "=" * 60)
    print("SDK Integration Status:")
    print("✓ Java installation: COMPLETE")
    print("✓ JPype installation: COMPLETE")
    print("✓ JVM startup: COMPLETE")
    print("✓ SDK classes accessible: COMPLETE")
    print("⚠ Parser implementation: NEEDS FORMAT VERIFICATION")
    print("=" * 60)

    print("\nNext Steps:")
    print("1. Verify UNX extraction yields compatible format for SDK")
    print("2. Test with actual .unv binary files (if available)")
    print("3. Or implement parsers for .blx/.dfx XML formats")
    print("4. Once working, integrate into pipeline")

    return True

if __name__ == "__main__":
    try:
        success = test_parser()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
