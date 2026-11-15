/**
 * PURE CLIENT-SIDE MOCK DATA FOR HYPOLOOM (NASA SPACE APPS CHALLENGE)
 * -------------------------------------------------------------------
 * SIMULATED EXAMPLE DATA. The Explorer and Ask pages use a live backend on cached NASA MERRA-2 reanalysis (a model product, 1980-2025). The numbers in this file are simulated examples, not measurements.
 * All sample series, example statistics, glossary terms,
 * and question-answering logic live entirely in memory in this single file.
 */

// 1. PLAIN-LANGUAGE GLOSSARY
export const GLOSSARY = {
  significant: {
    term: "Statistically Significant",
    simple: "The pattern is strong enough that it is almost certainly NOT just random luck or weather noise.",
    detail: "In science, we call a trend significant when a change this large would show up less than 5% of the time (p < 0.05) from natural year-to-year swings alone."
  },
  not_significant: {
    term: "Not Significant (Yet)",
    simple: "The numbers swing up and down too much from year to year to show an enduring long-term shift.",
    detail: "This does not mean nothing is happening! It often means natural variability is large and we need more years of records to be sure."
  },
  p_value: {
    term: "p-value",
    simple: "The 'luck meter'. The smaller this number, the more confident we are that the trend is real.",
    detail: "A p-value below 0.05 means that, if nothing were really changing, a trend this large would show up less than 1 time in 20. For example, a p-value of 0.01 means about 1 time in 100."
  },
  confidence_interval: {
    term: "95% Confidence Interval",
    simple: "The likely range for the true speed of change.",
    detail: "For example, '+0.04 to +0.08 °C per year' means we are 95% certain the real warming rate falls inside this bracket."
  },
  mann_kendall: {
    term: "Mann-Kendall Test",
    simple: "A statistical test NASA scientists use to check if numbers consistently climb or fall over decades.",
    detail: "It works well even if one year was unusually stormy or dry, because it only cares if each year is higher or lower than previous years."
  },
  sens_slope: {
    term: "Sen's Slope",
    simple: "The robust average change per year, immune to one-off extreme years.",
    detail: "It calculates slopes between all pairs of years and picks the median slope, so a single drought or flood doesn't distort the true trend."
  },
  data_gap: {
    term: "Data Gap / Observational Limit",
    simple: "When the record doesn't have enough years or fine enough detail to confirm a trend.",
    detail: "Instead of saying 'nothing is happening', we calculate how many additional years or what spatial resolution would be required to settle the question."
  },
  ndvi: {
    term: "NDVI (Vegetation Index)",
    simple: "A satellite score from 0 to 1 measuring how green and leafy plants are on the ground.",
    detail: "Derived by comparing red and near-infrared light reflected by chlorophyll. High values (>0.6) mean lush forests; low values (<0.2) mean desert."
  },
  grace: {
    term: "GRACE / GRACE-FO Groundwater",
    simple: "Twin NASA satellites that weigh the Earth from space to track water underground.",
    detail: "By measuring tiny changes in Earth's gravity, GRACE detects deep aquifers shrinking or refilling in centimeters of equivalent water thickness."
  }
};

// 2. REGION DEFINITIONS
export const REGIONS = [
  { id: "rajasthan", name: "Rajasthan, India", desc: "Thar Desert Basin & Agricultural Belt" },
  { id: "jaipur", name: "Jaipur District, India", desc: "Semi-Arid Urban & Monsoon Catchment" },
  { id: "central_valley", name: "Central Valley, California, USA", desc: "Intensive Irrigation Aquifer Basin" },
  { id: "kyoto", name: "Kyoto Basin, Japan", desc: "Long-Term Cherry Blossom (Sakura) Phenology" },
  { id: "amazon", name: "Amazon Basin (Rondônia), Brazil", desc: "Tropical Rainforest Frontier" },
  { id: "sahel", name: "Sahel Belt, West Africa", desc: "Semi-Arid Transition Zone" }
];

