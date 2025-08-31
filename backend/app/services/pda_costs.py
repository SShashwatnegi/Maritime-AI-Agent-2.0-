# app/services/pda_costs.py
from typing import Dict, List, Optional
from datetime import datetime

class PDACostService:
    def __init__(self):
        # Baseline references (dummy dataset for now)
        self.port_charges = {
            "Singapore": 50000,
            "Rotterdam": 65000,
            "Dubai": 40000,
            "Hamburg": 55000
        }
        self.canal_fees = {
            "Suez Canal": 350000,
            "Panama Canal": 250000
        }
        self.agency_fee_default = 10000

        # Store actual voyage costs
        # Structure: {voyage_id: {recorded_at, estimate, actual}}
        self.records: Dict[str, Dict] = {}

    def estimate_pda(self, origin: str, destination: str, canals: Optional[List[str]] = None) -> Dict:
        """Estimate PDA costs for voyage."""
        estimate = {
            "origin_port_charges": self.port_charges.get(origin, 45000),
            "destination_port_charges": self.port_charges.get(destination, 45000),
            "agency_costs": self.agency_fee_default,
            "canal_fees": 0
        }

        if canals:
            for canal in canals:
                estimate["canal_fees"] += self.canal_fees.get(canal, 0)

        estimate["total_estimated_usd"] = sum(estimate.values())
        return estimate

    def record_actual_costs(
        self, voyage_id: str,
        actuals: Dict[str, float],
        estimate: Optional[Dict] = None
    ) -> Dict:
        """
        Record actual PDA costs.
        Expected keys in `actuals`: 
            - origin_port_charges
            - destination_port_charges
            - agency_costs
            - canal_fees
            - total_usd
        """
        record = {
            "recorded_at": datetime.utcnow().isoformat(),
            "actuals": actuals
        }

        if estimate:
            record["estimate"] = estimate

        self.records[voyage_id] = record
        return record

    def compare_estimate_vs_actual(self, voyage_id: str, estimate: Optional[Dict] = None) -> Dict:
        """Compare stored actual costs vs. estimate."""
        record = self.records.get(voyage_id)
        if not record:
            return {"error": f"No actual costs recorded for voyage {voyage_id}"}

        actual = record["actuals"]
        comparison = {
            "estimated_total": estimate["total_estimated_usd"] if estimate else record.get("estimate", {}).get("total_estimated_usd", 0),
            "actual_total": actual.get("total_usd", 0),
        }
        comparison["difference"] = comparison["actual_total"] - comparison["estimated_total"]
        return comparison
