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
.status-cluster { display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }
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

/* ── Bulle principale : canvas WebGL à l'intérieur ── */
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
#orb-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: block;
}
/* Reflet supérieur par-dessus le canvas */
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
/* Particules par-dessus */
.particle-field { position: absolute; inset: -2%; pointer-events: none; }
.particle {
  --size: 8px; --left: 50%; --top: 50%; --delay: 0s; --duration: 6s;
  position: absolute;
  left: var(--left); top: var(--top);
  width: var(--size); height: var(--size);
  margin-left: calc(var(--size) * -0.5);
  margin-top: calc(var(--size) * -0.5);
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.98) 0%, rgba(103,232,249,0.95) 40%, rgba(103,232,249,0.08) 70%, transparent 100%);
  opacity: 0.6;
  box-shadow: 0 0 14px rgba(103,232,249,0.36), 0 0 26px rgba(124,58,237,0.16);
  animation: drift var(--duration) linear infinite;
  animation-delay: var(--delay);
}
@keyframes drift {
  0%   { transform: translate3d(-14px,-10px,0) scale(0.84); }
  25%  { transform: translate3d(10px,-14px,0) scale(1.08); }
  50%  { transform: translate3d(16px,12px,0) scale(1.18); }
  75%  { transform: translate3d(-8px,18px,0) scale(0.96); }
  100% { transform: translate3d(-14px,-10px,0) scale(0.84); }
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
/* Volume numérique */
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
/* Les barres sont maintenant canvas-less — elles répondent directement au signal */
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

/* ── Barre contrôle micro ── */
.mic-bar {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 18px;
  border-radius: 18px;
  border: 1px solid rgba(103,232,249,0.14);
  background: rgba(6,12,20,0.88);
}
/* Bouton micro principal */
.mic-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 20px;
  border-radius: 999px;
  border: 1.5px solid rgba(103,232,249,0.38);
  background: rgba(10,28,48,0.92);
  color: #a8f0fb;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: all 0.22s ease;
  white-space: nowrap;
  flex-shrink: 0;
}
.mic-btn:hover {
  background: rgba(20,50,80,0.98);
  border-color: rgba(103,232,249,0.7);
  box-shadow: 0 0 18px rgba(103,232,249,0.18);
}
.mic-btn.active {
  background: linear-gradient(135deg, rgba(16,185,129,0.22), rgba(103,232,249,0.18));
  border-color: rgba(52,211,153,0.7);
  color: #bbf7d0;
  box-shadow: 0 0 22px rgba(52,211,153,0.22);
  animation: micPulse 2s ease-in-out infinite;
}
.mic-btn.active .mic-icon { animation: micBounce 0.6s ease-in-out infinite alternate; }
@keyframes micPulse {
  0%,100% { box-shadow: 0 0 16px rgba(52,211,153,0.22); }
  50%      { box-shadow: 0 0 32px rgba(52,211,153,0.42); }
}
@keyframes micBounce {
  from { transform: scale(1.0); }
  to   { transform: scale(1.18); }
}
.mic-icon { font-size: 16px; line-height: 1; }

