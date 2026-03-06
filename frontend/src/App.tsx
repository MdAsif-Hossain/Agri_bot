import { useState, useRef, useCallback, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import { sendChat, sendVoice, sendImage } from "./api/client";
import type { Message, ChatResponse } from "./api/types";

const SUGGESTIONS = [
  "What causes rice blast disease?",
  "How to treat leaf blight in wheat?",
  "ধানের পোকা দমনের উপায় কী?",
  "Best fertilizer schedule for tomato",
  "How to identify pest damage on crops?",
];

function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const addAssistantMessage = useCallback(
    (response: ChatResponse, inputMode: "text" | "voice" | "image") => {
      const assistantMsg: Message = {
        id: generateId(),
        role: "assistant",
        content: response.answer,
        answer_bn: response.answer_bn,
        input_mode: inputMode,
        evidence: {
          citations: response.citations,
          kg_entities: response.kg_entities,
          evidence_grade: response.evidence_grade,
          is_verified: response.is_verified,
          verification_reason: response.verification_reason,
          retry_count: response.retry_count,
        },
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    },
    []
  );

  const addErrorMessage = useCallback((error: string) => {
    const errMsg: Message = {
      id: generateId(),
      role: "assistant",
      content: `⚠️ ${error}`,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, errMsg]);
  }, []);

  // Text handler
  const handleSendText = useCallback(
    async (query: string) => {
      const userMsg: Message = {
        id: generateId(),
        role: "user",
        content: query,
        input_mode: "text",
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);

      try {
        const response = await sendChat(query);
        addAssistantMessage(response, "text");
      } catch (err) {
        addErrorMessage(
          err instanceof Error ? err.message : "An error occurred"
        );
      } finally {
        setIsLoading(false);
      }
    },
    [addAssistantMessage, addErrorMessage]
  );

  // Voice handler
  const handleSendVoice = useCallback(
    async (audioBlob: Blob) => {
      const userMsg: Message = {
        id: generateId(),
        role: "user",
        content: "🎤 Voice message sent...",
        input_mode: "voice",
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);

      try {
        const response = await sendVoice(audioBlob);
        addAssistantMessage(response, "voice");
      } catch (err) {
        addErrorMessage(
          err instanceof Error ? err.message : "Voice processing error"
        );
      } finally {
        setIsLoading(false);
      }
    },
    [addAssistantMessage, addErrorMessage]
  );

  // Image handler
  const handleSendImage = useCallback(
    async (file: File, query: string) => {
      const userMsg: Message = {
        id: generateId(),
        role: "user",
        content: query
          ? `📷 [Image: ${file.name}] ${query}`
          : `📷 Analyzing image: ${file.name}`,
        input_mode: "image",
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);

      try {
        const response = await sendImage(file, query);
        addAssistantMessage(response, "image");
      } catch (err) {
        addErrorMessage(
          err instanceof Error ? err.message : "Image processing error"
        );
      } finally {
        setIsLoading(false);
      }
    },
    [addAssistantMessage, addErrorMessage]
  );

  // Clear chat
  const clearChat = useCallback(() => {
    setMessages([]);
  }, []);

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main content */}
      <main className="main-content">
        {/* Header */}
        <header className="chat-header">
          <div>
            <button
              className="menu-btn"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              aria-label="Toggle menu"
            >
              ☰
            </button>
            <h2>AgriBot Chat</h2>
            <span className="chat-header-subtitle">
              Agricultural Advisory System — Bengali & English
            </span>
          </div>
          <div className="header-actions">
            {messages.length > 0 && (
              <button className="clear-btn" onClick={clearChat}>
                🗑️ Clear
              </button>
            )}
          </div>
        </header>

        {/* Chat area */}
        <div className="chat-area">
          <div className="chat-messages">
            {messages.length === 0 ? (
              <div className="welcome-container">
                <div className="welcome-icon">🌾</div>
                <h2>Welcome to AgriBot</h2>
                <p>
                  Ask questions about crops, diseases, pests, fertilizers,
                  and more. Get evidence-based answers backed by
                  agricultural manuals with full citations.
                </p>
                <div className="suggestion-chips">
                  {SUGGESTIONS.map((suggestion) => (
                    <button
                      key={suggestion}
                      className="suggestion-chip"
                      onClick={() => handleSendText(suggestion)}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))
            )}

            {/* Loading indicator */}
            {isLoading && (
              <div className="message assistant">
                <div className="message-avatar">🌾</div>
                <div className="message-body">
                  <div className="typing-indicator">
                    <div className="typing-dot" />
                    <div className="typing-dot" />
                    <div className="typing-dot" />
                    <span className="typing-text">
                      Searching documents and reasoning...
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>
        </div>

        {/* Input */}
        <ChatInput
          onSendText={handleSendText}
          onSendVoice={handleSendVoice}
          onSendImage={handleSendImage}
          disabled={isLoading}
        />
      </main>
    </div>
  );
}
