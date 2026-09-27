"""
Pydantic Schemas for Request & Response Data Transfer Objects (DTOs)
--------------------------------------------------------------------
Defines strongly typed contracts for all REST API endpoints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# -------------------------------------------------------------------------
# Customer & Claim DTOs
# -------------------------------------------------------------------------
class CustomerDetail(BaseModel):
    customer_id: str
    customer_subtype: Optional[str] = None
    customer_main_type: Optional[str] = None
    age_group: Optional[str] = None
    purchasing_power_class: Optional[int] = None
    total_policies_count: Optional[int] = 0
    active_product_lines_count: Optional[int] = 0
    has_car_policy: Optional[bool] = False
    has_fire_policy: Optional[bool] = False
    has_boat_policy: Optional[bool] = False
    has_life_policy: Optional[bool] = False
    has_accident_policy: Optional[bool] = False


class ClaimSummary(BaseModel):
    claim_id: str
    customer_id: str
    policy_type: str
    policy_count: int
    claim_amount: float
    incident_severity: str
    incident_type: str
    incident_date: Optional[str] = None
    claim_date: Optional[str] = None
    claim_status: str
    incident_description: str


class ClaimsListResponse(BaseModel):
    total: int
    page: int
    limit: int
    claims: List[ClaimSummary]


class InvestigationSummary(BaseModel):
    composite_risk_score: Optional[float] = 0.0
    risk_tier: Optional[str] = "Low"
    is_anomaly: Optional[bool] = False
    requires_handoff: Optional[bool] = False
    recommendation: Optional[str] = None
    executive_summary: Optional[str] = None
    evidence_checklist: List[str] = []
    audit_log: List[Dict[str, Any]] = []
    investigated_at: Optional[str] = None


class ClaimDetailResponse(BaseModel):
    claim_id: str
    customer_id: str
    policy_type: str
    policy_count: int
    policy_contribution_tier: int
    purchasing_power_class: int
    claim_amount: float
    incident_type: str
    incident_severity: str
    incident_date: Optional[str] = None
    claim_date: Optional[str] = None
    reporting_delay_days: int
    police_report_filed: str
    witness_present: str
    prior_claims_count: int
    incident_description: str
    claim_status: str
    customer: Optional[CustomerDetail] = None
    latest_investigation: Optional[InvestigationSummary] = None


# -------------------------------------------------------------------------
# Search & Multi-Agent Investigation DTOs
# -------------------------------------------------------------------------
class SimilarSearchRequest(BaseModel):
    query_text: str = Field(..., description="Natural language incident description")
    policy_type: Optional[str] = Field(None, description="Optional filter by policy type")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")


class SimilarClaimResult(BaseModel):
    claim_id: str
    similarity_score: float
    policy_type: Optional[str] = None
    incident_type: Optional[str] = None
    incident_severity: Optional[str] = None
    claim_amount: Optional[float] = 0.0
    police_report_filed: Optional[str] = None
    reporting_delay_days: Optional[int] = 0
    incident_description: str


class InvestigationResponse(BaseModel):
    claim_id: str
    composite_risk_score: float
    risk_tier: str
    is_anomaly: bool
    requires_handoff: bool
    policy_coverage_status: str
    recommendation: str
    executive_summary: str
    evidence_checklist: List[str]
    similar_claims: List[Dict[str, Any]]
    audit_log: List[Dict[str, Any]]
    current_status: str


# -------------------------------------------------------------------------
# Adjuster Decision DTOs
# -------------------------------------------------------------------------
class AdjusterDecisionRequest(BaseModel):
    claim_id: str
    decision: str = Field(..., description="'Approved', 'Documentation Review', or 'SIU Escalation'")
    notes: Optional[str] = Field("", description="Adjuster audit notes and justification")
    adjuster_name: Optional[str] = Field("Senior Claims Specialist", description="Name/title of reviewer")


class AdjusterDecisionResponse(BaseModel):
    success: bool
    claim_id: str
    new_status: str
    decision_id: int
    recorded_at: str


# -------------------------------------------------------------------------
# Dashboard KPI Stats DTO
# -------------------------------------------------------------------------
class StatsResponse(BaseModel):
    total_claims: int
    pending_review: int
    approved: int
    documentation_review: int
    siu_escalated: int
    investigated_count: int
