"""Routes that work without database - uses mock data"""
from fastapi import APIRouter
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
