from datetime import datetime
from typing import Any, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from app.services.weather import WeatherService
from app.services.laytime import LaytimeCalculator
from app.services.voyage_planning import VoyagePlanningService
from app.services.documents import summarize_document
import asyncio
import os
import json
from dotenv import load_dotenv

class MaritimeLangChainAgent:
    def __init__(self, api_key: str):
        # Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0
        )

        # Conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # Services
        self.weather_service = WeatherService()
        self.voyage_service = VoyagePlanningService()  # 🆕 New service

        # Enhanced tools with voyage planning
        tools = [
            # Existing tools
            Tool(
                name="Weather Forecast",
                func=self.weather_forecast_tool,
                description="Get weather forecast for a city name or 'lat,lon'"
            ),
            Tool(
                name="Bad Weather Periods",
                func=self.bad_weather_tool,
                description="Get periods of bad weather (rain, storm, fog, snow) for a location"
            ),
            Tool(
                name="Laytime Calculator",
                func=lambda params: LaytimeCalculator().calculate(params),
                description="Calculate laytime based on cargo details and laytime terms"
            ),
            Tool(
                name="Document Summarizer",
                func=lambda file: asyncio.run(summarize_document(file)),
                description="Upload and summarize maritime PDF/DOCX/TXT documents"
            ),
            
            # 🆕 NEW VOYAGE PLANNING TOOLS
            Tool(
                name="Optimal Route Planner",
                func=self.optimal_route_tool,
                description="Plan optimal voyage routes between ports considering weather, piracy, costs. Format: 'origin_port|destination_port|vessel_type|priority'"
            ),
            Tool(
                name="Route Risk Analyzer", 
                func=self.route_risk_tool,
                description="Analyze risks along a specific route with waypoints. Format: JSON string with waypoints list"
            ),
            Tool(
                name="Fuel Optimizer",
                func=self.fuel_optimization_tool,
                description="Optimize fuel consumption for voyage. Format: 'distance_nm|vessel_type|current_speed|weather_conditions_json'"
            ),
            Tool(
                name="Port Information",
                func=self.port_info_tool,
                description="Get information about major world ports. Format: 'port_name' or 'search:keyword' or 'region:region_name'"
            ),
            Tool(
                name="Piracy Risk Zones",
                func=self.piracy_zones_tool,
                description="Get current piracy risk zones and threat levels worldwide"
            ),
            Tool(
                name="Route Comparison",
                func=self.route_comparison_tool,
                description="Compare multiple route options. Format: 'origin|destination|vessel_type|priority1,priority2,priority3'"
            )
        ]

        # Agent setup
        self.agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent="conversational-react-description",
            memory=self.memory,
            verbose=True
        )

    # Existing weather tools
    def weather_forecast_tool(self, location: str, hours: int = 48):
        try:
            forecast = self.weather_service.forecast_by_location(location, hours)
            formatted = f"Weather forecast for {location}:\n"
            for entry in forecast:
                dt = datetime.fromisoformat(entry["time"])
                formatted += f"- {dt.strftime('%Y-%m-%d %H:%M')}: {entry['condition']}, {entry['temperature']}°C\n"
            return formatted
        except Exception as e:
            return f"Error fetching weather: {str(e)}"

    def bad_weather_tool(self, location: str, hours: int = 48):
        try:
            periods = self.weather_service.bad_periods_by_location(location, hours)
            if not periods:
                return f"No bad weather expected in the next {hours} hours at {location}."
            formatted = f"Bad weather periods for {location}:\n"
            for start, end in periods:
                start_dt = datetime.fromisoformat(start)
                end_dt = datetime.fromisoformat(end)
                formatted += f"- From {start_dt.strftime('%Y-%m-%d %H:%M')} to {end_dt.strftime('%Y-%m-%d %H:%M')}\n"
            return formatted
        except Exception as e:
            return f"Error fetching bad weather periods: {str(e)}"

    # 🆕 NEW VOYAGE PLANNING TOOL IMPLEMENTATIONS

    def optimal_route_tool(self, params: str):
        """Optimal route planning tool"""
        try:
            parts = params.split('|')
            if len(parts) < 2:
                return "Invalid format. Use: origin_port|destination_port|vessel_type|priority"
            
            origin = parts[0].strip()
            destination = parts[1].strip()
            vessel_type = parts[2].strip() if len(parts) > 2 else "container"
            priority = parts[3].strip() if len(parts) > 3 else "balanced"
            
            # Run async function
            result = asyncio.run(self.voyage_service.plan_optimal_route(
                origin=origin,
                destination=destination,
                vessel_type=vessel_type,
                priority=priority
            ))
            
            if result.get("status") == "error":
                return f"Route planning error: {result.get('message')}"
            
            optimal = result.get("optimal_route", {})
            analysis = result.get("route_analysis", {})
            
            formatted = f"🚢 OPTIMAL ROUTE: {optimal.get('route_name')}\n"
            formatted += f"📏 Distance: {optimal.get('total_distance_nm')} nautical miles\n"
            formatted += f"⏱️ Duration: {optimal.get('estimated_duration_days')} days\n"
            formatted += f"⛽ Fuel: {optimal.get('total_fuel_consumption_mt')} MT\n"
            formatted += f"💰 Estimated Cost: ${optimal.get('total_cost_usd'):,}\n"
            formatted += f"🌦️ Weather Score: {optimal.get('weather_score')}/10\n"
            formatted += f"🛡️ Safety Score: {optimal.get('safety_score')}/10\n"
            
            if result.get("recommendations"):
                formatted += f"\n📋 RECOMMENDATIONS:\n"
                for rec in result.get("recommendations"):
                    formatted += f"• {rec}\n"
            
            return formatted
            
        except Exception as e:
            return f"Error in optimal route planning: {str(e)}"

    def route_risk_tool(self, waypoints_json: str):
        """Route risk analysis tool"""
        try:
            waypoints = json.loads(waypoints_json)
            if not isinstance(waypoints, list):
                return "Waypoints must be a list of coordinates"
            
            result = asyncio.run(self.voyage_service.analyze_route_risks(waypoints))
            
            if result.get("status") == "error":
                return f"Risk analysis error: {result.get('message')}"
            
            formatted = f"🛡️ ROUTE RISK ANALYSIS\n"
            formatted += f"📊 Overall Risk Score: {result.get('overall_risk_score', 0)}/10\n\n"
            
            weather_risks = result.get("weather_risks", [])
            if weather_risks:
                formatted += f"🌪️ WEATHER RISKS ({len(weather_risks)} points):\n"
                for risk in weather_risks[:3]:  # Show top 3
                    formatted += f"• {risk['description']} (Risk: {risk['risk_level']}/10)\n"
            
            piracy_risks = result.get("piracy_risks", [])
            if piracy_risks:
                formatted += f"\n🏴‍☠️ PIRACY RISKS ({len(piracy_risks)} points):\n"
                for risk in piracy_risks[:3]:  # Show top 3
                    formatted += f"• {risk['description']} (Risk: {risk['risk_level']}/10)\n"
            
            if not weather_risks and not piracy_risks:
                formatted += "✅ No significant risks identified along route\n"
                
            return formatted
            
        except json.JSONDecodeError:
            return "Invalid JSON format for waypoints"
        except Exception as e:
            return f"Error in route risk analysis: {str(e)}"

    def fuel_optimization_tool(self, params: str):
        """Fuel optimization tool"""
        try:
            parts = params.split('|')
            if len(parts) < 3:
                return "Invalid format. Use: distance_nm|vessel_type|current_speed|weather_conditions_json"
            
            distance_nm = float(parts[0])
            vessel_type = parts[1].strip()
            current_speed = float(parts[2])
            weather_conditions = json.loads(parts[3]) if len(parts) > 3 and parts[3] else []
            
            result = asyncio.run(self.voyage_service.calculate_fuel_optimization(
                route_distance_nm=distance_nm,
                vessel_type=vessel_type,
                current_speed_knots=current_speed,
                weather_conditions=weather_conditions
            ))
            
            if result.get("status") == "error":
                return f"Fuel optimization error: {result.get('message')}"
            
            current = result.get("current_scenario", {})
            optimized = result.get("optimized_scenario", {})
            savings = result.get("savings", {})
            
            formatted = f"⛽ FUEL OPTIMIZATION ANALYSIS\n\n"
            formatted += f"📈 CURRENT SCENARIO:\n"
            formatted += f"• Speed: {current.get('speed_knots')} knots\n"
            formatted += f"• Voyage Time: {current.get('voyage_days')} days\n"
            formatted += f"• Fuel Consumption: {current.get('total_fuel_mt')} MT\n\n"
            
            formatted += f"✨ OPTIMIZED SCENARIO:\n"
            formatted += f"• Recommended Speed: {optimized.get('recommended_speed_knots')} knots\n"
            formatted += f"• Voyage Time: {optimized.get('voyage_days')} days\n"
            formatted += f"• Fuel Consumption: {optimized.get('total_fuel_mt')} MT\n\n"
            
            formatted += f"💰 POTENTIAL SAVINGS:\n"
            formatted += f"• Fuel Saved: {savings.get('fuel_saved_mt')} MT ({savings.get('fuel_saved_percent')}%)\n"
            formatted += f"• Cost Savings: ${savings.get('cost_savings_usd'):,}\n"
            formatted += f"• Time Difference: {savings.get('time_difference_days')} days\n"
            
            recommendations = result.get("recommendations", [])
            if recommendations:
                formatted += f"\n📋 RECOMMENDATIONS:\n"
                for rec in recommendations:
                    formatted += f"• {rec}\n"
            
            return formatted
            
        except Exception as e:
            return f"Error in fuel optimization: {str(e)}"

    def port_info_tool(self, query: str):
        """Port information tool"""
        try:
            ports = self.voyage_service.major_ports
            
            if query.startswith("search:"):
                search_term = query[7:].lower()
                matches = []
                for key, port in ports.items():
                    if search_term in port.name.lower() or search_term in port.country.lower():
                        matches.append(f"• {port.name}, {port.country} ({port.lat}, {port.lon})")
                
                if matches:
                    return f"🔍 PORT SEARCH RESULTS for '{search_term}':\n" + "\n".join(matches[:10])
                else:
                    return f"No ports found matching '{search_term}'"
            
            elif query.startswith("region:"):
                region = query[7:].strip()
                matches = []
                for key, port in ports.items():
                    if self.voyage_service._get_region(port).lower() == region.lower():
                        matches.append(f"• {port.name}, {port.country}")
                
                if matches:
                    return f"🌍 PORTS IN {region.upper()}:\n" + "\n".join(matches)
                else:
                    return f"No ports found in region '{region}'"
            
            else:
                # Direct port lookup
                port_name = query.lower().replace(" ", "_")
                if port_name in ports:
                    port = ports[port_name]
                    return f"🏢 PORT INFO: {port.name}\n• Country: {port.country}\n• Coordinates: {port.lat}, {port.lon}\n• Major Port: {'Yes' if port.major_port else 'No'}\n• Region: {self.voyage_service._get_region(port)}"
                else:
                    return f"Port '{query}' not found. Try 'search:{query}' for partial matches."
                    
        except Exception as e:
            return f"Error retrieving port information: {str(e)}"

    def piracy_zones_tool(self, _):
        """Piracy risk zones tool"""
        try:
            zones = self.voyage_service.piracy_zones
            
            formatted = "🏴‍☠️ GLOBAL PIRACY RISK ZONES:\n\n"
            
            for zone in sorted(zones, key=lambda x: x["risk"], reverse=True):
                risk_level = "🔴 CRITICAL" if zone["risk"] >= 8 else \
                           "🟠 HIGH" if zone["risk"] >= 6 else \
                           "🟡 MEDIUM" if zone["risk"] >= 4 else "🟢 LOW"
                
                formatted += f"{risk_level} - {zone['name']}\n"
                formatted += f"  Risk Score: {zone['risk']}/10\n"
                formatted += f"  Area: {zone['bounds'][0]} to {zone['bounds'][1]}\n\n"
            
            formatted += "📊 RISK SCALE:\n"
            formatted += "• 1-3: Low Risk (Green)\n• 4-5: Medium Risk (Yellow)\n• 6-7: High Risk (Orange)\n• 8-10: Critical Risk (Red)"
            
            return formatted
            
        except Exception as e:
            return f"Error retrieving piracy zones: {str(e)}"

    def route_comparison_tool(self, params: str):
        """Route comparison tool"""
        try:
            parts = params.split('|')
            if len(parts) < 4:
                return "Invalid format. Use: origin|destination|vessel_type|priority1,priority2,priority3"
            
            origin = parts[0].strip()
            destination = parts[1].strip()
            vessel_type = parts[2].strip()
            priorities = [p.strip() for p in parts[3].split(',')]
            
            comparisons = []
            
            for priority in priorities:
                if priority not in ["speed", "cost", "safety", "balanced"]:
                    continue
                    
                result = asyncio.run(self.voyage_service.plan_optimal_route(
                    origin=origin,
                    destination=destination,
                    vessel_type=vessel_type,
                    priority=priority
                ))
                
                if result.get("status") == "success":
                    comparisons.append({
                        "priority": priority,
                        "route": result.get("optimal_route", {}),
                        "scores": result.get("route_analysis", {})
                    })
            
            if not comparisons:
                return "No valid routes found for comparison"
            
            formatted = f"⚖️ ROUTE COMPARISON: {origin} → {destination}\n\n"
            
            for comp in comparisons:
                route = comp["route"]
                priority = comp["priority"].upper()
                
                formatted += f"🎯 {priority} OPTIMIZED:\n"
                formatted += f"• Distance: {route.get('total_distance_nm')} nm\n"
                formatted += f"• Duration: {route.get('estimated_duration_days')} days\n"
                formatted += f"• Cost: ${route.get('total_cost_usd'):,}\n"
                formatted += f"• Safety Score: {route.get('safety_score')}/10\n\n"
            
            # Find best in each category
            shortest = min(comparisons, key=lambda x: x["route"].get("total_distance_nm", float('inf')))
            fastest = min(comparisons, key=lambda x: x["route"].get("estimated_duration_days", float('inf')))
            cheapest = min(comparisons, key=lambda x: x["route"].get("total_cost_usd", float('inf')))
            safest = max(comparisons, key=lambda x: x["route"].get("safety_score", 0))
            
            formatted += "🏆 BEST IN CATEGORY:\n"
            formatted += f"• Shortest: {shortest['priority'].title()} ({shortest['route'].get('total_distance_nm')} nm)\n"
            formatted += f"• Fastest: {fastest['priority'].title()} ({fastest['route'].get('estimated_duration_days')} days)\n"
            formatted += f"• Cheapest: {cheapest['priority'].title()} (${cheapest['route'].get('total_cost_usd'):,})\n"
            formatted += f"• Safest: {safest['priority'].title()} ({safest['route'].get('safety_score')}/10)\n"
            
            return formatted
            
        except Exception as e:
            return f"Error in route comparison: {str(e)}"

    # Async process_query (enhanced with voyage planning capabilities)
    async def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        try:
            # Enhanced query preprocessing for voyage planning
            enhanced_query = self._enhance_query_with_voyage_context(query)
            
            # Run the agent
            answer = await self.agent.arun(enhanced_query)
            
            # Determine which tools were likely used based on query content
            tools_used = self._identify_tools_used(query)
            
            return {
                "answer": answer,
                "tools_used": tools_used,
                "execution_plan": "Handled by conversational-react agent with voyage planning capabilities",
                "confidence": 1.0,
                "timestamp": datetime.now().isoformat(),
                "voyage_planning_enabled": True
            }
        except Exception as e:
            return {"error": str(e)}

    def _enhance_query_with_voyage_context(self, query: str) -> str:
        """Enhance query with voyage planning context"""
        voyage_keywords = [
            "route", "voyage", "planning", "optimize", "fuel", "piracy", 
            "weather", "port", "navigation", "shipping", "cost", "distance"
        ]
        
        if any(keyword in query.lower() for keyword in voyage_keywords):
            context = """
            🚢 VOYAGE PLANNING CONTEXT:
            You have access to advanced voyage planning tools including:
            - Optimal Route Planner: Plan routes considering weather, piracy, costs
            - Route Risk Analyzer: Analyze safety and weather risks
            - Fuel Optimizer: Optimize speed and consumption
            - Port Information: Database of major world ports
            - Piracy Risk Zones: Current threat levels globally
            - Route Comparison: Compare multiple optimization strategies
            
            Use these tools to provide comprehensive voyage planning assistance.
            """
            return f"{context}\n\nUser Query: {query}"
        
        return query

    def _identify_tools_used(self, query: str) -> list:
        """Identify which tools were likely used based on query content"""
        tools = []
        query_lower = query.lower()
        
        # Existing tools
        if "weather" in query_lower:
            tools.extend(["Weather Forecast", "Bad Weather Periods"])
        if "laytime" in query_lower or "demurrage" in query_lower:
            tools.append("Laytime Calculator")
        if "document" in query_lower or "summarize" in query_lower:
            tools.append("Document Summarizer")
        
        # New voyage planning tools
        if any(word in query_lower for word in ["route", "optimize", "plan voyage"]):
            tools.append("Optimal Route Planner")
        if "risk" in query_lower and ("route" in query_lower or "voyage" in query_lower):
            tools.append("Route Risk Analyzer")
        if "fuel" in query_lower:
            tools.append("Fuel Optimizer")
        if "port" in query_lower:
            tools.append("Port Information")
        if "piracy" in query_lower:
            tools.append("Piracy Risk Zones")
        if "compare" in query_lower and "route" in query_lower:
            tools.append("Route Comparison")
        
        return tools if tools else ["General Maritime Knowledge"]

    # Status check (enhanced)
    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "operational",
            "agent_type": "Maritime LangChain Agent with Voyage Planning",
            "capabilities": [
                "Weather forecasting",
                "Laytime calculations", 
                "Document summarization",
                "🆕 Optimal route planning",
                "🆕 Risk analysis",
                "🆕 Fuel optimization",
                "🆕 Port information",
                "🆕 Piracy zone monitoring",
                "🆕 Route comparison"
            ],
            "voyage_planning_tools": [
                "Optimal Route Planner",
                "Route Risk Analyzer", 
                "Fuel Optimizer",
                "Port Information",
                "Piracy Risk Zones",
                "Route Comparison"
            ],
            "memory_trace": [msg.content for msg in self.memory.chat_memory.messages[-5:]],  # Last 5 messages
            "last_updated": datetime.now().isoformat(),
            "version": "2.1.0-voyage-planning"
        }

    # Memory reset
    def clear_memory(self) -> Dict[str, Any]:
        self.memory.clear()
        return {
            "message": "Memory cleared successfully.", 
            "voyage_planning_ready": True,
            "available_tools": len(self.agent.tools)
        }

    # 🆕 New method: Get voyage planning capabilities
    def get_voyage_capabilities(self) -> Dict[str, Any]:
        """Get detailed information about voyage planning capabilities"""
        return {
            "voyage_planning_features": {
                "route_optimization": {
                    "description": "Multi-factor route optimization",
                    "factors_considered": [
                        "Weather conditions",
                        "Piracy risk zones", 
                        "Fuel consumption",
                        "Canal fees",
                        "Distance efficiency",
                        "Time constraints"
                    ],
                    "optimization_priorities": ["speed", "cost", "safety", "balanced"]
                },
                "risk_analysis": {
                    "description": "Comprehensive route risk assessment",
                    "risk_types": [
                        "Weather hazards",
                        "Piracy threats",
                        "Port congestion",
                        "Geopolitical risks"
                    ]
                },
                "fuel_optimization": {
                    "description": "Speed and consumption optimization",
                    "benefits": [
                        "Cost reduction",
                        "Environmental impact",
                        "Voyage efficiency"
                    ]
                }
            },
            "supported_vessel_types": ["container", "bulk", "tanker", "general"],
            "global_coverage": {
                "major_ports": len(self.voyage_service.major_ports),
                "piracy_zones": len(self.voyage_service.piracy_zones),
                "weather_integration": True
            },
            "status": "fully_operational",
            "last_updated": datetime.now().isoformat()
        }

    # 🆕 New method: Get example voyage planning queries
    def get_example_queries(self) -> Dict[str, Any]:
        """Get example queries for voyage planning capabilities"""
        return {
            "voyage_planning_examples": {
                "route_optimization": [
                    "Plan the optimal route from Singapore to Rotterdam for a container vessel",
                    "Find the most cost-effective route from Los Angeles to Shanghai",
                    "What's the safest route from Dubai to Hamburg considering piracy risks?"
                ],
                "risk_analysis": [
                    "Analyze risks along the route from Mumbai to Antwerp",
                    "What are the weather and piracy risks for a voyage to West Africa?",
                    "Check security threats along the Suez Canal route"
                ],
                "fuel_optimization": [
                    "Optimize fuel consumption for a 5000nm voyage at 18 knots",
                    "What's the best speed for fuel efficiency in rough weather?",
                    "Compare fuel costs between different sailing speeds"
                ],
                "general_planning": [
                    "Compare route options from New York to Le Havre",
                    "What ports are available in the Mediterranean?", 
                    "Show me current piracy risk zones worldwide",
                    "Plan a voyage avoiding high-risk areas"
                ]
            },
            "usage_tips": [
                "Be specific about vessel type and size for better optimization",
                "Mention your priority (speed/cost/safety) for tailored recommendations",
                "Include weather concerns for more accurate risk assessment",
                "Ask for comparisons to evaluate multiple options"
            ]
        }