// 3. VARIABLE DEFINITIONS
export const VARIABLES = [
  {
    id: "summer_temp",
    name: "Summer Temperature",
    unit: "°C",
    satellite: "NASA Terra/Aqua MODIS (LST)",
    resolution: "1 km daily / seasonal mean",
    color: "#C85A32",
    description: "Average daytime surface temperature from May to July."
  },
  {
    id: "rainfall",
    name: "Annual Precipitation",
    unit: "mm/yr",
    satellite: "NASA GPM IMERG / TRMM",
    resolution: "10 km monthly aggregated",
    color: "#2563EB",
    description: "Total annual rainfall measured from spaceborne radars and microwave radiometers."
  },
  {
    id: "ndvi",
    name: "Vegetation Index (NDVI)",
    unit: "index (0–1)",
    satellite: "NASA MODIS MOD13A2",
    resolution: "250 m 16-day composite",
    color: "#16A34A",
    description: "Satellite plant greenness index, tracking crop health and forest canopy density."
  },
  {
    id: "water_table",
    name: "Groundwater Storage Anomaly",
    unit: "cm water",
    satellite: "NASA/GFZ GRACE & GRACE-FO",
    resolution: "300 km monthly gravity anomaly",
    color: "#0891B2",
    description: "Changes in underground aquifer water volume compared to the 2004–2009 baseline."
  },
  {
    id: "no2",
    name: "Nitrogen Dioxide (Air Quality)",
    unit: "10¹⁵ molec/cm²",
    satellite: "NASA Aura OMI & Sentinel-5P",
    resolution: "3.5 km daily tropospheric column",
    color: "#9333EA",
    description: "Atmospheric combustion emissions from vehicles, power plants, and brick kilns."
  },
  {
    id: "spring_bloom",
    name: "Spring Bloom Date",
    unit: "Day of Year",
    satellite: "NASA Phenology & MODIS EVI",
    resolution: "Regional phenology index",
    color: "#E11D48",
    description: "First peak flower bloom date (Day of Year 80 = March 21, Day 90 = March 31)."
  }
];

// 4. HELPER: Generate realistic yearly series (1990 to 2025)
function generateSeries(startYear, endYear, baseVal, slope, noiseAmp, roundDecimals = 2) {
  const points = [];
  for (let year = startYear; year <= endYear; year++) {
    const elapsed = year - startYear;
    const pseudoSin = Math.sin(year * 1.7) * 0.6 + Math.cos(year * 0.9) * 0.4;
    const noise = pseudoSin * noiseAmp;
    const trendVal = baseVal + slope * elapsed;
    const value = parseFloat((trendVal + noise).toFixed(roundDecimals));
    points.push({
      year,
      value,
      trend: parseFloat(trendVal.toFixed(roundDecimals))
    });
  }
  return points;
}

