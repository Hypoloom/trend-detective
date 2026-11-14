import React, { useState, useEffect, useRef } from 'react';
import { X, Send, Trash2, ArrowLeft, CheckCircle2, AlertTriangle, HelpCircle, Sparkles, AlertCircle } from 'lucide-react';
import AnswerCard from './AnswerCard';
import { askAll, LIVE_CHIPS } from '../askAdapter';

/**
 * Robot Icon Header Illustration
 */
function MiniRobot() {
  return (
    <svg width="22" height="22" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="5" y="7" width="26" height="22" rx="7" fill="#FFFFFF" stroke="#0F172A" strokeWidth="2.5" />
      <rect x="8" y="10" width="20" height="9" rx="4" fill="#0F172A" />
      <circle cx="13" cy="14.5" r="2" fill="#38BDF8" />
      <circle cx="23" cy="14.5" r="2" fill="#38BDF8" />
      <path d="M14 24.5C15.2 26 20.8 26 22 24.5" stroke="#0F172A" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

/**
 * ChatPanel Component
 * Slides in on the RIGHT HALF of the screen (50% on desktop, fullscreen on mobile/tablet).
 * When open, page content shifts and reflows into the left 50%.
 */
export default function ChatPanel({
  isOpen = false,
  onClose,
  currentSection = null,
  initialDeepDive = null
}) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [hasError, setHasError] = useState(false);

  const panelRef = useRef(null);
  const inputRef = useRef(null);
  const chatEndRef = useRef(null);

  // When panel opens with a deep dive request, auto-generate the deep dive sequence!
  useEffect(() => {
    if (isOpen && initialDeepDive) {
      const section = initialDeepDive;
      const dd = section.deepDive || {};
      const initialAnswer = {
        kind: 'summary',
        topic: section.title,
        texts: {
          plain: dd.plain || section.summary || '',
          detailed: dd.detailed || '',
          pro: dd.pro || ''
        }
      };

      setMessages([
        {
          id: `deepdive-${Date.now()}`,
          sender: 'bot',
          isDeepDive: true,
          sectionTitle: section.title,
          data: initialAnswer,
          activeTab: 'plain',
          timestamp: new Date()
        }
      ]);
    } else if (isOpen && messages.length === 0) {
      // Default welcome state
      setMessages([
        {
          id: 'welcome',
          sender: 'bot',
          isWelcome: true,
          text: `Hello! I am Hypoloom's AI Robot Detective. Ask me about weather, climate trends, or anything on this page. Every answer is strictly grounded in NASA satellite records.`,
          timestamp: new Date()
        }
      ]);
    }
  }, [isOpen, initialDeepDive]);

  // Focus trap & Escape key listener
  useEffect(() => {
    if (!isOpen) return;

    // Focus input when opened
    setTimeout(() => inputRef.current?.focus(), 150);

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Submit a question  
  const handleSendMessage = async (textToSend) => {
    const question = typeof textToSend === 'string' ? textToSend : inputText;
    if (!question.trim() || isTyping) return;

    setHasError(false);
    setMessages((prev) => [...prev, { id: `user-${Date.now()}`, sender: 'user', text: question.trim(), timestamp: new Date() }]);
    setInputText('');
    setIsTyping(true);
    try {
      const data = await askAll(question.trim(), 'maharashtra');
      setMessages((prev) => [...prev, { id: `bot-${Date.now()}`, sender: 'bot', data, activeTab: 'plain', timestamp: new Date() }]);
    } catch (err) {
      setMessages((prev) => [...prev, { id: `err-${Date.now()}`, sender: 'bot', error: err.message, timestamp: new Date() }]);
    } finally {
      setIsTyping(false);
    }
  };

  // Change answer tab (Plain, Detailed, Pro)
  const handleTabChange = (messageId, tab) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId ? { ...msg, activeTab: tab } : msg
      )
    );
  };

  // Clear chat
  const handleClearChat = () => {
    setMessages([
      {
        id: 'fresh-welcome',
        sender: 'bot',
        isWelcome: true,
        text: `Chat cleared. Pick an example question below or type your own question about satellite observations.`,
        timestamp: new Date()
      }
    ]);
  };

  return (
    <aside
      ref={panelRef}
      className={`chat-panel-container ${isOpen ? 'open' : ''}`}
      aria-label="Hypoloom AI Robot Assistant Chat"
      role="dialog"
      aria-modal="true"
    >
      {/* 1. CHAT HEADER */}
      <div className="chat-panel-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{ width: 32, height: 32, borderRadius: '50%', backgroundColor: 'var(--color-bg-subtle)', border: '1px solid var(--color-border-dark)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <MiniRobot />
          </div>
          <div>
            <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--color-text-main)' }}>
              Trend Detective Robot
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-light)' }}>
              {currentSection ? `Context: ${currentSection.title}` : 'Earth System Intelligence'}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            onClick={handleClearChat}
            className="btn btn-outline btn-sm"
            style={{ fontSize: '0.75rem', padding: '0.25rem 0.55rem', borderRadius: 'var(--radius-full)' }}
            title="Clear chat messages"
          >
            <Trash2 size={13} />
            <span>Clear</span>
          </button>
          <button
            onClick={onClose}
            className="btn btn-outline btn-sm"
            style={{ padding: '0.3rem 0.6rem', borderRadius: 'var(--radius-full)' }}
            aria-label="Close assistant panel"
            title="Close chat panel (Esc)"
          >
            <X size={16} />
            <span className="mobile-only">Close</span>
          </button>
        </div>
      </div>

      {/* 2. CHAT BODY (SCROLLABLE MESSAGES) */}
      <div className="chat-panel-body">
        {messages.map((msg) => {
          // A) User Message
          if (msg.sender === 'user') {
            return (
              <div
                key={msg.id}
                style={{
                  alignSelf: 'flex-end',
                  backgroundColor: '#0F172A',
                  color: '#FFFFFF',
                  padding: '0.8rem 1.1rem',
                  borderRadius: '16px 16px 4px 16px',
                  maxWidth: '85%',
                  fontSize: '0.95rem'
                }}
              >
                {msg.text}
              </div>
            );
          }

          // B) Bot Welcome Message
          if (msg.isWelcome) {
            return (
              <div
                key={msg.id}
                style={{
                  alignSelf: 'flex-start',
                  backgroundColor: 'var(--color-bg-subtle)',
                  border: '1px solid var(--color-border)',
                  padding: '1rem',
                  borderRadius: '16px 16px 16px 4px',
                  maxWidth: '90%',
                  fontSize: '0.95rem'
                }}
              >
                <p style={{ margin: 0, color: 'var(--color-text-main)' }}>{msg.text}</p>
                <div style={{ marginTop: '0.75rem' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-light)', textTransform: 'uppercase' }}>
                    Try asking:
                  </span>
                  <div className="chip-container">
                      {LIVE_CHIPS.map((chip, idx) => (
                      <button
                        key={idx}
                        className="chip"
                        onClick={() => handleSendMessage(chip)}
                      >
                        {chip}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            );
          }


          // C) Bot answer (backend text, or Explorer summary for the deep dive)
          if (msg.error) {
            return (
              <div key={msg.id} style={{ padding: '0.75rem 1rem', backgroundColor: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 'var(--radius-md)', color: '#991B1B', fontSize: '0.85rem' }}>
                <AlertCircle size={15} style={{ display: 'inline', marginRight: '4px' }} />
                Could not get an answer: {msg.error}. Is the backend running?
              </div>
            );
          }
          return (
            <div
              key={msg.id}
              style={{
                alignSelf: 'flex-start',
                backgroundColor: 'var(--color-bg-subtle)',
                border: '1px solid var(--color-border)',
                padding: '1.25rem',
                borderRadius: '16px 16px 16px 4px',
                width: '100%'
              }}
            >
              <AnswerCard
                data={msg.data}
                activeTab={msg.activeTab || 'plain'}
                onTabChange={(t) => handleTabChange(msg.id, t)}
                chartHeight={160}
              />
            </div>
          );        })}

        {/* Typing indicator */}
        {isTyping && (
          <div style={{ alignSelf: 'flex-start', padding: '0.6rem 1rem', backgroundColor: 'var(--color-bg-subtle)', borderRadius: 'var(--radius-md)', fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
              <Sparkles size={14} color="var(--color-accent)" />
              Robot Detective is scanning satellite records...
            </span>
          </div>
        )}

        {/* Error notification */}
        {hasError && (
          <div style={{ padding: '0.75rem 1rem', backgroundColor: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 'var(--radius-md)', color: '#991B1B', fontSize: '0.85rem' }}>
            <AlertCircle size={15} style={{ display: 'inline', marginRight: '4px' }} />
            Could not retrieve satellite answer. Try clicking one of the suggested chips.
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* 3. FIXED CHAT INPUT FOOTER */}
      <div className="chat-panel-footer">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          style={{ display: 'flex', gap: '0.5rem' }}
        >
          <input
            ref={inputRef}
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask anything about this chart or region..."
            className="chat-input"
            disabled={isTyping}
          />
          <button
            type="submit"
            className="btn btn-primary"
            style={{ borderRadius: 'var(--radius-full)', padding: '0 1.25rem' }}
            disabled={!inputText.trim() || isTyping}
            aria-label="Send message to robot detective"
          >
            <Send size={16} />
          </button>
        </form>
        <div style={{ fontSize: '0.72rem', color: 'var(--color-text-light)', marginTop: '0.4rem', textAlign: 'center' }}>
          🛡️ <strong>Honesty Rule:</strong> Answers only from satellite data. Never hallucinates statistics.
        </div>
      </div>
    </aside>
  );
}
