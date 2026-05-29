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
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Syne+Mono&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:      #13131f;
  --surface: #1a1a28;
  --sur2:    #20202f;
  --border:  #2a2a3d;
  --accent:  #f7c948;
  --orange:  #ff6b35;
  --green:   #5ddb8e;
  --text:    #eceaf4;
  --muted:   #6b6885;
}

html, body {
  height: 100%; width: 100%;
  font-family: 'Syne', sans-serif;
  background: var(--bg); color: var(--text);
  overflow: hidden;
  touch-action: pan-x pan-y;
}

/* ════════════════════════════════════════════
   DESKTOP LAYOUT
════════════════════════════════════════════ */
#app {
  display: grid;
  grid-template-columns: 520px 1fr;
  height: 100vh;
  overflow: hidden;
}

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

.brand { font-size: 1.9rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1; }
.brand em { color: var(--accent); font-style: normal; }
.tagline { font-size: 0.72rem; color: var(--muted); letter-spacing: 0.16em;
  text-transform: uppercase; margin-top: 0.25rem; margin-bottom: 1.8rem; }

.divider { height: 1px; background: var(--border); margin: 1.2rem 0; }
.lbl { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.22em;
  text-transform: uppercase; color: var(--muted); margin-bottom: 0.6rem; }
.spacer { flex: 1; min-height: 1rem; }

/* click mode bar */
.click-mode-bar { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.mode-btn {
  flex: 1; padding: 0.5rem 0.6rem;
  background: var(--sur2); border: 1px solid var(--border);
  border-radius: 8px; color: var(--muted); font-family: 'Syne', sans-serif;
  font-size: 0.75rem; font-weight: 600; cursor: pointer; transition: all 0.18s; text-align: center;
}
.mode-btn:hover { border-color: var(--accent); color: var(--text); }
.mode-btn.active-pu { background: rgba(247,201,72,.1); border-color: var(--accent); color: var(--accent); }
.mode-btn.active-do { background: rgba(255,107,53,.1); border-color: var(--orange); color: var(--orange); }
.mode-hint { font-size: 0.68rem; color: var(--muted); margin-bottom: 0.8rem;
  min-height: 1rem; font-style: italic; transition: color .2s; }
.mode-hint.pu { color: var(--accent); }
.mode-hint.do { color: var(--orange); }

/* loc block */
.loc-block { display: flex; align-items: flex-start; gap: 0.9rem; }
.loc-dot-wrap { display: flex; flex-direction: column; align-items: center; padding-top: 0.7rem; flex-shrink: 0; }
.loc-dot { width: 12px; height: 12px; border-radius: 50%; border: 2.5px solid var(--accent); background: transparent; }
.loc-dot.orange { border-color: var(--orange); }
.loc-connector { width: 1px; flex: 1; min-height: 36px; background: var(--border); margin: 4px 0; }
.loc-inputs { flex: 1; min-width: 0; }

.field { position: relative; }
.field input[type=text] {
  width: 100%; background: var(--sur2); border: 1px solid var(--border);
  border-radius: 10px; color: var(--text); font-family: 'Syne', sans-serif;
  font-size: 1rem; padding: 0.68rem 0.9rem; outline: none;
  transition: border-color .2s, box-shadow .2s;
}
.field input[type=text]::placeholder { color: var(--muted); font-size: 0.92rem; }
.field input[type=text]:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(247,201,72,.07); }

.coord-chip { font-family: 'Syne Mono', monospace; font-size: 0.74rem;
  color: var(--muted); margin-top: 0.32rem; min-height: 1rem; transition: color .3s; }
.coord-chip.set { color: var(--green); }

.drop {
  position: absolute; top: calc(100% + 4px); left: 0; right: 0;
  background: #13131e; border: 1px solid var(--border); border-radius: 10px;
  z-index: 9999; max-height: 200px; overflow-y: auto; display: none;
  box-shadow: 0 12px 32px rgba(0,0,0,.6);
}
.drop.open { display: block; }
.drop-item {
  padding: 0.55rem 0.85rem; font-size: 0.85rem; cursor: pointer;
  border-bottom: 1px solid var(--border); color: var(--text);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  transition: background .1s;
}
.drop-item:last-child { border-bottom: none; }
.drop-item:hover { background: var(--border); }

