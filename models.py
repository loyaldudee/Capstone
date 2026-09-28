"""
SQLAlchemy ORM Relational Models
--------------------------------
Defines schema for Customers, Claims, Investigation Records, and Adjuster Decisions.
Database-agnostic (SQLite locally, PostgreSQL in production).
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    Text,
    ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(50), primary_key=True, index=True)
    customer_subtype = Column(String(100))
    customer_main_type = Column(String(100))
    age_group = Column(String(50))
    purchasing_power_class = Column(Integer)
    total_policies_count = Column(Integer)
    active_product_lines_count = Column(Integer)
    has_car_policy = Column(Boolean)
    has_fire_policy = Column(Boolean)
    has_boat_policy = Column(Boolean)
    has_life_policy = Column(Boolean)
    has_accident_policy = Column(Boolean)

    claims = relationship("Claim", back_populates="customer")


class Claim(Base):
    __tablename__ = "claims"

    claim_id = Column(String(50), primary_key=True, index=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), index=True)
    policy_type = Column(String(50), index=True)
    policy_count = Column(Integer)
    policy_contribution_tier = Column(Integer)
    purchasing_power_class = Column(Integer)
    claim_amount = Column(Float, index=True)
    incident_type = Column(String(100))
    incident_severity = Column(String(50), index=True)
    incident_date = Column(String(20))
    claim_date = Column(String(20))
    reporting_delay_days = Column(Integer)
    police_report_filed = Column(String(10))
    witness_present = Column(String(10))
    prior_claims_count = Column(Integer)
    incident_description = Column(Text)
    claim_status = Column(String(50), default="Pending Review", index=True)

    customer = relationship("Customer", back_populates="claims")
    investigations = relationship("InvestigationRecord", back_populates="claim")
    decisions = relationship("AdjusterDecision", back_populates="claim")


class InvestigationRecord(Base):
    __tablename__ = "investigation_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(50), ForeignKey("claims.claim_id"), index=True)
    composite_risk_score = Column(Float)
    risk_tier = Column(String(50))
    is_anomaly = Column(Boolean)
    requires_handoff = Column(Boolean)
    recommendation = Column(String(255))
    executive_summary = Column(Text)
    evidence_checklist = Column(Text)  # JSON-encoded string
    audit_log = Column(Text)            # JSON-encoded string
    advisor_guidance = Column(Text, nullable=True)  # JSON-encoded string
    investigated_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="investigations")


class AdjusterDecision(Base):
    __tablename__ = "adjuster_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(50), ForeignKey("claims.claim_id"), index=True)
    decision = Column(String(100))
    notes = Column(Text)
    adjuster_name = Column(String(100), default="Senior Claims Specialist")
    decided_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="decisions")
