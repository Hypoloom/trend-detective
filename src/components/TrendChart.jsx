import React, { useRef } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { Download, FileSpreadsheet } from 'lucide-react';

/**
 * Custom Tooltip for Recharts
 * High-contrast tooltip styled with CSS variables (adapts to light and dark themes).
 */
function CustomTooltip({ active, payload, label, unit = "°C", secondaryUnit = "" }) {
  if (active && payload && payload.length) {
    return (
      <div
        style={{
          backgroundColor: 'var(--color-bg-card)',
          border: '1px solid var(--color-border-dark)',
          borderRadius: 'var(--radius-md)',
          padding: '0.75rem 1rem',
          boxShadow: 'var(--shadow-md)',
          fontSize: '0.85rem',
          color: 'var(--color-text-main)'
        }}
      >
        <div style={{ fontWeight: 700, color: 'var(--color-text-main)', marginBottom: '0.35rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.25rem' }}>
          Year {label}
        </div>
        {payload.map((entry, index) => {
          const isSecondary = entry.dataKey === 'value2';
          const entryUnit = isSecondary ? (secondaryUnit || unit) : unit;
          return (
            <div key={`item-${index}`} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', marginTop: '0.25rem' }}>
              <span style={{ color: entry.color, display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 500 }}>
                <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: '50%', backgroundColor: entry.color }} />
                {entry.name}:
              </span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--color-text-main)' }}>
                {entry.value !== undefined ? Number(entry.value).toFixed(2) : 'N/A'} {entryUnit}
              </span>
            </div>
          );
        })}
      </div>
    );
  }
  return null;
}

/**
 * TrendChart Component
 * Displays satellite time-series data and calculated trend line.
 * Features:
 * - Single or dual series support
 * - Theme-aware styling (Light & Dark mode)
 * - Loading skeleton mode
 * - Download CSV and Download PNG
 */
