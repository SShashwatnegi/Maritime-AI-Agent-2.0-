import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  CheckCircle, 
  AlertCircle, 
  XCircle, 
  Cpu, 
  Database, 
  Zap, 
  RefreshCw,
  Clock,
  TrendingUp,
  Bot,
  Server
} from 'lucide-react';
import { maritimeAPI } from '../services/api';

function AgentStatus() {
  const [status, setStatus] = useState(null);
  const [tools, setTools] = useState([]);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    loadAllData();
    const interval = setInterval(loadAllData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [statusData, toolsData, comparisonData] = await Promise.all([
        maritimeAPI.getAgentStatus().catch(e => ({ error: e.message })),
        maritimeAPI.getAvailableTools().catch(e => ({ error: e.message })),
        maritimeAPI.getComparison().catch(e => ({ error: e.message }))
      ]);

      setStatus(statusData);
      setTools(toolsData.tools || []);
      setComparison(comparisonData);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to load status data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'active':
      case 'online':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'warning':
      case 'degraded':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case 'error':
      case 'offline':
      case 'down':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Activity className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'active':
      case 'online':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'warning':
      case 'degraded':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'error':
      case 'offline':
      case 'down':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const formatUptime = (seconds) => {
    if (!seconds) return 'Unknown';
    
    const days = Math.floor(seconds / (24 * 60 * 60));
    const hours = Math.floor((seconds % (24 * 60 * 60)) / (60 * 60));
    const minutes = Math.floor((seconds % (60 * 60)) / 60);
    
    if (days > 0) return `${days}d ${hours}h ${minutes}m`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const formatMemory = (bytes) => {
    if (!bytes) return 'Unknown';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
  };

  return (
    <div className="space-y-6">
      {/* Header with Refresh */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">System Status</h2>
          {lastUpdate && (
            <p className="text-sm text-gray-600 flex items-center space-x-1">
              <Clock className="h-4 w-4" />
              <span>Last updated: {lastUpdate.toLocaleTimeString()}</span>
            </p>
          )}
        </div>
        <button
          onClick={loadAllData}
          disabled={loading}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 transition-colors"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {loading && !status ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          <span className="ml-3 text-gray-600">Loading system status...</span>
        </div>
      ) : (
        <>
          {/* Overall System Status */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className={`p-6 rounded-xl border ${getStatusColor(status?.status)}`}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  {getStatusIcon(status?.status)}
                  <span className="font-semibold">Agent Status</span>
                </div>
                <Bot className="h-6 w-6 opacity-60" />
              </div>
              <p className="text-lg font-bold">{status?.status || 'Unknown'}</p>
              <p className="text-sm opacity-75">{status?.message || 'No message'}</p>
            </div>

            <div className="bg-blue-50 border border-blue-200 p-6 rounded-xl">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Server className="h-5 w-5 text-blue-600" />
                  <span className="font-semibold text-blue-800">API Health</span>
                </div>
                <Activity className="h-6 w-6 text-blue-400" />
              </div>
              <p className="text-lg font-bold text-blue-800">
                {status?.api_health || 'Unknown'}
              </p>
              <p className="text-sm text-blue-600">
                Response time: {status?.response_time || 'N/A'}
              </p>
            </div>

            <div className="bg-purple-50 border border-purple-200 p-6 rounded-xl">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Cpu className="h-5 w-5 text-purple-600" />
                  <span className="font-semibold text-purple-800">Memory</span>
                </div>
                <Database className="h-6 w-6 text-purple-400" />
              </div>
              <p className="text-lg font-bold text-purple-800">
                {formatMemory(status?.memory_usage)}
              </p>
              <p className="text-sm text-purple-600">
                Peak: {formatMemory(status?.memory_peak)}
              </p>
            </div>

            <div className="bg-green-50 border border-green-200 p-6 rounded-xl">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  <span className="font-semibold text-green-800">Uptime</span>
                </div>
                <Clock className="h-6 w-6 text-green-400" />
              </div>
              <p className="text-lg font-bold text-green-800">
                {formatUptime(status?.uptime)}
              </p>
              <p className="text-sm text-green-600">
                Since: {status?.start_time || 'Unknown'}
              </p>
            </div>
          </div>

          {/* Available Tools */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-2 mb-6">
              <Zap className="h-6 w-6 text-orange-600" />
              <h3 className="text-xl font-semibold text-gray-800">Available Tools</h3>
              <span className="bg-orange-100 text-orange-800 text-sm px-2 py-1 rounded-full">
                {tools.length}
              </span>
            </div>
            
            {tools.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {tools.map((tool, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-800">
                        {typeof tool === 'string' ? tool : tool.name || `Tool ${index + 1}`}
                      </h4>
                      {getStatusIcon(typeof tool === 'object' ? tool.status : 'active')}
                    </div>
                    
                    {typeof tool === 'object' && (
                      <>
                        <p className="text-sm text-gray-600">
                          {tool.description || 'No description available'}
                        </p>
                        {tool.version && (
                          <p className="text-xs text-gray-500 mt-1">
                            Version: {tool.version}
                          </p>
                        )}
                      </>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">No tools available</p>
              </div>
            )}
          </div>

          {/* Comparison Metrics */}
          {comparison && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center space-x-2 mb-6">
                <TrendingUp className="h-6 w-6 text-indigo-600" />
                <h3 className="text-xl font-semibold text-gray-800">Performance Comparison</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {Object.entries(comparison).map(([key, value], index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-800 capitalize mb-2">
                      {key.replace(/_/g, ' ')}
                    </h4>
                    <p className="text-lg font-bold text-indigo-600">{value}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default AgentStatus;