/* Indicateur statut et périphérique */
.mic-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
  flex: 1;
}
.mic-status-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.mic-status-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #4b5563;
  flex-shrink: 0;
  transition: background 0.3s ease, box-shadow 0.3s ease;
}
.mic-status-dot.active  { background: #34d399; box-shadow: 0 0 8px rgba(52,211,153,0.6); }
.mic-status-dot.speaking { background: #7dd3fc; box-shadow: 0 0 8px rgba(125,211,252,0.5); }
.mic-status-dot.error   { background: #f87171; box-shadow: 0 0 8px rgba(248,113,113,0.5); }
#mic-status-text {
  font-size: 12px;
  font-weight: 700;
  color: #a8c8d8;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mic-device-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.mic-device-icon { font-size: 13px; opacity: 0.7; }
#mic-device-text {
  font-size: 11px;
  color: #607080;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-style: italic;
}

/* Volume live dans la barre */
.mic-vol-badge {
  font-size: 11px;
  font-weight: 700;
  font-family: Consolas, monospace;
  color: rgba(103,232,249,0.55);
  min-width: 34px;
  text-align: right;
  flex-shrink: 0;
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
              <div class="particle-field" id="particle-field"></div>
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
            Micro actif automatiquement. Dites "salut assista" pour sortir LYRA de la veille.
          </div>
        </div>
        <div class="feed-body" id="feed-body"></div>
      </aside>
    </section>

    <!-- ── Barre contrôle micro ── -->
    <section class="mic-bar" id="mic-bar">
      <!-- Bouton ON/OFF micro -->
      <button class="mic-btn" id="mic-toggle-btn" onclick="toggleMic()">
        <span class="mic-icon">🎙</span>
        <span id="mic-btn-label">Activer le micro</span>
      </button>

      <!-- Statut temps réel + périphérique -->
      <div class="mic-info">
        <div class="mic-status-row">
          <div class="mic-status-dot" id="mic-status-dot"></div>
          <span id="mic-status-text">Micro inactif</span>
        </div>
        <div class="mic-device-row">
          <span class="mic-device-icon" id="mic-device-icon">🎧</span>
          <span id="mic-device-text">Aucun périphérique sélectionné</span>
        </div>
      </div>

      <!-- Volume en direct -->
      <span class="mic-vol-badge" id="mic-vol-badge">0%</span>
    </section>

    <section class="recorder" id="recorder">
      <div class="recorder-label" id="recorder-label">Signal micro</div>
      <div class="recorder-vol" id="recorder-vol">0%</div>
      <div class="recorder-rail" id="recorder-rail"></div>
    </section>

    <footer class="footnote">
      <div><strong>Usage</strong> Ouvrez LYRA, dites "salut assista", puis parlez naturellement. Pour une action sensible, répondez "oui" ou "non".</div>
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

// Niveau lissé pour les animations (évite les sauts)
let smoothedLevel = 0.0;
let smoothedSpeakLevel = 0.0;

// ═══════════════════════════════════════════════════
//  WEBGL — EFFET EAU SUR LA BULLE
// ═══════════════════════════════════════════════════
(function initOrbShader() {
  const canvas = document.getElementById("orb-canvas");
  const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
  if (!gl) return; // Fallback silencieux si WebGL indisponible

  // ── Vertex shader (plein écran) ──
  const vsrc = `
    attribute vec2 a_pos;
    void main() { gl_Position = vec4(a_pos, 0.0, 1.0); }
  `;

  // ── Fragment shader — eau turbulente ──
  const fsrc = `
    precision highp float;
    uniform vec2  u_res;
    uniform float u_time;
    uniform float u_energy;   // 0..1 = intensité (voix)
    uniform float u_speak;    // 0..1 = LYRA parle

    // Bruit simplex 2D léger
    vec3 permute(vec3 x) { return mod(((x*34.0)+1.0)*x, 289.0); }
    float snoise(vec2 v) {
      const vec4 C = vec4(0.211324865405187,0.366025403784439,-0.577350269189626,0.024390243902439);
      vec2 i  = floor(v + dot(v, C.yy));
      vec2 x0 = v - i + dot(i, C.xx);
      vec2 i1 = (x0.x > x0.y) ? vec2(1.0,0.0) : vec2(0.0,1.0);
      vec4 x12 = x0.xyxy + C.xxzz;
      x12.xy -= i1;
      i = mod(i, 289.0);
      vec3 p = permute(permute(i.y + vec3(0.0,i1.y,1.0)) + i.x + vec3(0.0,i1.x,1.0));
      vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy), dot(x12.zw,x12.zw)), 0.0);
      m = m*m; m = m*m;
      vec3 x = 2.0 * fract(p * C.www) - 1.0;
      vec3 h = abs(x) - 0.5;
      vec3 ox = floor(x + 0.5);
      vec3 a0 = x - ox;
      m *= 1.79284291400159 - 0.85373472095314*(a0*a0+h*h);
      vec3 g;
      g.x  = a0.x  * x0.x  + h.x  * x0.y;
      g.yz = a0.yz * x12.xz + h.yz * x12.yw;
      return 130.0 * dot(m, g);
    }

    void main() {
      vec2 uv = gl_FragCoord.xy / u_res;
      vec2 p  = uv * 2.0 - 1.0;

      // Masque circulaire
      float dist = length(p);
      float mask = 1.0 - smoothstep(0.88, 1.0, dist);
      if (mask < 0.001) { gl_FragColor = vec4(0.0); return; }

      float t     = u_time;
      float nrg   = u_energy;
      float spk   = u_speak;

      // ── Couches de bruit eau ──
      float speed1 = 0.18 + nrg * 0.55;
      float speed2 = 0.11 + nrg * 0.38;
      float amp1   = 0.18 + nrg * 0.52 + spk * 0.28;
      float amp2   = 0.12 + nrg * 0.38;

      float n1 = snoise(p * 2.4 + vec2(t * speed1, t * speed1 * 0.7)) * amp1;
      float n2 = snoise(p * 4.1 + vec2(-t * speed2, t * speed2 * 1.3)) * amp2;
      float n3 = snoise(p * 7.2 + vec2(t * 0.09, -t * 0.13)) * 0.07;
      float wave = n1 + n2 + n3;

      // ── Couleurs de base ──
      vec3 deep    = vec3(0.02, 0.04, 0.18);   // bleu très sombre
      vec3 mid     = vec3(0.05, 0.28, 0.62);   // bleu-cyan
      vec3 bright  = vec3(0.10, 0.78, 0.92);   // cyan vif
      vec3 purple  = vec3(0.42, 0.12, 0.88);   // violet
      vec3 speak_c = vec3(0.28, 0.92, 0.78);   // vert-cyan quand LYRA parle

      // Mélange selon le bruit
      float t1 = clamp(wave * 1.4 + 0.5, 0.0, 1.0);
      float t2 = clamp(wave * 0.8 + 0.3 + nrg * 0.3, 0.0, 1.0);
      vec3 col = mix(deep, mix(mid, bright, t1), t2);

      // Touche de violet en périphérie
      float edge = 1.0 - smoothstep(0.55, 0.88, dist);
      col = mix(col, purple, (1.0 - edge) * 0.35);

      // Colorisation quand LYRA parle
      col = mix(col, speak_c, spk * 0.32 * t1);

      // Energie = saturation + luminosité
      col = mix(col, col * (1.0 + nrg * 0.6), nrg * 0.5);
      col *= 0.88 + nrg * 0.26 + spk * 0.18;

      // Vignette douce sur les bords
      col *= mix(0.72, 1.0, edge);

      // Reflet interne de lumière
      float shine = max(0.0, snoise(p * 3.2 + vec2(t*0.07, t*0.05)));
      col += shine * 0.09 * mask;

      gl_FragColor = vec4(col * mask, mask * 0.97);
    }
  `;

  function compileShader(type, src) {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    return s;
  }

  const prog = gl.createProgram();
  gl.attachShader(prog, compileShader(gl.VERTEX_SHADER, vsrc));
  gl.attachShader(prog, compileShader(gl.FRAGMENT_SHADER, fsrc));
  gl.linkProgram(prog);
  gl.useProgram(prog);

  // Quad plein écran
  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
  const aPos = gl.getAttribLocation(prog, "a_pos");
  gl.enableVertexAttribArray(aPos);
  gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

  const uRes    = gl.getUniformLocation(prog, "u_res");
  const uTime   = gl.getUniformLocation(prog, "u_time");
  const uEnergy = gl.getUniformLocation(prog, "u_energy");
  const uSpeak  = gl.getUniformLocation(prog, "u_speak");

  gl.enable(gl.BLEND);
  gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

  let startTime = performance.now();

  function resizeCanvas() {
    const size = canvas.parentElement.offsetWidth;
    canvas.width  = size;
    canvas.height = size;
    gl.viewport(0, 0, size, size);
  }
  resizeCanvas();
  new ResizeObserver(resizeCanvas).observe(canvas.parentElement);

  function renderFrame() {
    const t = (performance.now() - startTime) / 1000;
    gl.clearColor(0,0,0,0);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.uniform2f(uRes, canvas.width, canvas.height);
    gl.uniform1f(uTime, t);
    gl.uniform1f(uEnergy, smoothedLevel);
    gl.uniform1f(uSpeak, smoothedSpeakLevel);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    requestAnimationFrame(renderFrame);
  }
  renderFrame();
})();

// ═══════════════════════════════════════════════════
//  BARRES SIGNAL MICRO
// ═══════════════════════════════════════════════════
const BAR_COUNT = 48;
let barHeights = new Float32Array(BAR_COUNT); // hauteurs cibles lissées
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

  const maxH = 44; // hauteur max en px

  for (let i = 0; i < BAR_COUNT; i++) {
    const bar = document.getElementById("rb"+i);
    if (!bar) continue;

    // Onde sinusoïdale dépendante du signal
    const phase = barPhases[i] + t * (0.8 + level * 4.0);
    const wave  = (Math.sin(phase) + 1) / 2;           // 0..1

    let target;
    if (level > 0.03) {
      // Signal détecté : barres qui montent vraiment
      // Centre plus haut, bords plus bas (forme cloche)
      const center = i / (BAR_COUNT - 1); // 0..1
      const bell   = Math.exp(-Math.pow((center - 0.5) * 2.8, 2));
      const noise  = wave * 0.35;
      target = level * bell * 0.88 + noise * level + 0.04;
    } else {
      // Inactif : animation très calme
      target = 0.03 + wave * 0.05;
    }
    target = Math.max(0.02, Math.min(1.0, target));

    // Lissage par barre (attaque rapide, relâchement lent)
    const prev = barHeights[i];
    barHeights[i] = target > prev
      ? prev + (target - prev) * 0.55  // attaque rapide
      : prev + (target - prev) * 0.18; // relâchement lent

    const h = Math.round(barHeights[i] * maxH);
    bar.style.height  = Math.max(3, h) + "px";
    bar.style.opacity = String(0.25 + barHeights[i] * 0.75);

    // Couleur : cyan pâle → violet vif selon intensité
    const r = Math.round(103 + (167-103) * barHeights[i]);
    const g = Math.round(232 - 232 * barHeights[i] * 0.5);
    const b = Math.round(249 - (249-250) * barHeights[i]);
    bar.style.background = `linear-gradient(180deg, rgb(${r},${g},${b}), rgba(103,232,249,0.9))`;
  }
}

// ═══════════════════════════════════════════════════
//  BOUCLE D'ANIMATION PRINCIPALE
// ═══════════════════════════════════════════════════
let lastRaf = 0;
function animLoop(ts) {
  const t = ts / 1000;

  // Lisser le niveau utilisateur (évite les sauts brutaux)
  const rawLevel = currentState.user_signal_level || 0;
  const rawSpeak = currentState.speech_level || 0;
  smoothedLevel      = smoothedLevel      + (rawLevel - smoothedLevel)      * 0.18;
  smoothedSpeakLevel = smoothedSpeakLevel + (rawSpeak - smoothedSpeakLevel) * 0.14;

  // Barres
  updateBars(smoothedLevel, t);

  // Orb CSS glow réactif (le WebGL gère déjà le contenu, on bouge juste le glow externe)
  const core = document.getElementById("orb-core");
  if (core) {
    const speaking = currentState.voice_speaking;
    const energy   = speaking
      ? 0.5 + smoothedSpeakLevel * 0.8
      : smoothedLevel > 0.04 ? 0.3 + smoothedLevel * 0.6
      : currentState.voice_awake ? 0.25 : 0.08;

    const c1a = Math.round(28  + energy * 80);
    const c2a = Math.round(22  + energy * 70);
    const c3a = Math.round(12  + energy * 48);
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
//  CONTRÔLE MICRO — bouton toggle
// ═══════════════════════════════════════════════════
let _micTogglingInProgress = false;

async function toggleMic() {
  if (_micTogglingInProgress) return;
  _micTogglingInProgress = true;
  const btn = document.getElementById("mic-toggle-btn");
  const label = document.getElementById("mic-btn-label");
  btn.disabled = true;
  try {
    let state;
    if (currentState.voice_listening) {
      label.textContent = "Arrêt…";
      state = await window.pywebview.api.stop_voice();
    } else {
      label.textContent = "Démarrage…";
      state = await window.pywebview.api.start_voice();
    }
    renderState(state);
  } catch(e) {
    console.error("toggleMic error:", e);
  } finally {
    btn.disabled = false;
    _micTogglingInProgress = false;
  }
}

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
function seedParticles() {
  const field = document.getElementById("particle-field");
  const parts = [];
  for (let i = 0; i < 80; i++) {
    const size     = (Math.random()*6+2).toFixed(2)+"px";
    const left     = (Math.random()*82+9).toFixed(2)+"%";
    const top      = (Math.random()*82+9).toFixed(2)+"%";
    const delay    = (Math.random()*5).toFixed(2)+"s";
    const duration = (Math.random()*4+5).toFixed(2)+"s";
    parts.push(`<span class="particle" style="--size:${size};--left:${left};--top:${top};--delay:${delay};--duration:${duration};"></span>`);
  }
  field.innerHTML = parts.join("");
}

// ═══════════════════════════════════════════════════
//  RENDU ÉTAT
// ═══════════════════════════════════════════════════
function renderState(state) {
  currentState = state || currentState;
  renderOrb();
  renderFeed();
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
          : "Activation du mode vocal...")));

  let label = "LYRA en veille";
  if (currentState.voice_speaking)       label = "LYRA parle";
  else if (currentState.busy)            label = "LYRA réfléchit";
  else if (currentState.voice_awake)     label = "LYRA réveillée";
  else if (currentState.voice_listening) label = "LYRA écoute le mot-clé";

  document.getElementById("orb-state").textContent     = label;
  document.getElementById("orb-transcript").textContent = transcript;
  document.getElementById("mic-chip").textContent = currentState.voice_listening ? "Micro ON" : "Micro OFF";
  document.getElementById("mic-chip").classList.toggle("live", !!currentState.voice_listening);
  document.getElementById("speak-chip").textContent = currentState.voice_speaking ? "Voix active" : "Voix en veille";
  document.getElementById("speak-chip").classList.toggle("live", !!currentState.voice_speaking);
  document.getElementById("mode-chip").textContent = currentState.voice_awake ? "Conversation active" : "Veille vocale";
  document.getElementById("mode-chip").classList.toggle("live", !!currentState.voice_awake);
  document.getElementById("status-line").textContent   = currentState.status_text || currentState.voice_status || "Conversation vocale active.";
  document.getElementById("feed-copy").textContent     = currentState.voice_status || 'LYRA écoute déjà. Dites simplement "salut assista".';

  // ── Nouvelle barre micro ───────────────────────────────────────────
  const listening = !!currentState.voice_listening;
  const speaking  = !!currentState.voice_speaking;
  const volPct    = Math.round((currentState.user_signal_level || 0) * 100);

  // Bouton toggle
  const btn   = document.getElementById("mic-toggle-btn");
  const lbl   = document.getElementById("mic-btn-label");
  if (btn) {
    btn.classList.toggle("active", listening);
    lbl.textContent = listening ? "Micro actif" : "Activer le micro";
  }

  // Statut dot + texte
  const dot  = document.getElementById("mic-status-dot");
  const stxt = document.getElementById("mic-status-text");
  if (dot && stxt) {
    dot.className = "mic-status-dot";
    if (speaking) {
      dot.classList.add("speaking");
      stxt.textContent = "LYRA parle";
    } else if (listening && currentState.voice_awake) {
      dot.classList.add("active");
      stxt.textContent = "Conversation ouverte";
    } else if (listening) {
      dot.classList.add("active");
      stxt.textContent = volPct > 6
        ? "Voix détectée — " + volPct + "%"
        : "En écoute — mot-clé";
    } else {
      stxt.textContent = "Micro inactif";
    }
  }

  // Icône + nom du périphérique
  const deviceIcon = document.getElementById("mic-device-icon");
  const deviceText = document.getElementById("mic-device-text");
  if (deviceIcon && deviceText) {
    // Priorité : mic_device_name du state (direct de Python), sinon parsing du voice_status
    let devName = currentState.mic_device_name || "";
    if (!devName) {
      const micStatus = (currentState.voice_status || "");
      const match = micStatus.match(/sur (.+?)(?:\.|$)/i);
      devName = match ? match[1].trim() : "";
    }

    if (!listening) {
      deviceIcon.textContent = "🎙";
      deviceText.textContent = "Aucun périphérique actif";
    } else if (devName) {
      // Détecte le type de périphérique pour l'icône
      const dn = devName.toLowerCase();
      if (dn.includes("headset") || dn.includes("casque") || dn.includes("headphone") || dn.includes("earbud")) {
        deviceIcon.textContent = "🎧";
      } else if (dn.includes("bluetooth") || dn.includes("wireless")) {
        deviceIcon.textContent = "📶";
      } else if (dn.includes("webcam") || dn.includes("camera") || dn.includes("cam")) {
        deviceIcon.textContent = "📷";
      } else if (dn.includes("usb")) {
        deviceIcon.textContent = "🔌";
      } else {
        deviceIcon.textContent = "🖥";  // micro PC intégré
      }
      deviceText.textContent = devName;
    } else {
      deviceIcon.textContent = "🎙";
      deviceText.textContent = "Périphérique détecté";
    }
  }

  // Volume live dans la barre
  const volBadge = document.getElementById("mic-vol-badge");
  if (volBadge) volBadge.textContent = listening ? volPct + "%" : "—";
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
  // Le micro n'est PAS démarré automatiquement — l'utilisateur clique le bouton
  // Si le micro était déjà actif (redémarrage), on synchronise l'état
  if (state.voice_listening) {
    renderState(state);
  }
}

window.addEventListener("DOMContentLoaded", function() {
  seedParticles();
  seedRecorder();
  const boot = setInterval(function() {
    if (window.pywebview && window.pywebview.api) {
      clearInterval(boot);
      bootVoiceLoop();
      // Polling état à 120ms pour les niveaux audio
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