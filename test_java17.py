#!/usr/bin/env python3
"""
BREAKTHROUGH TEST #2: Use Java 17 with Information Design Tool SDK
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Use Java 17!
os.environ["PATH"] = "/opt/homebrew/opt/openjdk@17/bin:" + os.environ.get("PATH", "")
os.environ["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"

import jpype
import jpype.imports

def test_with_java17():
    """Test with Java 17 and IDT JARs"""

    print("=" * 80)
    print("🎯 BREAKTHROUGH TEST #2: Java 17 + Information Design Tool")
    print("=" * 80)

    sdk_base = Path(__file__).parent / "backend/app/engines/bobj2sac/sdk/BOBJ_SDK"

    # Collect JARs from BOTH base SDK and IDT
    print("\n1. Collecting JAR files (Java 17 compatible)...")

    jar_locations = [
        sdk_base / "java/lib",
        sdk_base / "Information Design Tool/plugins",
    ]

    all_jars = []
    for location in jar_locations:
        if location.exists():
            jars = list(location.glob("**/*.jar"))
            print(f"   {location.name}: {len(jars)} JARs")
            all_jars.extend(jars)

    print(f"\n   ✓ Total JARs: {len(all_jars)}")

    # Start JVM with Java 17
    print("\n2. Starting JVM with Java 17...")
    print(f"   JAVA_HOME: {os.environ.get('JAVA_HOME')}")

    jpype.startJVM(
        jpype.getDefaultJVMPath(),
        f"-Djava.class.path={':'.join(str(j) for j in all_jars)}",
        "-Xmx2048m"
    )
    print("   ✓ JVM started")

    # Verify Java version
    from java.lang import System
    print(f"   Java version: {System.getProperty('java.version')}")
    print(f"   Java runtime: {System.getProperty('java.runtime.version')}")

    # Now try the universe package
    print("\n3. Importing UniversePackage with Java 17...")

    try:
        from com.businessobjects.mds.universe import UniversePackage, UniverseFactory
        print(f"   ✓✓✓ SUCCESS! UniversePackage imported: {UniversePackage}")

        package = UniversePackage.eINSTANCE
        print(f"   Package NS URI: {package.getNsURI()}")

    except Exception as e:
        print(f"   ✗ Failed: {e}")
        jpype.shutdownJVM()
        return False

    # Try loading the binary file
    print("\n4. Loading .blx file with Java 17 SDK...")

    binary_file = Path("/tmp/universe_test/blx_extracted/BOEXI40-Audit-Oracle.blx")

    try:
        from org.eclipse.emf.common.util import URI
        from org.eclipse.emf.ecore.resource.impl import ResourceSetImpl
        from org.eclipse.emf.ecore import EPackage

        # Register package
        registry = EPackage.Registry.INSTANCE
        registry.put(package.getNsURI(), package)
        print(f"   ✓ Package registered")

        # Create resource set
        resource_set = ResourceSetImpl()
        uri = URI.createFileURI(str(binary_file.absolute()))

        print(f"\n   Loading: {uri}...")

        # Try with auto-detection
        resource = resource_set.getResource(uri, True)

        if resource and resource.getContents() and resource.getContents().size() > 0:
            print(f"\n   ✅✅✅ BREAKTHROUGH! Loaded {resource.getContents().size()} objects!")

            obj = resource.getContents().get(0)
            print(f"\n   Universe object: {obj}")
            print(f"   Type: {type(obj)}")

            # Extract ALL metadata
            print(f"\n   === EXTRACTING METADATA ===")

            if hasattr(obj, 'getBusinessName'):
                name = obj.getBusinessName()
                print(f"   Business Name: {name}")

            if hasattr(obj, 'getDescription'):
                desc = obj.getDescription()
                print(f"   Description: {desc}")

            # Get folders (dimensions/measures are in folders)
            if hasattr(obj, 'getRootFolder'):
                root = obj.getRootFolder()
                print(f"\n   Root Folder: {root}")

                if root and hasattr(root, 'getFolders'):
                    folders = root.getFolders()
                    print(f"   Subfolders count: {folders.size() if folders else 0}")

            # Get all getter methods
            print(f"\n   === ALL PROPERTIES ===")
            for method_name in sorted(dir(obj)):
                if method_name.startswith('get') and not method_name.startswith('get_'):
                    try:
                        method = getattr(obj, method_name)
                        value = method()
                        if value is not None:
                            value_str = str(value)
                            if len(value_str) < 100:
                                print(f"   {method_name}(): {value_str}")
                            else:
                                print(f"   {method_name}(): {value_str[:100]}...")
                    except:
                        pass

            jpype.shutdownJVM()
            return True
        else:
            print(f"   ✗ Resource loaded but has no contents")

    except Exception as e:
        print(f"   ✗ Failed: {e}")
        import traceback
        traceback.print_exc()

    jpype.shutdownJVM()
    return False

if __name__ == "__main__":
    success = test_with_java17()

    if success:
        print("\n" + "=" * 80)
        print("🎉🎉🎉 SOLUTION FOUND!")
        print("=" * 80)
        print("""
THE MISSING PIECE: Java 17!

The Information Design Tool SDK requires Java 17 (class version 61.0).
We were using Java 11 (class version 55.0).

NEXT STEPS:
1. Update sdk_bridge.py to use Java 17
2. Install Java 17 on Render
3. Re-test extraction with full SDK
4. Extract REAL metadata from universes!
""")
    else:
        print("\n" + "=" * 80)
        print("Still investigating...")
        print("=" * 80)

    sys.exit(0 if success else 1)
