# app/api/cargo_matching_routes.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.services.cargo_matching import CargoMatchingService, Vessel, CargoOpportunity, VesselType, CargoType

router = APIRouter(prefix="/cargo-matching", tags=["Cargo Matching"])

# Initialize the service
cargo_service = CargoMatchingService()

# Pydantic models for API
class VesselModel(BaseModel):
    id: str
    name: str
    vessel_type: VesselType
    dwt: int
    capacity_teu: Optional[int] = None
    capacity_cbm: Optional[int] = None
    length: float = 0
    beam: float = 0
    draft: float = 0
    current_position_lat: float = 0
    current_position_lon: float = 0
    next_available_date: datetime
    daily_operating_cost: float = 15000
    fuel_consumption_mt_day: float = 25
    suitable_cargo_types: List[CargoType] = []
    ice_class: Optional[str] = None
    special_equipment: List[str] = []

class CargoOpportunityModel(BaseModel):
    id: str
    description: str
    cargo_type: CargoType
    quantity_mt: float
    volume_cbm: Optional[float] = None
    origin_port: str = ""
    destination_port: str = ""
    origin_lat: float = 0
    origin_lon: float = 0
    destination_lat: float = 0
    destination_lon: float = 0
    laycan_start: datetime
    laycan_end: datetime
    freight_rate_usd_mt: float = 0
    discharge_rate_mt_day: float = 5000
    loading_rate_mt_day: float = 5000
    special_requirements: List[str] = []
    charterer: str = ""
    urgency_factor: float = 1.0

class MatchRequestModel(BaseModel):
    vessel_id: Optional[str] = None
    cargo_id: Optional[str] = None
    top_n: int = Field(default=10, ge=1, le=50)

