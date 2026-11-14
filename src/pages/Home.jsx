import React from 'react';
import { ArrowRight, Sparkles, Sliders, CheckCircle2, Clock, Eye, HelpCircle } from 'lucide-react';
import TrendChart from '../components/TrendChart';
import StatsCard from '../components/StatsCard';
import { SERIES_DATABASE, PAGE_SECTIONS } from '../data/mockData';

/**
 * Robot Icon for "Ask about this" buttons
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
 * Home Page Component
 * Redesigned for the new layout guidelines:
 * - Full-width, uncrowded layout with generous 8px spacing scale (80px section gaps)
 * - No chatbot box sitting permanently on the page
 * - Clear visual order: big heading, one sentence, one chart or card, one button
 * - Progressive disclosure: stats details sit behind "Show details"
 * - Per-section "Ask about this" buttons that trigger the AI Robot's Deep Dive
 */
export default function Home({ setActivePage, openGlossary, onOpenDeepDive }) {
  // Featured sample dataset (Rajasthan Summer Temperature)
  const featured = SERIES_DATABASE["rajasthan_summer_temp"];

  return (
    <div style={{ paddingTop: 'var(--space-6)', paddingBottom: 'var(--space-8)' }}>
      <div className="container">

        {/* SECTION 1: HERO (Big heading, one sentence, two buttons) */}
        <section
          id="hero-headline"
          data-section="hero-headline"
          className="section-gap"
          style={{ maxWidth: '850px' }}
        >
          <div className="eyebrow">NASA SATELLITE DATA · 1990 TO 2025</div>
          <h1>
            Is your part of the world getting hotter?
          </h1>
          <p style={{ fontSize: '1.25rem', marginBottom: 'var(--space-4)', lineHeight: '1.6' }}>
            We read decades of NASA satellite records, measure the change, and tell you
            how sure we are, in words anyone can follow.
          </p>

          <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
            <button
              className="btn btn-primary"
              onClick={() => setActivePage('explorer')}
            >
              <span>Explore the data</span>
              <ArrowRight size={16} />
            </button>
            <button
              className="btn btn-outline"
              onClick={() => onOpenDeepDive(PAGE_SECTIONS['hero-headline'])}
            >
              <TinyRobot />
              <span>Ask the Robot Detective</span>
            </button>
          </div>
        </section>

        {/* SECTION 2: FIGURE 1 SAMPLE CASE (Full width, clear visual order) */}
        <section
          id="figure-1-rajasthan"
          data-section="figure-1-rajasthan"
          className="section-gap"
        >
          <div className="card" style={{ padding: 'var(--space-5)' }}>
            {/* Header row with "Ask about this" button */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
              <div>
                <span style={{ fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--color-text-light)' }}>
                  FIGURE 1 · SAMPLE CASE
                </span>
                <h2 style={{ fontSize: '1.8rem', marginTop: '4px' }}>
                  Average summer temperature, Rajasthan, 1990 to 2025
                </h2>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                <span className="badge badge-significant" style={{ fontSize: '0.8rem' }}>
                  <CheckCircle2 size={13} /> Statistically Significant
                </span>
                <button
                  className="ask-about-pill"
                  onClick={() => onOpenDeepDive(PAGE_SECTIONS['figure-1-rajasthan'])}
                  title="Ask the AI Robot about this chart"
                >
                  <TinyRobot />
                  <span>Ask about this chart</span>
                </button>
              </div>
            </div>

            {/* One sentence explanation */}
            <p style={{ fontSize: '1.05rem', color: 'var(--color-text-muted)', marginBottom: 'var(--space-4)' }}>
              May–July daytime surface temperatures captured by NASA MODIS satellites show summers are warming steadily by +0.06 °C per year.
            </p>

            {/* Full Width Trend Chart */}
            <TrendChart
              series={featured.series}
              variable1Name="Summer Average"
              unit1="°C"
              height={360}
              caption="The black line is each summer's average. The orange line is the trend: about +0.06 °C per year. Sample data shown."
            />

            {/* Stats row with "Show details" toggle */}
            <StatsCard
              slopePerYear={featured.slopePerYear}
              unit="°C"
              verdict={featured.verdict}
              pValue={featured.pValue}
              ci95={featured.ci95}
              yearsUsed={featured.yearsUsed}
              datasetName="NASA MODIS Land Surface Temp"
              onOpenGlossary={openGlossary}
            />
          </div>
        </section>

        {/* SECTION 3: HOW IT WORKS (3 Cards in a row, generous whitespace) */}
        <section
          id="how-it-works"
          data-section="how-it-works"
          className="section-gap"
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 'var(--space-2)', marginBottom: 'var(--space-4)' }}>
            <div>
              <div className="eyebrow">3-STEP SCIENTIFIC PIPELINE</div>
              <h2>How the Detective Works</h2>
              <p style={{ fontSize: '1.1rem' }}>
                We turn complex satellite sensor data into honest, accessible answers in three steps.
              </p>
            </div>
            <button
              className="ask-about-pill"
              onClick={() => onOpenDeepDive(PAGE_SECTIONS['how-it-works'])}
            >
              <TinyRobot />
              <span>Ask about the method</span>
            </button>
          </div>

          <div className="grid-3">
            {/* Step 1: Pick */}
            <div className="card" style={{ padding: 'var(--space-4)' }}>
              <div style={{ width: 44, height: 44, borderRadius: '50%', backgroundColor: 'var(--color-accent-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--space-3)', color: 'var(--color-accent)' }}>
                <Sliders size={22} />
              </div>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--color-accent)', textTransform: 'uppercase', marginBottom: '4px' }}>
                Step 1
              </div>
              <h3 style={{ fontSize: '1.3rem' }}>Pick a Region & Metric</h3>
              <p style={{ fontSize: '0.95rem' }}>
                Choose any region on Earth and a key satellite indicator—temperature, rainfall, groundwater, or plant greenness.
              </p>
            </div>

            {/* Step 2: Measure */}
            <div className="card" style={{ padding: 'var(--space-4)' }}>
              <div style={{ width: 44, height: 44, borderRadius: '50%', backgroundColor: '#EFF6FF', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--space-3)', color: '#2563EB' }}>
                <Clock size={22} />
              </div>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#2563EB', textTransform: 'uppercase', marginBottom: '4px' }}>
                Step 2
              </div>
              <h3 style={{ fontSize: '1.3rem' }}>Measure 35+ Years</h3>
              <p style={{ fontSize: '0.95rem' }}>
                We assemble unbroken time series (1990–2025) and calculate Sen's slope to find the rate of change without being fooled by outlier seasons.
              </p>
            </div>

            {/* Step 3: Understand */}
            <div className="card" style={{ padding: 'var(--space-4)' }}>
              <div style={{ width: 44, height: 44, borderRadius: '50%', backgroundColor: '#F0FDF4', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--space-3)', color: '#16A34A' }}>
                <Eye size={22} />
              </div>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#16A34A', textTransform: 'uppercase', marginBottom: '4px' }}>
                Step 3
              </div>
              <h3 style={{ fontSize: '1.3rem' }}>Separate Signal From Noise</h3>
              <p style={{ fontSize: '0.95rem' }}>
                Using the Mann-Kendall test, we determine if the change is genuinely real or just random year-to-year weather swings.
              </p>
            </div>
          </div>
        </section>

        {/* SECTION 4: DATA GAPS TEASER (Max 3 cards, one button) */}
        <section
          id="data-gaps-teaser"
          data-section="data-gaps-teaser"
          className="section-gap"
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 'var(--space-2)', marginBottom: 'var(--space-4)' }}>
            <div>
              <div className="eyebrow">WHAT MAKES US DIFFERENT</div>
              <h2>When a trend is not clear, we tell you what is missing.</h2>
              <p style={{ fontSize: '1.1rem' }}>
                Most tools stop at "not significant". We go one step further and estimate how much more data would settle the question.
              </p>
            </div>
            <button
              className="ask-about-pill"
              onClick={() => onOpenDeepDive(PAGE_SECTIONS['data-gaps-teaser'])}
            >
              <TinyRobot />
              <span>Ask about data gaps</span>
            </button>
          </div>

          <div className="grid-3" style={{ marginBottom: 'var(--space-4)' }}>
            {/* Box 1 */}
            <div className="card" style={{ padding: 'var(--space-4)' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--color-text-light)', fontWeight: 600 }}>
                Rainfall, Jaipur
              </span>
              <h3 style={{ fontSize: '1.5rem', marginTop: '6px', color: 'var(--status-unclear-text)' }}>
                Not yet clear
              </h3>
              <p style={{ fontSize: '0.95rem' }}>
                Year-to-year swings hide the trend. Natural monsoon variability is wider than the subtle drift.
              </p>
            </div>

            {/* Box 2 */}
            <div className="card" style={{ padding: 'var(--space-4)', backgroundColor: '#F0F9FF', borderColor: '#BAE6FD' }}>
              <span style={{ fontSize: '0.85rem', color: '#0369A1', fontWeight: 600 }}>
                Data we would need
              </span>
              <h3 style={{ fontSize: '1.5rem', marginTop: '6px', color: '#0369A1' }}>
                About 14 more years
              </h3>
              <p style={{ fontSize: '0.95rem' }}>
                Sample statistical estimate calculated from our power-analysis method.
              </p>
            </div>

            {/* Box 3 */}
            <div className="card" style={{ padding: 'var(--space-4)' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--color-text-light)', fontWeight: 600 }}>
                Or a finer view
              </span>
              <h3 style={{ fontSize: '1.5rem', marginTop: '6px' }}>
                Daily, not monthly
              </h3>
              <p style={{ fontSize: '0.95rem' }}>
                Finer daily radar readings instead of monthly aggregates can reveal the pattern years sooner.
              </p>
            </div>
          </div>

          <div>
            <button
              className="btn btn-outline"
              onClick={() => setActivePage('gaps')}
            >
              <span>Explore all data gaps</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </section>

      </div>
    </div>
  );
}