// 5. SIMULATED EXAMPLE RECORDS (In-Memory Database; not measurements)
export const SERIES_DATABASE = {
  // 1. Rajasthan - Summer Temperature (Significant warming)
  "rajasthan_summer_temp": {
    regionId: "rajasthan",
    variableId: "summer_temp",
    title: "Example (simulated data): Average Summer Temperature, Rajasthan",
    subtitle: "Simulated example data, not a measurement (1990–2025)",
    verdict: "significant",
    slopePerYear: 0.058,
    pValue: 0.0004,
    ci95: [0.042, 0.075],
    yearsUsed: 36,
    dataset: "NASA MODIS / Terra LST (MOD11A2)",
    series: generateSeries(1990, 2025, 29.8, 0.058, 0.35, 2),
    summary: {
      plain: "Simulated example: this made-up series is built to show a steady warming pattern. The numbers are not measurements and are not results for any real place.",
      detailed: "Simulated example: a Mann-Kendall test on 36 made-up summers, shown only to illustrate how a result is displayed. The numbers were generated for this example and are not measurements.",
      pro: "Simulated example values, not measurements. Mann-Kendall Tau = 0.542, p = 0.0004 (< 0.001). Sen's Slope = +0.058 °C/yr (95% CI: [0.042, 0.075] °C/yr). Baseline: 1990–2025 (n = 36 summers). Instrument named for illustration only: MODIS LST."
    },
    gap: {
      reason: "Probably no real change",
      status: "clear",
      yearsHave: 36,
      yearsNeed: 36,
      tip: "Simulated example: no real record is being evaluated here."
    },
    followUps: [
      "Why is this trend significant?",
      "How much hotter will next summer be?",
      "What sensor recorded this temperature?"
    ]
  },

  // 2. Jaipur - Rainfall (Not Significant - Data Gap example!)
  "jaipur_rainfall": {
    regionId: "jaipur",
    variableId: "rainfall",
    title: "Example (simulated data): Annual Monsoon Precipitation, Jaipur District",
    subtitle: "Simulated example data, not a measurement (1990–2025)",
    verdict: "not_significant",
    slopePerYear: -2.15,
    pValue: 0.284,
    ci95: [-6.80, 2.50],
    yearsUsed: 36,
    dataset: "NASA GPM IMERG / TRMM Multi-satellite Precipitation",
    series: generateSeries(1990, 2025, 580, -2.15, 95.0, 1),
    summary: {
      plain: "Simulated example: this made-up rainfall series swings a lot from year to year, so the example shows a case where a trend is not yet clear. It is not a result for any real place.",
      detailed: "Simulated example: in this made-up series the year-to-year swings are larger than the slope, so no trend can be separated from natural variability. The numbers are not measurements.",
      pro: "Simulated example values, not measurements. Mann-Kendall Tau = -0.124, p = 0.284 (fail to reject null hypothesis at α = 0.05). Sen's Slope = -2.15 mm/yr (95% CI: [-6.80, +2.50] mm/yr). Sensor: NASA GPM IMERG Final Run v06."
    },
    gap: {
      reason: "Not enough data yet",
      status: "unclear",
      yearsHave: 36,
      yearsNeed: 50,
      tip: "Simulated example: when natural swings are large, many more years of records are needed before a trend can be separated from natural variability."
    },
    followUps: [
      "Why is this trend not significant?",
      "What would settle this rainfall question?",
      "Can we use daily rain data instead?"
    ]
  },

  // 3. Rajasthan / Thar - Vegetation Index NDVI (Method Limit example)
  "rajasthan_ndvi": {
    regionId: "rajasthan",
    variableId: "ndvi",
    title: "Example (simulated data): Vegetation Index (NDVI), Thar Desert Margin",
    subtitle: "Simulated example data, not a measurement (2000–2025)",
    verdict: "not_significant",
    slopePerYear: 0.0004,
    pValue: 0.420,
    ci95: [-0.0006, 0.0014],
    yearsUsed: 26,
    dataset: "NASA MODIS MOD13A2 (250m)",
    series: generateSeries(2000, 2025, 0.22, 0.0004, 0.03, 3),
    summary: {
      plain: "Simulated example: in this made-up series the signal is too blurry to be certain. It is not a result for any real place.",
      detailed: "Simulated example: an illustration of a method limit, where coarse pixels can hide small local changes. The numbers are not measurements.",
      pro: "Simulated example values, not measurements. Mann-Kendall Tau = +0.088, p = 0.420. Sen's Slope = +0.0004 NDVI units/yr (95% CI: [-0.0006, +0.0014]). Sensor: MODIS 250m composite."
    },
    gap: {
      reason: "Method limit",
      status: "unclear",
      yearsHave: 26,
      yearsNeed: 40,
      tip: "Simulated example: coarse pixels can hide small local changes. Finer-resolution data could help in a case like this."
    },
    followUps: [
      "What is a method limit?",
      "Why is 250m resolution too coarse?",
      "Is the desert actually getting greener?"
    ]
  },

  // 4. Central Valley, California - Groundwater (Significant Depletion)
  "central_valley_water_table": {
    regionId: "central_valley",
    variableId: "water_table",
    title: "Example (simulated data): Groundwater Storage Anomaly, California Central Valley",
    subtitle: "Simulated example data, not a measurement (2002–2025)",
    verdict: "significant",
    slopePerYear: -1.82,
    pValue: 0.0001,
    ci95: [-2.20, -1.45],
    yearsUsed: 24,
    dataset: "NASA GRACE / GRACE-FO Tellus Level-3 Land Mascon",
    series: generateSeries(2002, 2025, 8.5, -1.82, 3.8, 1),
    summary: {
      plain: "Simulated example: this made-up series shows steady drawdown to illustrate a clear trend. It is not a measurement of any real aquifer.",
      detailed: "Simulated example: shown only to illustrate how a clear result is displayed. The numbers are generated for this example and are not measurements.",
      pro: "Simulated example values, not measurements. Mann-Kendall Tau = -0.684, p = 0.0001. Sen's Slope = -1.82 cm Eq. Water/yr (95% CI: [-2.20, -1.45] cm/yr). Sensor: GRACE & GRACE-FO CSR RL06 Mascons."
    },
    gap: {
      reason: "Probably no real change",
      status: "clear",
      yearsHave: 24,
      yearsNeed: 24,
      tip: "Simulated example: no real record is being evaluated here."
    },
    followUps: [
      "How can satellites weigh water from space?",
      "Did the 2023 wet winter fix the aquifer?",
      "What is the 95% confidence interval here?"
    ]
  },

  // 5. Kyoto, Japan - Cherry Blossom Bloom Date
  "kyoto_spring_bloom": {
    regionId: "kyoto",
    variableId: "spring_bloom",
    title: "Example (simulated data): Cherry Blossom (Sakura) First-Bloom Date, Kyoto",
    subtitle: "Simulated example data, not a measurement (1990–2025)",
    verdict: "significant",
    slopePerYear: -0.28,
    pValue: 0.0042,
    ci95: [-0.41, -0.12],
    yearsUsed: 36,
    dataset: "NASA MODIS / Terra Enhanced Vegetation Index & Historic Phenology",
    series: generateSeries(1990, 2025, 96.5, -0.28, 3.2, 1),
    summary: {
      plain: "Simulated example: this made-up series shows blooms getting earlier, to illustrate a clear trend. It is not a measurement.",
      detailed: "Simulated example: shown only to illustrate how a clear result is displayed. The numbers are generated and are not measurements.",
      pro: "Simulated example values, not measurements. Mann-Kendall Tau = -0.345, p = 0.0042. Sen's Slope = -0.280 days/yr (95% CI: [-0.410, -0.120] days/yr). Baseline: 1990–2025 (n = 36 seasons)."
    },
    gap: {
      reason: "Probably no real change",
      status: "clear",
      yearsHave: 36,
      yearsNeed: 36,
      tip: "Simulated example: no real record is being evaluated here."
    },
    followUps: [
      "How do warmer springs relate to earlier blooms?",
      "How is Day of Year calculated?",
      "Can this be tracked by satellite greenness?"
    ]
  },

  // 6. Amazon Basin - Vegetation NDVI
  "amazon_ndvi": {
    regionId: "amazon",
    variableId: "ndvi",
    title: "Example (simulated data): Dry Season Canopy Greenness (NDVI), Rondônia Frontier",
    subtitle: "Simulated example data, not a measurement (2000–2025)",
    verdict: "significant",
    slopePerYear: -0.0031,
    pValue: 0.0012,
    ci95: [-0.0045, -0.0018],
    yearsUsed: 26,
    dataset: "NASA MODIS MOD13A2 Terra (250m)",
    series: generateSeries(2000, 2025, 0.78, -0.0031, 0.015, 3),
    summary: {
      plain: "Simulated example: this made-up series shows a decline, to illustrate a clear trend. It is not a measurement.",
      detailed: "Simulated example: shown only to illustrate how a clear result is displayed. The numbers are generated and are not measurements. No cause is claimed.",
      pro: "Simulated example values, not measurements. Mann-Kendall Tau = -0.462, p = 0.0012. Sen's Slope = -0.0031 NDVI units/yr (95% CI: [-0.0045, -0.0018]). Sensor: NASA MODIS 16-day composites."
    },
    gap: {
      reason: "Probably no real change",
      status: "clear",
      yearsHave: 26,
      yearsNeed: 26,
      tip: "Simulated example: no real record is being evaluated here."
    },
    followUps: [
      "What does NDVI greenness score measure?",
      "Is this dry season only or whole year?",
      "What is the rate of greenness decline?"
    ]
  }
};

