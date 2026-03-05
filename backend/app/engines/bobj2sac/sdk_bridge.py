"""
SAP BusinessObjects SDK Integration Layer
Uses JPype to bridge Python with SAP Java SDK

UPDATED: Now includes Information Design Tool SDK with Java 17
"""

import jpype
import jpype.imports
from pathlib import Path
from typing import Optional, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

# SDK location
SDK_DIR = Path(__file__).parent / "sdk" / "BOBJ_SDK"

# Java 17 is required for Information Design Tool SDK
JAVA_17_HOME = "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"

class BOBJSDKBridge:
    """
    Bridge to SAP BusinessObjects Java SDK
    Manages JVM lifecycle and SDK access

    UPDATED: Now uses Java 17 and includes Information Design Tool SDK
    """

    _jvm_started = False

    @classmethod
    def start_jvm(cls, use_idt_sdk: bool = True) -> bool:
        """
        Start Java Virtual Machine with SDK JARs

        Args:
            use_idt_sdk: If True, include Information Design Tool SDK JARs (requires Java 17)

        Returns True if successful
        """
        if cls._jvm_started:
            logger.info("JVM already started")
            return True

        if not SDK_DIR.exists():
            logger.warning(f"SDK directory not found: {SDK_DIR} - operating in placeholder mode")
            return False

        # Collect JAR files from multiple locations
        jar_locations = [
            SDK_DIR / "java" / "lib",
        ]

        if use_idt_sdk:
            # Include Information Design Tool SDK (requires Java 17)
            jar_locations.append(SDK_DIR / "Information Design Tool" / "plugins")

            # Set Java 17 home if available
            if Path(JAVA_17_HOME).exists():
                os.environ["JAVA_HOME"] = JAVA_17_HOME
                os.environ["PATH"] = f"{JAVA_17_HOME}/bin:{os.environ.get('PATH', '')}"
                logger.info(f"Using Java 17: {JAVA_17_HOME}")

        jar_files = []
        for location in jar_locations:
            if location.exists():
                jars = list(location.glob("**/*.jar"))
                logger.info(f"Found {len(jars)} JARs in {location.name}")
                jar_files.extend(jars)

        if not jar_files:
            logger.error(f"No JAR files found in {SDK_DIR}")
            return False

        logger.info(f"Total: {len(jar_files)} SDK JAR files")

        try:
            # Start JVM with SDK jars
            jpype.startJVM(
                jpype.getDefaultJVMPath(),
                f"-Djava.class.path={':'.join(str(jar) for jar in jar_files)}",
                "-Xmx2048m",
                convertStrings=True
            )

            cls._jvm_started = True

            # Log Java version
            from java.lang import System
            java_version = System.getProperty("java.version")
            logger.info(f"✓ JVM started successfully with Java {java_version}")
            logger.info(f"✓ Loaded {len(jar_files)} SDK JARs")

            # Verify SDK classes are accessible
            cls._verify_sdk_classes()

            return True

        except Exception as e:
            logger.error(f"Failed to start JVM: {e}")
            return False

    @classmethod
    def _verify_sdk_classes(cls):
        """Verify SDK classes are accessible"""
        try:
            # Try to import core SDK classes
            from com.businessobjects.rebean.wi import ReportEngines
            from com.crystaldecisions.sdk.framework import CrystalEnterprise

            logger.info("✓ SDK classes verified and accessible")

        except Exception as e:
            logger.warning(f"Some SDK classes may not be accessible: {e}")

    @classmethod
    def shutdown_jvm(cls):
        """Shutdown JVM (call on app exit)"""
        if cls._jvm_started:
            jpype.shutdownJVM()
            cls._jvm_started = False
            logger.info("JVM shutdown")

    @classmethod
    def is_running(cls) -> bool:
        """Check if JVM is running"""
        return cls._jvm_started and jpype.isJVMStarted()


