import React, { useState, useMemo, useEffect } from 'react';
import { Sliders, HelpCircle, Layers, Calendar, Info, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';
import TrendChart from '../components/TrendChart';
import StatsCard from '../components/StatsCard';
import DataGapCard from '../components/DataGapCard';
import { REGIONS, VARIABLES, getSeries } from '../data/mockData';

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
 * ExplorerPage Component
 * Full-width, uncrowded layout:
 * - Top controls for Region & Variables (1 or 2) & Year Range
 * - Full-width Recharts visualization with Sen's slope
 * - Clean Stats card with "Show details" toggle
 * - Dynamic AI Robot Assistant integration: updates robot context on every change,
 *   replacing the old crowded side panel!
 */
export default function ExplorerPage({ openGlossary, onUpdateRobotContext, onOpenDeepDive }) {
  const [selectedRegionId, setSelectedRegionId] = useState('rajasthan');
  const [selectedVar1Id, setSelectedVar1Id] = useState('summer_temp');
  const [selectedVar2Id, setSelectedVar2Id] = useState('');
  const [startYear, setStartYear] = useState(1990);
  const [endYear, setEndYear] = useState(2025);
  const [isChartLoading, setIsChartLoading] = useState(false);

  // Retrieve metadata
  const currentRegion = useMemo(() => {
    return REGIONS.find((r) => r.id === selectedRegionId) || REGIONS[0];
  }, [selectedRegionId]);

  const currentVar1 = useMemo(() => {
    return VARIABLES.find((v) => v.id === selectedVar1Id) || VARIABLES[0];
  }, [selectedVar1Id]);

  const currentVar2 = useMemo(() => {
    if (!selectedVar2Id) return null;
    return VARIABLES.find((v) => v.id === selectedVar2Id) || null;
  }, [selectedVar2Id]);

  // Series data
  const baseData1 = useMemo(() => {
    return getSeries(selectedRegionId, selectedVar1Id);
  }, [selectedRegionId, selectedVar1Id]);

  const baseData2 = useMemo(() => {
    if (!selectedVar2Id) return null;
    return getSeries(selectedRegionId, selectedVar2Id);
  }, [selectedRegionId, selectedVar2Id]);

  // Filter series to selected year slice
  const filteredSeries1 = useMemo(() => {
    if (!baseData1.series) return [];
    return baseData1.series.filter((pt) => pt.year >= startYear && pt.year <= endYear);
  }, [baseData1, startYear, endYear]);

  const filteredSeries2 = useMemo(() => {
    if (!baseData2 || !baseData2.series) return null;
    return baseData2.series.filter((pt) => pt.year >= startYear && pt.year <= endYear);
  }, [baseData2, startYear, endYear]);

  const yearsInSlice = endYear - startYear + 1;

  // DYNAMIC ROBOT INTEGRATION:
  // When dropdown selections change, tell the Robot Assistant so its speech bubble updates!
  useEffect(() => {
    if (onUpdateRobotContext) {
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
    setIsChartLoading(true);
    setSelectedRegionId(newRegion);
    setTimeout(() => setIsChartLoading(false), 200);
  };

  const handleVar1Change = (newVar) => {
    setIsChartLoading(true);
    setSelectedVar1Id(newVar);
    if (selectedVar2Id === newVar) setSelectedVar2Id('');
    setTimeout(() => setIsChartLoading(false), 200);
  };

  return (
    <div style={{ paddingTop: 'var(--space-6)', paddingBottom: 'var(--space-8)' }}>
      <div className="container">

        {/* HEADER */}
        <section className="section-gap" style={{ marginBottom: 'var(--space-4)' }}>
          <div className="eyebrow">INTERACTIVE SCIENTIFIC WORKBENCH</div>
          <h1>Earth System Data Explorer</h1>
          <p style={{ fontSize: '1.2rem', maxWidth: '75ch' }}>
            Compare NASA satellite observations across regions and time periods. Measure the speed of change and see if it stands out from natural noise.
          </p>
        </section>

        {/* TOP CONTROLS BAR (Full Width) */}
        <div className="card" style={{ padding: 'var(--space-4)', marginBottom: 'var(--space-4)', backgroundColor: 'var(--color-bg-subtle)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'var(--space-3)', alignItems: 'flex-end' }}>

            {/* Region */}
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--color-text-light)', textTransform: 'uppercase', marginBottom: '6px' }}>
                1. Select Region
              </label>
              <select
                className="select-control"
                style={{ width: '100%', padding: '0.65rem 0.9rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-dark)', fontSize: '0.95rem', backgroundColor: 'var(--color-bg-card)', color: 'var(--color-text-main)' }}
                value={selectedRegionId}
                onChange={(e) => handleRegionChange(e.target.value)}
              >
                {REGIONS.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Primary Variable */}
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--color-text-light)', textTransform: 'uppercase', marginBottom: '6px' }}>
                2. Primary Variable
              </label>
              <select
                className="select-control"
                style={{ width: '100%', padding: '0.65rem 0.9rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-dark)', fontSize: '0.95rem', backgroundColor: 'var(--color-bg-card)', color: 'var(--color-text-main)' }}
                value={selectedVar1Id}
                onChange={(e) => handleVar1Change(e.target.value)}
              >
                {VARIABLES.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name} ({v.unit})
                  </option>
                ))}
              </select>
            </div>

            {/* Secondary Variable */}
            <div>
              <label style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 700, color: 'var(--color-text-light)', textTransform: 'uppercase', marginBottom: '6px' }}>
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
              <select
                className="select-control"
                style={{ width: '100%', padding: '0.65rem 0.9rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-dark)', fontSize: '0.95rem', backgroundColor: 'var(--color-bg-card)', color: 'var(--color-text-main)' }}
                value={selectedVar2Id}
                onChange={(e) => setSelectedVar2Id(e.target.value)}
              >
                <option value="">-- None (Single Variable) --</option>
                {VARIABLES.filter((v) => v.id !== selectedVar1Id).map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name} ({v.unit})
                  </option>
                ))}
              </select>
            </div>

            {/* Year Range Slider */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--color-text-light)', textTransform: 'uppercase' }}>
                  Years: {startYear} – {endYear}
                </span>
                <span style={{ fontSize: '0.8rem', color: 'var(--color-accent)', fontWeight: 600 }}>
                  ({yearsInSlice} years)
                </span>
              </div>
              <div style={{ display: 'flex', gap: 'var(--space-1)', alignItems: 'center' }}>
                <input
                  type="range"
                  min="1990"
                  max="2015"
                  value={startYear}
                  onChange={(e) => setStartYear(Math.min(Number(e.target.value), endYear - 5))}
                  style={{ width: '100%', accentColor: 'var(--color-accent)', cursor: 'pointer' }}
                  title="Start Year"
                />
                <input
                  type="range"
                  min="2000"
                  max="2025"
                  value={endYear}
                  onChange={(e) => setEndYear(Math.max(Number(e.target.value), startYear + 5))}
                  style={{ width: '100%', accentColor: 'var(--color-accent)', cursor: 'pointer' }}
                  title="End Year"
                />
              </div>
            </div>

          </div>
        </div>

        {/* FULL WIDTH VISUALIZATION CARD */}
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
              <span className={`badge ${baseData1.verdict === 'significant' ? 'badge-significant' : 'badge-unclear'}`}>
                {baseData1.verdict === 'significant' ? (
                  <><CheckCircle2 size={13} /> Significant Trend</>
                ) : (
                  <><AlertTriangle size={13} /> Inconclusive Trend</>
                )}
              </span>

              <button
                className="ask-about-pill"
                onClick={() => onOpenDeepDive({
                  id: `explorer-${selectedRegionId}-${selectedVar1Id}`,
                  title: `${currentVar1.name} in ${currentRegion.name}`,
                  summary: baseData1.summary.plain,
                  deepDive: baseData1.summary,
                  suggestedQuestions: [
                    `Why is ${currentVar1.name} changing in ${currentRegion.name}?`,
                    `Is this trend statistically significant?`,
                    `How should I read the orange trend line?`
                  ]
                })}
              >
                <TinyRobot />
                <span>Explain this chart</span>
              </button>
            </div>
          </div>

          <p style={{ fontSize: '1rem', color: 'var(--color-text-muted)', marginBottom: 'var(--space-4)' }}>
            Satellite Sensor: <strong>{currentVar1.satellite}</strong> ({currentVar1.resolution}). {currentVar1.description}
          </p>

          <TrendChart
            series={filteredSeries1}
            series2={filteredSeries2}
            variable1Name={currentVar1.name}
            variable2Name={currentVar2 ? currentVar2.name : ""}
            unit1={currentVar1.unit}
            unit2={currentVar2 ? currentVar2.unit : ""}
            isLoading={isChartLoading}
            height={380}
            caption={
              currentVar2
                ? `Black line: ${currentVar1.name} (${currentVar1.unit}, left axis). Blue line: ${currentVar2.name} (${currentVar2.unit}, right axis). Orange dashed: trend line.`
                : `Black dots: annual satellite observations. Orange dashed: Sen's slope trendline (+${baseData1.slopePerYear} ${currentVar1.unit}/year).`
            }
          />

          {/* Stats row with "Show details" progressive disclosure */}
          <StatsCard
            slopePerYear={baseData1.slopePerYear}
            unit={currentVar1.unit}
            verdict={baseData1.verdict}
            pValue={baseData1.pValue}
            ci95={baseData1.ci95}
            yearsUsed={yearsInSlice}
            datasetName={currentVar1.satellite}
            onOpenGlossary={openGlossary}
          />
        </section>

        {/* If inconclusive, show Data Gap Card */}
        {baseData1.verdict !== 'significant' && (
          <section className="section-gap">
            <DataGapCard
              gap={baseData1.gap}
              title={`Data Gap Alert: ${currentVar1.name} in ${currentRegion.name}`}
              onOpenGlossary={openGlossary}
            />
          </section>
        )}

      </div>
    </div>
  );
}
