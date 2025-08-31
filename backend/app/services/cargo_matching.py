import random
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from geopy.distance import geodesic
from app.services.voyage_planning import VoyagePlanningService


class VesselType(Enum):
    CONTAINER = "container"
    BULK = "bulk"
    TANKER = "tanker"
    GENERAL = "general"

class CargoType(Enum):
    CONTAINER = "container"
    BULK = "bulk"
    LIQUID = "liquid"
    GENERAL = "general"

@dataclass
class Vessel:
    id: str
    name: str
    vessel_type: VesselType
    dwt: float
    current_position: Tuple[float, float]
    next_available_date: datetime
    daily_operating_cost: float
    fuel_consumption_mt_day: float

@dataclass
class CargoOpportunity:
    id: str
    description: str
    cargo_type: CargoType
    quantity_mt: float
    origin_port: str
    destination_port: str
    origin_coords: Tuple[float, float]
    destination_coords: Tuple[float, float]
    laycan_start: datetime
    laycan_end: datetime
    freight_rate_usd_mt: float

@dataclass
class CargoVesselMatch:
    vessel: Vessel
    cargo: CargoOpportunity
    profitability_usd: float
    profit_margin_percent: float
    compatibility_score: float
    voyage_duration_days: float
    risk_score: float

class CargoMatchingService:
    def __init__(self):
        self.vessels: List[Vessel] = []
        self.cargo_opportunities: List[CargoOpportunity] = []
        self.voyage_service = VoyagePlanningService()
        
        # Genetic Algorithm Parameters
        self.population_size = 50
        self.max_generations = 100
        self.mutation_rate = 0.1
        self.epsilon = 0.01  # Threshold for dU/dt
        self.k_steps = 5     # Number of steps for convergence check
        self.exploration_temp = 1.0  # High temperature for exploration
        self.exploitation_temp = 0.1 # Low temperature for exploitation

    def add_vessel(self, vessel: Vessel):
        self.vessels.append(vessel)

    def add_cargo_opportunity(self, cargo: CargoOpportunity):
        self.cargo_opportunities.append(cargo)

    async def find_optimal_matches(self, vessel_id: Optional[str] = None, cargo_id: Optional[str] = None, top_n: int = 10) -> List[CargoVesselMatch]:
        """
        Find optimal cargo-vessel matches using genetic algorithm with adaptive phases.
        """
        try:
            # Filter vessels and cargos based on input
            vessels = [v for v in self.vessels if vessel_id is None or v.id == vessel_id]
            cargos = [c for c in self.cargo_opportunities if cargo_id is None or c.id == cargo_id]
            
            if not vessels or not cargos:
                return []

            # Initialize population (random vessel-cargo pairings)
            population = self._initialize_population(vessels, cargos)
            best_fitness_history = []
            phase = "exploration"
            current_temp = self.exploration_temp
            stagnant_steps = 0
            prev_best_fitness = None

            for generation in range(self.max_generations):
                # Evaluate fitness for all individuals
                evaluated_population = []
                for individual in population:
                    match = self._create_match(individual, vessels, cargos)
                    if match:
                        fitness = self._calculate_fitness(match)
                        evaluated_population.append((individual, fitness, match))
                
                # Sort by fitness (descending)
                evaluated_population.sort(key=lambda x: x[1], reverse=True)
                best_fitness = evaluated_population[0][1] if evaluated_population else 0
                best_matches = [match for _, _, match in evaluated_population if match][:top_n]

                # Check for phase transition
                if prev_best_fitness is not None:
                    fitness_change = abs(best_fitness - prev_best_fitness)
                    if fitness_change < self.epsilon:
                        stagnant_steps += 1
                    else:
                        stagnant_steps = 0

                    if stagnant_steps >= self.k_steps and phase == "exploration":
                        phase = "exploitation"
                        current_temp = self.exploitation_temp

                prev_best_fitness = best_fitness
                best_fitness_history.append(best_fitness)

                # Generate next population
                population = self._evolve_population(evaluated_population, vessels, cargos, current_temp)

                # Early stopping if convergence is stable
                if generation > 20 and max(best_fitness_history[-10:]) - min(best_fitness_history[-10:]) < self.epsilon:
                    break

            # Return top matches
            return [match for _, _, match in sorted(evaluated_population, key=lambda x: x[1], reverse=True)[:top_n]]

        except Exception as e:
            print(f"Error in find_optimal_matches: {e}")
            return []

    def _initialize_population(self, vessels: List[Vessel], cargos: List[CargoOpportunity]) -> List[List[Tuple[int, int]]]:
        """Initialize random population of vessel-cargo pairings."""
        population = []
        for _ in range(self.population_size):
            individual = []
            used_vessels = set()
            used_cargos = set()
            for _ in range(min(len(vessels), len(cargos))):
                v_idx = random.randint(0, len(vessels) - 1)
                c_idx = random.randint(0, len(cargos) - 1)
                while v_idx in used_vessels or c_idx in used_cargos:
                    v_idx = random.randint(0, len(vessels) - 1)
                    c_idx = random.randint(0, len(cargos) - 1)
                individual.append((v_idx, c_idx))
                used_vessels.add(v_idx)
                used_cargos.add(c_idx)
            population.append(individual)
        return population

    def _create_match(self, individual: List[Tuple[int, int]], vessels: List[Vessel], cargos: List[CargoOpportunity]) -> Optional[CargoVesselMatch]:
        """Create a CargoVesselMatch from an individual (vessel_idx, cargo_idx pair)."""
        try:
            v_idx, c_idx = individual[0]  # Process first pair for simplicity
            vessel = vessels[v_idx]
            cargo = cargos[c_idx]

            economics = self.calculate_voyage_economics(vessel, cargo)
            compatibility = self.assess_vessel_cargo_compatibility(vessel, cargo)
            risks, _ = self.assess_risks_and_recommendations(vessel, cargo, economics)

            risk_score = sum(float(r.split(': ')[1].split('/')[0]) for r in risks if ':' in r) / max(len(risks), 1)

            return CargoVesselMatch(
                vessel=vessel,
                cargo=cargo,
                profitability_usd=economics["net_profit"],
                profit_margin_percent=economics["profit_margin"],
                compatibility_score=compatibility,
                voyage_duration_days=economics["total_voyage_days"],
                risk_score=risk_score
            )
        except:
            return None

    def _calculate_fitness(self, match: CargoVesselMatch) -> float:
        """Calculate fitness: U = profit_margin + compatibility - risk_penalty."""
        return match.profit_margin_percent / 100 + match.compatibility_score - match.risk_score

    def _evolve_population(self, evaluated_population: List[Tuple[List[Tuple[int, int]], float, CargoVesselMatch]], 
                          vessels: List[Vessel], cargos: List[CargoOpportunity], temperature: float) -> List[List[Tuple[int, int]]]:
        """Evolve population using selection, crossover, and mutation."""
        new_population = []
        elite_size = int(self.population_size * 0.1)  # Keep top 10%

        # Elitism: Keep best individuals
        for individual, _, _ in evaluated_population[:elite_size]:
            new_population.append(individual)

        # Generate new individuals
        while len(new_population) < self.population_size:
            # Selection (tournament)
            parent1 = self._tournament_selection(evaluated_population, temperature)
            parent2 = self._tournament_selection(evaluated_population, temperature)

            # Crossover
            child = self._crossover(parent1, parent2, vessels, cargos)

            # Mutation
            if random.random() < self.mutation_rate * temperature:
                child = self._mutate(child, vessels, cargos)

            new_population.append(child)

        return new_population

    def _tournament_selection(self, population: List[Tuple[List[Tuple[int, int]], float, CargoVesselMatch]], temperature: float) -> List[Tuple[int, int]]:
        """Select individual using tournament selection with temperature-based randomness."""
        tournament_size = 5
        tournament = random.sample(population, min(tournament_size, len(population)))
        if random.random() < temperature:
            return random.choice(tournament)[0]  # Random selection in exploration phase
        return max(tournament, key=lambda x: x[1])[0]  # Best fitness in exploitation phase

    def _crossover(self, parent1: List[Tuple[int, int]], parent2: List[Tuple[int, int]], 
                   vessels: List[Vessel], cargos: List[CargoOpportunity]) -> List[Tuple[int, int]]:
        """Perform crossover between two parents."""
        if not parent1 or not parent2:
            return parent1 or parent2 or []

        child = []
        length = min(len(parent1), len(parent2))
        crossover_point = random.randint(0, length)
        used_vessels = set()
        used_cargos = set()

        # Take first part from parent1
        for pair in parent1[:crossover_point]:
            if pair[0] not in used_vessels and pair[1] not in used_cargos:
                child.append(pair)
                used_vessels.add(pair[0])
                used_cargos.add(pair[1])

        # Complete with parent2
        for pair in parent2:
            if pair[0] not in used_vessels and pair[1] not in used_cargos:
                child.append(pair)
                used_vessels.add(pair[0])
                used_cargos.add(pair[1])

        return child

    def _mutate(self, individual: List[Tuple[int, int]], vessels: List[Vessel], cargos: List[CargoOpportunity]) -> List[Tuple[int, int]]:
        """Mutate an individual by swapping a vessel-cargo pair."""
        if not individual:
            return individual
        idx = random.randint(0, len(individual) - 1)
        v_idx = random.randint(0, len(vessels) - 1)
        c_idx = random.randint(0, len(cargos) - 1)
        individual[idx] = (v_idx, c_idx)
        return individual

    def assess_vessel_cargo_compatibility(self, vessel: Vessel, cargo: CargoOpportunity) -> float:
        """Assess compatibility between vessel and cargo (0-10)."""
        score = 10.0

        # Type compatibility
        type_map = {
            (VesselType.CONTAINER, CargoType.CONTAINER): 1.0,
            (VesselType.BULK, CargoType.BULK): 1.0,
            (VesselType.TANKER, CargoType.LIQUID): 1.0,
            (VesselType.GENERAL, CargoType.GENERAL): 1.0,
            (VesselType.GENERAL, CargoType.BULK): 0.8,
            (VesselType.GENERAL, CargoType.CONTAINER): 0.7
        }
        type_score = type_map.get((vessel.vessel_type, cargo.cargo_type), 0.5)
        score *= type_score

        # Capacity check
        if cargo.quantity_mt > vessel.dwt:
            score *= 0.2  # Severe penalty for insufficient capacity
        elif cargo.quantity_mt < vessel.dwt * 0.5:
            score *= 0.8  # Penalty for underutilization

        # Availability check
        if vessel.next_available_date > cargo.laycan_end:
            score *= 0.3  # Severe penalty for unavailable vessel
        elif vessel.next_available_date < cargo.laycan_start:
            score *= 0.9  # Slight penalty for early availability

        return min(10.0, score)

    def calculate_voyage_economics(self, vessel: Vessel, cargo: CargoOpportunity) -> dict:
        """Calculate voyage economics."""
        try:
            route = asyncio.run(self.voyage_service.plan_optimal_route(
                origin=cargo.origin_port,
                destination=cargo.destination_port,
                vessel_type=vessel.vessel_type.value,
                priority="cost"
            ))

            if route.get("status") == "error":
                return {"error": route["message"]}

            distance_nm = route["optimal_route"]["total_distance_nm"]
            voyage_days = route["optimal_route"]["estimated_duration_days"]
            fuel_mt = route["optimal_route"]["total_fuel_consumption_mt"]

            # Calculate costs
            fuel_cost = fuel_mt * 650  # Assuming $650/MT
            operating_cost = vessel.daily_operating_cost * voyage_days
            total_costs = fuel_cost + operating_cost

            # Calculate revenue
            gross_revenue = cargo.quantity_mt * cargo.freight_rate_usd_mt
            net_profit = gross_revenue - total_costs
            profit_margin = (net_profit / gross_revenue * 100) if gross_revenue > 0 else 0

            return {
                "gross_revenue": gross_revenue,
                "total_costs": total_costs,
                "net_profit": net_profit,
                "profit_margin": profit_margin,
                "total_voyage_days": voyage_days
            }
        except Exception as e:
            return {"error": str(e)}

    def assess_risks_and_recommendations(self, vessel: Vessel, cargo: CargoOpportunity, economics: dict) -> Tuple[List[str], List[str]]:
        """Assess risks and provide recommendations."""
        risks = []
        recommendations = []

        # Check compatibility
        compatibility = self.assess_vessel_cargo_compatibility(vessel, cargo)
        if compatibility < 3:
            risks.append(f"Low compatibility: {compatibility:.1f}/10")
            recommendations.append("Consider alternative vessel or cargo type")

        # Check economics
        if economics.get("net_profit", 0) < 0:
            risks.append("Negative profitability")
            recommendations.append("Reevaluate freight rate or optimize route")

        # Check voyage duration
        if economics.get("total_voyage_days", 0) > 30:
            risks.append(f"Long voyage: {economics['total_voyage_days']:.1f} days")
            recommendations.append("Consider intermediate ports for efficiency")

        # Weather and piracy risks
        waypoints = asyncio.run(self.voyage_service.plan_optimal_route(
            cargo.origin_port, cargo.destination_port, vessel.vessel_type.value, "safety"
        )).get("optimal_route", {}).get("waypoints", [])
        route_risks = asyncio.run(self.voyage_service.analyze_route_risks(waypoints))
        
        if route_risks.get("overall_risk_score", 0) > 7:
            risks.append(f"High route risk: {route_risks['overall_risk_score']}/10")
            recommendations.append("Implement enhanced security and weather monitoring")

        return risks, recommendations

    async def analyze_market_opportunities(self, vessel_type: Optional[VesselType] = None) -> dict:
        """Analyze market conditions and opportunities."""
        total_cargo_mt = sum(c.quantity_mt for c in self.cargo_opportunities)
        total_vessel_capacity = sum(v.dwt for v in self.vessels if vessel_type is None or v.vessel_type == vessel_type)
        
        supply_demand_ratio = total_vessel_capacity / total_cargo_mt if total_cargo_mt > 0 else 0
        market_condition = "Balanced" if 0.8 <= supply_demand_ratio <= 1.2 else \
                         "Oversupply" if supply_demand_ratio > 1.2 else "Undersupply"
        
        freight_rates = {}
        for cargo_type in CargoType:
            cargos = [c for c in self.cargo_opportunities if c.cargo_type == cargo_type]
            if cargos:
                avg_rate = sum(c.freight_rate_usd_mt for c in cargos) / len(cargos)
                freight_rates[cargo_type.value] = avg_rate

        recommendations = []
        if supply_demand_ratio > 1.5:
            recommendations.append("Consider repositioning vessels to higher-demand regions")
        elif supply_demand_ratio < 0.5:
            recommendations.append("Explore additional cargo opportunities")
        
        return {
            "market_overview": {
                "total_cargo_available_mt": total_cargo_mt,
                "total_vessel_capacity_mt": total_vessel_capacity,
                "supply_demand_ratio": round(supply_demand_ratio, 2),
                "market_condition": market_condition
            },
            "average_freight_rates": freight_rates,
            "recommendations": recommendations
        }

    def get_vessel_utilization_forecast(self, vessel_id: str, days_ahead: int) -> dict:
        """Forecast vessel utilization and revenue."""
        vessel = next((v for v in self.vessels if v.id == vessel_id), None)
        if not vessel:
            return {"error": f"Vessel {vessel_id} not found"}

        matches = asyncio.run(self.find_optimal_matches(vessel_id=vessel_id, top_n=10))
        if not matches:
            return {"error": "No cargo matches found for vessel"}

        potential_matches = sum(1 for m in matches if m.cargo.laycan_start <= vessel.next_available_date + timedelta(days=days_ahead))
        total_revenue = sum(m.profitability_usd for m in matches)
        utilization_days = sum(m.voyage_duration_days for m in matches)
        utilization_percent = (utilization_days / days_ahead) * 100 if days_ahead > 0 else 0

        top_opportunities = [
            {
                "cargo_id": m.cargo.id,
                "voyage_days": m.voyage_duration_days,
                "profitability": m.profitability_usd,
                "laycan_start": m.cargo.laycan_start.strftime("%Y-%m-%d")
            }
            for m in matches[:3]
        ]

        return {
            "potential_matches": potential_matches,
            "estimated_utilization_percent": utilization_percent,
            "projected_revenue_usd": total_revenue,
            "top_opportunities": top_opportunities
        }