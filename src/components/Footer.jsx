import React from 'react';
import { ExternalLink, ShieldCheck } from 'lucide-react';

/**
 * Footer Component
 * Includes project attribution for NASA Space Apps Challenge,
 * honesty pledge, and dataset credit links.
 */
export default function Footer({ setActivePage, openGlossary }) {
  return (
    <footer className="footer">
      <div className="container">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '2.5rem', marginBottom: '2.5rem' }}>
          {/* Column 1: Brand & Space Apps */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.75rem' }}>
              <div className="brand-dot" />
              <strong style={{ fontSize: '1.1rem' }}>Hypoloom · Trend Detective</strong>
            </div>
            <p style={{ fontSize: '0.9rem', marginBottom: '1rem', color: 'var(--color-text-muted)' }}>
              Built for the NASA Space Apps Challenge <em>"Be An Earth System Trend Detective"</em>.
              We take decades of satellite observations, measure the trajectory, and honestly state how sure we are in words anyone can understand.
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--color-text-light)' }}>
              <ShieldCheck size={16} color="var(--color-accent)" />
              <span><strong>Honesty Rule:</strong> We never invent causes or statistics not present in the data.</span>
            </div>
          </div>

          {/* Column 2: Navigation */}
          <div>
            <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-light)', marginBottom: '1rem' }}>
              Sections
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.9rem' }}>
              <li>
                <button onClick={() => setActivePage('home')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', padding: 0 }}>
                  Home & Overview
                </button>
              </li>
              <li>
                <button onClick={() => setActivePage('ask')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', padding: 0 }}>
                  Ask the Detective (Chat)
                </button>
              </li>
              <li>
                <button onClick={() => setActivePage('explorer')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', padding: 0 }}>
                  Manual Data Explorer
                </button>
              </li>
              <li>
                <button onClick={() => setActivePage('gaps')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', padding: 0 }}>
                  Data Gaps & What is Missing
                </button>
              </li>
              <li>
                <button onClick={() => setActivePage('method')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', padding: 0 }}>
                  NASA Methodology & About
                </button>
              </li>
            </ul>
          </div>

          {/* Column 3: Satellite Data Sources */}
          <div>
            <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-light)', marginBottom: '1rem' }}>
              NASA Earth Data Sources
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
              <li style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <ExternalLink size={12} />
                <span>NASA MODIS (Terra & Aqua Land Surface Temp & NDVI)</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <ExternalLink size={12} />
                <span>NASA GPM IMERG (Global Precipitation Measurement)</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <ExternalLink size={12} />
                <span>NASA/GFZ GRACE & GRACE-FO (Groundwater Storage)</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <ExternalLink size={12} />
                <span>NASA Aura OMI & Sentinel-5P (Atmospheric NO₂)</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom copyright & disclaimer */}
        <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', fontSize: '0.8rem', color: 'var(--color-text-light)' }}>
          <div>
            © {new Date().getFullYear()} Hypoloom Team · NASA Space Apps Challenge.
          </div>
          <div style={{ display: 'flex', gap: '1.5rem' }}>
            <span style={{ cursor: 'pointer', textDecoration: 'underline' }} onClick={openGlossary}>
              Scientific Terms Glossary
            </span>
            <span>All numbers on this demonstration site are sample data.</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
