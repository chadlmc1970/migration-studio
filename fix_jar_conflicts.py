#!/usr/bin/env python3
"""
BREAKTHROUGH ATTEMPT: Fix JAR Conflicts
Remove duplicate EMF JARs and use only the latest versions
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Java 17
os.environ["PATH"] = "/opt/homebrew/opt/openjdk@17/bin:" + os.environ.get("PATH", "")
os.environ["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"

import jpype
import jpype.imports

def filter_jars(jar_files):
    """
    Remove duplicate/conflicting EMF JARs
    Keep only the newest versions
    """
    # Dictionary to track the newest version of each JAR
    jar_dict = {}

    for jar in jar_files:
        name = jar.name

        # Extract base name and version
        if "org.eclipse.emf.ecore_" in name:
            # Keep only the newest version (2.16.x over 2.4.x)
            if "2.4." in name:
                print(f"   ❌ Skipping old EMF: {name}")
                continue
        elif "org.eclipse.emf.ecore.xmi_" in name:
            if "2.4." in name:
                print(f"   ❌ Skipping old XMI: {name}")
                continue
        elif "org.eclipse.emf.common_" in name:
            if "2.4." in name:
                print(f"   ❌ Skipping old common: {name}")
                continue
        elif "org.eclipse.equinox" in name:
            if "3.4." in name:
                print(f"   ❌ Skipping old equinox: {name}")
                continue
        elif "org.eclipse.osgi_" in name:
            if "3.4." in name:
                print(f"   ❌ Skipping old osgi: {name}")
                continue

        jar_dict[str(jar)] = jar

    return list(jar_dict.values())

def test_with_filtered_jars():
    """Test with duplicate JARs removed"""

    print("=" * 80)
    print("🔧 FIXING JAR CONFLICTS")
    print("=" * 80)

    sdk_base = Path(__file__).parent / "backend/app/engines/bobj2sac/sdk/BOBJ_SDK"

    # Collect all JARs
    print("\n1. Collecting JARs from base SDK...")
    base_jars = list((sdk_base / "java/lib").glob("**/*.jar"))
    print(f"   Found: {len(base_jars)} JARs")

    # Filter out duplicates
    print("\n2. Filtering duplicate/old EMF JARs...")
    filtered_jars = filter_jars(base_jars)
    removed = len(base_jars) - len(filtered_jars)
    print(f"   ✓ Removed {removed} duplicate JARs")
    print(f"   ✓ Kept {len(filtered_jars)} JARs")

    # Start JVM
    print("\n3. Starting JVM with filtered classpath...")
    try:
        jpype.startJVM(
            jpype.getDefaultJVMPath(),
            f"-Djava.class.path={':'.join(str(j) for j in filtered_jars)}",
            "-Xmx2048m"
        )

        from java.lang import System
        print(f"   ✓ Java {System.getProperty('java.version')}")

    except Exception as e:
        print(f"   ❌ JVM startup failed: {e}")
        return False

    # Try Universe Package
    print("\n4. Testing UniversePackage import...")
    try:
        from com.businessobjects.mds.universe import UniversePackage, UniverseFactory
        print(f"   ✓✓✓ SUCCESS! UniversePackage imported!")
        print(f"   NS URI: {UniversePackage.eINSTANCE.getNsURI()}")

        # Now try loading a file
        print("\n5. Loading binary .blx file...")
        binary_file = Path("/tmp/universe_test/blx_extracted/BOEXI40-Audit-Oracle.blx")

        from org.eclipse.emf.common.util import URI
        from org.eclipse.emf.ecore.resource.impl import ResourceSetImpl
        from org.eclipse.emf.ecore import EPackage

        # Register package
        package = UniversePackage.eINSTANCE
        registry = EPackage.Registry.INSTANCE
        registry.put(package.getNsURI(), package)

        # Load
        resource_set = ResourceSetImpl()
        uri = URI.createFileURI(str(binary_file.absolute()))

        print(f"   Loading: {binary_file.name}...")
        resource = resource_set.getResource(uri, True)

        if resource and resource.getContents() and resource.getContents().size() > 0:
            print(f"\n   🎉🎉🎉 BREAKTHROUGH! Loaded {resource.getContents().size()} objects!")

            universe = resource.getContents().get(0)
            print(f"\n   Universe: {universe}")
            print(f"   Type: {type(universe)}")

            # Extract metadata
            print(f"\n6. Extracting metadata...")
            for method_name in dir(universe):
                if method_name.startswith('get') and not method_name.startswith('get_'):
                    try:
                        method = getattr(universe, method_name)
                        value = method()
                        if value is not None:
                            val_str = str(value)
                            if len(val_str) < 200:
                                print(f"   {method_name}(): {val_str}")
                    except:
                        pass

            jpype.shutdownJVM()
            return True
        else:
            print(f"   ⚠️ Resource loaded but empty")

    except Exception as e:
        print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()

    jpype.shutdownJVM()
    return False

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 BREAKTHROUGH ATTEMPT: Fix JAR Signature Conflicts")
    print("=" * 80)

    success = test_with_filtered_jars()

    if success:
        print("\n" + "=" * 80)
        print("✅✅✅ BREAKTHROUGH ACHIEVED!")
        print("=" * 80)
        print("""
Solution: Remove duplicate/old EMF JARs

Next steps:
1. Update sdk_bridge.py to filter JARs
2. Test with all universes
3. Deploy to production
4. Extract REAL metadata!
""")
    else:
        print("\n" + "=" * 80)
        print("⚠️ Still investigating...")
        print("=" * 80)

    sys.exit(0 if success else 1)
