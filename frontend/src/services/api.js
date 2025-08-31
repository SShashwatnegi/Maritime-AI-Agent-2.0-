import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance with detailed config
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('🚀 API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`,
      headers: config.headers,
      data: config.data
    });
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', {
      status: response.status,
      data: response.data,
      url: response.config.url
    });
    return response;
  },
  (error) => {
    console.error('❌ API Error:', {
      message: error.message,
      code: error.code,
      status: error.response?.status,
      data: error.response?.data,
      config: error.config
    });
    
    // Provide more specific error messages
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      throw new Error('Cannot connect to API server. Make sure your backend is running on http://localhost:8000');
    }
    
    return Promise.reject(error);
  }
);

// Test function to check API connectivity
const testConnection = async () => {
  try {
    console.log('🔍 Testing API connection to:', API_BASE);
    const response = await fetch(`${API_BASE.replace('/api', '')}/health`, {
      method: 'GET',
      mode: 'cors',
    });
    console.log('🏥 Health check response:', response.status);
    return response.ok;
  } catch (error) {
    console.error('🚨 Connection test failed:', error);
    return false;
  }
};

export const maritimeAPI = {
  // Test connection
  testConnection,

  // Agentic AI endpoints
  agentQuery: async (query, file = null, context = null) => {
    console.log('🤖 Agent Query Request:', { query, hasFile: !!file, context });
    
    const formData = new FormData();
    formData.append('query', query);
    if (file) {
      formData.append('file', file);
      console.log('📄 File attached:', file.name, file.size);
    }
    if (context) formData.append('context', JSON.stringify(context));

    try {
      const response = await api.post('/agent/query', formData, {
        headers: { 
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000 // Increase timeout for agent queries
      });
      return response.data;
    } catch (error) {
      console.error('🚨 Agent Query Error:', error);
      throw error;
    }
  },

  getAgentStatus: async () => {
    try {
      const response = await api.get('/agent/status');
      return response.data;
    } catch (error) {
      console.error('🚨 Agent Status Error:', error);
      throw error;
    }
  },

  getAgentExamples: async () => {
    try {
      const response = await api.get('/agent/examples');
      return response.data;
    } catch (error) {
      console.error('🚨 Agent Examples Error:', error);
      throw error;
    }
  },

  getAgentMemory: async () => {
    try {
      const response = await api.get('/agent/memory');
      return response.data;
    } catch (error) {
      console.error('🚨 Agent Memory Error:', error);
      throw error;
    }
  },

  clearAgentMemory: async () => {
    try {
      const response = await api.post('/agent/memory/clear');
      return response.data;
    } catch (error) {
      console.error('🚨 Clear Memory Error:', error);
      throw error;
    }
  },

  getAvailableTools: async () => {
    try {
      const response = await api.get('/agent/tools');
      return response.data;
    } catch (error) {
      console.error('🚨 Available Tools Error:', error);
      throw error;
    }
  },

  getComparison: async () => {
    try {
      const response = await api.get('/agent/comparison');
      return response.data;
    } catch (error) {
      console.error('🚨 Comparison Error:', error);
      throw error;
    }
  },

  // ========== NEW: Voice Interface Endpoints ==========

  // Process voice command
  processVoiceCommand: async (command, language = 'en-US') => {
    try {
      console.log('🎤 Voice Command Request:', { command, language });
      const response = await api.post('/voice/process', { 
        command, 
        language 
      });
      return response.data;
    } catch (error) {
      console.error('🚨 Voice Command Error:', error);
      throw error;
    }
  },

  // Text to Speech
  textToSpeech: async (text, language = 'en-US', voice = null) => {
    try {
      console.log('🔊 Text-to-Speech Request:', { text: text.substring(0, 50) + '...', language, voice });
      const response = await api.post('/voice/text-to-speech', {
        text,
        language,
        voice
      });
      return response.data;
    } catch (error) {
      console.error('🚨 Text-to-Speech Error:', error);
      throw error;
    }
  },

  // Voice Chat (continuous conversation)
  voiceChat: async (message, sessionId = null, context = null) => {
    try {
      console.log('💬 Voice Chat Request:', { message: message.substring(0, 50) + '...', sessionId, hasContext: !!context });
      const response = await api.post('/voice/chat', {
        message,
        session_id: sessionId,
        context
      });
      return response.data;
    } catch (error) {
      console.error('🚨 Voice Chat Error:', error);
      throw error;
    }
  },

  // Get voice shortcuts
  getVoiceShortcuts: async () => {
    try {
      console.log('⚡ Voice Shortcuts Request');
      const response = await api.get('/voice/shortcuts');
      return response.data;
    } catch (error) {
      console.error('🚨 Voice Shortcuts Error:', error);
      throw error;
    }
  },

  // Get supported languages
  getSupportedLanguages: async () => {
    try {
      console.log('🌐 Supported Languages Request');
      const response = await api.get('/voice/languages');
      return response.data;
    } catch (error) {
      console.error('🚨 Supported Languages Error:', error);
      throw error;
    }
  },

  // Get voice interface status
  getVoiceStatus: async () => {
    try {
      console.log('📊 Voice Status Request');
      const response = await api.get('/voice/status');
      return response.data;
    } catch (error) {
      console.error('🚨 Voice Status Error:', error);
      throw error;
    }
  },

  // Test voice command
  testVoiceCommand: async (command) => {
    try {
      console.log('🧪 Test Voice Command Request:', { command });
      const response = await api.post('/voice/test-command', { command });
      return response.data;
    } catch (error) {
      console.error('🚨 Test Voice Command Error:', error);
      throw error;
    }
  },

  // ========== Voyage Planning Endpoints ==========

  // Route optimization
  optimizeRoute: async (origin, destination, vessel_type = 'container', priorities = []) => {
    try {
      console.log('🗺️ Route Optimization Request:', { origin, destination, vessel_type, priorities });
      const response = await api.post('/voyage/optimize', {
        origin,
        destination,
        vessel_type,
        priorities
      });
      return response.data;
    } catch (error) {
      console.error('🚨 Route Optimization Error:', error);
      throw error;
    }
  },

  // Risk analysis
  analyzeRisks: async (route, vessel_type = 'container') => {
    try {
      console.log('⚠️ Risk Analysis Request:', { route, vessel_type });
      const response = await api.post('/voyage/analyze-risks', {
        route,
        vessel_type
      });
      return response.data;
    } catch (error) {
      console.error('🚨 Risk Analysis Error:', error);
      throw error;
    }
  },

  // Fuel optimization
  optimizeFuel: async (distance, vessel_specs, weather_conditions = null) => {
    try {
      console.log('⛽ Fuel Optimization Request:', { distance, vessel_specs, weather_conditions });
      const response = await api.post('/voyage/fuel-optimization', {
        distance,
        vessel_specs,
        weather_conditions
      });
      return response.data;
    } catch (error) {
      console.error('🚨 Fuel Optimization Error:', error);
      throw error;
    }
  },

  // Get port database
  getPorts: async (region = null, search = null) => {
    try {
      console.log('🏗️ Ports Database Request:', { region, search });
      const params = new URLSearchParams();
      if (region) params.append('region', region);
      if (search) params.append('search', search);
      
      const response = await api.get(`/voyage/ports?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('🚨 Ports Database Error:', error);
      throw error;
    }
  },

  // Get piracy zones
  getPiracyZones: async () => {
    try {
      console.log('🏴‍☠️ Piracy Zones Request');
      const response = await api.get('/voyage/piracy-zones');
      return response.data;
    } catch (error) {
      console.error('🚨 Piracy Zones Error:', error);
      throw error;
    }
  },

  // Compare routes
  compareRoutes: async (routes) => {
    try {
      console.log('⚖️ Route Comparison Request:', { routeCount: routes.length });
      const response = await api.post('/voyage/compare-routes', {
        routes
      });
      return response.data;
    } catch (error) {
      console.error('🚨 Route Comparison Error:', error);
      throw error;
    }
  },

  // Get voyage planning tools
  getVoyageTools: async () => {
    try {
      console.log('🛠️ Voyage Tools Request');
      const response = await api.get('/voyage/tools');
      return response.data;
    } catch (error) {
      console.error('🚨 Voyage Tools Error:', error);
      throw error;
    }
  },

  // ========== Direct Tool Endpoints ==========

  askDirect: async (query) => {
    try {
      console.log('🧠 Direct AI Query:', query);
      const response = await api.post('/ask', { query });
      return response.data;
    } catch (error) {
      console.error('🚨 Direct AI Error:', error);
      throw error;
    }
  },

  summarizeDocument: async (file) => {
    try {
      console.log('📄 Document Summary Request:', file.name);
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/documents/summarize', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } catch (error) {
      console.error('🚨 Document Summary Error:', error);
      throw error;
    }
  },

  getWeather: async (lat, lon) => {
    try {
      console.log('🌤️ Weather Request:', { lat, lon });
      const response = await api.get(`/weather/${lat}/${lon}`);
      return response.data;
    } catch (error) {
      console.error('🚨 Weather Error:', error);
      throw error;
    }
  },

  // Health check
  ping: async () => {
    try {
      console.log('🏓 Ping Request');
      const response = await api.get('/ping');
      return response.data;
    } catch (error) {
      console.error('🚨 Ping Error:', error);
      throw error;
    }
  }
};

export default maritimeAPI;