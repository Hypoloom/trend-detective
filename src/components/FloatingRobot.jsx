import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, ArrowRight, RotateCcw, X, MessageSquare, HelpCircle } from 'lucide-react';

/**
 * Friendly Custom SVG Robot Illustration
 * Not an emoji: professional, friendly, scientific icon.
 */
function RobotSvg({ isWaving = false }) {
  return (
    <svg
      width="52"
      height="52"
      viewBox="0 0 36 36"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      {/* Antenna with beacon glow */}
      <line x1="18" y1="2" x2="18" y2="7" stroke="#C85A32" strokeWidth="2.5" strokeLinecap="round" />
      <circle cx="18" cy="2" r="3" fill="#FF5722" />
      <circle cx="18" cy="2" r="1.3" fill="#FFE0B2" />

      {/* Head / Body */}
      <rect x="5" y="7" width="26" height="22" rx="7" fill="#FFFFFF" stroke="#0F172A" strokeWidth="2" />

      {/* Visor Screen */}
      <rect x="8" y="10" width="20" height="9" rx="4" fill="#0A0F1D" />

      {/* Glowing Friendly Eyes with specular catchlight */}
      <circle cx="13" cy="14.5" r="2.3" fill="#38BDF8" />
      <circle cx="13.8" cy="13.7" r="0.8" fill="#FFFFFF" />
      <circle cx="23" cy="14.5" r="2.3" fill="#38BDF8" />
      <circle cx="23.8" cy="13.7" r="0.8" fill="#FFFFFF" />

      {/* Cute Smile / Signal waveform */}
      <path d="M14 24.5C15.2 26 20.8 26 22 24.5" stroke="#0F172A" strokeWidth="2" strokeLinecap="round" />

      {/* Left Ear / Audio Sensor */}
      <rect x="2" y="14" width="3" height="7" rx="1.5" fill="#C85A32" />
      {/* Right Ear */}
      <rect x="31" y="14" width="3" height="7" rx="1.5" fill="#C85A32" />

      {/* Chest Signal Lights */}
      <circle cx="12" cy="21.5" r="1.3" fill="#22C55E" />
      <circle cx="18" cy="21.5" r="1.3" fill="#C85A32" />
      <circle cx="24" cy="21.5" r="1.3" fill="#EAB308" />
    </svg>
  );
}

/**
 * FloatingRobot Component
 * - Draggable via pointer events (mouse/touch)
 * - Snaps to nearest screen edge when released
 * - Remembers position with localStorage
 * - Keyboard accessible (arrow keys move, reset position button)
 * - Knows what's on the page (shows speech bubble for current section)
 * - Offers [Quick summary] and [Deep dive]
 */
