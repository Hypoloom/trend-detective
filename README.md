# 🛰️ Hypoloom · Earth System Trend Detective

> **NASA Space Apps Challenge:** *"Be An Earth System Trend Detective"*  
> Decode decades of NASA satellite records into clear, honest trends that students and the general public can understand.

---

## ⚡ Quick Start: How to Run the App

Open your terminal or command prompt inside the `hypoloom` folder and run:

```bash
# 1. Start the local development server
npm run dev
```

Then open **`http://localhost:5173`** in your browser.

To create a production build ready for deployment:
```bash
npm run build
```

---

## 🧭 What Was Updated (New Layout & AI Robot Assistant)

### 1. Clean, Uncrowded Layout (8px Spacing Scale)
- **Full width of screen:** No static chat box permanently sitting on the page.
- **One main idea per section:** Generous white space between sections (48px–80px gaps).
- **Maximum 3 cards in a row:** Clean grid layouts with high readability.
- **Larger body text:** 17–18px body font with line lengths kept under 68 characters.
- **Progressive disclosure:** Complex stats (p-value, confidence interval, sensor info) sit behind a clean **"Show details"** toggle button. The plain result is shown first!
- **Simple 4-item navigation:** **Home**, **Explorer**, **Data Gaps**, **Method**.

### 2. Draggable AI Robot Assistant
- **Floating Robot Icon:** A friendly custom SVG robot floats in the bottom-right corner of **every page**.
- **Gentle Hover Animation:** Smooth floating animation, disabled if the user has `prefers-reduced-motion` enabled.
- **Draggable:** Drag with mouse or finger using pointer events.
- **Smart Edge Snapping:** When released, snaps cleanly to the nearest screen edge or corner.
- **Remembers Position:** Saves position in `localStorage` safely wrapped in `try/catch`.
- **Accidental Drag Protection:** Dragging does NOT trigger the chat. Only an intentional click or tap opens the chat.
- **Keyboard Alternative:** Use Arrow keys when the robot is focused to move it; click "Reset position" to snap back.

### 3. Context-Aware Speech Bubble & Deep Dive
- As you hover or scroll to different sections, the robot shows a speech bubble:
  `"Want to know about [Section Title]?"`
- Buttons:
  - **`[Quick summary]`**: Gives a 2-sentence plain-language summary in the bubble.
  - **`[Deep dive]`**: Slides open the chat panel, presents a progressive walk-down (**Plain** -> **Detailed** -> **Pro**), and provides 3 follow-up question chips.
- Each chart and heading also has an **`Ask about this`** pill button that triggers the same deep dive.

### 4. Half-Screen Slide-Out Chat Panel
- When the chat opens, it slides in on the **RIGHT HALF** of the screen (50% on desktop).
- The page content smoothly moves into the **LEFT HALF** and reflows so nothing is cut off.
- On mobile and tablet, the chat panel slides in full-screen with a friendly Back/Close button.
- Pressing `Esc` or clicking `Close` closes the panel and returns focus to the robot.

---

## 📂 Project Structure & Key Files

```text
hypoloom/
├── index.html                   # HTML template with Google Fonts (Fraunces & Plus Jakarta Sans)
├── package.json                 # Project dependencies (React 18, Vite, Recharts, Lucide Icons)
├── vite.config.js               # Fast development build settings
└── src/
    ├── main.jsx                 # React entry point
    ├── App.jsx                  # Split layout (workspace + chat-panel) and section tracker
    ├── index.css                # 8px spacing scale, full-width reflow layout, robot animations
    │
    ├── data/
    │   └── mockData.js          # ⭐ SINGLE SOURCE OF TRUTH (datasets, PAGE_SECTIONS & getAnswer)
    │
    ├── components/
    │   ├── Navbar.jsx           # Simplified 4-item navigation & glossary button
    │   ├── Footer.jsx           # NASA Space Apps attribution & honesty statement
    │   ├── FloatingRobot.jsx    # Draggable SVG robot assistant with speech bubble
    │   ├── ChatPanel.jsx        # Half-screen slide-out chat with Plain/Detailed/Pro tabs
    │   ├── StatsCard.jsx        # Stats card with "Show details" progressive disclosure toggle
    │   ├── DataGapCard.jsx      # Unique Data Gap card: "What is missing and what would settle it?"
    │   ├── TrendChart.jsx       # Recharts component (1 or 2 variables, CSV & PNG downloads)
    │   └── GlossaryModal.jsx    # Pop-up dictionary for scientific terms
    │
    └── pages/
        ├── Home.jsx             # Hero headline, Figure 1 live chart, 3-step How It Works, Data Gaps
        ├── ExplorerPage.jsx     # Dropdown filters (1 or 2 variables), year-range slider, live chart
        ├── DataGapsPage.jsx     # Matrix of unclear trends, reason badges & progress bars
        └── MethodPage.jsx       # Plain-language guide to Mann-Kendall, Sen's slope & NASA sensors
```

---

## 🛠️ Where to Customize

### 1. Where to Edit Text & Section Information
- **Page content & headlines:**
  - Home: [`src/pages/Home.jsx`](file:///C:/Users/Ankit/.gemini/antigravity/scratch/hypoloom/src/pages/Home.jsx)
  - Explorer: [`src/pages/ExplorerPage.jsx`](file:///C:/Users/Ankit/.gemini/antigravity/scratch/hypoloom/src/pages/ExplorerPage.jsx)
  - Data Gaps: [`src/pages/DataGapsPage.jsx`](file:///C:/Users/Ankit/.gemini/antigravity/scratch/hypoloom/src/pages/DataGapsPage.jsx)
  - Method: [`src/pages/MethodPage.jsx`](file:///C:/Users/Ankit/.gemini/antigravity/scratch/hypoloom/src/pages/MethodPage.jsx)
- **Robot Section Knowledge:** Edit `PAGE_SECTIONS` in [`src/data/mockData.js`](file:///C:/Users/Ankit/.gemini/antigravity/scratch/hypoloom/src/data/mockData.js). Each section has `title`, `summary`, `deepDive`, and `suggestedQuestions`.

### 2. Where to Change Colours & Theme
All theme variables are at the top of [`src/index.css`](file:///C:/Users/Ankit/.gemini/antigravity/scratch/hypoloom/src/index.css):
```css
:root {
  --color-accent: #C85A32;        /* NASA Terracotta orange */
  --color-bg: #FFFFFF;            /* White page background */
  --status-sig-bg: #DCFCE7;       /* Green for Significant */
  --status-sig-text: #15803D;
  --status-unclear-bg: #FEF3C7;   /* Amber for Not Yet Clear */
  --status-unclear-text: #B45309;
}
```

### 3. Where to Plug in Real Data (For Your Teammate)
Your teammate only needs to replace `getAnswer(question, sectionContext)` in [`src/data/mockData.js`](file:///C:/Users/Ankit/.gemini/antigravity/scratch/hypoloom/src/data/mockData.js):
```javascript
export async function getAnswer(question, sectionContext) {
  // Replace with real backend or NASA Earthdata API:
  // const res = await fetch(`/api/query?q=${encodeURIComponent(question)}`);
  // return await res.json();
}
```

---

## 🛡️ The Detective Honesty Rule
The robot assistant is programmed to **only explain numbers that exist in the satellite data object**. It never hallucinates non-existent trends, speculates causes without data, or exaggerates certainty.
