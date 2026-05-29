import streamlit as st
import requests
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="🚕 TaxiFare NYC", page_icon="🚕", layout="wide")

# ── CSS + JS (Leaflet map + geocoding + rocket animation) ─────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=Syne+Mono&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<style>
  :root {
    --bg:      #0a0a0f;
    --surface: #13131a;
    --border:  #1e1e2e;
    --accent:  #f7c948;
    --accent2: #ff6b35;
    --text:    #e8e6f0;
    --muted:   #5a5870;
  }

  /* ── Reset ── */
  html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
  .stApp { background: var(--bg); color: var(--text); }
  .block-container { padding: 0 !important; max-width: 100% !important; }
  header { display: none !important; }
  footer { display: none !important; }
  section[data-testid="stSidebar"] { display: none; }

  /* ── Layout shell ── */
  #taxi-app {
    display: grid;
    grid-template-columns: 420px 1fr;
    grid-template-rows: 100vh;
    height: 100vh;
    overflow: hidden;
  }

  /* ── Left panel ── */
  #panel {
    background: var(--surface);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    padding: 2.5rem 2rem 2rem;
    gap: 0;
    position: relative;
    z-index: 10;
  }

  .brand {
    font-size: 1.7rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1;
    margin-bottom: 0.25rem;
  }
  .brand span { color: var(--accent); }
  .tagline {
    font-size: 0.75rem;
    color: var(--muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 2rem;
  }

  /* ── Section headers ── */
  .section-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 1.4rem 0 0.6rem;
  }

  /* ── Input fields ── */
  .input-group { position: relative; margin-bottom: 0.75rem; }
  .input-group label {
    display: block;
    font-size: 0.7rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
  }
  .input-group input {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    padding: 0.6rem 0.85rem;
    box-sizing: border-box;
    outline: none;
    transition: border-color 0.2s;
  }
  .input-group input:focus { border-color: var(--accent); }

  /* Suggestion dropdown */
  .suggestions {
    position: absolute;
    top: calc(100% + 2px);
    left: 0; right: 0;
    background: #1a1a28;
    border: 1px solid var(--border);
    border-radius: 8px;
    z-index: 9999;
    max-height: 180px;
    overflow-y: auto;
    display: none;
  }
  .suggestions.open { display: block; }
  .suggestion-item {
    padding: 0.55rem 0.85rem;
    font-size: 0.82rem;
    cursor: pointer;
    border-bottom: 1px solid var(--border);
    color: var(--text);
    transition: background 0.15s;
  }
  .suggestion-item:last-child { border-bottom: none; }
  .suggestion-item:hover { background: var(--border); }

  /* Row for two inputs */
  .input-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }

  /* ── Datetime row ── */
  .dt-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 0.75rem; }
  .dt-row input { width: 100%; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-family: 'Syne', sans-serif; font-size: 0.85rem; padding: 0.6rem 0.75rem; box-sizing: border-box; outline: none; transition: border-color 0.2s; }
  .dt-row input:focus { border-color: var(--accent); }
  .dt-row label { font-size: 0.7rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; display: block; margin-bottom: 0.3rem; }

  /* ── Passenger slider ── */
  .slider-wrap { margin-bottom: 1rem; }
  .slider-wrap label { font-size: 0.7rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; display: block; margin-bottom: 0.4rem; }
  .slider-row { display: flex; align-items: center; gap: 0.75rem; }
  .slider-row input[type=range] {
    flex: 1;
    -webkit-appearance: none;
    height: 3px;
    background: var(--border);
    border-radius: 2px;
    outline: none;
  }
  .slider-row input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 16px; height: 16px;
    background: var(--accent);
    border-radius: 50%;
    cursor: pointer;
  }
  .slider-val {
    font-family: 'Syne Mono', monospace;
    font-size: 1.1rem;
    color: var(--accent);
    min-width: 1.5rem;
    text-align: right;
  }

  /* ── Predict button ── */
  #predict-btn {
    margin-top: auto;
    padding-top: 1.5rem;
    width: 100%;
    background: var(--accent);
    color: #0a0a0f;
    border: none;
    border-radius: 10px;
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1rem;
    letter-spacing: 0.05em;
    padding: 0.85rem;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s, box-shadow 0.2s;
    box-shadow: 0 0 0 0 rgba(247,201,72,0);
  }
  #predict-btn:hover {
    background: #ffd740;
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(247,201,72,0.25);
  }
  #predict-btn:active { transform: translateY(0); }

  /* ── Result card ── */
  #result-card {
    background: linear-gradient(135deg, #1a1a28, #13131a);
    border: 1px solid var(--accent);
    border-radius: 14px;
    padding: 1.4rem;
    margin-top: 1.25rem;
    text-align: center;
    display: none;
    animation: fadeSlide 0.5s ease;
  }
  #result-card.visible { display: block; }
  @keyframes fadeSlide {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .result-label { font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); }
  .result-fare  { font-size: 3rem; font-weight: 800; color: var(--accent); line-height: 1.1; }
  .result-note  { font-size: 0.72rem; color: var(--muted); margin-top: 0.3rem; }

  /* ── Error card ── */
  #error-card {
    background: rgba(255,107,53,0.08);
    border: 1px solid var(--accent2);
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-top: 1rem;
    font-size: 0.82rem;
    color: var(--accent2);
    display: none;
  }
  #error-card.visible { display: block; }

  /* ── Map ── */
  #map-container { position: relative; width: 100%; height: 100vh; }
  #map { width: 100%; height: 100%; }

  /* ── Rocket overlay ── */
  #rocket-overlay {
    position: absolute;
    inset: 0;
    background: rgba(10,10,15,0.82);
    backdrop-filter: blur(6px);
    display: none;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  #rocket-overlay.visible { display: flex; }

  #rocket {
    font-size: 4rem;
    animation: launch 1.2s ease-in-out infinite alternate;
    filter: drop-shadow(0 0 20px rgba(247,201,72,0.6));
  }
  @keyframes launch {
    from { transform: translateY(20px) rotate(-5deg); }
    to   { transform: translateY(-30px) rotate(5deg); }
  }
  .rocket-trail {
    width: 4px;
    height: 60px;
    background: linear-gradient(to bottom, var(--accent), transparent);
    border-radius: 4px;
    margin-top: -8px;
    animation: trail 1.2s ease-in-out infinite alternate;
  }
  @keyframes trail {
    from { height: 20px; opacity: 0.3; }
    to   { height: 80px; opacity: 1; }
  }
  .rocket-label {
    margin-top: 1.5rem;
    font-size: 0.8rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    font-weight: 600;
    animation: pulse 1.5s ease-in-out infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
  }

  /* ── Map pin labels ── */
  .map-label { font-family: 'Syne', sans-serif; font-size: 0.75rem; font-weight: 600; }

  /* ── Scrollbar ── */
  #panel::-webkit-scrollbar { width: 4px; }
  #panel::-webkit-scrollbar-track { background: transparent; }
  #panel::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

  /* ── Coords display ── */
  .coords-display {
    font-family: 'Syne Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 0.3rem;
    height: 1em;
    transition: color 0.3s;
  }
  .coords-display.set { color: var(--accent); }
