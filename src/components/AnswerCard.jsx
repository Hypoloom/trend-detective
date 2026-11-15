import React from 'react';
import { AlertTriangle, CheckCircle2, HelpCircle } from 'lucide-react';
import TrendChart from './TrendChart';
import { VERDICT_LABELS } from '../askAdapter';

function axisChip(a) {
  if (a.status === 'analyzed') {
    const detected = a.verdict === 'detected';
    return {
      cls: detected ? 'badge-significant' : 'badge-unclear',
      Icon: detected ? CheckCircle2 : AlertTriangle,
      text: `${a.label}: ${VERDICT_LABELS[a.verdict] || a.verdict}${a.fragile ? ' (fragile)' : ''}`
    };
  }
  const text = {
    needs_user: `${a.label}: needs your input`,
    not_knowable: `${a.label}: cannot be known from this data`,
    data_unavailable: `${a.label}: no data available`,
    provided: `${a.label}: provided by you`
  }[a.status] || `${a.label}: ${a.status}`;
  return { cls: 'badge-nodata', Icon: HelpCircle, text };
}

const isNum = (x) => typeof x === 'number' && Number.isFinite(x);

function fmtNum(x) {
  if (!isNum(x)) return '';
  return String(Number(x.toPrecision(3)));
}

// Lines built only from the numbers in the backend's why object.
function whyLines(why, units) {
  if (!why) return [];
  const u = units ? ` ${units} per year` : ' per year';
  const out = [];
  const mv = isNum(why.meaningful_value) ? fmtNum(why.meaningful_value) : null;
  const ci = Array.isArray(why.slope_ci) && why.slope_ci.length === 2 && isNum(why.slope_ci[0]) && isNum(why.slope_ci[1])
    ? why.slope_ci : null;

  if (why.class === 'no_trend_below_meaningful') {
    if (ci && mv) out.push(`The 95% range of the estimated change (${fmtNum(ci[0])} to ${fmtNum(ci[1])}${u}) lies entirely below the ${mv}${u} chosen as meaningful.`);
    else if (mv) out.push(`The estimated change is smaller than the ${mv}${u} chosen as meaningful.`);
  } else if (why.class === 'no_trend_reaches_meaningful') {
    if (ci && mv) out.push(`The 95% range of the estimated change (${fmtNum(ci[0])} to ${fmtNum(ci[1])}${u}) reaches the ${mv}${u} chosen as meaningful, so a change of that size cannot be ruled out.`);
    else if (mv) out.push(`A change of the ${mv}${u} chosen as meaningful cannot be ruled out.`);
  } else if (why.class === 'data_limited') {
    if (isNum(why.years_have) && isNum(why.years_needed_for_meaningful)) {
      out.push(`This record has about ${fmtNum(why.years_have)} years; about ${fmtNum(why.years_needed_for_meaningful)} would be needed for the size chosen as meaningful.`);
    } else {
      out.push('The record may be too short or too noisy to show a trend.');
    }
  } else if (why.class === 'masked') {
    out.push('Regions show opposite significant trends, so the combined series can hide them.');
  } else if (why.class === 'inconclusive') {
    out.push('The evidence is mixed: the trend is not significant, and the record is not clearly too short.');
  } else if (why.class === 'no_trend') {
    out.push('No trend was found. That is not proof that nothing is changing.');
  }

  if (isNum(why.min_detectable_slope)) {
    out.push(`This record could only reliably detect trends larger than about ${fmtNum(why.min_detectable_slope)}${u}.`);
  }
  if (why.threshold_sensitive === true) {
    out.push('Halving or doubling the size chosen as meaningful changes this verdict.');
  } else if (why.threshold_sensitive === false) {
    out.push('Halving or doubling the size chosen as meaningful does not change this verdict.');
  }
  return out;
}

