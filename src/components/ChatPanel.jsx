import React, { useState, useEffect, useRef } from 'react';
import { X, Send, Trash2, ArrowLeft, CheckCircle2, AlertTriangle, HelpCircle, Sparkles, AlertCircle } from 'lucide-react';
import TrendChart from './TrendChart';
import { getAnswer, SAMPLE_CHIPS } from '../data/mockData';

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
      const initialAnswer = getAnswer(section.title, section);

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
  const handleSendMessage = (textToSend) => {
    const question = textToSend || inputText;
    if (!question.trim()) return;

    setHasError(false);
    const userMsg = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: question.trim(),
      timestamp: new Date()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsTyping(true);

    // Simulate satellite data lookup delay
    setTimeout(() => {
      try {
        const answer = getAnswer(question, currentSection);
        const botMsg = {
          id: `bot-${Date.now()}`,
          sender: 'bot',
          data: answer,
          activeTab: 'plain',
          timestamp: new Date()
        };
        setMessages((prev) => [...prev, botMsg]);
      } catch (err) {
        setHasError(true);
      } finally {
        setIsTyping(false);
      }
    }, 600);
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
                    {SAMPLE_CHIPS.slice(0, 3).map((chip, idx) => (
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

          // C) Bot Structured Answer (Plain | Detailed | Pro)
          const { data, activeTab = 'plain' } = msg;
          if (!data) return null;

          const isSignificant = data.verdict === 'significant';
          const isNotEnough = data.verdict === 'not_enough_data';
          const badgeClass = isSignificant
            ? 'badge-significant'
            : (isNotEnough ? 'badge-nodata' : 'badge-unclear');

          const badgeLabel = isSignificant
            ? 'Significant result'
            : (isNotEnough ? 'Not enough data' : 'Not significant yet');

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
              {/* Header: Topic & Verdict Badge */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.6rem' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--color-text-main)' }}>
                  {data.matchedTopic || 'NASA Satellite Analysis'}
                </span>
                <span className={`badge ${badgeClass}`} style={{ fontSize: '0.75rem' }}>
                  {badgeLabel}
                </span>
              </div>

              {/* 3 Answer Tabs: Plain | Detailed | Pro */}
              <div style={{ marginBottom: '1rem' }}>
                <div className="tab-group" style={{ marginBottom: '0.75rem' }}>
                  <button
                    className={`tab-btn ${activeTab === 'plain' ? 'active' : ''}`}
                    onClick={() => handleTabChange(msg.id, 'plain')}
                  >
                    Plain
                  </button>
                  <button
                    className={`tab-btn ${activeTab === 'detailed' ? 'active' : ''}`}
                    onClick={() => handleTabChange(msg.id, 'detailed')}
                  >
                    Detailed
                  </button>
                  <button
                    className={`tab-btn ${activeTab === 'pro' ? 'active' : ''}`}
                    onClick={() => handleTabChange(msg.id, 'pro')}
                  >
                    Pro
                  </button>
                </div>

                {/* Tab Content */}
                <div style={{ backgroundColor: 'var(--color-bg-card)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', fontSize: '0.95rem', lineHeight: '1.6' }}>
                  {activeTab === 'plain' && (
                    <p style={{ margin: 0, fontWeight: 500, color: 'var(--color-text-main)' }}>
                      {data.plain}
                    </p>
                  )}

                  {activeTab === 'detailed' && (
                    <div>
                      <p style={{ margin: 0, color: 'var(--color-text-main)', marginBottom: '0.5rem' }}>
                        {data.detailed}
                      </p>
                      <div style={{ fontSize: '0.8rem', color: 'var(--color-text-light)', borderTop: '1px dashed var(--color-border)', paddingTop: '0.4rem', marginTop: '0.4rem' }}>
                        🛰️ <strong>Sensor:</strong> {data.dataset} ({data.yearsUsed} years)
                      </div>
                    </div>
                  )}

                  {activeTab === 'pro' && (
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: 'var(--color-text-main)', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                      <div>{data.pro}</div>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem', marginTop: '0.5rem', backgroundColor: 'var(--color-bg-subtle)', padding: '0.6rem', borderRadius: '4px' }}>
                        <div><strong>Slope:</strong> {data.slopePerYear > 0 ? '+' : ''}{data.slopePerYear}/yr</div>
                        <div><strong>p-value:</strong> {data.pValue}</div>
                        <div><strong>95% CI:</strong> [{data.ci95?.[0]}, {data.ci95?.[1]}]</div>
                        <div><strong>Sample:</strong> n = {data.yearsUsed}</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Mini Trend Chart inside answer */}
              {data.series && data.series.length > 0 && (
                <div style={{ backgroundColor: 'var(--color-bg-card)', padding: '0.75rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', marginBottom: '0.75rem' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-light)', marginBottom: '0.4rem' }}>
                    Observation Series & Trendline (1990–2025)
                  </div>
                  <TrendChart
                    series={data.series}
                    variable1Name="Observed"
                    unit1=""
                    height={160}
                    showDownloadButtons={false}
                    caption=""
                  />
                </div>
              )}

              {/* Data Gap callout if unclear */}
              {!isSignificant && data.gap && (
                <div style={{ padding: '0.75rem 1rem', backgroundColor: '#FFFBEB', borderRadius: 'var(--radius-md)', border: '1px solid #FDE68A', fontSize: '0.85rem', marginBottom: '0.75rem' }}>
                  <strong style={{ color: '#92400E' }}>Data Gap: {data.gap.reason}</strong>
                  <p style={{ margin: '0.2rem 0 0', color: '#78350F' }}>
                    {data.gap.tip} ({data.gap.yearsHave} yrs collected, ~{data.gap.yearsNeed} needed)
                  </p>
                </div>
              )}

              {/* 3 Follow-Up Question Chips (as required) */}
              {data.followUps && data.followUps.length > 0 && (
                <div style={{ borderTop: '1px dashed var(--color-border)', paddingTop: '0.75rem', marginTop: '0.5rem' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-light)', textTransform: 'uppercase' }}>
                    Follow-up questions:
                  </span>
                  <div className="chip-container" style={{ marginTop: '0.35rem' }}>
                    {data.followUps.map((chip, idx) => (
                      <button
                        key={idx}
                        className="chip"
                        style={{ backgroundColor: 'var(--color-bg-card)', borderColor: 'var(--color-accent-border)' }}
                        onClick={() => handleSendMessage(chip)}
                      >
                        {chip}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}

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