.row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0.7rem; margin-bottom: 0.9rem; }
.mini-lbl { font-size: 0.66rem; font-weight: 700; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--muted); margin-bottom: 0.35rem; }
.row2 input[type=date], .row2 input[type=time] {
  width: 100%; background: var(--sur2); border: 1px solid var(--border);
  border-radius: 10px; color: var(--text); font-family: 'Syne', sans-serif;
  font-size: 0.95rem; padding: 0.62rem 0.8rem; outline: none;
  transition: border-color .2s; color-scheme: dark;
}
.row2 input:focus { border-color: var(--accent); }

.slider-row { display: flex; align-items: center; gap: 0.85rem; }
input[type=range] {
  flex: 1; -webkit-appearance: none; height: 3px;
  background: var(--border); border-radius: 2px; outline: none; cursor: pointer;
}
input[type=range]::-webkit-slider-thumb {
  -webkit-appearance: none; width: 18px; height: 18px;
  background: var(--accent); border-radius: 50%; cursor: pointer; transition: transform .15s;
}
input[type=range]::-webkit-slider-thumb:hover { transform: scale(1.25); }
.pax-val { font-family: 'Syne Mono', monospace; font-size: 1.1rem;
  color: var(--accent); min-width: 1.4rem; text-align: right; }

#btn {
  width: 100%; background: var(--accent); color: #0b0b10;
  border: none; border-radius: 11px; font-family: 'Syne', sans-serif;
  font-weight: 800; font-size: 1rem; letter-spacing: 0.04em;
  padding: 0.88rem; cursor: pointer;
  transition: background .2s, transform .12s, box-shadow .2s;
}
#btn:hover { background: #ffd740; transform: translateY(-2px); box-shadow: 0 8px 28px rgba(247,201,72,.2); }
#btn:active { transform: translateY(0); box-shadow: none; }

/* result card */
#result {
  background: var(--sur2); border: 1px solid var(--border);
  border-radius: 13px; margin-top: 1.1rem; overflow: hidden;
  display: none; animation: pop .35s cubic-bezier(.34,1.56,.64,1);
}
#result.on { display: block; }
@keyframes pop { from{opacity:0;transform:scale(.94) translateY(6px);} to{opacity:1;transform:scale(1) translateY(0);} }
.fare-hero { padding: 1.2rem 1.3rem 1rem; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between; }
.fare-lbl { font-size: 0.62rem; letter-spacing: .22em; text-transform: uppercase; color: var(--muted); }
.fare-amt { font-size: 3rem; font-weight: 800; color: var(--accent); line-height: 1; margin-top: .1rem; }
.fare-note { font-size: .7rem; color: var(--muted); margin-top: .18rem; }
.fare-taxi { font-size: 2.2rem; opacity: .45; }
.stats-grid { display: grid; grid-template-columns: 1fr 1fr; border-bottom: 1px solid var(--border); }
.stat-cell { padding: .85rem 1.2rem; border-right: 1px solid var(--border); }
.stat-cell:nth-child(even) { border-right: none; }
.stat-lbl { font-size: .61rem; letter-spacing: .18em; text-transform: uppercase; color: var(--muted); margin-bottom: .24rem; }
.stat-val { font-family: 'Syne Mono', monospace; font-size: 1.05rem; font-weight: 600; color: var(--text); }
.stat-val.accent { color: var(--accent); }
.time-row { display: flex; align-items: center; justify-content: space-between; padding: .85rem 1.2rem; }
.time-item { text-align: center; }
.time-lbl { font-size: .61rem; letter-spacing: .18em; text-transform: uppercase; color: var(--muted); margin-bottom: .2rem; }
.time-val { font-family: 'Syne Mono', monospace; font-size: 1.1rem; font-weight: 600; color: var(--text); }
.time-arrow { font-size: 1rem; color: var(--muted); }

#err {
  background: rgba(255,107,53,.07); border: 1px solid var(--orange);
  border-radius: 9px; padding: .75rem .9rem; margin-top: .9rem;
  font-size: .82rem; color: var(--orange); display: none;
}
#err.on { display: block; }

