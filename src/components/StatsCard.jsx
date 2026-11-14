import React, { useState } from 'react';
import { HelpCircle, CheckCircle2, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';

const fmt = (x) => {
  if (x === null || x === undefined || Number.isNaN(x)) return 'N/A';
  const a = Math.abs(x);
  const d = a >= 1 ? 2 : a >= 0.1 ? 3 : 4;
  return x.toFixed(d);
};

/**
 * StatsCard: plain result first, technical stats behind a toggle.
 * Optional props: verdictLabel, fragile, sourceLabel, recordLabel, unitNote.
 */
export default function StatsCard({
  slopePerYear,
  unit = "°C",
  verdict = "significant",
  pValue = 0.001,
  ci95 = [0.04, 0.08],
  yearsUsed = 36,
  datasetName = "",
  verdictLabel = "",
  plainSummary = "",
  fragile = false,
  sourceLabel = "",
  recordLabel = "",
  unitNote = "",
  onOpenGlossary
}) {
  const [showDetails, setShowDetails] = useState(false);

  const slopeNum = Number(slopePerYear);
  const formattedSlope = (slopeNum > 0 ? "+" : "") + fmt(slopeNum);
  const pText = pValue === null || pValue === undefined
    ? 'N/A'
    : pValue < 0.001 ? '< 0.001' : pValue.toFixed(4);
  const pSub = pValue === null || pValue === undefined
    ? 'Mann-Kendall'
    : pValue < 0.001 ? 'Mann-Kendall, p < 0.001' : `Mann-Kendall, p = ${pValue.toFixed(3)}`;

  const verdictConfig = {
    significant: {
      badgeClass: 'badge-significant',
      label: 'Significant',
      plainSummary: fragile
        ? 'A trend is detected, but it depends on a few extreme years. Treat it as a candidate, not a settled result.'
        : 'The long-term change is steady and unlikely to be chance.',
      subtext: pSub,
      icon: CheckCircle2
    },
    not_significant: {
      badgeClass: 'badge-unclear',
      label: 'Not yet clear',
      plainSummary: 'No trend was found. This is not proof that nothing is changing.',
      subtext: pSub,
      icon: AlertTriangle
    },
    not_enough_data: {
      badgeClass: 'badge-nodata',
      label: 'Need more data',
      plainSummary: 'The record is currently too short or too noisy to confirm a trend.',
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
  const badgeText = verdictLabel || verdictConfig.label;
  const ciText = Array.isArray(ci95) && ci95.length === 2
    ? `${fmt(ci95[0])} to ${fmt(ci95[1])}`
    : 'N/A';

  return (
    <div style={{ marginTop: 'var(--space-3)', borderTop: '1px solid var(--color-border)', paddingTop: 'var(--space-3)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1.25rem' }}>
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
          {unitNote && (
            <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', marginTop: '2px' }}>{unitNote}</div>
          )}
        </div>

        <div>
          <span style={{ fontSize: '0.8rem', color: 'var(--color-text-light)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Is it real?
          </span>
          <div style={{ margin: '4px 0' }}>
            <span className={`badge ${verdictConfig.badgeClass}`} style={{ fontSize: '0.9rem', padding: '0.35rem 0.85rem' }}>
              <VerdictIcon size={14} />
              {badgeText}
            </span>
          </div>
          <span style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
            {plainSummary || verdictConfig.plainSummary}
          </span>
        </div>

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

      {showDetails && (
        <div className="details-drawer">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.25rem' }}>
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
                {pText}
              </div>
              <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
                {verdictConfig.subtext}
              </span>
            </div>

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
                {ciText} {unit}/year
              </div>
              <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
                Range of slopes consistent with the data (95% interval)
              </span>
            </div>

            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-light)' }}>
                Data source & record
              </div>
              <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--color-text-main)', marginTop: '4px' }}>
                {sourceLabel || datasetName || 'NASA dataset'}
              </div>
              <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
                {recordLabel || `Based on ${yearsUsed} consecutive years`}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}