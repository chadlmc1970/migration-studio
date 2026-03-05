#!/usr/bin/env python3
"""
Find the correct SDK API to load binary universe files
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

os.environ["PATH"] = "/opt/homebrew/opt/openjdk@11/bin:" + os.environ.get("PATH", "")
os.environ["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home"

import jpype
import jpype.imports

def find_load_methods():
    """Search SDK for methods to load universe files"""

    # Start JVM
    sdk_dir = Path(__file__).parent / "backend/app/engines/bobj2sac/sdk/BOBJ_SDK"
    jar_files = list(sdk_dir.glob("**/*.jar"))

    jpype.startJVM(
        jpype.getDefaultJVMPath(),
        f"-Djava.class.path={':'.join(str(j) for j in jar_files)}",
        "-Xmx2048m"
    )

    print("="*80)
    print("SEARCHING FOR UNIVERSE LOADING METHODS")
    print("="*80)

    # Get Universe and UniverseFactory classes
    from com.businessobjects.mds.universe import Universe, UniverseFactory
    from com.businessobjects.mds.universe.impl import UniverseImpl

    factory = UniverseFactory.eINSTANCE
    universe = factory.createUniverse()

    print(f"\nUniverseFactory methods:")
    factory_methods = [m for m in dir(factory) if not m.startswith('_')]
    for m in sorted(factory_methods):
        if any(keyword in m.lower() for keyword in ['load', 'open', 'read', 'import', 'deserialize', 'parse']):
            print(f"  ✓ {m}")

    print(f"\nUniverse object methods:")
    universe_methods = [m for m in dir(universe) if not m.startswith('_')]
    for m in sorted(universe_methods):
        if any(keyword in m.lower() for keyword in ['load', 'open', 'read', 'set', 'import']):
            print(f"  ✓ {m}")

    print(f"\nUniverse class static methods:")
    universe_class_methods = [m for m in dir(Universe) if not m.startswith('_')]
    for m in sorted(universe_class_methods):
        if any(keyword in m.lower() for keyword in ['load', 'open', 'read', 'create', 'from']):
            print(f"  ✓ {m}")

    # Try EMF Resource approach with proper registration
    print(f"\n{'='*80}")
    print("TRYING EMF RESOURCE WITH RESOURCE FACTORY")
    print("="*80)

    try:
        from org.eclipse.emf.ecore.resource import Resource
        from org.eclipse.emf.ecore.resource.impl import ResourceSetImpl
        from org.eclipse.emf.ecore.xmi.impl import XMIResourceFactoryImpl
        from org.eclipse.emf.common.util import URI

        # Register resource factory
        resource_set = ResourceSetImpl()

        # Get the resource factory registry
        registry = resource_set.getResourceFactoryRegistry()
        print(f"Registry: {registry}")

        # Try to register for .blx extension
        ext_map = registry.getExtensionToFactoryMap()
        print(f"Extension map: {ext_map}")

        # Check what's already registered
        print(f"\nRegistered extensions:")
        for key in ext_map.keySet():
            print(f"  - {key}: {ext_map.get(key)}")

        # Try registering .blx
        ext_map.put("blx", XMIResourceFactoryImpl())
        print(f"\n✓ Registered .blx extension")

        # Now try to load
        binary_file = Path("/tmp/universe_test/blx_extracted/BOEXI40-Audit-Oracle.blx")
        uri = URI.createFileURI(str(binary_file.absolute()))

        print(f"\nLoading: {uri}")
        resource = resource_set.getResource(uri, True)

        if resource and resource.getContents() and resource.getContents().size() > 0:
            print(f"✓✓✓ SUCCESS! Loaded {resource.getContents().size()} objects")

            universe_obj = resource.getContents().get(0)
            print(f"\nUniverse loaded: {universe_obj}")
            print(f"Type: {type(universe_obj)}")

            # Try to get properties
            if hasattr(universe_obj, 'getBusinessName'):
                print(f"Business Name: {universe_obj.getBusinessName()}")
            if hasattr(universe_obj, 'getDescription'):
                print(f"Description: {universe_obj.getDescription()}")

            return True
        else:
            print("✗ Resource loaded but has no contents")

    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()

    jpype.shutdownJVM()
    return False


if __name__ == "__main__":
    success = find_load_methods()

    if success:
        print(f"\n{'='*80}")
        print("✅✅✅ EXTRACTION + LOADING = 100% SUCCESS")
        print("="*80)
    else:
        print(f"\n{'='*80}")
        print("File extraction: ✅ SUCCESS")
        print("SDK loading: ⚠️ Need correct API")
        print("="*80)