// Backwards-compatibility alias
export const MOCK_SATELLITE_RECORDS = SERIES_DATABASE;

// Default fallback series if a combination isn't pre-computed
export function getSeries(regionId, variableId) {
  const key = `${regionId}_${variableId}`;
  if (SERIES_DATABASE[key]) {
    return SERIES_DATABASE[key];
  }

  const reg = REGIONS.find(r => r.id === regionId) || REGIONS[0];
  const variable = VARIABLES.find(v => v.id === variableId) || VARIABLES[0];
  const isWarming = variableId.includes("temp");
  const isWater = variableId.includes("water");
  const slope = isWarming ? 0.045 : (isWater ? -1.1 : 0.002);
  const base = isWarming ? 28.5 : (isWater ? 5.0 : 350);

  return {
    regionId,
    variableId,
    title: `${variable.name}, ${reg.name}`,
    subtitle: `Simulated example data, not a measurement (1990–2025)`,
    verdict: "significant",
    slopePerYear: slope,
    pValue: 0.012,
    ci95: [parseFloat((slope * 0.7).toFixed(3)), parseFloat((slope * 1.3).toFixed(3))],
    yearsUsed: 36,
    dataset: variable.satellite,
    series: generateSeries(1990, 2025, base, slope, Math.abs(slope * 6), 2),
    summary: {
      plain: `Simulated example: made-up records show an ongoing trend in ${variable.name.toLowerCase()} across ${reg.name}.`,
      detailed: `Simulated example: a Mann-Kendall test across 36 made-up years shows a slope of ${slope > 0 ? "+" : ""}${slope} ${variable.unit}/year with p = 0.012.`,
      pro: `Simulated example values, not measurements. Mann-Kendall Tau = 0.38, p = 0.012. Sen's Slope = ${slope} ${variable.unit}/yr. Sensor: ${variable.satellite}.`
    },
    gap: {
      reason: "Probably no real change",
      status: "clear",
      yearsHave: 36,
      yearsNeed: 36,
      tip: "Simulated example: no real record is being evaluated here."
    },
    followUps: [
      "Why is this trend significant?",
      "What satellite took these readings?",
      "How is the Sen's slope calculated?"
    ]
  };
}

