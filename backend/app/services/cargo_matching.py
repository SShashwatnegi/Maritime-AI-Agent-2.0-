# app/services/cargo_matching.py
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import math

class VesselType(Enum):
    BULK_CARRIER = "bulk_carrier"
    CONTAINER = "container"
    TANKER = "tanker"
    GENERAL_CARGO = "general_cargo"
    RO_RO = "ro_ro"
    REEFER = "reefer"

class CargoType(Enum):
    DRY_BULK = "dry_bulk"
    LIQUID_BULK = "liquid_bulk"
    CONTAINERS = "containers"
    BREAKBULK = "breakbulk"
    VEHICLES = "vehicles"
    REFRIGERATED = "refrigerated"

@dataclass
class Vessel:
    """Vessel specification and availability"""
    id: str
    name: str
    vessel_type: VesselType
    dwt: float  # Deadweight tonnage
    capacity_teu: Optional[int] = None  # For container vessels
    capacity_cbm: Optional[float] = None  # Cubic meters
    speed_knots: float = 15.0
    fuel_consumption_mt_day: float = 35.0
    daily_hire_rate: float = 12000.0  # USD per day
    current_location: Dict[str, float] = None  # {"lat": x, "lon": y}
    laycan_start: datetime = None
    laycan_end: datetime = None
    next_available: datetime = None
    owner: str = ""
    flag: str = ""
    year_built: int = 2010
    cargo_gear: bool = False
    ice_class: bool = False

@dataclass
class Cargo:
    """Cargo specification and requirements"""
    id: str
    cargo_type: CargoType
    commodity: str
    quantity_mt: float
    quantity_teu: Optional[int] = None  # For containerized cargo
    volume_cbm: Optional[float] = None
    loading_port: str = ""
    discharge_port: str = ""
    laycan_start: datetime = None
    laycan_end: datetime = None
    freight_rate: float = 0.0  # USD per MT or per day
    freight_type: str = "voyage"  # "voyage" or "time_charter"
    special_requirements: List[str] = None
    charterer: str = ""
    stowage_factor: float = 1.5  # CBM per MT
    requires_cargo_gear: bool = False
    temperature_controlled: bool = False

@dataclass
class CargoMatch:
    """Matched cargo-vessel pairing with analysis"""
    vessel: Vessel
    cargo: Cargo
    compatibility_score: float  # 0-100
    profitability_score: float  # 0-100
    estimated_profit_usd: float
    voyage_duration_days: float
    distance_nm: float
    fuel_cost_usd: float
    port_costs_usd: float
    total_voyage_cost_usd: float
    gross_revenue_usd: float
    net_profit_usd: float
    profit_margin_percent: float
    ballast_distance_nm: float
    utilization_percent: float
    risks: List[str]
    recommendations: List[str]

