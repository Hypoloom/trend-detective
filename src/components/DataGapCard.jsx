import React from 'react';
import { AlertCircle, Clock, Zap, HelpCircle } from 'lucide-react';

/**
 * DataGapCard: when a trend is not statistically clear, explains why and what would settle it.
 * Handles: "Not enough data yet", "Method limit", "No trend found (not proof of absence)".
 */
export default function DataGapCard({
  gap = null,
  title = "Data gap analysis",
  onOpenGlossary
}) {
  if (!gap) return null;

  const { reason = "Not enough data yet", yearsHave = 0, yearsNeed = 0, tip = "" } = gap;
  const isNoTrend = reason.startsWith("No trend found");
  const isMasked = reason === "Method limit";
  const hasNeed = Number.isFinite(yearsNeed) && yearsNeed > 0;
  const percentage = hasNeed ? Math.min(100, Math.round((yearsHave / yearsNeed) * 100)) : 0;
  const isClear = isNoTrend || (hasNeed && yearsHave >= yearsNeed) || reason.toLowerCase().includes("no real change");
  const showBar = hasNeed && !isNoTrend && !isMasked;

  const reasonClass = {
    "Not enough data yet": "badge-unclear",
    "Method limit": "badge-nodata",
    "Probably no real change": "badge-significant"
  }[reason] || "badge-unclear";

  let explanation;
  if (isNoTrend) {
    explanation = `No trend was found in ${yearsHave} years of records. This is not proof that nothing is changing: only trends above a certain size could have been detected with this record.`;
  } else if (isMasked) {
    explanation = "Different regions or parts of the data move in opposite directions, so combining them can hide real changes. Looking at the parts separately may reveal more.";
  } else if (isClear) {
    explanation = `We have ${yearsHave} years of records. The record is long enough to test this trend.`;
  } else if (hasNeed) {
    explanation = `We have ${yearsHave} years recorded. Our statistical estimate suggests about ${yearsNeed} total years would be needed to settle whether this trend is real. This assumes the trend continues at its current pace.`;
  } else {
    explanation = `We have ${yearsHave} years recorded, which is not enough to settle whether this trend is real.`;
  }

  return (
    <div
      className="card"
      style={{
        marginTop: '1.5rem',
        backgroundColor: isClear ? 'var(--color-bg-card)' : 'var(--color-accent-light)',
        borderColor: isClear ? 'var(--color-border)' : 'var(--color-accent-border)'
      }}
    >
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

      <p style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)', marginBottom: showBar ? '1rem' : 0 }}>
        {explanation}
      </p>

      {showBar && (
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
      )}

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
            <strong style={{ color: 'var(--color-text-main)' }}>What would help: </strong>
            <span style={{ color: 'var(--color-text-muted)' }}>{tip}</span>
          </div>
        </div>
      )}
    </div>
  );
}