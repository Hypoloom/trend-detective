import React, { useState } from 'react';
import { AlertTriangle, Clock, Layers, HelpCircle, CheckCircle2, ArrowRight } from 'lucide-react';
import DataGapCard from '../components/DataGapCard';
import { KNOWN_DATA_GAPS, PAGE_SECTIONS } from '../data/mockData';

/**
 * Robot Icon for "Ask about this"
 */
function TinyRobot() {
  return (
    <svg width="15" height="15" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
      <line x1="18" y1="2" x2="18" y2="7" stroke="#C85A32" strokeWidth="2.5" strokeLinecap="round" />
      <rect x="5" y="7" width="26" height="22" rx="7" fill="#FFFFFF" stroke="#0F172A" strokeWidth="2.5" />
      <rect x="8" y="10" width="20" height="9" rx="4" fill="#0F172A" />
      <circle cx="13" cy="14.5" r="2" fill="#38BDF8" />
      <circle cx="23" cy="14.5" r="2" fill="#38BDF8" />
    </svg>
  );
}

/**
 * DataGapsPage Component
 * Full-width, uncrowded design with generous 8px spacing:
 * - 3 Core reasons (max 3 cards)
 * - Earth System Data Gap matrix table
 * - Spotlight case study (Jaipur rainfall)
 * - "Ask about this" triggers for the AI Robot Assistant
 */