/* ── Map wrap ── */
#map-wrap { position: relative; overflow: hidden; }
#map { width: 100%; height: 100%; min-height: 0; }
#map-wrap:not(.fullscreen) #map { height: 100vh; }
#map.cursor-pu { cursor: crosshair; }
#map.cursor-do { cursor: crosshair; }

/* map click hint */
#map-hint {
  position: absolute; bottom: 2rem; left: 50%; transform: translateX(-50%);
  background: rgba(20,20,35,.88); backdrop-filter: blur(8px);
  border: 1px solid var(--border); border-radius: 50px;
  padding: .5rem 1.2rem; font-size: .78rem; color: var(--text);
  pointer-events: none; white-space: nowrap;
  opacity: 0; transition: opacity .3s; z-index: 500;
}
#map-hint.show { opacity: 1; }
#map-hint .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%;
  margin-right: .4rem; vertical-align: middle; }

/* ════════════════════════════════════════════
   MOBILE MAP EXPAND BUTTON & FULLSCREEN
════════════════════════════════════════════ */
#map-expand-btn {
  display: none; /* shown only on mobile */
  position: absolute; top: .75rem; right: .75rem; z-index: 600;
  background: rgba(20,20,35,.88); backdrop-filter: blur(6px);
  border: 1px solid var(--border); border-radius: 8px;
  padding: .45rem .65rem; cursor: pointer;
  font-size: .72rem; font-family: 'Syne', sans-serif; font-weight: 700;
  color: var(--text); letter-spacing: .05em;
  transition: background .15s;
}
#map-expand-btn:hover { background: rgba(247,201,72,.15); }

#map-close-btn {
  display: none; /* shown in fullscreen mode */
  position: absolute; top: .75rem; right: .75rem; z-index: 600;
  background: rgba(20,20,35,.95); backdrop-filter: blur(6px);
  border: 1px solid var(--border); border-radius: 50%;
  width: 38px; height: 38px; cursor: pointer;
  font-size: 1.1rem; color: var(--text);
  align-items: center; justify-content: center;
  transition: background .15s;
}
#map-close-btn:hover { background: rgba(247,201,72,.2); }

/* fullscreen: map-wrap covers everything */
#map-wrap.fullscreen {
  position: fixed !important;
  inset: 0 !important;
  z-index: 5000 !important;
  width: 100vw !important;
  height: 100dvh !important;
}
#map-wrap.fullscreen #map { height: 100dvh !important; }
#map-wrap.fullscreen #map-expand-btn { display: none !important; }
#map-wrap.fullscreen #map-close-btn { display: flex !important; }

/* ════════════════════════════════════════════
   ROCKET OVERLAY
════════════════════════════════════════════ */
#rocket-wrap {
  position: absolute; inset: 0;
  background: rgba(16,16,26,.88); backdrop-filter: blur(10px);
  display: none; flex-direction: column;
  align-items: center; justify-content: center; z-index: 2000;
  overflow: hidden;
}
#rocket-wrap.on { display: flex; }
#rocket-scene { display: flex; flex-direction: column; align-items: center; }
#rocket-scene.launch { animation: rocketLaunch 2s ease-in forwards; }
@keyframes rocketLaunch {
  0%   { transform: translateY(0)     rotate(0deg)   scale(1);   opacity:1; }
  30%  { transform: translateY(-20px)  rotate(-4deg)  scale(1.08);opacity:1; }
  65%  { transform: translateY(-120px) rotate(3deg)   scale(1.05);opacity:.8; }
  100% { transform: translateY(-600px) rotate(0deg)   scale(.5);  opacity:0; }
}
#rocket { font-size: 4rem; filter: drop-shadow(0 0 28px rgba(247,201,72,.65));
  animation: hover 1.2s ease-in-out infinite alternate; }
#rocket-scene.launch #rocket { animation: none; }
@keyframes hover { from{transform:translateY(8px) rotate(-5deg) scale(.97);} to{transform:translateY(-8px) rotate(5deg) scale(1.03);} }
.trail { width: 3px; border-radius: 3px; margin-top: -4px;
  background: linear-gradient(to bottom, var(--accent), transparent);
  animation: trailP 1.2s ease-in-out infinite alternate; }
