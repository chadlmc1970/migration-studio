"""
Storage Controls for Neon Database
Prevents unbounded growth and provides cleanup utilities
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.database import Artifact, Universe, Run, Event
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class StorageControls:
    """Database storage controls and cleanup utilities"""

    # Size limits (in bytes)
    MAX_ARTIFACT_SIZE = 10 * 1024 * 1024  # 10 MB per artifact
    MAX_TOTAL_DB_SIZE = 500 * 1024 * 1024  # 500 MB total (well under Neon free tier 512 MB)
    MAX_UNIVERSE_ARTIFACTS = 20  # Max artifacts per universe (prevents runaway versioning)

    # Retention policies (in days)
    EVENT_RETENTION_DAYS = 30  # Keep events for 30 days
    RUN_RETENTION_DAYS = 90  # Keep run records for 90 days
    ARTIFACT_VERSION_LIMIT = 3  # Keep only last 3 versions of each artifact type

    @classmethod
    def get_storage_stats(cls, db: Session) -> dict:
        """Get current database storage statistics"""

        # Get artifact storage by type
        artifact_stats = db.query(
            Artifact.artifact_type,
            func.count(Artifact.id).label('count'),
            func.sum(Artifact.file_size).label('total_size')
        ).group_by(Artifact.artifact_type).all()

        artifact_breakdown = {}
        total_artifact_size = 0
        for stat in artifact_stats:
            size = stat.total_size or 0
            artifact_breakdown[stat.artifact_type] = {
                'count': stat.count,
                'size_bytes': size,
                'size_mb': round(size / (1024 * 1024), 2)
            }
            total_artifact_size += size

        # Get other table counts
        universe_count = db.query(Universe).count()
        run_count = db.query(Run).count()
        event_count = db.query(Event).count()

        # Estimate total DB size (rough approximation)
        estimated_total = total_artifact_size  # Artifacts are the main storage

        return {
            'total_size_bytes': estimated_total,
            'total_size_mb': round(estimated_total / (1024 * 1024), 2),
            'max_size_mb': cls.MAX_TOTAL_DB_SIZE / (1024 * 1024),
            'usage_percent': round((estimated_total / cls.MAX_TOTAL_DB_SIZE) * 100, 2),
            'artifacts': artifact_breakdown,
            'counts': {
                'universes': universe_count,
                'artifacts': sum(s.count for s in artifact_stats),
                'runs': run_count,
                'events': event_count
            },
            'warnings': cls._get_warnings(estimated_total, db)
        }

    @classmethod
    def _get_warnings(cls, total_size: int, db: Session) -> list:
        """Generate storage warnings"""
        warnings = []

        usage_percent = (total_size / cls.MAX_TOTAL_DB_SIZE) * 100
        if usage_percent > 80:
            warnings.append(f"Database storage is {usage_percent:.1f}% full - cleanup recommended")
        elif usage_percent > 60:
            warnings.append(f"Database storage is {usage_percent:.1f}% full - monitor closely")

        # Check for excessive artifacts per universe
        excessive = db.query(Universe.id, func.count(Artifact.id).label('artifact_count'))\
            .join(Artifact)\
            .group_by(Universe.id)\
            .having(func.count(Artifact.id) > cls.MAX_UNIVERSE_ARTIFACTS).all()

        if excessive:
            warnings.append(f"{len(excessive)} universes have excessive artifacts (>{cls.MAX_UNIVERSE_ARTIFACTS})")

        return warnings

    @classmethod
    def validate_artifact_size(cls, content: str) -> tuple[bool, str]:
        """Validate artifact size before saving"""
        size = len(content.encode('utf-8'))

        if size > cls.MAX_ARTIFACT_SIZE:
            size_mb = size / (1024 * 1024)
            max_mb = cls.MAX_ARTIFACT_SIZE / (1024 * 1024)
            return False, f"Artifact too large: {size_mb:.2f} MB exceeds limit of {max_mb:.2f} MB"

        return True, "OK"

    @classmethod
    def cleanup_old_events(cls, db: Session, days: int = None) -> int:
        """Delete events older than retention period"""
        days = days or cls.EVENT_RETENTION_DAYS
        cutoff = datetime.utcnow() - timedelta(days=days)

        deleted = db.query(Event).filter(Event.timestamp < cutoff).delete()
        db.commit()

        logger.info(f"Deleted {deleted} events older than {days} days")
        return deleted

    @classmethod
    def cleanup_old_runs(cls, db: Session, days: int = None) -> int:
        """Delete run records older than retention period"""
        days = days or cls.RUN_RETENTION_DAYS
        cutoff = datetime.utcnow() - timedelta(days=days)

        deleted = db.query(Run).filter(Run.started_at < cutoff).delete()
        db.commit()

        logger.info(f"Deleted {deleted} run records older than {days} days")
        return deleted

    @classmethod
    def cleanup_old_artifact_versions(cls, db: Session, keep_versions: int = None) -> int:
        """Keep only the latest N versions of each artifact type per universe"""
        keep_versions = keep_versions or cls.ARTIFACT_VERSION_LIMIT
        deleted_count = 0

        # Get all universe/artifact_type combinations
        combos = db.query(Artifact.universe_id, Artifact.artifact_type)\
            .distinct().all()

        for universe_id, artifact_type in combos:
            # Get artifacts ordered by created_at desc
            artifacts = db.query(Artifact)\
                .filter_by(universe_id=universe_id, artifact_type=artifact_type)\
                .order_by(Artifact.created_at.desc())\
                .all()

            # Delete all except the latest N versions
            if len(artifacts) > keep_versions:
                to_delete = artifacts[keep_versions:]
                for artifact in to_delete:
                    db.delete(artifact)
                    deleted_count += 1

        db.commit()
        logger.info(f"Deleted {deleted_count} old artifact versions (kept {keep_versions} per type)")
        return deleted_count

    @classmethod
    def cleanup_orphaned_universes(cls, db: Session) -> int:
        """Delete universes with no artifacts (failed uploads)"""
        # Find universes with no artifacts
        orphaned = db.query(Universe)\
            .outerjoin(Artifact)\
            .group_by(Universe.id)\
            .having(func.count(Artifact.id) == 0)\
            .all()

        deleted_count = 0
        for universe in orphaned:
            db.delete(universe)
            deleted_count += 1

        db.commit()
        logger.info(f"Deleted {deleted_count} orphaned universes (no artifacts)")
        return deleted_count

    @classmethod
    def full_cleanup(cls, db: Session) -> dict:
        """Run all cleanup operations"""
        results = {
            'events_deleted': cls.cleanup_old_events(db),
            'runs_deleted': cls.cleanup_old_runs(db),
            'artifact_versions_deleted': cls.cleanup_old_artifact_versions(db),
            'orphaned_universes_deleted': cls.cleanup_orphaned_universes(db),
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"Full cleanup completed: {results}")
        return results

    @classmethod
    def get_largest_artifacts(cls, db: Session, limit: int = 10) -> list:
        """Get the largest artifacts for analysis"""
        artifacts = db.query(Artifact)\
            .order_by(Artifact.file_size.desc())\
            .limit(limit)\
            .all()

        return [{
            'universe_id': a.universe_id,
            'artifact_type': a.artifact_type,
            'size_bytes': a.file_size,
            'size_mb': round(a.file_size / (1024 * 1024), 2) if a.file_size else 0,
            'created_at': a.created_at.isoformat() if a.created_at else None
        } for a in artifacts]