export default function AnswerCard({ data, activeTab = 'plain', onTabChange, chartHeight = 200 }) {
  if (!data) return null;

  if (data.kind === 'fallback') {
    return (
      <div>
        <div style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '0.4rem' }}>
          I could not match this to a topic I can analyze
        </div>
        {data.reason && <p style={{ margin: '0 0 0.5rem', fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>{data.reason}</p>}
        {data.formText && (
          <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem', padding: '0.75rem 1rem', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', background: 'var(--color-bg-card)' }}>
            {data.formText}
          </div>
        )}
      </div>
    );
  }

  const texts = data.texts || {};
  const tabs = [['plain', 'Plain'], ['detailed', 'Detailed'], ['pro', 'Pro']];
  const body = texts[activeTab] || texts.plain || '';

  const years = data.startYear && data.endYear ? `${data.startYear}\u2013${data.endYear}` : '1980\u20132025';
  const header = `${data.regionLabel || ''}${data.regionLabel ? ' \u00b7 ' : ''}NASA MERRA-2 reanalysis (model product), ${years}`;

  // The backend positions annual means at mid-year (1980.5). Show whole years.
  const chartSeries = (data.series || []).map((p) => ({ ...p, year: Math.floor(p.year) }));

  const whyAxes = (data.axes || [])
    .filter((a) => a.status === 'analyzed' && a.why)
    .map((a) => ({ label: a.label, tag: a.reasonLabel, lines: whyLines(a.why, a.units) }))
    .filter((a) => a.tag || a.lines.length > 0);

  const rw = data.riskWindow;
  const rwMonths = rw && Array.isArray(rw.month_names) && rw.month_names.length > 0 ? rw.month_names.join(', ') : '';
  const diff = rw && rw.recent_vs_earlier ? rw.recent_vs_earlier : null;
  const diffText = diff && isNum(diff.difference)
    ? `In the recent part of the record these months averaged ${fmtNum(Math.abs(diff.difference))}${diff.units ? ` ${diff.units}` : ''} ${diff.direction || ''} than in the earlier years. This is descriptive only.`
    : '';

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.6rem' }}>
        <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--color-text-main)' }}>{data.topic}</span>
        {data.kind === 'answer' && (
          <span style={{ fontSize: '0.75rem', color: 'var(--color-text-light)' }}>{header}</span>
        )}
      </div>

      {data.abstained && (
        <div style={{ padding: '0.75rem 1rem', marginBottom: '0.75rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-accent-border)', background: 'var(--color-accent-light)', fontSize: '0.88rem' }}>
          <AlertTriangle size={14} /> <strong>The data alone cannot answer this.</strong>{' '}
          {data.abstainReason}
        </div>
      )}

      <div className="tab-group" style={{ marginBottom: '0.75rem' }}>
        {tabs.map(([id, label]) => (
          <button key={id} className={`tab-btn ${activeTab === id ? 'active' : ''}`} onClick={() => onTabChange && onTabChange(id)}>
            {label}
          </button>
        ))}
      </div>

      <div style={{ background: 'var(--color-bg-card)', padding: '1rem 1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', fontSize: '0.95rem', lineHeight: 1.6, whiteSpace: 'pre-wrap', fontFamily: activeTab === 'pro' ? 'var(--font-mono)' : undefined }}>
        {body}
      </div>

      {data.axes && data.axes.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.75rem' }}>
          {data.axes.map((a, i) => {
            const c = axisChip(a);
            return (
              <span key={i} className={`badge ${c.cls}`} style={{ fontSize: '0.75rem' }}>
                <c.Icon size={12} /> {c.text}
              </span>
            );
          })}
        </div>
      )}

      {rwMonths && (
        <div style={{ marginTop: '0.75rem', padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', background: 'var(--color-bg-card)', fontSize: '0.85rem', lineHeight: 1.5 }}>
          <div style={{ fontWeight: 700, marginBottom: '0.25rem' }}>Risk window: {rwMonths}</div>
          {rw.definition && <div style={{ color: 'var(--color-text-muted)' }}>{rw.definition}</div>}
          {diffText && <div style={{ marginTop: '0.3rem' }}>{diffText}</div>}
          {rw.caveat && <div style={{ marginTop: '0.3rem', color: 'var(--color-text-muted)' }}>{rw.caveat}</div>}
        </div>
      )}

      {whyAxes.length > 0 && (
        <details style={{ marginTop: '0.75rem', padding: '0.6rem 1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', background: 'var(--color-bg-card)', fontSize: '0.85rem', lineHeight: 1.5 }}>
          <summary style={{ cursor: 'pointer', fontWeight: 700 }}>Why these results</summary>
          {whyAxes.map((a, i) => (
            <div key={i} style={{ marginTop: '0.6rem' }}>
              <div style={{ fontWeight: 600 }}>{a.label}{a.tag ? `: ${a.tag}` : ''}</div>
              {a.lines.length > 0 && (
                <ul style={{ margin: '0.25rem 0 0', paddingLeft: '1.1rem' }}>
                  {a.lines.map((l, j) => <li key={j}>{l}</li>)}
                </ul>
              )}
            </div>
          ))}
          <div style={{ marginTop: '0.6rem', color: 'var(--color-text-muted)' }}>
            The size chosen as meaningful is a project choice, not a standard. Not finding a trend is not proof that there is none.
          </div>
        </details>
      )}

      {chartSeries.length > 0 && (
        <div style={{ marginTop: '0.75rem', background: 'var(--color-bg-card)', padding: '0.75rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '0.4rem' }}>
            {data.seriesLabel}: annual anomalies
          </div>
          <TrendChart
            series={chartSeries}
            variable1Name={data.seriesLabel || 'Observed'}
            unit1=""
            height={chartHeight}
            showDownloadButtons={false}
            caption={data.hasTrendLine
              ? 'Annual means with the seasonal cycle removed (anomalies). The line is the estimated trend; the shaded band is its 95% range, not a range for individual years.'
              : 'Annual means with the seasonal cycle removed (anomalies).'}
          />
        </div>
      )}

      {data.kind === 'answer' && (
        <div style={{ fontSize: '0.75rem', color: 'var(--color-text-light)', marginTop: '0.6rem' }}>
          {data.usedLlm ? 'Wording by an LLM, checked against the computed results.' : 'Wording from fixed templates (no LLM). Numbers come from the analysis engine.'}
        </div>
      )}
    </div>
  );
}