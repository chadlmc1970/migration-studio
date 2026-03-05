"""Routes that work without database - uses mock data"""
from fastapi import APIRouter, HTTPException
from app.database import is_db_available
from app.api.mock_data import MOCK_UNIVERSES, MOCK_KPIS, MOCK_EVENTS

router_no_db = APIRouter(prefix="/api")


@router_no_db.get("/universes")
async def list_universes_no_db():
    """List all universes - mock data version"""
    return MOCK_UNIVERSES


@router_no_db.get("/kpis")
async def get_kpis_no_db():
    """Get KPI metrics - mock data version"""
    return MOCK_KPIS


@router_no_db.get("/events")
async def get_events_no_db(limit: int = 50):
    """Get events - mock data version"""
    return MOCK_EVENTS


@router_no_db.get("/state")
async def get_state_no_db():
    """Get pipeline state - mock data version"""
    universes_dict = {}
    for u in MOCK_UNIVERSES:
        universes_dict[u["id"]] = {
            "parsed": u["parsed"],
            "transformed": u["transformed"],
            "validated": u["validated"],
            "validated_at": u.get("validated_at")
        }
    return {"universes": universes_dict}


@router_no_db.get("/universes/{universe_id}/reports")
async def get_universe_reports_no_db(universe_id: str):
    """Get universe reports - mock data version"""
    # Check if universe exists in mock data
    universe_exists = any(u["id"] == universe_id for u in MOCK_UNIVERSES)
    if not universe_exists:
        raise HTTPException(status_code=404, detail=f"Universe not found: {universe_id}")

    # Return mock report data with AI enhancements
    return {
        "universe_id": universe_id,
        "ai_enhanced": True,
        "ai_enhancements": [
            {
                "category": "Semantic Enrichment",
                "description": "AI automatically generated business-friendly descriptions for 45 dimensions and measures",
                "impact": "high"
            },
            {
                "category": "Data Quality Scoring",
                "description": "Analyzed model completeness and assigned quality scores (92/100 overall)",
                "impact": "medium"
            },
            {
                "category": "Coverage Analysis",
                "description": "Identified 100% coverage of audit log dimensions with full validation",
                "impact": "high"
            }
        ],
        "coverage_report": {
            "coverage_percentage": 95.0,
            "total_objects": 45,
            "covered_objects": 43,
            "missing_objects": 2
        },
        "semantic_diff": None,
        "available_artifacts": {
            "sac_model": True,
            "datasphere_views": True,
            "hana_schema": True,
            "lineage_dot": True
        }
    }
