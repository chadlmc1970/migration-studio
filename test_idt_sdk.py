#!/usr/bin/env python3
"""
BREAKTHROUGH TEST: Use Information Design Tool SDK JARs
The IDT has universe-specific JARs we weren't loading!
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

os.environ["PATH"] = "/opt/homebrew/opt/openjdk@11/bin:" + os.environ.get("PATH", "")
os.environ["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home"

import jpype
import jpype.imports

def test_with_idt_jars():
    """Test with Information Design Tool JARs included"""

    print("=" * 80)
    print("🎯 BREAKTHROUGH TEST: Information Design Tool JARs")
    print("=" * 80)

    sdk_base = Path(__file__).parent / "backend/app/engines/bobj2sac/sdk/BOBJ_SDK"

    # Collect ALL JARs including Information Design Tool
    print("\n1. Collecting JAR files...")

    jar_locations = [
        sdk_base / "java/lib",
        sdk_base / "java/lib/external",
        sdk_base / "Information Design Tool/plugins",  # ← NEW!
    ]

    all_jars = []
    for location in jar_locations:
        if location.exists():
            jars = list(location.glob("**/*.jar"))
            print(f"   {location.name}: {len(jars)} JARs")
            all_jars.extend(jars)

    print(f"\n   ✓ Total JARs: {len(all_jars)}")

    # Start JVM with ALL JARs
    print("\n2. Starting JVM with Information Design Tool SDK...")
    jpype.startJVM(
        jpype.getDefaultJVMPath(),
        f"-Djava.class.path={':'.join(str(j) for j in all_jars)}",
        "-Xmx2048m"
    )
    print("   ✓ JVM started")

    # Try to import the MDS resource classes
    print("\n3. Testing com.businessobjects.mds.resource package...")

    try:
        # This is the key package we found!
        from com.businessobjects.mds.resource import ResourceFactory
        print(f"   ✓✓✓ FOUND ResourceFactory: {ResourceFactory}")

        methods = [m for m in dir(ResourceFactory) if not m.startswith('_')]
        print(f"   Methods: {methods[:15]}")

    except Exception as e:
        print(f"   ✗ ResourceFactory not found: {e}")

    # Try universe migration package
    print("\n4. Testing com.businessobjects.universe.migration...")

    try:
        import com.businessobjects.universe.migration as migration
        print(f"   ✓ Migration package found: {migration}")

        # Look for loader/reader classes
        classes = dir(migration)
        relevant = [c for c in classes if any(k in c.lower() for k in ['load', 'read', 'open', 'parse'])]
        if relevant:
            print(f"   Relevant classes: {relevant}")

    except Exception as e:
        print(f"   ✗ Migration package: {e}")

    # Try bimodeler universe package
    print("\n5. Testing com.businessobjects.bimodeler.universe...")

    try:
        import com.businessobjects.bimodeler.universe as bimodeler
        print(f"   ✓ Bimodeler package found: {bimodeler}")

        classes = dir(bimodeler)
        relevant = [c for c in classes if any(k in c.lower() for k in ['load', 'read', 'resource', 'factory'])]
        if relevant:
            print(f"   Relevant classes: {relevant}")

    except Exception as e:
        print(f"   ✗ Bimodeler package: {e}")

    # Now try loading with the full classpath
    print("\n6. Attempting to load .blx file with IDT SDK...")

    binary_file = Path("/tmp/universe_test/blx_extracted/BOEXI40-Audit-Oracle.blx")

    try:
        from org.eclipse.emf.common.util import URI
        from org.eclipse.emf.ecore.resource.impl import ResourceSetImpl
        from com.businessobjects.mds.universe import UniversePackage

        # Register package
        package = UniversePackage.eINSTANCE
        from org.eclipse.emf.ecore import EPackage
        registry = EPackage.Registry.INSTANCE
        registry.put(package.getNsURI(), package)

        # Create resource set
        resource_set = ResourceSetImpl()

        # Check what factories are now available
        factory_registry = resource_set.getResourceFactoryRegistry()

        print(f"\n   Checking registered factories...")
        ext_map = factory_registry.getExtensionToFactoryMap()
        print(f"   Extension map size: {ext_map.size()}")

        for key in ext_map.keySet():
            factory = ext_map.get(key)
            print(f"     • .{key} → {factory.getClass().getName()}")

        # Try to find and register the MDS resource factory
        print(f"\n   Searching for MDS ResourceFactory implementation...")

        try:
            # Try different possible class names
            possible_factories = [
                "com.businessobjects.mds.resource.UniverseResourceFactory",
                "com.businessobjects.mds.resource.UniverseResourceFactoryImpl",
                "com.businessobjects.mds.resource.impl.ResourceFactoryImpl",
                "com.businessobjects.mds.universe.util.UniverseResourceFactoryImpl",
                "com.businessobjects.bimodeler.universe.UniverseResourceFactory",
            ]

            for factory_class in possible_factories:
                try:
                    cls = jpype.JClass(factory_class)
                    print(f"   ✓✓✓ FOUND: {factory_class}")

                    # Try to instantiate
                    factory = cls()
                    print(f"   ✓ Instantiated: {factory}")

                    # Register for .blx/.dfx/.cnx
                    ext_map.put("blx", factory)
                    ext_map.put("dfx", factory)
                    ext_map.put("cnx", factory)
                    print(f"   ✓ Registered for .blx/.dfx/.cnx")

                    # NOW TRY TO LOAD!
                    uri = URI.createFileURI(str(binary_file.absolute()))
                    print(f"\n   Loading: {uri}...")

                    resource = resource_set.getResource(uri, True)

                    if resource and resource.getContents() and resource.getContents().size() > 0:
                        print(f"\n   ✅✅✅ SUCCESS! Loaded {resource.getContents().size()} objects!")

                        obj = resource.getContents().get(0)
                        print(f"\n   Universe object: {obj}")
                        print(f"   Type: {type(obj)}")

                        # Try to access properties
                        if hasattr(obj, 'getBusinessName'):
                            print(f"   Business Name: {obj.getBusinessName()}")
                        if hasattr(obj, 'getDescription'):
                            print(f"   Description: {obj.getDescription()}")

                        # Get all properties
                        print(f"\n   Available methods:")
                        methods = [m for m in dir(obj) if m.startswith('get')]
                        for m in sorted(methods)[:20]:
                            try:
                                val = getattr(obj, m)()
                                if val is not None:
                                    print(f"     • {m}(): {val}")
                            except:
                                pass

                        jpype.shutdownJVM()
                        return True

                except Exception as e:
                    pass

        except Exception as e:
            print(f"   ✗ Factory search failed: {e}")

    except Exception as e:
        print(f"   ✗ Load failed: {e}")
        import traceback
        traceback.print_exc()

    jpype.shutdownJVM()

    print("\n" + "=" * 80)
    print("🎯 RESULT")
    print("=" * 80)
    print("""
The Information Design Tool SDK has additional JARs that might contain:
- com.businessobjects.mds.resource.jar
- com.businessobjects.bimodeler.universe.jar
- com.businessobjects.universe.migration.jar

These are MORE COMPLETE universe handling packages than the basic MDS SDK.

If the ResourceFactory still isn't found, then the binary format likely requires:
- Universe Designer Tool running (desktop application)
- OR CMS server connection for decryption
- OR these are export artifacts that need re-export in different format
""")

    return False

if __name__ == "__main__":
    success = test_with_idt_jars()
    sys.exit(0 if success else 1)
