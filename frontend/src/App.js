import React, { useState, useEffect } from 'react';
import { Ship, Bot, Zap, Activity, Waves, Navigation, Mic, Map } from 'lucide-react';
import AgentChat from './components/AgentChat';
import DirectTools from './components/DirectTools';
import AgentStatus from './components/AgentStatus';
import VoiceInterface from './components/VoiceInterface';
import VoyagePlanning from './components/VoyagePlanning';
import FloatingAIAvatar from './components/FloatingAIAvatar'; // Added import
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('agent');
  const [apiHealth, setApiHealth] = useState(null);
  
  // Persistent state for conversations
  const [agentConversation, setAgentConversation] = useState([]);
  const [directToolsResponses, setDirectToolsResponses] = useState([]);
  const [voiceConversation, setVoiceConversation] = useState([]);
  const [voyageData, setVoyageData] = useState([]);

  useEffect(() => {
    checkApiHealth();
    const interval = setInterval(checkApiHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/ping');
      const data = await response.json();
      setApiHealth(data.status === 'healthy');
    } catch (error) {
      console.error('API health check failed:', error);
      setApiHealth(false);
    }
  };

  const tabs = [
    { 
      id: 'agent', 
      label: 'AI Agent', 
      icon: Bot, 
      description: 'Intelligent maritime assistant with agentic capabilities',
      gradient: 'from-blue-500 to-cyan-500'
    },
    { 
      id: 'voice', 
      label: 'Voice Interface', 
      icon: Mic, 
      description: 'Natural voice commands and audio responses for hands-free operation',
      gradient: 'from-green-500 to-emerald-500'
    },
    { 
      id: 'voyage', 
      label: 'Voyage Planning', 
      icon: Map, 
      description: 'Smart route optimization, risk analysis, and fuel planning',
      gradient: 'from-indigo-500 to-purple-500'
    },
    { 
      id: 'tools', 
      label: 'Direct Tools', 
      icon: Zap, 
      description: 'Quick access tools for immediate results',
      gradient: 'from-purple-500 to-pink-500'
    },
    { 
      id: 'status', 
      label: 'System Status', 
      icon: Activity, 
      description: 'Agent health metrics and performance monitoring',
      gradient: 'from-orange-500 to-red-500'
    }
  ];

  // Function to add a new message to agent conversation
  const addAgentMessage = (message) => {
    setAgentConversation(prev => [...prev, {
      id: Date.now(),
      timestamp: new Date(),
      ...message
    }]);
  };

  // Function to add a new response to direct tools
  const addDirectToolsResponse = (response) => {
    setDirectToolsResponses(prev => [...prev, {
      id: Date.now(),
      timestamp: new Date(),
      ...response
    }]);
  };

  // Function to add a new message to voice conversation
  const addVoiceMessage = (message) => {
    setVoiceConversation(prev => [...prev, {
      id: Date.now(),
      timestamp: new Date(),
      ...message
    }]);
  };

  // Function to clear conversation history
  const clearAgentConversation = () => {
    setAgentConversation([]);
  };

  const clearDirectToolsResponses = () => {
    setDirectToolsResponses([]);
  };

  const clearVoiceConversation = () => {
    setVoiceConversation([]);
  };

  return (
    <div className="min-h-screen bg-gray-900 particle-bg">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-20 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-2000"></div>
      </div>

      {/* Floating Ships Background */}
      <div className="ship-background">
        <div className="floating-ship ship-1"></div>
        <div className="floating-ship ship-2"></div>
        <div className="floating-ship ship-3"></div>
      </div>

      {/* Ocean Waves */}
      <div className="ocean-waves">
        <div className="wave"></div>
        <div className="wave"></div>
        <div className="wave"></div>
      </div>

      {/* Header */}
      <header className="maritime-gradient text-white shadow-2xl relative z-10 overflow-hidden">
        {/* Animated header background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-4 right-20 w-32 h-32 bg-white/5 rounded-full blur-xl animate-pulse"></div>
          <div className="absolute bottom-8 left-16 w-24 h-24 bg-cyan-300/10 rounded-full blur-lg animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/4 w-16 h-16 bg-blue-200/5 rounded-full blur-md animate-pulse delay-2000"></div>
        </div>
        
        {/* Floating header ship */}
        <div className="absolute top-6 right-32 opacity-20">
          <div className="floating-header-ship text-4xl">
            🚢
          </div>
        </div>

        {/* Subtle wave pattern overlay */}
        <div className="absolute bottom-0 left-0 right-0 h-16 opacity-10">
          <svg className="w-full h-full" viewBox="0 0 1200 120" preserveAspectRatio="none">
            <path d="M0,60 C300,20 600,100 1200,60 L1200,120 L0,120 Z" fill="currentColor" className="text-white animate-pulse">
              <animate attributeName="d" 
                       values="M0,60 C300,20 600,100 1200,60 L1200,120 L0,120 Z;
                               M0,60 C300,100 600,20 1200,60 L1200,120 L0,120 Z;
                               M0,60 C300,20 600,100 1200,60 L1200,120 L0,120 Z" 
                       dur="8s" 
                       repeatCount="indefinite"/>
            </path>
          </svg>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="w-14 h-14 bg-gradient-to-br from-white/20 to-white/5 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-white/10">
                  <Ship className="h-8 w-8 floating text-white" />
                </div>
                <Waves className="h-5 w-5 absolute -bottom-1 -right-1 text-cyan-300 animate-bounce" />
              </div>
              <div>
                <h1 className="text-4xl font-bold mb-1 bg-gradient-to-r from-white via-blue-100 to-cyan-200 bg-clip-text text-transparent">
                  Maritime AI Agent
                </h1>
                <p className="text-blue-100 text-lg flex items-center space-x-2 font-medium">
                  <Navigation className="h-5 w-5" />
                  <span>Advanced AI-powered maritime operations assistant with Voice Interface</span>
                </p>
              </div>
            </div>
            
            {/* Enhanced API Status Indicator */}
            <div className="flex items-center space-x-4">
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl px-6 py-3 border border-white/20">
                <div className="flex items-center space-x-3">
                  <div className="flex flex-col items-end">
                    <span className="text-lg font-semibold text-white">
                      System Online
                    </span>
                    <span className="text-sm text-blue-200">
                      {new Date().toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="w-5 h-5 rounded-full status-online shadow-lg"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Enhanced Navigation Tabs */}
      <nav className="bg-gray-800/50 backdrop-blur-md border-b border-gray-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-2 py-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const hasMessages = tab.id === 'agent' ? agentConversation.length > 0 : 
                                 tab.id === 'tools' ? directToolsResponses.length > 0 : 
                                 tab.id === 'voice' ? voiceConversation.length > 0 : 
                                 tab.id === 'voyage' ? voyageData.length > 0 : false;
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-3 px-6 py-3 rounded-2xl font-medium transition-all duration-300 relative group ${
                    activeTab === tab.id ? 'tab-active' : 'tab-inactive'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.label}</span>
                  
                  {/* NEW indicator for Voice Interface */}
                  {tab.id === 'voice' && (
                    <div className="absolute -top-1 -right-1 w-6 h-4 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full border-2 border-gray-800 flex items-center justify-center">
                      <span className="text-xs text-white font-bold">NEW</span>
                    </div>
                  )}
                  
                  {/* Message indicator with enhanced styling */}
                  {hasMessages && tab.id !== 'voice' && tab.id !== 'voyage' && (
                    <div className="absolute -top-1 -right-1 w-4 h-4 bg-gradient-to-r from-red-500 to-pink-500 rounded-full border-2 border-gray-800 flex items-center justify-center">
                      <span className="text-xs text-white font-bold">
                        {tab.id === 'agent' ? agentConversation.length : 
                         directToolsResponses.length}
                      </span>
                    </div>
                  )}
                  
                  {/* Hover glow effect */}
                  <div className={`absolute inset-0 rounded-2xl bg-gradient-to-r ${tab.gradient} opacity-0 group-hover:opacity-20 transition-opacity duration-300`}></div>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        <div className="space-y-8">
          {/* Enhanced Tab Description */}
          <div className="text-center">
            <div className="glass-effect rounded-2xl p-6 max-w-2xl mx-auto">
              <p className="text-gray-300 text-lg leading-relaxed">
                {tabs.find(tab => tab.id === activeTab)?.description}
              </p>
            </div>
          </div>

          {/* Tab Content with enhanced animations */}
          <div className="min-h-[600px]">
            <div className="transform transition-all duration-500 ease-in-out">
              {activeTab === 'agent' && (
                <div className="animate-in slide-in-from-right-5 duration-500">
                  <AgentChat 
                    conversation={agentConversation}
                    onAddMessage={addAgentMessage}
                    onClearConversation={clearAgentConversation}
                  />
                </div>
              )}
              {activeTab === 'voice' && (
                <div className="animate-in slide-in-from-right-5 duration-500">
                  <VoiceInterface 
                    conversation={voiceConversation}
                    onAddMessage={addVoiceMessage}
                    onClearConversation={clearVoiceConversation}
                  />
                </div>
              )}
              {activeTab === 'voyage' && (
                <div className="animate-in slide-in-from-right-5 duration-500">
                  <VoyagePlanning />
                </div>
              )}
              {activeTab === 'tools' && (
                <div className="animate-in slide-in-from-right-5 duration-500">
                  <DirectTools 
                    responses={directToolsResponses}
                    onAddResponse={addDirectToolsResponse}
                    onClearResponses={clearDirectToolsResponses}
                  />
                </div>
              )}
              {activeTab === 'status' && (
                <div className="animate-in slide-in-from-right-5 duration-500">
                  <AgentStatus />
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Enhanced Footer */}
      <footer className="bg-gray-900/50 border-t border-gray-700 mt-20 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <div className="glass-effect rounded-2xl p-6 max-w-md mx-auto">
              <p className="text-gray-400 text-sm mb-2">Maritime AI Agent v4.0 - Voice Interface</p>
              <p className="text-gray-500 text-xs">
                Powered by Advanced AI Technology with Voice Capabilities
              </p>
              <div className="mt-4 flex items-center justify-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse delay-200"></div>
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse delay-400"></div>
                <div className="w-2 h-2 bg-cyan-500 rounded-full animate-pulse delay-600"></div>
              </div>
            </div>
          </div>
        </div>
      </footer>

      {/* Floating AI Avatar - Added here */}
      <FloatingAIAvatar />
    </div>
  );
}

export default App;