import React from 'react';
import { AlertCircle, Clock, Zap, HelpCircle, Search } from 'lucide-react';

/**
 * DataGapCard: when a trend is not statistically clear, explains why and what would settle it.
 * Handles: "Not enough data yet", "Method limit", "No trend found (not proof of absence)".
 * Optional `why` (contract.why from the backend) adds a "Why" block built only from engine numbers.
 */
const fmtNum = (v) => {
  if (v === null || v === undefined || !Number.isFinite(Number(v))) return 'n/a';
  const n = Number(v);
  if (n === 0) return '0';
  return Number(n.toPrecision(3)).toString();
};

function whyLines(why, units) {
  if (!why) return [];
  const u = units ? ` ${units} per year` : ' per year';
  const out = [];
  const ci = Array.isArray(why.slope_ci) ? why.slope_ci : null;
  const hasCi = ci && ci[0] !== null && ci[1] !== null;
  const mv = why.meaningful_value;

  if (why.class === 'no_trend_below_meaningful') {
    out.push(`The 95% range of the yearly change (${fmtNum(ci[0])} to ${fmtNum(ci[1])}${u}) lies entirely below the ${fmtNum(mv)}${u} chosen as meaningful, so a change of that size is unlikely in this record.`);
  } else if (why.class === 'no_trend_reaches_meaningful') {
    out.push(`The 95% range of the yearly change (${fmtNum(ci[0])} to ${fmtNum(ci[1])}${u}) reaches the ${fmtNum(mv)}${u} chosen as meaningful, so a change of that size cannot be ruled out.`);
  } else if (why.class === 'data_limited') {
    const need = why.years_needed_for_meaningful;
    out.push(need !== null && need !== undefined
      ? `The record has ${fmtNum(why.years_have)} years; about ${fmtNum(need)} would be needed to detect a change of ${fmtNum(mv)}${u}.`
      : `The record has ${fmtNum(why.years_have)} years, which is too short or too noisy to show a trend.`);
  } else if (why.class === 'masked') {
    out.push('Parts of the data move in opposite directions, so the combined series hides them.');
  } else if (why.class === 'inconclusive') {
    out.push('The evidence is mixed: the trend is not significant, and the record is not clearly too short.');
  } else if (hasCi) {
    out.push(`The 95% range of the yearly change is ${fmtNum(ci[0])} to ${fmtNum(ci[1])}${u}.`);
  }

  if (why.min_detectable_slope !== null && why.min_detectable_slope !== undefined) {
    out.push(`This record could only reliably detect trends larger than about ${fmtNum(why.min_detectable_slope)}${u}.`);
  }
  if (why.threshold_sensitive === true) {
    out.push('Changing the size chosen as meaningful (halving or doubling it) changes this verdict, so the verdict depends on that choice.');
  } else if (why.threshold_sensitive === false) {
    out.push('Halving or doubling the size chosen as meaningful does not change this verdict.');
  }
  return out;
}

export default function DataGapCard({
  gap = null,
  why = null,
  units = '',
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
  const lines = whyLines(why, units);

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

      <p style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)', marginBottom: (showBar || lines.length) ? '1rem' : 0 }}>
        {explanation}
      </p>

      {lines.length > 0 && (
        <div
          style={{
            marginBottom: showBar ? '1rem' : 0,
            padding: '0.75rem 1rem',
            backgroundColor: 'var(--color-bg-card)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-border)',
            fontSize: '0.85rem'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
            <Search size={15} color="var(--color-accent)" />
            <strong style={{ color: 'var(--color-text-main)' }}>Why this result</strong>
          </div>
          <ul style={{ margin: 0, paddingLeft: '1.1rem', color: 'var(--color-text-muted)' }}>
            {lines.map((l, i) => (<li key={i} style={{ marginBottom: '0.25rem' }}>{l}</li>))}
          </ul>
          <div style={{ marginTop: '0.4rem', color: 'var(--color-text-light)' }}>
            The size chosen as meaningful is a project choice, not a standard. Not finding a trend is not proof that there is none.
          </div>
        </div>
      )}

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