#rocket-scene.launch .trail { animation: trailG 2s ease-in forwards; }
@keyframes trailP { from{height:14px;opacity:.25;} to{height:65px;opacity:.9;} }
@keyframes trailG  { 0%{height:40px;opacity:.8;} 50%{height:150px;opacity:1;} 100%{height:350px;opacity:0;} }
.rocket-txt { margin-top: 1.5rem; font-size: .74rem; letter-spacing: .24em;
  text-transform: uppercase; color: var(--accent); font-weight: 700;
  animation: blink 1.3s ease-in-out infinite; }
#rocket-scene.launch .rocket-txt { animation: fadeO .6s ease 1.2s forwards; }
@keyframes blink { 0%,100%{opacity:.35;} 50%{opacity:1;} }
@keyframes fadeO { to{opacity:0;} }
.stars { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
.star  { position: absolute; background: white; border-radius: 50%; animation: fall linear infinite; }
@keyframes fall { from{transform:translateY(-10px);opacity:0;} 10%{opacity:1;} to{transform:translateY(110vh);opacity:0;} }

/* Leaflet */
.leaflet-tooltip { font-family:'Syne',sans-serif; font-size:.74rem; font-weight:600;
  background:#1a1a28; border:1px solid #2a2a3d; color:#eceaf4;
  box-shadow:0 4px 12px rgba(0,0,0,.4); border-radius:6px; }
.leaflet-tooltip::before { display:none; }

/* ════════════════════════════════════════════
   MOBILE LAYOUT  ≤ 768px
════════════════════════════════════════════ */
@media (max-width: 768px) {

  html, body { overflow: hidden; touch-action: none; }

  #app {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr auto;
    height: 100dvh;
    overflow: hidden;
  }

  /* Map top, panel bottom */
  #map-wrap { order: 1; overflow: hidden; flex: 1; min-height: 0; }
  #map      { height: 100%; }
  #panel    { order: 2; flex-shrink: 0; }

  /* Show expand button */
  #map-expand-btn { display: block; }

  /* Panel = fixed-height bottom sheet, NO scroll */
  #panel {
    padding: .7rem .9rem .65rem;
    border-right: none;
    border-top: 1px solid var(--border);
    overflow: hidden;
    flex-direction: column;
    gap: 0;
    height: auto;
    flex-shrink: 0;
  }

  /* ── Row 1: brand ── */
  .brand { font-size: 1.05rem; margin-bottom: .45rem; line-height: 1; }
  .tagline  { display: none; }
  .divider  { display: none; }
  .spacer   { display: none; }
  .coord-chip { display: none; }
  .mode-hint  { display: none; }
  .lbl        { display: none; }

  /* ── Row 2: click buttons ── */
  .click-mode-bar { display: grid; grid-template-columns: 1fr 1fr;
    gap: .35rem; margin-bottom: .4rem; }
  .mode-btn { font-size: .66rem; padding: .35rem .4rem; border-radius: 6px; }

  /* ── Row 3: address inputs side by side ── */
  .loc-block { flex-direction: row; gap: .35rem; margin-bottom: .4rem; align-items: stretch; }
  .loc-dot-wrap { display: none; }
  .loc-inputs { display: grid; grid-template-columns: 1fr 1fr; gap: .35rem; flex: 1; }
  .loc-inputs .coord-chip { display: none; }
  .field { margin: 0 !important; }
  .field input[type=text] { font-size: .78rem; padding: .42rem .6rem; border-radius: 7px; }

  /* ── Row 4: date / time / pax on one line ── */
  .row2 { display: contents; }
  .row2 > div { display: contents; }
  .mini-lbl { display: none; }
  .row2 input[type=date], .row2 input[type=time] {
    font-size: .76rem; padding: .4rem .5rem; border-radius: 7px;
  }
  /* wrapper injected by JS for mobile 3-col row */
  #mobile-when-row {
    display: grid; grid-template-columns: 1fr 1fr 1fr;
    gap: .35rem; margin-bottom: .4rem; align-items: center;
  }
  .pax-mobile-wrap { display: flex; align-items: center; gap: .3rem;
    background: var(--sur2); border: 1px solid var(--border);
    border-radius: 7px; padding: .38rem .55rem; }
  .pax-mobile-wrap input[type=range] { flex: 1; height: 2px; }
  .pax-mobile-wrap .pax-val { font-size: .8rem; }

  /* ── Row 5: predict button ── */
  #btn { font-size: .84rem; padding: .58rem; border-radius: 8px; }

  /* ── Row 6: result strip ── */
  #result { margin-top: .4rem; border-radius: 9px; }
  .fare-hero { padding: .45rem .8rem; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between; gap: .5rem; }
  .fare-lbl { display: none; }
  .fare-note { display: none; }
  .fare-taxi { font-size: 1.4rem; opacity: .4; }
  .fare-amt  { font-size: 1.7rem; line-height: 1; }
  .stats-grid { display: none; }

  /* compact time + stats row */
  .result-bottom-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: .4rem .8rem;
    border-top: none;
  }
  .time-row { padding: 0; border: none; flex: 1; justify-content: flex-start; gap: .6rem; }
  .time-arrow { font-size: .8rem; margin: 0 .15rem; }
  .time-lbl { font-size: .52rem; }
  .time-val { font-size: .82rem; }
  .mob-stats { display: flex; gap: .8rem; }
  .mob-stat { display: flex; flex-direction: column; align-items: flex-end; }
  .mob-stat-lbl { font-size: .52rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
  .mob-stat-val { font-family: 'Syne Mono', monospace; font-size: .82rem; font-weight: 600; }
  .mob-stat-val.accent { color: var(--accent); }

  #map-hint { bottom: 32%; font-size: .68rem; padding: .38rem .85rem; }
  #err { font-size: .73rem; padding: .45rem .65rem; margin-top: .35rem; }
}
</style>
</head>
<body>
<div id="app">

  <!-- ═══════════ PANEL ═══════════ -->
  <div id="panel">
    <div class="brand">Taxi<em>Fare</em></div>
    <div class="tagline">NYC · Real-time prediction</div>

    <div class="lbl">Route</div>
    <div class="click-mode-bar">
      <div class="mode-btn" id="btn-pu" onclick="setClickMode('pu')">📍 Click pickup on map</div>
      <div class="mode-btn" id="btn-do" onclick="setClickMode('do')">🏁 Click drop-off on map</div>
    </div>
    <div class="mode-hint" id="mode-hint">Or type an address below</div>

    <div class="loc-block">
      <div class="loc-dot-wrap">
        <div class="loc-dot"></div>
        <div class="loc-connector"></div>
        <div class="loc-dot orange"></div>
      </div>
      <div class="loc-inputs">
        <div class="field" style="margin-bottom:.42rem">
          <input id="pu-input" type="text" placeholder="Pickup address…" autocomplete="off"/>
          <div class="drop" id="pu-drop"></div>
        </div>
        <div class="coord-chip" id="pu-coords">—</div>
        <div class="field" style="margin-top:.65rem">
          <input id="do-input" type="text" placeholder="Drop-off address…" autocomplete="off"/>
          <div class="drop" id="do-drop"></div>
        </div>
        <div class="coord-chip" id="do-coords">—</div>
      </div>
    </div>

    <div class="divider"></div>

    <div class="lbl">When</div>
    <div class="row2" id="when-row">
      <div><div class="mini-lbl">Date</div><input type="date" id="r-date"/></div>
      <div><div class="mini-lbl">Time</div><input type="time" id="r-time"/></div>
    </div>

    <div class="divider"></div>

    <div class="lbl">Passengers</div>
    <div class="slider-row" id="pax-row" style="margin-bottom:.9rem">
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
        <div class="stat-cell"><div class="stat-lbl">Distance</div><div class="stat-val accent" id="stat-dist">—</div></div>
        <div class="stat-cell"><div class="stat-lbl">Duration</div><div class="stat-val" id="stat-dur">—</div></div>
      </div>
      <!-- desktop time row -->
      <div class="time-row" id="time-row-desktop">
        <div class="time-item"><div class="time-lbl">Departure</div><div class="time-val" id="t-depart">—</div></div>
        <div class="time-arrow">→</div>
        <div class="time-item"><div class="time-lbl">Arrival</div><div class="time-val" id="t-arrive">—</div></div>
      </div>
      <!-- mobile bottom row (time + stats) -->
      <div class="result-bottom-row" id="result-bottom-row" style="display:none">
        <div class="time-row">
          <div class="time-item"><div class="time-lbl">Dep.</div><div class="time-val" id="m-depart">—</div></div>
          <div class="time-arrow">→</div>
          <div class="time-item"><div class="time-lbl">Arr.</div><div class="time-val" id="m-arrive">—</div></div>
        </div>
        <div class="mob-stats">
          <div class="mob-stat"><span class="mob-stat-lbl">Dist</span><span class="mob-stat-val accent" id="m-dist">—</span></div>
          <div class="mob-stat"><span class="mob-stat-lbl">Time</span><span class="mob-stat-val" id="m-dur">—</span></div>
        </div>
      </div>
    </div>

    <div id="err"></div>
  </div>

  <!-- ═══════════ MAP ═══════════ -->
  <div id="map-wrap">
    <div id="map"></div>
    <button id="map-expand-btn" onclick="expandMap()">⛶ Expand map</button>
    <button id="map-close-btn"  onclick="collapseMap()">✕</button>
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
    const sz=Math.random()*2.5+.5;
    s.style.cssText=`width:${sz}px;height:${sz}px;left:${Math.random()*100}%;animation-duration:${Math.random()*2+1.5}s;animation-delay:${Math.random()*4}s;opacity:0;`;
    c.appendChild(s);
  }
})();

