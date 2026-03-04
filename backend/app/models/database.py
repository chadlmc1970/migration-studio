"""SQLAlchemy ORM models for Migration Studio database"""
from sqlalchemy import Column, String, Boolean, Integer, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Universe(Base):
    """Universe model - maps to universes table"""
    __tablename__ = "universes"

    id = Column(String(255), primary_key=True)
    parsed = Column(Boolean, default=False)
    transformed = Column(Boolean, default=False)
    validated = Column(Boolean, default=False)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    events = relationship("Event", back_populates="universe", cascade="all, delete-orphan")
    validation_reports = relationship("ValidationReport", back_populates="universe", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="universe", cascade="all, delete-orphan")


class Event(Base):
    """Event model - maps to events table"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    universe_id = Column(String(255), ForeignKey("universes.id", ondelete="CASCADE"), nullable=True)
    extra_data = Column("metadata", JSONB, nullable=True)

    # Relationships
    universe = relationship("Universe", back_populates="events")


class Run(Base):
    """Run model - maps to runs table"""
    __tablename__ = "runs"

    id = Column(String(50), primary_key=True)
    status = Column(String(20), nullable=False)  # pending, running, completed, failed
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    universes_processed = Column(Integer, default=0)
    extra_data = Column("metadata", JSONB, nullable=True)


class ValidationReport(Base):
    """ValidationReport model - maps to validation_reports table"""
    __tablename__ = "validation_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    universe_id = Column(String(255), ForeignKey("universes.id", ondelete="CASCADE"), nullable=False)
    coverage_report = Column(JSONB, nullable=True)
    semantic_diff = Column(JSONB, nullable=True)
    lineage_graph = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    universe = relationship("Universe", back_populates="validation_reports")


class Artifact(Base):
    """Artifact model - maps to artifacts table"""
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    universe_id = Column(String(255), ForeignKey("universes.id", ondelete="CASCADE"), nullable=False)
    artifact_type = Column(String(50), nullable=False)  # sac_model, datasphere_views, hana_schema, lineage_dot
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    universe = relationship("Universe", back_populates="artifacts")