export default function TrendChart({
  series = [],
  series2 = null,
  variable1Name = "Observed Value",
  variable2Name = "",
  unit1 = "°C",
  unit2 = "",
  title = "Time Series & Trend",
  caption = "The line shows annual satellite readings. The dashed orange line is the Sen's slope trend.",
  isLoading = false,
  height = 340,
  showDownloadButtons = true
}) {
  const chartWrapperRef = useRef(null);

  // Download raw series as CSV file
  const handleDownloadCSV = () => {
    if (!series || series.length === 0) return;

    let headers = `Year,"${variable1Name} (${unit1})",TrendLine`;
    if (series2 && series2.length > 0) {
      headers += `,"${variable2Name || 'Variable 2'} (${unit2 || unit1})"`;
    }

    const rows = series.map((pt, idx) => {
      let line = `${pt.year},${pt.value},${pt.trend || ''}`;
      if (series2 && series2[idx]) {
        line += `,${series2[idx].value}`;
      }
      return line;
    });

    const csvContent = "data:text/csv;charset=utf-8," + [headers, ...rows].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `hypoloom_data_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Download chart as PNG image
  const handleDownloadPNG = () => {
    if (!chartWrapperRef.current) return;
    const svgElement = chartWrapperRef.current.querySelector("svg");
    if (!svgElement) return;

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const svgString = new XMLSerializer().serializeToString(svgElement);
    const svgBlob = new Blob([svgString], { type: "image/svg+xml;charset=utf-8" });
    const URL = window.URL || window.webkitURL || window;
    const blobURL = URL.createObjectURL(svgBlob);

    const image = new Image();
    image.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = svgElement.clientWidth || 800;
      canvas.height = svgElement.clientHeight || 400;
      const context = canvas.getContext("2d");
      // Background matched to active theme
      context.fillStyle = isDark ? "#0B0F17" : "#FFFFFF";
      context.fillRect(0, 0, canvas.width, canvas.height);
      context.drawImage(image, 0, 0);

      const png = canvas.toDataURL("image/png");
      const downloadLink = document.createElement("a");
      downloadLink.download = `hypoloom_chart_${Date.now()}.png`;
      downloadLink.href = png;
      downloadLink.click();
    };
    image.src = blobURL;
  };

  // Merge series if dual variable
  const mergedData = series.map((item, idx) => {
    const pt2 = series2 ? series2[idx] : null;
    return {
      year: item.year,
      value: item.value,
      trend: item.trend,
      value2: pt2 ? pt2.value : undefined,
      trend2: pt2 ? pt2.trend : undefined,
    };
  });

  // Loading skeleton state
  if (isLoading) {
    return (
      <div style={{ marginTop: '1rem', width: '100%' }}>
        <div style={{ height: '24px', width: '40%', marginBottom: '1rem' }} className="skeleton" />
        <div style={{ height: `${height}px`, width: '100%' }} className="skeleton" />
        <div style={{ height: '16px', width: '60%', marginTop: '0.75rem' }} className="skeleton" />
      </div>
    );
  }

  return (
    <div style={{ width: '100%', position: 'relative' }}>
      {/* Top action row */}
      {showDownloadButtons && (
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <button
            onClick={handleDownloadCSV}
            className="btn btn-outline btn-sm"
            style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem', borderRadius: 'var(--radius-full)' }}
            title="Download CSV spreadsheet"
          >
            <FileSpreadsheet size={13} />
            <span>CSV</span>
          </button>
          <button
            onClick={handleDownloadPNG}
            className="btn btn-outline btn-sm"
            style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem', borderRadius: 'var(--radius-full)' }}
            title="Download PNG chart image"
          >
            <Download size={13} />
            <span>PNG</span>
          </button>
        </div>
      )}

      {/* Recharts Container */}
      <div ref={chartWrapperRef} style={{ width: '100%', height: `${height}px` }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={mergedData} margin={{ top: 10, right: 15, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border)" />
            <XAxis
              dataKey="year"
              tickLine={false}
              axisLine={{ stroke: 'var(--color-border-dark)' }}
              tick={{ fill: 'var(--color-text-light)', fontSize: 11, fontFamily: 'var(--font-sans)' }}
              dy={8}
            />
            {/* Primary Y-Axis */}
            <YAxis
              yAxisId="left"
              tickLine={false}
              axisLine={{ stroke: 'var(--color-border-dark)' }}
              tick={{ fill: 'var(--color-text-light)', fontSize: 11, fontFamily: 'var(--font-sans)' }}
              domain={['auto', 'auto']}
              unit={` ${unit1}`}
            />
            {/* Secondary Y-Axis for 2nd variable */}
            {series2 && (
              <YAxis
                yAxisId="right"
                orientation="right"
                tickLine={false}
                axisLine={{ stroke: 'var(--color-border-dark)' }}
                tick={{ fill: '#38BDF8', fontSize: 11, fontFamily: 'var(--font-sans)' }}
                domain={['auto', 'auto']}
                unit={` ${unit2 || ''}`}
              />
            )}
            <Tooltip
              content={<CustomTooltip unit={unit1} secondaryUnit={unit2} />}
            />
            <Legend
              verticalAlign="top"
              align="right"
              wrapperStyle={{ paddingBottom: '10px', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}
            />

            {/* Variable 1: Seasonal reading */}
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="value"
              name={variable1Name}
              stroke="var(--color-text-main)"
              strokeWidth={2}
              dot={{ r: 2.5, fill: 'var(--color-text-main)', strokeWidth: 0 }}
              activeDot={{ r: 5, fill: 'var(--color-accent)' }}
            />

            {/* Variable 1: Sen's Slope Trend */}
            <Line
              yAxisId="left"
              type="linear"
              dataKey="trend"
              name="Calculated Trend"
              stroke="var(--color-accent)"
              strokeWidth={2.5}
              strokeDasharray="4 2"
              dot={false}
              isAnimationActive={false}
            />

            {/* Variable 2 (if selected) */}
            {series2 && (
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="value2"
                name={variable2Name || "Variable 2"}
                stroke="#38BDF8"
                strokeWidth={2}
                dot={{ r: 2, fill: '#38BDF8' }}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Editorial Caption under the chart */}
      {caption && (
        <p style={{ fontSize: '0.85rem', color: 'var(--color-text-light)', marginTop: '0.75rem', fontStyle: 'italic' }}>
          {caption}
        </p>
      )}
    </div>
  );
}