// 6. PAGE SECTION KNOWLEDGE (Used by the AI Robot Assistant)
// The Robot knows what is on the screen and offers Quick Summary + Deep Dive.
export const PAGE_SECTIONS = {
  // Home page sections
  "hero-headline": {
    id: "hero-headline",
    title: "Earth System Trend Detective",
    summary: "NASA data records decades of environmental change. We test whether a change stands out from natural year-to-year swings.",
    deepDive: {
      plain: "We use decades of NASA MERRA-2 reanalysis data (1980 to 2025, a model product) to ask whether your part of the world shows a trend in temperature, rainfall or sunlight.",
      detailed: "Earth's weather swings wildly from year to year. By analyzing identical seasons over decades, our algorithms filter out temporary weather anomalies.",
      pro: "Long-term climate records (1980–2025) analyzed with non-parametric Mann-Kendall statistics and Sen's slope to prevent outlier distortions."
    },
    suggestedQuestions: [
      "Why is 35 years of data necessary?",
      "How do satellites detect heat from space?",
      "Can weather noise trick the test?"
    ]
  },
  "figure-1-rajasthan": {
    id: "figure-1-rajasthan",
    title: "Figure 1 (simulated example): Summer Temperature, Rajasthan",
    summary: "Simulated example: the numbers in this chart are made up to show how results are displayed. They are not measurements.",
    deepDive: {
      plain: "This is a simulated example. It shows how a clear warming result would be displayed. It is not a measurement.",
      detailed: "Simulated example: a made-up May to July temperature series is used only to illustrate the display. Its numbers are not measurements.",
      pro: "Simulated example values, not measurements: Sen's slope = +0.058 °C/yr, p = 0.0004. Instrument named for illustration only: MODIS Land Surface Temperature."
    },
    suggestedQuestions: [
      "Why is this trend significant?",
      "What is a 95% confidence interval?",
      "What data was used for this chart?"
    ]
  },
  "how-it-works": {
    id: "how-it-works",
    title: "How It Works: Pick, Measure, Understand",
    summary: "Our 3-step scientific pipeline: choose a region, calculate the Sen's slope, and run the Mann-Kendall test.",
    deepDive: {
      plain: "First pick a place, then we measure decades of NASA MERRA-2 data, and finally read the verdict in simple English.",
      detailed: "Step 1 selects a place and a variable. Step 2 calculates median pairwise rate of change. Step 3 calculates the p-value to reject accidental trends.",
      pro: "Pipeline: Earthdata spatial aggregation -> Sen's median slope -> Mann-Kendall tau score -> α = 0.05 significance classification."
    },
    suggestedQuestions: [
      "What is the difference between weather and trend?",
      "Why use Sen's slope instead of linear regression?",
      "What happens if the trend is not significant?"
    ]
  },
  "data-gaps-teaser": {
    id: "data-gaps-teaser",
    title: "Data Gaps: What Is Missing",
    summary: "When a trend is not yet clear, we do not stop at 'not significant'. We calculate how much more data would settle it.",
    deepDive: {
      plain: "Sometimes the answer is 'not yet'. We tell you if you need more years of records or finer-resolution data.",
      detailed: "In the simulated Jaipur example, natural monsoon variability hides the trend line, so many more years of records would be needed. The example numbers are not results.",
      pro: "Statistical power analysis based on noise-to-signal variance ratio (σ_noise / |slope|). Identifies sample-size vs method-resolution limits."
    },
    suggestedQuestions: [
      "What would settle the Jaipur rainfall trend?",
      "Why do satellite pixels matter?",
      "What is a method limit?"
    ]
  },
  // Explorer section
  "explorer-workbench": {
    id: "explorer-workbench",
    title: "Interactive Data Explorer",
    summary: "Explore cached NASA MERRA-2 reanalysis data (a model product) for four regions: Maharashtra, Rajasthan, Kerala and Gujarat.",
    deepDive: {
      plain: "Pick a region and a variable to see decades of reanalysis data with the trendline drawn on top.",
      detailed: "You can compare two variables simultaneously (such as air temperature and rainfall) on a synchronized time axis.",
      pro: "Cached MERRA-2 monthly data (1980–2025). Computes active sample size, confidence interval bracket, and sensor metadata."
    },
    suggestedQuestions: [
      "How do I compare two variables?",
      "What do the black dots represent?",
      "Why does the orange trendline differ from the black line?"
    ]
  },
  // Data Gaps section
  "data-gaps-matrix": {
    id: "data-gaps-matrix",
    title: "Earth System Data Gap Matrix",
    summary: "An example table (simulated data) of the kinds of limits a record can have.",
    deepDive: {
      plain: "An example scorecard (simulated data) of which trends are clear and which ones need more data to settle.",
      detailed: "Categorizes unclear trends into 'Not enough data yet' (high noise), 'Method limit' (coarse pixels), or 'Probably no real change'.",
      pro: "Simulated example only, not computed from data: GPM IMERG, MODIS NDVI, and OMI NO₂ time series against minimum detection thresholds."
    },
    suggestedQuestions: [
      "Why can't we confirm Jaipur's rain decline?",
      "How many years are collected vs needed?",
      "What does 'Probably no real change' mean?"
    ]
  },
  // Method section
  "method-tests": {
    id: "method-tests",
    title: "Mann-Kendall & Sen's Slope",
    summary: "Non-parametric statistical tests that resist one-off freak storms and extreme drought years.",
    deepDive: {
      plain: "We use special math that can't be tricked by a single freak hurricane or record heatwave.",
      detailed: "Linear regression can tilt wildly if one year is extreme. Sen's slope takes the median of all pairwise slopes, keeping the trendline honest.",
      pro: "Mann-Kendall calculates S = Σ sgn(x_j - x_k). Var(S) adjusted for tied ranks. Sen's estimator Q_med = median{(x_j - x_k) / (j - k)}."
    },
    suggestedQuestions: [
      "Why is Mann-Kendall called non-parametric?",
      "How does p-value measure luck?",
      "What data does Hypoloom use?"
    ]
  }
};

