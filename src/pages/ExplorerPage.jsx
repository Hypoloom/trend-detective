import React, { useState, useMemo, useEffect } from 'react';
import { CheckCircle2, AlertTriangle } from 'lucide-react';
import TrendChart from '../components/TrendChart';
import StatsCard from '../components/StatsCard';
import DataGapCard from '../components/DataGapCard';
import { REGIONS as MOCK_REGIONS_ALL, VARIABLES as MOCK_VARIABLES, getSeries as getMockSeries } from '../data/mockData';
import { fetchSeries, LIVE_REGIONS, LIVE_VARIABLES } from '../api';

// The mock "rajasthan" clashes with the live id and carries false claims, so it is dropped here.
const MOCK_REGIONS = MOCK_REGIONS_ALL
  .filter((r) => r.id !== 'rajasthan')
  .map((r) => ({ ...r, name: `${r.name} (simulated)` }));
const ALL_REGIONS = [...LIVE_REGIONS, ...MOCK_REGIONS];
const isLiveRegion = (id) => LIVE_REGIONS.some((r) => r.id === id);

const VERDICT_LABELS = {
  detected: 'Trend detected',
  no_trend: 'No trend found',
  data_limited: 'Data-limited',
  masked: 'Masked by aggregation',
  inconclusive: 'Inconclusive'
};

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

const SELECT_STYLE = {
  width: '100%', padding: '0.65rem 0.9rem', borderRadius: 'var(--radius-md)',
  border: '1px solid var(--color-border-dark)', fontSize: '0.95rem',
  backgroundColor: 'var(--color-bg-card)', color: 'var(--color-text-main)'
};
const LABEL_STYLE = {
  display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--color-text-light)',
  textTransform: 'uppercase', marginBottom: '6px'
};

