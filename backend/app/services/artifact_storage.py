"""
Artifact Storage Service
Stores all pipeline artifacts in Neon PostgreSQL database
"""
from pathlib import Path
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.database import Artifact
from app.services.storage_controls import StorageControls
import json
import logging

logger = logging.getLogger(__name__)


class ArtifactStorage:
    """
    Enterprise artifact storage using PostgreSQL
    Replaces filesystem-based storage for Render deployment
    """

    # Artifact type definitions
    TYPE_SAC_MODEL = "sac_model"
    TYPE_DATASPHERE_VIEWS = "datasphere_views"
    TYPE_HANA_SCHEMA = "hana_schema"
    TYPE_LINEAGE_DOT = "lineage_dot"
    TYPE_CIM = "cim"
    TYPE_COVERAGE_REPORT = "coverage_report"
    TYPE_SEMANTIC_DIFF = "semantic_diff"

    # Content type mappings
    CONTENT_TYPES = {
        TYPE_SAC_MODEL: "application/json",
        TYPE_DATASPHERE_VIEWS: "text/sql",
        TYPE_HANA_SCHEMA: "text/sql",
        TYPE_LINEAGE_DOT: "text/plain",
        TYPE_CIM: "application/json",
        TYPE_COVERAGE_REPORT: "application/json",
        TYPE_SEMANTIC_DIFF: "application/json",
    }

    @classmethod
    def save_artifact(
        cls,
        db: Session,
        universe_id: str,
        artifact_type: str,
        content: str,
        version: int = 1
    ) -> Artifact:
        """
        Save or update artifact in database

        Args:
            db: Database session
            universe_id: Universe identifier
            artifact_type: Type of artifact (sac_model, hana_schema, etc)
            content: Artifact content (JSON string, SQL, DOT, etc)
            version: Version number

        Returns:
            Created/updated Artifact object

        Raises:
            ValueError: If artifact size exceeds limit
        """
        # Validate artifact size
        is_valid, error_msg = StorageControls.validate_artifact_size(content)
        if not is_valid:
            logger.error(f"Artifact size validation failed: {error_msg}")
            raise ValueError(error_msg)

        # Check if artifact already exists
        existing = db.query(Artifact).filter_by(
            universe_id=universe_id,
            artifact_type=artifact_type
        ).first()

        if existing:
            # Update existing artifact
            existing.content = content
            existing.file_size = len(content.encode('utf-8'))
            existing.version = version
            logger.info(f"Updated artifact: {universe_id}/{artifact_type} (v{version})")
            db.commit()
            return existing
        else:
            # Create new artifact
            artifact = Artifact(
                universe_id=universe_id,
                artifact_type=artifact_type,
                content=content,
                file_size=len(content.encode('utf-8')),
                content_type=cls.CONTENT_TYPES.get(artifact_type, "text/plain"),
                version=version
            )
            db.add(artifact)
            db.commit()
            logger.info(f"Created artifact: {universe_id}/{artifact_type} (v{version})")
            return artifact

    @classmethod
    def save_json_artifact(
        cls,
        db: Session,
        universe_id: str,
        artifact_type: str,
        data: Dict[str, Any],
        version: int = 1
    ) -> Artifact:
        """Save JSON artifact"""
        content = json.dumps(data, indent=2)
        return cls.save_artifact(db, universe_id, artifact_type, content, version)

    @classmethod
    def save_file_artifact(
        cls,
        db: Session,
        universe_id: str,
        artifact_type: str,
        file_path: Path,
        version: int = 1
    ) -> Artifact:
        """Save artifact from file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return cls.save_artifact(db, universe_id, artifact_type, content, version)

    @classmethod
    def get_artifact(
        cls,
        db: Session,
        universe_id: str,
        artifact_type: str
    ) -> Optional[Artifact]:
        """
        Retrieve artifact from database

        Returns:
            Artifact object or None if not found
        """
        return db.query(Artifact).filter_by(
            universe_id=universe_id,
            artifact_type=artifact_type
        ).first()

    @classmethod
    def get_artifact_content(
        cls,
        db: Session,
        universe_id: str,
        artifact_type: str
    ) -> Optional[str]:
        """Get artifact content as string"""
        artifact = cls.get_artifact(db, universe_id, artifact_type)
        return artifact.content if artifact else None

    @classmethod
    def get_artifact_json(
        cls,
        db: Session,
        universe_id: str,
        artifact_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get artifact content as parsed JSON"""
        content = cls.get_artifact_content(db, universe_id, artifact_type)
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON artifact {universe_id}/{artifact_type}: {e}")
                return None
        return None

    @classmethod
    def list_artifacts(
        cls,
        db: Session,
        universe_id: str
    ) -> List[Artifact]:
        """List all artifacts for a universe"""
        return db.query(Artifact).filter_by(
            universe_id=universe_id
        ).order_by(Artifact.created_at.desc()).all()

    @classmethod
    def artifact_exists(
        cls,
        db: Session,
        universe_id: str,
        artifact_type: str
    ) -> bool:
        """Check if artifact exists"""
        return db.query(Artifact).filter_by(
            universe_id=universe_id,
            artifact_type=artifact_type
        ).count() > 0

    @classmethod
    def delete_artifact(
        cls,
        db: Session,
        universe_id: str,
        artifact_type: str
    ) -> bool:
        """Delete artifact"""
        deleted = db.query(Artifact).filter_by(
            universe_id=universe_id,
            artifact_type=artifact_type
        ).delete()
        db.commit()
        return deleted > 0

    @classmethod
    def delete_all_artifacts(
        cls,
        db: Session,
        universe_id: str
    ) -> int:
        """Delete all artifacts for a universe"""
        deleted = db.query(Artifact).filter_by(
            universe_id=universe_id
        ).delete()
        db.commit()
        logger.info(f"Deleted {deleted} artifacts for universe {universe_id}")
        return deleted