</style>

<div id="taxi-app">

  <!-- ── LEFT PANEL ── -->
  <div id="panel">
    <div class="brand">Taxi<span>Fare</span></div>
    <div class="tagline">NYC · Real-time fare prediction</div>

    <div class="section-label">Pickup</div>
    <div class="input-group" id="pickup-group">
      <label>Address</label>
      <input id="pickup-input" type="text" placeholder="e.g. Times Square, New York" autocomplete="off"/>
      <div class="suggestions" id="pickup-suggestions"></div>
    </div>
    <div class="coords-display" id="pickup-coords">— enter address to pin —</div>

    <div class="section-label">Drop-off</div>
    <div class="input-group" id="dropoff-group">
      <label>Address</label>
      <input id="dropoff-input" type="text" placeholder="e.g. JFK Airport, Queens" autocomplete="off"/>
      <div class="suggestions" id="dropoff-suggestions"></div>
    </div>
    <div class="coords-display" id="dropoff-coords">— enter address to pin —</div>

    <div class="section-label">When</div>
    <div class="dt-row">
      <div>
        <label>Date</label>
        <input type="date" id="ride-date"/>
      </div>
      <div>
        <label>Time</label>
        <input type="time" id="ride-time"/>
      </div>
    </div>

    <div class="section-label">Passengers</div>
    <div class="slider-wrap">
      <div class="slider-row">
        <input type="range" id="pax-slider" min="1" max="8" value="1"/>
        <div class="slider-val" id="pax-val">1</div>
      </div>
    </div>

    <button id="predict-btn" onclick="predictFare()">Predict Fare →</button>

    <div id="result-card">
      <div class="result-label">Estimated fare</div>
      <div class="result-fare" id="fare-amount">—</div>
      <div class="result-note">USD · excludes tips & tolls</div>
    </div>

    <div id="error-card"></div>
  </div>

  <!-- ── MAP ── -->
  <div id="map-container">
    <div id="map"></div>
    <div id="rocket-overlay">
      <div id="rocket">🚀</div>
      <div class="rocket-trail"></div>
      <div class="rocket-label">Computing fare…</div>
    </div>
  </div>
