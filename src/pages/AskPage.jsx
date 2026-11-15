import React, { useState, useRef, useEffect } from 'react';
import { Send, Trash2, AlertCircle } from 'lucide-react';
import AnswerCard from '../components/AnswerCard';
import { askAll, LIVE_CHIPS } from '../askAdapter';

export default function AskPage({ openGlossary }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'bot',
      isWelcome: true,
      text: "Hello! I am Hypoloom's Trend Detective. Ask a question about a pond or a citrus orchard. I check NASA MERRA-2 reanalysis records (1980\u20132025) for Maharashtra, say what the data shows, and say when the data alone cannot answer.",
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSubmit = async (textToSend) => {
    const question = typeof textToSend === 'string' ? textToSend : inputText;
    if (!question.trim() || isTyping) return;

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

  const handleTabChange = (messageId, newTab) => {
    setMessages((prev) => prev.map((msg) => (msg.id === messageId ? { ...msg, activeTab: newTab } : msg)));
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: 'welcome-fresh',
        sender: 'bot',
        isWelcome: true,
        text: 'Chat cleared. Pick an example question below or type your own.',
        timestamp: new Date()
      }
    ]);
  };

  return (
    <div style={{ paddingTop: '2rem', paddingBottom: '3.5rem' }}>
      <div className="container" style={{ maxWidth: '960px' }}>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <div className="eyebrow">NATURAL LANGUAGE QUESTIONS</div>
            <h2>Ask the Trend Detective</h2>
            <p style={{ fontSize: '0.95rem', color: 'var(--color-text-muted)' }}>
              Ask in everyday English. Numbers come from NASA MERRA-2 reanalysis records analyzed by the backend. When the data cannot answer, the answer says so.
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

        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-light)', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Example Questions
          </div>
          <div className="chip-container">
            {LIVE_CHIPS.map((chip, idx) => (
              <button key={idx} type="button" className="chip" onClick={() => handleSubmit(chip)}>
                {chip}
              </button>
            ))}
          </div>
        </div>

        <div className="chat-window">
          <div className="chat-messages">
            {messages.map((msg) => {
              if (msg.sender === 'user') {
                return (
                  <div key={msg.id} className="chat-bubble chat-bubble-user">
                    <p style={{ margin: 0, fontSize: '0.95rem', color: '#FFFFFF' }}>{msg.text}</p>
                  </div>
                );
              }

              if (msg.isWelcome) {
                return (
                  <div key={msg.id} className="chat-bubble chat-bubble-bot" style={{ maxWidth: '90%' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                      <div className="brand-dot" />
                      <strong style={{ fontSize: '0.85rem' }}>Hypoloom Detective</strong>
                    </div>
                    <p style={{ fontSize: '0.95rem', color: 'var(--color-text-main)', margin: 0 }}>{msg.text}</p>
                  </div>
                );
              }

              if (msg.error) {
                return (
                  <div key={msg.id} style={{ padding: '0.75rem 1rem', backgroundColor: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 'var(--radius-md)', color: '#991B1B', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <AlertCircle size={16} />
                    <span>Could not get an answer: {msg.error}. Is the backend running on port 8000?</span>
                  </div>
                );
              }

              return (
                <div key={msg.id} className="chat-bubble chat-bubble-bot" style={{ maxWidth: '95%' }}>
                  <AnswerCard
                    data={msg.data}
                    activeTab={msg.activeTab || 'plain'}
                    onTabChange={(t) => handleTabChange(msg.id, t)}
                    chartHeight={200}
                  />
                </div>
              );
            })}

            {isTyping && (
              <div className="chat-bubble chat-bubble-bot" style={{ width: 'fit-content', padding: '0.75rem 1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
                  <div className="brand-dot" style={{ animation: 'pulse 1s infinite' }} />
                  <span>Running the analysis...</span>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmit();
            }}
            className="chat-input-area"
          >
            <input
              type="text"
              placeholder="Ask a question (e.g. 'Why is my pond turning green?')..."
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

        <div style={{ marginTop: '1rem', textAlign: 'center', fontSize: '0.8rem', color: 'var(--color-text-light)' }}>
          <strong>Honesty statement:</strong> answers use only the computed results. A trend that co-occurs with a question is not an explanation, and "no trend found" is not proof of no change.
        </div>

      </div>
    </div>
  );
}