import React, { useState } from 'react';
import { 
  ChevronDown, 
  ChevronRight, 
  Brain, 
  Zap, 
  Target, 
  BookOpen, 
  ExternalLink,
  Clock,
  FileText,
  AlertTriangle,
  CheckCircle,
  Cloud
} from 'lucide-react';

function ResponseDisplay({ response }) {
  const [showReasoning, setShowReasoning] = useState(false);
  const [showTools, setShowTools] = useState(false);
  const [showPlan, setShowPlan] = useState(false);

  if (!response) return null;

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-50 border-green-200';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getConfidenceText = (confidence) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  const getResponseIcon = () => {
    if (response.error) return <AlertTriangle className="h-6 w-6 text-red-500" />;
    if (response.type === 'weather') return <Cloud className="h-6 w-6 text-blue-500" />;
    if (response.type === 'document') return <FileText className="h-6 w-6 text-purple-500" />;
    if (response.type === 'agentic') return <Brain className="h-6 w-6 text-blue-500" />;
    return <CheckCircle className="h-6 w-6 text-green-500" />;
  };

  const getResponseTypeLabel = () => {
    switch (response.type) {
      case 'agentic': return 'Agentic AI Response';
      case 'direct': return 'Direct AI Response';
      case 'weather': return 'Weather Information';
      case 'document': return 'Document Analysis';
      case 'error': return 'Error Response';
      default: return 'Response';
    }
  };

  return (
    <div className="glass-effect rounded-xl shadow-lg border p-6">
      {/* Response Header */}
      <div className="flex items-center space-x-3 mb-6">
        {getResponseIcon()}
        <div>
          <h3 className="text-xl font-semibold text-slate-800">
            {getResponseTypeLabel()}
          </h3>
          {response.timestamp && (
            <p className="text-sm text-slate-600 flex items-center space-x-1">
              <Clock className="h-4 w-4" />
              <span>{new Date(response.timestamp).toLocaleTimeString()}</span>
            </p>
          )}
        </div>
      </div>

      {/* Main Response Content */}
      <div className={`p-4 rounded-lg border ${response.error ? 'bg-red-50 border-red-200' : 'bg-slate-50 border-slate-200'}`}>
        <div className="prose prose-sm max-w-none">
          <p className="whitespace-pre-wrap text-gray-800 leading-relaxed mb-0">
            {response.answer || response.content || 'No response content'}
          </p>
        </div>
      </div>

      {/* Confidence Score for Agentic Responses */}
      {response.confidence !== undefined && (
        <div className="mt-4 flex items-center space-x-2">
          <Target className="h-4 w-4 text-gray-500" />
          <span className="text-sm text-gray-600">Confidence:</span>
          <span className={`text-sm px-3 py-1 rounded-full border ${getConfidenceColor(response.confidence)}`}>
            {getConfidenceText(response.confidence)} ({Math.round(response.confidence * 100)}%)
          </span>
        </div>
      )}

      {/* Tools Used Section */}
      {response.tools_used && response.tools_used.length > 0 && (
        <div className="mt-6 border-t border-gray-200 pt-4">
          <button
            onClick={() => setShowTools(!showTools)}
            className="flex items-center space-x-2 text-sm text-blue-600 hover:text-blue-800 transition-colors"
          >
            {showTools ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            <Zap className="h-4 w-4" />
            <span>Tools Used ({response.tools_used.length})</span>
          </button>
          
          {showTools && (
            <div className="mt-3 space-y-2">
              {response.tools_used.map((tool, index) => (
                <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <div className="flex items-center space-x-2">
                    <Zap className="h-4 w-4 text-blue-600" />
                    <span className="font-medium text-blue-800">
                      {typeof tool === 'string' ? tool : tool.name || `Tool ${index + 1}`}
                    </span>
                  </div>
                  {typeof tool === 'object' && tool.description && (
                    <p className="text-sm text-blue-700 mt-2">{tool.description}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Execution Plan Section */}
      {response.execution_plan && (
        <div className="mt-6 border-t border-gray-200 pt-4">
          <button
            onClick={() => setShowPlan(!showPlan)}
            className="flex items-center space-x-2 text-sm text-purple-600 hover:text-purple-800 transition-colors"
          >
            {showPlan ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            <Brain className="h-4 w-4" />
            <span>Execution Plan</span>
          </button>
          
          {showPlan && (
            <div className="mt-3 bg-purple-50 border border-purple-200 rounded-lg p-4">
              <div className="prose prose-sm max-w-none">
                <p className="whitespace-pre-wrap text-purple-700 leading-relaxed">
                  {response.execution_plan}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Document-specific info */}
      {response.filename && (
        <div className="mt-4 text-sm text-slate-600 flex items-center space-x-2">
          <FileText className="h-4 w-4" />
          <span>Analyzed: {response.filename}</span>
        </div>
      )}

      {/* Weather-specific display */}
      {response.type === 'weather' && response.weatherData && (
        <div className="mt-6 border-t border-gray-200 pt-4">
          <h4 className="font-semibold text-gray-800 mb-4 flex items-center space-x-2">
            <Cloud className="h-5 w-5 text-blue-600" />
            <span>Weather Details for {response.portName}</span>
          </h4>
          
          {/* Current Weather */}
          {response.weatherData.current && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <h5 className="font-medium text-blue-800 mb-2">Current Conditions</h5>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Temperature:</span>
                  <div className="font-medium">{response.weatherData.current.temperature}°C</div>
                </div>
                <div>
                  <span className="text-gray-600">Condition:</span>
                  <div className="font-medium">{response.weatherData.current.condition}</div>
                </div>
                <div>
                  <span className="text-gray-600">Wind:</span>
                  <div className="font-medium">{response.weatherData.current.wind_speed} km/h</div>
                </div>
                <div>
                  <span className="text-gray-600">Humidity:</span>
                  <div className="font-medium">{response.weatherData.current.humidity}%</div>
                </div>
              </div>
            </div>
          )}

          {/* Bad Weather Periods */}
          {response.weatherData.bad_periods && response.weatherData.bad_periods.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h5 className="font-medium text-red-800 mb-2 flex items-center space-x-2">
                <AlertTriangle className="h-4 w-4" />
                <span>Adverse Weather Periods</span>
              </h5>
              {response.weatherData.bad_periods.map((period, index) => (
                <div key={index} className="text-sm text-red-700">
                  From {period[0]} to {period[1]}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Raw data for debugging (only in development) */}
      {process.env.NODE_ENV === 'development' && (
        <details className="mt-6 text-xs">
          <summary className="cursor-pointer text-gray-500 hover:text-gray-700">
            Debug: Raw Response Data
          </summary>
          <pre className="mt-2 bg-gray-100 p-3 rounded overflow-x-auto text-xs">
            {JSON.stringify(response, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}

export default ResponseDisplay;