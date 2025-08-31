# app/api/ais_routes.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from app.services.ais_service import AISService
import asyncio

# Initialize router and AIS service
ais_router = APIRouter()
ais_service = AISService()

# Response models
class ShipPosition(BaseModel):
    mmsi: str
    name: str
    lat: float
    lon: float
    speed: float
    timestamp: str
    distance_km: Optional[float] = None

class TrafficStats(BaseModel):
    total_ships_tracked: int
    ships_moving: int
    ships_stationary: int
    last_update: str
    cache_status: str

class AISResponse(BaseModel):
    status: str
    data: Optional[dict] = None
    ships: Optional[List[ShipPosition]] = None
    stats: Optional[TrafficStats] = None
    message: Optional[str] = None

# Start AIS collection when module loads
@ais_router.on_event("startup")
async def start_ais():
    await ais_service.start_background_collection()

# --- AIS ENDPOINTS ---

@ais_router.get("/ais/status", response_model=AISResponse)
async def get_ais_status():
    """Get AIS system status"""
    try:
        stats = ais_service.get_traffic_stats()
        return AISResponse(
            status="success",
            stats=TrafficStats(**stats),
            message="AIS tracking system operational"
        )
    except Exception as e:
        return AISResponse(status="error", message=str(e))

@ais_router.get("/ais/ships/area", response_model=AISResponse)
async def get_ships_in_area(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"), 
    radius: float = Query(50, description="Search radius in km")
):
    """Get ships within radius of coordinates"""
    try:
        ships_data = ais_service.get_ships_in_area(lat, lon, radius)
        ships = [ShipPosition(**ship) for ship in ships_data]
        
        return AISResponse(
            status="success",
            ships=ships,
            message=f"Found {len(ships)} ships within {radius}km of {lat}, {lon}"
        )
    except Exception as e:
        return AISResponse(status="error", message=str(e))

@ais_router.get("/ais/ships/search", response_model=AISResponse)
async def search_ships_by_name(
    name: str = Query(..., description="Ship name to search for")
):
    """Search ships by name"""
    try:
        ships_data = ais_service.get_ships_by_name(name)
        ships = [ShipPosition(**ship) for ship in ships_data]
        
        return AISResponse(
            status="success",
            ships=ships,
            message=f"Found {len(ships)} ships matching '{name}'"
        )
    except Exception as e:
        return AISResponse(status="error", message=str(e))

@ais_router.get("/ais/ships/{mmsi}", response_model=AISResponse)
async def get_ship_by_mmsi(mmsi: str):
    """Get ship by MMSI"""
    try:
        ship_data = ais_service.get_ship_by_mmsi(mmsi)
        
        if not ship_data:
            return AISResponse(
                status="error", 
                message=f"Ship with MMSI {mmsi} not found"
            )
        
        ship = ShipPosition(**ship_data)
        return AISResponse(
            status="success",
            ships=[ship],
            message=f"Ship found: {ship.name or 'Unknown'}"
        )
    except Exception as e:
        return AISResponse(status="error", message=str(e))

@ais_router.get("/ais/traffic/port/{port_name}", response_model=AISResponse)
async def get_port_traffic(port_name: str):
    """Monitor traffic around major ports"""
    try:
        # Major port coordinates
        port_coords = {
            "singapore": (1.2966, 103.8006, 25),
            "rotterdam": (51.9225, 4.4792, 20),
            "shanghai": (31.2304, 121.4737, 30),
            "los_angeles": (33.7361, -118.2644, 25),
            "hamburg": (53.5511, 9.9937, 20),
            "new_york": (40.6892, -74.0445, 25),
            "dubai": (25.2769, 55.2962, 20),
            "antwerp": (51.2194, 4.4025, 15)
        }
        
        port_lower = port_name.lower().replace("-", "_")
        if port_lower not in port_coords:
            return AISResponse(
                status="error",
                message=f"Port '{port_name}' not found. Available: {list(port_coords.keys())}"
            )
        
        lat, lon, radius = port_coords[port_lower]
        ships_data = ais_service.get_ships_in_area(lat, lon, radius)
        ships = [ShipPosition(**ship) for ship in ships_data]
        
        return AISResponse(
            status="success",
            ships=ships,
            data={
                "port": port_name.title(),
                "coordinates": {"lat": lat, "lon": lon},
                "search_radius_km": radius,
                "ship_count": len(ships)
            },
            message=f"Traffic around {port_name.title()} port: {len(ships)} ships"
        )
        
    except Exception as e:
        return AISResponse(status="error", message=str(e))

@ais_router.post("/ais/control/start")
async def start_ais_collection():
    """Start AIS data collection"""
    try:
        await ais_service.start_background_collection()
        return AISResponse(
            status="success",
            message="AIS collection started"
        )
    except Exception as e:
        return AISResponse(status="error", message=str(e))

@ais_router.post("/ais/control/stop")
async def stop_ais_collection():
    """Stop AIS data collection"""
    try:
        ais_service.stop_collection()
        return AISResponse(
            status="success", 
            message="AIS collection stopped"
        )
    except Exception as e:
        return AISResponse(status="error", message=str(e))

@ais_router.get("/ais/demo")
async def ais_demo():
    """Demo endpoint showing AIS capabilities"""
    return {
        "ais_tracking_demo": {
            "description": "Real-time ship tracking using AIS data",
            "endpoints": {
                "status": "/api/ais/status",
                "search_area": "/api/ais/ships/area?lat=1.2966&lon=103.8006&radius=50",
                "search_name": "/api/ais/ships/search?name=maersk",
                "get_ship": "/api/ais/ships/123456789",
                "port_traffic": "/api/ais/traffic/port/singapore"
            },
            "example_queries": [
                "Find ships near Singapore",
                "Search for Maersk vessels",
                "Get ship with MMSI 123456789",
                "Show traffic around Rotterdam port"
            ],
            "integration": "AIS tools available in maritime agent at /api/agent/query"
        }
    }