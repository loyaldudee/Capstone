"""
API Route Handlers (APIRouter)
------------------------------
Encapsulates all RESTful endpoints for claims querying, multi-agent execution,
vector similarity search, human-in-the-loop decisions, and evaluation reporting.
"""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from database import get_db
from models import Claim, Customer, InvestigationRecord, AdjusterDecision
from schemas import (
    StatsResponse,
    ClaimsListResponse,
    ClaimDetailResponse,
    SimilarSearchRequest,
    SimilarClaimResult,
    InvestigationResponse,
    AdjusterDecisionRequest,
    AdjusterDecisionResponse
)

from task3_multi_agent_system.graph import run_claims_investigation
from task2_models_analytics.models.claims_vector_engine import ClaimsVectorEngine

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_REPORT_PATH = os.path.join(ROOT_DIR, "task4_evaluation_and_ui", "evaluation_report.json")

# Router definition
router = APIRouter(prefix="/api")

# Cached vector engine instance
_vector_engine: Optional[ClaimsVectorEngine] = None


def get_vector_engine() -> ClaimsVectorEngine:
    global _vector_engine
    if _vector_engine is None:
        vector_store_path = os.path.join(ROOT_DIR, "task2_models_analytics", "vector_store")
        _vector_engine = ClaimsVectorEngine.load(vector_store_dir=vector_store_path)
    return _vector_engine


# -------------------------------------------------------------------------
# 1. System Statistics
# -------------------------------------------------------------------------
@router.get("/stats", response_model=StatsResponse, summary="Get Overview KPI Metrics")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(Claim).count()
    pending = db.query(Claim).filter(Claim.claim_status == "Pending Review").count()
    approved = db.query(Claim).filter(Claim.claim_status == "Approved").count()
    doc_review = db.query(Claim).filter(Claim.claim_status == "Documentation Review").count()
    siu = db.query(Claim).filter(Claim.claim_status == "SIU Escalation").count()
    investigated = db.query(InvestigationRecord.claim_id).distinct().count()

    return {
        "total_claims": total,
        "pending_review": pending,
        "approved": approved,
        "documentation_review": doc_review,
        "siu_escalated": siu,
        "investigated_count": investigated
    }