// ── Mobile layout wiring ───────────────────────────────────────────────────
const isMobile = () => window.innerWidth <= 768;

function wireMobileLayout() {
  if (!isMobile()) return;
  // Wrap date, time, pax slider into one 3-col row
  const whenRow = document.getElementById('when-row');
  const paxRow  = document.getElementById('pax-row');
  if (document.getElementById('mobile-when-row')) return; // already done

  const wrap = document.createElement('div');
  wrap.id = 'mobile-when-row';

  const dateInput = document.getElementById('r-date');
  const timeInput = document.getElementById('r-time');
  const paxInput  = document.getElementById('pax');
  const paxValEl  = document.getElementById('pax-val');

  const paxWrap = document.createElement('div');
  paxWrap.className = 'pax-mobile-wrap';
  paxWrap.appendChild(paxInput);
  paxWrap.appendChild(paxValEl);

  wrap.appendChild(dateInput);
  wrap.appendChild(timeInput);
  wrap.appendChild(paxWrap);

  whenRow.replaceWith(wrap);
  paxRow.remove();

  // Show mobile result bottom row, hide desktop one
  document.getElementById('result-bottom-row').style.display = 'flex';
  document.getElementById('time-row-desktop').style.display = 'none';
}

window.addEventListener('DOMContentLoaded', wireMobileLayout);
window.addEventListener('resize', wireMobileLayout);

