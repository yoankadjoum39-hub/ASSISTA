LYRA_HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {
  --bg: #02060d;
  --bg-2: #07101c;
  --surface: rgba(7, 14, 24, 0.78);
  --border: rgba(125, 211, 252, 0.2);
  --text: #ecf7ff;
  --muted: #95afc8;
  --accent: #67e8f9;
  --accent-2: #7c3aed;
  --accent-3: #38bdf8;
  --glow: 0 35px 120px rgba(0, 0, 0, 0.42);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  height: 100%;
  overflow: hidden;
  background:
    radial-gradient(circle at 18% 20%, rgba(56,189,248,0.18), transparent 26%),
    radial-gradient(circle at 82% 16%, rgba(124,58,237,0.18), transparent 24%),
    radial-gradient(circle at 50% 80%, rgba(103,232,249,0.08), transparent 28%),
    linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%);
  color: var(--text);
  font-family: "Segoe UI", sans-serif;
}
body::before {
  content: "";
  position: fixed;
  inset: -15%;
  background:
    linear-gradient(90deg, transparent 0%, rgba(103,232,249,0.024) 50%, transparent 100%),
    linear-gradient(0deg, transparent 0%, rgba(124,58,237,0.02) 50%, transparent 100%);
  background-size: 140px 140px;
  animation: gridDrift 14s linear infinite;
  opacity: 0.55;
  pointer-events: none;
}
@keyframes gridDrift {
  from { transform: translate3d(0,0,0); }
  to   { transform: translate3d(70px,70px,0); }
}
.shell {
  position: relative;
  height: 100%;
  display: grid;
  grid-template-rows: auto 1fr auto auto;
  gap: 16px;
  padding: 24px;
}
.topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.brand-box { display: flex; flex-direction: column; gap: 6px; }
.brand {
  font-size: 31px;
  font-weight: 900;
  letter-spacing: 0.24em;
  color: #d9fbff;
  text-shadow: 0 0 20px rgba(103,232,249,0.2);
}
.subline {
  color: var(--muted);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.status-cluster { display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; align-items: center; }
.chip {
  border-radius: 999px;
  padding: 8px 12px;
  background: rgba(10,18,29,0.88);
  border: 1px solid var(--border);
  color: #dcf9ff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.03);
}
.chip.live {
  border-color: rgba(52,211,153,0.55);
  color: #bbf7d0;
  box-shadow: 0 0 18px rgba(52,211,153,0.12);
}

/* ── Bouton micro ── */
#btn-mic {
  border-radius: 999px;
  padding: 9px 18px;
  background: rgba(10,18,29,0.88);
  border: 1.5px solid rgba(103,232,249,0.38);
  color: #67e8f9;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.07em;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s, border-color 0.2s, color 0.2s;
  outline: none;
  display: flex;
  align-items: center;
  gap: 7px;
}
#btn-mic:hover {
  background: rgba(103,232,249,0.10);
  box-shadow: 0 0 20px rgba(103,232,249,0.22);
}
#btn-mic.active {
  background: rgba(103,232,249,0.14);
  border-color: rgba(52,211,153,0.7);
  color: #bbf7d0;
  box-shadow: 0 0 24px rgba(52,211,153,0.22);
}
#btn-mic .mic-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #67e8f9;
  transition: background 0.2s;
}
#btn-mic.active .mic-dot {
  background: #34d399;
  box-shadow: 0 0 6px rgba(52,211,153,0.8);
  animation: micPulse 1.1s ease-in-out infinite alternate;
}
@keyframes micPulse {
  from { opacity: 1; }
  to   { opacity: 0.35; }
}

