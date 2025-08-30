# app/api/voyage_routes.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.services.voyage_planning import VoyagePlanningService
import asyncio

# Initialize router and service
voyage_router = APIRouter(prefix="/voyage", tags=["Voyage Planning"])
voyage_service = VoyagePlanningService()

# Pydantic models for request/response
class VoyageRequest(BaseModel):
    origin: str = Field(..., description="Origin port name", example="Singapore")
    destination: str = Field(..., description="Destination port name", example="Rotterdam")
    vessel_type: str = Field(default="container", description="Vessel type", 
                           pattern="^(container|bulk|tanker|general)$")   # ✅ FIXED
    vessel_size_teu: int = Field(default=10000, ge=1000, le=50000, 
                               description="Vessel size in TEU")
    fuel_price_usd: float = Field(default=650.0, ge=300, le=1200, 
                                description="Fuel price per MT in USD")
    priority: str = Field(default="balanced", description="Optimization priority",
                         pattern="^(speed|cost|safety|balanced)$")   # ✅ FIXED

class RouteAnalysisRequest(BaseModel):
    waypoints: List[Dict[str, float]] = Field(..., description="Route waypoints with lat/lon")

class FuelOptimizationRequest(BaseModel):
    route_distance_nm: float = Field(..., ge=1, le=50000, description="Route distance in nautical miles")
    vessel_type: str = Field(..., pattern="^(container|bulk|tanker|general)$")   # ✅ FIXED
    current_speed_knots: float = Field(..., ge=5, le=30, description="Current speed in knots")
    weather_conditions: List[Dict] = Field(default=[], description="Weather forecast data")

# -------------------------
# Route Risk Analysis
# -------------------------
@voyage_router.post("/analyze-risks",
                   summary="🛡️ Route Risk Analysis", 
                   description="Analyze weather, piracy, and other risks along a specific route")
