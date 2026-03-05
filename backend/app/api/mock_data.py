"""Mock data for when database is not available"""

MOCK_UNIVERSES = [
    {
        "id": "BOEXI40-Audit-Sybase",
        "parsed": True,
        "transformed": True,
        "validated": True,
        "validated_at": "2026-03-05T12:00:00"
    },
    {
        "id": "BOEXI40-Audit-MSSQL",
        "parsed": True,
        "transformed": True,
        "validated": True,
        "validated_at": "2026-03-05T12:00:00"
    },
    {
        "id": "BOEXI40-Audit-DB2",
        "parsed": True,
        "transformed": True,
        "validated": True,
        "validated_at": "2026-03-05T12:00:00"
    },
    {
        "id": "BOEXI40-Audit-MySQL",
        "parsed": True,
        "transformed": True,
        "validated": True,
        "validated_at": "2026-03-05T12:00:00"
    },
    {
        "id": "BOEXI40-Audit-SQLAnywhere",
        "parsed": True,
        "transformed": True,
        "validated": True,
        "validated_at": "2026-03-05T12:00:00"
    },
    {
        "id": "BOEXI40-Audit-HANA",
        "parsed": True,
        "transformed": True,
        "validated": True,
        "validated_at": "2026-03-05T12:00:00"
    },
    {
        "id": "BOEXI40-Audit-Oracle",
        "parsed": True,
        "transformed": True,
        "validated": True,
        "validated_at": "2026-03-05T12:00:00"
    }
]

MOCK_KPIS = {
    "total_universes": 7,
    "parsed": 7,
    "transformed": 7,
    "validated": 7,
    "needs_attention": 0
}

MOCK_EVENTS = [
    {
        "timestamp": "2026-03-05T12:00:00",
        "level": "info",
        "message": "System initialized (using mock data - set DATABASE_URL to enable persistence)"
    }
]