export default function FloatingRobot({
  activeSection = null,
  onOpenChat,
  onOpenDeepDive
}) {
  // Coordinates state: default to bottom-right corner
  const [position, setPosition] = useState(() => {
    try {
      const saved = localStorage.getItem('hypoloom_robot_pos');
      if (saved) return JSON.parse(saved);
    } catch (e) {
      // localStorage may be disabled
    }
    return { x: window.innerWidth - 110, y: window.innerHeight - 118 };
  });

  const [isDragging, setIsDragging] = useState(false);
  const [dragMoved, setDragMoved] = useState(false);
  const [showBubble, setShowBubble] = useState(true);
  const [showSummaryView, setShowSummaryView] = useState(false);
  const [showA11yMenu, setShowA11yMenu] = useState(false);

  const dragRef = useRef({ startX: 0, startY: 0, initialX: 0, initialY: 0 });
  const buttonRef = useRef(null);

  // Keep robot inside viewport if window resizes
  useEffect(() => {
    const handleResize = () => {
      setPosition((prev) => ({
        x: Math.min(Math.max(20, prev.x), window.innerWidth - 104),
        y: Math.min(Math.max(20, prev.y), window.innerHeight - 104)
      }));
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Update bubble whenever activeSection changes
  useEffect(() => {
    if (activeSection) {
      setShowBubble(true);
      setShowSummaryView(false);
    }
  }, [activeSection?.id]);

  // Save position to localStorage
  const savePosition = (pos) => {
    try {
      localStorage.setItem('hypoloom_robot_pos', JSON.stringify(pos));
    } catch (e) {
      // Ignore storage errors
    }
  };

  // Pointer Events: Start Drag
  const handlePointerDown = (e) => {
    if (e.button !== 0 && e.pointerType === 'mouse') return;

    setIsDragging(true);
    setDragMoved(false);
    dragRef.current = {
      startX: e.clientX,
      startY: e.clientY,
      initialX: position.x,
      initialY: position.y
    };
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  // Pointer Events: Moving
  const handlePointerMove = (e) => {
    if (!isDragging) return;

    const deltaX = e.clientX - dragRef.current.startX;
    const deltaY = e.clientY - dragRef.current.startY;

    if (Math.hypot(deltaX, deltaY) > 6) {
      setDragMoved(true);
      setShowBubble(false);
    }

    const newX = Math.min(Math.max(16, dragRef.current.initialX + deltaX), window.innerWidth - 102);
    const newY = Math.min(Math.max(16, dragRef.current.initialY + deltaY), window.innerHeight - 102);

    setPosition({ x: newX, y: newY });
  };

  // Pointer Events: End Drag (Snap to nearest edge)
  const handlePointerUp = (e) => {
    if (!isDragging) return;
    setIsDragging(false);

    try {
      e.currentTarget.releasePointerCapture(e.pointerId);
    } catch (err) {}

    // If it was a real drag, snap to the nearest screen edge
    if (dragMoved) {
      const screenMid = window.innerWidth / 2;
      const snapX = position.x < screenMid ? 24 : window.innerWidth - 110;
      const finalY = Math.min(Math.max(24, position.y), window.innerHeight - 114);

      const finalPos = { x: snapX, y: finalY };
      setPosition(finalPos);
      savePosition(finalPos);
    } else {
      // Real click or tap: open chat!
      onOpenChat();
    }
  };

  // Keyboard navigation for robot
  const handleKeyDown = (e) => {
    const step = 25;
    let newPos = null;

    if (e.key === 'ArrowUp') {
      e.preventDefault();
      newPos = { ...position, y: Math.max(20, position.y - step) };
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      newPos = { ...position, y: Math.min(window.innerHeight - 104, position.y + step) };
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      newPos = { ...position, x: Math.max(20, position.x - step) };
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      newPos = { ...position, x: Math.min(window.innerWidth - 104, position.x + step) };
    } else if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onOpenChat();
    }

    if (newPos) {
      setPosition(newPos);
      savePosition(newPos);
    }
  };

  // Reset position helper
  const handleResetPosition = () => {
    const defaultPos = { x: window.innerWidth - 110, y: window.innerHeight - 118 };
    setPosition(defaultPos);
    savePosition(defaultPos);
    setShowA11yMenu(false);
  };

  const isNearLeft = position.x < window.innerWidth / 2;

  return (
    <div
      className="floating-robot-container"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        transition: isDragging ? 'none' : 'left 0.25s ease-out, top 0.25s ease-out'
      }}
    >
      {/* SPEECH BUBBLE: What's on this section */}
      {showBubble && activeSection && (
        <div
          className="robot-bubble"
          style={{
            left: isNearLeft ? '0' : 'auto',
            right: isNearLeft ? 'auto' : '0',
            bottom: '104px'
          }}
        >
          {/* Close bubble button */}
          <button
            onClick={() => setShowBubble(false)}
            style={{
              position: 'absolute',
              top: '8px',
              right: '8px',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--color-text-light)',
              padding: '2px'
            }}
            aria-label="Dismiss speech bubble"
          >
            <X size={14} />
          </button>

          {!showSummaryView ? (
            /* Bubble prompt view */
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '4px' }}>
                <Sparkles size={13} color="var(--color-accent)" />
                <span className="robot-bubble-title">Want to know about this?</span>
              </div>
              <p className="robot-bubble-text">
                {activeSection.title}
              </p>
              <div className="robot-bubble-actions">
                <button
                  className="btn btn-outline btn-sm"
                  style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem' }}
                  onClick={() => setShowSummaryView(true)}
                >
                  Quick summary
                </button>
                <button
                  className="btn btn-accent btn-sm"
                  style={{ fontSize: '0.75rem', padding: '0.25rem 0.65rem' }}
                  onClick={() => {
                    setShowBubble(false);
                    onOpenDeepDive(activeSection);
                  }}
                >
                  Deep dive →
                </button>
              </div>
            </div>
          ) : (
            /* Quick Summary view (2 simple sentences) */
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '4px' }}>
                <strong style={{ fontSize: '0.8rem', color: 'var(--color-text-main)' }}>Quick Summary:</strong>
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', lineHeight: '1.45', margin: '4px 0 8px' }}>
                {activeSection.summary}
              </p>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <button
                  style={{ background: 'none', border: 'none', fontSize: '0.75rem', color: 'var(--color-text-light)', cursor: 'pointer', padding: 0 }}
                  onClick={() => setShowSummaryView(false)}
                >
                  ← Back
                </button>
                <button
                  className="btn btn-accent btn-sm"
                  style={{ fontSize: '0.75rem', padding: '0.25rem 0.65rem' }}
                  onClick={() => {
                    setShowBubble(false);
                    onOpenDeepDive(activeSection);
                  }}
                >
                  Open deep dive
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* THE EYE-CATCHING ROBOT BUTTON */}
      <button
        ref={buttonRef}
        type="button"
        className={`robot-button ${!isDragging ? 'robot-float-anim' : ''}`}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
        onKeyDown={handleKeyDown}
        aria-label="Hypoloom AI Robot Assistant. Click to open chatbot. Arrow keys move position."
        title="AI Robot Assistant (Drag to reposition, click to ask)"
      >
        {/* Pulsing attention ring */}
        <div className="robot-pulse-ring" />

        {/* Floating "Ask Detective" badge with blinking green beacon */}
        <div className="robot-badge-pill">
          <span className="robot-beacon-dot" />
          <span>Ask Detective</span>
        </div>

        {/* Large Friendly SVG Icon */}
        <RobotSvg />
      </button>

      {/* Small accessibility reset pill */}
      <button
        onClick={handleResetPosition}
        style={{
          position: 'absolute',
          bottom: '-22px',
          left: '50%',
          transform: 'translateX(-50%)',
          background: 'none',
          border: 'none',
          fontSize: '0.65rem',
          color: 'var(--color-text-light)',
          cursor: 'pointer',
          whiteSpace: 'nowrap',
          textDecoration: 'underline',
          opacity: 0.8
        }}
        title="Reset robot to bottom-right corner"
      >
        Reset position
      </button>
    </div>
  );
}
