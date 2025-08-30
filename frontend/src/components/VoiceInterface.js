import React, { useState, useRef, useEffect } from 'react';
import { 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  Play, 
  Pause, 
  RotateCcw,
  MessageSquare,
  Languages,
  Zap,
  Globe,
  Loader2,
  AlertTriangle,
  CheckCircle,
  Settings
} from 'lucide-react';
import { maritimeAPI } from '../services/api';

const VoiceInterface = ({ onAddMessage }) => {
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('en-US');
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [error, setError] = useState(null);
  const [shortcuts, setShortcuts] = useState([]);
  const [supportedLanguages, setSupportedLanguages] = useState([]);
  
  const recognitionRef = useRef(null);
  const audioRef = useRef(null);
  const audioContextRef = useRef(null);

  const quickCommands = [
    { command: "weather check", description: "Get weather forecast", icon: "🌤️" },
    { command: "route plan", description: "Start voyage planning", icon: "🗺️" },
    { command: "fuel optimize", description: "Analyze fuel consumption", icon: "⛽" },
    { command: "risk analysis", description: "Assess route risks", icon: "⚠️" },
    { command: "piracy zones", description: "Show security threats", icon: "🏴‍☠️" },
    { command: "port info", description: "Get port information", icon: "🏗️" },
    { command: "emergency", description: "Emergency protocols", icon: "🚨" }
  ];

  useEffect(() => {
    initializeVoiceInterface();
    loadVoiceData();
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const initializeVoiceInterface = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = selectedLanguage;

      recognitionRef.current.onstart = () => {
        setIsListening(true);
        setError(null);
      };

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          if (result.isFinal) {
            finalTranscript += result[0].transcript;
          } else {
            interimTranscript += result[0].transcript;
          }
        }

        setTranscript(finalTranscript || interimTranscript);
        
        if (finalTranscript) {
          handleVoiceCommand(finalTranscript);
        }
      };

      recognitionRef.current.onerror = (event) => {
        setError(`Speech recognition error: ${event.error}`);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    } else {
      setError('Speech recognition not supported in this browser');
    }
  };

  const loadVoiceData = async () => {
    try {
      const [shortcutsData, languagesData] = await Promise.all([
        maritimeAPI.getVoiceShortcuts(),
        maritimeAPI.getSupportedLanguages()
      ]);
      setShortcuts(shortcutsData.shortcuts || []);
      setSupportedLanguages(languagesData.languages || []);
    } catch (error) {
      console.error('Failed to load voice data:', error);
    }
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      recognitionRef.current.lang = selectedLanguage;
      recognitionRef.current.start();
      setTranscript('');
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const handleVoiceCommand = async (text) => {
    if (!text.trim()) return;

    setIsProcessing(true);
    try {
      const response = await maritimeAPI.processVoiceCommand(text);
      
      // Add message to conversation
      if (onAddMessage) {
        onAddMessage({
          type: 'user',
          query: text,
          isVoice: true
        });

        onAddMessage({
          type: 'assistant',
          response: {
            type: 'voice',
            answer: response.response,
            audioUrl: response.audio_url,
            confidence: response.confidence
          }
        });
      }

      // Play audio response if enabled
      if (voiceEnabled && response.audio_url) {
        playAudioResponse(response.audio_url);
      }

    } catch (error) {
      setError(`Voice processing error: ${error.message}`);
      if (onAddMessage) {
        onAddMessage({
          type: 'assistant',
          response: {
            type: 'error',
            answer: `Voice command failed: ${error.message}`,
            error: true
          }
        });
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const playAudioResponse = async (audioUrl) => {
    try {
      setIsPlaying(true);
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        await audioRef.current.play();
      }
    } catch (error) {
      console.error('Audio playback error:', error);
      setError('Audio playback failed');
    }
  };

  const handleQuickCommand = (command) => {
    setTranscript(command);
    handleVoiceCommand(command);
  };

  const toggleVoice = () => {
    setVoiceEnabled(!voiceEnabled);
    if (isPlaying && audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  const clearTranscript = () => {
    setTranscript('');
    setError(null);
  };

  return (
    <div className="space-y-6">
      {/* Voice Interface Header */}
      <div className="text-center py-6 maritime-gradient rounded-xl text-white">
        <div className="flex items-center justify-center mb-4">
          <div className="relative">
            <Mic className="w-12 h-12 opacity-90" />
            {isListening && (
              <div className="absolute inset-0 rounded-full bg-red-500 animate-ping opacity-75"></div>
            )}
          </div>
        </div>
        <h2 className="text-2xl font-bold mb-2">Voice Interface</h2>
        <p className="text-blue-100 mb-4">
          Speak naturally to your maritime AI assistant
        </p>
        
        {/* Status Indicators */}
        <div className="flex justify-center space-x-4 text-sm">
          <div className="flex items-center space-x-2">
            {isListening ? (
              <>
                <div className="w-3 h-3 bg-red-400 rounded-full animate-pulse"></div>
                <span>Listening...</span>
              </>
            ) : (
              <>
                <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                <span>Ready</span>
              </>
            )}
          </div>
          
          {isProcessing && (
            <div className="flex items-center space-x-2">
              <Loader2 className="w-3 h-3 animate-spin" />
              <span>Processing...</span>
            </div>
          )}
          
          {isPlaying && (
            <div className="flex items-center space-x-2">
              <Volume2 className="w-3 h-3" />
              <span>Playing...</span>
            </div>
          )}
        </div>
      </div>

      {/* Voice Controls */}
      <div className="glass-effect rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Main Controls */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Voice Controls</h3>
            
            {/* Primary Voice Button */}
            <div className="text-center">
              <button
                onClick={isListening ? stopListening : startListening}
                disabled={isProcessing}
                className={`w-20 h-20 rounded-full flex items-center justify-center text-white font-bold text-lg transition-all duration-300 ${
                  isListening 
                    ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                    : 'bg-blue-600 hover:bg-blue-700'
                } disabled:opacity-50 disabled:cursor-not-allowed card-shadow`}
              >
                {isProcessing ? (
                  <Loader2 className="w-8 h-8 animate-spin" />
                ) : isListening ? (
                  <MicOff className="w-8 h-8" />
                ) : (
                  <Mic className="w-8 h-8" />
                )}
              </button>
              <p className="text-sm text-gray-600 mt-2">
                {isListening ? 'Click to stop' : 'Click to start speaking'}
              </p>
            </div>

            {/* Secondary Controls */}
            <div className="flex justify-center space-x-4">
              <button
                onClick={toggleVoice}
                className={`p-3 rounded-lg transition-colors ${
                  voiceEnabled 
                    ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                    : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                }`}
                title={voiceEnabled ? 'Voice responses enabled' : 'Voice responses disabled'}
              >
                {voiceEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
              </button>
              
              <button
                onClick={clearTranscript}
                className="p-3 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
                title="Clear transcript"
              >
                <RotateCcw className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Settings Panel */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center space-x-2">
              <Settings className="w-5 h-5" />
              <span>Settings</span>
            </h3>
            
            {/* Language Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Languages className="w-4 h-4 inline mr-1" />
                Language
              </label>
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="en-US">English (US)</option>
                <option value="en-GB">English (UK)</option>
                <option value="es-ES">Spanish</option>
                <option value="fr-FR">French</option>
                <option value="de-DE">German</option>
                <option value="it-IT">Italian</option>
                <option value="pt-PT">Portuguese</option>
                <option value="zh-CN">Chinese (Mandarin)</option>
                <option value="ja-JP">Japanese</option>
                <option value="ko-KR">Korean</option>
              </select>
            </div>

            {/* Voice Status */}
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Speech Recognition:</span>
                <span className={`font-medium ${
                  recognitionRef.current ? 'text-green-600' : 'text-red-600'
                }`}>
                  {recognitionRef.current ? 'Supported' : 'Not Supported'}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm mt-1">
                <span className="text-gray-600">Audio Output:</span>
                <span className={`font-medium ${
                  voiceEnabled ? 'text-green-600' : 'text-gray-500'
                }`}>
                  {voiceEnabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Transcript Display */}
        {(transcript || error) && (
          <div className="mt-6 p-4 rounded-lg border">
            {error ? (
              <div className="flex items-start space-x-2 text-red-700 bg-red-50 p-3 rounded">
                <AlertTriangle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium">Error</p>
                  <p className="text-sm">{error}</p>
                </div>
              </div>
            ) : (
              <div className="flex items-start space-x-2 text-blue-700 bg-blue-50 p-3 rounded">
                <MessageSquare className="w-5 h-5 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium">Transcript</p>
                  <p className="text-sm">{transcript}</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Quick Commands */}
      <div className="glass-effect rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center space-x-2">
          <Zap className="w-5 h-5 text-orange-600" />
          <span>Quick Voice Commands</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {quickCommands.map((cmd, index) => (
            <button
              key={index}
              onClick={() => handleQuickCommand(cmd.command)}
              disabled={isProcessing}
              className="p-4 border border-gray-200 rounded-lg text-left hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{cmd.icon}</span>
                <div>
                  <div className="font-medium text-gray-800">"{cmd.command}"</div>
                  <div className="text-sm text-gray-600">{cmd.description}</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Audio Element for Playback */}
      <audio
        ref={audioRef}
        onEnded={() => setIsPlaying(false)}
        onError={() => {
          setIsPlaying(false);
          setError('Audio playback failed');
        }}
        className="hidden"
      />
    </div>
  );
};

export default VoiceInterface;