# Routes
@router.post("/vessels/add")
async def add_vessel(vessel_data: VesselModel):
    """Add a vessel to the matching pool"""
    try:
        vessel = Vessel(
            id=vessel_data.id,
            name=vessel_data.name,
            vessel_type=vessel_data.vessel_type,
            dwt=vessel_data.dwt,
            capacity_teu=vessel_data.capacity_teu,
            capacity_cbm=vessel_data.capacity_cbm,
            length=vessel_data.length,
            beam=vessel_data.beam,
            draft=vessel_data.draft,
            current_position=(vessel_data.current_position_lat, vessel_data.current_position_lon),
            next_available_date=vessel_data.next_available_date,
            daily_operating_cost=vessel_data.daily_operating_cost,
            fuel_consumption_mt_day=vessel_data.fuel_consumption_mt_day,
            suitable_cargo_types=vessel_data.suitable_cargo_types,
            ice_class=vessel_data.ice_class,
            special_equipment=vessel_data.special_equipment
        )
        
        cargo_service.add_vessel(vessel)
        
        return {
            "message": f"Vessel {vessel_data.name} added successfully",
            "vessel_id": vessel_data.id,
            "total_vessels": len(cargo_service.vessels)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cargo/add")
async def add_cargo_opportunity(cargo_data: CargoOpportunityModel):
    """Add a cargo opportunity to the matching pool"""
    try:
        cargo = CargoOpportunity(
            id=cargo_data.id,
            description=cargo_data.description,
            cargo_type=cargo_data.cargo_type,
            quantity_mt=cargo_data.quantity_mt,
            volume_cbm=cargo_data.volume_cbm,
            origin_port=cargo_data.origin_port,
            destination_port=cargo_data.destination_port,
            origin_coords=(cargo_data.origin_lat, cargo_data.origin_lon),
            destination_coords=(cargo_data.destination_lat, cargo_data.destination_lon),
            laycan_start=cargo_data.laycan_start,
            laycan_end=cargo_data.laycan_end,
            freight_rate_usd_mt=cargo_data.freight_rate_usd_mt,
            discharge_rate_mt_day=cargo_data.discharge_rate_mt_day,
            loading_rate_mt_day=cargo_data.loading_rate_mt_day,
            special_requirements=cargo_data.special_requirements,
            charterer=cargo_data.charterer,
            urgency_factor=cargo_data.urgency_factor
        )
        
        cargo_service.add_cargo_opportunity(cargo)
        
        return {
            "message": f"Cargo opportunity {cargo_data.description} added successfully",
            "cargo_id": cargo_data.id,
            "total_cargo_opportunities": len(cargo_service.cargo_opportunities)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/find-matches")
async def find_optimal_matches(request: MatchRequestModel):
    """Find optimal cargo-vessel matches"""
    try:
        matches = await cargo_service.find_optimal_matches(
            vessel_id=request.vessel_id,
            cargo_id=request.cargo_id,
            top_n=request.top_n
        )
        
        # Convert matches to response format
        results = []
        for match in matches:
            results.append({
                "vessel": {
                    "id": match.vessel.id,
                    "name": match.vessel.name,
                    "type": match.vessel.vessel_type.value,
                    "dwt": match.vessel.dwt
                },
                "cargo": {
                    "id": match.cargo.id,
                    "description": match.cargo.description,
                    "type": match.cargo.cargo_type.value,
                    "quantity_mt": match.cargo.quantity_mt,
                    "route": f"{match.cargo.origin_port} -> {match.cargo.destination_port}",
                    "laycan": f"{match.cargo.laycan_start.strftime('%Y-%m-%d')} to {match.cargo.laycan_end.strftime('%Y-%m-%d')}"
                },
                "analysis": {
                    "compatibility_score": round(match.compatibility_score, 2),
                    "profitability_usd": round(match.profitability_usd, 2),
                    "profit_margin_percent": round(match.profit_margin_percent, 2),
                    "voyage_duration_days": round(match.voyage_duration_days, 1),
                    "gross_revenue_usd": round(match.gross_revenue_usd, 2),
                    "total_costs_usd": round(match.total_fuel_cost_usd + match.total_operating_cost_usd, 2)
                },
                "breakdown": {
                    "positioning_days": round(match.positioning_days, 1),
                    "loading_days": round(match.loading_days, 1),
                    "discharge_days": round(match.discharge_days, 1),
                    "fuel_cost_usd": round(match.total_fuel_cost_usd, 2),
                    "operating_cost_usd": round(match.total_operating_cost_usd, 2)
                },
                "risk_factors": match.risk_factors,
                "recommendations": match.recommendations
            })
        
        return {
            "matches_found": len(results),
            "search_criteria": {
                "vessel_id": request.vessel_id,
                "cargo_id": request.cargo_id,
                "top_n": request.top_n
            },
            "matches": results,
            "market_summary": {
                "total_vessels": len(cargo_service.vessels),
                "total_cargo_opportunities": len(cargo_service.cargo_opportunities),
                "avg_profitability": round(sum(match.profitability_usd for match in matches) / len(matches), 2) if matches else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-analysis")
async def get_market_analysis(vessel_type: Optional[VesselType] = None):
    """Get market analysis and opportunities"""
    try:
        analysis = await cargo_service.analyze_market_opportunities(vessel_type)
        return {
            "market_analysis": analysis,
            "timestamp": datetime.now().isoformat(),
            "data_points": {
                "vessels_analyzed": len(cargo_service.vessels),
                "cargo_opportunities_analyzed": len(cargo_service.cargo_opportunities)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vessels/{vessel_id}/utilization-forecast")
async def get_vessel_utilization_forecast(
    vessel_id: str,
    days_ahead: int = Query(default=30, ge=1, le=365)
):
    """Get vessel utilization forecast"""
    try:
        forecast = cargo_service.get_vessel_utilization_forecast(vessel_id, days_ahead)
        if "error" in forecast:
            raise HTTPException(status_code=404, detail=forecast["error"])
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vessels")
async def list_vessels():
    """List all vessels in the matching pool"""
    vessels = []
    for vessel in cargo_service.vessels:
        vessels.append({
            "id": vessel.id,
            "name": vessel.name,
            "type": vessel.vessel_type.value,
            "dwt": vessel.dwt,
            "current_position": vessel.current_position,
            "next_available": vessel.next_available_date.isoformat() if vessel.next_available_date else None
        })
    
    return {
        "total_vessels": len(vessels),
        "vessels": vessels
    }

@router.get("/cargo-opportunities")
async def list_cargo_opportunities():
    """List all cargo opportunities in the matching pool"""
    cargo_list = []
    for cargo in cargo_service.cargo_opportunities:
        cargo_list.append({
            "id": cargo.id,
            "description": cargo.description,
            "type": cargo.cargo_type.value,
            "quantity_mt": cargo.quantity_mt,
            "route": f"{cargo.origin_port} -> {cargo.destination_port}",
            "laycan": f"{cargo.laycan_start.strftime('%Y-%m-%d')} to {cargo.laycan_end.strftime('%Y-%m-%d')}",
            "freight_rate_usd_mt": cargo.freight_rate_usd_mt,
            "charterer": cargo.charterer,
            "urgency_factor": cargo.urgency_factor
        })
    
    return {
        "total_cargo_opportunities": len(cargo_list),
        "cargo_opportunities": cargo_list
    }

@router.delete("/vessels/{vessel_id}")
async def remove_vessel(vessel_id: str):
    """Remove a vessel from the matching pool"""
    cargo_service.vessels = [v for v in cargo_service.vessels if v.id != vessel_id]
    return {
        "message": f"Vessel {vessel_id} removed successfully",
        "total_vessels": len(cargo_service.vessels)
    }

@router.delete("/cargo-opportunities/{cargo_id}")
async def remove_cargo_opportunity(cargo_id: str):
    """Remove a cargo opportunity from the matching pool"""
    cargo_service.cargo_opportunities = [c for c in cargo_service.cargo_opportunities if c.id != cargo_id]
    return {
        "message": f"Cargo opportunity {cargo_id} removed successfully",
        "total_cargo_opportunities": len(cargo_service.cargo_opportunities)
    }

@router.get("/compatibility/{vessel_id}/{cargo_id}")
async def check_compatibility(vessel_id: str, cargo_id: str):
    """Check compatibility between a specific vessel and cargo"""
    try:
        vessel = next((v for v in cargo_service.vessels if v.id == vessel_id), None)
        cargo = next((c for c in cargo_service.cargo_opportunities if c.id == cargo_id), None)
        
        if not vessel:
            raise HTTPException(status_code=404, detail="Vessel not found")
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo opportunity not found")
        
        compatibility_score = cargo_service.assess_vessel_cargo_compatibility(vessel, cargo)
        economics = cargo_service.calculate_voyage_economics(vessel, cargo)
        risks, recommendations = cargo_service.assess_risks_and_recommendations(vessel, cargo, economics)
        
        return {
            "vessel_id": vessel_id,
            "cargo_id": cargo_id,
            "compatibility_score": round(compatibility_score, 2),
            "is_compatible": compatibility_score >= 5.0,
            "economics": {
                "gross_revenue_usd": round(economics["gross_revenue"], 2),
                "total_costs_usd": round(economics["total_costs"], 2),
                "net_profit_usd": round(economics["net_profit"], 2),
                "profit_margin_percent": round(economics["profit_margin"], 2),
                "voyage_duration_days": round(economics["total_voyage_days"], 1)
            },
            "risk_factors": risks,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/best-matches/{vessel_id}")
async def get_best_matches_for_vessel(vessel_id: str, limit: int = Query(default=5, ge=1, le=20)):
    """Get best cargo matches for a specific vessel"""
    try:
        matches = await cargo_service.find_optimal_matches(vessel_id=vessel_id, top_n=limit)
        
        if not matches:
            return {
                "vessel_id": vessel_id,
                "matches_found": 0,
                "message": "No suitable cargo opportunities found for this vessel"
            }
        
        return {
            "vessel_id": vessel_id,
            "matches_found": len(matches),
            "best_matches": [{
                "cargo_id": match.cargo.id,
                "description": match.cargo.description,
                "profitability_usd": round(match.profitability_usd, 2),
                "profit_margin_percent": round(match.profit_margin_percent, 2),
                "compatibility_score": round(match.compatibility_score, 2),
                "voyage_days": round(match.voyage_duration_days, 1),
                "route": f"{match.cargo.origin_port} -> {match.cargo.destination_port}"
            } for match in matches]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/best-vessels/{cargo_id}")
async def get_best_vessels_for_cargo(cargo_id: str, limit: int = Query(default=5, ge=1, le=20)):
    """Get best vessel matches for a specific cargo"""
    try:
        matches = await cargo_service.find_optimal_matches(cargo_id=cargo_id, top_n=limit)
        
        if not matches:
            return {
                "cargo_id": cargo_id,
                "matches_found": 0,
                "message": "No suitable vessels found for this cargo opportunity"
            }
        
        return {
            "cargo_id": cargo_id,
            "matches_found": len(matches),
            "best_vessels": [{
                "vessel_id": match.vessel.id,
                "vessel_name": match.vessel.name,
                "vessel_type": match.vessel.vessel_type.value,
                "dwt": match.vessel.dwt,
                "profitability_usd": round(match.profitability_usd, 2),
                "profit_margin_percent": round(match.profit_margin_percent, 2),
                "compatibility_score": round(match.compatibility_score, 2),
                "positioning_days": round(match.positioning_days, 1)
            } for match in matches]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-analysis")
async def batch_cargo_vessel_analysis(request: Dict[str, Any]):
    """Perform batch analysis of multiple cargo-vessel combinations"""
    try:
        vessel_ids = request.get("vessel_ids", [])
        cargo_ids = request.get("cargo_ids", [])
        
        if not vessel_ids or not cargo_ids:
            raise HTTPException(status_code=400, detail="Both vessel_ids and cargo_ids must be provided")
        
        results = []
        
        for vessel_id in vessel_ids:
            vessel_matches = await cargo_service.find_optimal_matches(vessel_id=vessel_id, top_n=len(cargo_ids))
            
            # Filter matches to only include requested cargo IDs
            filtered_matches = [m for m in vessel_matches if m.cargo.id in cargo_ids]
            
            if filtered_matches:
                best_match = filtered_matches[0]
                results.append({
                    "vessel_id": vessel_id,
                    "best_cargo_match": {
                        "cargo_id": best_match.cargo.id,
                        "profitability_usd": round(best_match.profitability_usd, 2),
                        "compatibility_score": round(best_match.compatibility_score, 2),
                        "profit_margin_percent": round(best_match.profit_margin_percent, 2)
                    },
                    "all_matches": len(filtered_matches)
                })
            else:
                results.append({
                    "vessel_id": vessel_id,
                    "best_cargo_match": None,
                    "all_matches": 0
                })
        
        return {
            "batch_analysis": {
                "vessels_analyzed": len(vessel_ids),
                "cargo_opportunities_analyzed": len(cargo_ids),
                "successful_matches": len([r for r in results if r["best_cargo_match"]]),
                "total_potential_profit": sum(r["best_cargo_match"]["profitability_usd"] 
                                            for r in results if r["best_cargo_match"])
            },
            "vessel_results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_matching_statistics():
    """Get overall cargo-vessel matching statistics"""
    try:
        total_vessels = len(cargo_service.vessels)
        total_cargo = len(cargo_service.cargo_opportunities)
        
        if total_vessels == 0 or total_cargo == 0:
            return {
                "message": "Insufficient data for statistics",
                "total_vessels": total_vessels,
                "total_cargo_opportunities": total_cargo
            }
        
        # Analyze vessel types
        vessel_types = {}
        for vessel in cargo_service.vessels:
            vessel_type = vessel.vessel_type.value
            vessel_types[vessel_type] = vessel_types.get(vessel_type, 0) + 1
        
        # Analyze cargo types
        cargo_types = {}
        total_cargo_mt = 0
        total_revenue_potential = 0
        
        for cargo in cargo_service.cargo_opportunities:
            cargo_type = cargo.cargo_type.value
            cargo_types[cargo_type] = cargo_types.get(cargo_type, 0) + 1
            total_cargo_mt += cargo.quantity_mt
            total_revenue_potential += cargo.quantity_mt * cargo.freight_rate_usd_mt
        
        # Quick compatibility analysis
        compatible_pairs = 0
        total_pairs = 0
        
        for vessel in cargo_service.vessels[:10]:  # Sample first 10 vessels for performance
            for cargo in cargo_service.cargo_opportunities[:10]:  # Sample first 10 cargos
                total_pairs += 1
                compatibility = cargo_service.assess_vessel_cargo_compatibility(vessel, cargo)
                if compatibility >= 5.0:
                    compatible_pairs += 1
        
        compatibility_rate = (compatible_pairs / total_pairs * 100) if total_pairs > 0 else 0
        
        return {
            "overview": {
                "total_vessels": total_vessels,
                "total_cargo_opportunities": total_cargo,
                "total_cargo_volume_mt": round(total_cargo_mt, 2),
                "total_revenue_potential_usd": round(total_revenue_potential, 2),
                "compatibility_rate_percent": round(compatibility_rate, 2)
            },
            "vessel_distribution": vessel_types,
            "cargo_distribution": cargo_types,
            "market_indicators": {
                "avg_freight_rate_per_mt": round(total_revenue_potential / total_cargo_mt, 2) if total_cargo_mt > 0 else 0,
                "avg_cargo_size_mt": round(total_cargo_mt / total_cargo, 2) if total_cargo > 0 else 0,
                "avg_vessel_capacity_dwt": round(sum(v.dwt for v in cargo_service.vessels) / total_vessels, 2) if total_vessels > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))