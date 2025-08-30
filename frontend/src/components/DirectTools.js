import React, { useState, useRef } from 'react';
import { 
  Brain, 
  FileText, 
  Cloud, 
  Upload, 
  Trash2, 
  Settings,
  MapPin,
  RefreshCw,
  History,
  MessageSquare
} from 'lucide-react';
import { maritimeAPI } from '../services/api';
import ResponseDisplay from './ResponseDisplay';
import WeatherCard from './WeatherCard';

const DirectTools = ({ responses = [], onAddResponse, onClearResponses }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);

  const majorPorts = [
    { name: 'Singapore', lat: 1.3521, lon: 103.8198, flag: '🇸🇬' },
    { name: 'Rotterdam', lat: 51.9225, lon: 4.4792, flag: '🇳🇱' },
    { name: 'Hamburg', lat: 53.5511, lon: 9.9937, flag: '🇩🇪' },
    { name: 'Hong Kong', lat: 22.3193, lon: 114.1694, flag: '🇭🇰' },
    { name: 'Dubai', lat: 25.2762, lon: 55.2964, flag: '🇦🇪' },
    { name: 'Shanghai', lat: 31.2304, lon: 121.4737, flag: '🇨🇳' }
  ];

  const handleDirectAI = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    const currentQuery = query;
    setQuery(''); // Clear input immediately

    try {
      const data = await maritimeAPI.askDirect(currentQuery);
      onAddResponse({
        type: 'ai_query',
        query: currentQuery,
        response: {
          type: 'direct',
          answer: data.answer
        }
      });
    } catch (error) {
      onAddResponse({
        type: 'ai_query',
        query: currentQuery,
        response: {
          type: 'error',
          answer: `Error: ${error.response?.data?.detail || error.message}`,
          error: true
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentSummary = async () => {
    if (!file) {
      alert('Please select a file first');
      return;
    }
    
    setLoading(true);
    const currentFile = file;
    setFile(null); // Clear file immediately

    try {
      const data = await maritimeAPI.summarizeDocument(currentFile);
      onAddResponse({
        type: 'document',
        filename: currentFile.name,
        response: {
          type: 'document',
          answer: data.answer,
          filename: currentFile.name
        }
      });
    } catch (error) {
      onAddResponse({
        type: 'document',
        filename: currentFile.name,
        response: {
          type: 'error',
          answer: `Error: ${error.response?.data?.detail || error.message}`,
          error: true
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const handleWeatherQuery = async (lat, lon, portName) => {
    setLoading(true);
    try {
      const data = await maritimeAPI.getWeather(lat, lon);
      onAddResponse({
        type: 'weather',
        portName: portName,
        coordinates: { lat, lon },
        response: {
          type: 'weather',
          answer: `Weather data retrieved for ${portName} (${lat}, ${lon})`,
          weatherData: data,
          portName: portName
        }
      });
    } catch (error) {
      onAddResponse({
        type: 'weather',
        portName: portName,
        coordinates: { lat, lon },
        response: {
          type: 'error',
          answer: `Error: ${error.response?.data?.detail || error.message}`,
          error: true
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center py-6">
        <Settings className="w-12 h-12 mx-auto text-green-600 mb-4" />
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Direct Tool Access</h2>
        <p className="text-slate-600">Use individual tools directly for specific tasks</p>
      </div>

      {/* Response History */}
      {responses.length > 0 && (
        <div className="glass-effect rounded-xl shadow-lg border">
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <History className="h-5 w-5 text-green-600" />
              <h3 className="text-lg font-semibold text-slate-800">Recent Responses</h3>
              <span className="text-sm text-gray-500">({responses.length})</span>
            </div>
            <button
              onClick={onClearResponses}
              className="flex items-center space-x-1 text-red-600 hover:text-red-800 text-sm transition-colors"
            >
              <Trash2 className="h-4 w-4" />
              <span>Clear History</span>
            </button>
          </div>
          
          <div className="max-h-96 overflow-y-auto p-4 space-y-4">
            {responses.slice().reverse().map((item) => (
              <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                <div className="mb-3">
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    {item.type === 'ai_query' && <Brain className="h-4 w-4" />}
                    {item.type === 'document' && <FileText className="h-4 w-4" />}
                    {item.type === 'weather' && <Cloud className="h-4 w-4" />}
                    <span className="capitalize font-medium">{item.type.replace('_', ' ')}</span>
                    <span>•</span>
                    <span>{item.timestamp?.toLocaleTimeString()}</span>
                  </div>
                  
                  {item.query && (
                    <div className="mt-2 text-sm bg-gray-50 p-2 rounded border-l-4 border-blue-500">
                      <strong>Query:</strong> {item.query}
                    </div>
                  )}
                  
                  {item.filename && (
                    <div className="mt-2 text-sm text-gray-600">
                      <strong>File:</strong> {item.filename}
                    </div>
                  )}
                  
                  {item.portName && (
                    <div className="mt-2 text-sm text-gray-600">
                      <strong>Location:</strong> {item.portName} ({item.coordinates?.lat}, {item.coordinates?.lon})
                    </div>
                  )}
                </div>
                
                <ResponseDisplay response={item.response} />
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Direct AI Query */}
        <div className="glass-effect rounded-xl shadow-lg border p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center space-x-2">
            <Brain className="w-5 h-5 text-green-600" />
            <span>Direct AI Query</span>
          </h3>
          <div className="space-y-4">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a direct maritime question..."
              className="w-full px-3 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all duration-200"
              rows="4"
            />
            <button
              onClick={handleDirectAI}
              disabled={loading || !query.trim()}
              className="w-full bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-all duration-200 font-medium card-shadow"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </div>
              ) : (
                'Ask AI'
              )}
            </button>
          </div>
        </div>

        {/* Document Summary */}
        <div className="glass-effect rounded-xl shadow-lg border p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center space-x-2">
            <FileText className="w-5 h-5 text-purple-600" />
            <span>Document Summary</span>
          </h3>
          <div className="space-y-4">
            <div className="relative">
              {!file ? (
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full flex flex-col items-center justify-center space-y-2 border-2 border-dashed border-slate-300 py-8 rounded-lg hover:border-purple-400 text-slate-600 hover:text-purple-600 transition-colors duration-200"
                >
                  <Upload className="w-8 h-8" />
                  <span className="font-medium">Upload Document</span>
                  <span className="text-sm">PDF, DOC, DOCX, or TXT</span>
                </button>
              ) : (
                <div className="p-4 bg-slate-50 rounded-lg border">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <FileText className="w-5 h-5 text-purple-600" />
                      <div>
                        <div className="font-medium text-slate-800">{file.name}</div>
                        <div className="text-sm text-slate-600">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => setFile(null)}
                      className="text-red-500 hover:text-red-700 transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>
            <button
              onClick={handleDocumentSummary}
              disabled={loading || !file}
              className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-all duration-200 font-medium card-shadow"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Summarizing...</span>
                </div>
              ) : (
                'Summarize Document'
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Weather Information */}
      <div className="glass-effect rounded-xl shadow-lg border p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-6 flex items-center space-x-2">
          <Cloud className="w-5 h-5 text-sky-600" />
          <span>Weather Information</span>
        </h3>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {majorPorts.map((port) => (
            <WeatherCard
              key={port.name}
              port={port}
              onWeatherQuery={handleWeatherQuery}
              loading={loading}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default DirectTools;