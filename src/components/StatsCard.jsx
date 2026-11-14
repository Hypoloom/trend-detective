import React, { useState } from 'react';
import { HelpCircle, CheckCircle2, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';

/**
 * StatsCard Component
 * Implements the user's progressive disclosure rule:
 * - Plain result shown first (Rate of change + Verdict badge).
 * - Advanced stats (p-value, 95% confidence interval, sensor info) sit
 *   inside a friendly "Show details" toggle.
 */
export default function StatsCard({
  slopePerYear,
  unit = "°C",
  verdict = "significant",
  pValue = 0.001,
  ci95 = [0.04, 0.08],
  yearsUsed = 36,
  datasetName = "",
  onOpenGlossary
}) {
  const [showDetails, setShowDetails] = useState(false);

  // Format slope with sign
  const formattedSlope = (slopePerYear > 0 ? "+" : "") + slopePerYear.toFixed(3);

  // Verdict config
  const verdictConfig = {
    significant: {
      badgeClass: 'badge-significant',
      label: 'Significant',
      plainSummary: 'The long-term change is steady and almost certainly real (not weather luck).',
      subtext: pValue < 0.001 ? 'Mann-Kendall, p < 0.001' : `Mann-Kendall, p = ${pValue.toFixed(3)}`,
      icon: CheckCircle2
    },
    not_significant: {
      badgeClass: 'badge-unclear',
      label: 'Not yet clear',
      plainSummary: 'Year-to-year weather swings are wider than the subtle drift.',
      subtext: `Mann-Kendall, p = ${pValue.toFixed(3)}`,
      icon: AlertTriangle
    },
    not_enough_data: {
      badgeClass: 'badge-nodata',
      label: 'Need more data',
      plainSummary: 'Satellite records are currently too short or coarse to confirm.',
      subtext: `${yearsUsed} years recorded`,
      icon: HelpCircle
    }
  }[verdict] || {
    badgeClass: 'badge-unclear',
    label: 'Analyzing',
    plainSummary: 'Calculating trend parameters...',
    subtext: 'Inconclusive',
    icon: AlertTriangle
  };

  const VerdictIcon = verdictConfig.icon;

  return (
    <div style={{ marginTop: 'var(--space-3)', borderTop: '1px solid var(--color-border)', paddingTop: 'var(--space-3)' }}>
      {/* 1. PLAIN RESULT SHOWN FIRST (Clean & Uncrowded) */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1.25rem' }}>
        {/* Rate of Change */}
        <div>
          <span style={{ fontSize: '0.8rem', color: 'var(--color-text-light)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Rate of Change
          </span>
          <div style={{ fontSize: '1.85rem', fontWeight: 700, color: 'var(--color-text-main)', lineHeight: '1.15', margin: '2px 0' }}>
            {formattedSlope} <span style={{ fontSize: '1rem', fontWeight: 500, color: 'var(--color-text-muted)' }}>{unit}/year</span>
          </div>
          <span style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
            Average pace over {yearsUsed} years
          </span>
        </div>

        {/* Verdict Badge & Plain meaning */}
        <div>
          <span style={{ fontSize: '0.8rem', color: 'var(--color-text-light)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Is it real?
          </span>
          <div style={{ margin: '4px 0' }}>
            <span className={`badge ${verdictConfig.badgeClass}`} style={{ fontSize: '0.9rem', padding: '0.35rem 0.85rem' }}>
              <VerdictIcon size={14} />
              {verdictConfig.label}
            </span>
          </div>
          <span style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
            {verdictConfig.plainSummary}
          </span>
        </div>

        {/* "Show details" toggle button */}
        <div>
          <button
            type="button"
            className="details-toggle-btn"
            onClick={() => setShowDetails(!showDetails)}
            aria-expanded={showDetails}
          >
            <span>{showDetails ? 'Hide technical stats' : 'Show details (p-value, CI)'}</span>
            {showDetails ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
        </div>
      </div>

      {/* 2. ADVANCED DETAILS (Revealed on click) */}
      {showDetails && (
        <div className="details-drawer">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.25rem' }}>
            {/* p-value detail */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-light)' }}>
                <span>p-value (Significance)</span>
                <button
                  onClick={() => onOpenGlossary && onOpenGlossary('p_value')}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, color: 'var(--color-text-light)' }}
                  title="Learn what p-value means"
                >
                  <HelpCircle size={13} />
                </button>
              </div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-text-main)', marginTop: '2px' }}>
                {pValue < 0.001 ? '< 0.001' : pValue.toFixed(4)}
              </div>
              <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
                {verdictConfig.subtext}
              </span>
            </div>

            {/* 95% Confidence Interval */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-light)' }}>
                <span>95% Confidence Interval</span>
                <button
                  onClick={() => onOpenGlossary && onOpenGlossary('confidence_interval')}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, color: 'var(--color-text-light)' }}
                  title="Learn what Confidence Interval means"
                >
                  <HelpCircle size={13} />
                </button>
              </div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-text-main)', marginTop: '2px' }}>
                {ci95 ? `${ci95[0].toFixed(2)} to ${ci95[1].toFixed(2)}` : 'N/A'} {unit}
              </div>
              <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
                True slope lies within this bracket with 95% certainty
              </span>
            </div>

            {/* Sensor & Years */}
            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-light)' }}>
                Satellite Instrument & Record
              </div>
              <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--color-text-main)', marginTop: '4px' }}>
                {datasetName || 'NASA Satellite Sensor'}
              </div>
              <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
                Based on {yearsUsed} consecutive years (1990–2025)
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
