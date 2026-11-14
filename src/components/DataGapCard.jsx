import React from 'react';
import { AlertCircle, Clock, Zap, ArrowRight, HelpCircle } from 'lucide-react';

/**
 * DataGapCard Component
 * HYPOLOOM'S SIGNATURE FEATURE:
 * When a trend is not statistically clear, explains why and what would settle it:
 * - Reason label ("Not enough data yet" | "Method limit" | "Probably no real change")
 * - Progress bar ("36 years collected, about 50 years needed")
 * - Plain-language suggestion ("Daily readings instead of monthly would help")
 */
export default function DataGapCard({
  gap = null,
  title = "Data gap analysis",
  onOpenGlossary
}) {
  if (!gap) return null;

  const { reason = "Not enough data yet", yearsHave = 36, yearsNeed = 50, tip = "" } = gap;
  const percentage = Math.min(100, Math.round((yearsHave / yearsNeed) * 100));
  const isClear = yearsHave >= yearsNeed || reason.toLowerCase().includes("no real change");

  // Reason badge styling
  const reasonClass = {
    "Not enough data yet": "badge-unclear",
    "Method limit": "badge-nodata",
    "Probably no real change": "badge-significant"
  }[reason] || "badge-unclear";

  return (
    <div
      className="card"
      style={{
        marginTop: '1.5rem',
        backgroundColor: isClear ? 'var(--color-bg-card)' : 'var(--color-accent-light)',
        borderColor: isClear ? 'var(--color-border)' : 'var(--color-accent-border)'
      }}
    >
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertCircle size={18} color={isClear ? 'var(--status-sig-text)' : 'var(--color-accent)'} />
          <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)' }}>
            {title}
          </h4>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className={`badge ${reasonClass}`}>
            {reason}
          </span>
          <button
            onClick={() => onOpenGlossary && onOpenGlossary('data_gap')}
            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, color: 'var(--color-text-light)' }}
            title="Click to learn about Data Gaps"
            aria-label="Learn about data gaps"
          >
            <HelpCircle size={14} />
          </button>
        </div>
      </div>

      {/* Subtext explanation */}
      <p style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)', marginBottom: '1rem' }}>
        {isClear
          ? `We have collected ${yearsHave} years of consistent satellite records. The observational record is long enough to verify this trend.`
          : `We have ${yearsHave} years recorded. Our statistical estimate shows about ${yearsNeed} total years would be needed to definitively settle whether this trend is real.`}
      </p>

      {/* Progress Bar (Collected vs Needed) */}
      <div className="progress-container">
        <div className="progress-track" role="progressbar" aria-valuenow={percentage} aria-valuemin="0" aria-valuemax="100">
          <div
            className="progress-fill"
            style={{
              width: `${percentage}%`,
              background: isClear
                ? 'var(--status-sig-text)'
                : 'linear-gradient(90deg, #2563EB 0%, #C85A32 100%)'
            }}
          />
        </div>
        <div className="progress-labels">
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <Clock size={13} />
            <strong>{yearsHave} years</strong> collected
          </span>
          <span style={{ color: isClear ? 'var(--status-sig-text)' : 'var(--color-accent)' }}>
            <strong>{yearsNeed} years</strong> needed ({percentage}% progress)
          </span>
        </div>
      </div>

      {/* Actionable Suggestion */}
      {tip && (
        <div
          style={{
            marginTop: '1rem',
            padding: '0.75rem 1rem',
            backgroundColor: 'var(--color-bg-card)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-border)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '0.6rem',
            fontSize: '0.85rem'
          }}
        >
          <Zap size={16} color="var(--color-accent)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong style={{ color: 'var(--color-text-main)' }}>Detective's recommendation: </strong>
            <span style={{ color: 'var(--color-text-muted)' }}>{tip}</span>
          </div>
        </div>
      )}
    </div>
  );
}