export default function ExplorerPage({ openGlossary, onUpdateRobotContext, onOpenDeepDive }) {
  const [selectedRegionId, setSelectedRegionId] = useState('maharashtra');
  const [selectedVar1Id, setSelectedVar1Id] = useState('T2M');
  const [selectedVar2Id, setSelectedVar2Id] = useState('');
  const [startYear, setStartYear] = useState(1980);
  const [endYear, setEndYear] = useState(2025);
  const [isChartLoading, setIsChartLoading] = useState(false);
  const [baseData1, setBaseData1] = useState(null);
  const [baseData2, setBaseData2] = useState(null);
  const [error, setError] = useState(null);

  const isLive = isLiveRegion(selectedRegionId);
  const variables = isLive ? LIVE_VARIABLES : MOCK_VARIABLES;
  const sliderMin = isLive ? 1980 : 1990;

  const currentRegion = useMemo(
    () => ALL_REGIONS.find((r) => r.id === selectedRegionId) || ALL_REGIONS[0],
    [selectedRegionId]
  );
  const currentVar1 = useMemo(
    () => variables.find((v) => v.id === selectedVar1Id) || variables[0],
    [variables, selectedVar1Id]
  );
  const currentVar2 = useMemo(() => {
    if (!selectedVar2Id) return null;
    return variables.find((v) => v.id === selectedVar2Id) || null;
  }, [variables, selectedVar2Id]);

  // Load data: live regions call the backend, mock regions use the in-memory mock.
  useEffect(() => {
    let cancelled = false;
    setError(null);
    if (!isLive) {
      setBaseData1(getMockSeries(selectedRegionId, selectedVar1Id));
      setBaseData2(selectedVar2Id ? getMockSeries(selectedRegionId, selectedVar2Id) : null);
      return undefined;
    }
    setIsChartLoading(true);
    Promise.all([
      fetchSeries(selectedVar1Id, selectedRegionId),
      selectedVar2Id ? fetchSeries(selectedVar2Id, selectedRegionId) : Promise.resolve(null)
    ])
      .then(([a, b]) => {
        if (!cancelled) {
          setBaseData1(a);
          setBaseData2(b);
        }
      })
      .catch((e) => {
        if (!cancelled) setError(e.message);
      })
      .finally(() => {
        if (!cancelled) setIsChartLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedRegionId, selectedVar1Id, selectedVar2Id, isLive]);

  const filteredSeries1 = useMemo(() => {
    if (!baseData1 || !baseData1.series) return [];
    return baseData1.series.filter((pt) => pt.year >= startYear && pt.year <= endYear);
  }, [baseData1, startYear, endYear]);

  const filteredSeries2 = useMemo(() => {
    if (!baseData2 || !baseData2.series) return null;
    return baseData2.series.filter((pt) => pt.year >= startYear && pt.year <= endYear);
  }, [baseData2, startYear, endYear]);

  const yearsInSlice = endYear - startYear + 1;

  useEffect(() => {
    if (onUpdateRobotContext && baseData1 && baseData1.summary) {
      onUpdateRobotContext({
        id: `explorer-${selectedRegionId}-${selectedVar1Id}`,
        title: `${currentVar1.name} in ${currentRegion.name}`,
        summary: baseData1.summary.plain,
        deepDive: baseData1.summary,
        suggestedQuestions: [
          `Why is ${currentVar1.name} changing in ${currentRegion.name}?`,
          `Is this trend statistically significant?`,
          `How should I read the orange trend line?`
        ]
      });
    }
  }, [selectedRegionId, selectedVar1Id, selectedVar2Id, currentRegion, currentVar1, baseData1]);

  const handleRegionChange = (newRegion) => {
    const live = isLiveRegion(newRegion);
    setSelectedRegionId(newRegion);
    setSelectedVar1Id(live ? LIVE_VARIABLES[0].id : MOCK_VARIABLES[0].id);
    setSelectedVar2Id('');
    setStartYear(live ? 1980 : 1990);
    setEndYear(2025);
    setBaseData1(null);
    setBaseData2(null);
  };

  const handleVar1Change = (newVar) => {
    setSelectedVar1Id(newVar);
    if (selectedVar2Id === newVar) setSelectedVar2Id('');
  };

  if (!baseData1) {
    return (
      <div className="container" style={{ paddingTop: 'var(--space-8)', paddingBottom: 'var(--space-8)' }}>
        <h1>Earth System Data Explorer</h1>
        <p>
          {error
            ? `Could not load data: ${error}. Is the backend running on port 8000?`
            : 'Loading analysis...'}
        </p>
      </div>
    );
  }

  const verdictCode = baseData1.verdict_code;
  const isSignificant = baseData1.verdict === 'significant';
  const badgeLabel = isLive ? (VERDICT_LABELS[verdictCode] || 'Unknown') : (isSignificant ? 'Significant Trend' : 'Inconclusive Trend');
  const chartCaption = currentVar2
    ? `Black line: ${currentVar1.name} (${currentVar1.unit}, left axis). Blue line: ${currentVar2.name} (${currentVar2.unit}, right axis). Orange dashed: trend line.`
    : isLive
      ? (baseData1.caption || 'Annual means of the deseasonalized series. Orange dashed: Theil-Sen trend line.')
      : `Black dots: annual observations. Orange dashed: Sen's slope trendline (${baseData1.slopePerYear} ${currentVar1.unit}/year).`;

  const deepDivePayload = {
    id: `explorer-${selectedRegionId}-${selectedVar1Id}`,
    title: `${currentVar1.name} in ${currentRegion.name}`,
    summary: baseData1.summary.plain,
    deepDive: baseData1.summary,
    suggestedQuestions: [
      `Why is ${currentVar1.name} changing in ${currentRegion.name}?`,
      `Is this trend statistically significant?`,
      `How should I read the orange trend line?`
    ]
  };

  return (
    <div style={{ paddingTop: 'var(--space-6)', paddingBottom: 'var(--space-8)' }}>
      <div className="container">

        <section className="section-gap" style={{ marginBottom: 'var(--space-4)' }}>
          <div className="eyebrow">INTERACTIVE SCIENTIFIC WORKBENCH</div>
          <h1>Earth System Data Explorer</h1>
          <p style={{ fontSize: '1.2rem', maxWidth: '75ch' }}>
            Explore NASA Earth-science data across regions and time periods. Measure the speed of change and see if it stands out from natural noise.
          </p>
        </section>

        {!isLive && (
          <div className="card" style={{ padding: 'var(--space-3)', marginBottom: 'var(--space-3)' }}>
            <strong>Simulated data.</strong> This region uses invented sample numbers for layout only. Pick a live region to see real results.
          </div>
        )}
        {error && (
          <div className="card" style={{ padding: 'var(--space-3)', marginBottom: 'var(--space-3)' }}>
            Could not refresh data: {error}
          </div>
        )}

        <div className="card" style={{ padding: 'var(--space-4)', marginBottom: 'var(--space-4)', backgroundColor: 'var(--color-bg-subtle)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'var(--space-3)', alignItems: 'flex-end' }}>

            <div>
              <label style={LABEL_STYLE}>1. Select Region</label>
              <select className="select-control" style={SELECT_STYLE} value={selectedRegionId} onChange={(e) => handleRegionChange(e.target.value)}>
                <optgroup label="Live (NASA MERRA-2)">
                  {LIVE_REGIONS.map((r) => (<option key={r.id} value={r.id}>{r.name}</option>))}
                </optgroup>
                <optgroup label="Simulated">
                  {MOCK_REGIONS.map((r) => (<option key={r.id} value={r.id}>{r.name}</option>))}
                </optgroup>
              </select>
            </div>

            <div>
              <label style={LABEL_STYLE}>2. Primary Variable</label>
              <select className="select-control" style={SELECT_STYLE} value={selectedVar1Id} onChange={(e) => handleVar1Change(e.target.value)}>
                {variables.map((v) => (<option key={v.id} value={v.id}>{v.name} ({v.unit})</option>))}
              </select>
            </div>

            <div>
              <label style={{ ...LABEL_STYLE, display: 'flex', justifyContent: 'space-between' }}>
                <span>3. Second Variable (Optional)</span>
                {selectedVar2Id && (
                  <button
                    onClick={() => setSelectedVar2Id('')}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-accent)', fontSize: '0.75rem', padding: 0 }}
                  >
                    Clear
                  </button>
                )}
              </label>
              <select className="select-control" style={SELECT_STYLE} value={selectedVar2Id} onChange={(e) => setSelectedVar2Id(e.target.value)}>
                <option value="">-- None (Single Variable) --</option>
                {variables.filter((v) => v.id !== selectedVar1Id).map((v) => (
                  <option key={v.id} value={v.id}>{v.name} ({v.unit})</option>
                ))}
              </select>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--color-text-light)', textTransform: 'uppercase' }}>
                  Chart years: {startYear} – {endYear}
                </span>
                <span style={{ fontSize: '0.8rem', color: 'var(--color-accent)', fontWeight: 600 }}>
                  ({yearsInSlice} years)
                </span>
              </div>
              <div style={{ display: 'flex', gap: 'var(--space-1)', alignItems: 'center' }}>
                <input
                  type="range" min={sliderMin} max="2020" value={startYear}
                  onChange={(e) => setStartYear(Math.min(Number(e.target.value), endYear - 5))}
                  style={{ width: '100%', accentColor: 'var(--color-accent)', cursor: 'pointer' }}
                  title="Start Year"
                />
                <input
                  type="range" min={sliderMin + 5} max="2025" value={endYear}
                  onChange={(e) => setEndYear(Math.max(Number(e.target.value), startYear + 5))}
                  style={{ width: '100%', accentColor: 'var(--color-accent)', cursor: 'pointer' }}
                  title="End Year"
                />
              </div>
              {isLive && (
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-light)', marginTop: '4px' }}>
                  Sliders change the chart view only. Statistics cover the full {baseData1.yearsUsed}-year record.
                </div>
              )}
            </div>

          </div>
        </div>

        <section className="card" style={{ padding: 'var(--space-5)', marginBottom: 'var(--space-6)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
            <div>
              <span style={{ fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--color-text-light)', fontWeight: 700 }}>
                {currentRegion.name} · {startYear} to {endYear}
              </span>
              <h2 style={{ fontSize: '1.8rem', marginTop: '4px' }}>
                {currentVar1.name} {currentVar2 ? `& ${currentVar2.name}` : 'Over Time'}
              </h2>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
              <span className={`badge ${(isLive ? verdictCode === 'detected' : isSignificant) ? 'badge-significant' : 'badge-unclear'}`}>
                {(isLive ? verdictCode === 'detected' : isSignificant)
                  ? <CheckCircle2 size={13} />
                  : <AlertTriangle size={13} />}
                {' '}{badgeLabel}
              </span>

              <button className="ask-about-pill" onClick={() => onOpenDeepDive(deepDivePayload)}>
                <TinyRobot />
                <span>Explain this chart</span>
              </button>
            </div>
          </div>

          <p style={{ fontSize: '1rem', color: 'var(--color-text-muted)', marginBottom: 'var(--space-4)' }}>
            Source: <strong>{currentVar1.satellite}</strong> ({currentVar1.resolution}). {currentVar1.description}
          </p>

          {isLive && baseData1.fragile && (
            <div className="card" style={{ padding: 'var(--space-3)', marginBottom: 'var(--space-3)' }}>
              <AlertTriangle size={14} /> <strong>Fragile result.</strong>{' '}
              {baseData1.fragileNote || 'This result depends on a few extreme years.'}
            </div>
          )}

          <TrendChart
            series={filteredSeries1}
            series2={filteredSeries2}
            variable1Name={currentVar1.name}
            variable2Name={currentVar2 ? currentVar2.name : ''}
            unit1={currentVar1.unit}
            unit2={currentVar2 ? currentVar2.unit : ''}
            isLoading={isChartLoading}
            height={380}
            caption={chartCaption}
          />

          <StatsCard
            slopePerYear={baseData1.slopePerYear}
            unit={currentVar1.unit}
            verdict={baseData1.verdict}
            pValue={baseData1.pValue}
            ci95={baseData1.ci95}
            yearsUsed={isLive ? baseData1.yearsUsed : yearsInSlice}
            datasetName={currentVar1.satellite}
            onOpenGlossary={openGlossary}
          />

          {isLive && baseData1.summary && (
            <p style={{ marginTop: 'var(--space-3)' }}>{baseData1.summary.plain}</p>
          )}
        </section>

        {baseData1.verdict !== 'significant' && baseData1.gap && (
          <section className="section-gap">
            <DataGapCard
              gap={baseData1.gap}
              title={`What is missing: ${currentVar1.name} in ${currentRegion.name}`}
              onOpenGlossary={openGlossary}
            />
          </section>
        )}

      </div>
    </div>
  );
}