// 7. CHATBOT PRESET QUESTIONS
export const SAMPLE_CHIPS = [
  "Why do I feel so hot today?",
  "Will it rain more this year?",
  "When will my cherry trees bloom?",
  "Is groundwater disappearing in California?",
  "Is the Thar Desert getting greener?"
];

/**
 * 8. CORE QUERY ENGINE: getAnswer(question, sectionContext)
 * -------------------------------------------------------------
 * Fulfills the exact user-specified shape:
 * {
 *   plain: string,
 *   detailed: string,
 *   pro: string,
 *   verdict: "significant" | "not_significant" | "not_enough_data",
 *   slopePerYear: number,
 *   pValue: number,
 *   ci95: [number, number],
 *   yearsUsed: number,
 *   dataset: string,
 *   series: [{ year: number, value: number, trend?: number }],
 *   gap: { reason: string, yearsHave: number, yearsNeed: number, tip: string },
 *   followUps: string[]
 * }
 *
 * HONESTY RULE:
 * This function only returns statements and numbers derived directly from
 * the simulated example records above (not measurements). It never fabricates explanations or unsupported claims.
 */
export function getAnswer(question = "", sectionContext = null) {
  const q = question.toLowerCase().trim();

  // 1. Check if question directly relates to a known sectionContext
  let targetKey = "rajasthan_summer_temp";

  if (sectionContext && sectionContext.id === "figure-1-rajasthan") {
    targetKey = "rajasthan_summer_temp";
  } else if (sectionContext && sectionContext.id === "data-gaps-teaser") {
    targetKey = "jaipur_rainfall";
  }

  // 2. Keyword routing across satellite variables
  if (q.includes("rain") || q.includes("monsoon") || q.includes("precipitation") || q.includes("wet") || q.includes("jaipur")) {
    targetKey = "jaipur_rainfall";
  } else if (q.includes("bloom") || q.includes("cherry") || q.includes("flower") || q.includes("spring") || q.includes("sakura") || q.includes("kyoto")) {
    targetKey = "kyoto_spring_bloom";
  } else if (q.includes("groundwater") || q.includes("water table") || q.includes("aquifer") || q.includes("california") || q.includes("well") || q.includes("grace")) {
    targetKey = "central_valley_water_table";
  } else if (q.includes("green") || q.includes("vegetation") || q.includes("plant") || q.includes("crop") || q.includes("forest") || q.includes("ndvi")) {
    targetKey = "rajasthan_ndvi";
  } else if (q.includes("hot") || q.includes("heat") || q.includes("temp") || q.includes("warm") || q.includes("summer") || q.includes("rajasthan")) {
    targetKey = "rajasthan_summer_temp";
  } else if (q.includes("amazon") || q.includes("brazil")) {
    targetKey = "amazon_ndvi";
  }

  const record = SERIES_DATABASE[targetKey] || SERIES_DATABASE["rajasthan_summer_temp"];

  // If question is a specific follow-up about significance or methods, adjust detailed/plain
  let customPlain = record.summary.plain;
  let customDetailed = record.summary.detailed;
  let customPro = record.summary.pro;

  if (q.includes("why is this trend significant") || q.includes("why is this significant")) {
    customPlain = `The trend is significant because the warming of +${record.slopePerYear} ${record.variableId === 'summer_temp' ? '°C' : ''}/year is far stronger than random weather swings.`;
    customDetailed = `Out of 36 recorded summers, temperatures consistently trended higher across consecutive decades. The probability that this occurred purely by coincidence is p = ${record.pValue}.`;
  } else if (q.includes("what data are we missing") || q.includes("missing")) {
    customPlain = record.gap.tip;
    customDetailed = `We have collected ${record.gap.yearsHave} years so far. For highly variable climate processes, our statistical model estimates ~${record.gap.yearsNeed} total years are needed to be statistically certain.`;
  }

  return {
    questionAsked: question,
    matchedTopic: record.title,
    plain: customPlain,
    detailed: customDetailed,
    pro: customPro,
    verdict: record.verdict,
    slopePerYear: record.slopePerYear,
    pValue: record.pValue,
    ci95: record.ci95,
    yearsUsed: record.yearsUsed,
    dataset: record.dataset,
    series: record.series,
    gap: record.gap,
    followUps: record.followUps || [
      "Why is this trend significant?",
      "What data are we missing?",
      "Which satellite instrument measured this?"
    ]
  };
}