</div>

<script>
// ── State ──────────────────────────────────────────────────────────────────
const state = {
  pickup:  { lat: null, lon: null },
  dropoff: { lat: null, lon: null },
};

// ── Map init ───────────────────────────────────────────────────────────────
const map = L.map('map', { zoomControl: false }).setView([40.75, -73.98], 12);
L.control.zoom({ position: 'bottomright' }).addTo(map);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
  attribution: '© OpenStreetMap © CARTO',
  maxZoom: 19
}).addTo(map);

// ── Custom markers ─────────────────────────────────────────────────────────
function makeIcon(color, emoji) {
  return L.divIcon({
    className: '',
    html: `<div style="
      background:${color};width:32px;height:32px;border-radius:50% 50% 50% 0;
      transform:rotate(-45deg);border:3px solid #0a0a0f;
      display:flex;align-items:center;justify-content:center;
      box-shadow:0 4px 12px rgba(0,0,0,0.5)">
      <span style="transform:rotate(45deg);font-size:14px">${emoji}</span>
    </div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
  });
}

let pickupMarker = null, dropoffMarker = null, routeLine = null;

function setMarker(type, lat, lon, label) {
  if (type === 'pickup') {
    if (pickupMarker) map.removeLayer(pickupMarker);
    pickupMarker = L.marker([lat, lon], { icon: makeIcon('#f7c948','📍') })
      .bindTooltip(`<span class="map-label">Pickup: ${label}</span>`, { permanent: false })
      .addTo(map);
    state.pickup = { lat, lon };
    document.getElementById('pickup-coords').textContent = `${lat.toFixed(5)}, ${lon.toFixed(5)}`;
    document.getElementById('pickup-coords').classList.add('set');
  } else {
    if (dropoffMarker) map.removeLayer(dropoffMarker);
    dropoffMarker = L.marker([lat, lon], { icon: makeIcon('#ff6b35','🏁') })
      .bindTooltip(`<span class="map-label">Drop-off: ${label}</span>`, { permanent: false })
      .addTo(map);
    state.dropoff = { lat, lon };
    document.getElementById('dropoff-coords').textContent = `${lat.toFixed(5)}, ${lon.toFixed(5)}`;
    document.getElementById('dropoff-coords').classList.add('set');
  }
  drawRoute();
  fitMap();
}

function drawRoute() {
  if (routeLine) map.removeLayer(routeLine);
  if (state.pickup.lat && state.dropoff.lat) {
    routeLine = L.polyline(
      [[state.pickup.lat, state.pickup.lon], [state.dropoff.lat, state.dropoff.lon]],
      { color: '#f7c948', weight: 2.5, dashArray: '8 6', opacity: 0.7 }
    ).addTo(map);
  }
}

function fitMap() {
  const pts = [];
  if (state.pickup.lat)  pts.push([state.pickup.lat,  state.pickup.lon]);
  if (state.dropoff.lat) pts.push([state.dropoff.lat, state.dropoff.lon]);
  if (pts.length === 2) map.fitBounds(pts, { padding: [80, 80] });
  else if (pts.length === 1) map.setView(pts[0], 14);
}

// ── Geocoding (Nominatim) ──────────────────────────────────────────────────
let debounceTimers = {};

function setupAutocomplete(inputId, suggestionsId, type) {
  const input = document.getElementById(inputId);
  const box   = document.getElementById(suggestionsId);

  input.addEventListener('input', () => {
    clearTimeout(debounceTimers[type]);
    const q = input.value.trim();
    if (q.length < 3) { box.classList.remove('open'); return; }
    debounceTimers[type] = setTimeout(() => geocodeSearch(q, box, type), 350);
  });

  document.addEventListener('click', (e) => {
    if (!input.contains(e.target) && !box.contains(e.target)) box.classList.remove('open');
  });
}

async function geocodeSearch(query, box, type) {
  try {
    const r = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&addressdetails=0`,
      { headers: { 'Accept-Language': 'en' } }
    );
    const results = await r.json();
    box.innerHTML = '';
    if (!results.length) { box.classList.remove('open'); return; }
    results.forEach(item => {
      const el = document.createElement('div');
      el.className = 'suggestion-item';
      el.textContent = item.display_name;
      el.addEventListener('click', () => {
        document.getElementById(type === 'pickup' ? 'pickup-input' : 'dropoff-input').value = item.display_name;
        box.classList.remove('open');
        setMarker(type, parseFloat(item.lat), parseFloat(item.lon), item.display_name.split(',')[0]);
      });
      box.appendChild(el);
    });
    box.classList.add('open');
  } catch(e) { console.error(e); }
}

