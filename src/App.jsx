import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import GlossaryModal from './components/GlossaryModal';
import FloatingRobot from './components/FloatingRobot';
import ChatPanel from './components/ChatPanel';

// Pages (4 main views)
import Home from './pages/Home';
import ExplorerPage from './pages/ExplorerPage';
import DataGapsPage from './pages/DataGapsPage';
import MethodPage from './pages/MethodPage';

import { PAGE_SECTIONS } from './data/mockData';

/**
 * App Root Component
 * Architecture:
 * - Reflowing Layout: Page content takes 100% width normally. When Chat is open,
 *   content smoothly shifts into the LEFT 50%, while ChatPanel occupies the RIGHT 50%.
 * - Floating Draggable Robot Assistant present on EVERY page.
 * - Intersection Observer tracks which section is in view to inform the Robot.
 * - Dark & Light Mode Theme Support with localStorage persistence.
 */
export default function App() {
  const [activePage, setActivePage] = useState('home'); // 'home' | 'explorer' | 'gaps' | 'method'
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [activeSection, setActiveSection] = useState(PAGE_SECTIONS['hero-headline']);
  const [deepDiveData, setDeepDiveData] = useState(null);

  // Theme state: defaults to light theme, persists in localStorage
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem('hypoloom_theme') || 'light';
    } catch (e) {
      return 'light';
    }
  });

  // Apply theme to document element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem('hypoloom_theme', theme);
    } catch (e) {}
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  // Glossary modal state
  const [isGlossaryOpen, setIsGlossaryOpen] = useState(false);
  const [selectedGlossaryTerm, setSelectedGlossaryTerm] = useState(null);

  // Scroll to top on page change
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Set default section for the new page
    if (activePage === 'home') {
      setActiveSection(PAGE_SECTIONS['hero-headline']);
    } else if (activePage === 'explorer') {
      setActiveSection(PAGE_SECTIONS['explorer-workbench']);
    } else if (activePage === 'gaps') {
      setActiveSection(PAGE_SECTIONS['data-gaps-matrix']);
    } else if (activePage === 'method') {
      setActiveSection(PAGE_SECTIONS['method-tests']);
    }
  }, [activePage]);

  // Track sections on scroll using IntersectionObserver
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const sectionId = entry.target.getAttribute('data-section');
            if (sectionId && PAGE_SECTIONS[sectionId]) {
              setActiveSection(PAGE_SECTIONS[sectionId]);
            }
          }
        });
      },
      { threshold: 0.35 }
    );

    const sectionElements = document.querySelectorAll('[data-section]');
    sectionElements.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, [activePage]);

  // Open Chat with a specific Deep Dive topic
  const handleOpenDeepDive = (sectionData) => {
    setActiveSection(sectionData);
    setDeepDiveData(sectionData);
    setIsChatOpen(true);
  };

  // Toggle general chat
  const handleToggleChat = () => {
    setIsChatOpen((prev) => !prev);
  };

  // Glossary helpers
  const handleOpenGlossary = (termKey = null) => {
    setSelectedGlossaryTerm(termKey);
    setIsGlossaryOpen(true);
  };

  const handleCloseGlossary = () => {
    setIsGlossaryOpen(false);
    setSelectedGlossaryTerm(null);
  };

  return (
    <div className={`app-layout ${isChatOpen ? 'chat-open' : ''}`}>
      {/* LEFT / MAIN WORKSPACE (Reflows to 50% when chat is open) */}
      <div className="page-workspace">
        {/* Navigation Bar (4 items + Dark Mode Toggle + Glossary) */}
        <Navbar
          activePage={activePage}
          setActivePage={setActivePage}
          openGlossary={() => handleOpenGlossary()}
          theme={theme}
          toggleTheme={toggleTheme}
        />

        {/* Page Content */}
        <main className="main-content">
          {activePage === 'home' && (
            <Home
              setActivePage={setActivePage}
              openGlossary={handleOpenGlossary}
              onOpenDeepDive={handleOpenDeepDive}
            />
          )}

          {activePage === 'explorer' && (
            <ExplorerPage
              openGlossary={handleOpenGlossary}
              onUpdateRobotContext={(section) => setActiveSection(section)}
              onOpenDeepDive={handleOpenDeepDive}
            />
          )}

          {activePage === 'gaps' && (
            <DataGapsPage
              openGlossary={handleOpenGlossary}
              onOpenDeepDive={handleOpenDeepDive}
            />
          )}

          {activePage === 'method' && (
            <MethodPage
              openGlossary={handleOpenGlossary}
              onOpenDeepDive={handleOpenDeepDive}
            />
          )}
        </main>

        {/* Footer */}
        <Footer
          setActivePage={setActivePage}
          openGlossary={() => handleOpenGlossary()}
        />
      </div>

      {/* FLOATING DRAGGABLE AI ROBOT ASSISTANT (Present on every page) */}
      <FloatingRobot
        activeSection={activeSection}
        onOpenChat={handleToggleChat}
        onOpenDeepDive={handleOpenDeepDive}
      />

      {/* HALF-SCREEN CHAT PANEL (Right 50% on Desktop, Fullscreen on Mobile) */}
      <ChatPanel
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        currentSection={activeSection}
        initialDeepDive={deepDiveData}
      />

      {/* Glossary Modal */}
      <GlossaryModal
        isOpen={isGlossaryOpen}
        onClose={handleCloseGlossary}
        selectedTermKey={selectedGlossaryTerm}
      />
    </div>
  );
}
