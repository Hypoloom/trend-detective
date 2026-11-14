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

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.6rem' }}>
        <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--color-text-main)' }}>{data.topic}</span>
        {data.kind === 'answer' && (
          <span style={{ fontSize: '0.75rem', color: 'var(--color-text-light)' }}>
            Maharashtra {'\u00b7'} NASA MERRA-2 reanalysis (model product), 1980{'\u2013'}2025
          </span>
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

      {data.series && data.series.length > 0 && (
        <div style={{ marginTop: '0.75rem', background: 'var(--color-bg-card)', padding: '0.75rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '0.4rem' }}>
            {data.seriesLabel}: annual anomalies
          </div>
          <TrendChart
            series={data.series}
            variable1Name={data.seriesLabel || 'Observed'}
            unit1=""
            height={chartHeight}
            showDownloadButtons={false}
            caption="Annual means with the seasonal cycle removed (anomalies)."
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