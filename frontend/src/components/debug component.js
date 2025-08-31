import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  CheckCircle, 
  RefreshCw, 
  Server, 
  Wifi, 
  WifiOff,
  Terminal,
  Globe
} from 'lucide-react';
import { maritimeAPI } from '../services/api';

const DebugConnection = () => {
  const [connectionStatus, setConnectionStatus] = useState({
    api: null,
    backend: null,
    cors: null,
    testing: false
  });
  const [logs, setLogs] = useState([]);

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev.slice(-9), { message, type, timestamp }]);
  };

  const testAllConnections = async () => {
    setConnectionStatus(prev => ({ ...prev, testing: true }));
    addLog('Starting connection tests...', 'info');

    // Test 1: Basic API Health
    try {
      addLog('Testing API health endpoint...', 'info');
      const healthResponse = await fetch('http://localhost:8000/health');
      if (healthResponse.ok) {
        const data = await healthResponse.json();
        setConnectionStatus(prev => ({ ...prev, backend: true }));
        addLog(`✅ Backend health: ${data.status}`, 'success');
      } else {
        throw new Error(`Health check failed: ${healthResponse.status}`);
      }
    } catch (error) {
      setConnectionStatus(prev => ({ ...prev, backend: false }));
      addLog(`❌ Backend health failed: ${error.message}`, 'error');
    }

    // Test 2: API Ping
    try {
      addLog('Testing API ping endpoint...', 'info');
      const pingData = await maritimeAPI.ping();
      setConnectionStatus(prev => ({ ...prev, api: true }));
      addLog(`✅ API ping successful: ${pingData.message || 'OK'}`, 'success');
    } catch (error) {
      setConnectionStatus(prev => ({ ...prev, api: false }));
      addLog(`❌ API ping failed: ${error.message}`, 'error');
    }

    // Test 3: CORS Test
    try {
      addLog('Testing CORS configuration...', 'info');
      const corsResponse = await fetch('http://localhost:8000/api/ping', {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      if (corsResponse.ok) {
        setConnectionStatus(prev => ({ ...prev, cors: true }));
        addLog('✅ CORS configuration working', 'success');
      } else {
        throw new Error(`CORS test failed: ${corsResponse.status}`);
      }
    } catch (error) {
      setConnectionStatus(prev => ({ ...prev, cors: false }));
      addLog(`❌ CORS test failed: ${error.message}`, 'error');
    }

    setConnectionStatus(prev => ({ ...prev, testing: false }));
    addLog('Connection tests completed', 'info');
  };

  useEffect(() => {
    testAllConnections();
  }, []);

  const getStatusIcon = (status) => {
    if (status === null) return <RefreshCw className="h-5 w-5 text-gray-400 animate-spin" />;
    return status ? 
      <CheckCircle className="h-5 w-5 text-green-500" /> : 
      <AlertTriangle className="h-5 w-5 text-red-500" />;
  };

  const getStatusText = (status) => {
    if (status === null) return 'Testing...';
    return status ? 'Connected' : 'Failed';
  };

  const getStatusBg = (status) => {
    if (status === null) return 'bg-gray-50 border-gray-200';
    return status ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200';
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Connection Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className={`p-4 rounded-lg border ${getStatusBg(connectionStatus.backend)}`}>
          <div className="flex items-center space-x-3">
            {getStatusIcon(connectionStatus.backend)}
            <div>
              <h3 className="font-medium">Backend Server</h3>
              <p className="text-sm text-gray-600">{getStatusText(connectionStatus.backend)}</p>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">http://localhost:8000/health</p>
        </div>

        <div className={`p-4 rounded-lg border ${getStatusBg(connectionStatus.api)}`}>
          <div className="flex items-center space-x-3">
            {getStatusIcon(connectionStatus.api)}
            <div>
              <h3 className="font-medium">API Endpoints</h3>
              <p className="text-sm text-gray-600">{getStatusText(connectionStatus.api)}</p>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">http://localhost:8000/api/*</p>
        </div>

        <div className={`p-4 rounded-lg border ${getStatusBg(connectionStatus.cors)}`}>
          <div className="flex items-center space-x-3">
            {getStatusIcon(connectionStatus.cors)}
            <div>
              <h3 className="font-medium">CORS Policy</h3>
              <p className="text-sm text-gray-600">{getStatusText(connectionStatus.cors)}</p>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Cross-origin requests</p>
        </div>
      </div>

      {/* Test Button */}
      <div className="flex justify-center">
        <button
          onClick={testAllConnections}
          disabled={connectionStatus.testing}
          className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
        >
          <RefreshCw className={`h-4 w-4 ${connectionStatus.testing ? 'animate-spin' : ''}`} />
          <span>Test All Connections</span>
        </button>
      </div>

      {/* Troubleshooting Guide */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
          <Terminal className="h-5 w-5 text-blue-600" />
          <span>Troubleshooting Guide</span>
        </h3>
        
        <div className="space-y-4 text-sm">
          <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
            <h4 className="font-medium text-yellow-800 mb-2">🔧 Common Issues & Solutions:</h4>
            <ul className="space-y-2 text-yellow-700">
              <li><strong>Backend not running:</strong> Start your FastAPI server with <code className="bg-yellow-100 px-1 rounded">uvicorn main:app --reload --port 8000</code></li>
              <li><strong>Wrong port:</strong> Ensure backend is on port 8000, or update API_BASE in api.js</li>
              <li><strong>CORS issues:</strong> Add CORS middleware to your FastAPI backend</li>
              <li><strong>Firewall:</strong> Check if localhost:8000 is blocked</li>
            </ul>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded p-3">
            <h4 className="font-medium text-blue-800 mb-2">🔍 Backend CORS Setup:</h4>
            <p className="text-blue-700 mb-2">Add this to your FastAPI main.py:</p>
            <pre className="bg-blue-100 p-2 rounded text-xs overflow-x-auto">
{`from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)`}
            </pre>
          </div>

          <div className="bg-green-50 border border-green-200 rounded p-3">
            <h4 className="font-medium text-green-800 mb-2">✅ Quick Test Commands:</h4>
            <ul className="space-y-1 text-green-700">
              <li><code className="bg-green-100 px-1 rounded">curl http://localhost:8000/health</code></li>
              <li><code className="bg-green-100 px-1 rounded">curl http://localhost:8000/api/ping</code></li>
              <li><code className="bg-green-100 px-1 rounded">netstat -an | grep 8000</code> (check if port is open)</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Connection Logs */}
      <div className="bg-gray-900 rounded-lg p-4">
        <h3 className="text-white font-medium mb-3 flex items-center space-x-2">
          <Terminal className="h-4 w-4" />
          <span>Connection Logs</span>
        </h3>
        <div className="space-y-1 max-h-60 overflow-y-auto">
          {logs.length === 0 ? (
            <p className="text-gray-400 text-sm">No logs yet...</p>
          ) : (
            logs.map((log, index) => (
              <div key={index} className="flex items-start space-x-2 text-sm">
                <span className="text-gray-500">[{log.timestamp}]</span>
                <span className={
                  log.type === 'success' ? 'text-green-400' :
                  log.type === 'error' ? 'text-red-400' :
                  'text-gray-300'
                }>
                  {log.message}
                </span>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Current Configuration */}
      <div className="bg-gray-50 rounded-lg border p-4">
        <h3 className="font-medium mb-3 flex items-center space-x-2">
          <Globe className="h-4 w-4 text-gray-600" />
          <span>Current Configuration</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">API Base URL:</span>
            <div className="font-mono bg-white border rounded px-2 py-1">{API_BASE}</div>
          </div>
          <div>
            <span className="text-gray-600">Frontend URL:</span>
            <div className="font-mono bg-white border rounded px-2 py-1">{window.location.origin}</div>
          </div>
          <div>
            <span className="text-gray-600">Environment:</span>
            <div className="font-mono bg-white border rounded px-2 py-1">{process.env.NODE_ENV}</div>
          </div>
          <div>
            <span className="text-gray-600">User Agent:</span>
            <div className="font-mono bg-white border rounded px-2 py-1 truncate">{navigator.userAgent.split(' ')[0]}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DebugConnection;