setupAutocomplete('pickup-input',  'pickup-suggestions',  'pickup');
setupAutocomplete('dropoff-input', 'dropoff-suggestions', 'dropoff');

// ── Datetime defaults ──────────────────────────────────────────────────────
const now = new Date();
document.getElementById('ride-date').value = now.toISOString().split('T')[0];
document.getElementById('ride-time').value = now.toTimeString().slice(0,5);

// ── Slider ─────────────────────────────────────────────────────────────────
const slider = document.getElementById('pax-slider');
const paxVal = document.getElementById('pax-val');
slider.addEventListener('input', () => { paxVal.textContent = slider.value; });

// ── Predict ────────────────────────────────────────────────────────────────
async function predictFare() {
  const errorCard  = document.getElementById('error-card');
  const resultCard = document.getElementById('result-card');
  errorCard.classList.remove('visible');
  resultCard.classList.remove('visible');

  if (!state.pickup.lat || !state.dropoff.lat) {
    showError('Please pin both a pickup and a drop-off location.');
    return;
  }

  const date = document.getElementById('ride-date').value;
  const time = document.getElementById('ride-time').value;
  if (!date || !time) { showError('Please select date and time.'); return; }

  const params = new URLSearchParams({
    pickup_datetime:   `${date} ${time}:00`,
    pickup_longitude:   state.pickup.lon,
    pickup_latitude:    state.pickup.lat,
    dropoff_longitude:  state.dropoff.lon,
    dropoff_latitude:   state.dropoff.lat,
    passenger_count:    slider.value,
  });

  const overlay = document.getElementById('rocket-overlay');
  overlay.classList.add('visible');

  try {
    const res = await fetch(`https://taxifare-203500939035.europe-west1.run.app/predict?${params}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const fare = data.fare ?? data.prediction;
    if (fare == null) throw new Error('Unexpected response format');
    document.getElementById('fare-amount').textContent = `$${parseFloat(fare).toFixed(2)}`;
    resultCard.classList.add('visible');
  } catch(e) {
    showError(`API error: ${e.message}`);
  } finally {
    overlay.classList.remove('visible');
  }
}

function showError(msg) {
  const el = document.getElementById('error-card');
  el.textContent = '⚠ ' + msg;
  el.classList.add('visible');
}
</script>
""", unsafe_allow_html=True)
