from datetime import datetime, timedelta

class LaytimeCalculator:
    """
    Service class for calculating laytime, demurrage, and despatch.
    """

    def __init__(self, allowed_hours: int, demurrage_rate: float = 0.0, despatch_rate: float = 0.0):
        self.allowed_hours = allowed_hours
        self.demurrage_rate = demurrage_rate
        self.despatch_rate = despatch_rate

    def calculate(self, arrival: datetime, nor: datetime, completion: datetime, excluded_periods=None) -> dict:
        """
        Calculate laytime usage.
        - arrival: vessel arrival time
        - nor: notice of readiness tendered time
        - completion: cargo operations completion time
        - excluded_periods: list of (start, end) datetime ranges to exclude (holidays/weather)

        Returns a dict with laytime used, balance, demurrage/despatch.
        """
        if excluded_periods is None:
            excluded_periods = []

        # Laytime starts at NOR
        total_time = completion - nor

        # Deduct excluded periods (bad weather, strikes, etc.)
        excluded = timedelta()
        for start, end in excluded_periods:
            overlap_start = max(nor, start)
            overlap_end = min(completion, end)
            if overlap_start < overlap_end:
                excluded += (overlap_end - overlap_start)

        effective_time = total_time - excluded
        used_hours = effective_time.total_seconds() / 3600.0
        balance_hours = self.allowed_hours - used_hours

        # Financials
        demurrage = 0.0
        despatch = 0.0
        if used_hours > self.allowed_hours and self.demurrage_rate:
            demurrage = (used_hours - self.allowed_hours) * self.demurrage_rate
        elif used_hours < self.allowed_hours and self.despatch_rate:
            despatch = (self.allowed_hours - used_hours) * self.despatch_rate

        return {
            "arrival": arrival,
            "nor": nor,
            "completion": completion,
            "total_time_hours": round(total_time.total_seconds() / 3600.0, 2),
            "excluded_hours": round(excluded.total_seconds() / 3600.0, 2),
            "used_hours": round(used_hours, 2),
            "allowed_hours": self.allowed_hours,
            "balance_hours": round(balance_hours, 2),
            "demurrage": round(demurrage, 2),
            "despatch": round(despatch, 2),
        }
