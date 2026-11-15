import { askQuestion } from './api';

const LEVELS = ['plain', 'detailed', 'pro'];

export const VERDICT_LABELS = {
  detected: 'Trend detected',
  no_trend: 'No trend found',
  data_limited: 'Data-limited',
  masked: 'Masked by aggregation',
  inconclusive: 'Inconclusive'
};

// Same ids as REGIONS in backend/app.py.
export const REGION_OPTIONS = [
  { id: 'maharashtra', label: 'Maharashtra' },
  { id: 'rajasthan', label: 'Rajasthan' },
  { id: 'kerala', label: 'Kerala' },
  { id: 'gujarat', label: 'Gujarat' }
];

// Questions the router is known to match (pond, citrus).
export const LIVE_CHIPS = [
  'Why is my pond turning green?',
  'My pond turned green',
  'Why are my oranges so small this year?', 'Is it getting hotter where I live?', 'Is the monsoon getting wetter or drier?', 'Are summers getting sunnier or cloudier?'
];

// Short label chosen only from the backend's why.class.
const REASON_LABELS = {
  no_trend_below_meaningful: 'Estimated change is smaller than the size chosen as meaningful',
  no_trend_reaches_meaningful: 'A change of the meaningful size cannot be ruled out',
  data_limited: 'Record may be too short or too noisy',
  masked: 'Opposite regional trends may be hidden by combining them',
  inconclusive: 'Evidence is mixed',
  no_trend: 'No trend found (not proof of no change)'
};

const TOPIC_LABELS = {
  pond: 'Pond turning green',
  citrus: 'Small oranges',
  heat: 'Is it getting hotter?',
  monsoon: 'Monsoon rainfall',
  sunshine: 'Sunshine',
  year_vs_record: 'This year compared with the record',
  region_compare: 'Region comparison',
  season: 'Season trend'
};

const isNum = (x) => typeof x === 'number' && Number.isFinite(x);

// chart.trend_line has two points {year, trend, low, high}. Interpolate a
// straight line (and its band) across every year so the chart can draw it.
function buildSeries(chart) {
  const pts = (chart.points || []).map((p) => ({ year: p.year, value: p.value }));
  const tl = Array.isArray(chart.trend_line) ? chart.trend_line : [];
  if (tl.length < 2) return pts;
  const a = tl[0];
  const b = tl[tl.length - 1];
  const keys = ['trend', 'low', 'high'];
  if (!keys.every((k) => isNum(a[k]) && isNum(b[k])) || !isNum(a.year) || !isNum(b.year)) return pts;
  const span = b.year - a.year;
  const lerp = (k, y) => (span ? a[k] + ((b[k] - a[k]) * (y - a.year)) / span : a[k]);
  return pts.map((p) => ({
    ...p,
    trend: lerp('trend', p.year),
    low: lerp('low', p.year),
    high: lerp('high', p.year)
  }));
}

// One /api/ask call per level, so the three tabs show backend text.
export async function askAll(question, region = 'maharashtra', context = null) {
  const res = await Promise.all(LEVELS.map((l) => askQuestion(question, l, region, context)));
  const first = res[0];
  if (first.fallback) {
    return {
      kind: 'fallback',
      topic: 'Guided form',
      reason: first.reason || '',
      formText: typeof first.form_text === 'string' ? first.form_text : ''
    };
  }
  const texts = {};
  LEVELS.forEach((l, i) => { texts[l] = res[i].text || ''; });
  const result = first.result || {};
  const rawAxes = result.axes || [];
  const axes = rawAxes.map((a) => {
    const r = a.result || null;
    const why = r && r.why ? r.why : null;
    return {
      label: a.label || a.name,
      status: a.status,
      verdict: r && r.verdict ? r.verdict.code : null,
      fragile: Boolean(r && r.trend && r.trend.fragile),
      units: r && r.trend ? r.trend.units || '' : '',
      why,
      reasonLabel: why ? REASON_LABELS[why.class] || '' : ''
    };
  });
  const withChart = rawAxes.find(
    (a) => a.status === 'analyzed' && a.result && a.result.chart && a.result.chart.points
  );
  const series = withChart ? buildSeries(withChart.result.chart) : [];
  const prov = withChart && withChart.result.provenance ? withChart.result.provenance : {};
  const regionOption = REGION_OPTIONS.find((r) => r.id === region); const shownOption = REGION_OPTIONS.find((r) => r.label === result.region) || regionOption; const shownRegion = shownOption ? shownOption.id : region;
  return {
    kind: 'answer',
    topic: first.domain, topicLabel: TOPIC_LABELS[first.domain] || first.domain,
    regionId: shownRegion,
    regionLabel: result.region || (first.domain === 'region_compare' ? 'All four regions' : (regionOption ? regionOption.label : region)),
    startYear: prov.start ? String(prov.start).slice(0, 4) : null,
    endYear: prov.end ? String(prov.end).slice(0, 4) : null,
    abstained: Boolean(first.abstained),
    abstainReason: result.abstain_reason || '',
    axes,
    riskWindow: result.risk_window || null,
    texts,
    series,
    hasTrendLine: series.length > 0 && isNum(series[0].trend),
    seriesLabel: withChart ? (withChart.label || withChart.name) : '',
    usedLlm: Boolean(first.used_llm)
  };
}