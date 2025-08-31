import React, { useEffect, useRef, useState } from "react";
import { maritimeAPI } from "../services/api";

export default function MarineRobotAgent({
  personaName = "Marine AI Robot",
  avatarImage = "https://i.ibb.co/fdFjXSTC/robot.png",
  placeholder = "Type your message...",
  examples,
}) {
  const [conversation, setConversation] = useState([]);
  const [query, setQuery] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [imageError, setImageError] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(scrollToBottom, [conversation]);

  const handleAgentQuery = async () => {
    if (!query.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: "user",
      query,
      file: file ? { name: file.name } : null,
      timestamp: new Date(),
    };
    setConversation((prev) => [...prev, userMessage]);

    setLoading(true);
    const currentQuery = query;
    const currentFile = file;
    setQuery("");
    setFile(null);

    try {
      const data = await maritimeAPI.agentQuery(currentQuery, currentFile);
      const aiResponse = {
        id: Date.now() + 1,
        type: "assistant",
        response: { answer: data.answer },
      };
      setConversation((prev) => [...prev, aiResponse]);
    } catch (error) {
      const errorResponse = {
        id: Date.now() + 2,
        type: "assistant",
        response: { answer: `Error: ${error.message}`, error: true },
      };
      setConversation((prev) => [...prev, errorResponse]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => setFile(e.target.files[0]);
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && e.ctrlKey) handleAgentQuery();
  };
  const handleImageError = () => setImageError(true);

  return (
    <>
      <style>
        {`
          @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-8px); }
            100% { transform: translateY(0px); }
          }
          @keyframes blink {
            0%, 90%, 100% { opacity: 1; }
            95% { opacity: 0; }
          }
          @keyframes talking {
            0% { transform: scaleY(1); }
            50% { transform: scaleY(0.8); }
            100% { transform: scaleY(1); }
          }
        `}
      </style>

      {/* Floating Avatar & Chatbox */}
      <div
        style={{
          position: "fixed",
          bottom: "20px",
          right: "20px",
          zIndex: 9999,
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-end",
          gap: "10px",
        }}
      >
        {open && (
          <div
            style={{
              width: "360px",
              maxHeight: "500px",
              background: "#111",
              color: "#0ff",
              borderRadius: "12px",
              padding: "10px",
              display: "flex",
              flexDirection: "column",
              gap: "10px",
              boxShadow: "0 4px 16px rgba(0,0,0,0.6)",
              overflow: "hidden",
            }}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: "8px", flex: 1, overflowY: "auto" }}>
              {conversation.map((msg) => (
                <div
                  key={msg.id}
                  style={{
                    alignSelf: msg.type === "assistant" ? "flex-start" : "flex-end",
                    maxWidth: "75%",
                  }}
                >
                  <div
                    style={{
                      background: msg.type === "assistant" ? "#003366" : "#005577",
                      color: "#0ff",
                      padding: "8px 12px",
                      borderRadius: "14px",
                      wordBreak: "break-word",
                      fontSize: "14px",
                    }}
                  >
                    {msg.type === "user" ? (
                      <>
                        <p>{msg.query}</p>
                        {msg.file && <div style={{ fontSize: "12px", marginTop: "4px" }}>Attached: {msg.file.name}</div>}
                      </>
                    ) : (
                      <p>{msg.response.answer}</p>
                    )}
                  </div>
                </div>
              ))}
              {loading && <div style={{ color: "#0ff" }}>Agent is thinking...</div>}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={placeholder}
                rows={2}
                style={{
                  flex: 1,
                  padding: "6px",
                  borderRadius: "6px",
                  border: "2px solid #0ff",
                  background: "#111",
                  color: "#0ff",
                  fontSize: "14px",
                }}
              />
              <div style={{ display: "flex", gap: "6px" }}>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  style={{ padding: "4px 10px", borderRadius: "6px", border: "2px solid #0ff", color: "#0ff", fontSize: "12px" }}
                >
                  Upload
                </button>
                {file && (
                  <div style={{ color: "#0ff", fontSize: "12px" }}>
                    {file.name} <button onClick={() => setFile(null)}>✖</button>
                  </div>
                )}
                <input ref={fileInputRef} type="file" onChange={handleFileSelect} className="hidden" />
                <button
                  onClick={handleAgentQuery}
                  disabled={!query.trim() || loading}
                  style={{ padding: "4px 10px", borderRadius: "6px", background: "#0ff", color: "#000", cursor: "pointer", fontSize: "12px" }}
                >
                  {loading ? "Thinking..." : "Send"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Avatar Image with Animation */}
        <div
          onClick={() => setOpen(!open)}
          style={{
            width: "150px",
            height: "150px",
            cursor: "pointer",
            animation: "float 3s ease-in-out infinite",
          }}
        >
          {avatarImage && !imageError ? (
            <img
              src={avatarImage}
              alt={`${personaName} avatar`}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "contain",
                animation: loading ? "talking 0.3s infinite" : "blink 6s infinite",
              }}
              onError={handleImageError}
            />
          ) : (
            <div style={{ fontSize: "64px" }}>🤖</div>
          )}
        </div>
      </div>
    </>
  );
}