async def analyze_route_risks(request: RouteAnalysisRequest):
    """
    **Comprehensive Route Risk Analysis**
    
    Evaluates risks along your planned route:
    - 🌪️ Weather hazards and severe conditions
    - 🏴‍☠️ Piracy threat zones and security risks
    - 🚢 Port congestion and traffic density
    - 📊 Overall risk scoring and recommendations
    """
    try:
        if not request.waypoints:
            raise HTTPException(status_code=400, detail="Waypoints are required")
        
        # Validate waypoints format
        for i, point in enumerate(request.waypoints):
            if "lat" not in point or "lon" not in point:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Waypoint {i+1} must contain 'lat' and 'lon' keys"
                )
        
        result = await voyage_service.analyze_route_risks(request.waypoints)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
            
        return {
            "status": "success",
            "route_analysis": result,
            "risk_summary": {
                "total_waypoints": len(request.waypoints),
                "weather_risk_points": len(result.get("weather_risks", [])),
                "piracy_risk_points": len(result.get("piracy_risks", [])),
                "overall_risk_level": "High" if result.get("overall_risk_score", 0) > 6 
                                    else "Medium" if result.get("overall_risk_score", 0) > 3 
                                    else "Low"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")

# -------------------------
# Fuel Optimization
# -------------------------
@voyage_router.post("/fuel-optimization",
                   summary="⛽ Fuel Consumption Optimization",
                   description="Calculate optimal speed and fuel consumption for your voyage")
async def optimize_fuel_consumption(request: FuelOptimizationRequest):
    """
    **Smart Fuel Optimization**
    
    Optimizes fuel consumption considering:
    - 🚢 Vessel characteristics and performance
    - 🌊 Weather conditions and sea state
    - ⚡ Speed vs. fuel efficiency curves
    - 💰 Cost savings calculations
    - ⏱️ Time vs. efficiency trade-offs
    """
    try:
        result = await voyage_service.calculate_fuel_optimization(
            route_distance_nm=request.route_distance_nm,
            vessel_type=request.vessel_type,
            current_speed_knots=request.current_speed_knots,
            weather_conditions=request.weather_conditions
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
            
        return {
            "status": "success",
            "fuel_optimization": result,
            "efficiency_summary": {
                "potential_savings_mt": result.get("savings", {}).get("fuel_saved_mt", 0),
                "cost_savings_usd": result.get("savings", {}).get("cost_savings_usd", 0),
                "efficiency_gain_percent": result.get("savings", {}).get("fuel_saved_percent", 0),
                "recommendation": "Optimize speed" if result.get("savings", {}).get("fuel_saved_mt", 0) > 10 
                                else "Current speed is efficient"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fuel optimization failed: {str(e)}")




# -------------------------
# Port Information
# -------------------------
@voyage_router.get("/ports",
                  summary="🏢 Major Ports Database",
                  description="Get information about major world ports")
async def get_major_ports(
    region: Optional[str] = Query(None, description="Filter by region"),
    search: Optional[str] = Query(None, description="Search port names")
):
    """
    **Major Ports Information**
    
    Access database of major world ports:
    - 📍 Port locations and coordinates
    - 🌍 Regional categorization
    - 🚢 Port capabilities and characteristics
    - 🔍 Search and filtering options
    """
    try:
        ports = voyage_service.major_ports
        port_list = []
        
        for key, port in ports.items():
            port_info = {
                "id": key,
                "name": port.name,
                "country": port.country,
                "latitude": port.lat,
                "longitude": port.lon,
                "major_port": port.major_port,
                "region": voyage_service._get_region(port)
            }
            
            # Apply filters
            if region and voyage_service._get_region(port).lower() != region.lower():
                continue
            if search and search.lower() not in port.name.lower():
                continue
                
            port_list.append(port_info)
        
        return {
            "status": "success",
            "ports": port_list,
            "total_ports": len(port_list),
            "regions_available": list(set(voyage_service._get_region(p) for p in ports.values())),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Port data retrieval failed: {str(e)}")

# -------------------------
# Piracy Risk Zones
# -------------------------
@voyage_router.get("/piracy-zones",
                  summary="🏴‍☠️ Piracy Risk Zones",
                  description="Get current piracy risk zones and threat levels")
async def get_piracy_zones():
    """
    **Global Piracy Risk Assessment**
    
    Current piracy threat information:
    - 📍 High-risk maritime zones
    - ⚠️ Threat level classifications
    - 🗺️ Geographic boundaries
    - 📊 Risk scoring system (1-10 scale)
    """
    try:
        zones = []
        for zone in voyage_service.piracy_zones:
            zones.append({
                "name": zone["name"],
                "risk_level": zone["risk"],
                "risk_category": "Critical" if zone["risk"] >= 8 else
                              "High" if zone["risk"] >= 6 else
                              "Medium" if zone["risk"] >= 4 else "Low",
                "boundaries": {
                    "southwest": {"lat": zone["bounds"][0][0], "lon": zone["bounds"][0][1]},
                    "northeast": {"lat": zone["bounds"][1][0], "lon": zone["bounds"][1][1]}
                }
            })
        
        return {
            "status": "success",
            "piracy_zones": zones,
            "total_zones": len(zones),
            "risk_scale": {
                "1-3": "Low Risk",
                "4-5": "Medium Risk", 
                "6-7": "High Risk",
                "8-10": "Critical Risk"
            },
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Piracy data retrieval failed: {str(e)}")

# -------------------------
# Route Comparison
# -------------------------
@voyage_router.post("/compare-routes",
                   summary="⚖️ Route Comparison",
                   description="Compare multiple route options side by side")
async def compare_routes(
    origin: str = Query(..., description="Origin port"),
    destination: str = Query(..., description="Destination port"),
    vessel_type: str = Query(default="container"),
    priorities: List[str] = Query(default=["balanced", "cost", "speed"], 
                                description="Optimization priorities to compare")
):
    """
    **Multi-Priority Route Comparison**
    
    Compare routes optimized for different priorities:
    - 💰 Cost-optimized route
    - ⚡ Speed-optimized route  
    - 🛡️ Safety-optimized route
    - ⚖️ Balanced approach
    - 📊 Side-by-side comparison metrics
    """
    try:
        comparisons = []
        
        for priority in priorities:
            if priority not in ["speed", "cost", "safety", "balanced"]:
                continue
                
            result = await voyage_service.plan_optimal_route(
                origin=origin,
                destination=destination,
                vessel_type=vessel_type,
                priority=priority
            )
            
            if result.get("status") == "success":
                comparisons.append({
                    "priority": priority,
                    "route_summary": result.get("optimal_route", {}),
                    "scores": result.get("route_analysis", {})
                })
        
        if not comparisons:
            raise HTTPException(status_code=400, detail="No valid routes found for comparison")
        
        # Find best route for each metric
        best_analysis = {
            "shortest_distance": min(comparisons, key=lambda x: x["route_summary"].get("total_distance_nm", float('inf'))),
            "fastest_route": min(comparisons, key=lambda x: x["route_summary"].get("estimated_duration_days", float('inf'))),
            "lowest_cost": min(comparisons, key=lambda x: x["route_summary"].get("total_cost_usd", float('inf'))),
            "highest_safety": max(comparisons, key=lambda x: x["route_summary"].get("safety_score", 0))
        }
        
        return {
            "status": "success",
            "route_comparisons": comparisons,
            "best_in_category": {
                category: {
                    "priority": route["priority"],
                    "value": route["route_summary"].get(
                        "total_distance_nm" if "distance" in category else
                        "estimated_duration_days" if "fastest" in category else
                        "total_cost_usd" if "cost" in category else
                        "safety_score"
                    )
                }
                for category, route in best_analysis.items()
            },
            "comparison_timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route comparison failed: {str(e)}")

# -------------------------
# Voyage Planning Tools Summary
# -------------------------
@voyage_router.get("/tools",
                  summary="🛠️ Available Planning Tools",
                  description="Get overview of all voyage planning capabilities")
async def get_planning_tools():
    """
    **Voyage Planning Tools Overview**
    
    Complete toolkit for maritime voyage optimization:
    - 🎯 Route optimization with multiple priorities
    - 🛡️ Risk analysis and threat assessment  
    - ⛽ Fuel consumption optimization
    - 🏢 Major ports database
    - 🏴‍☠️ Piracy risk zones mapping
    - ⚖️ Multi-route comparison
    """
    return {
        "status": "success",
        "available_tools": {
            "route_optimization": {
                "endpoint": "/voyage/optimize",
                "description": "Generate optimal routes considering weather, safety, cost, and efficiency",
                "features": ["Multi-factor optimization", "Weather integration", "Cost analysis"]
            },
            "risk_analysis": {
                "endpoint": "/voyage/analyze-risks", 
                "description": "Analyze risks along specific routes",
                "features": ["Weather hazards", "Piracy threats", "Risk scoring"]
            },
            "fuel_optimization": {
                "endpoint": "/voyage/fuel-optimization",
                "description": "Optimize fuel consumption and speed",
                "features": ["Speed optimization", "Cost savings", "Environmental impact"]
            },
            "port_database": {
                "endpoint": "/voyage/ports",
                "description": "Access major world ports information",
                "features": ["Global coverage", "Search & filtering", "Port details"]
            },
            "piracy_zones": {
                "endpoint": "/voyage/piracy-zones",
                "description": "Current piracy risk zones",
                "features": ["Risk levels", "Geographic boundaries", "Threat assessment"]
            },
            "route_comparison": {
                "endpoint": "/voyage/compare-routes",
                "description": "Compare multiple route optimization strategies",
                "features": ["Multi-priority comparison", "Best-in-class analysis", "Decision support"]
            }
        },
        "supported_vessel_types": ["container", "bulk", "tanker", "general"],
        "optimization_priorities": ["speed", "cost", "safety", "balanced"],
        "service_version": "1.0.0",
        "last_updated": datetime.now().isoformat()
    }
# Optimal Route Planning
# -------------------------
@voyage_router.post("/optimize", 
                   summary="🎯 Smart Route Optimization",
                   description="Generate optimal voyage routes considering weather, piracy, costs, and efficiency")
async def optimize_voyage_route(request: VoyageRequest):
    """
    **Smart Voyage Planning & Optimization**
    
    Analyzes multiple factors to suggest the best route:
    - 🌦️ Weather conditions and forecasts
    - 🏴‍☠️ Piracy risk zones  
    - ⛽ Fuel consumption optimization
    - 💰 Canal fees and operational costs
    - ⏱️ Time efficiency
    - 🛡️ Safety considerations
    """
    try:
        result = await voyage_service.plan_optimal_route(
            origin=request.origin,
            destination=request.destination,
            vessel_type=request.vessel_type,
            vessel_size_teu=request.vessel_size_teu,
            fuel_price_usd=request.fuel_price_usd,
            priority=request.priority
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route optimization failed: {str(e)}")

# -------------------------