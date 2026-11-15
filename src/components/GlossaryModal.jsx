import React, { useState } from 'react';
import { X, Search, HelpCircle, BookOpen } from 'lucide-react';
import { GLOSSARY } from '../data/mockData';

/**
 * GlossaryModal Component
 * Interactive modal giving plain-language explanations of scientific terms.
 */
export default function GlossaryModal({ isOpen, onClose, selectedTermKey = null }) {
  const [searchTerm, setSearchTerm] = useState('');

  if (!isOpen) return null;

  const entries = Object.entries(GLOSSARY).filter(([key, item]) => {
    const q = searchTerm.toLowerCase();
    return item.term.toLowerCase().includes(q) ||
           item.simple.toLowerCase().includes(q) ||
           item.detail.toLowerCase().includes(q);
  });

  return (
    <div className="modal-backdrop" onClick={onClose} role="dialog" aria-modal="true" aria-labelledby="glossary-title">
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem' }}>
          <div>
            <div className="eyebrow" style={{ marginBottom: '0.25rem' }}>Plain-Language Guide</div>
            <h3 id="glossary-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <BookOpen size={20} color="var(--color-accent)" />
              Trend Glossary
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--color-text-light)' }}>
              Scientific ideas explained in simple words for students and the public.
            </p>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0.25rem', color: 'var(--color-text-light)' }}
            aria-label="Close glossary"
          >
            <X size={20} />
          </button>
        </div>

        {/* Search filter input */}
        <div style={{ position: 'relative', marginBottom: '1.25rem' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-light)' }} />
          <input
            type="text"
            placeholder="Search terms (e.g. p-value, Sen's slope, Mann-Kendall)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="chat-input"
            style={{ paddingLeft: '2.4rem', width: '100%', fontSize: '0.85rem' }}
            autoFocus
          />
        </div>

        {/* Terms List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxHeight: '55vh', overflowY: 'auto', paddingRight: '0.25rem' }}>
          {entries.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--color-text-light)' }}>
              <HelpCircle size={32} style={{ margin: '0 auto 0.5rem', opacity: 0.5 }} />
              <p>No matching terms found. Try searching for "trend", "slope", or "p-value".</p>
            </div>
          ) : (
            entries.map(([key, item]) => (
              <div
                key={key}
                style={{
                  padding: '1rem',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: selectedTermKey === key ? 'var(--color-accent-light)' : 'var(--color-bg-subtle)',
                  border: selectedTermKey === key ? '1px solid var(--color-accent-border)' : '1px solid var(--color-border)',
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)' }}>
                    {item.term}
                  </h4>
                  {selectedTermKey === key && (
                    <span className="badge badge-unclear" style={{ fontSize: '0.7rem' }}>Selected</span>
                  )}
                </div>
                {/* 1. Simple Definition */}
                <p style={{ fontSize: '0.9rem', color: 'var(--color-text-main)', marginBottom: '0.4rem', fontWeight: 500 }}>
                  💡 {item.simple}
                </p>
                {/* 2. Detail */}
                <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                  {item.detail}
                </p>
              </div>
            ))
          )}
        </div>

        {/* Close Button */}
        <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--color-border)', textAlign: 'right' }}>
          <button className="btn btn-primary btn-sm" onClick={onClose}>
            Got it, close
          </button>
        </div>
      </div>
    </div>
  );
}