class CargoMatchingService:
    """Intelligent Cargo & Tonnage Matching Assistant"""
    
    def __init__(self):
        # Sample vessels database (in production, connect to fleet management system)
        self.vessels_db = self._initialize_sample_vessels()
        
        # Sample cargo database (in production, connect to cargo booking system)
        self.cargo_db = self._initialize_sample_cargo()
        
        # Port coordinates for distance calculations
        self.port_coordinates = {
            "singapore": {"lat": 1.2966, "lon": 103.8006},
            "rotterdam": {"lat": 51.9225, "lon": 4.4792},
            "shanghai": {"lat": 31.2304, "lon": 121.4737},
            "new_york": {"lat": 40.6892, "lon": -74.0445},
            "los_angeles": {"lat": 33.7361, "lon": -118.2644},
            "hamburg": {"lat": 53.5511, "lon": 9.9937},
            "antwerp": {"lat": 51.2194, "lon": 4.4025},
            "busan": {"lat": 35.1796, "lon": 129.0756},
            "dubai": {"lat": 25.2769, "lon": 55.2962},
            "mumbai": {"lat": 19.0896, "lon": 72.8656},
            "santos": {"lat": -23.9618, "lon": -46.3322},
            "cape_town": {"lat": -33.9249, "lon": 18.4241}
        }
        
        # Market rates and costs
        self.fuel_price_usd_mt = 650.0
        self.port_cost_base = 15000.0  # Base port costs per call
        self.canal_fees = {
            "suez": 250000,
            "panama": 300000
        }

    def _initialize_sample_vessels(self) -> List[Vessel]:
        """Initialize sample vessel database"""
        now = datetime.now()
        return [
            Vessel(
                id="V001", name="Ocean Pioneer", vessel_type=VesselType.BULK_CARRIER,
                dwt=75000, speed_knots=14, fuel_consumption_mt_day=32,
                daily_hire_rate=11000, current_location={"lat": 1.2966, "lon": 103.8006},
                laycan_start=now + timedelta(days=5), laycan_end=now + timedelta(days=10),
                owner="Global Shipping Ltd", flag="Marshall Islands", year_built=2018,
                cargo_gear=True
            ),
            Vessel(
                id="V002", name="Container Express", vessel_type=VesselType.CONTAINER,
                dwt=65000, capacity_teu=5500, speed_knots=20, fuel_consumption_mt_day=45,
                daily_hire_rate=15000, current_location={"lat": 51.9225, "lon": 4.4792},
                laycan_start=now + timedelta(days=3), laycan_end=now + timedelta(days=8),
                owner="Maritime Carriers", flag="Liberia", year_built=2020
            ),
            Vessel(
                id="V003", name="Bulk Master", vessel_type=VesselType.BULK_CARRIER,
                dwt=180000, speed_knots=13, fuel_consumption_mt_day=55,
                daily_hire_rate=18000, current_location={"lat": -23.9618, "lon": -46.3322},
                laycan_start=now + timedelta(days=7), laycan_end=now + timedelta(days=12),
                owner="Dry Bulk Shipping", flag="Panama", year_built=2015,
                cargo_gear=False
            ),
            Vessel(
                id="V004", name="Chemical Carrier", vessel_type=VesselType.TANKER,
                dwt=45000, capacity_cbm=52000, speed_knots=14, fuel_consumption_mt_day=28,
                daily_hire_rate=13000, current_location={"lat": 25.2769, "lon": 55.2962},
                laycan_start=now + timedelta(days=4), laycan_end=now + timedelta(days=9),
                owner="Tanker Fleet Inc", flag="Singapore", year_built=2019
            )
        ]

    def _initialize_sample_cargo(self) -> List[Cargo]:
        """Initialize sample cargo database"""
        now = datetime.now()
        return [
            Cargo(
                id="C001", cargo_type=CargoType.DRY_BULK, commodity="Iron Ore",
                quantity_mt=70000, loading_port="santos", discharge_port="singapore",
                laycan_start=now + timedelta(days=6), laycan_end=now + timedelta(days=11),
                freight_rate=25.0, freight_type="voyage", charterer="Steel Corp",
                stowage_factor=0.4  # Dense cargo
            ),
            Cargo(
                id="C002", cargo_type=CargoType.CONTAINERS, commodity="Mixed Containers",
                quantity_teu=4500, loading_port="shanghai", discharge_port="rotterdam",
                laycan_start=now + timedelta(days=4), laycan_end=now + timedelta(days=9),
                freight_rate=1200.0, freight_type="voyage", charterer="Container Lines"
            ),
            Cargo(
                id="C003", cargo_type=CargoType.DRY_BULK, commodity="Coal",
                quantity_mt=150000, loading_port="new_york", discharge_port="hamburg",
                laycan_start=now + timedelta(days=8), laycan_end=now + timedelta(days=13),
                freight_rate=18.0, freight_type="voyage", charterer="Energy Trading",
                stowage_factor=1.2
            ),
            Cargo(
                id="C004", cargo_type=CargoType.LIQUID_BULK, commodity="Chemicals",
                quantity_mt=35000, volume_cbm=40000, loading_port="dubai", discharge_port="antwerp",
                laycan_start=now + timedelta(days=5), laycan_end=now + timedelta(days=10),
                freight_rate=45.0, freight_type="voyage", charterer="Chemicals Inc"
            )
        ]

    async def find_optimal_matches(self, 
                                 max_matches: int = 10,
                                 min_compatibility: float = 70.0,
                                 sort_by: str = "profitability") -> List[CargoMatch]:
        """
        Find optimal cargo-vessel matches based on compatibility and profitability
        
        Args:
            max_matches: Maximum number of matches to return
            min_compatibility: Minimum compatibility score threshold
            sort_by: Sorting criteria ("profitability", "compatibility", "utilization")
        """
        matches = []
        
        # Generate all possible cargo-vessel combinations
        for vessel in self.vessels_db:
            for cargo in self.cargo_db:
                match = await self._evaluate_match(vessel, cargo)
                
                if match and match.compatibility_score >= min_compatibility:
                    matches.append(match)
        
        # Sort matches based on criteria
        if sort_by == "profitability":
            matches.sort(key=lambda x: x.profitability_score, reverse=True)
        elif sort_by == "compatibility":
            matches.sort(key=lambda x: x.compatibility_score, reverse=True)
        elif sort_by == "utilization":
            matches.sort(key=lambda x: x.utilization_percent, reverse=True)
        
        return matches[:max_matches]

    async def _evaluate_match(self, vessel: Vessel, cargo: Cargo) -> Optional[CargoMatch]:
        """Evaluate compatibility and profitability of vessel-cargo match"""
        try:
            # Check basic compatibility
            compatibility_score = self._calculate_compatibility_score(vessel, cargo)
            if compatibility_score < 50:  # Skip obviously incompatible matches
                return None
            
            # Calculate voyage economics
            economics = await self._calculate_voyage_economics(vessel, cargo)
            if not economics:
                return None
            
            # Calculate profitability score
            profitability_score = self._calculate_profitability_score(economics)
            
            # Assess utilization
            utilization_percent = self._calculate_utilization(vessel, cargo)
            
            # Identify risks and recommendations
            risks = self._identify_risks(vessel, cargo, economics)
            recommendations = self._generate_recommendations(vessel, cargo, economics)
            
            return CargoMatch(
                vessel=vessel,
                cargo=cargo,
                compatibility_score=compatibility_score,
                profitability_score=profitability_score,
                estimated_profit_usd=economics["net_profit"],
                voyage_duration_days=economics["voyage_days"],
                distance_nm=economics["total_distance"],
                fuel_cost_usd=economics["fuel_cost"],
                port_costs_usd=economics["port_costs"],
                total_voyage_cost_usd=economics["total_costs"],
                gross_revenue_usd=economics["gross_revenue"],
                net_profit_usd=economics["net_profit"],
                profit_margin_percent=economics["profit_margin"],
                ballast_distance_nm=economics["ballast_distance"],
                utilization_percent=utilization_percent,
                risks=risks,
                recommendations=recommendations
            )
            
        except Exception as e:
            print(f"Error evaluating match {vessel.id}-{cargo.id}: {e}")
            return None

    def _calculate_compatibility_score(self, vessel: Vessel, cargo: Cargo) -> float:
        """Calculate compatibility score between vessel and cargo"""
        score = 0.0
        
        # Vessel type compatibility (40 points max)
        if self._vessel_cargo_type_compatible(vessel.vessel_type, cargo.cargo_type):
            score += 40
        else:
            return 0  # Incompatible vessel-cargo type
        
        # Capacity compatibility (30 points max)
        capacity_score = self._calculate_capacity_score(vessel, cargo)
        score += capacity_score * 0.3
        
        # Laycan compatibility (20 points max)
        laycan_score = self._calculate_laycan_compatibility(vessel, cargo)
        score += laycan_score * 0.2
        
        # Special requirements (10 points max)
        special_score = self._check_special_requirements(vessel, cargo)
        score += special_score * 0.1
        
        return min(100.0, score)

    def _vessel_cargo_type_compatible(self, vessel_type: VesselType, cargo_type: CargoType) -> bool:
        """Check if vessel type can carry cargo type"""
        compatibility_matrix = {
            VesselType.BULK_CARRIER: [CargoType.DRY_BULK],
            VesselType.CONTAINER: [CargoType.CONTAINERS],
            VesselType.TANKER: [CargoType.LIQUID_BULK],
            VesselType.GENERAL_CARGO: [CargoType.BREAKBULK, CargoType.DRY_BULK],
            VesselType.RO_RO: [CargoType.VEHICLES],
            VesselType.REEFER: [CargoType.REFRIGERATED, CargoType.CONTAINERS]
        }
        
        return cargo_type in compatibility_matrix.get(vessel_type, [])

    def _calculate_capacity_score(self, vessel: Vessel, cargo: Cargo) -> float:
        """Calculate capacity utilization score"""
        if cargo.cargo_type == CargoType.CONTAINERS:
            if vessel.capacity_teu and cargo.quantity_teu:
                utilization = cargo.quantity_teu / vessel.capacity_teu
                if 0.7 <= utilization <= 1.0:
                    return 100
                elif 0.5 <= utilization < 0.7:
                    return 80 * utilization / 0.7
                else:
                    return 50
        else:
            # Weight-based capacity check
            if cargo.quantity_mt <= vessel.dwt:
                utilization = cargo.quantity_mt / vessel.dwt
                if 0.7 <= utilization <= 0.95:
                    return 100
                elif 0.5 <= utilization < 0.7:
                    return 80 * utilization / 0.7
                else:
                    return 60
        
        return 0

    def _calculate_laycan_compatibility(self, vessel: Vessel, cargo: Cargo) -> float:
        """Calculate laycan compatibility score"""
        if not vessel.laycan_start or not cargo.laycan_start:
            return 50  # Assume moderate compatibility if dates not specified
        
        vessel_window = (vessel.laycan_start, vessel.laycan_end or vessel.laycan_start + timedelta(days=3))
        cargo_window = (cargo.laycan_start, cargo.laycan_end or cargo.laycan_start + timedelta(days=3))
        
        # Check for overlap
        overlap_start = max(vessel_window[0], cargo_window[0])
        overlap_end = min(vessel_window[1], cargo_window[1])
        
        if overlap_start <= overlap_end:
            overlap_days = (overlap_end - overlap_start).days
            if overlap_days >= 2:
                return 100
            elif overlap_days >= 1:
                return 80
            else:
                return 60
        else:
            # Check how far apart they are
            gap_days = min(abs((vessel_window[0] - cargo_window[1]).days),
                          abs((cargo_window[0] - vessel_window[1]).days))
            if gap_days <= 2:
                return 40
            elif gap_days <= 5:
                return 20
            else:
                return 0

    def _check_special_requirements(self, vessel: Vessel, cargo: Cargo) -> float:
        """Check if vessel meets special cargo requirements"""
        score = 100.0
        
        if cargo.special_requirements:
            for requirement in cargo.special_requirements:
                if requirement == "cargo_gear" and not vessel.cargo_gear:
                    score -= 50
                elif requirement == "ice_class" and not vessel.ice_class:
                    score -= 30
                elif requirement == "temperature_controlled" and vessel.vessel_type != VesselType.REEFER:
                    score -= 40
        
        return max(0.0, score)

    async def _calculate_voyage_economics(self, vessel: Vessel, cargo: Cargo) -> Optional[Dict]:
        """Calculate detailed voyage economics"""
        try:
            # Calculate distances
            ballast_distance = self._calculate_ballast_distance(vessel, cargo)
            laden_distance = self._calculate_laden_distance(cargo)
            total_distance = ballast_distance + laden_distance
            
            # Calculate voyage duration
            ballast_days = ballast_distance / (vessel.speed_knots * 24) if ballast_distance > 0 else 0
            laden_days = laden_distance / (vessel.speed_knots * 24)
            port_days = 3  # Estimated port time
            total_voyage_days = ballast_days + laden_days + port_days
            
            # Calculate costs
            fuel_cost = (total_distance / 24) * vessel.fuel_consumption_mt_day * self.fuel_price_usd_mt
            hire_cost = total_voyage_days * vessel.daily_hire_rate
            port_costs = self.port_cost_base * 2  # Loading and discharge ports
            canal_costs = self._calculate_canal_costs(cargo)
            total_costs = fuel_cost + hire_cost + port_costs + canal_costs
            
            # Calculate revenue
            if cargo.freight_type == "voyage":
                if cargo.cargo_type == CargoType.CONTAINERS:
                    gross_revenue = cargo.quantity_teu * cargo.freight_rate
                else:
                    gross_revenue = cargo.quantity_mt * cargo.freight_rate
            else:  # time charter
                gross_revenue = total_voyage_days * cargo.freight_rate
            
            # Calculate profit
            net_profit = gross_revenue - total_costs
            profit_margin = (net_profit / gross_revenue * 100) if gross_revenue > 0 else 0
            
            return {
                "ballast_distance": ballast_distance,
                "laden_distance": laden_distance,
                "total_distance": total_distance,
                "voyage_days": total_voyage_days,
                "fuel_cost": fuel_cost,
                "hire_cost": hire_cost,
                "port_costs": port_costs,
                "canal_costs": canal_costs,
                "total_costs": total_costs,
                "gross_revenue": gross_revenue,
                "net_profit": net_profit,
                "profit_margin": profit_margin
            }
            
        except Exception as e:
            print(f"Error calculating voyage economics: {e}")
            return None

    def _calculate_ballast_distance(self, vessel: Vessel, cargo: Cargo) -> float:
        """Calculate ballast leg distance"""
        if not vessel.current_location:
            return 0  # Assume vessel is already at loading port
        
        loading_port_coords = self.port_coordinates.get(cargo.loading_port.lower())
        if not loading_port_coords:
            return 500  # Default ballast distance estimate
        
        vessel_coords = vessel.current_location
        return self._calculate_distance(
            vessel_coords["lat"], vessel_coords["lon"],
            loading_port_coords["lat"], loading_port_coords["lon"]
        )

    def _calculate_laden_distance(self, cargo: Cargo) -> float:
        """Calculate laden voyage distance"""
        loading_coords = self.port_coordinates.get(cargo.loading_port.lower())
        discharge_coords = self.port_coordinates.get(cargo.discharge_port.lower())
        
        if not loading_coords or not discharge_coords:
            return 5000  # Default voyage distance estimate
        
        return self._calculate_distance(
            loading_coords["lat"], loading_coords["lon"],
            discharge_coords["lat"], discharge_coords["lon"]
        )

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great circle distance in nautical miles"""
        # Haversine formula
        R = 3440.065  # Earth radius in nautical miles
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c

    def _calculate_canal_costs(self, cargo: Cargo) -> float:
        """Estimate canal transit costs"""
        # Simplified logic - in practice would need route analysis
        if cargo.loading_port.lower() in ["dubai", "mumbai"] and cargo.discharge_port.lower() in ["rotterdam", "hamburg", "antwerp"]:
            return self.canal_fees["suez"]
        elif "new_york" in [cargo.loading_port.lower(), cargo.discharge_port.lower()] and any(port in [cargo.loading_port.lower(), cargo.discharge_port.lower()] for port in ["shanghai", "busan"]):
            return self.canal_fees["panama"]
        return 0

    def _calculate_profitability_score(self, economics: Dict) -> float:
        """Calculate profitability score based on voyage economics"""
        profit_margin = economics["profit_margin"]
        
        if profit_margin >= 20:
            return 100
        elif profit_margin >= 15:
            return 90
        elif profit_margin >= 10:
            return 80
        elif profit_margin >= 5:
            return 60
        elif profit_margin >= 0:
            return 40
        else:
            return 0

    def _calculate_utilization(self, vessel: Vessel, cargo: Cargo) -> float:
        """Calculate vessel utilization percentage"""
        if cargo.cargo_type == CargoType.CONTAINERS:
            if vessel.capacity_teu and cargo.quantity_teu:
                return min(100.0, (cargo.quantity_teu / vessel.capacity_teu) * 100)
        else:
            return min(100.0, (cargo.quantity_mt / vessel.dwt) * 100)
        
        return 0.0

    def _identify_risks(self, vessel: Vessel, cargo: Cargo, economics: Dict) -> List[str]:
        """Identify potential risks for the match"""
        risks = []
        
        if economics["profit_margin"] < 5:
            risks.append("Low profit margin - market volatility risk")
        
        if economics["voyage_days"] > 30:
            risks.append("Long voyage duration - exposure to market changes")
        
        if vessel.year_built < 2000:
            risks.append("Older vessel - higher maintenance and breakdown risk")
        
        if cargo.special_requirements and not all(self._vessel_meets_requirement(vessel, req) for req in cargo.special_requirements):
            risks.append("Special requirements may not be fully met")
        
        # Geographic risks
        high_risk_areas = ["gulf_of_aden", "gulf_of_guinea", "strait_of_malacca"]
        if any(area in cargo.loading_port.lower() or area in cargo.discharge_port.lower() for area in high_risk_areas):
            risks.append("Transit through high piracy risk areas")
        
        return risks

    def _vessel_meets_requirement(self, vessel: Vessel, requirement: str) -> bool:
        """Check if vessel meets specific requirement"""
        requirement_map = {
            "cargo_gear": vessel.cargo_gear,
            "ice_class": vessel.ice_class,
            "temperature_controlled": vessel.vessel_type == VesselType.REEFER
        }
        return requirement_map.get(requirement, True)

    def _generate_recommendations(self, vessel: Vessel, cargo: Cargo, economics: Dict) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        utilization = self._calculate_utilization(vessel, cargo)
        if utilization < 70:
            recommendations.append(f"Low utilization ({utilization:.1f}%) - consider partial cargo or backhaul opportunities")
        
        if economics["ballast_distance"] > 1000:
            recommendations.append("Long ballast leg - negotiate freight rate to offset positioning costs")
        
        if economics["profit_margin"] > 15:
            recommendations.append("High profitability - prioritize this match")
        
        if vessel.fuel_consumption_mt_day > 40:
            recommendations.append("High fuel consumption - consider slow steaming for cost savings")
        
        # Market timing recommendations
        laycan_gap = abs((vessel.laycan_start - cargo.laycan_start).days) if vessel.laycan_start and cargo.laycan_start else 0
        if laycan_gap <= 1:
            recommendations.append("Perfect laycan match - secure booking quickly")
        
        return recommendations

    # Additional methods for vessel and cargo management
    async def add_vessel(self, vessel: Vessel) -> bool:
        """Add new vessel to database"""
        if not any(v.id == vessel.id for v in self.vessels_db):
            self.vessels_db.append(vessel)
            return True
        return False

    async def add_cargo(self, cargo: Cargo) -> bool:
        """Add new cargo to database"""
        if not any(c.id == cargo.id for c in self.cargo_db):
            self.cargo_db.append(cargo)
            return True
        return False

    async def get_vessel_matches(self, vessel_id: str, max_matches: int = 5) -> List[CargoMatch]:
        """Get best cargo matches for specific vessel"""
        vessel = next((v for v in self.vessels_db if v.id == vessel_id), None)
        if not vessel:
            return []
        
        matches = []
        for cargo in self.cargo_db:
            match = await self._evaluate_match(vessel, cargo)
            if match and match.compatibility_score >= 60:
                matches.append(match)
        
        matches.sort(key=lambda x: x.profitability_score, reverse=True)
        return matches[:max_matches]

    async def get_cargo_matches(self, cargo_id: str, max_matches: int = 5) -> List[CargoMatch]:
        """Get best vessel matches for specific cargo"""
        cargo = next((c for c in self.cargo_db if c.id == cargo_id), None)
        if not cargo:
            return []
        
        matches = []
        for vessel in self.vessels_db:
            match = await self._evaluate_match(vessel, cargo)
            if match and match.compatibility_score >= 60:
                matches.append(match)
        
        matches.sort(key=lambda x: x.profitability_score, reverse=True)
        return matches[:max_matches]

    def get_service_status(self) -> Dict:
        """Get cargo matching service status"""
        return {
            "service": "Cargo & Tonnage Matching Assistant",
            "status": "operational",
            "database_stats": {
                "total_vessels": len(self.vessels_db),
                "total_cargo": len(self.cargo_db),
                "vessel_types": list(set(v.vessel_type.value for v in self.vessels_db)),
                "cargo_types": list(set(c.cargo_type.value for c in self.cargo_db))
            },
            "capabilities": [
                "Cargo-vessel compatibility analysis",
                "Profitability estimation",
                "Voyage economics calculation",
                "Risk assessment",
                "Optimization recommendations",
                "Real-time matching"
            ],
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat()
        }