"""
SAP BusinessObjects SDK Integration Layer
Uses JPype to bridge Python with SAP Java SDK
"""

import jpype
import jpype.imports
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# SDK location
SDK_DIR = Path(__file__).parent / "sdk" / "BOBJ_SDK"

class BOBJSDKBridge:
    """
    Bridge to SAP BusinessObjects Java SDK
    Manages JVM lifecycle and SDK access
    """

    _jvm_started = False

    @classmethod
    def start_jvm(cls) -> bool:
        """
        Start Java Virtual Machine with SDK JARs
        Returns True if successful
        """
        if cls._jvm_started:
            logger.info("JVM already started")
            return True

        if not SDK_DIR.exists():
            logger.error(f"SDK directory not found: {SDK_DIR}")
            return False

        # Find all JAR files
        jar_files = list(SDK_DIR.glob("**/*.jar"))

        if not jar_files:
            logger.error(f"No JAR files found in {SDK_DIR}")
            return False

        logger.info(f"Found {len(jar_files)} SDK JAR files")

        # Build classpath
        classpath = ":".join(str(jar) for jar in jar_files)

        try:
            # Start JVM with SDK jars
            jpype.startJVM(
                classpath=[str(jar) for jar in jar_files],
                convertStrings=True
            )

            cls._jvm_started = True
            logger.info("✓ JVM started successfully with SAP BOBJ SDK")

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
        """Open universe file using SDK"""
        logger.info(f"Opening universe: {unv_path}")

        try:
            from org.eclipse.emf.common.util import URI
            from org.eclipse.emf.ecore.resource.impl import ResourceSetImpl
            from com.businessobjects.mds.universe import UniverseFactory

            # Create resource set and load universe
            resource_set = ResourceSetImpl()
            uri = URI.createFileURI(str(unv_path.absolute()))
            resource = resource_set.getResource(uri, True)

            # Get universe from resource
            if resource and resource.getContents() and resource.getContents().size() > 0:
                universe = resource.getContents().get(0)
                logger.info(f"✓ Universe loaded: {universe}")
                return universe
            else:
                raise ValueError(f"No universe found in {unv_path}")

        except Exception as e:
            logger.error(f"Failed to open universe: {e}")
            raise

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
