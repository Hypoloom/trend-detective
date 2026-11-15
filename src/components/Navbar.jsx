import React from 'react';
import { BookOpen, AlertCircle, Sun, Moon } from 'lucide-react';

/**
 * Navbar Component
 * Simplified 4-item navigation:
 * Home, Explorer, Data Gaps, Method, plus Theme Toggle (Light / Dark).
 */
export default function Navbar({ activePage, setActivePage, openGlossary, theme = 'light', toggleTheme }) {
  const navItems = [
    { id: 'home', label: 'Home' },
    { id: 'explorer', label: 'Explorer' },
    { id: 'gaps', label: 'Data Gaps' },
    { id: 'method', label: 'Method' },
  ];

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        {/* Brand Logo & NASA Space Apps attribution */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={() => setActivePage('home')}
            style={{ background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left', padding: 0 }}
            className="brand-logo"
            aria-label="Go to Hypoloom home"
          >
            <div className="brand-dot" />
            <span>Hypoloom</span>
            <span className="brand-badge">Trend Detective</span>
          </button>
        </div>

        {/* 4 Main Navigation Links */}
        <nav className="nav-links" aria-label="Main Navigation">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-btn ${activePage === item.id ? 'active' : ''}`}
              onClick={() => setActivePage(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>

        {/* Right side: Sample Data indicator, Theme Toggle & Glossary */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <div className="sample-pill" title="Explorer and Ask use live NASA MERRA-2 reanalysis data. Home and Data Gaps show simulated examples.">
            <AlertCircle size={13} color="var(--color-accent)" />
            <span>Live + simulated</span>
          </div>

          {/* Dark / Light Mode Toggle Button */}
          <button
            className="btn btn-outline btn-sm"
            onClick={toggleTheme}
            style={{
              borderRadius: 'var(--radius-full)',
              padding: '0.4rem 0.65rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem'
            }}
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            aria-label={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {theme === 'dark' ? (
              <>
                <Sun size={15} color="#FBBF24" />
                <span style={{ fontSize: '0.8rem' }}>Light</span>
              </>
            ) : (
              <>
                <Moon size={15} color="#64748B" />
                <span style={{ fontSize: '0.8rem' }}>Dark</span>
              </>
            )}
          </button>

          <button
            className="btn btn-outline btn-sm"
            onClick={openGlossary}
            style={{ borderRadius: 'var(--radius-full)', gap: '0.35rem' }}
            title="Open plain-language glossary of statistical and data terms"
          >
            <BookOpen size={14} />
            <span>Glossary</span>
          </button>
        </div>
      </div>
    </header>
  );
}
