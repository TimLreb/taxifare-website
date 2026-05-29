import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="TaxiFare NYC", page_icon="🚕", layout="wide")

st.markdown("""
<style>
  header, footer, #MainMenu { display: none !important; }
  .stApp { overflow: hidden; }
  .block-container { padding: 0 !important; max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)

components.html("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Syne+Mono&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:       #0b0b10;
  --surface:  #111118;
  --surface2: #16161f;
  --border:   #21212e;
  --accent:   #f7c948;
  --orange:   #ff6b35;
  --green:    #5ddb8e;
  --text:     #eceaf4;
  --muted:    #52506a;
  --ROCKET_DURATION: 2s;
}

html, body { height: 100%; width: 100%; font-family: 'Syne', sans-serif;
  background: var(--bg); color: var(--text); overflow: hidden; }

#app { display: grid; grid-template-columns: 520px 1fr; height: 100vh; }

/* ── MOBILE ── */
@media (max-width: 768px) {
  #app {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
    height: 100dvh;
  }
  #panel {
    padding: 1.1rem 1.1rem 1rem;
    max-height: 55dvh;
    border-right: none;
    border-bottom: 1px solid var(--border);
  }
  #map-wrap { min-height: 0; }
  #map { height: 100%; min-height: 200px; }
  .brand { font-size: 1.4rem; }
  .tagline { font-size: 0.62rem; margin-bottom: 0.9rem; }
  .lbl { font-size: 0.62rem; margin-bottom: 0.45rem; }
  .click-mode-bar { gap: 0.4rem; margin-bottom: 0.7rem; }
  .mode-btn { font-size: 0.7rem; padding: 0.42rem 0.5rem; }
  .mode-hint { font-size: 0.64rem; margin-bottom: 0.55rem; }
  .loc-block { gap: 0.6rem; }
  .loc-dot { width: 10px; height: 10px; }
  .field input[type=text] { font-size: 0.88rem; padding: 0.55rem 0.75rem; }
  .coord-chip { font-size: 0.66rem; }
  .row2 { gap: 0.5rem; margin-bottom: 0.7rem; }
  .row2 input[type=date], .row2 input[type=time] { font-size: 0.85rem; padding: 0.5rem 0.65rem; }
  .mini-lbl { font-size: 0.6rem; }
  .slider-row { gap: 0.6rem; }
  .pax-val { font-size: 0.95rem; }
  #btn { font-size: 0.9rem; padding: 0.72rem; border-radius: 9px; }
  .divider { margin: 0.8rem 0; }
  .spacer { min-height: 0.5rem; }
  #result { margin-top: 0.8rem; }
  .fare-hero { padding: 0.85rem 1rem 0.75rem; }
  .fare-amt { font-size: 2.3rem; }
  .fare-note { font-size: 0.65rem; }
  .fare-taxi { font-size: 1.7rem; }
  .stat-cell { padding: 0.65rem 0.9rem; }
  .stat-val { font-size: 0.9rem; }
  .time-row { padding: 0.65rem 0.9rem; }
  .time-val { font-size: 0.95rem; }
  #map-hint { bottom: 1rem; font-size: 0.72rem; }
}

/* ── Panel ── */
#panel {
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex; flex-direction: column;
  padding: 2rem 2rem 1.8rem;
  overflow-y: auto; overflow-x: hidden;
  position: relative; z-index: 10;
}
#panel::-webkit-scrollbar { width: 3px; }
#panel::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* brand */
.brand { font-size: 1.9rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1; }
.brand em { color: var(--accent); font-style: normal; }
.tagline { font-size: 0.72rem; color: var(--muted); letter-spacing: 0.16em;
  text-transform: uppercase; margin-top: 0.25rem; margin-bottom: 1.8rem; }

.divider { height: 1px; background: var(--border); margin: 1.2rem 0; }

.lbl { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.22em;
  text-transform: uppercase; color: var(--muted); margin-bottom: 0.6rem; }

/* ── Click mode toggle ── */
.click-mode-bar {
  display: flex; gap: 0.5rem; margin-bottom: 1rem;
}
.mode-btn {
  flex: 1; padding: 0.5rem 0.6rem;
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: 8px; color: var(--muted); font-family: 'Syne', sans-serif;
  font-size: 0.75rem; font-weight: 600; letter-spacing: 0.05em;
  cursor: pointer; transition: all 0.18s; text-align: center;
}
.mode-btn:hover { border-color: var(--accent); color: var(--text); }
.mode-btn.active-pu  { background: rgba(247,201,72,0.1);  border-color: var(--accent); color: var(--accent); }
.mode-btn.active-do  { background: rgba(255,107,53,0.1);  border-color: var(--orange); color: var(--orange); }
.mode-hint {
  font-size: 0.68rem; color: var(--muted); margin-bottom: 0.8rem;
  min-height: 1rem; transition: color 0.2s;
  font-style: italic;
}
.mode-hint.pu { color: var(--accent); }
.mode-hint.do { color: var(--orange); }

/* location block */
.loc-block { display: flex; align-items: flex-start; gap: 0.9rem; }
.loc-dot-wrap { display: flex; flex-direction: column; align-items: center; padding-top: 0.7rem; flex-shrink: 0; }
.loc-dot { width: 12px; height: 12px; border-radius: 50%; border: 2.5px solid var(--accent); background: transparent; }
.loc-dot.orange { border-color: var(--orange); }
.loc-connector { width: 1px; flex: 1; min-height: 36px; background: var(--border); margin: 4px 0; }
.loc-inputs { flex: 1; min-width: 0; }

/* inputs */
.field { position: relative; }
.field input[type=text] {
  width: 100%; background: var(--surface2);
  border: 1px solid var(--border); border-radius: 10px;
  color: var(--text); font-family: 'Syne', sans-serif;
  font-size: 1rem; padding: 0.68rem 0.9rem;
  outline: none; transition: border-color 0.2s, box-shadow 0.2s;
}
.field input[type=text]::placeholder { color: var(--muted); font-size: 0.92rem; }
.field input[type=text]:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(247,201,72,0.07);
}

/* coord chip */
.coord-chip {
  font-family: 'Syne Mono', monospace; font-size: 0.74rem;
  color: var(--muted); margin-top: 0.32rem; margin-bottom: 0;
  min-height: 1rem; transition: color 0.3s;
}
.coord-chip.set { color: var(--green); }

/* dropdown */
.drop {
  position: absolute; top: calc(100% + 4px); left: 0; right: 0;
  background: #13131e; border: 1px solid var(--border); border-radius: 10px;
  z-index: 9999; max-height: 200px; overflow-y: auto; display: none;
  box-shadow: 0 12px 32px rgba(0,0,0,0.6);
}
.drop.open { display: block; }
.drop-item {
  padding: 0.55rem 0.85rem; font-size: 0.85rem; cursor: pointer;
  border-bottom: 1px solid var(--border); color: var(--text);
  transition: background 0.1s; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis;
}
.drop-item:last-child { border-bottom: none; }
.drop-item:hover { background: var(--border); }

/* two-col row */
.row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0.7rem; margin-bottom: 0.9rem; }
.mini-lbl { font-size: 0.66rem; font-weight: 700; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--muted); margin-bottom: 0.35rem; }
.row2 input[type=date], .row2 input[type=time] {
  width: 100%; background: var(--surface2); border: 1px solid var(--border);
  border-radius: 10px; color: var(--text); font-family: 'Syne', sans-serif;
  font-size: 0.95rem; padding: 0.62rem 0.8rem; outline: none;
  transition: border-color 0.2s; color-scheme: dark;
}
.row2 input:focus { border-color: var(--accent); }

/* slider */
.slider-row { display: flex; align-items: center; gap: 0.85rem; }
input[type=range] {
  flex: 1; -webkit-appearance: none; height: 3px;
  background: var(--border); border-radius: 2px; outline: none; cursor: pointer;
}
input[type=range]::-webkit-slider-thumb {
  -webkit-appearance: none; width: 18px; height: 18px;
  background: var(--accent); border-radius: 50%; cursor: pointer; transition: transform 0.15s;
}
input[type=range]::-webkit-slider-thumb:hover { transform: scale(1.25); }
.pax-val { font-family: 'Syne Mono', monospace; font-size: 1.1rem;
  color: var(--accent); min-width: 1.4rem; text-align: right; }

.spacer { flex: 1; min-height: 1rem; }

/* predict button */
#btn {
  width: 100%; background: var(--accent); color: #0b0b10;
  border: none; border-radius: 11px; font-family: 'Syne', sans-serif;
  font-weight: 800; font-size: 1rem; letter-spacing: 0.04em;
  padding: 0.88rem; cursor: pointer;
  transition: background 0.2s, transform 0.12s, box-shadow 0.2s;
}
#btn:hover { background: #ffd740; transform: translateY(-2px); box-shadow: 0 8px 28px rgba(247,201,72,0.2); }
#btn:active { transform: translateY(0); box-shadow: none; }

/* ── Result card ── */
#result {
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: 13px; margin-top: 1.1rem; overflow: hidden;
  display: none; animation: pop 0.35s cubic-bezier(0.34,1.56,0.64,1);
}
#result.on { display: block; }
@keyframes pop {
  from { opacity:0; transform:scale(0.94) translateY(6px); }
  to   { opacity:1; transform:scale(1) translateY(0); }
}
.fare-hero {
  padding: 1.2rem 1.3rem 1rem;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
}
.fare-lbl { font-size: 0.62rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--muted); }
.fare-amt { font-size: 3rem; font-weight: 800; color: var(--accent); line-height: 1; margin-top: 0.1rem; }
.fare-note { font-size: 0.7rem; color: var(--muted); margin-top: 0.18rem; }
.fare-taxi { font-size: 2.2rem; opacity: 0.45; }

.stats-grid { display: grid; grid-template-columns: 1fr 1fr; border-bottom: 1px solid var(--border); }
.stat-cell { padding: 0.85rem 1.2rem; border-right: 1px solid var(--border); }
.stat-cell:nth-child(even) { border-right: none; }
.stat-lbl { font-size: 0.61rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); margin-bottom: 0.24rem; }
.stat-val { font-family: 'Syne Mono', monospace; font-size: 1.05rem; font-weight: 600; color: var(--text); }
.stat-val.accent { color: var(--accent); }

.time-row { display: flex; align-items: center; justify-content: space-between; padding: 0.85rem 1.2rem; }
.time-item { text-align: center; }
.time-lbl { font-size: 0.61rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); margin-bottom: 0.2rem; }
.time-val { font-family: 'Syne Mono', monospace; font-size: 1.1rem; font-weight: 600; color: var(--text); }
.time-arrow { font-size: 1rem; color: var(--muted); }

/* error */
#err {
  background: rgba(255,107,53,0.07); border: 1px solid var(--orange);
  border-radius: 9px; padding: 0.75rem 0.9rem; margin-top: 0.9rem;
  font-size: 0.82rem; color: var(--orange); display: none;
}
#err.on { display: block; }

/* ── Map cursor states ── */
#map-wrap { position: relative; overflow: hidden; }
#map { width: 100%; height: 100vh; }
#map.cursor-pu  { cursor: crosshair; }
#map.cursor-do  { cursor: crosshair; }

/* map click hint overlay */
#map-hint {
  position: absolute; bottom: 2rem; left: 50%; transform: translateX(-50%);
  background: rgba(11,11,16,0.85); backdrop-filter: blur(8px);
  border: 1px solid var(--border); border-radius: 50px;
  padding: 0.5rem 1.2rem; font-size: 0.78rem; color: var(--text);
  pointer-events: none; white-space: nowrap;
  opacity: 0; transition: opacity 0.3s; z-index: 500;
}
#map-hint.show { opacity: 1; }
#map-hint .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%;
  margin-right: 0.4rem; vertical-align: middle; }

/* ── Rocket overlay ── */
#rocket-wrap {
  position: absolute; inset: 0;
  background: rgba(8,8,14,0.85); backdrop-filter: blur(10px);
  display: none; flex-direction: column;
  align-items: center; justify-content: center; z-index: 2000;
  overflow: hidden;
}
#rocket-wrap.on { display: flex; }

#rocket-scene {
  display: flex; flex-direction: column; align-items: center;
}
#rocket-scene.launch {
  animation: rocketLaunch 2s ease-in forwards;
}
@keyframes rocketLaunch {
  0%   { transform: translateY(0)     rotate(0deg)   scale(1);    opacity: 1; }
  30%  { transform: translateY(-20px)  rotate(-4deg)  scale(1.08); opacity: 1; }
  65%  { transform: translateY(-120px) rotate(3deg)   scale(1.05); opacity: 0.8; }
  100% { transform: translateY(-600px) rotate(0deg)   scale(0.5);  opacity: 0; }
}

#rocket {
  font-size: 4rem;
  filter: drop-shadow(0 0 28px rgba(247,201,72,0.65));
  animation: hover 1.2s ease-in-out infinite alternate;
}
#rocket-scene.launch #rocket { animation: none; }

@keyframes hover {
  from { transform: translateY(8px) rotate(-5deg) scale(0.97); }
  to   { transform: translateY(-8px) rotate(5deg) scale(1.03); }
}

.trail {
  width: 3px; border-radius: 3px; margin-top: -4px;
  background: linear-gradient(to bottom, var(--accent), transparent);
  animation: trailPulse 1.2s ease-in-out infinite alternate;
}
#rocket-scene.launch .trail { animation: trailGrow 2s ease-in forwards; }
@keyframes trailPulse { from{height:14px;opacity:0.25;} to{height:65px;opacity:0.9;} }
@keyframes trailGrow  { 0%{height:40px;opacity:0.8;} 50%{height:150px;opacity:1;} 100%{height:350px;opacity:0;} }

.rocket-txt {
  margin-top: 1.5rem; font-size: 0.74rem; letter-spacing: 0.24em;
  text-transform: uppercase; color: var(--accent); font-weight: 700;
  animation: blink 1.3s ease-in-out infinite;
}
#rocket-scene.launch .rocket-txt { animation: fadeOut 0.6s ease 1.2s forwards; }
@keyframes blink    { 0%,100%{opacity:0.35;} 50%{opacity:1;} }
@keyframes fadeOut  { to{opacity:0;} }

.stars { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
.star  { position: absolute; background: white; border-radius: 50%; animation: fall linear infinite; }
@keyframes fall { from{transform:translateY(-10px);opacity:0;} 10%{opacity:1;} to{transform:translateY(110vh);opacity:0;} }

/* Leaflet */
.leaflet-tooltip {
  font-family: 'Syne', sans-serif; font-size: 0.74rem; font-weight: 600;
  background: #111118; border: 1px solid #21212e; color: #eceaf4;
  box-shadow: 0 4px 12px rgba(0,0,0,0.4); border-radius: 6px;
}
.leaflet-tooltip::before { display: none; }
</style>
</head>
<body>
<div id="app">

  <!-- ── PANEL ── -->
  <div id="panel">
    <div class="brand">Taxi<em>Fare</em></div>
    <div class="tagline">NYC · Real-time prediction</div>

    <div class="lbl">Route</div>

    <!-- Click mode toggles -->
    <div class="click-mode-bar">
      <div class="mode-btn" id="btn-pu" onclick="setClickMode('pu')">📍 Click pickup on map</div>
      <div class="mode-btn" id="btn-do" onclick="setClickMode('do')">🏁 Click drop-off on map</div>
    </div>
    <div class="mode-hint" id="mode-hint">Or type an address below</div>

    <!-- Address inputs -->
    <div class="loc-block">
      <div class="loc-dot-wrap">
        <div class="loc-dot"></div>
        <div class="loc-connector"></div>
        <div class="loc-dot orange"></div>
      </div>
      <div class="loc-inputs">
        <div class="field" style="margin-bottom:0.42rem">
          <input id="pu-input" type="text" placeholder="Pickup address…" autocomplete="off"/>
          <div class="drop" id="pu-drop"></div>
        </div>
        <div class="coord-chip" id="pu-coords">—</div>
        <div class="field" style="margin-top:0.65rem">
          <input id="do-input" type="text" placeholder="Drop-off address…" autocomplete="off"/>
          <div class="drop" id="do-drop"></div>
        </div>
        <div class="coord-chip" id="do-coords">—</div>
      </div>
    </div>

    <div class="divider"></div>

    <div class="lbl">When</div>
    <div class="row2">
      <div><div class="mini-lbl">Date</div><input type="date" id="r-date"/></div>
      <div><div class="mini-lbl">Time</div><input type="time" id="r-time"/></div>
    </div>

    <div class="divider"></div>

    <div class="lbl">Passengers</div>
    <div class="slider-row" style="margin-bottom:0.9rem">
      <input type="range" id="pax" min="1" max="8" value="1"/>
      <div class="pax-val" id="pax-val">1</div>
    </div>

    <div class="spacer"></div>

    <button id="btn" onclick="predict()">Predict Fare →</button>

    <div id="result">
      <div class="fare-hero">
        <div>
          <div class="fare-lbl">Estimated Fare</div>
          <div class="fare-amt" id="fare-amt">—</div>
          <div class="fare-note">USD · excl. tips &amp; tolls</div>
        </div>
        <div class="fare-taxi">🚕</div>
      </div>
      <div class="stats-grid">
        <div class="stat-cell">
          <div class="stat-lbl">Distance</div>
          <div class="stat-val accent" id="stat-dist">—</div>
        </div>
        <div class="stat-cell">
          <div class="stat-lbl">Duration</div>
          <div class="stat-val" id="stat-dur">—</div>
        </div>
      </div>
      <div class="time-row">
        <div class="time-item">
          <div class="time-lbl">Departure</div>
          <div class="time-val" id="t-depart">—</div>
        </div>
        <div class="time-arrow">→</div>
        <div class="time-item">
          <div class="time-lbl">Arrival</div>
          <div class="time-val" id="t-arrive">—</div>
        </div>
      </div>
    </div>

    <div id="err"></div>
  </div>

  <!-- ── MAP ── -->
  <div id="map-wrap">
    <div id="map"></div>
    <div id="map-hint"></div>
    <div id="rocket-wrap">
      <div class="stars" id="stars"></div>
      <div id="rocket-scene">
        <div id="rocket">🚀</div>
        <div class="trail"></div>
        <div class="rocket-txt">Computing fare…</div>
      </div>
    </div>
  </div>

</div>
<script>
// ── Stars ──────────────────────────────────────────────────────────────────
(function(){
  const c=document.getElementById('stars');
  for(let i=0;i<60;i++){
    const s=document.createElement('div'); s.className='star';
    const sz=Math.random()*2.5+0.5;
    s.style.cssText=`width:${sz}px;height:${sz}px;left:${Math.random()*100}%;animation-duration:${Math.random()*2+1.5}s;animation-delay:${Math.random()*4}s;opacity:0;`;
    c.appendChild(s);
  }
})();

// ── State ──────────────────────────────────────────────────────────────────
const S = { pu:{lat:null,lon:null}, do:{lat:null,lon:null} };
let clickMode = null; // 'pu' | 'do' | null

// ── Map ────────────────────────────────────────────────────────────────────
const map = L.map('map',{zoomControl:false}).setView([40.75,-73.97],12);
L.control.zoom({position:'bottomright'}).addTo(map);
map.on('zoomend moveend', () => map.invalidateSize());
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{
  attribution:'© OpenStreetMap © CARTO', maxZoom:19
}).addTo(map);

function mkIcon(color, emoji) {
  return L.divIcon({
    className:'',
    html:`<div style="background:${color};width:32px;height:32px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:3px solid #0b0b10;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(0,0,0,0.6)"><span style="transform:rotate(45deg);font-size:14px">${emoji}</span></div>`,
    iconSize:[32,32], iconAnchor:[16,32]
  });
}

let markers={pu:null,do:null}, routeLayers=[], straightLine=null;

function clearRoute() {
  routeLayers.forEach(l=>map.removeLayer(l));
  routeLayers=[];
  if(straightLine){map.removeLayer(straightLine);straightLine=null;}
}

function pin(type, lat, lon, label) {
  if(markers[type]) map.removeLayer(markers[type]);
  const cfg=type==='pu'
    ?{color:'#f7c948',emoji:'📍',tip:'Pickup'}
    :{color:'#ff6b35',emoji:'🏁',tip:'Drop-off'};
  markers[type]=L.marker([lat,lon],{icon:mkIcon(cfg.color,cfg.emoji)})
    .bindTooltip(cfg.tip+(label?': '+label:''),{permanent:false})
    .addTo(map);
  S[type]={lat,lon};
  const chip=document.getElementById(type+'-coords');
  chip.textContent=lat.toFixed(5)+'   '+lon.toFixed(5);
  chip.classList.add('set');
  clearRoute();
  if(S.pu.lat&&S.do.lat){
    straightLine=L.polyline([[S.pu.lat,S.pu.lon],[S.do.lat,S.do.lon]],{
      color:'#f7c948',weight:2,dashArray:'6 5',opacity:0.35
    }).addTo(map);
  }
  fitBounds();
}

function fitBounds() {
  const pts=[];
  if(S.pu.lat) pts.push([S.pu.lat,S.pu.lon]);
  if(S.do.lat) pts.push([S.do.lat,S.do.lon]);
  if(pts.length===2) map.fitBounds(pts,{padding:[80,80]});
  else if(pts.length===1) map.setView(pts[0],14);
}

function drawRoute(coords) {
  clearRoute();
  const glow=L.polyline(coords,{color:'#f7c948',weight:10,opacity:0.1}).addTo(map);
  const line=L.polyline(coords,{color:'#f7c948',weight:3.5,opacity:0.92}).addTo(map);
  routeLayers.push(glow,line);
  map.fitBounds(line.getBounds(),{padding:[70,70]});
}

// ── Click mode ─────────────────────────────────────────────────────────────
const mapEl    = document.getElementById('map');
const hintEl   = document.getElementById('map-hint');
const btnPu    = document.getElementById('btn-pu');
const btnDo    = document.getElementById('btn-do');
const hintMsgEl= document.getElementById('mode-hint');

function setClickMode(mode) {
  if(clickMode===mode){ // toggle off
    clickMode=null;
    mapEl.className='';
    btnPu.classList.remove('active-pu');
    btnDo.classList.remove('active-do');
    hintEl.classList.remove('show');
    hintMsgEl.textContent='Or type an address below';
    hintMsgEl.className='mode-hint';
    return;
  }
  clickMode=mode;
  mapEl.className='cursor-'+mode;
  btnPu.classList.toggle('active-pu', mode==='pu');
  btnDo.classList.toggle('active-do', mode==='do');
  const isPu=mode==='pu';
  hintEl.innerHTML=`<span class="dot" style="background:${isPu?'#f7c948':'#ff6b35'}"></span>`
    +(isPu?'Click on the map to set <strong>pickup</strong>':'Click on the map to set <strong>drop-off</strong>');
  hintEl.classList.add('show');
  hintMsgEl.textContent=isPu?'👆 Now click your pickup on the map':'👆 Now click your drop-off on the map';
  hintMsgEl.className='mode-hint '+(isPu?'pu':'do');
}

map.on('click', async function(e){
  if(!clickMode) return;
  const {lat,lng}=e.latlng;
  const type=clickMode;

  // Reverse geocode for a readable label
  let label='';
  try {
    const r=await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`,
      {headers:{'Accept-Language':'en'}});
    const d=await r.json();
    label=d.display_name||'';
    const inputEl=document.getElementById(type+'-input');
    inputEl.value=label.split(',').slice(0,2).join(',');
  } catch(e){}

  pin(type, lat, lng, label.split(',')[0]);

  // Auto-advance: after picking pickup, switch to drop-off mode
  if(type==='pu' && !S.do.lat){
    setClickMode('do');
  } else {
    // both set — exit mode
    clickMode=null;
    mapEl.className='';
    btnPu.classList.remove('active-pu');
    btnDo.classList.remove('active-do');
    hintEl.classList.remove('show');
    hintMsgEl.textContent='Both pins set — ready to predict!';
    hintMsgEl.className='mode-hint';
    setTimeout(()=>{ hintMsgEl.textContent='Or type an address below'; },3000);
  }
});

// ── OSRM routing ───────────────────────────────────────────────────────────
async function getRoute() {
  const url=`https://router.project-osrm.org/route/v1/driving/`
    +`${S.pu.lon},${S.pu.lat};${S.do.lon},${S.do.lat}?overview=full&geometries=geojson`;
  const r=await fetch(url);
  const d=await r.json();
  if(d.code!=='Ok') throw new Error('Routing failed');
  const route=d.routes[0];
  return {
    coords:route.geometry.coordinates.map(c=>[c[1],c[0]]),
    distance:route.distance,
    duration:route.duration,
  };
}

// ── Geocoding autocomplete ─────────────────────────────────────────────────
const timers={};
function autocomplete(inputId,dropId,type){
  const inp=document.getElementById(inputId);
  const drop=document.getElementById(dropId);
  inp.addEventListener('input',()=>{
    clearTimeout(timers[type]);
    const q=inp.value.trim();
    if(q.length<3){drop.classList.remove('open');return;}
    timers[type]=setTimeout(()=>suggest(q,inp,drop,type),380);
  });
  document.addEventListener('click',e=>{
    if(!inp.contains(e.target)&&!drop.contains(e.target)) drop.classList.remove('open');
  });
}
async function suggest(q,inp,drop,type){
  try{
    const r=await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&limit=5`,
      {headers:{'Accept-Language':'en'}}
    );
    const res=await r.json();
    drop.innerHTML='';
    if(!res.length){drop.classList.remove('open');return;}
    res.forEach(item=>{
      const el=document.createElement('div');
      el.className='drop-item';
      el.textContent=item.display_name;
      el.title=item.display_name;
      el.addEventListener('click',()=>{
        inp.value=item.display_name;
        drop.classList.remove('open');
        pin(type,parseFloat(item.lat),parseFloat(item.lon),item.display_name.split(',')[0]);
      });
      drop.appendChild(el);
    });
    drop.classList.add('open');
  }catch(e){console.error(e);}
}
autocomplete('pu-input','pu-drop','pu');
autocomplete('do-input','do-drop','do');

// ── Defaults ───────────────────────────────────────────────────────────────
const nowD=new Date();
document.getElementById('r-date').value=nowD.toISOString().split('T')[0];
document.getElementById('r-time').value=nowD.toTimeString().slice(0,5);
const paxSlider=document.getElementById('pax');
const paxValEl=document.getElementById('pax-val');
paxSlider.addEventListener('input',()=>paxValEl.textContent=paxSlider.value);

// ── Helpers ────────────────────────────────────────────────────────────────
function fmtTime(d){ return d.getHours().toString().padStart(2,'0')+':'+d.getMinutes().toString().padStart(2,'0'); }
function fmtDur(s){ const m=Math.round(s/60); if(m<60) return m+' min'; const h=Math.floor(m/60),r=m%60; return h+'h'+(r?' '+r+'min':''); }
function fmtDist(m){ return (m/1000).toFixed(1)+' km'; }

// ── Rocket ─────────────────────────────────────────────────────────────────
// ⬇⬇ ROCKET DURATION — change these 3 values together ⬇⬇
const ROCKET_MS  = 2000;  // total overlay display time (ms)
const ROCKET_CSS = '2s';  // must match rocketLaunch animation duration in CSS
// ⬆⬆ ────────────────────────────────────────────────────────── ⬆⬆

function showRocket(){
  const wrap=document.getElementById('rocket-wrap');
  const scene=document.getElementById('rocket-scene');
  scene.classList.remove('launch');
  void scene.offsetWidth;
  wrap.classList.add('on');
}

function launchAndHide(cb){
  const scene=document.getElementById('rocket-scene');
  scene.style.setProperty('--dur', ROCKET_CSS);
  scene.classList.add('launch');
  setTimeout(()=>{
    document.getElementById('rocket-wrap').classList.remove('on');
    scene.classList.remove('launch');
    cb();
  }, ROCKET_MS);
}

// ── Predict ────────────────────────────────────────────────────────────────
async function predict(){
  document.getElementById('err').classList.remove('on');
  document.getElementById('result').classList.remove('on');
  if(!S.pu.lat||!S.do.lat){showErr('Pin both a pickup and a drop-off first.');return;}
  const date=document.getElementById('r-date').value;
  const time=document.getElementById('r-time').value;
  if(!date||!time){showErr('Select date and time.');return;}

  const params=new URLSearchParams({
    pickup_datetime:`${date} ${time}:00`,
    pickup_longitude:S.pu.lon, pickup_latitude:S.pu.lat,
    dropoff_longitude:S.do.lon, dropoff_latitude:S.do.lat,
    passenger_count:paxSlider.value,
  });

  showRocket();

  try{
    const minWait=new Promise(r=>setTimeout(r, ROCKET_MS-100));
    const [fareRes,routeData]=await Promise.all([
      fetch(`https://taxifare-203500939035.europe-west1.run.app/predict?${params}`)
        .then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}),
      getRoute(),
      minWait
    ]);
    const fare=fareRes.fare??fareRes.prediction;
    if(fare==null) throw new Error('No fare in response');
    const dep=new Date();
    const arr=new Date(dep.getTime()+routeData.duration*1000);
    launchAndHide(()=>{
      drawRoute(routeData.coords);
      document.getElementById('fare-amt').textContent='$'+parseFloat(fare).toFixed(2);
      document.getElementById('stat-dist').textContent=fmtDist(routeData.distance);
      document.getElementById('stat-dur').textContent=fmtDur(routeData.duration);
      document.getElementById('t-depart').textContent=fmtTime(dep);
      document.getElementById('t-arrive').textContent=fmtTime(arr);
      document.getElementById('result').classList.add('on');
    });
  }catch(e){
    document.getElementById('rocket-wrap').classList.remove('on');
    showErr('Error: '+e.message);
  }
}

function showErr(msg){
  const el=document.getElementById('err');
  el.textContent='⚠ '+msg;
  el.classList.add('on');
}
</script>
</body>
</html>
""", height=900, scrolling=False)