class UNVParser:
    """
    Parse BOBJ Universe (.unv) files using SAP SDK
    """

    def __init__(self):
        if not BOBJSDKBridge.is_running():
            if not BOBJSDKBridge.start_jvm():
                raise RuntimeError("Failed to start JVM with SAP SDK")

    def parse_universe(self, unv_path: Path) -> Dict[str, Any]:
        """
        Parse .unv file and extract metadata

        Returns CIM-compatible dictionary with:
        - universe metadata (name, id, description)
        - tables (name, type, sql)
        - joins (left, right, type, condition)
        - dimensions (name, table, column, description)
        - measures (name, table, column, aggregation, formula)
        - contexts (name, joins) - for resolving ambiguous paths
        - prompts/LOVs (name, type, query, default)
        - connection info (database, server, credentials)
        """

        logger.info(f"Parsing UNV file: {unv_path}")

        try:
            # Import SDK classes
            from com.businessobjects.rebean.wi import ReportEngines
            from com.crystaldecisions.sdk.occa.infostore import IInfoStore

            # Open universe file
            universe = self._open_universe(unv_path)

            # Extract metadata
            cim = {
                "universe": self._extract_universe_metadata(universe),
                "tables": self._extract_tables(universe),
                "joins": self._extract_joins(universe),
                "dimensions": self._extract_dimensions(universe),
                "measures": self._extract_measures(universe),
                "contexts": self._extract_contexts(universe),
                "prompts": self._extract_prompts(universe),
                "connection": self._extract_connection_info(universe)
            }

            logger.info(f"✓ Extracted {len(cim['dimensions'])} dimensions, {len(cim['measures'])} measures")

            return cim

        except Exception as e:
            logger.error(f"Failed to parse UNV file: {e}")
            raise

    def _open_universe(self, unv_path: Path):
        """
        Open universe file using SDK

        UPDATED: Now tries multiple loading strategies:
        1. EMF ResourceSet with auto-detection
        2. Register custom ResourceFactory for .blx/.dfx/.cnx
        3. Try direct binary resource loading
        """
        logger.info(f"Opening universe: {unv_path}")

        try:
            from org.eclipse.emf.common.util import URI
            from org.eclipse.emf.ecore.resource.impl import ResourceSetImpl
            from org.eclipse.emf.ecore import EPackage
            from com.businessobjects.mds.universe import UniversePackage, UniverseFactory

            # Register UniversePackage
            package = UniversePackage.eINSTANCE
            registry = EPackage.Registry.INSTANCE
            registry.put(package.getNsURI(), package)
            logger.info(f"Registered UniversePackage: {package.getNsURI()}")

            # Create resource set
            resource_set = ResourceSetImpl()
            factory_registry = resource_set.getResourceFactoryRegistry()

            # Try to find and register ResourceFactory from IDT SDK
            self._register_universe_resource_factory(factory_registry)

            # Load the universe file
            uri = URI.createFileURI(str(unv_path.absolute()))
            logger.info(f"Loading URI: {uri}")

            resource = resource_set.getResource(uri, True)

            # Get universe from resource
            if resource and resource.getContents() and resource.getContents().size() > 0:
                universe = resource.getContents().get(0)
                logger.info(f"✓ Universe loaded successfully!")
                logger.info(f"  Type: {type(universe)}")
                logger.info(f"  Contents: {resource.getContents().size()} objects")
                return universe
            else:
                raise ValueError(f"Resource loaded but has no contents")

        except Exception as e:
            logger.error(f"Failed to open universe: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def _register_universe_resource_factory(self, factory_registry):
        """
        Try to register ResourceFactory for .blx/.dfx/.cnx files

        Searches for:
        - com.businessobjects.mds.resource.UniverseResourceFactory
        - com.businessobjects.bimodeler.universe.UniverseResourceFactory
        - Other possible ResourceFactory implementations
        """
        possible_factories = [
            "com.businessobjects.mds.resource.UniverseResourceFactory",
            "com.businessobjects.mds.resource.UniverseResourceFactoryImpl",
            "com.businessobjects.mds.resource.impl.ResourceFactoryImpl",
            "com.businessobjects.mds.universe.util.UniverseResourceFactoryImpl",
            "com.businessobjects.bimodeler.universe.UniverseResourceFactory",
            "com.businessobjects.universe.resource.UniverseResourceFactory",
        ]

        ext_map = factory_registry.getExtensionToFactoryMap()

        for factory_class_name in possible_factories:
            try:
                factory_class = jpype.JClass(factory_class_name)
                factory = factory_class()

                # Register for all universe file extensions
                ext_map.put("blx", factory)
                ext_map.put("dfx", factory)
                ext_map.put("cnx", factory)
                ext_map.put("unx", factory)

                logger.info(f"✓ Registered ResourceFactory: {factory_class_name}")
                return True

            except Exception as e:
                # Try next factory
                pass

        logger.warning("Could not find ResourceFactory implementation in SDK")

        # Fallback: register XMI factory for all extensions
        try:
            from org.eclipse.emf.ecore.xmi.impl import XMIResourceFactoryImpl
            factory = XMIResourceFactoryImpl()
            ext_map.put("*", factory)
            logger.info("Registered fallback XMI factory")
        except:
            pass

        return False

    def _extract_universe_metadata(self, universe) -> Dict[str, Any]:
        """Extract universe-level metadata"""
        return {
            "name": universe.getName(),
            "id": universe.getId(),
            "description": universe.getDescription() or "",
            "version": universe.getVersion()
        }

    def _extract_tables(self, universe) -> list:
        """Extract table definitions"""
        tables = []

        for table in universe.getTables():
            tables.append({
                "name": table.getName(),
                "type": table.getType(),  # "table", "view", "derived"
                "sql": table.getSQL() if hasattr(table, 'getSQL') else None,
                "description": table.getDescription() or ""
            })

        return tables

    def _extract_joins(self, universe) -> list:
        """Extract join definitions"""
        joins = []

        for join in universe.getJoins():
            joins.append({
                "left_table": join.getLeftTable().getName(),
                "right_table": join.getRightTable().getName(),
                "type": join.getType(),  # "inner", "left", "right"
                "condition": join.getExpression(),
                "cardinality": join.getCardinality() if hasattr(join, 'getCardinality') else None
            })

        return joins

    def _extract_dimensions(self, universe) -> list:
        """Extract dimension objects"""
        dimensions = []

        for dim in universe.getDimensions():
            dimensions.append({
                "name": dim.getName(),
                "table": dim.getTable().getName() if dim.getTable() else None,
                "column": dim.getColumn(),
                "description": dim.getDescription() or "",
                "type": dim.getType(),
                "qualification": dim.getQualification()  # "dimension", "detail"
            })

        return dimensions

    def _extract_measures(self, universe) -> list:
        """Extract measure objects"""
        measures = []

        for measure in universe.getMeasures():
            measures.append({
                "name": measure.getName(),
                "table": measure.getTable().getName() if measure.getTable() else None,
                "column": measure.getColumn(),
                "aggregation": measure.getAggregation(),  # "SUM", "COUNT", "AVG"
                "formula": measure.getFormula() if hasattr(measure, 'getFormula') else None,
                "description": measure.getDescription() or ""
            })

        return measures

    def _extract_contexts(self, universe) -> list:
        """
        Extract contexts (resolve join ambiguity)
        This is a BOBJ-specific feature that's critical for complex universes
        """
        contexts = []

        if hasattr(universe, 'getContexts'):
            for context in universe.getContexts():
                contexts.append({
                    "name": context.getName(),
                    "joins": [join.getExpression() for join in context.getJoins()],
                    "description": context.getDescription() or ""
                })

        return contexts

    def _extract_prompts(self, universe) -> list:
        """
        Extract prompts and List of Values (LOVs)
        Critical for interactive reports
        """
        prompts = []

        if hasattr(universe, 'getListOfValues'):
            for lov in universe.getListOfValues():
                prompts.append({
                    "name": lov.getName(),
                    "type": lov.getType(),  # "single", "multiple", "cascading"
                    "query": lov.getQuery(),
                    "default_value": lov.getDefaultValue() if hasattr(lov, 'getDefaultValue') else None,
                    "allow_custom": lov.getAllowCustomValues() if hasattr(lov, 'getAllowCustomValues') else False
                })

        return prompts

    def _extract_connection_info(self, universe) -> Dict[str, Any]:
        """Extract database connection information"""
        connection = {}

        if hasattr(universe, 'getConnection'):
            conn = universe.getConnection()
            connection = {
                "type": conn.getType(),
                "database": conn.getDatabase() if hasattr(conn, 'getDatabase') else None,
                "server": conn.getServer() if hasattr(conn, 'getServer') else None,
                "driver": conn.getDriver() if hasattr(conn, 'getDriver') else None
            }

        return connection


class SDKInfo:
    """
    Utility to inspect SDK contents and capabilities
    """

    @staticmethod
    def list_available_classes():
        """List all available SDK classes"""
        if not BOBJSDKBridge.is_running():
            BOBJSDKBridge.start_jvm()

        # Try to discover available classes
        try:
            import jpype.imports

            packages = [
                "com.businessobjects.rebean.wi",
                "com.crystaldecisions.sdk",
                "com.sap.connectivity.cs"
            ]

            for package in packages:
                try:
                    logger.info(f"Package: {package}")
                    # List classes in package
                except Exception as e:
                    logger.warning(f"Could not inspect package {package}: {e}")

        except Exception as e:
            logger.error(f"Failed to list SDK classes: {e}")

    @staticmethod
    def get_sdk_version() -> Optional[str]:
        """Get SAP BOBJ SDK version"""
        if not BOBJSDKBridge.is_running():
            BOBJSDKBridge.start_jvm()

        try:
            # Try to get version from SDK
            from com.crystaldecisions.sdk.framework import CrystalEnterprise
            version = CrystalEnterprise.getVersion()
            return version
        except Exception as e:
            logger.warning(f"Could not determine SDK version: {e}")
            return None