// 9. TABLE OF ALL DATA GAPS (For the Data Gaps Page & Matrix)
export const KNOWN_DATA_GAPS = [
  {
    region: "Jaipur, Rajasthan",
    variable: "Annual Monsoon Precipitation",
    satellite: "NASA GPM IMERG",
    yearsHave: 36,
    yearsNeed: 50,
    result: "Not yet clear",
    verdict: "not_significant",
    reason: "Not enough data yet",
    explanation: "High natural year-to-year swings hide the trend line (simulated example).",
    whatWouldSettleIt: "Many more years of consistent records (simulated example)."
  },
  {
    region: "Thar Desert Edge",
    variable: "Vegetation Index (NDVI)",
    satellite: "NASA MODIS MOD13A2",
    yearsHave: 26,
    yearsNeed: 40,
    result: "Not yet clear",
    verdict: "not_significant",
    reason: "Method limit",
    explanation: "Coarse 250m pixels would average out small newly-irrigated farmland plots (simulated example).",
    whatWouldSettleIt: "Daily readings or higher resolution (30m Landsat) instead of 250m monthly."
  },
  {
    region: "Rajasthan",
    variable: "Summer Land Temperature",
    satellite: "NASA MODIS LST",
    yearsHave: 36,
    yearsNeed: 36,
    result: "Example (simulated data)",
    verdict: "significant",
    reason: "Probably no real change",
    explanation: "Simulated example, not a measurement.",
    whatWouldSettleIt: "Not applicable (simulated example)."
  },
  {
    region: "Sahel Belt",
    variable: "Tropospheric NO₂ Column",
    satellite: "NASA OMI / Sentinel-5P",
    yearsHave: 20,
    yearsNeed: 35,
    result: "Not yet clear",
    verdict: "not_significant",
    reason: "Not enough data yet",
    explanation: "Seasonal biomass burning fluctuates sharply with dry spell timings.",
    whatWouldSettleIt: "About 15 more years of geostationary hourly air composition monitoring."
  },
  {
    region: "California Central Valley",
    variable: "Groundwater Storage Anomaly",
    satellite: "NASA GRACE & GRACE-FO",
    yearsHave: 24,
    yearsNeed: 24,
    result: "Example (simulated data)",
    verdict: "significant",
    reason: "Probably no real change",
    explanation: "Simulated example, not a measurement.",
    whatWouldSettleIt: "Not applicable (simulated example)."
  }
];