.center-stage {
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(320px,1fr) minmax(360px,470px);
  gap: 20px;
}
.orb-panel, .feed-panel {
  position: relative;
  border-radius: 28px;
  border: 1px solid var(--border);
  background: var(--surface);
  box-shadow: var(--glow);
  overflow: hidden;
}
.orb-panel::before, .feed-panel::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.05), transparent 38%);
  pointer-events: none;
}
.orb-panel {
  display: flex;
  align-items: center;
  justify-content: center;
}
.orb-wrap {
  position: relative;
  width: min(60vw, 660px);
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.halo {
  position: absolute;
  inset: 12%;
  border-radius: 50%;
  border: 1px solid rgba(103,232,249,0.18);
  box-shadow: 0 0 55px rgba(103,232,249,0.1), inset 0 0 55px rgba(124,58,237,0.08);
  animation: rotateSlow 18s linear infinite;
}
.halo.two  { inset: 5%; border-color: rgba(124,58,237,0.18); animation-duration: 24s; animation-direction: reverse; }
.halo.three { inset: 0; border-style: dashed; border-color: rgba(103,232,249,0.12); animation-duration: 32s; }
@keyframes rotateSlow {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
.orb-shell {
  position: relative;
  width: 58%;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.orb-core {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  border-radius: 50%;
  overflow: hidden;
  box-shadow:
    0 0 40px rgba(34,211,238,0.28),
    0 0 170px rgba(124,58,237,0.22),
    inset 0 0 48px rgba(255,255,255,0.12);
  transition: box-shadow 200ms ease;
  animation: orbPulse 4s ease-in-out infinite alternate;
}
@keyframes orbPulse {
  0%   { transform: scale(1.00); }
  100% { transform: scale(1.04); }
}

/* Canvas 2D pour la sphère de particules 3D */
#orb-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: block;
}

/* Reflet supérieur */
.orb-gloss {
  position: absolute;
  top: 6%;
  left: 14%;
  width: 42%;
  height: 28%;
  background: radial-gradient(ellipse at 40% 30%,
    rgba(255,255,255,0.82) 0%,
    rgba(255,255,255,0.18) 35%,
    transparent 70%);
  border-radius: 50%;
  filter: blur(6px);
  pointer-events: none;
  mix-blend-mode: screen;
  z-index: 2;
}
.orb-fringe, .orb-fringe.two {
  position: absolute;
  inset: -4%;
  border-radius: inherit;
  border: 2px solid rgba(103,232,249,0.18);
  filter: blur(4px);
  animation: fringeMorph 4.2s ease-in-out infinite alternate;
}
.orb-fringe.two {
  inset: -7%;
  border-color: rgba(167,139,250,0.16);
  filter: blur(8px);
  animation-duration: 5.6s;
}
@keyframes fringeMorph {
  0%   { transform: scale(0.98) rotate(0deg);  border-radius: 50% 41% 57% 43% / 49% 55% 45% 51%; }
  100% { transform: scale(1.03) rotate(9deg);  border-radius: 43% 57% 45% 55% / 57% 44% 56% 43%; }
}

.orb-label {
  position: absolute;
  bottom: 7.5%;
  left: 50%;
  transform: translateX(-50%);
  width: min(88%,560px);
  text-align: center;
  padding: 16px 18px;
  border-radius: 22px;
  background: rgba(5,10,18,0.76);
  border: 1px solid rgba(103,232,249,0.14);
  backdrop-filter: blur(4px);
}
.orb-state {
  font-size: 12px;
  color: #aaf4ff;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 800;
}
.orb-transcript {
  margin-top: 8px;
  min-height: 52px;
  font-size: 17px;
  line-height: 1.52;
}

/* ── Feed ── */
.feed-panel { display: flex; flex-direction: column; min-height: 0; }
.feed-head  { padding: 18px 18px 14px; border-bottom: 1px solid rgba(125,211,252,0.12); }
.feed-title { font-size: 13px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.12em; color: #c8fbff; }
.feed-copy  { margin-top: 8px; color: var(--muted); font-size: 13px; line-height: 1.6; }
.feed-body  { flex: 1; min-height: 0; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.entry { border-radius: 18px; padding: 14px 15px; border: 1px solid rgba(125,211,252,0.12); background: rgba(9,17,29,0.86); }
.entry.user { background: linear-gradient(135deg, rgba(10,68,110,0.98), rgba(24,104,156,0.84)); }
.entry.live { border-color: rgba(103,232,249,0.28); box-shadow: 0 0 0 1px rgba(103,232,249,0.08); }
.entry-meta { font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: #9dbada; margin-bottom: 7px; }
.entry-body { font-size: 14px; line-height: 1.7; overflow-wrap: anywhere; }
.entry-body p { margin: 0 0 10px; }
.entry-body code { font-family: Consolas,monospace; font-size: 12px; padding: 2px 6px; border-radius: 8px; background: rgba(2,6,13,0.92); }
.entry-body pre { margin-top: 10px; padding: 14px; border-radius: 16px; overflow: auto; background: rgba(2,6,13,0.96); border: 1px solid rgba(125,211,252,0.1); }
.cursor { display: inline-block; width: 9px; height: 1.1em; margin-left: 3px; border-radius: 2px; background: var(--accent); vertical-align: bottom; animation: blink 0.95s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }

/* ── Signal Micro ── */
.recorder {
  position: relative;
  height: 88px;
  border-radius: 20px;
  border: 1px solid rgba(103,232,249,0.12);
  background: rgba(6,12,20,0.88);
  overflow: hidden;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.recorder.live {
  border-color: rgba(103,232,249,0.35);
  box-shadow: 0 0 24px rgba(103,232,249,0.08);
}
.recorder::before {
  content: "";
  position: absolute;
  inset: auto 0 0 0;
  height: 1px;
  background: rgba(103,232,249,0.22);
}
.recorder-label {
  position: absolute;
  top: 10px;
  left: 16px;
  z-index: 2;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #a8f0fb;
}
.recorder-vol {
  position: absolute;
  top: 10px;
  right: 16px;
  z-index: 2;
  font-size: 11px;
  font-weight: 700;
  font-family: Consolas, monospace;
  color: rgba(103,232,249,0.6);
  letter-spacing: 0.05em;
}
.recorder-rail {
  position: absolute;
  inset: auto 14px 10px 14px;
  height: 46px;
  display: flex;
  align-items: flex-end;
  gap: 3px;
}
.rec-bar {
  flex: 1;
  min-width: 3px;
  border-radius: 3px 3px 0 0;
  transform-origin: bottom center;
  transition: height 55ms cubic-bezier(0.22,1,0.36,1), opacity 55ms ease, background 400ms ease;
  height: 4px;
  opacity: 0.35;
  background: linear-gradient(180deg, rgba(167,139,250,0.95), rgba(103,232,249,0.98));
  box-shadow: 0 0 8px rgba(103,232,249,0.18);
}
.recorder.live .rec-bar {
  box-shadow: 0 0 14px rgba(103,232,249,0.32);
}

.footnote {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 0 4px;
  font-size: 12px;
  color: var(--muted);
}
.footnote strong { color: #d8fbff; }
@media (max-width: 1080px) {
  .shell { padding: 18px; gap: 14px; }
  .center-stage { grid-template-columns: 1fr; }
  .orb-wrap { width: min(88vw, 540px); }
  .feed-panel { min-height: 280px; }
}
</style>
</head>
<body>
  <main class="shell">
    <section class="topline">
      <div class="brand-box">
        <div class="brand">LYRA</div>
        <div class="subline">Voice to voice futuriste • veille vocale • PC control hands-free</div>
      </div>
      <div class="status-cluster">
        <button id="btn-mic" onclick="toggleMic()">
          <span class="mic-dot"></span>
          <span id="btn-mic-label">Micro OFF</span>
        </button>
        <div class="chip" id="mic-chip">Micro OFF</div>
        <div class="chip" id="speak-chip">Voix en veille</div>
        <div class="chip" id="mode-chip">Veille vocale</div>
      </div>
    </section>

    <section class="center-stage">
      <div class="orb-panel">
        <div class="orb-wrap">
          <div class="halo"></div>
          <div class="halo two"></div>
          <div class="halo three"></div>
          <div class="orb-shell">
            <div class="orb-core" id="orb-core">
              <canvas id="orb-canvas"></canvas>
              <div class="orb-gloss"></div>
              <div class="orb-fringe"></div>
              <div class="orb-fringe two"></div>
            </div>
          </div>
          <div class="orb-label">
            <div class="orb-state" id="orb-state">Initialisation de LYRA...</div>
            <div class="orb-transcript" id="orb-transcript">Dites "salut assista" pour la réveiller.</div>
          </div>
        </div>
      </div>

      <aside class="feed-panel">
        <div class="feed-head">
          <div class="feed-title">Flux conversationnel</div>
          <div class="feed-copy" id="feed-copy">
            Activez le micro puis dites "salut assista" pour démarrer.
          </div>
        </div>
        <div class="feed-body" id="feed-body"></div>
      </aside>
    </section>

    <section class="recorder" id="recorder">
      <div class="recorder-label" id="recorder-label">Signal micro</div>
      <div class="recorder-vol" id="recorder-vol">0%</div>
      <div class="recorder-rail" id="recorder-rail"></div>
    </section>

    <footer class="footnote">
      <div><strong>Usage</strong> Cliquez sur "Micro OFF" pour activer, dites "salut assista", puis parlez naturellement.</div>
      <div id="status-line">Veille vocale en préparation...</div>
    </footer>
  </main>

<script>
// ═══════════════════════════════════════════════════
//  ÉTAT GLOBAL
// ═══════════════════════════════════════════════════
let currentState = {
  history: [], busy: false,
  streaming_text: "", streaming_html: "",
  status_text: "", last_transcript: "",
  voice_status: "", voice_listening: false,
  voice_speaking: false, voice_awake: false,
  awaiting_wake_word: true,
  speech_level: 0.0, user_signal_level: 0.0,
  auto_speak_enabled: true,
};

let smoothedLevel = 0.0;
let smoothedSpeakLevel = 0.0;
let micActive = false;

// ═══════════════════════════════════════════════════
//  TOGGLE MICRO (bouton)
// ═══════════════════════════════════════════════════
async function toggleMic() {
  if (!window.pywebview || !window.pywebview.api) return;
  if (micActive) {
    await window.pywebview.api.stop_voice();
    micActive = false;
  } else {
    await window.pywebview.api.start_voice();
    micActive = true;
  }
  updateMicButton();
}

function updateMicButton() {
  const btn   = document.getElementById("btn-mic");
  const label = document.getElementById("btn-mic-label");
  if (micActive || currentState.voice_listening) {
    btn.classList.add("active");
    label.textContent = "Micro ON";
  } else {
    btn.classList.remove("active");
    label.textContent = "Micro OFF";
  }
}

// ═══════════════════════════════════════════════════
//  SPHÈRE DE PARTICULES 3D — Canvas 2D
// ═══════════════════════════════════════════════════
(function initParticleSphere() {
  const canvas = document.getElementById("orb-canvas");
  const ctx    = canvas.getContext("2d");
  if (!ctx) return;

  const N = 160;          // nombre de particules
  const R = 0.46;         // rayon (fraction du canvas)

  // Génère des points uniformément sur une sphère (méthode de Fibonacci)
  const pts = [];
  const phi = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < N; i++) {
    const y     = 1 - (i / (N - 1)) * 2;
    const r     = Math.sqrt(1 - y * y);
    const theta = phi * i;
    pts.push({
      ox: r * Math.cos(theta),   // coords normalisées sur sphère unité
      oy: y,
      oz: r * Math.sin(theta),
      // Propriétés visuelles
      size: 1.2 + Math.random() * 3.2,
      speed: 0.18 + Math.random() * 0.26,
      phase: Math.random() * Math.PI * 2,
      drift: (Math.random() - 0.5) * 0.012,  // dérive angulaire individuelle
      color: Math.random(),                    // 0=cyan, 1=violet, 0.5=blanc
    });
  }

  // Axes de rotation globaux
  let rotX = 0.0, rotY = 0.0, rotZ = 0.0;
  // Vitesse de rotation auto (en rad/s)
  const SPEED_X = 0.12, SPEED_Y = 0.19, SPEED_Z = 0.07;

  // Distorsion instable (bruit sinusoïdal multi-fréquence)
  function wobble(t) {
    return {
      ax: Math.sin(t * 0.31) * 0.08 + Math.sin(t * 0.73) * 0.04,
      ay: Math.cos(t * 0.19) * 0.06 + Math.cos(t * 0.53) * 0.03,
      az: Math.sin(t * 0.47) * 0.05,
    };
  }

  function rotatePoint(x, y, z, rx, ry, rz) {
    // Rotation X
    let cy = Math.cos(rx), sy = Math.sin(rx);
    let y2 = y * cy - z * sy;
    let z2 = y * sy + z * cy;
    y = y2; z = z2;
    // Rotation Y
    let cx = Math.cos(ry), sx = Math.sin(ry);
    let x2 = x * cx + z * sx;
    z2 = -x * sx + z * cx;
    x = x2; z = z2;
    // Rotation Z
    let cz = Math.cos(rz), sz = Math.sin(rz);
    x2 = x * cz - y * sz;
    y2 = x * sz + y * cz;
    return { x: x2, y: y2, z: z2 };
  }

  function ptColor(p, depth, t, energy, speaking) {
    // Couleur de base selon propriété de la particule
    const mix = p.color + Math.sin(t * p.speed + p.phase) * 0.15;
    const cyan   = [103, 232, 249];
    const violet = [167, 139, 250];
    const white  = [210, 250, 255];
    const green  = [52,  211, 153];

    let r, g, b;
    if (mix < 0.33) {
      const f = mix / 0.33;
      r = cyan[0] + (white[0]-cyan[0])*f;
      g = cyan[1] + (white[1]-cyan[1])*f;
      b = cyan[2] + (white[2]-cyan[2])*f;
    } else {
      const f = (mix - 0.33) / 0.67;
      r = white[0] + (violet[0]-white[0])*f;
      g = white[1] + (violet[1]-white[1])*f;
      b = white[2] + (violet[2]-white[2])*f;
    }

    // Boost quand énergie vocale ou LYRA parle
    if (speaking > 0.1) {
      r = r * (1-speaking*0.4) + green[0] * speaking * 0.4;
      g = g * (1-speaking*0.4) + green[1] * speaking * 0.4;
      b = b * (1-speaking*0.4) + green[2] * speaking * 0.4;
    }
    r = Math.round(Math.min(255, r + energy * 30));
    g = Math.round(Math.min(255, g + energy * 10));
    b = Math.round(Math.min(255, b + energy * 5));

    // Opacité perspective : particules derrière = plus sombres
    const alpha = 0.18 + depth * 0.72 + energy * 0.15 + speaking * 0.1;
    return `rgba(${r},${g},${b},${Math.min(1,alpha)})`;
  }

  let lastT = 0;
  function frame(ts) {
    const t   = ts / 1000;
    const dt  = Math.min(t - lastT, 0.05);
    lastT = t;

    const energy   = smoothedLevel;
    const speaking = smoothedSpeakLevel;

    // Rotation auto + accélération si énergie
    const boost = 1 + energy * 2.5 + speaking * 1.5;
    rotX += SPEED_X * dt * boost;
    rotY += SPEED_Y * dt * boost;
    rotZ += SPEED_Z * dt * boost;

    // Wobble instable
    const wb = wobble(t);

    const size = canvas.width;
    const cx   = size / 2;
    const cy   = size / 2;
    const rad  = size * R;

    ctx.clearRect(0, 0, size, size);

    // Fond sphère — gradient radial profond
    const bg = ctx.createRadialGradient(cx, cy, 0, cx, cy, rad * 1.05);
    bg.addColorStop(0,    `rgba(10,30,70,${0.82 + energy * 0.1})`);
    bg.addColorStop(0.45, `rgba(5,14,45,${0.88})`);
    bg.addColorStop(0.78, `rgba(30,8,68,${0.82})`);
    bg.addColorStop(1,    `rgba(2,5,18,0)`);
    ctx.beginPath();
    ctx.arc(cx, cy, rad * 1.05, 0, Math.PI * 2);
    ctx.fillStyle = bg;
    ctx.fill();

    // Prépare liste de points projetés, triés par profondeur
    const visible = [];
    for (let i = 0; i < N; i++) {
      const p = pts[i];
      // Dérive individuelle
      p.phase += p.drift * dt * boost;

      // Position sur la sphère (légère distorsion par wobble)
      const rx = rotX + wb.ax + p.phase * 0.01;
      const ry = rotY + wb.ay;
      const rz = rotZ + wb.az;

      const { x, y, z } = rotatePoint(p.ox, p.oy, p.oz, rx, ry, rz);

      // Projection perspective
      const perspective = 2.4;
      const scale = perspective / (perspective + z + 1);
      const px = cx + x * rad * scale;
      const py = cy - y * rad * scale;

      // Profondeur 0..1
      const depth = (z + 1) / 2;

      visible.push({ p, px, py, depth, scale, z });
    }

    // Trier back-to-front
    visible.sort((a, b) => a.z - b.z);

    // Lueur centrale
    const glow = ctx.createRadialGradient(cx, cy*0.88, 0, cx, cy, rad*0.7);
    glow.addColorStop(0,   `rgba(103,232,249,${0.04 + energy*0.10 + speaking*0.08})`);
    glow.addColorStop(0.5, `rgba(124,58,237,${0.04 + energy*0.06})`);
    glow.addColorStop(1,   `rgba(0,0,0,0)`);
    ctx.beginPath();
    ctx.arc(cx, cy, rad, 0, Math.PI * 2);
    ctx.fillStyle = glow;
    ctx.fill();

    // Dessine les particules
    for (const { p, px, py, depth, scale } of visible) {
      // Halo autour de la particule
      const psize = p.size * scale * (0.9 + energy * 0.6 + speaking * 0.4);
      const haloR = psize * (3.5 + energy * 2);
      if (haloR > 0.5) {
        const hg = ctx.createRadialGradient(px, py, 0, px, py, haloR);
        const col = ptColor(p, depth, lastT, energy, speaking);
        hg.addColorStop(0,   col.replace('rgba', 'rgba').replace(/,[^,]+\)$/, `,${(depth*0.22+energy*0.12).toFixed(2)})`));
        hg.addColorStop(1,   'rgba(0,0,0,0)');
        ctx.beginPath();
        ctx.arc(px, py, haloR, 0, Math.PI * 2);
        ctx.fillStyle = hg;
        ctx.fill();
      }

      // Point central lumineux
      ctx.beginPath();
      ctx.arc(px, py, Math.max(0.5, psize), 0, Math.PI * 2);
      ctx.fillStyle = ptColor(p, depth, lastT, energy, speaking);
      ctx.fill();
    }

    // Masque circulaire (bord doux)
    const mask = ctx.createRadialGradient(cx, cy, rad * 0.82, cx, cy, rad * 1.02);
    mask.addColorStop(0, 'rgba(0,0,0,0)');
    mask.addColorStop(1, 'rgba(2,5,16,1)');
    ctx.beginPath();
    ctx.arc(cx, cy, rad * 1.02, 0, Math.PI * 2);
    ctx.fillStyle = mask;
    ctx.fill();

    requestAnimationFrame(frame);
  }

  function resize() {
    const s = canvas.parentElement.offsetWidth;
    canvas.width  = s;
    canvas.height = s;
  }
  resize();
  new ResizeObserver(resize).observe(canvas.parentElement);
  requestAnimationFrame(frame);
})();

// ═══════════════════════════════════════════════════
//  BARRES SIGNAL MICRO
// ═══════════════════════════════════════════════════
const BAR_COUNT = 48;
let barHeights = new Float32Array(BAR_COUNT);
let barPhases  = new Float32Array(BAR_COUNT);

function seedRecorder() {
  const rail = document.getElementById("recorder-rail");
  const bars = [];
  for (let i = 0; i < BAR_COUNT; i++) {
    barPhases[i] = Math.random() * Math.PI * 2;
    bars.push('<span class="rec-bar" id="rb'+i+'"></span>');
  }
  rail.innerHTML = bars.join("");
}

function updateBars(level, t) {
  const recorder  = document.getElementById("recorder");
  const isActive  = level > 0.04 || currentState.voice_listening;
  recorder.classList.toggle("live", isActive);

  const label = document.getElementById("recorder-label");
  label.textContent = level > 0.06
    ? "Enregistrement vocal détecté"
    : isActive ? "Micro en écoute"
    : "Signal micro";

  document.getElementById("recorder-vol").textContent =
    Math.round(level * 100) + "%";

  const maxH = 44;
  for (let i = 0; i < BAR_COUNT; i++) {
    const bar = document.getElementById("rb"+i);
    if (!bar) continue;
    const phase = barPhases[i] + t * (0.8 + level * 4.0);
    const wave  = (Math.sin(phase) + 1) / 2;
    let target;
    if (level > 0.03) {
      const center = i / (BAR_COUNT - 1);
      const bell   = Math.exp(-Math.pow((center - 0.5) * 2.8, 2));
      const noise  = wave * 0.35;
      target = level * bell * 0.88 + noise * level + 0.04;
    } else {
      target = 0.03 + wave * 0.05;
    }
    target = Math.max(0.02, Math.min(1.0, target));
    const prev = barHeights[i];
    barHeights[i] = target > prev
      ? prev + (target - prev) * 0.55
      : prev + (target - prev) * 0.18;
    const h = Math.round(barHeights[i] * maxH);
    bar.style.height  = Math.max(3, h) + "px";
    bar.style.opacity = String(0.25 + barHeights[i] * 0.75);
    const r = Math.round(103 + (167-103) * barHeights[i]);
    const g = Math.round(232 - 232 * barHeights[i] * 0.5);
    const b = Math.round(249 - (249-250) * barHeights[i]);
    bar.style.background = `linear-gradient(180deg, rgb(${r},${g},${b}), rgba(103,232,249,0.9))`;
  }
}

// ═══════════════════════════════════════════════════
//  BOUCLE D'ANIMATION PRINCIPALE
// ═══════════════════════════════════════════════════
function animLoop(ts) {
  const t = ts / 1000;
  const rawLevel = currentState.user_signal_level || 0;
  const rawSpeak = currentState.speech_level || 0;
  smoothedLevel      = smoothedLevel      + (rawLevel - smoothedLevel)      * 0.18;
  smoothedSpeakLevel = smoothedSpeakLevel + (rawSpeak - smoothedSpeakLevel) * 0.14;

  updateBars(smoothedLevel, t);

  const core = document.getElementById("orb-core");
  if (core) {
    const speaking = currentState.voice_speaking;
    const energy   = speaking
      ? 0.5 + smoothedSpeakLevel * 0.8
      : smoothedLevel > 0.04 ? 0.3 + smoothedLevel * 0.6
      : currentState.voice_awake ? 0.25 : 0.08;
    core.style.boxShadow = `
      0 0 ${30 + energy*60}px rgba(34,211,238,${(0.18 + energy*0.35).toFixed(2)}),
      0 0 ${100 + energy*180}px rgba(124,58,237,${(0.12 + energy*0.28).toFixed(2)}),
      inset 0 0 ${30 + energy*40}px rgba(255,255,255,${(0.06 + energy*0.14).toFixed(2)})
    `;
  }
  requestAnimationFrame(animLoop);
}
requestAnimationFrame(animLoop);

// ═══════════════════════════════════════════════════
//  HELPERS UI
// ═══════════════════════════════════════════════════
function escapeHtml(text) {
  return String(text || "")
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}
function renderMarkdownStream(text) {
  let e = escapeHtml(text);
  e = e.replace(/```(\w*)\n([\s\S]*?)```/g, (_,lang,code) =>
    '<pre><code data-lang="'+escapeHtml(lang||"text")+'">'+code+'</code></pre>');
  e = e.replace(/`([^`]+)`/g,'<code>$1</code>');
  e = e.replace(/^### (.+)$/gm,'<h3>$1</h3>');
  e = e.replace(/^## (.+)$/gm,'<h2>$1</h2>');
  e = e.replace(/^# (.+)$/gm,'<h1>$1</h1>');
  e = e.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');
  e = e.replace(/\n/g,'<br>');
  return e;
}

// ═══════════════════════════════════════════════════
//  RENDU ÉTAT
// ═══════════════════════════════════════════════════
function renderState(state) {
  currentState = state || currentState;
  renderOrb();
  renderFeed();
  updateMicButton();
}

function renderOrb() {
  const transcript = currentState.last_transcript
    ? currentState.last_transcript
    : (currentState.voice_speaking
      ? "LYRA vous répond..."
      : (currentState.voice_awake
        ? "Conversation ouverte. Parlez naturellement."
        : (currentState.voice_listening
          ? 'Dites "salut assista" pour me réveiller.'
          : "Activez le micro pour commencer.")));

  let label = "LYRA en veille";
  if (currentState.voice_speaking)       label = "LYRA parle";
  else if (currentState.busy)            label = "LYRA réfléchit";
  else if (currentState.voice_awake)     label = "LYRA réveillée";
  else if (currentState.voice_listening) label = "LYRA écoute le mot-clé";

  document.getElementById("orb-state").textContent      = label;
  document.getElementById("orb-transcript").textContent = transcript;
  document.getElementById("mic-chip").textContent        = currentState.voice_listening ? "Micro ON" : "Micro OFF";
  document.getElementById("mic-chip").classList.toggle("live", !!currentState.voice_listening);
  document.getElementById("speak-chip").textContent      = currentState.voice_speaking ? "Voix active" : "Voix en veille";
  document.getElementById("speak-chip").classList.toggle("live", !!currentState.voice_speaking);
  document.getElementById("mode-chip").textContent       = currentState.voice_awake ? "Conversation active" : "Veille vocale";
  document.getElementById("mode-chip").classList.toggle("live", !!currentState.voice_awake);
  document.getElementById("status-line").textContent     = currentState.status_text || currentState.voice_status || "Conversation vocale active.";
  document.getElementById("feed-copy").textContent       = currentState.voice_status || 'LYRA écoute. Dites simplement "salut assista".';

  // Sync micActive avec l'état Python
  micActive = !!currentState.voice_listening;
}

function renderFeed() {
  const body = document.getElementById("feed-body");
  const chunks = [];
  (currentState.history || []).slice(-10).forEach(function(item) {
    const cls    = item.role === "user" ? "user" : "assista";
    const author = item.role === "user" ? "Vous" : "LYRA";
    const html   = item.role === "user"
      ? escapeHtml(item.text).replace(/\n/g,"<br>")
      : (item.html || renderMarkdownStream(item.text));
    chunks.push(`<article class="entry ${cls}"><div class="entry-meta">${author}</div><div class="entry-body">${html}</div></article>`);
  });
  if (currentState.busy && currentState.streaming_text) {
    chunks.push(`<article class="entry live"><div class="entry-meta">LYRA en direct</div><div class="entry-body">${currentState.streaming_html || renderMarkdownStream(currentState.streaming_text)}<span class="cursor"></span></div></article>`);
  }
  body.innerHTML = chunks.join("");
  body.scrollTop = body.scrollHeight;
}

// ═══════════════════════════════════════════════════
//  BOOT
// ═══════════════════════════════════════════════════
async function bootVoiceLoop() {
  const state = await window.pywebview.api.init_session();
  renderState(state);
  if (!state.auto_speak_enabled) {
    renderState(await window.pywebview.api.set_auto_speak(true));
  }
  // Ne démarre pas le micro automatiquement — l'utilisateur clique le bouton
}

window.addEventListener("DOMContentLoaded", function() {
  seedRecorder();
  const boot = setInterval(function() {
    if (window.pywebview && window.pywebview.api) {
      clearInterval(boot);
      bootVoiceLoop();
      setInterval(function() {
        window.pywebview.api.get_state().then(renderState);
      }, 120);
    }
  }, 100);
});
</script>
</body>
</html>
"""