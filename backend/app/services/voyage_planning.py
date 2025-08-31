# app/services/voyage_planning.py
import math
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from geopy.distance import geodesic
from app.services.weather import WeatherService
import asyncio

@dataclass
class Port:
    """Port information"""
    name: str
    lat: float
    lon: float
    country: str
    major_port: bool = True

@dataclass
class RouteSegment:
    """Individual route segment"""
    from_port: Port
    to_port: Port
    distance_nm: float
    estimated_time_hours: float
    fuel_consumption_mt: float
    weather_risk: float
    piracy_risk: float
    canal_fees_usd: float = 0.0

@dataclass
class VoyageRoute:
    """Complete voyage route"""
    origin: Port
    destination: Port
    segments: List[RouteSegment]
    total_distance_nm: float
    total_time_hours: float
    total_fuel_mt: float
    total_cost_usd: float
    weather_score: float
    safety_score: float
    efficiency_score: float
    waypoints: List[Dict]

class VoyagePlanningService:
    """Smart Voyage Planning & Optimization Service"""
    
    def __init__(self):
        self.weather_service = WeatherService()
        
        # Major world ports database (simplified)
        self.major_ports = {
            "singapore": Port("Singapore", 1.2966, 103.8006, "Singapore"),
            "rotterdam": Port("Rotterdam", 51.9225, 4.4792, "Netherlands"),
            "antwerp": Port("Antwerp", 51.2194, 4.4025, "Belgium"),
            "hamburg": Port("Hamburg", 53.5511, 9.9937, "Germany"),
            "los_angeles": Port("Los Angeles", 33.7361, -118.2644, "USA"),
            "long_beach": Port("Long Beach", 33.7701, -118.2437, "USA"),
            "shanghai": Port("Shanghai", 31.2304, 121.4737, "China"),
            "ningbo": Port("Ningbo", 29.8683, 121.544, "China"),
            "busan": Port("Busan", 35.1796, 129.0756, "South Korea"),
            "hong_kong": Port("Hong Kong", 22.3193, 114.1694, "Hong Kong"),
            "dubai": Port("Dubai", 25.2769, 55.2962, "UAE"),
            "suez": Port("Suez", 29.9668, 32.5498, "Egypt"),
            "panama": Port("Panama", 8.9824, -79.5199, "Panama"),
            "cape_town": Port("Cape Town", -33.9249, 18.4241, "South Africa"),
            "mumbai": Port("Mumbai", 19.0896, 72.8656, "India"),
            "santos": Port("Santos", -23.9618, -46.3322, "Brazil"),
            "new_york": Port("New York", 40.6892, -74.0445, "USA"),
            "felixstowe": Port("Felixstowe", 51.9542, 1.3464, "UK"),
            "le_havre": Port("Le Havre", 49.4944, 0.1079, "France"),
            "yokohama": Port("Yokohama", 35.4437, 139.6380, "Japan")
        }
        
        # Piracy risk zones (simplified risk scores 0-10)
        self.piracy_zones = [
            {"name": "Somalia/Gulf of Aden", "bounds": [(5, 40), (20, 60)], "risk": 8},
            {"name": "Nigeria/Gulf of Guinea", "bounds": [(-5, -5), (10, 10)], "risk": 7},
            {"name": "Strait of Malacca", "bounds": [(0, 95), (10, 105)], "risk": 4},
            {"name": "South China Sea", "bounds": [(5, 105), (25, 125)], "risk": 3},
            {"name": "Caribbean", "bounds": [(10, -85), (25, -60)], "risk": 3},
            {"name": "West Africa", "bounds": [(-10, -20), (15, 15)], "risk": 5}
        ]
        
        # Canal fees (simplified)
        self.canal_fees = {
            "suez": {"base_fee": 250000, "per_teu": 15},  # USD
            "panama": {"base_fee": 300000, "per_teu": 18},
            "kiel": {"base_fee": 5000, "per_teu": 2}
        }

    async def plan_optimal_route(self, 
                                origin: str, 
                                destination: str,
                                vessel_type: str = "container",
                                vessel_size_teu: int = 10000,
                                fuel_price_usd: float = 650.0,
                                priority: str = "balanced") -> Dict:
        """
        Plan optimal voyage route considering multiple factors
        
        Args:
            origin: Origin port name
            destination: Destination port name  
            vessel_type: Type of vessel (container, bulk, tanker)
            vessel_size_teu: Vessel capacity in TEU
            fuel_price_usd: Current fuel price per MT
            priority: Optimization priority (speed, cost, safety, balanced)
        """
        try:
            # Find origin and destination ports
            origin_port = await self._find_port(origin)
            destination_port = await self._find_port(destination)
            
            if not origin_port or not destination_port:
                raise ValueError(f"Could not find ports: {origin} -> {destination}")
            
            # Generate route alternatives
            routes = await self._generate_route_alternatives(
                origin_port, destination_port, vessel_type, vessel_size_teu
            )
            
            # Score and rank routes
            scored_routes = []
            for route in routes:
                score = await self._calculate_route_score(route, fuel_price_usd, priority)
                scored_routes.append((route, score))
            
            # Sort by score (higher is better)
            scored_routes.sort(key=lambda x: x[1]["total_score"], reverse=True)
            optimal_route = scored_routes[0][0]
            optimal_score = scored_routes[0][1]
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(optimal_route, scored_routes)
            
            return {
                "status": "success",
                "optimal_route": {
                    "route_name": f"{origin_port.name} → {destination_port.name}",
                    "total_distance_nm": optimal_route.total_distance_nm,
                    "estimated_duration_days": round(optimal_route.total_time_hours / 24, 1),
                    "total_fuel_consumption_mt": optimal_route.total_fuel_mt,
                    "estimated_fuel_cost_usd": round(optimal_route.total_fuel_mt * fuel_price_usd, 0),
                    "total_cost_usd": optimal_route.total_cost_usd,
                    "weather_score": optimal_route.weather_score,
                    "safety_score": optimal_route.safety_score,
                    "efficiency_score": optimal_route.efficiency_score,
                    "waypoints": optimal_route.waypoints
                },
                "route_analysis": optimal_score,
                "alternatives": [
                    {
                        "route_name": f"Alternative {i+1}",
                        "distance_nm": route.total_distance_nm,
                        "duration_days": round(route.total_time_hours / 24, 1),
                        "fuel_cost_usd": round(route.total_fuel_mt * fuel_price_usd, 0),
                        "total_score": score["total_score"]
                    }
                    for i, (route, score) in enumerate(scored_routes[1:4])  # Top 3 alternatives
                ],
                "recommendations": recommendations,
                "optimization_priority": priority,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def analyze_route_risks(self, waypoints: List[Dict]) -> Dict:
        """Analyze risks along a specific route"""
        try:
            risks = {
                "weather_risks": [],
                "piracy_risks": [],
                "congestion_risks": [],
                "overall_risk_score": 0.0
            }
            
            total_risk = 0.0
            
            for i, point in enumerate(waypoints):
                lat, lon = point["lat"], point["lon"]
                
                # Weather risk analysis
                try:
                    weather_forecast = await asyncio.to_thread(
                        self.weather_service.get_weather_forecast, lat, lon, 72
                    )
                    weather_risk = self._assess_weather_risk(weather_forecast)
                    if weather_risk > 5:
                        risks["weather_risks"].append({
                            "location": f"Point {i+1}",
                            "lat": lat, "lon": lon,
                            "risk_level": weather_risk,
                            "description": "Severe weather conditions expected"
                        })
                except:
                    weather_risk = 3  # Default moderate risk
                
                # Piracy risk analysis
                piracy_risk = self._assess_piracy_risk(lat, lon)
                if piracy_risk > 4:
                    risks["piracy_risks"].append({
                        "location": f"Point {i+1}",
                        "lat": lat, "lon": lon,
                        "risk_level": piracy_risk,
                        "description": self._get_piracy_zone_name(lat, lon)
                    })
                
                total_risk += weather_risk + piracy_risk
            
            risks["overall_risk_score"] = round(total_risk / len(waypoints), 1) if waypoints else 0
            
            return risks
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def calculate_fuel_optimization(self, 
                                        route_distance_nm: float,
                                        vessel_type: str,
                                        current_speed_knots: float,
                                        weather_conditions: List[Dict]) -> Dict:
        """Calculate fuel optimization suggestions"""
        try:
            # Base fuel consumption rates (MT/day) by vessel type
            fuel_rates = {
                "container": {"base": 45, "per_knot": 2.5},
                "bulk": {"base": 35, "per_knot": 2.0},
                "tanker": {"base": 40, "per_knot": 2.2},
                "general": {"base": 30, "per_knot": 1.8}
            }
            
            base_rate = fuel_rates.get(vessel_type, fuel_rates["general"])
            
            # Current consumption calculation
            voyage_days = route_distance_nm / (current_speed_knots * 24)
            current_daily_consumption = base_rate["base"] + (current_speed_knots * base_rate["per_knot"])
            current_total_fuel = current_daily_consumption * voyage_days
            
            # Optimal speed calculation considering weather
            weather_factor = self._calculate_weather_impact(weather_conditions)
            optimal_speed = self._calculate_optimal_speed(current_speed_knots, weather_factor)
            
            # Optimized consumption
            opt_voyage_days = route_distance_nm / (optimal_speed * 24)
            opt_daily_consumption = base_rate["base"] + (optimal_speed * base_rate["per_knot"])
            opt_total_fuel = opt_daily_consumption * opt_voyage_days
            
            fuel_savings = current_total_fuel - opt_total_fuel
            time_difference = opt_voyage_days - voyage_days
            
            return {
                "current_scenario": {
                    "speed_knots": current_speed_knots,
                    "voyage_days": round(voyage_days, 1),
                    "daily_fuel_mt": round(current_daily_consumption, 1),
                    "total_fuel_mt": round(current_total_fuel, 1)
                },
                "optimized_scenario": {
                    "recommended_speed_knots": round(optimal_speed, 1),
                    "voyage_days": round(opt_voyage_days, 1),
                    "daily_fuel_mt": round(opt_daily_consumption, 1),
                    "total_fuel_mt": round(opt_total_fuel, 1)
                },
                "savings": {
                    "fuel_saved_mt": round(fuel_savings, 1),
                    "fuel_saved_percent": round((fuel_savings/current_total_fuel)*100, 1),
                    "time_difference_days": round(time_difference, 1),
                    "cost_savings_usd": round(fuel_savings * 650, 0)  # Assuming $650/MT
                },
                "recommendations": self._generate_fuel_recommendations(fuel_savings, time_difference)
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _find_port(self, port_name: str) -> Optional[Port]:
        """Find port by name (fuzzy matching)"""
        port_name_lower = port_name.lower().replace(" ", "_")
        
        # Exact match
        if port_name_lower in self.major_ports:
            return self.major_ports[port_name_lower]
        
        # Partial match
        for key, port in self.major_ports.items():
            if port_name_lower in key or key in port_name_lower:
                return port
        
        return None

    async def _generate_route_alternatives(self, origin: Port, destination: Port, 
                                         vessel_type: str, vessel_size: int) -> List[VoyageRoute]:
        """Generate multiple route alternatives"""
        routes = []
        
        # Direct route
        direct_route = await self._create_direct_route(origin, destination, vessel_type, vessel_size)
        routes.append(direct_route)
        
        # Canal routes (if applicable)
        if self._requires_canal_transit(origin, destination):
            canal_routes = await self._create_canal_routes(origin, destination, vessel_type, vessel_size)
            routes.extend(canal_routes)
        
        # Alternative routes via major hubs
        hub_routes = await self._create_hub_routes(origin, destination, vessel_type, vessel_size)
        routes.extend(hub_routes)
        
        return routes

    async def _create_direct_route(self, origin: Port, destination: Port, 
                                 vessel_type: str, vessel_size: int) -> VoyageRoute:
        """Create direct point-to-point route"""
        distance_nm = self._calculate_distance(origin.lat, origin.lon, destination.lat, destination.lon)
        
        # Generate waypoints along great circle route
        waypoints = self._generate_waypoints(origin.lat, origin.lon, destination.lat, destination.lon)
        
        # Calculate route metrics
        fuel_consumption = self._estimate_fuel_consumption(distance_nm, vessel_type)
        estimated_time = self._estimate_voyage_time(distance_nm, vessel_type)
        
        # Assess risks along route
        weather_risk = await self._assess_route_weather_risk(waypoints)
        piracy_risk = self._assess_route_piracy_risk(waypoints)
        
        segment = RouteSegment(
            from_port=origin,
            to_port=destination,
            distance_nm=distance_nm,
            estimated_time_hours=estimated_time,
            fuel_consumption_mt=fuel_consumption,
            weather_risk=weather_risk,
            piracy_risk=piracy_risk
        )
        
        return VoyageRoute(
            origin=origin,
            destination=destination,
            segments=[segment],
            total_distance_nm=distance_nm,
            total_time_hours=estimated_time,
            total_fuel_mt=fuel_consumption,
            total_cost_usd=fuel_consumption * 650,  # Base cost estimate
            weather_score=10 - weather_risk,
            safety_score=10 - piracy_risk,
            efficiency_score=8.0,  # Direct routes are efficient
            waypoints=waypoints
        )

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great circle distance in nautical miles"""
        distance_km = geodesic((lat1, lon1), (lat2, lon2)).kilometers
        return distance_km * 0.539957  # Convert to nautical miles

    def _generate_waypoints(self, lat1: float, lon1: float, lat2: float, lon2: float, 
                          num_points: int = 10) -> List[Dict]:
        """Generate waypoints along great circle route"""
        waypoints = []
        
        for i in range(num_points + 1):
            fraction = i / num_points
            
            # Linear interpolation (simplified - should use great circle interpolation)
            lat = lat1 + (lat2 - lat1) * fraction
            lon = lon1 + (lon2 - lon1) * fraction
            
            waypoints.append({
                "lat": round(lat, 4),
                "lon": round(lon, 4),
                "sequence": i + 1
            })
        
        return waypoints

    def _estimate_fuel_consumption(self, distance_nm: float, vessel_type: str) -> float:
        """Estimate fuel consumption for voyage"""
        # Base consumption rates (MT per nautical mile)
        rates = {
            "container": 0.0045,
            "bulk": 0.0035,
            "tanker": 0.004,
            "general": 0.003
        }
        
        rate = rates.get(vessel_type, rates["general"])
        return distance_nm * rate

    def _estimate_voyage_time(self, distance_nm: float, vessel_type: str) -> float:
        """Estimate voyage time in hours"""
        # Average speeds by vessel type (knots)
        speeds = {
            "container": 20,
            "bulk": 14,
            "tanker": 15,
            "general": 16
        }
        
        speed = speeds.get(vessel_type, speeds["general"])
        return distance_nm / speed

    async def _assess_route_weather_risk(self, waypoints: List[Dict]) -> float:
        """Assess weather risk along route"""
        total_risk = 0.0
        risk_points = 0
        
        # Sample every few waypoints to avoid API limits
        for i in range(0, len(waypoints), max(1, len(waypoints)//5)):
            point = waypoints[i]
            try:
                # Get weather forecast for this point
                forecast = await asyncio.to_thread(
                    self.weather_service.get_weather_forecast, 
                    point["lat"], point["lon"], 48
                )
                risk = self._assess_weather_risk(forecast)
                total_risk += risk
                risk_points += 1
            except:
                total_risk += 3  # Default moderate risk
                risk_points += 1
        
        return total_risk / max(risk_points, 1)

    def _assess_weather_risk(self, forecast: List[Dict]) -> float:
        """Convert weather forecast to risk score (0-10)"""
        risk_score = 0
        
        for entry in forecast:
            condition = entry.get("condition", "").lower()
            
            # Risk scoring based on conditions
            if any(word in condition for word in ["storm", "severe", "hurricane"]):
                risk_score += 3
            elif any(word in condition for word in ["rain", "thunderstorm"]):
                risk_score += 2
            elif any(word in condition for word in ["fog", "mist"]):
                risk_score += 1.5
            elif any(word in condition for word in ["snow", "ice"]):
                risk_score += 2.5
        
        # Average risk over forecast period
        return min(10, risk_score / max(len(forecast), 1) * 3)

    def _assess_route_piracy_risk(self, waypoints: List[Dict]) -> float:
        """Assess piracy risk along route"""
        max_risk = 0
        
        for point in waypoints:
            risk = self._assess_piracy_risk(point["lat"], point["lon"])
            max_risk = max(max_risk, risk)
        
        return max_risk

    def _assess_piracy_risk(self, lat: float, lon: float) -> float:
        """Assess piracy risk at specific coordinates"""
        for zone in self.piracy_zones:
            bounds = zone["bounds"]
            if (bounds[0][0] <= lat <= bounds[1][0] and 
                bounds[0][1] <= lon <= bounds[1][1]):
                return zone["risk"]
        
        return 1.0  # Default low risk

    def _get_piracy_zone_name(self, lat: float, lon: float) -> str:
        """Get name of piracy zone at coordinates"""
        for zone in self.piracy_zones:
            bounds = zone["bounds"]
            if (bounds[0][0] <= lat <= bounds[1][0] and 
                bounds[0][1] <= lon <= bounds[1][1]):
                return zone["name"]
        
        return "Low risk area"

    async def _create_canal_routes(self, origin: Port, destination: Port, 
                                 vessel_type: str, vessel_size: int) -> List[VoyageRoute]:
        """Create routes through major canals"""
        # Simplified - would need more complex logic for actual canal routing
        return []

    async def _create_hub_routes(self, origin: Port, destination: Port, 
                               vessel_type: str, vessel_size: int) -> List[VoyageRoute]:
        """Create routes via major shipping hubs"""
        # Simplified - would route through Singapore, Rotterdam, etc.
        return []

    def _requires_canal_transit(self, origin: Port, destination: Port) -> bool:
        """Check if route might benefit from canal transit"""
        # Simplified logic
        origin_region = self._get_region(origin)
        dest_region = self._get_region(destination)
        
        return origin_region != dest_region

    def _get_region(self, port: Port) -> str:
        """Determine geographic region of port"""
        if port.lat > 30 and port.lon > -10 and port.lon < 40:
            return "Europe"
        elif port.lat > 0 and port.lon > 90:
            return "Asia"
        elif port.lat < 0 and port.lon > 90:
            return "Oceania"
        elif port.lon < -60:
            return "Americas"
        else:
            return "Other"

    async def _calculate_route_score(self, route: VoyageRoute, fuel_price: float, priority: str) -> Dict:
        """Calculate comprehensive route score"""
        # Base scores
        efficiency = 10 - (route.total_time_hours / 100)  # Time efficiency
        cost = 10 - (route.total_cost_usd / 100000)       # Cost efficiency  
        safety = route.safety_score
        weather = route.weather_score
        
        # Priority weighting
        weights = {
            "speed": {"efficiency": 0.5, "cost": 0.2, "safety": 0.2, "weather": 0.1},
            "cost": {"efficiency": 0.2, "cost": 0.5, "safety": 0.2, "weather": 0.1},
            "safety": {"efficiency": 0.2, "cost": 0.2, "safety": 0.4, "weather": 0.2},
            "balanced": {"efficiency": 0.25, "cost": 0.25, "safety": 0.25, "weather": 0.25}
        }
        
        weight = weights.get(priority, weights["balanced"])
        
        total_score = (
            efficiency * weight["efficiency"] +
            cost * weight["cost"] +
            safety * weight["safety"] +
            weather * weight["weather"]
        )
        
        return {
            "total_score": round(total_score, 2),
            "efficiency_score": round(efficiency, 2),
            "cost_score": round(cost, 2),
            "safety_score": round(safety, 2),
            "weather_score": round(weather, 2),
            "priority": priority
        }

    async def _generate_recommendations(self, optimal_route: VoyageRoute, 
                                      all_routes: List) -> List[str]:
        """Generate voyage planning recommendations"""
        recommendations = []
        
        # Fuel efficiency recommendations
        if optimal_route.total_fuel_mt > 500:
            recommendations.append("Consider slow steaming to reduce fuel consumption")
        
        # Weather recommendations  
        if optimal_route.weather_score < 6:
            recommendations.append("Monitor weather closely - rough conditions expected")
        
        # Safety recommendations
        if optimal_route.safety_score < 7:
            recommendations.append("Enhanced security measures recommended due to piracy risk")
        
        # Route alternatives
        if len(all_routes) > 1:
            recommendations.append("Multiple route options available - consider weather updates")
        
        return recommendations

    def _calculate_weather_impact(self, weather_conditions: List[Dict]) -> float:
        """Calculate weather impact on fuel consumption"""
        impact_factor = 1.0
        
        for condition in weather_conditions:
            desc = condition.get("condition", "").lower()
            if any(word in desc for word in ["storm", "rough"]):
                impact_factor += 0.2
            elif any(word in desc for word in ["rain", "wind"]):
                impact_factor += 0.1
        
        return min(impact_factor, 1.5)  # Cap at 50% increase

    def _calculate_optimal_speed(self, current_speed: float, weather_factor: float) -> float:
        """Calculate optimal speed considering weather"""
        # Reduce speed in bad weather for fuel efficiency
        if weather_factor > 1.2:
            return current_speed * 0.85
        elif weather_factor > 1.1:
            return current_speed * 0.9
        else:
            return current_speed * 1.05  # Can go slightly faster in good weather

    def _generate_fuel_recommendations(self, fuel_savings: float, time_difference: float) -> List[str]:
        """Generate fuel optimization recommendations"""
        recommendations = []
        
        if fuel_savings > 50:
            recommendations.append(f"Significant fuel savings possible: {fuel_savings:.1f} MT")
        
        if time_difference > 1:
            recommendations.append(f"Route will take {time_difference:.1f} days longer")
        elif time_difference < -1:
            recommendations.append(f"Route will be {abs(time_difference):.1f} days faster")
        
        if fuel_savings > 0 and time_difference < 2:
            recommendations.append("Recommended: Optimize for fuel efficiency")
        elif time_difference < -0.5:
            recommendations.append("Consider current speed for time savings")
        
        return recommendations