# app/api/pda_routes.py
from fastapi import APIRouter
from app.services.pda_costs import PDACostService

pda_router = APIRouter(prefix="/pda", tags=["PDA & Cost Management"])
pda_service = PDACostService()

@pda_router.get("/estimate")
def estimate_pda(origin: str, destination: str, canals: str = None):
    canal_list = canals.split(",") if canals else []
    return pda_service.estimate_pda(origin, destination, canal_list)

@pda_router.post("/record/{voyage_id}")
def record_actual(voyage_id: str, actuals: dict):
    return pda_service.record_actual_costs(voyage_id, actuals)

@pda_router.post("/compare/{voyage_id}")
def compare(voyage_id: str, origin: str, destination: str, canals: str = None):
    canal_list = canals.split(",") if canals else []
    estimate = pda_service.estimate_pda(origin, destination, canal_list)
    return pda_service.compare_estimate_vs_actual(voyage_id, estimate)