export default function DataGapsPage({ openGlossary, onOpenDeepDive }) {
  const [filterReason, setFilterReason] = useState('all');

  const filteredGaps = KNOWN_DATA_GAPS.filter((gap) => {
    if (filterReason === 'all') return true;
    return gap.reason === filterReason;
  });

  return (
    <div style={{ paddingTop: 'var(--space-6)', paddingBottom: 'var(--space-8)' }}>
      <div className="container">

        {/* HERO SECTION */}
        <section
          id="data-gaps-hero"
          data-section="data-gaps-teaser"
          className="section-gap"
          style={{ maxWidth: '850px' }}
        >
          <div className="eyebrow">OUR SIGNATURE INNOVATION</div>
          <h1>When a trend is not clear, we tell you what is missing.</h1>
          <p style={{ fontSize: '1.2rem', marginTop: 'var(--space-2)', lineHeight: '1.6' }}>
            In climate science, the most common answer is "Not Statistically Significant".
            Standard tools stop right there and leave the public confused.
            Hypoloom goes one step further: we estimate <em>why</em> the trend is unclear and <em>what data would settle the question</em>.
          </p>
        </section>

        {/* 3 CORE REASONS EXPLAINED (Max 3 in a row) */}
        <section className="section-gap">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-3)' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-light)' }}>
              The 3 Scientific Reasons for an Unclear Trend
            </span>
            <button
              className="ask-about-pill"
              onClick={() => onOpenDeepDive(PAGE_SECTIONS['data-gaps-teaser'])}
            >
              <TinyRobot />
              <span>Ask about these 3 reasons</span>
            </button>
          </div>

          <div className="grid-3">
            {/* Reason 1 */}
            <div className="card" style={{ padding: 'var(--space-4)', borderLeft: '4px solid var(--color-accent)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.6rem' }}>
                <span className="badge badge-unclear">Reason 1</span>
                <h3 style={{ fontSize: '1.25rem', margin: 0 }}>Not Enough Data Yet</h3>
              </div>
              <p style={{ fontSize: '0.95rem' }}>
                The climate variable (like monsoon rainfall) naturally swings wildly up and down each year.
                Even if there is a real shift underneath, 30 years isn't long enough to separate the signal from natural weather noise.
              </p>
              <div style={{ marginTop: 'var(--space-2)', fontSize: '0.85rem', color: 'var(--color-accent)', fontWeight: 600 }}>
                Solution: Keep collecting observations until the record is long enough.
              </div>
            </div>

            {/* Reason 2 */}
            <div className="card" style={{ padding: 'var(--space-4)', borderLeft: '4px solid #64748B' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.6rem' }}>
                <span className="badge badge-nodata">Reason 2</span>
                <h3 style={{ fontSize: '1.25rem', margin: 0 }}>Method / Resolution Limit</h3>
              </div>
              <p style={{ fontSize: '0.95rem' }}>
                The data's grid cells are too large, or the record is too coarse in time.
                For example, 250m MODIS pixels blur out narrow irrigation green belts amidst sand dunes.
              </p>
              <div style={{ marginTop: 'var(--space-2)', fontSize: '0.85rem', color: 'var(--color-text-main)', fontWeight: 600 }}>
                Solution: Use higher resolution sensors (30m Landsat or daily drone radar).
              </div>
            </div>

            {/* Reason 3 */}
            <div className="card" style={{ padding: 'var(--space-4)', borderLeft: '4px solid var(--status-sig-text)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.6rem' }}>
                <span className="badge badge-significant">Reason 3</span>
                <h3 style={{ fontSize: '1.25rem', margin: 0 }}>Probably No Real Change</h3>
              </div>
              <p style={{ fontSize: '0.95rem' }}>
                We have a long record and the slope is close to zero.
                That is not proof that nothing is changing: it means any change is smaller than this record can reliably detect.
              </p>
              <div style={{ marginTop: 'var(--space-2)', fontSize: '0.85rem', color: 'var(--status-sig-text)', fontWeight: 600 }}>
                Solution: A longer record or a finer view could still find a small change.
              </div>
            </div>
          </div>
        </section>

        {/* COMPARISON TABLE MATRIX */}
        <section className="section-gap">
          <div className="card" style={{ padding: 'var(--space-5)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-2)', marginBottom: 'var(--space-4)' }}>
              <div>
                <h2 style={{ fontSize: '1.6rem', marginBottom: '4px' }}>
                  Earth System Data Gap Matrix
                </h2>
                <p style={{ fontSize: '0.95rem', color: 'var(--color-text-light)', margin: 0 }}>
                  Example table (simulated data): it shows the kinds of limits a record can have. These rows are not measured results.
                </p>
              </div>

              {/* Filter tabs */}
              <div style={{ display: 'flex', gap: 'var(--space-1)', flexWrap: 'wrap' }}>
                <button
                  className={`tab-btn ${filterReason === 'all' ? 'active' : ''}`}
                  onClick={() => setFilterReason('all')}
                  style={{ fontSize: '0.8rem', padding: '0.35rem 0.8rem', border: '1px solid var(--color-border)' }}
                >
                  All ({KNOWN_DATA_GAPS.length})
                </button>
                <button
                  className={`tab-btn ${filterReason === 'Not enough data yet' ? 'active' : ''}`}
                  onClick={() => setFilterReason('Not enough data yet')}
                  style={{ fontSize: '0.8rem', padding: '0.35rem 0.8rem', border: '1px solid var(--color-border)' }}
                >
                  Not enough data
                </button>
                <button
                  className={`tab-btn ${filterReason === 'Method limit' ? 'active' : ''}`}
                  onClick={() => setFilterReason('Method limit')}
                  style={{ fontSize: '0.8rem', padding: '0.35rem 0.8rem', border: '1px solid var(--color-border)' }}
                >
                  Method limit
                </button>
              </div>
            </div>

            {/* Table */}
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Region & Variable</th>
                    <th>Sensor</th>
                    <th>Record Length</th>
                    <th>Current Verdict</th>
                    <th>Reason for Gap</th>
                    <th>What Would Settle It</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredGaps.map((row, idx) => {
                    const isClear = row.verdict === 'significant';
                    return (
                      <tr key={idx}>
                        <td>
                          <strong>{row.region}</strong>
                          <div style={{ fontSize: '0.85rem', color: 'var(--color-text-light)' }}>
                            {row.variable}
                          </div>
                        </td>
                        <td style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
                          {row.satellite}
                        </td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.9rem' }}>
                            <Clock size={13} color="var(--color-text-light)" />
                            <span><strong>{row.yearsHave}</strong> / {row.yearsNeed} yrs</span>
                          </div>
                          <div style={{ width: '80px', height: '5px', backgroundColor: 'var(--color-border)', borderRadius: '2px', marginTop: '6px' }}>
                            <div
                              style={{
                                width: `${Math.min(100, Math.round((row.yearsHave / row.yearsNeed) * 100))}%`,
                                height: '100%',
                                backgroundColor: isClear ? 'var(--status-sig-text)' : 'var(--color-accent)',
                                borderRadius: '2px'
                              }}
                            />
                          </div>
                        </td>
                        <td>
                          <span className={`badge ${isClear ? 'badge-significant' : 'badge-unclear'}`} style={{ fontSize: '0.8rem' }}>
                            {row.result}
                          </span>
                        </td>
                        <td>
                          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-muted)' }}>
                            {row.reason}
                          </span>
                          <div style={{ fontSize: '0.8rem', color: 'var(--color-text-light)', marginTop: '2px' }}>
                            {row.explanation}
                          </div>
                        </td>
                        <td>
                          <span style={{ fontSize: '0.9rem', color: isClear ? 'var(--status-sig-text)' : 'var(--color-accent)', fontWeight: 600 }}>
                            {row.whatWouldSettleIt}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* SPOTLIGHT CASE STUDY */}
        <section className="section-gap">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-2)' }}>
            <div>
              <div className="eyebrow">Spotlight Case Study</div>
              <h2>Example (simulated data): why can't we say if rainfall is declining?</h2>
            </div>
            <button
              className="ask-about-pill"
              onClick={() => onOpenDeepDive(PAGE_SECTIONS['data-gaps-matrix'])}
            >
              <TinyRobot />
              <span>Ask about this example</span>
            </button>
          </div>

          <DataGapCard
            gap={{
              reason: "Not enough data yet",
              yearsHave: 36,
              yearsNeed: 50,
              tip: "Simulated example: in this made-up case the natural year-to-year swings are much larger than the slope, so many more years of records would be needed before a trend could be separated from natural variability. This is not a result for any real region."
            }}
            title="Example (simulated data): statistical power analysis, Jaipur annual precipitation"
            onOpenGlossary={openGlossary}
          />
        </section>

      </div>
    </div>
  );
}