# -------------------------------------------------------------------------
# 2. Claims Listing & Filtering
# -------------------------------------------------------------------------
@router.get("/claims", response_model=ClaimsListResponse, summary="Browse Claims with Filters")
def list_claims(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    query: Optional[str] = Query(None, description="Search claim ID or customer ID"),
    policy_type: Optional[str] = Query(None, description="Filter by policy line"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    q = db.query(Claim)

    if query:
        q = q.filter(
            or_(
                Claim.claim_id.ilike(f"%{query}%"),
                Claim.customer_id.ilike(f"%{query}%"),
                Claim.incident_type.ilike(f"%{query}%"),
                Claim.incident_description.ilike(f"%{query}%")
            )
        )

    if policy_type:
        q = q.filter(Claim.policy_type == policy_type)

    if status:
        q = q.filter(Claim.claim_status == status)

    total_count = q.count()
    offset = (page - 1) * limit
    claims = q.order_by(desc(Claim.claim_id)).offset(offset).limit(limit).all()


    formatted_claims = [
        {
            "claim_id": c.claim_id,
            "customer_id": c.customer_id,
            "policy_type": c.policy_type,
            "policy_count": c.policy_count,
            "claim_amount": c.claim_amount,
            "incident_severity": c.incident_severity,
            "incident_type": c.incident_type,
            "incident_date": c.incident_date,
            "claim_date": c.claim_date,
            "claim_status": c.claim_status,
            "incident_description": c.incident_description
        }
        for c in claims
    ]

    return {
        "total": total_count,
        "page": page,
        "limit": limit,
        "claims": formatted_claims
    }


# -------------------------------------------------------------------------
# 3. Claim Dossier & Customer Profile
# -------------------------------------------------------------------------
@router.get("/claims/{claim_id}", response_model=ClaimDetailResponse, summary="Get Full Claim Dossier")
def get_claim_dossier(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found.")

    cust = db.query(Customer).filter(Customer.customer_id == claim.customer_id).first()

    latest_inv = (
        db.query(InvestigationRecord)
        .filter(InvestigationRecord.claim_id == claim_id)
        .order_by(desc(InvestigationRecord.investigated_at))
        .first()
    )

    inv_data = None
    if latest_inv:
        checklist = []
        if latest_inv.evidence_checklist:
            try:
                checklist = json.loads(latest_inv.evidence_checklist)
            except Exception:
                checklist = [latest_inv.evidence_checklist]

        audit = []
        if latest_inv.audit_log:
            try:
                audit = json.loads(latest_inv.audit_log)
            except Exception:
                audit = []

        inv_data = {
            "composite_risk_score": latest_inv.composite_risk_score,
            "risk_tier": latest_inv.risk_tier,
            "is_anomaly": latest_inv.is_anomaly,
            "requires_handoff": latest_inv.requires_handoff,
            "recommendation": latest_inv.recommendation,
            "executive_summary": latest_inv.executive_summary,
            "evidence_checklist": checklist,
            "audit_log": audit,
            "investigated_at": latest_inv.investigated_at.isoformat() if latest_inv.investigated_at else None
        }

    cust_dict = None
    if cust:
        cust_dict = {
            "customer_id": cust.customer_id,
            "customer_subtype": cust.customer_subtype,
            "customer_main_type": cust.customer_main_type,
            "age_group": cust.age_group,
            "purchasing_power_class": cust.purchasing_power_class,
            "total_policies_count": cust.total_policies_count,
            "active_product_lines_count": cust.active_product_lines_count,
            "has_car_policy": cust.has_car_policy,
            "has_fire_policy": cust.has_fire_policy,
            "has_boat_policy": cust.has_boat_policy,
            "has_life_policy": cust.has_life_policy,
            "has_accident_policy": cust.has_accident_policy
        }

    return {
        "claim_id": claim.claim_id,
        "customer_id": claim.customer_id,
        "policy_type": claim.policy_type,
        "policy_count": claim.policy_count,
        "policy_contribution_tier": claim.policy_contribution_tier,
        "purchasing_power_class": claim.purchasing_power_class,
        "claim_amount": claim.claim_amount,
        "incident_type": claim.incident_type,
        "incident_severity": claim.incident_severity,
        "incident_date": claim.incident_date,
        "claim_date": claim.claim_date,
        "reporting_delay_days": claim.reporting_delay_days,
        "police_report_filed": claim.police_report_filed,
        "witness_present": claim.witness_present,
        "prior_claims_count": claim.prior_claims_count,
        "incident_description": claim.incident_description,
        "claim_status": claim.claim_status,
        "customer": cust_dict,
        "latest_investigation": inv_data
    }


# -------------------------------------------------------------------------
# 4. Multi-Agent Investigation Trigger
# -------------------------------------------------------------------------
@router.post("/investigate/{claim_id}", response_model=InvestigationResponse, summary="Execute 5-Agent Investigation Workflow")
def investigate_claim(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found.")

    cust = db.query(Customer).filter(Customer.customer_id == claim.customer_id).first()

    claim_dict = {
        "claim_id": claim.claim_id,
        "customer_id": claim.customer_id,
        "policy_type": claim.policy_type,
        "policy_count": claim.policy_count,
        "policy_contribution_tier": claim.policy_contribution_tier,
        "purchasing_power_class": claim.purchasing_power_class,
        "claim_amount": claim.claim_amount,
        "incident_type": claim.incident_type,
        "incident_severity": claim.incident_severity,
        "incident_date": claim.incident_date,
        "claim_date": claim.claim_date,
        "reporting_delay_days": claim.reporting_delay_days,
        "police_report_filed": claim.police_report_filed,
        "witness_present": claim.witness_present,
        "prior_claims_count": claim.prior_claims_count,
        "incident_description": claim.incident_description
    }

    cust_dict = {}
    if cust:
        cust_dict = {
            "customer_id": cust.customer_id,
            "customer_subtype_desc": cust.customer_subtype,
            "customer_main_type_desc": cust.customer_main_type,
            "age_group_desc": cust.age_group,
            "MKOOPKLA": cust.purchasing_power_class,
            "total_policies_count": cust.total_policies_count,
            "active_product_lines_count": cust.active_product_lines_count
        }

    try:
        result_state = run_claims_investigation(claim_dict, cust_dict)

        risk_analysis = result_state.get("risk_analysis", {})
        anomaly_findings = result_state.get("anomaly_findings", {})
        requires_handoff = result_state.get("requires_investigation_handoff", False)
        composite_score = risk_analysis.get("supervised_risk_probability", 0.0)
        risk_tier = risk_analysis.get("preliminary_risk_tier", "Low")
        is_anomaly = anomaly_findings.get("is_anomaly", False)
        checklist = result_state.get("siu_evidence_checklist", [])
        recommendation = result_state.get("final_recommended_action") or result_state.get("retrieval_insights", "Standard Review")
        executive_summary = result_state.get("executive_summary", "")
        similar_claims = result_state.get("similar_claims", [])
        audit_log = result_state.get("audit_log", [])

        inv_record = InvestigationRecord(
            claim_id=claim.claim_id,
            composite_risk_score=float(composite_score),
            risk_tier=str(risk_tier),
            is_anomaly=bool(is_anomaly),
            requires_handoff=bool(requires_handoff),
            recommendation=str(recommendation),
            executive_summary=str(executive_summary),
            evidence_checklist=json.dumps(checklist),
            audit_log=json.dumps(audit_log),
            investigated_at=datetime.utcnow()
        )
        db.add(inv_record)

        if requires_handoff and claim.claim_status == "Pending Review":
            claim.claim_status = "SIU Escalation"

        db.commit()

        return {
            "claim_id": claim.claim_id,
            "composite_risk_score": composite_score,
            "risk_tier": risk_tier,
            "is_anomaly": is_anomaly,
            "requires_handoff": requires_handoff,
            "policy_coverage_status": result_state.get("policy_coverage_status", "Valid"),
            "recommendation": recommendation,
            "executive_summary": executive_summary,
            "evidence_checklist": checklist,
            "similar_claims": similar_claims,
            "audit_log": audit_log,
            "current_status": claim.claim_status
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LangGraph multi-agent execution failed: {str(e)}"
        )


# -------------------------------------------------------------------------
# 5. Semantic Vector Search
# -------------------------------------------------------------------------
@router.post("/search/similar", response_model=List[SimilarClaimResult], summary="Semantic Vector Search")
def semantic_vector_search(req: SimilarSearchRequest):
    engine = get_vector_engine()
    try:
        results = engine.search_similar_claims(
            query_text=req.query_text,
            policy_type=req.policy_type,
            top_k=req.top_k
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ChromaDB search failed: {str(e)}")


# -------------------------------------------------------------------------
# 6. Human Reviewer Gate
# -------------------------------------------------------------------------
@router.post("/adjuster/decision", response_model=AdjusterDecisionResponse, summary="Record Adjuster Sign-Off")
def submit_adjuster_decision(req: AdjusterDecisionRequest, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.claim_id == req.claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim {req.claim_id} not found.")

    valid_decisions = ["Approved", "Documentation Review", "SIU Escalation"]
    if req.decision not in valid_decisions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid decision '{req.decision}'. Must be one of: {valid_decisions}"
        )

    claim.claim_status = req.decision

    decision_record = AdjusterDecision(
        claim_id=claim.claim_id,
        decision=req.decision,
        notes=req.notes,
        adjuster_name=req.adjuster_name,
        decided_at=datetime.utcnow()
    )
    db.add(decision_record)
    db.commit()

    return {
        "success": True,
        "claim_id": claim.claim_id,
        "new_status": claim.claim_status,
        "decision_id": decision_record.id,
        "recorded_at": decision_record.decided_at.isoformat()
    }


# -------------------------------------------------------------------------
# 7. Verification & Evaluation Benchmarks
# -------------------------------------------------------------------------
@router.get("/evaluation/metrics", summary="Model & Retrieval Verification Benchmarks")
def get_evaluation_metrics():
    if os.path.exists(EVAL_REPORT_PATH):
        with open(EVAL_REPORT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    raise HTTPException(status_code=404, detail="Evaluation report not found. Run evaluate_system.py first.")

@router.get("/health")
def health_check():
    return {"status": "Aegis AI Claims Assistant is Live & Ready"}