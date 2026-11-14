import React, { useState, useRef, useEffect } from 'react';
import { Send, Trash2, Sparkles, AlertCircle, RefreshCw, CheckCircle2, AlertTriangle, HelpCircle, BarChart2 } from 'lucide-react';
import TrendChart from '../components/TrendChart';
import { getAnswer, SAMPLE_CHIPS } from '../data/mockData';

/**
 * AskPage (Chatbot Component)
 * Features:
 * - 3 Answer levels: Plain | Detailed | Pro for every answer
 * - Example question chips
 * - Result badges: Significant (green), Not significant (amber), Not enough data (grey)
 * - Small trend chart inside/under each bot answer
 * - Typing indicator, empty state, error state, clear chat button
 * - Strict adherence to the Honesty Rule
 */
export default function AskPage({ openGlossary }) {
  // Chat messages state: initial welcoming message
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'bot',
      isWelcome: true,
      text: "Hello! I am Hypoloom's Trend Detective. Ask me about weather, climate, or seasonal shifts you've noticed (like summer heat, rainfall, blooming flowers, or groundwater). I look up 35+ years of NASA satellite observations and tell you if the trend is real.",
      timestamp: new Date()
    },
    // Pre-populate with one realistic answer so user sees the 3 tabs immediately
    {
      id: 'demo-initial',
      sender: 'user',
      text: 'Why do I feel so hot today?',
      timestamp: new Date()
    },
    {
      id: 'demo-answer',
      sender: 'bot',
      data: getAnswer('Why do I feel so hot today?'),
      activeTab: 'plain',
      timestamp: new Date()
    }
  ]);

  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [hasError, setHasError] = useState(false);
  const chatEndRef = useRef(null);

  // Auto-scroll chat to latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Handle submitting a question
  const handleSubmit = (textToSend) => {
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

    // Simulate satellite data retrieval & Mann-Kendall computation delay
    setTimeout(() => {
      try {
        const answerData = getAnswer(question);
        const botMsg = {
          id: `bot-${Date.now()}`,
          sender: 'bot',
          data: answerData,
          activeTab: 'plain',
          timestamp: new Date()
        };
        setMessages((prev) => [...prev, botMsg]);
      } catch (err) {
        setHasError(true);
      } finally {
        setIsTyping(false);
      }
    }, 700);
  };

  // Switch tab (Plain, Detailed, Pro) for a specific bot message
  const handleTabChange = (messageId, newTab) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId ? { ...msg, activeTab: newTab } : msg
      )
    );
  };

  // Clear chat back to fresh state
  const handleClearChat = () => {
    setMessages([
      {
        id: 'welcome-fresh',
        sender: 'bot',
        isWelcome: true,
        text: "Chat cleared. Pick an example question below or type your own question about satellite observations.",
        timestamp: new Date()
      }
    ]);
    setHasError(false);
  };

  return (
    <div style={{ paddingTop: '2rem', paddingBottom: '3.5rem' }}>
      <div className="container" style={{ maxWidth: '960px' }}>

        {/* Page Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <div className="eyebrow">NATURAL LANGUAGE SATELLITE QUERY</div>
            <h2>Ask the Trend Detective</h2>
            <p style={{ fontSize: '0.95rem', color: 'var(--color-text-muted)' }}>
              Ask a question in everyday English. Every answer is strictly grounded in verified NASA satellite datasets.
            </p>
          </div>

          <button
            onClick={handleClearChat}
            className="btn btn-outline btn-sm"
            style={{ borderRadius: 'var(--radius-full)', color: 'var(--color-text-light)' }}
            title="Reset conversation"
          >
            <Trash2 size={14} />
            <span>Clear chat</span>
          </button>
        </div>

        {/* Suggestion Chips */}
        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-light)', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Example Questions
          </div>
          <div className="chip-container">
            {SAMPLE_CHIPS.map((chip, idx) => (
              <button
                key={idx}
                type="button"
                className="chip"
                onClick={() => handleSubmit(chip)}
              >
                {chip}
              </button>
            ))}
          </div>
        </div>

        {/* Chat Window */}
        <div className="chat-window">
          {/* Scrollable messages area */}
          <div className="chat-messages">
            {messages.map((msg) => {
              // 1. User Message
              if (msg.sender === 'user') {
                return (
                  <div key={msg.id} className="chat-bubble chat-bubble-user">
                    <p style={{ margin: 0, fontSize: '0.95rem', color: '#FFFFFF' }}>{msg.text}</p>
                  </div>
                );
              }

              // 2. Welcome Bot Message
              if (msg.isWelcome) {
                return (
                  <div key={msg.id} className="chat-bubble chat-bubble-bot" style={{ maxWidth: '90%' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                      <div className="brand-dot" />
                      <strong style={{ fontSize: '0.85rem' }}>Hypoloom Detective</strong>
                    </div>
                    <p style={{ fontSize: '0.95rem', color: 'var(--color-text-main)', margin: 0 }}>
                      {msg.text}
                    </p>
                  </div>
                );
              }

              // 3. Structured Satellite Bot Answer
              const { data, activeTab = 'plain' } = msg;
              if (!data) return null;

              // Verdict styling
              const isSignificant = data.verdict === 'significant';
              const isNotEnough = data.verdict === 'not_enough_data';
              const badgeClass = isSignificant
                ? 'badge-significant'
                : (isNotEnough ? 'badge-nodata' : 'badge-unclear');

              const badgeLabel = isSignificant
                ? 'Significant'
                : (isNotEnough ? 'Not enough data' : 'Not significant yet');

              const confidenceLabel = isSignificant ? 'High confidence' : 'Inconclusive';

              return (
                <div key={msg.id} className="chat-bubble chat-bubble-bot" style={{ maxWidth: '95%' }}>
                  {/* Top Bar: Satellite Source & Verdict Badge */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.6rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div className="brand-dot" />
                      <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-main)' }}>
                        {data.matchedTopic || 'NASA Satellite Analysis'}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--color-text-light)' }}>
                        Â· {data.yearsUsed} years recorded
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span className={`badge ${badgeClass}`}>
                        {badgeLabel}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--color-text-light)' }}>
                        ({confidenceLabel})
                      </span>
                    </div>
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

                    {/* Content for the active tab */}
                    <div style={{ backgroundColor: '#FFFFFF', padding: '1rem 1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', fontSize: '0.95rem', lineHeight: '1.6' }}>
                      {activeTab === 'plain' && (
                        <p style={{ margin: 0, color: 'var(--color-text-main)', fontWeight: 500 }}>
                          {data.plain}
                        </p>
                      )}

                      {activeTab === 'detailed' && (
                        <div>
                          <p style={{ margin: 0, color: 'var(--color-text-main)', marginBottom: '0.5rem' }}>
                            {data.detailed}
                          </p>
                          <div style={{ fontSize: '0.8rem', color: 'var(--color-text-light)', borderTop: '1px dashed var(--color-border)', paddingTop: '0.4rem', marginTop: '0.4rem' }}>
                            ðŸ›°ï¸ <strong>Primary Instrument:</strong> {data.dataset}
                          </div>
                        </div>
                      )}

                      {activeTab === 'pro' && (
                        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: '#1E293B', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                          <div>{data.pro}</div>
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.5rem', marginTop: '0.5rem', backgroundColor: 'var(--color-bg-subtle)', padding: '0.6rem', borderRadius: '4px' }}>
                            <div><strong>Slope/yr:</strong> {data.slopePerYear > 0 ? '+' : ''}{data.slopePerYear}</div>
                            <div><strong>p-value:</strong> {data.pValue}</div>
                            <div><strong>95% CI:</strong> [{data.ci95?.[0]}, {data.ci95?.[1]}]</div>
                            <div><strong>Sample Size:</strong> n = {data.yearsUsed}</div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Inline Mini Trend Chart */}
                  {data.series && data.series.length > 0 && (
                    <div style={{ marginTop: '0.75rem', backgroundColor: '#FFFFFF', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-muted)' }}>
                          Time Series Observation & Sen's Slope
                        </span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--color-text-light)' }}>
                          1990 â†’ 2025
                        </span>
                      </div>
                      <TrendChart
                        series={data.series}
                        variable1Name="Observed"
                        unit1=""
                        height={200}
                        caption={`Black: annual reading. Orange: calculated trend (${data.slopePerYear > 0 ? '+' : ''}${data.slopePerYear}/yr).`}
                        showDownloadButtons={false}
                      />
                    </div>
                  )}

                  {/* If trend is not clear: show signature Data Gap preview! */}
                  {!isSignificant && data.gap && (
                    <div style={{ marginTop: '0.75rem', padding: '0.75rem 1rem', backgroundColor: '#FFFBEB', borderRadius: 'var(--radius-md)', border: '1px solid #FDE68A', fontSize: '0.85rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#92400E', fontWeight: 600, marginBottom: '0.2rem' }}>
                        <AlertTriangle size={14} />
                        <span>Data Gap Detected: {data.gap.reason}</span>
                      </div>
                      <p style={{ margin: 0, color: '#78350F' }}>
                        {data.gap.tip} (Collected: {data.gap.yearsHave} yrs, needed: ~{data.gap.yearsNeed} yrs)
                      </p>
                    </div>
                  )}
                </div>
              );
            })}

            {/* Typing Indicator */}
            {isTyping && (
              <div className="chat-bubble chat-bubble-bot" style={{ width: 'fit-content', padding: '0.75rem 1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
                  <div className="brand-dot" style={{ animation: 'pulse 1s infinite' }} />
                  <span>Scanning NASA satellite archives & running Mann-Kendall test...</span>
                </div>
              </div>
            )}

            {/* Error State */}
            {hasError && (
              <div style={{ padding: '0.75rem 1rem', backgroundColor: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 'var(--radius-md)', color: '#991B1B', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertCircle size={16} />
                <span>Could not process the question against satellite archives. Please try one of the suggested chips above.</span>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Chat Input Field */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmit();
            }}
            className="chat-input-area"
          >
            <input
              type="text"
              placeholder="Ask a question about weather or climate (e.g. 'Why do I feel so hot today?')..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="chat-input"
              disabled={isTyping}
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!inputText.trim() || isTyping}
              style={{ borderRadius: 'var(--radius-full)', padding: '0 1.5rem' }}
              aria-label="Send message"
            >
              <Send size={16} />
              <span>Send</span>
            </button>
          </form>
        </div>

        {/* Honesty Footnote */}
        <div style={{ marginTop: '1rem', textAlign: 'center', fontSize: '0.8rem', color: 'var(--color-text-light)' }}>
          ðŸ” <strong>Honesty Statement:</strong> The Trend Detective answers exclusively using data from the selected records. It will never invent correlations or speculate outside satellite facts.
        </div>

      </div>
    </div>
  );
}

