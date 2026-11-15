import React from 'react';
import { BookOpen, Satellite, ShieldCheck, Database } from 'lucide-react';
import { PAGE_SECTIONS } from '../data/mockData';

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
 * MethodPage Component
 * Explains:
 * - Statistical tests in plain language (Mann-Kendall, Sen's slope, p-values)
 * - NASA satellite instruments used
 * - Demo sample data statement & connection roadmap
 */
export default function MethodPage({ openGlossary, onOpenDeepDive }) {
  return (
    <div style={{ paddingTop: 'var(--space-6)', paddingBottom: 'var(--space-8)' }}>
      <div className="container" style={{ maxWidth: '960px' }}>

        {/* HERO SECTION */}
        <section
          id="method-hero"
          data-section="method-tests"
          className="section-gap"
        >
          <div className="eyebrow">NASA SPACE APPS CHALLENGE METHODOLOGY</div>
          <h1>How the Detective Tests for Truth</h1>
          <p style={{ fontSize: '1.2rem', marginTop: 'var(--space-2)', lineHeight: '1.6' }}>
            When someone claims "summers are getting hotter" or "wells are running dry",
            how do scientists test it? Here is the math and the data behind Hypoloom,
            explained in plain language without intimidating jargon.
          </p>
        </section>

        {/* SAMPLE DATA DEMO NOTICE */}
        <div style={{ backgroundColor: 'var(--color-accent-light)', border: '1px solid var(--color-accent-border)', borderRadius: 'var(--radius-lg)', padding: 'var(--space-4)', marginBottom: 'var(--space-8)', display: 'flex', gap: 'var(--space-2)', alignItems: 'flex-start' }}>
          <Database size={24} color="var(--color-accent)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h3 style={{ fontSize: '1.15rem', color: 'var(--color-accent)', marginBottom: '4px' }}>
              Notice: Some pages use live data and some use simulated examples
            </h3>
            <p style={{ fontSize: '0.95rem', color: 'var(--color-text-muted)', margin: 0, lineHeight: '1.6' }}>
              The Explorer and Ask pages use a live backend on cached NASA MERRA-2 reanalysis data (a model product, 1980 to 2025) for four regions: Maharashtra, Rajasthan, Kerala and Gujarat. The other pages (Home, Data Gaps and the glossary) use simulated example data held in <code>src/data/mockData.js</code>; its numbers are not measurements.
              
              
            </p>
          </div>
        </div>

        {/* SECTION 1: THE TWO TESTS */}
        <section className="section-gap">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-3)' }}>
            <h2 style={{ fontSize: '1.75rem', margin: 0 }}>
              1. The Two Tests We Run on Every Record
            </h2>
            <button
              className="ask-about-pill"
              onClick={() => onOpenDeepDive(PAGE_SECTIONS['method-tests'])}
            >
              <TinyRobot />
              <span>Ask about the math</span>
            </button>
          </div>

          <div className="grid-2">
            {/* Mann-Kendall */}
            <div className="card" style={{ padding: 'var(--space-4)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: 'var(--space-2)' }}>
                <span className="badge badge-unclear" style={{ fontSize: '0.78rem' }}>Step 1: Test Reality</span>
                <h3 style={{ fontSize: '1.3rem', margin: 0 }}>The Mann-Kendall Test</h3>
              </div>
              <p style={{ fontSize: '0.95rem', marginBottom: 'var(--space-3)' }}>
                <strong>The question it asks:</strong> "Is this number consistently creeping up or down over decades, or is it just random weather noise?"
              </p>
              <div style={{ backgroundColor: 'var(--color-bg-subtle)', padding: 'var(--space-2)', borderRadius: 'var(--radius-md)', fontSize: '0.9rem', color: 'var(--color-text-main)' }}>
                💡 <strong>Why we use it:</strong> Earth weather is messy. One freak hail storm or heatwave shouldn't trick our algorithm. Mann-Kendall is <em>non-parametric</em>, meaning it doesn't care if a year was extreme—it only counts whether years generally climb higher over time.
              </div>
            </div>

            {/* Sen's Slope */}
            <div className="card" style={{ padding: 'var(--space-4)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: 'var(--space-2)' }}>
                <span className="badge badge-significant" style={{ fontSize: '0.78rem' }}>Step 2: Speedometer</span>
                <h3 style={{ fontSize: '1.3rem', margin: 0 }}>Sen's Slope Estimator</h3>
              </div>
              <p style={{ fontSize: '0.95rem', marginBottom: 'var(--space-3)' }}>
                <strong>The question it asks:</strong> "Exactly how many degrees Celsius or millimeters of water are we gaining or losing each year?"
              </p>
              <div style={{ backgroundColor: 'var(--color-bg-subtle)', padding: 'var(--space-2)', borderRadius: 'var(--radius-md)', fontSize: '0.9rem', color: 'var(--color-text-main)' }}>
                💡 <strong>Why we use it:</strong> Ordinary regression lines can be tilted wildly by a single super-drought year. Sen's slope calculates the trajectory between every single pair of years and takes the <em>median</em>. It is virtually immune to outliers.
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 2: THE 3 OUTPUT BADGES */}
        <section className="section-gap">
          <h2 style={{ fontSize: '1.75rem', marginBottom: 'var(--space-3)' }}>
            2. The 3 Output Badges Explained
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
            <div className="card" style={{ padding: 'var(--space-3)', display: 'flex', alignItems: 'flex-start', gap: 'var(--space-2)' }}>
              <span className="badge badge-significant" style={{ fontSize: '0.85rem', flexShrink: 0, marginTop: '2px' }}>
                Significant
              </span>
              <div>
                <strong style={{ fontSize: '1rem', color: 'var(--color-text-main)' }}>A trend was detected (p &lt; 0.05).</strong>
                <p style={{ fontSize: '0.92rem', color: 'var(--color-text-muted)', margin: '4px 0 0' }}>
                  If nothing were changing, a pattern this strong would show up less than 5% of the time. Treat it as a candidate trend and check it against other sources before relying on it.
                </p>
              </div>
            </div>

            <div className="card" style={{ padding: 'var(--space-3)', display: 'flex', alignItems: 'flex-start', gap: 'var(--space-2)' }}>
              <span className="badge badge-unclear" style={{ fontSize: '0.85rem', flexShrink: 0, marginTop: '2px' }}>
                Not significant yet
              </span>
              <div>
                <strong style={{ fontSize: '1rem', color: 'var(--color-text-main)' }}>Weather swings are larger than the change (p ≥ 0.05).</strong>
                <p style={{ fontSize: '0.92rem', color: 'var(--color-text-muted)', margin: '4px 0 0' }}>
                  Weather swings are larger than the change (p ≥ 0.05). This does NOT mean the climate is motionless. The record may be too short or too noisy to show a change, or there may be no real change. The Explorer's 'Why this result' box says which.
                </p>
              </div>
            </div>

            <div className="card" style={{ padding: 'var(--space-3)', display: 'flex', alignItems: 'flex-start', gap: 'var(--space-2)' }}>
              <span className="badge badge-nodata" style={{ fontSize: '0.85rem', flexShrink: 0, marginTop: '2px' }}>
                Not enough data
              </span>
              <div>
                <strong style={{ fontSize: '1rem', color: 'var(--color-text-main)' }}>The record is too short or too coarse.</strong>
                <p style={{ fontSize: '0.92rem', color: 'var(--color-text-muted)', margin: '4px 0 0' }}>
                  If a region would need many more years to overcome natural swings, we honestly flag the record as incomplete.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* SECTION 3: NASA SATELLITE FLEET */}
        <section className="section-gap">
          <h2 style={{ fontSize: '1.75rem', marginBottom: 'var(--space-3)' }}>
            3. The Data Behind This Site
          </h2>

          <div className="card" style={{ padding: 'var(--space-4)' }}>
            <ul style={{ listStyle: 'none', paddingLeft: 0, display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <li style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'flex-start' }}>
                <Database size={20} color="var(--color-accent)" style={{ flexShrink: 0, marginTop: '3px' }} />
                <div>
                  <strong style={{ fontSize: '1.05rem' }}>NASA MERRA-2 (used by the live Explorer and Ask pages)</strong>
                  <p style={{ fontSize: '0.92rem', color: 'var(--color-text-muted)', margin: '4px 0 0' }}>
                    A reanalysis: a computer model of the atmosphere combined with many observations. It is a model product, not a direct satellite measurement. We use cached monthly values for 1980 to 2025 for four regions.
                  </p>
                </div>
              </li>

              <li style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'flex-start', borderTop: '1px solid var(--color-border)', paddingTop: 'var(--space-3)' }}>
                <Satellite size={20} color="var(--color-accent)" style={{ flexShrink: 0, marginTop: '3px' }} />
                <div>
                  <strong style={{ fontSize: '1.05rem' }}>Simulated examples only: NASA MODIS (Terra & Aqua Satellites)</strong>
                  <p style={{ fontSize: '0.92rem', color: 'var(--color-text-muted)', margin: '4px 0 0' }}>
                    Measures infrared radiation emitted by land to calculate Land Surface Temperature (LST), and measures reflected red/near-infrared light to compute vegetation greenness (NDVI). Orbiting Earth since 1999/2002.
                  </p>
                </div>
              </li>

              <li style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'flex-start', borderTop: '1px solid var(--color-border)', paddingTop: 'var(--space-3)' }}>
                <Satellite size={20} color="#2563EB" style={{ flexShrink: 0, marginTop: '3px' }} />
                <div>
                  <strong style={{ fontSize: '1.05rem' }}>Simulated examples only: NASA GPM IMERG (Global Precipitation Measurement)</strong>
                  <p style={{ fontSize: '0.92rem', color: 'var(--color-text-muted)', margin: '4px 0 0' }}>
                    An international satellite constellation using spaceborne dual-frequency radar and microwave imagers to map global rain and snowfall every 30 minutes.
                  </p>
                </div>
              </li>

              <li style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'flex-start', borderTop: '1px solid var(--color-border)', paddingTop: 'var(--space-3)' }}>
                <Satellite size={20} color="#0891B2" style={{ flexShrink: 0, marginTop: '3px' }} />
                <div>
                  <strong style={{ fontSize: '1.05rem' }}>Simulated examples only: NASA/GFZ GRACE & GRACE-FO (Gravity Recovery and Climate Experiment)</strong>
                  <p style={{ fontSize: '0.92rem', color: 'var(--color-text-muted)', margin: '4px 0 0' }}>
                    Twin satellites chasing each other 220 km apart. When the lead satellite passes over heavy underground water, Earth's gravity pulls it forward. By measuring changes in the distance between the two satellites down to a micron, NASA weighs water stored deep in aquifers.
                  </p>
                </div>
              </li>
            </ul>
          </div>
        </section>

        {/* SECTION 4: HONESTY PLEDGE */}
        <section className="card" style={{ padding: 'var(--space-5)', backgroundColor: 'var(--color-bg-subtle)', border: '1px solid var(--color-border)', textAlign: 'center' }}>
          <ShieldCheck size={36} color="var(--color-accent)" style={{ margin: '0 auto var(--space-2)' }} />
          <h2 style={{ fontSize: '1.45rem', marginBottom: 'var(--space-1)' }}>The Trend Detective Honesty Pledge</h2>
          <p style={{ fontSize: '0.95rem', color: 'var(--color-text-muted)', maxWidth: '640px', margin: '0 auto var(--space-3)', lineHeight: '1.6' }}>
            We pledge to never hallucinate causes, exaggerate confidence, or turn an inconclusive result into a sensational headline.
            If the record is too short or noisy to know for sure, we will say so clearly, show the progress bar, and tell you what data would settle the question.
          </p>
          <button className="btn btn-primary btn-sm" onClick={() => openGlossary && openGlossary()}>
            <BookOpen size={14} />
            <span>Open Terms Glossary</span>
          </button>
        </section>

      </div>
    </div>
  );
}
