export async function fetchSeries(dataset, region = 'maharashtra') {
  const res = await fetch(`/api/ui/analysis?dataset=${dataset}&region=${region}`)
  if (!res.ok) throw new Error(`analysis failed: ${res.status}`)
  return res.json()
}

export async function askQuestion(question, level = 'plain', region = 'maharashtra') {
  const res = await fetch('/api/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, level, region })
  })
  if (!res.ok) throw new Error(`ask failed: ${res.status}`)
  return res.json()
}

// Boxes are rough project choices, not official boundaries.
export const LIVE_REGIONS = [
  { id: 'maharashtra', name: 'Maharashtra, India (live)', desc: 'Approximate box 72-80 E, 16-21 N' },
  { id: 'rajasthan', name: 'Rajasthan, India (live)', desc: 'Approximate box 69.5-78 E, 23-30 N' },
  { id: 'kerala', name: 'Kerala, India (live)', desc: 'Approximate box 74.8-77.5 E, 8.2-12.8 N' },
  { id: 'gujarat', name: 'Gujarat, India (live)', desc: 'Approximate box 68-74.5 E, 20-24.7 N' }
]

const SAT = 'NASA MERRA-2 reanalysis (model product)'
const RES = 'Regional monthly mean, 1980-2025'

export const LIVE_VARIABLES = [
  { id: 'T2M', name: 'Air temperature (mean)', unit: 'K', satellite: SAT, resolution: RES,
    description: 'Monthly mean 2 m air temperature, seasonal cycle removed.' },
  { id: 'T2M_MIN', name: 'Night air temperature', unit: 'K', satellite: SAT, resolution: RES,
    description: 'Monthly mean of the daily minimum 2 m air temperature, seasonal cycle removed.' },
  { id: 'T2M_MAX', name: 'Day air temperature', unit: 'K', satellite: SAT, resolution: RES,
    description: 'Monthly mean of the daily maximum 2 m air temperature, seasonal cycle removed.' },
  { id: 'PRECIP', name: 'Rainfall', unit: 'mm/day', satellite: SAT, resolution: RES,
    description: 'Corrected precipitation, seasonal cycle removed. Treat as a candidate: possible product discontinuity after 2006.' },
  { id: 'SUNLIGHT', name: 'Sunlight at the surface', unit: 'W m-2', satellite: SAT, resolution: RES,
    description: 'Downward shortwave radiation at the surface, seasonal cycle removed. Experimental.' }
]