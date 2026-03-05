#!/usr/bin/env python3
"""Test SDK JVM startup and discover universe classes"""
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

os.environ["PATH"] = "/opt/homebrew/opt/openjdk@11/bin:" + os.environ.get("PATH", "")
os.environ["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home"

import jpype
import jpype.imports

def test_jvm_startup():
    """Test JVM startup with all SDK JARs"""
    sdk_dir = Path(__file__).parent / "backend/app/engines/bobj2sac/sdk/BOBJ_SDK"

    # Collect all JAR files
    jar_files = []
    for pattern in ["**/*.jar"]:
        jar_files.extend(sdk_dir.glob(pattern))

    print(f"✓ Found {len(jar_files)} JAR files in SDK")

    # Build classpath
    classpath = ":".join(str(jar) for jar in jar_files)

    # Start JVM
    print("Starting JVM with SDK classpath...")
    jpype.startJVM(
        jpype.getDefaultJVMPath(),
        f"-Djava.class.path={classpath}",
        "-Xmx2048m"
    )

    print("✓ JVM started successfully")

    # Try to discover universe-related classes
    print("\n=== Discovering SDK Classes ===")

    # Common package patterns from SAP BusinessObjects
    packages_to_try = [
        "com.businessobjects.rebean.wi",
        "com.crystaldecisions.sdk.occa.universe",
        "com.sap.connectivity.cs",
        "com.businessobjects.mds.universe"
    ]

    for pkg in packages_to_try:
        print(f"\nTrying package: {pkg}")
        try:
            # Try different class names
            for cls_name in ["Universe", "IUniverse", "UniverseFactory", "BusinessLayer"]:
                full_name = f"{pkg}.{cls_name}"
                try:
                    cls = jpype.JClass(full_name)
                    print(f"  ✓ Found: {full_name}")
                    # List methods
                    methods = [m for m in dir(cls) if not m.startswith("_")]
                    print(f"    Methods: {', '.join(methods[:10])}")
                except:
                    pass
        except Exception as e:
            pass

    print("\n=== Testing Universe Loading ===")

    # Try to load a test universe file
    test_unv = Path("/Users/I870089/pipeline/input/Version 2 - for SAP BI 4.x")
    if test_unv.exists():
        unx_files = list(test_unv.glob("*.unx"))
        if unx_files:
            print(f"Found {len(unx_files)} .unx files to test")

    jpype.shutdownJVM()
    print("\n✓ JVM shutdown complete")

if __name__ == "__main__":
    try:
        test_jvm_startup()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