// ── Map expand / collapse ──────────────────────────────────────────────────
function expandMap() {
  document.getElementById('map-wrap').classList.add('fullscreen');
  setTimeout(() => map.invalidateSize(), 50);
}
function collapseMap() {
  document.getElementById('map-wrap').classList.remove('fullscreen');
  setTimeout(() => map.invalidateSize(), 50);
  // Re-fit to route/pins after collapse
  fitAfterCollapse();
}
function fitAfterCollapse() {
  if (routeLayers.length > 0) {
    map.fitBounds(routeLayers[1].getBounds(), {padding:[60,60]});
  } else {
    fitBounds();
  }
}

// ── State ──────────────────────────────────────────────────────────────────
const S = { pu:{lat:null,lon:null}, do:{lat:null,lon:null} };
let clickMode = null;

// ── Map init ───────────────────────────────────────────────────────────────
const map = L.map('map',{zoomControl:false}).setView([40.75,-73.97],12);
L.control.zoom({position:'bottomright'}).addTo(map);
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{
  attribution:'© OpenStreetMap © CARTO', maxZoom:19, opacity:0.9
}).addTo(map);
map.on('zoomend moveend', () => map.invalidateSize());

function mkIcon(color, emoji) {
  return L.divIcon({
    className:'',
    html:`<div style="background:${color};width:32px;height:32px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:3px solid #0b0b10;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(0,0,0,.6)"><span style="transform:rotate(45deg);font-size:14px">${emoji}</span></div>`,
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
  const cfg=type==='pu'?{color:'#f7c948',emoji:'📍',tip:'Pickup'}:{color:'#ff6b35',emoji:'🏁',tip:'Drop-off'};
  markers[type]=L.marker([lat,lon],{icon:mkIcon(cfg.color,cfg.emoji)})
    .bindTooltip(cfg.tip+(label?': '+label:''),{permanent:false}).addTo(map);
  S[type]={lat,lon};
  const chip=document.getElementById(type+'-coords');
  chip.textContent=lat.toFixed(5)+'   '+lon.toFixed(5);
  chip.classList.add('set');
  clearRoute();
  if(S.pu.lat&&S.do.lat){
    straightLine=L.polyline([[S.pu.lat,S.pu.lon],[S.do.lat,S.do.lon]],{
      color:'#f7c948',weight:2,dashArray:'6 5',opacity:.35
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
  const glow=L.polyline(coords,{color:'#f7c948',weight:10,opacity:.1}).addTo(map);
  const line=L.polyline(coords,{color:'#f7c948',weight:3.5,opacity:.92}).addTo(map);
  routeLayers.push(glow,line);
  // Fit with extra bottom padding on mobile (panel covers bottom ~30%)
  const pad = isMobile() ? [20, 20, window.innerHeight*0.35, 20] : [70,70];
  map.fitBounds(line.getBounds(), {padding: pad});
}

// ── Click mode ─────────────────────────────────────────────────────────────
const mapEl=document.getElementById('map');
const hintEl=document.getElementById('map-hint');
const btnPuEl=document.getElementById('btn-pu');
const btnDoEl=document.getElementById('btn-do');
const hintMsgEl=document.getElementById('mode-hint');

function setClickMode(mode) {
  if(clickMode===mode){
    clickMode=null; mapEl.className='';
    btnPuEl.classList.remove('active-pu'); btnDoEl.classList.remove('active-do');
    hintEl.classList.remove('show');
    hintMsgEl.textContent='Or type an address below'; hintMsgEl.className='mode-hint'; return;
  }
  clickMode=mode; mapEl.className='cursor-'+mode;
  btnPuEl.classList.toggle('active-pu',mode==='pu');
  btnDoEl.classList.toggle('active-do',mode==='do');
  const isPu=mode==='pu';
  hintEl.innerHTML=`<span class="dot" style="background:${isPu?'#f7c948':'#ff6b35'}"></span>`
    +(isPu?'Click map to set <strong>pickup</strong>':'Click map to set <strong>drop-off</strong>');
  hintEl.classList.add('show');
  hintMsgEl.textContent=isPu?'👆 Click your pickup on the map':'👆 Click your drop-off on the map';
  hintMsgEl.className='mode-hint '+(isPu?'pu':'do');
}

map.on('click', async function(e){
  if(!clickMode) return;
  const {lat,lng}=e.latlng; const type=clickMode;
  let label='';
  try {
    const r=await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`,
      {headers:{'Accept-Language':'en'}});
    const d=await r.json(); label=d.display_name||'';
    document.getElementById(type+'-input').value=label.split(',').slice(0,2).join(',');
  } catch(e){}
  pin(type,lat,lng,label.split(',')[0]);
  if(type==='pu'&&!S.do.lat){ setClickMode('do'); }
  else {
    clickMode=null; mapEl.className='';
    btnPuEl.classList.remove('active-pu'); btnDoEl.classList.remove('active-do');
    hintEl.classList.remove('show');
    hintMsgEl.textContent='Both pins set — ready to predict!'; hintMsgEl.className='mode-hint';
    setTimeout(()=>{ hintMsgEl.textContent='Or type an address below'; },2500);
  }
});

// ── OSRM routing ───────────────────────────────────────────────────────────
async function getRoute() {
  const url=`https://router.project-osrm.org/route/v1/driving/${S.pu.lon},${S.pu.lat};${S.do.lon},${S.do.lat}?overview=full&geometries=geojson`;
  const r=await fetch(url); const d=await r.json();
  if(d.code!=='Ok') throw new Error('Routing failed');
  const route=d.routes[0];
  return { coords:route.geometry.coordinates.map(c=>[c[1],c[0]]), distance:route.distance, duration:route.duration };
}

// ── Geocoding ──────────────────────────────────────────────────────────────
const timers={};
function autocomplete(inputId,dropId,type){
  const inp=document.getElementById(inputId), drop=document.getElementById(dropId);
  inp.addEventListener('input',()=>{
    clearTimeout(timers[type]); const q=inp.value.trim();
    if(q.length<3){drop.classList.remove('open');return;}
    timers[type]=setTimeout(()=>suggest(q,inp,drop,type),380);
  });
  document.addEventListener('click',e=>{ if(!inp.contains(e.target)&&!drop.contains(e.target)) drop.classList.remove('open'); });
}
async function suggest(q,inp,drop,type){
  try{
    const r=await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&limit=5`,{headers:{'Accept-Language':'en'}});
    const res=await r.json(); drop.innerHTML='';
    if(!res.length){drop.classList.remove('open');return;}
    res.forEach(item=>{
      const el=document.createElement('div'); el.className='drop-item';
      el.textContent=item.display_name; el.title=item.display_name;
      el.addEventListener('click',()=>{
        inp.value=item.display_name; drop.classList.remove('open');
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
function fmtDur(s){ const m=Math.round(s/60); if(m<60) return m+' min'; return Math.floor(m/60)+'h'+(m%60?' '+(m%60)+'min':''); }
function fmtDist(m){ return (m/1000).toFixed(1)+' km'; }

// ── Rocket ─────────────────────────────────────────────────────────────────
const ROCKET_MS = 2000;
function showRocket(){ const sc=document.getElementById('rocket-scene'); sc.classList.remove('launch'); void sc.offsetWidth; document.getElementById('rocket-wrap').classList.add('on'); }
function launchAndHide(cb){
  const sc=document.getElementById('rocket-scene'); sc.classList.add('launch');
  setTimeout(()=>{ document.getElementById('rocket-wrap').classList.remove('on'); sc.classList.remove('launch'); cb(); }, ROCKET_MS);
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
    const [fareRes,routeData]=await Promise.all([
      fetch(`https://taxifare-203500939035.europe-west1.run.app/predict?${params}`).then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}),
      getRoute(),
      new Promise(r=>setTimeout(r,ROCKET_MS-100))
    ]);
    const fare=fareRes.fare??fareRes.prediction;
    if(fare==null) throw new Error('No fare in response');
    const dep=new Date(), arr=new Date(dep.getTime()+routeData.duration*1000);
    launchAndHide(()=>{
      drawRoute(routeData.coords);
      document.getElementById('fare-amt').textContent='$'+parseFloat(fare).toFixed(2);
      document.getElementById('stat-dist').textContent=fmtDist(routeData.distance);
      document.getElementById('stat-dur').textContent=fmtDur(routeData.duration);
      document.getElementById('t-depart').textContent=fmtTime(dep);
      document.getElementById('t-arrive').textContent=fmtTime(arr);
      document.getElementById('m-depart').textContent=fmtTime(dep);
      document.getElementById('m-arrive').textContent=fmtTime(arr);
      document.getElementById('m-dist').textContent=fmtDist(routeData.distance);
      document.getElementById('m-dur').textContent=fmtDur(routeData.duration);
      document.getElementById('result').classList.add('on');
    });
  }catch(e){ document.getElementById('rocket-wrap').classList.remove('on'); showErr('Error: '+e.message); }
}

function showErr(msg){ const el=document.getElementById('err'); el.textContent='⚠ '+msg; el.classList.add('on'); }
</script>
</body>
</html>
""", height=900, scrolling=False)
