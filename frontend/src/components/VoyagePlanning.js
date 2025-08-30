import React, { useState, useEffect } from 'react';
import { 
  Map, 
  Navigation, 
  Fuel, 
  Shield, 
  Anchor, 
  AlertTriangle, 
  TrendingUp,
  Search,
  Compass,
  Ship,
  Target,
  BarChart3,
  MapPin,
  Calendar,
  Clock,
  DollarSign,
  Zap,
  RefreshCw
} from 'lucide-react';
import { maritimeAPI } from '../services/api';

const VoyagePlanning = () => {
  const [activeSection, setActiveSection] = useState('route');
  const [loading, setLoading] = useState(false);
  const [routeData, setRouteData] = useState(null);
  const [riskData, setRiskData] = useState(null);
  const [fuelData, setFuelData] = useState(null);
  const [ports, setPorts] = useState([]);
  const [piracyZones, setPiracyZones] = useState([]);
  
  // Form states
  const [routeForm, setRouteForm] = useState({
    origin: '',
    destination: '',
    vesselType: 'container',
    priorities: ['fuel_efficiency', 'safety']
  });
  
  const [fuelForm, setFuelForm] = useState({
    distance: 5000,
    vesselSpecs: {
      type: 'container',
      dwt: 50000,
      engine_power: 15000,
      fuel_type: 'HFO'
    },
    weatherConditions: 'moderate'
  });

  const vesselTypes = [
    { value: 'container', label: 'Container Ship', icon: '🚢' },
    { value: 'bulk', label: 'Bulk Carrier', icon: '⛴️' },
    { value: 'tanker', label: 'Tanker', icon: '🛢️' },
    { value: 'general', label: 'General Cargo', icon: '📦' },
    { value: 'roro', label: 'RoRo Ferry', icon: '🚗' }
  ];

  const priorities = [
    { value: 'fuel_efficiency', label: 'Fuel Efficiency', icon: <Fuel className="w-4 h-4" /> },
    { value: 'safety', label: 'Safety', icon: <Shield className="w-4 h-4" /> },
    { value: 'speed', label: 'Transit Time', icon: <Clock className="w-4 h-4" /> },
    { value: 'cost', label: 'Cost Optimization', icon: <DollarSign className="w-4 h-4" /> }
  ];

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      // Mock data for now - replace with actual API calls when backend is ready
      setPorts([
        { name: 'Singapore', country: 'Singapore', type: 'Container', depth: 16, lat: 1.3521, lon: 103.8198 },
        { name: 'Rotterdam', country: 'Netherlands', type: 'Container', depth: 24, lat: 51.9225, lon: 4.4792 },
        { name: 'Shanghai', country: 'China', type: 'Container', depth: 18, lat: 31.2304, lon: 121.4737 },
        { name: 'Los Angeles', country: 'USA', type: 'Container', depth: 15, lat: 33.7373, lon: -118.2644 },
        { name: 'Hamburg', country: 'Germany', type: 'Container', depth: 14, lat: 53.5511, lon: 9.9937 },
        { name: 'Dubai', country: 'UAE', type: 'Container', depth: 17, lat: 25.2762, lon: 55.2964 }
      ]);
      setPiracyZones([
        { name: 'Gulf of Aden', description: 'High piracy activity area', risk_level: 'High', last_updated: '2024-01-15' },
        { name: 'Strait of Malacca', description: 'Medium risk corridor', risk_level: 'Medium', last_updated: '2024-01-14' },
        { name: 'West Africa Coast', description: 'Elevated piracy risk', risk_level: 'High', last_updated: '2024-01-16' }
      ]);
    } catch (error) {
      console.error('Failed to load initial data:', error);
    }
  };

  const handleRouteOptimization = async () => {
    if (!routeForm.origin || !routeForm.destination) {
      alert('Please enter both origin and destination');
      return;
    }
    
    setLoading(true);
    try {
      // Mock response - replace with actual API call
      const mockResponse = {
        distance: Math.floor(Math.random() * 5000) + 2000,
        transit_time: Math.floor(Math.random() * 15) + 8,
        estimated_cost: Math.floor(Math.random() * 50000) + 25000,
        recommended_route: `${routeForm.origin} -> ${routeForm.destination}`
      };
      setRouteData(mockResponse);
    } catch (error) {
      console.error('Route optimization failed:', error);
      alert('Route optimization failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRiskAnalysis = async () => {
    if (!routeData) {
      alert('Please optimize a route first');
      return;
    }
    
    setLoading(true);
    try {
      // Mock response - replace with actual API call
      const mockResponse = {
        overall_risk: 'moderate',
        piracy_risk: 'low',
        weather_risk: 'moderate',
        risk_factors: ['Seasonal weather patterns', 'Minor piracy activity in transit zones'],
        recommendations: 'Maintain standard security protocols and monitor weather updates during transit.'
      };
      setRiskData(mockResponse);
    } catch (error) {
      console.error('Risk analysis failed:', error);
      alert('Risk analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFuelOptimization = async () => {
    setLoading(true);
    try {
      // Mock response - replace with actual API call
      const mockResponse = {
        total_fuel_consumption: Math.floor(fuelForm.distance * 0.08 + Math.random() * 100),
        optimal_speed: 14 + Math.floor(Math.random() * 4),
        estimated_fuel_cost: Math.floor(fuelForm.distance * 45 + Math.random() * 10000),
        fuel_efficiency: Math.floor(Math.random() * 10) + 15,
        recommendations: 'Maintain optimal speed of 16 knots for best fuel efficiency. Consider weather routing to minimize consumption.'
      };
      setFuelData(mockResponse);
    } catch (error) {
      console.error('Fuel optimization failed:', error);
      alert('Fuel optimization failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const sections = [
    { id: 'route', label: 'Route Planning', icon: Navigation },
    { id: 'risk', label: 'Risk Analysis', icon: AlertTriangle },
    { id: 'fuel', label: 'Fuel Optimization', icon: Fuel },
    { id: 'ports', label: 'Port Database', icon: Anchor }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center py-6 maritime-gradient rounded-xl text-white">
        <Map className="w-12 h-12 mx-auto mb-4 opacity-90" />
        <h2 className="text-3xl font-bold mb-2">Smart Voyage Planning</h2>
        <p className="text-xl text-blue-100 mb-6">
          AI-powered route optimization with comprehensive risk assessment
        </p>
        <div className="flex justify-center space-x-6 text-sm">
          <div className="flex items-center space-x-1">
            <Target className="w-4 h-4" />
            <span>Route Optimization</span>
          </div>
          <div className="flex items-center space-x-1">
            <Shield className="w-4 h-4" />
            <span>Risk Assessment</span>
          </div>
          <div className="flex items-center space-x-1">
            <Fuel className="w-4 h-4" />
            <span>Fuel Planning</span>
          </div>
        </div>
      </div>

      {/* Section Navigation */}
      <div className="flex flex-wrap gap-2 p-4 glass-effect rounded-xl">
        {sections.map((section) => {
          const Icon = section.icon;
          return (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${
                activeSection === section.id
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{section.label}</span>
            </button>
          );
        })}
      </div>

      {/* Route Planning Section */}
      {activeSection === 'route' && (
        <div className="space-y-6">
          <div className="glass-effect rounded-xl p-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center space-x-2">
              <Navigation className="w-5 h-5 text-blue-600" />
              <span>Route Optimization</span>
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Origin Port
                  </label>
                  <input
                    type="text"
                    value={routeForm.origin}
                    onChange={(e) => setRouteForm({...routeForm, origin: e.target.value})}
                    placeholder="e.g., Singapore"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Destination Port
                  </label>
                  <input
                    type="text"
                    value={routeForm.destination}
                    onChange={(e) => setRouteForm({...routeForm, destination: e.target.value})}
                    placeholder="e.g., Rotterdam"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Vessel Type
                  </label>
                  <select
                    value={routeForm.vesselType}
                    onChange={(e) => setRouteForm({...routeForm, vesselType: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {vesselTypes.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.icon} {type.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="space-y-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Optimization Priorities
                </label>
                <div className="space-y-2">
                  {priorities.map((priority) => (
                    <label key={priority.value} className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={routeForm.priorities.includes(priority.value)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setRouteForm({
                              ...routeForm, 
                              priorities: [...routeForm.priorities, priority.value]
                            });
                          } else {
                            setRouteForm({
                              ...routeForm,
                              priorities: routeForm.priorities.filter(p => p !== priority.value)
                            });
                          }
                        }}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <div className="flex items-center space-x-2">
                        {priority.icon}
                        <span className="text-sm">{priority.label}</span>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </div>
            
            <button
              onClick={handleRouteOptimization}
              disabled={loading}
              className="w-full mt-6 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Optimizing Route...</span>
                </div>
              ) : (
                <>
                  <Compass className="w-4 h-4 inline mr-2" />
                  Optimize Route
                </>
              )}
            </button>
          </div>
          
          {/* Route Results */}
          {routeData && (
            <div className="glass-effect rounded-xl p-6">
              <h4 className="text-lg font-semibold text-gray-800 mb-4">Route Optimization Results</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Navigation className="w-5 h-5 text-blue-600" />
                    <span className="font-medium text-blue-800">Distance</span>
                  </div>
                  <p className="text-2xl font-bold text-blue-900">
                    {routeData.distance} nm
                  </p>
                </div>
                
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Clock className="w-5 h-5 text-green-600" />
                    <span className="font-medium text-green-800">Transit Time</span>
                  </div>
                  <p className="text-2xl font-bold text-green-900">
                    {routeData.transit_time} days
                  </p>
                </div>
                
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <DollarSign className="w-5 h-5 text-purple-600" />
                    <span className="font-medium text-purple-800">Est. Cost</span>
                  </div>
                  <p className="text-2xl font-bold text-purple-900">
                    ${routeData.estimated_cost?.toLocaleString()}
                  </p>
                </div>
              </div>
              
              <button
                onClick={handleRiskAnalysis}
                disabled={loading}
                className="mt-4 bg-orange-600 text-white py-2 px-4 rounded-lg hover:bg-orange-700 disabled:opacity-50 font-medium transition-colors"
              >
                <AlertTriangle className="w-4 h-4 inline mr-2" />
                Analyze Risks for This Route
              </button>
            </div>
          )}
        </div>
      )}

      {/* Risk Analysis Section */}
      {activeSection === 'risk' && (
        <div className="glass-effect rounded-xl p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            <span>Risk Analysis</span>
          </h3>
          
          {riskData ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <AlertTriangle className="w-5 h-5 text-red-600" />
                    <span className="font-medium text-red-800">Overall Risk</span>
                  </div>
                  <p className="text-2xl font-bold text-red-900 capitalize">
                    {riskData.overall_risk || 'Moderate'}
                  </p>
                </div>
                
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Shield className="w-5 h-5 text-yellow-600" />
                    <span className="font-medium text-yellow-800">Piracy Risk</span>
                  </div>
                  <p className="text-2xl font-bold text-yellow-900 capitalize">
                    {riskData.piracy_risk || 'Low'}
                  </p>
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <TrendingUp className="w-5 h-5 text-blue-600" />
                    <span className="font-medium text-blue-800">Weather Risk</span>
                  </div>
                  <p className="text-2xl font-bold text-blue-900 capitalize">
                    {riskData.weather_risk || 'Moderate'}
                  </p>
                </div>
              </div>
              
              {riskData.risk_factors && riskData.risk_factors.length > 0 && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-medium text-gray-800 mb-2">Risk Factors Identified:</h4>
                  <ul className="space-y-1">
                    {riskData.risk_factors.map((factor, index) => (
                      <li key={index} className="text-sm text-gray-700 flex items-center space-x-2">
                        <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                        <span>{factor}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {riskData.recommendations && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="font-medium text-green-800 mb-2">Safety Recommendations:</h4>
                  <p className="text-sm text-green-700">{riskData.recommendations}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">No risk analysis available. Please optimize a route first.</p>
            </div>
          )}
        </div>
      )}

      {/* Fuel Optimization Section */}
      {activeSection === 'fuel' && (
        <div className="space-y-6">
          <div className="glass-effect rounded-xl p-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center space-x-2">
              <Fuel className="w-5 h-5 text-green-600" />
              <span>Fuel Optimization</span>
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Voyage Distance (nautical miles)
                  </label>
                  <input
                    type="number"
                    value={fuelForm.distance}
                    onChange={(e) => setFuelForm({...fuelForm, distance: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Vessel DWT (tons)
                  </label>
                  <input
                    type="number"
                    value={fuelForm.vesselSpecs.dwt}
                    onChange={(e) => setFuelForm({
                      ...fuelForm, 
                      vesselSpecs: {...fuelForm.vesselSpecs, dwt: parseInt(e.target.value)}
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Engine Power (kW)
                  </label>
                  <input
                    type="number"
                    value={fuelForm.vesselSpecs.engine_power}
                    onChange={(e) => setFuelForm({
                      ...fuelForm, 
                      vesselSpecs: {...fuelForm.vesselSpecs, engine_power: parseInt(e.target.value)}
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Fuel Type
                  </label>
                  <select
                    value={fuelForm.vesselSpecs.fuel_type}
                    onChange={(e) => setFuelForm({
                      ...fuelForm, 
                      vesselSpecs: {...fuelForm.vesselSpecs, fuel_type: e.target.value}
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="HFO">Heavy Fuel Oil (HFO)</option>
                    <option value="MGO">Marine Gas Oil (MGO)</option>
                    <option value="LSFO">Low Sulfur Fuel Oil (LSFO)</option>
                    <option value="LNG">Liquefied Natural Gas (LNG)</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Weather Conditions
                  </label>
                  <select
                    value={fuelForm.weatherConditions}
                    onChange={(e) => setFuelForm({...fuelForm, weatherConditions: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="calm">Calm (Sea State 0-2)</option>
                    <option value="moderate">Moderate (Sea State 3-4)</option>
                    <option value="rough">Rough (Sea State 5-6)</option>
                    <option value="severe">Severe (Sea State 7+)</option>
                  </select>
                </div>
              </div>
            </div>
            
            <button
              onClick={handleFuelOptimization}
              disabled={loading}
              className="w-full mt-6 bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Optimizing Fuel...</span>
                </div>
              ) : (
                <>
                  <Fuel className="w-4 h-4 inline mr-2" />
                  Optimize Fuel Consumption
                </>
              )}
            </button>
          </div>
          
          {/* Fuel Results */}
          {fuelData && (
            <div className="glass-effect rounded-xl p-6">
              <h4 className="text-lg font-semibold text-gray-800 mb-4">Fuel Optimization Results</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Fuel className="w-5 h-5 text-green-600" />
                    <span className="font-medium text-green-800">Total Fuel</span>
                  </div>
                  <p className="text-2xl font-bold text-green-900">
                    {fuelData.total_fuel_consumption} MT
                  </p>
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <TrendingUp className="w-5 h-5 text-blue-600" />
                    <span className="font-medium text-blue-800">Optimal Speed</span>
                  </div>
                  <p className="text-2xl font-bold text-blue-900">
                    {fuelData.optimal_speed} knots
                  </p>
                </div>
                
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <DollarSign className="w-5 h-5 text-purple-600" />
                    <span className="font-medium text-purple-800">Fuel Cost</span>
                  </div>
                  <p className="text-2xl font-bold text-purple-900">
                    ${fuelData.estimated_fuel_cost?.toLocaleString()}
                  </p>
                </div>
                
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <BarChart3 className="w-5 h-5 text-orange-600" />
                    <span className="font-medium text-orange-800">Efficiency</span>
                  </div>
                  <p className="text-2xl font-bold text-orange-900">
                    {fuelData.fuel_efficiency} MT/day
                  </p>
                </div>
              </div>
              
              {fuelData.recommendations && (
                <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-800 mb-2">Optimization Recommendations:</h4>
                  <p className="text-sm text-blue-700">{fuelData.recommendations}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Port Database Section */}
      {activeSection === 'ports' && (
        <div className="glass-effect rounded-xl p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center space-x-2">
            <Anchor className="w-5 h-5 text-blue-600" />
            <span>Port Database</span>
          </h3>
          
          <div className="mb-6">
            <div className="flex space-x-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search ports by name or region..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                <Search className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {ports.slice(0, 12).map((port, idx) => (
              <div
                key={idx}
                className="bg-white border border-gray-200 rounded-xl shadow-sm p-4 hover:shadow-md transition-all"
              >
                <div className="flex items-center space-x-2 mb-2">
                  <MapPin className="w-5 h-5 text-blue-600" />
                  <h4 className="font-semibold text-gray-800">{port.name}</h4>
                </div>
                <p className="text-sm text-gray-600">{port.country}</p>
                <p className="text-sm text-gray-600">Type: {port.type}</p>
                <p className="text-sm text-gray-600">Depth: {port.depth} m</p>
                <p className="text-xs text-gray-400 mt-2">
                  Lat: {port.lat}, Lon: {port.lon}
                </p>
              </div>
            ))}
          </div>

          {/* Piracy Zones Section */}
          <div className="mt-8">
            <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center space-x-2">
              <Shield className="w-5 h-5 text-red-600" />
              <span>High-Risk Piracy Zones</span>
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {piracyZones.map((zone, idx) => (
                <div
                  key={idx}
                  className="bg-red-50 border border-red-200 rounded-xl p-4 shadow-sm"
                >
                  <div className="flex items-center space-x-2 mb-2">
                    <AlertTriangle className="w-5 h-5 text-red-600" />
                    <h5 className="font-semibold text-red-800">{zone.name}</h5>
                  </div>
                  <p className="text-sm text-gray-700">{zone.description}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Risk: <span className="capitalize font-medium">{zone.risk_level}</span>
                  </p>
                  <p className="text-xs text-gray-400">Updated: {zone.last_updated}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoyagePlanning;
