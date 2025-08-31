# app/services/ais_service.py
import asyncio
import websockets
import json
import csv
import time
from datetime import datetime
from typing import Dict, List, Optional

class AISService:
    """AIS Ship Tracking Service using your existing WebSocket collector code"""
    
    def __init__(self, api_key: str = "4f3516c391fc003cf99eed0bcd85494601070a50"):
        self.api_key = api_key
        self.ship_cache = {}  # MMSI -> [Timestamp, ShipName, Lat, Lon, Speed]
        self.is_running = False
        self.current_file = "1.csv"
        self.file_index = 1
        self.save_interval = 1800  # 30 minutes
        
    def get_ships_in_area(self, lat: float, lon: float, radius_km: float = 50) -> List[Dict]:
        """Get ships within radius of coordinates"""
        ships_in_area = []
        
        for mmsi, ship_data in self.ship_cache.items():
            ship_lat, ship_lon = ship_data[2], ship_data[3]
            
            # Simple distance calculation (approximation)
            lat_diff = abs(lat - ship_lat)
            lon_diff = abs(lon - ship_lon)
            distance_approx = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111  # rough km conversion
            
            if distance_approx <= radius_km:
                ships_in_area.append({
                    "mmsi": mmsi,
                    "name": ship_data[1],
                    "lat": ship_lat,
                    "lon": ship_lon,
                    "speed": ship_data[4],
                    "timestamp": ship_data[0],
                    "distance_km": round(distance_approx, 2)
                })
        
        return sorted(ships_in_area, key=lambda x: x["distance_km"])
    
    def get_ships_by_name(self, name_search: str) -> List[Dict]:
        """Search ships by name"""
        results = []
        search_lower = name_search.lower()
        
        for mmsi, ship_data in self.ship_cache.items():
            ship_name = ship_data[1].lower()
            if search_lower in ship_name:
                results.append({
                    "mmsi": mmsi,
                    "name": ship_data[1],
                    "lat": ship_data[2],
                    "lon": ship_data[3],
                    "speed": ship_data[4],
                    "timestamp": ship_data[0]
                })
        
        return results
    
    def get_ship_by_mmsi(self, mmsi: str) -> Optional[Dict]:
        """Get specific ship by MMSI"""
        if mmsi in self.ship_cache:
            ship_data = self.ship_cache[mmsi]
            return {
                "mmsi": mmsi,
                "name": ship_data[1],
                "lat": ship_data[2],
                "lon": ship_data[3],
                "speed": ship_data[4],
                "timestamp": ship_data[0]
            }
        return None
    
    def get_traffic_stats(self) -> Dict:
        """Get overall traffic statistics"""
        total_ships = len(self.ship_cache)
        moving_ships = sum(1 for ship in self.ship_cache.values() if ship[4] > 0.5)
        
        return {
            "total_ships_tracked": total_ships,
            "ships_moving": moving_ships,
            "ships_stationary": total_ships - moving_ships,
            "last_update": datetime.now().isoformat(),
            "cache_status": "active" if self.is_running else "inactive"
        }

    async def start_background_collection(self):
        """Start AIS collection in background"""
        if not self.is_running:
            self.is_running = True
            asyncio.create_task(self._collect_ships())
    
    def stop_collection(self):
        """Stop AIS collection"""
        self.is_running = False
    
    async def _collect_ships(self):
        """Your existing collect_ships function adapted"""
        start_time = time.time()
        
        # Create first CSV with headers
        with open(self.current_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "MMSI", "ShipName", "Latitude", "Longitude", "Speed"])

        while self.is_running:
            try:
                async with websockets.connect("wss://stream.aisstream.io/v0/stream") as ws:
                    asyncio.create_task(self._keep_alive(ws))

                    subscribe = {
                        "APIKey": self.api_key,
                        "BoundingBoxes": [[[-90, -180], [90, 180]]],  # global coverage
                        "FilterMessageTypes": ["PositionReport"]
                    }
                    await ws.send(json.dumps(subscribe))
                    print(f"Connected and collecting ship data -> {self.current_file}")

                    async for message in ws:
                        if not self.is_running:
                            break
                            
                        try:
                            data = json.loads(message)

                            if data.get("MessageType") != "PositionReport":
                                continue

                            meta = data.get("MetaData", {})
                            report = data.get("Message", {}).get("PositionReport", {})

                            mmsi = meta.get("MMSI")
                            name = meta.get("ShipName", "").strip()
                            lat = report.get("Latitude")
                            lon = report.get("Longitude")
                            sog = report.get("Sog")   # speed over ground
                            ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

                            if not mmsi or lat is None or lon is None:
                                continue

                            # Update in-memory cache
                            self.ship_cache[str(mmsi)] = [ts, name, lat, lon, sog]

                            # Rotate CSV every save_interval
                            if time.time() - start_time >= self.save_interval:
                                self.file_index += 1
                                self.current_file = f"{self.file_index}.csv"
                                self.ship_cache = {}  # reset cache for new file
                                with open(self.current_file, mode="w", newline="", encoding="utf-8") as f:
                                    writer = csv.writer(f)
                                    writer.writerow(["Timestamp", "MMSI", "ShipName", "Latitude",
                                                     "Longitude", "Speed"])
                                start_time = time.time()
                                print(f"Started new file: {self.current_file}")

                            # Write all cached ships into current CSV
                            with open(self.current_file, mode="w", newline="", encoding="utf-8") as f:
                                writer = csv.writer(f)
                                writer.writerow(["Timestamp", "MMSI", "ShipName", "Latitude",
                                                 "Longitude", "Speed"])
                                for ship_mmsi, info in self.ship_cache.items():
                                    writer.writerow([info[0], ship_mmsi] + info[1:])

                        except Exception as e:
                            continue

            except websockets.ConnectionClosed:
                await asyncio.sleep(5)
            except Exception as e:
                await asyncio.sleep(5)

    async def _keep_alive(self, ws):
        """Send periodic ping to keep WebSocket alive"""
        while self.is_running:
            try:
                await ws.send(json.dumps({"type": "ping"}))
            except:
                break
            await asyncio.sleep(30)