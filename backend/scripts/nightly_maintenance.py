#!/usr/bin/env python3
"""
Nightly Database Maintenance Script
Runs cleanup and optimization tasks to keep Neon database healthy

Usage:
  python nightly_maintenance.py

Environment Variables:
  DATABASE_URL - PostgreSQL connection string
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.services.storage_controls import StorageControls
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_maintenance():
    """Run nightly database maintenance tasks"""
    logger.info("=" * 60)
    logger.info("Starting nightly database maintenance")
    logger.info("=" * 60)

    db = next(get_db())

    try:
        # 1. Get current storage stats
        logger.info("\n1. Current Storage Statistics:")
        stats_before = StorageControls.get_storage_stats(db)
        logger.info(f"   Total Size: {stats_before['total_size_mb']:.2f} MB")
        logger.info(f"   Usage: {stats_before['usage_percent']:.1f}%")
        logger.info(f"   Artifacts: {stats_before['counts']['artifacts']}")
        logger.info(f"   Universes: {stats_before['counts']['universes']}")
        logger.info(f"   Runs: {stats_before['counts']['runs']}")
        logger.info(f"   Events: {stats_before['counts']['events']}")

        if stats_before['warnings']:
            logger.warning(f"   Warnings: {', '.join(stats_before['warnings'])}")

        # 2. Clean up old events (keep last 30 days)
        logger.info("\n2. Cleaning up old events...")
        events_deleted = StorageControls.cleanup_old_events(db, days=30)
        logger.info(f"   ✓ Deleted {events_deleted} old events")

        # 3. Clean up old run records (keep last 90 days)
        logger.info("\n3. Cleaning up old run records...")
        runs_deleted = StorageControls.cleanup_old_runs(db, days=90)
        logger.info(f"   ✓ Deleted {runs_deleted} old run records")

        # 4. Clean up old artifact versions (keep last 3 versions)
        logger.info("\n4. Cleaning up old artifact versions...")
        versions_deleted = StorageControls.cleanup_old_artifact_versions(db, keep_versions=3)
        logger.info(f"   ✓ Deleted {versions_deleted} old artifact versions")

        # 5. Clean up orphaned universes
        logger.info("\n5. Cleaning up orphaned universes...")
        orphans_deleted = StorageControls.cleanup_orphaned_universes(db)
        logger.info(f"   ✓ Deleted {orphans_deleted} orphaned universes")

        # 6. Get storage stats after cleanup
        logger.info("\n6. Storage Statistics After Cleanup:")
        stats_after = StorageControls.get_storage_stats(db)
        logger.info(f"   Total Size: {stats_after['total_size_mb']:.2f} MB")
        logger.info(f"   Usage: {stats_after['usage_percent']:.1f}%")
        logger.info(f"   Artifacts: {stats_after['counts']['artifacts']}")
        logger.info(f"   Universes: {stats_after['counts']['universes']}")
        logger.info(f"   Runs: {stats_after['counts']['runs']}")
        logger.info(f"   Events: {stats_after['counts']['events']}")

        # Calculate space freed
        space_freed = stats_before['total_size_mb'] - stats_after['total_size_mb']
        logger.info(f"\n   Space Freed: {space_freed:.2f} MB")

        # 7. Show largest artifacts
        logger.info("\n7. Top 5 Largest Artifacts:")
        largest = StorageControls.get_largest_artifacts(db, limit=5)
        for i, artifact in enumerate(largest, 1):
            logger.info(f"   {i}. {artifact['universe_id']}/{artifact['artifact_type']}: {artifact['size_mb']:.2f} MB")

        # 8. Summary
        logger.info("\n" + "=" * 60)
        logger.info("Maintenance Summary:")
        logger.info(f"  - Events deleted: {events_deleted}")
        logger.info(f"  - Runs deleted: {runs_deleted}")
        logger.info(f"  - Artifact versions deleted: {versions_deleted}")
        logger.info(f"  - Orphaned universes deleted: {orphans_deleted}")
        logger.info(f"  - Space freed: {space_freed:.2f} MB")
        logger.info(f"  - Final usage: {stats_after['usage_percent']:.1f}%")
        logger.info("=" * 60)

        # Warning if usage is still high
        if stats_after['usage_percent'] > 70:
            logger.warning(f"⚠️  Database usage is {stats_after['usage_percent']:.1f}% - consider manual cleanup")

        logger.info("\n✅ Nightly maintenance completed successfully")

    except Exception as e:
        logger.error(f"❌ Maintenance failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    # Verify DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        logger.error("❌ DATABASE_URL environment variable not set")
        sys.exit(1)

    run_maintenance()
