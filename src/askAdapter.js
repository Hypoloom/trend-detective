import { askQuestion } from './api';

const LEVELS = ['plain', 'detailed', 'pro'];

export const VERDICT_LABELS = {
  detected: 'Trend detected',
  no_trend: 'No trend found',
  data_limited: 'Data-limited',
  masked: 'Masked by aggregation',
  inconclusive: 'Inconclusive'
};

// Questions the router is known to match (pond, citrus).
export const LIVE_CHIPS = [
  'Why is my pond turning green?',
  'My pond turned green',
  'Why are my oranges so small this year?'
];

// One /api/ask call per level, so the three tabs show backend text.
export async function askAll(question, region = 'maharashtra') {
  const res = await Promise.all(LEVELS.map((l) => askQuestion(question, l, region)));
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
  const axes = rawAxes.map((a) => ({
    label: a.label || a.name,
    status: a.status,
    verdict: a.result && a.result.verdict ? a.result.verdict.code : null,
    fragile: Boolean(a.result && a.result.trend && a.result.trend.fragile)
  }));
  const withChart = rawAxes.find(
    (a) => a.status === 'analyzed' && a.result && a.result.chart && a.result.chart.points
  );
  const series = withChart
    ? withChart.result.chart.points.map((p) => ({ year: p.year, value: p.value }))
    : [];
  return {
    kind: 'answer',
    topic: first.domain,
    abstained: Boolean(first.abstained),
    abstainReason: result.abstain_reason || '',
    axes,
    texts,
    series,
    seriesLabel: withChart ? (withChart.label || withChart.name) : '',
    usedLlm: Boolean(first.used_llm)
  };
}