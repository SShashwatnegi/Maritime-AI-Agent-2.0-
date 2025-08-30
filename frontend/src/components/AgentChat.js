import React, { useState, useRef } from 'react';
import { 
  Send, 
  Upload, 
  Bot, 
  FileText, 
  Trash2, 
  RefreshCw,
  Play,
  Zap,
  Brain,
  History,
  MessageSquare,
  User
} from 'lucide-react';
import { maritimeAPI } from '../services/api';
import ResponseDisplay from './ResponseDisplay';

const AgentChat = ({ conversation = [], onAddMessage, onClearConversation, examples }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const handleAgentQuery = async () => {
    if (!query.trim()) return;
    
    // Add user message to conversation
    const userMessage = {
      type: 'user',
      query: query,
      file: file ? { name: file.name, size: file.size } : null
    };
    onAddMessage(userMessage);
    
    setLoading(true);
    const currentQuery = query;
    const currentFile = file;
    
    // Clear input immediately
    setQuery('');
    setFile(null);

    try {
      const data = await maritimeAPI.agentQuery(currentQuery, currentFile);
      
      // Add AI response to conversation
      const aiResponse = {
        type: 'assistant',
        response: {
          type: 'agentic',
          answer: data.answer,
          tools_used: data.tools_used,
          execution_plan: data.execution_plan,
          confidence: data.confidence,
          timestamp: data.timestamp
        }
      };
      onAddMessage(aiResponse);
      
    } catch (error) {
      // Add error response to conversation
      const errorResponse = {
        type: 'assistant',
        response: {
          type: 'error',
          answer: `Error: ${error.response?.data?.detail || error.message}`,
          error: true
        }
      };
      onAddMessage(errorResponse);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
  };

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleAgentQuery();
    }
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-8 maritime-gradient rounded-xl text-white card-shadow">
        <Bot className="w-16 h-16 mx-auto mb-4 opacity-90" />
        <h2 className="text-3xl font-bold mb-2">Intelligent Maritime Assistant</h2>
        <p className="text-xl text-blue-100 mb-6">
          Ask complex questions in natural language - I'll figure out which tools to use
        </p>
        <div className="flex justify-center space-x-6 text-sm">
          <div className="flex items-center space-x-1">
            <Zap className="w-4 h-4" />
            <span>Auto Tool Selection</span>
          </div>
          <div className="flex items-center space-x-1">
            <Brain className="w-4 h-4" />
            <span>Multi-step Reasoning</span>
          </div>
          <div className="flex items-center space-x-1">
            <History className="w-4 h-4" />
            <span>Context Memory</span>
          </div>
        </div>
      </div>

      {/* Conversation History */}
      {conversation.length > 0 && (
        <div className="glass-effect rounded-xl shadow-lg border">
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5 text-blue-600" />
              <h3 className="text-lg font-semibold text-slate-800">Conversation History</h3>
              <span className="text-sm text-gray-500">({conversation.length} messages)</span>
            </div>
            <button
              onClick={onClearConversation}
              className="flex items-center space-x-1 text-red-600 hover:text-red-800 text-sm transition-colors"
            >
              <Trash2 className="h-4 w-4" />
              <span>Clear History</span>
            </button>
          </div>
          
          <div className="max-h-96 overflow-y-auto p-4 space-y-4">
            {conversation.map((message) => (
              <div key={message.id} className="space-y-3">
                {message.type === 'user' && (
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                      <User className="h-4 w-4 text-white" />
                    </div>
                    <div className="flex-1 bg-blue-50 rounded-lg p-3 border border-blue-200">
                      <p className="text-gray-800">{message.query}</p>
                      {message.file && (
                        <div className="mt-2 text-sm text-gray-600 flex items-center space-x-1">
                          <FileText className="h-4 w-4" />
                          <span>Attached: {message.file.name}</span>
                        </div>
                      )}
                      <div className="text-xs text-gray-500 mt-2">
                        {message.timestamp?.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                )}
                
                {message.type === 'assistant' && (
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
                      <Bot className="h-4 w-4 text-white" />
                    </div>
                    <div className="flex-1">
                      <ResponseDisplay response={message.response} />
                    </div>
                  </div>
                )}
              </div>
            ))}
            
            {/* Loading indicator */}
            {loading && (
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
                  <Bot className="h-4 w-4 text-white" />
                </div>
                <div className="flex-1 bg-green-50 rounded-lg p-3 border border-green-200">
                  <div className="flex items-center space-x-2">
                    <RefreshCw className="w-4 h-4 animate-spin text-green-600" />
                    <span className="text-green-700">Agent is thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>
      )}

      {/* Query Interface */}
      <div className="glass-effect rounded-xl shadow-lg border p-6">
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Ask me anything about maritime operations:
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="e.g., Should I delay departure from Singapore due to weather? Or: Calculate demurrage for my vessel arriving Jan 15th..."
            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none transition-all duration-200"
            rows="4"
          />
          <p className="text-xs text-slate-500 mt-1">Press Ctrl+Enter to send</p>
        </div>

        {/* File Upload */}
        <div className="mb-6">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center space-x-2 px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 text-sm transition-colors duration-200"
            >
              <Upload className="w-4 h-4" />
              <span>Upload Document (Optional)</span>
            </button>
            {file && (
              <div className="flex items-center space-x-2 text-sm text-slate-600 bg-slate-50 px-3 py-2 rounded-lg">
                <FileText className="w-4 h-4" />
                <span className="truncate max-w-40">{file.name}</span>
                <button
                  onClick={() => setFile(null)}
                  className="text-red-500 hover:text-red-700 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.doc,.docx,.txt"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        <button
          onClick={handleAgentQuery}
          disabled={loading || !query.trim()}
          className="w-full flex items-center justify-center space-x-2 maritime-gradient text-white py-3 px-4 rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-all duration-200 card-shadow"
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Agent is thinking...</span>
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              <span>Ask Agent</span>
            </>
          )}
        </button>
      </div>

      {/* Example Queries */}
      {examples && (
        <div className="glass-effect rounded-xl shadow-lg border p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center space-x-2">
            <Play className="w-5 h-5 text-blue-600" />
            <span>Try These Examples</span>
          </h3>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {examples.examples.slice(0, 6).map((example, idx) => (
              <button
                key={idx}
                onClick={() => handleExampleClick(example.query)}
                className="p-4 border border-slate-200 rounded-lg text-left hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 response-card"
              >
                <div className="text-sm font-medium text-blue-700 mb-1">{example.category}</div>
                <div className="text-sm text-slate-700 mb-2 line-clamp-2">{example.query}</div>
                <div className="text-xs text-slate-500">
                  Uses: {example.tools_used.slice(0, 2).join(', ')}
                  {example.tools_used.length > 2 && '...'}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentChat;