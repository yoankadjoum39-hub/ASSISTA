# assista_ui.py — Interface ASSISTA v2 — Lab complet
# 3 colonnes : Stage sphère | Feed messages | Panneau Outils
# Streaming token-par-token, Shell Log, Mémoire, Plan overlay enrichi

from nexus_core.history_db import normalize_display_text

ASSISTA_HTML = normalize_display_text(r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ASSISTA</title>
<style>
/* ══════════════════════════════════════════════
   BASE & VARS
══════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');

:root {
  --bg:          #040a10;
  --surface:     #06101a;
  --surface2:    #080f1a;
  --border:      rgba(56,180,255,0.13);
  --border2:     rgba(56,180,255,0.07);
  --accent:      #38b4ff;
  --accent2:     #a78bfa;
  --accent3:     #3ce1ff;
  --text:        #d4e8ff;
  --text-dim:    rgba(212,232,255,0.42);
  --danger:      #f85149;
  --ok:          #39d98a;
  --warn:        #f4d35e;
  --safe:        #39d98a;
  --moderate:    #f4d35e;
  --dangerous:   #f85149;
  --font-ui:     'Rajdhani','Segoe UI',sans-serif;
  --font-mono:   'Share Tech Mono',monospace;
  --feed-w:      360px;
  --panel-w:     300px;
}
html, body { height:100%; width:100%; overflow:hidden; background:var(--bg); color:var(--text); font-family:var(--font-ui); }

/* ══════════════════════════════════════════════
   LAYOUT — 3 colonnes
══════════════════════════════════════════════ */
.shell {
  display: grid;
  grid-template-rows: 54px 1fr 76px 36px;
  grid-template-columns: 1fr var(--feed-w) var(--panel-w);
  grid-template-areas:
    "topline topline topline"
    "stage   feed    panel"
    "micbar  feed    panel"
    "foot    foot    foot";
  height: 100vh; width: 100%;
}

/* ══════════════════════════════════════════════
   TOPLINE
══════════════════════════════════════════════ */
.topline {
  grid-area: topline;
  display:flex; align-items:center;
  padding: 0 20px;
  background: rgba(4,10,16,0.95);
  border-bottom: 1px solid var(--border);
  gap: 16px; backdrop-filter: blur(12px); z-index:10;
}
.brand-box { display:flex; flex-direction:column; }
.brand {
  font-size:21px; font-weight:700; letter-spacing:4px;
  background: linear-gradient(90deg, var(--accent), var(--accent2), var(--accent3));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; line-height:1;
}
.subline { font-size:9px; color:var(--text-dim); letter-spacing:2px; margin-top:2px; }

.status-cluster { display:flex; gap:6px; margin-left:auto; align-items:center; }
.chip {
  font-size:10px; font-weight:600; letter-spacing:0.8px;
  padding:3px 10px; border-radius:20px;
  border:1px solid var(--border); background:rgba(56,180,255,0.05);
  color:var(--text-dim); transition:all .3s; font-family:var(--font-mono);
}
.chip.active   { border-color:var(--accent);  color:var(--accent);  background:rgba(56,180,255,0.10); }
.chip.speaking { border-color:var(--accent2); color:var(--accent2); background:rgba(167,139,250,0.10); }
.chip.awake    { border-color:var(--ok);      color:var(--ok);      background:rgba(57,217,138,0.10); }
.chip.busy     { border-color:var(--warn);    color:var(--warn);    background:rgba(244,211,94,0.10); animation:pulse 1s infinite; }

/* Autopilot */
.autopilot-wrap { display:flex; align-items:center; gap:6px; }
.ap-label { font-size:10px; letter-spacing:1px; color:var(--text-dim); font-weight:600; }
.ap-toggle {
  position:relative; width:38px; height:20px;
  background:#1a2030; border-radius:10px;
  border:1px solid var(--border); cursor:pointer; transition:background .3s;
}
.ap-toggle.on { background:rgba(56,180,255,0.22); border-color:var(--accent); }
.ap-toggle::after {
  content:''; position:absolute; width:14px; height:14px;
  background:var(--text-dim); border-radius:50%;
  top:2px; left:2px; transition:all .3s;
}
.ap-toggle.on::after { left:20px; background:var(--accent); }

/* Topline buttons */
.top-btn {
  background:rgba(56,180,255,0.06); border:1px solid var(--border);
  color:var(--text-dim); border-radius:6px; padding:4px 10px;
  font-size:10px; font-weight:600; letter-spacing:1px; cursor:pointer;
  transition:all .2s; font-family:var(--font-mono);
}
.top-btn:hover { color:var(--accent); border-color:var(--accent); background:rgba(56,180,255,0.10); }
.top-btn.speaking {
  border-color:rgba(167,139,250,0.6); color:var(--accent2);
  background:rgba(167,139,250,0.14); animation:pulse 1s infinite;
}
.top-btn.handsfree {
  border-color:rgba(57,217,138,0.35);
  color:var(--ok);
  background:rgba(57,217,138,0.08);
}
.top-btn.handsfree.on {
  color:#04100a;
  background:var(--ok);
  border-color:var(--ok);
}

/* ══════════════════════════════════════════════
   STAGE (sphère)
══════════════════════════════════════════════ */
.center-stage {
  grid-area: stage;
  position:relative; overflow:hidden;
  display:flex; align-items:center; justify-content:center;
}
.center-stage::before {
  content:''; position:absolute; inset:0;
  background:
    radial-gradient(circle at 30% 30%, rgba(56,180,255,0.07),transparent 40%),
    radial-gradient(circle at 72% 70%, rgba(167,139,250,0.06),transparent 40%);
  pointer-events:none; z-index:1;
}
#sphere-canvas-wrap { position:absolute; inset:0; z-index:0; }
#sphere-canvas-wrap canvas { width:100%!important; height:100%!important; }
.orb-label {
  position:absolute; bottom:28px; left:50%; transform:translateX(-50%);
  text-align:center; z-index:4; pointer-events:none;
}
.orb-state {
  font-size:12px; font-weight:600; letter-spacing:2px;
  color:var(--accent); text-transform:uppercase; font-family:var(--font-mono);
  text-shadow:0 0 20px rgba(56,180,255,0.65);
}
.orb-transcript { font-size:11px; color:var(--text-dim); margin-top:4px; letter-spacing:.4px; max-width:400px; }

/* Streaming bubble flottant sur la sphère */
#stream-bubble {
  position:absolute; top:20px; left:50%; transform:translateX(-50%);
  max-width:70%; z-index:5; display:none;
  background:rgba(6,10,18,0.88); border:1px solid rgba(56,180,255,0.25);
  border-radius:12px; padding:12px 16px; font-size:12px; line-height:1.6;
  color:var(--text); backdrop-filter:blur(10px);
  font-family:var(--font-ui); box-shadow:0 8px 32px rgba(0,0,0,0.4);
}
#stream-bubble.show { display:block; }
.stream-cursor { display:inline-block; width:7px; height:13px; background:var(--accent); margin-left:2px; animation:blink .6s infinite; }

/* Plan overlay */
.plan-overlay {
  position:absolute; inset:0; z-index:20;
  background:rgba(4,10,16,0.94); backdrop-filter:blur(18px);
  display:none; flex-direction:column; align-items:center; justify-content:center;
  gap:18px; padding:36px;
}
.plan-overlay.show { display:flex; }
.plan-title { font-size:17px; font-weight:700; letter-spacing:2px; color:var(--warn); font-family:var(--font-mono); }
.plan-summary { font-size:12px; color:var(--text-dim); text-align:center; max-width:500px; }
.plan-steps { width:100%; max-width:560px; }
.plan-step {
  display:flex; gap:10px; align-items:flex-start;
  padding:9px 0; border-bottom:1px solid var(--border);
  font-size:12px; color:var(--text);
}
.plan-step:last-child { border-bottom:none; }
.step-num {
  min-width:24px; height:24px; border-radius:50%;
  background:rgba(244,211,94,0.12); color:var(--warn);
  font-size:11px; font-weight:700; display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
.step-risk {
  font-size:9px; font-weight:700; letter-spacing:0.8px; text-transform:uppercase;
  padding:2px 6px; border-radius:4px; align-self:center; flex-shrink:0;
}
.step-risk.safe      { background:rgba(57,217,138,0.12); color:var(--safe); border:1px solid rgba(57,217,138,0.25); }
.step-risk.moderate  { background:rgba(244,211,94,0.12); color:var(--moderate); border:1px solid rgba(244,211,94,0.25); }
.step-risk.dangerous { background:rgba(248,81,73,0.12); color:var(--danger); border:1px solid rgba(248,81,73,0.25); }
.step-risk.blocked   { background:rgba(248,81,73,0.25); color:#fff; border:1px solid rgba(248,81,73,0.5); }
.plan-step-detail { flex:1; min-width:0; }
.plan-step-title { font-weight:600; }
.plan-step-cmd { font-family:var(--font-mono); font-size:10px; color:var(--text-dim); margin-top:3px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.plan-actions { display:flex; gap:10px; margin-top:6px; }
.btn-approve, .btn-reject {
  padding:10px 24px; border-radius:8px; border:none;
  font-size:13px; font-weight:700; cursor:pointer;
  letter-spacing:1px; transition:all .2s; font-family:var(--font-ui);
}
.btn-approve { background:rgba(57,217,138,0.14); color:var(--ok); border:1px solid rgba(57,217,138,0.28); }
.btn-approve:hover { background:var(--ok); color:#040a10; }
.btn-reject  { background:rgba(248,81,73,0.10); color:var(--danger); border:1px solid rgba(248,81,73,0.22); }
.btn-reject:hover  { background:var(--danger); color:#fff; }

/* ══════════════════════════════════════════════
   FEED PANEL
══════════════════════════════════════════════ */
.feed-panel {
  grid-area: feed; display:flex; flex-direction:column;
  border-left:1px solid var(--border); background:var(--surface); overflow:hidden;
}
.feed-head {
  padding:10px 14px; border-bottom:1px solid var(--border);
  display:flex; align-items:center; justify-content:space-between; flex-shrink:0;
}
.feed-title { font-size:10px; font-weight:700; letter-spacing:2px; color:var(--text-dim); }
.feed-actions { display:flex; gap:6px; }
.feed-btn {
  font-size:10px; color:var(--text-dim); cursor:pointer; padding:3px 8px;
  border-radius:5px; border:1px solid var(--border); transition:all .2s; font-family:var(--font-mono);
}
.feed-btn:hover { color:var(--accent); border-color:var(--accent); }
.feed-body { flex:1; overflow-y:auto; padding:10px; display:flex; flex-direction:column; gap:8px; }
.feed-body::-webkit-scrollbar { width:4px; }
.feed-body::-webkit-scrollbar-thumb { background:rgba(56,180,255,0.2); border-radius:2px; }

/* Messages */
.msg-bubble {
  max-width:92%; border-radius:10px; padding:9px 12px;
  font-size:12px; line-height:1.6; animation:fadeUp .22s ease;
}
.msg-bubble.user {
  align-self:flex-end;
  background:rgba(56,180,255,0.09); border:1px solid rgba(56,180,255,0.18); color:var(--text);
}
.msg-bubble.assista {
  align-self:flex-start;
  background:rgba(167,139,250,0.07); border:1px solid rgba(167,139,250,0.16); color:var(--text);
}
.msg-bubble .msg-meta { font-size:9px; color:var(--text-dim); margin-top:5px; }
.msg-bubble code { font-family:var(--font-mono); background:rgba(56,180,255,0.08); padding:1px 5px; border-radius:3px; font-size:11px; }
.msg-bubble pre { background:rgba(0,0,0,0.35); border:1px solid var(--border2); border-radius:6px; padding:8px 10px; overflow-x:auto; margin:6px 0; }
.msg-bubble pre code { background:none; padding:0; font-size:11px; }

/* Streaming message en cours */
.msg-bubble.streaming { border-color:rgba(56,180,255,0.35); opacity:0.9; }

/* Chips d'action dans le feed */
.action-chip {
  display:inline-flex; align-items:center; gap:5px;
  font-size:10px; padding:2px 8px; border-radius:20px; margin:2px 2px 2px 0;
  font-family:var(--font-mono); font-weight:600;
}
.action-chip.ok   { background:rgba(57,217,138,0.10); border:1px solid rgba(57,217,138,0.25); color:var(--ok); }
.action-chip.err  { background:rgba(248,81,73,0.10);  border:1px solid rgba(248,81,73,0.22);  color:var(--danger); }
.action-chip.run  { background:rgba(56,180,255,0.10); border:1px solid rgba(56,180,255,0.22); color:var(--accent); }

/* ══════════════════════════════════════════════
   VIBRATION MICRO — canvas dédié
══════════════════════════════════════════════ */
#mic-vibe-canvas {
  position:absolute; bottom:0; left:0; width:100%; height:64px;
  pointer-events:none; z-index:3;
}

/* ══════════════════════════════════════════════
   MIC BAR
══════════════════════════════════════════════ */
.mic-bar {
  grid-area: micbar;
  display:flex; align-items:center; gap:10px; padding:0 20px;
  border-top:1px solid var(--border); background:rgba(4,10,16,0.92);
}
#prompt-input {
  flex:1; background:rgba(8,16,26,0.9); border:1px solid var(--border);
  border-radius:10px; padding:8px 14px; color:var(--text); font-size:13px;
  font-family:var(--font-ui); outline:none; transition:border-color .2s;
  resize:none; height:44px; line-height:1.4; overflow:hidden;
}
#prompt-input:focus { border-color:rgba(56,180,255,0.4); }
.mic-btn {
  width:44px; height:44px; border-radius:50%;
  background:rgba(56,180,255,0.08); border:1px solid var(--border);
  display:flex; align-items:center; justify-content:center;
  cursor:pointer; transition:all .3s; font-size:18px; flex-shrink:0;
}
.mic-btn:hover { border-color:var(--accent); background:rgba(56,180,255,0.15); }
.mic-btn.active { background:rgba(56,180,255,0.22); border-color:var(--accent); animation:pulse 1.5s infinite; }
.mic-calib-btn {
  width:44px; height:20px; border-radius:5px;
  background:rgba(56,180,255,0.05); border:1px solid rgba(56,180,255,0.15);
  color:rgba(56,180,255,0.4); font-size:11px; cursor:pointer; transition:all 0.2s;
}
.mic-calib-btn:hover { background:rgba(56,180,255,0.12); color:#38b4ff; }
.send-btn {
  padding:0 18px; height:44px; border-radius:10px; flex-shrink:0;
  background:rgba(56,180,255,0.12); border:1px solid rgba(56,180,255,0.3);
  color:var(--accent); font-size:12px; font-weight:700; letter-spacing:1px;
  cursor:pointer; transition:all .2s; font-family:var(--font-ui);
}
.send-btn:hover { background:var(--accent); color:#040a10; }
.rec-rail {
  display:flex; align-items:flex-end; gap:2px; height:28px;
  overflow:hidden; padding:4px 0;
}
.rec-bar { width:3px; min-height:4px; background:var(--accent); border-radius:2px; transition:height .08s, background .08s; }
#mic-vol-badge { font-size:9px; color:var(--text-dim); font-family:var(--font-mono); width:28px; text-align:center; }

/* ══════════════════════════════════════════════
   PANEL DROIT — Outils (onglets)
══════════════════════════════════════════════ */
.right-panel {
  grid-area: panel;
  display:flex; flex-direction:column;
  border-left:1px solid var(--border); background:var(--surface2); overflow:hidden;
}
.panel-tabs {
  display:flex; border-bottom:1px solid var(--border); flex-shrink:0; background:rgba(4,10,16,0.8);
}
.panel-tab {
  flex:1; padding:8px 0; font-size:10px; font-weight:700; letter-spacing:0.8px;
  text-align:center; cursor:pointer; color:var(--text-dim); border:none; background:transparent;
  border-bottom:2px solid transparent; transition:all .18s; text-transform:uppercase;
}
.panel-tab:hover { color:var(--text); }
.panel-tab.active { color:var(--accent); border-bottom-color:var(--accent); background:rgba(56,180,255,0.05); }
.panel-body { flex:1; overflow:hidden; }
.panel-page { height:100%; overflow-y:auto; padding:12px; display:none; }
.panel-page.active { display:block; }
.panel-page::-webkit-scrollbar { width:3px; }
.panel-page::-webkit-scrollbar-thumb { background:rgba(56,180,255,0.15); }

/* Shell log */
.log-entry {
  padding:7px 9px; border-radius:6px; margin-bottom:5px;
  border:1px solid var(--border2); font-family:var(--font-mono); font-size:10px;
  line-height:1.5;
}
.log-entry.ok   { border-color:rgba(57,217,138,0.2); background:rgba(57,217,138,0.04); }
.log-entry.err  { border-color:rgba(248,81,73,0.2);  background:rgba(248,81,73,0.04); }
.log-entry.blocked { border-color:rgba(248,81,73,0.35); background:rgba(248,81,73,0.08); }
.log-entry.timeout { border-color:rgba(244,211,94,0.25); background:rgba(244,211,94,0.05); }
.log-ts  { font-size:9px; color:var(--text-dim); margin-bottom:3px; }
.log-cmd { color:var(--accent3); word-break:break-all; }
.log-detail { color:var(--text-dim); font-size:9px; margin-top:2px; }

/* Mémoire */
.fact-item {
  padding:6px 9px; border-radius:6px; margin-bottom:4px; font-size:11px;
  background:rgba(167,139,250,0.06); border:1px solid rgba(167,139,250,0.14);
  color:var(--text-dim); line-height:1.5;
}
.fact-item::before { content:'▸ '; color:var(--accent2); }
.mem-section-title {
  font-size:9px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase;
  color:var(--text-dim); margin:10px 0 6px; padding-bottom:4px;
  border-bottom:1px solid var(--border2);
}
.panel-action-btn {
  width:100%; padding:7px; border-radius:7px; margin-bottom:6px;
  background:rgba(248,81,73,0.09); border:1px solid rgba(248,81,73,0.22);
  color:var(--danger); font-size:11px; font-weight:700; cursor:pointer; letter-spacing:0.5px;
  transition:all .2s;
}
.panel-action-btn:hover { background:rgba(248,81,73,0.2); }
.panel-action-btn.safe {
  background:rgba(56,180,255,0.08); border-color:rgba(56,180,255,0.22); color:var(--accent);
}
.panel-action-btn.safe:hover { background:rgba(56,180,255,0.18); }

/* Contexte PC */
.ctx-item { padding:5px 8px; margin-bottom:4px; font-size:11px; border-radius:5px; background:rgba(56,180,255,0.05); border:1px solid var(--border2); }
.ctx-label { font-size:9px; color:var(--text-dim); letter-spacing:0.8px; text-transform:uppercase; margin-bottom:1px; }
.ctx-val   { color:var(--accent3); font-family:var(--font-mono); font-size:10px; word-break:break-all; }

/* Config overlay */
.config-overlay {
  position:fixed; inset:0; z-index:100;
  background:rgba(4,10,16,0.95); backdrop-filter:blur(16px);
  display:none; align-items:center; justify-content:center;
}
.config-overlay.show { display:flex; }
.config-box {
  background:var(--surface); border:1px solid var(--border);
  border-radius:14px; padding:28px; width:460px;
  box-shadow:0 24px 80px rgba(0,0,0,0.6);
  max-height:90vh; overflow-y:auto;
}
.cfg-title { font-size:16px; font-weight:700; letter-spacing:2px; margin-bottom:18px; color:var(--accent); font-family:var(--font-mono); }
.cfg-label { font-size:10px; letter-spacing:1px; color:var(--text-dim); margin-bottom:4px; text-transform:uppercase; }
.cfg-key-row { position:relative; display:flex; align-items:center; margin-bottom:4px; }
.cfg-key-row .cfg-input { margin-bottom:0; padding-right:36px; flex:1; }
.cfg-eye-btn {
  position:absolute; right:6px; background:none; border:none;
  color:var(--text-dim); cursor:pointer; font-size:14px; padding:0 4px;
  transition:color .2s;
}
.cfg-eye-btn:hover { color:var(--accent); }
.cfg-env-note { font-size:9px; color:var(--ok); font-family:var(--font-mono); margin-bottom:8px; min-height:14px; }
.cfg-input {
  width:100%; background:rgba(8,16,26,0.9); border:1px solid var(--border);
  border-radius:7px; padding:8px 12px; color:var(--text); font-size:12px;
  font-family:var(--font-mono); outline:none; margin-bottom:12px;
}
.cfg-input:focus { border-color:rgba(56,180,255,0.4); }

/* Mode buttons */
.cfg-mode-row { display:flex; gap:8px; margin-bottom:10px; }
.cfg-mode-btn {
  flex:1; padding:7px 0; border-radius:7px; font-size:11px; font-weight:700;
  cursor:pointer; border:1px solid var(--border); background:rgba(8,16,26,0.7);
  color:var(--text-dim); letter-spacing:0.5px; transition:all .2s;
}
.cfg-mode-btn.active {
  background:rgba(56,180,255,0.12); border-color:var(--accent); color:var(--accent);
}

/* Model list */
.cfg-model-list { display:flex; flex-direction:column; gap:5px; margin-bottom:8px; }
.cfg-model-opt {
  display:flex; align-items:center; gap:10px;
  padding:8px 12px; border-radius:7px; cursor:pointer;
  border:1px solid var(--border); background:rgba(8,16,26,0.6);
  transition:all .2s;
}
.cfg-model-opt:has(input:checked) {
  border-color:rgba(56,180,255,0.5); background:rgba(56,180,255,0.08);
}
.cfg-model-opt input[type=radio] { accent-color:var(--accent); width:14px; height:14px; flex-shrink:0; }
.cfg-model-name { flex:1; font-size:12px; font-family:var(--font-mono); color:var(--text); }
.cfg-model-tag {
  font-size:9px; padding:1px 6px; border-radius:10px;
  background:rgba(57,217,138,0.12); color:var(--ok); border:1px solid rgba(57,217,138,0.25);
  letter-spacing:0.5px; font-weight:700;
}

.cfg-hint { font-size:10px; color:var(--text-dim); margin-bottom:14px; line-height:1.5; }
.cfg-btns { display:flex; gap:10px; justify-content:flex-end; margin-top:6px; }
.cfg-btn {
  padding:8px 20px; border-radius:7px; font-size:12px; font-weight:700;
  cursor:pointer; border:none; transition:all .2s; letter-spacing:0.5px;
}
.cfg-btn.save { background:rgba(56,180,255,0.15); color:var(--accent); border:1px solid rgba(56,180,255,0.3); }
.cfg-btn.save:hover { background:var(--accent); color:#040a10; }
.cfg-btn.cancel { background:rgba(48,54,61,0.5); color:var(--text-dim); border:1px solid var(--border); }

/* ══════════════════════════════════════════════
   FOOTER
══════════════════════════════════════════════ */
.foot {
  grid-area: foot;
  display:flex; align-items:center; padding:0 18px; gap:16px;
  background:rgba(4,10,16,0.92); border-top:1px solid var(--border);
}
#status-line { font-size:10px; color:var(--text-dim); font-family:var(--font-mono); flex:1; }
.foot-links { display:flex; gap:10px; }
.foot-link { font-size:9px; color:var(--text-dim); letter-spacing:1px; cursor:pointer; text-transform:uppercase; transition:color .2s; }
.foot-link:hover { color:var(--accent); }

/* ══════════════════════════════════════════════
   ANIMATIONS
══════════════════════════════════════════════ */
@keyframes fadeUp  { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
@keyframes pulse   { 0%,100%{opacity:1} 50%{opacity:0.55} }
@keyframes blink   { 0%,100%{opacity:1} 50%{opacity:0} }
@keyframes spin    { to{transform:rotate(360deg)} }
.spinner { width:12px; height:12px; border-radius:50%; border:2px solid rgba(56,180,255,0.2); border-top-color:var(--accent); animation:spin .7s linear infinite; display:inline-block; }

/* Scrollbar global */
::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:rgba(56,180,255,0.15); border-radius:2px; }
</style>
</head>
<body>
<div class="shell">

  <!-- ══ TOPLINE ══ -->
  <header class="topline">
    <div class="brand-box">
      <div class="brand">ASSISTA</div>
      <div class="subline">PC INTELLIGENCE · v2</div>
    </div>

    <div class="status-cluster">
      <div class="chip" id="mic-chip">Micro OFF</div>
      <div class="chip" id="speak-chip">Voix en veille</div>
      <div class="chip" id="mode-chip">Veille</div>
      <div class="chip" id="busy-chip" style="display:none">⚙ Traitement</div>
    </div>

    <div class="autopilot-wrap" style="margin-left:8px">
      <span class="ap-label">AUTO</span>
      <div class="ap-toggle" id="ap-toggle" onclick="toggleAutopilot()" title="Mode Autopilot"></div>
    </div>

    <button class="top-btn" onclick="openConfig()">⚙ Config</button>
    <button class="top-btn" onclick="refreshShellLog()">📋 Log</button>
    <button class="top-btn" id="speak-btn" onclick="toggleSpeak()">🔊 Relire</button>
    <button class="top-btn handsfree" id="handsfree-btn" onclick="toggleHandsFree()">Mains libres</button>
  </header>

  <!-- ══ STAGE ══ -->
  <section class="center-stage">
    <div id="sphere-canvas-wrap"></div>

    <!-- Streaming bubble -->
    <div id="stream-bubble">
      <span id="stream-text"></span><span class="stream-cursor" id="stream-cursor"></span>
    </div>

    <div class="orb-label">
      <div class="orb-state" id="orb-state">ASSISTA</div>
      <div class="orb-transcript" id="orb-transcript">Dites "salut" ou écrivez pour commencer.</div>
    </div>

    <!-- Vibration micro -->
    <canvas id="mic-vibe-canvas"></canvas>

    <!-- Plan overlay -->
    <div class="plan-overlay" id="plan-overlay">
      <div class="plan-title">⚠ VALIDATION REQUISE</div>
      <div class="plan-summary" id="plan-summary">ASSISTA souhaite exécuter les actions suivantes :</div>
      <div class="plan-steps" id="plan-steps"></div>
      <div class="plan-actions">
        <button class="btn-approve" onclick="approvePlan()">✔ Approuver</button>
        <button class="btn-reject"  onclick="rejectPlan()">✕ Annuler</button>
      </div>
    </div>
  </section>

  <!-- ══ FEED ══ -->
  <aside class="feed-panel">
    <div class="feed-head">
      <span class="feed-title">CONVERSATION</span>
      <div class="feed-actions">
        <button class="feed-btn" onclick="copyFeed()">Copier</button>
        <button class="feed-btn" onclick="clearFeed()">Vider</button>
      </div>
    </div>
    <div class="feed-body" id="feed-body"></div>
  </aside>

  <!-- ══ MIC BAR ══ -->
  <div class="mic-bar">
    <button class="mic-btn" id="mic-toggle-btn" onclick="toggleMic()" title="Ctrl+M">🎙</button>
    <div class="rec-rail" id="rec-rail"></div>
    <span id="mic-vol-badge">0%</span>
    <textarea id="prompt-input" placeholder="Demandez n'importe quoi à ASSISTA…" onkeydown="handleKey(event)" oninput="autoGrow(this)"></textarea>
    <button class="send-btn" onclick="sendPrompt()">ENVOYER</button>
  </div>

  <!-- ══ PANEL DROIT ══ -->
  <aside class="right-panel">
    <div class="panel-tabs">
      <button class="panel-tab active" data-tab="shell" onclick="switchPanel('shell')">Shell</button>
      <button class="panel-tab" data-tab="mem" onclick="switchPanel('mem')">Mémoire</button>
      <button class="panel-tab" data-tab="ctx" onclick="switchPanel('ctx')">Contexte</button>
      <button class="panel-tab" data-tab="ops" onclick="switchPanel('ops')">Ops</button>
    </div>
    <div class="panel-body">
      <!-- Shell Log -->
      <div class="panel-page active" id="panel-shell">
        <div class="mem-section-title">Journal des commandes shell</div>
        <div id="shell-log-list"><div style="color:var(--text-dim);font-size:11px;padding:10px 0">Aucune commande exécutée.</div></div>
        <button class="panel-action-btn safe" style="margin-top:10px" onclick="refreshShellLog()">↻ Actualiser</button>
      </div>
      <!-- Mémoire -->
      <div class="panel-page" id="panel-mem">
        <div class="mem-section-title">Faits mémorisés <span id="facts-count" style="color:var(--accent);font-size:10px"></span></div>
        <div id="facts-list"><div style="color:var(--text-dim);font-size:11px;padding:10px 0">Aucun fait mémorisé.</div></div>
        <button class="panel-action-btn" onclick="confirmForget()">🗑 Effacer la mémoire</button>
        <button class="panel-action-btn safe" onclick="refreshMemory()">↻ Actualiser</button>
      </div>
      <!-- Contexte PC -->
      <div class="panel-page" id="panel-ctx">
        <div class="mem-section-title">Contexte système</div>
        <div id="ctx-info"><div style="color:var(--text-dim);font-size:11px;padding:10px 0">Chargement…</div></div>
        <div style="display:flex;gap:8px;margin-top:10px">
          <button class="panel-action-btn" style="flex:1;background:rgba(248,81,73,0.12);border-color:rgba(248,81,73,0.3);color:#f85149" onclick="startPcMapper()">🔍 Scan complet</button>
          <button class="panel-action-btn safe" style="flex:1" onclick="startQuickScan()">⚡ Scan rapide</button>
        </div>
        <div style="margin-top:8px;font-size:10px;color:var(--text-dim);line-height:1.4">
          <strong>Scan rapide</strong> : Bureau, Documents, Downloads (~5 000 fichiers, &lt;30s)<br>
          <strong>Scan complet</strong> : tous les dossiers utilisateur (~80 000 fichiers, quelques minutes)
        </div>
        <div style="margin-top:10px">
          <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--text-dim);margin-bottom:4px">
            <span id="mapper-progress-status">Progression du mapping</span>
            <span id="mapper-progress-label">0%</span>
          </div>
          <div style="height:10px;border-radius:999px;background:rgba(255,255,255,.08);overflow:hidden;border:1px solid rgba(255,255,255,.08)">
            <div id="mapper-progress-fill" style="height:100%;width:0%;background:linear-gradient(90deg,var(--accent),#7fe3ff);transition:width .4s ease"></div>
          </div>
          <div id="mapper-progress-detail" style="font-size:10px;color:var(--text-dim);margin-top:4px;word-break:break-all"></div>
        </div>
        <button class="panel-action-btn safe" onclick="refreshCtx()">↻ Actualiser</button>
      </div>
      <div class="panel-page" id="panel-ops">
        <div class="mem-section-title">Orchestration avancée</div>
        <div id="ops-info"><div style="color:var(--text-dim);font-size:11px;padding:10px 0">Chargement…</div></div>
        <button class="panel-action-btn" onclick="runSecurityAudit()">Audit sécurité</button>
        <button class="panel-action-btn safe" onclick="refreshOps()">↻ Actualiser</button>
      </div>
    </div>
  </aside>

  <!-- ══ FOOTER ══ -->
  <footer class="foot">
    <span id="status-line">Prête.</span>
    <div class="foot-links">
      <span class="foot-link" onclick="sendPrompt('aide')">Aide</span>
      <span class="foot-link" onclick="sendPrompt('liste tes commandes')">Commandes</span>
      <span class="foot-link" onclick="sendPrompt('infos système')">Système</span>
    </div>
  </footer>

</div><!-- /.shell -->

<!-- ══ CONFIG OVERLAY ══ -->
<div class="config-overlay" id="config-overlay">
  <div class="config-box">
    <div class="cfg-title">⚙ Configuration API</div>

    <div class="cfg-label">Clé API OpenRouter</div>
    <div class="cfg-key-row">
      <input class="cfg-input" id="cf-api-key" type="password" placeholder="sk-or-… (ou OPENROUTER_API_KEY env)">
      <button class="cfg-eye-btn" id="cf-eye-btn" onclick="toggleKeyVisibility()" title="Afficher/masquer">👁</button>
    </div>
    <div class="cfg-env-note" id="cfg-env-note"></div>

    <div class="cfg-label" style="margin-top:6px">Modèle LLM</div>
    <!-- Sélecteur de mode : Auto / Manuel -->
    <div class="cfg-mode-row">
      <button class="cfg-mode-btn active" id="btn-mode-auto"   onclick="setModelMode('auto')">🔄 Auto (fallback)</button>
      <button class="cfg-mode-btn"        id="btn-mode-manual" onclick="setModelMode('manual')">🎯 Choisir un modèle</button>
    </div>
    <!-- Liste de modèles (visible en mode Manuel) -->
    <div id="cfg-model-list" class="cfg-model-list" style="display:none">
      <label class="cfg-model-opt" data-model="openrouter/free">
        <input type="radio" name="cf-model-radio" value="openrouter/free">
        <span class="cfg-model-name">OpenRouter Free Router</span>
        <span class="cfg-model-tag">auto</span>
      </label>
      <label class="cfg-model-opt" data-model="deepseek/deepseek-r1:free">
        <input type="radio" name="cf-model-radio" value="deepseek/deepseek-r1:free">
        <span class="cfg-model-name">DeepSeek R1</span>
        <span class="cfg-model-tag">free</span>
      </label>
      <label class="cfg-model-opt" data-model="meta-llama/llama-3.3-70b-instruct:free">
        <input type="radio" name="cf-model-radio" value="meta-llama/llama-3.3-70b-instruct:free">
        <span class="cfg-model-name">Llama 3.3 70B</span>
        <span class="cfg-model-tag">free</span>
      </label>
      <label class="cfg-model-opt" data-model="qwen/qwen3-coder:free">
        <input type="radio" name="cf-model-radio" value="qwen/qwen3-coder:free">
        <span class="cfg-model-name">Qwen3 Coder</span>
        <span class="cfg-model-tag">free</span>
      </label>
    </div>
    <!-- Modèle custom (visible en mode Manuel, champ libre) -->
    <div id="cfg-model-custom-wrap" style="display:none; margin-top:6px">
      <input class="cfg-input" id="cf-model-custom" placeholder="ou entrez un modèle custom…" style="margin-bottom:0">
    </div>
    <!-- Modèle actif affiché en mode Auto -->
    <div id="cfg-auto-note" class="cfg-hint" style="margin-top:6px; margin-bottom:4px">
      Mode <strong>Auto</strong> : ASSISTA essaie les modèles dans l'ordre et bascule automatiquement si l'un est lent ou indisponible.<br>
      Ordre : DeepSeek R1 → Gemini 2.0 Flash → Llama 3.3 → Mistral 7B → Qwen3 Coder
    </div>

    <div class="cfg-label" style="margin-top:6px">URL de base</div>
    <input class="cfg-input" id="cf-base-url" value="https://openrouter.ai/api/v1/chat/completions">

    <div class="cfg-hint" style="margin-top:2px">
      Obtenez votre clé gratuite sur <strong>openrouter.ai</strong>. Laissez la clé vide pour utiliser la variable d'environnement <code>OPENROUTER_API_KEY</code>.
    </div>
    <div class="cfg-btns">
      <button class="cfg-btn cancel" onclick="closeConfig()">Annuler</button>
      <button class="cfg-btn save"   onclick="saveConfig()">Enregistrer</button>
    </div>
  </div>
</div>

<script>
/* ══════════════════════════════════════════════════════
   GLOBALS
══════════════════════════════════════════════════════ */
let currentState    = {};
let pendingPlanId   = null;
let autopilotOn     = false;
let volSmoothed     = 0;
let _streamTokens   = [];
let _streamActive   = false;
let currentDisplayedResponse = '';
let _ctxRefreshTimer = null;
let handsFreeOn = false;

/* ══════════════════════════════════════════════════════
   SAFE API — protège tous les appels pywebview
══════════════════════════════════════════════════════ */
function _apiReady() {
  return !!(window.pywebview && window.pywebview.api && typeof window.pywebview.api === 'object');
}
function safeApi(fn, fallback) {
  if (_apiReady()) {
    try { return fn(window.pywebview.api); }
    catch(e) { console.warn('[ASSISTA safeApi]', e); }
  } else {
    console.warn('[ASSISTA] pywebview.api pas encore prêt');
  }
  return fallback !== undefined ? Promise.resolve(fallback) : Promise.resolve(null);
}
function waitForApi(callback, tries) {
  tries = tries || 0;
  if (_apiReady()) {
    callback();
  } else if (tries < 80) {
    setTimeout(function() { waitForApi(callback, tries + 1); }, 100);
  } else {
    console.error('[ASSISTA] pywebview.api jamais disponible après 8s');
    var el = document.getElementById('orb-state');
    if (el) el.textContent = 'Erreur connexion';
  }
}

const REC_BARS = 18;

/* ══════════════════════════════════════════════════════
   SPHERE ANIMATION — noyau stable, bords déformants, étincelles
══════════════════════════════════════════════════════ */
(function initSphere() {
  const wrap   = document.getElementById('sphere-canvas-wrap');
  const canvas = document.createElement('canvas');
  wrap.appendChild(canvas);
  const ctx = canvas.getContext('2d');

  let W, H, CX, CY, R;
  const N_DOTS   = 340;
  const N_SPARKS = 42;
  const dots   = [];
  const sparks = [];

  function resize() {
    W = canvas.width  = wrap.offsetWidth;
    H = canvas.height = wrap.offsetHeight;
    CX = W / 2; CY = H / 2;
    R  = Math.min(W, H) * 0.36;
  }

  // ── Points de la sphère (distribution Fibonacci) ──────────────────────
  function buildDots() {
    dots.length = 0;
    const golden = Math.PI * (3 - Math.sqrt(5));
    for (let i = 0; i < N_DOTS; i++) {
      const y = 1 - (i / (N_DOTS - 1)) * 2;
      const r = Math.sqrt(Math.max(0, 1 - y * y));
      const t = golden * i;
      // isBorder : point proche de l'équateur ou des pôles → bords
      const absy = Math.abs(y);
      const isBorder = r > 0.85 || absy > 0.88;
      dots.push({
        bx: Math.cos(t) * r, by: y, bz: Math.sin(t) * r,
        phase:    Math.random() * Math.PI * 2,
        speed:    0.3 + Math.random() * 0.5,
        // déformation réservée aux bords uniquement
        wobble:   isBorder ? (Math.random() - 0.5) * 0.11 : 0,
        isBorder,
        // impulsion aléatoire pour les bords
        impulseT: Math.random() * 10,
        impulseP: Math.random() * Math.PI * 2,
        impulseAmp: isBorder ? (0.03 + Math.random() * 0.07) : 0,
        impulseFreq: 0.4 + Math.random() * 1.2,
      });
    }
  }

  // ── Étincelles libres ─────────────────────────────────────────────────
  function buildSparks() {
    sparks.length = 0;
    for (let i = 0; i < N_SPARKS; i++) sparks.push(newSpark());
  }
  function newSpark() {
    const phi   = Math.random() * Math.PI * 2;
    const theta = Math.random() * Math.PI;
    return {
      phi, theta,
      dphi:   (Math.random() - 0.5) * 0.035,
      dtheta: (Math.random() - 0.5) * 0.025,
      dist:   1 + Math.random() * 0.18,
      ddist:  (Math.random() - 0.5) * 0.007,
      size:   0.7 + Math.random() * 1.9,
      alpha:  0.35 + Math.random() * 0.6,
      life:   Math.random(),
      speed:  0.0015 + Math.random() * 0.005,
      hue:    Math.random() < 0.28,
    };
  }

  // ── Rotation fluide — axe Y constant, micro-wobble X/Z très doux ──────
  let angleY = 0, angleX = 0, angleZ = 0;
  let tWobX = 0, tWobZ = 0;
  let wobX = 0, wobZ = 0;
  let wobTimer = 0;

  function updateRotation(dt) {
    // Rotation Y principale, douce et constante
    angleY += 0.0028 * dt * 60;
    // Micro-wobble des axes X/Z — très lent, très faible
    wobTimer += dt;
    if (wobTimer > 3.5 + Math.random() * 3) {
      wobTimer = 0;
      tWobX = (Math.random() - 0.5) * 0.008;
      tWobZ = (Math.random() - 0.5) * 0.006;
    }
    wobX += (tWobX - wobX) * 0.012;
    wobZ += (tWobZ - wobZ) * 0.012;
    angleX += wobX * dt * 60;
    angleZ += wobZ * dt * 60;
  }

  function rotatePoint(x, y, z) {
    let x1 =  x * Math.cos(angleY) + z * Math.sin(angleY);
    let z1 = -x * Math.sin(angleY) + z * Math.cos(angleY);
    let y1 = y;
    let y2 =  y1 * Math.cos(angleX) - z1 * Math.sin(angleX);
    let z2 =  y1 * Math.sin(angleX) + z1 * Math.cos(angleX);
    let x3 = x1 * Math.cos(angleZ) - y2 * Math.sin(angleZ);
    let y3 = x1 * Math.sin(angleZ) + y2 * Math.cos(angleZ);
    return [x3, y3, z2];
  }

  let lastTs = 0;

  function draw(ts) {
    const dt = Math.min((ts - lastTs) / 1000, 0.05);
    lastTs = ts;

    updateRotation(dt);
    ctx.clearRect(0, 0, W, H);

    const speaking  = currentState.voice_speaking;
    const listening = currentState.voice_listening;
    const busy      = currentState.busy;
    const t = ts * 0.001;

    // ── Halo de fond ────────────────────────────────────────────────────
    const haloCr = speaking ? 167 : (busy ? 244 : 56);
    const haloCg = speaking ? 139 : (busy ? 211 : 180);
    const haloCb = speaking ? 250 : (busy ?  94 : 255);
    const grd = ctx.createRadialGradient(CX, CY, 0, CX, CY, R * 1.6);
    grd.addColorStop(0,   `rgba(${haloCr},${haloCg},${haloCb},0.07)`);
    grd.addColorStop(0.5, `rgba(${haloCr},${haloCg},${haloCb},0.025)`);
    grd.addColorStop(1,   'transparent');
    ctx.fillStyle = grd;
    ctx.beginPath(); ctx.arc(CX, CY, R * 1.6, 0, Math.PI * 2); ctx.fill();

    // ── Points de la sphère — noyau stable, bords déformants ────────────
    const sorted = dots.map(d => {
      let rWob = 1;
      if (d.isBorder) {
        // Déformation de bord : combinaison d'un wobble lent + impulsion aléatoire
        const baseWob  = d.wobble * Math.sin(t * d.speed + d.phase);
        const impulse  = d.impulseAmp * Math.sin(t * d.impulseFreq + d.impulseP);
        rWob = 1 + baseWob + impulse;
      }
      const [rx, ry, rz] = rotatePoint(d.bx * rWob, d.by * rWob, d.bz * rWob);
      const persp = 1 / (1.75 - rz * 0.55);
      const sx = CX + rx * R * persp;
      const sy = CY + ry * R * persp;
      const depth = (rz + 1) * 0.5;
      let pulse = 1;
      if (speaking)  pulse = 1 + Math.sin(t * 9  + d.phase) * 0.5;
      if (listening) pulse = 1 + Math.sin(t * 4  + d.phase) * 0.28;
      if (busy)      pulse = 1 + Math.sin(t * 14 + d.phase) * 0.35;
      return { sx, sy, depth, size: persp * 2.4 * pulse, d };
    }).sort((a, b) => a.depth - b.depth);

    sorted.forEach(({ sx, sy, depth, size }) => {
      const opacity = 0.1 + depth * 0.6;
      let r = 56, g = 180, b = 255;
      if (speaking)  { r = 167; g = 139; b = 250; }
      if (busy)      { r = 244; g = 211; b =  94; }
      ctx.beginPath();
      ctx.arc(sx, sy, size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${r},${g},${b},${opacity.toFixed(2)})`;
      ctx.fill();
    });

    // ── Anneaux orbitaux ────────────────────────────────────────────────
    const rings = [
      { tiltX: 0.18, tiltZ: 0,    speed: 1,    color: `rgba(56,180,255,0.13)` },
      { tiltX: 0.9,  tiltZ: 0.4,  speed: -0.7, color: `rgba(167,139,250,0.09)` },
      { tiltX: 0.5,  tiltZ: 1.1,  speed: 0.5,  color: `rgba(56,180,255,0.07)` },
    ];
    rings.forEach(ring => {
      const a = angleY * ring.speed;
      ctx.beginPath();
      ctx.ellipse(CX, CY, R * 1.04,
        R * (0.18 + Math.abs(Math.sin(ring.tiltX + t * 0.15)) * 0.14),
        a + ring.tiltZ, 0, Math.PI * 2);
      ctx.strokeStyle = ring.color;
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // ── Étincelles libres ────────────────────────────────────────────────
    sparks.forEach((sp, i) => {
      sp.life += sp.speed;
      sp.phi   += sp.dphi;
      sp.theta += sp.dtheta;
      sp.dist  += sp.ddist;
      if (sp.dist > 1.55 || sp.dist < 0.85) {
        sp.ddist *= -0.7;
        sp.dphi   = (Math.random() - 0.5) * 0.05;
        sp.dtheta = (Math.random() - 0.5) * 0.04;
      }
      if (sp.life > 1) { sparks[i] = newSpark(); return; }
      const sx3 = Math.sin(sp.theta) * Math.cos(sp.phi) * sp.dist;
      const sy3 = Math.cos(sp.theta) * sp.dist;
      const sz3 = Math.sin(sp.theta) * Math.sin(sp.phi) * sp.dist;
      const [rx, ry, rz] = rotatePoint(sx3, sy3, sz3);
      const persp = 1 / (1.75 - rz * 0.55);
      const ex = CX + rx * R * persp;
      const ey = CY + ry * R * persp;
      const fade = Math.sin(sp.life * Math.PI);
      const a = sp.alpha * fade;
      const sr = sp.hue ? 200 : (speaking ? 220 : 130);
      const sg = sp.hue ?  80 : (speaking ?  80 : 210);
      const sb = sp.hue ? 255 : (speaking ? 255 : 255);
      const gSp = ctx.createRadialGradient(ex, ey, 0, ex, ey, sp.size * 3);
      gSp.addColorStop(0,   `rgba(${sr},${sg},${sb},${(a * 0.9).toFixed(2)})`);
      gSp.addColorStop(0.4, `rgba(${sr},${sg},${sb},${(a * 0.3).toFixed(2)})`);
      gSp.addColorStop(1,   'transparent');
      ctx.fillStyle = gSp;
      ctx.beginPath(); ctx.arc(ex, ey, sp.size * 3, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(ex, ey, sp.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255,255,255,${(a * 0.95).toFixed(2)})`; ctx.fill();
    });

    requestAnimationFrame(draw);
  }

  window.resizeSphere = function() { resize(); buildDots(); buildSparks(); };
  window.addEventListener('resize', resizeSphere);
  resizeSphere();
  requestAnimationFrame(draw);
})();

/* ══════════════════════════════════════════════════════
   VIBRATION MICRO — canvas temps réel, réactif au volume
══════════════════════════════════════════════════════ */
(function initMicVibe() {
  const cv = document.getElementById('mic-vibe-canvas');
  if (!cv) return;
  const ctx = cv.getContext('2d');
  // Historique de volume dédié à la vibe
  const VIBE_LEN = 80;
  const vibeHistory = new Array(VIBE_LEN).fill(0);
  let lastTs = 0;

  function resizeVibe() {
    const stage = document.querySelector('.center-stage');
    if (!stage) return;
    cv.width  = stage.offsetWidth;
    cv.height = 64;
  }
  window.addEventListener('resize', resizeVibe);
  resizeVibe();

  // Exposé globalement pour être mis à jour depuis updateVol()
  window._micVibeLevel = 0;

  function drawVibe(ts) {
    const dt = (ts - lastTs) / 1000;
    lastTs = ts;

    const vol = window._micVibeLevel || 0;
    vibeHistory.shift();
    vibeHistory.push(vol);

    const W = cv.width, H = cv.height;
    ctx.clearRect(0, 0, W, H);

    const active = currentState && currentState.voice_listening;
    if (!active || vol < 0.005) {
      requestAnimationFrame(drawVibe);
      return;
    }

    // Amplitude de la vibe proportionnelle au volume
    const maxAmp = H * 0.42 * Math.min(1, vol * 2.2);
    const noise  = (Math.random() - 0.5) * vol * 0.18;

    // Couleur réactive au volume
    const cr = vol > 0.6 ? 248 : vol > 0.3 ? 244 : 56;
    const cg = vol > 0.6 ?  81 : vol > 0.3 ? 211 : 180;
    const cb = vol > 0.6 ?  73 : vol > 0.3 ?  94 : 255;

    ctx.beginPath();
    for (let i = 0; i < VIBE_LEN; i++) {
      const x = (i / (VIBE_LEN - 1)) * W;
      const v = vibeHistory[i];
      const amp = v * maxAmp + noise * v;
      // Forme en miroir symétrique (haut et bas)
      const y = H / 2 - amp * (i % 2 === 0 ? 1 : -1);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    // Trace symétrique bas
    for (let i = VIBE_LEN - 1; i >= 0; i--) {
      const x = (i / (VIBE_LEN - 1)) * W;
      const v = vibeHistory[i];
      const amp = v * maxAmp + noise * v;
      const y = H / 2 + amp * (i % 2 === 0 ? 1 : -1);
      ctx.lineTo(x, y);
    }
    ctx.closePath();

    const grad = ctx.createLinearGradient(0, 0, 0, H);
    grad.addColorStop(0,   `rgba(${cr},${cg},${cb},0.22)`);
    grad.addColorStop(0.5, `rgba(${cr},${cg},${cb},0.08)`);
    grad.addColorStop(1,   `rgba(${cr},${cg},${cb},0.22)`);
    ctx.fillStyle = grad;
    ctx.fill();

    // Ligne centrale lumineuse
    ctx.beginPath();
    for (let i = 0; i < VIBE_LEN; i++) {
      const x = (i / (VIBE_LEN - 1)) * W;
      const v = vibeHistory[i];
      const amp = v * maxAmp * 0.8;
      const y = H / 2 - amp * (i % 2 === 0 ? 1 : -1);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.strokeStyle = `rgba(${cr},${cg},${cb},${(0.55 + vol * 0.35).toFixed(2)})`;
    ctx.lineWidth = 1.5;
    ctx.lineJoin = 'round';
    ctx.stroke();

    requestAnimationFrame(drawVibe);
  }
  requestAnimationFrame(drawVibe);
})();

/* ══════════════════════════════════════════════════════
   VISUALISEUR MICRO — oscilloscope canvas temps réel
══════════════════════════════════════════════════════ */
const _micHistory = new Array(60).fill(0);
let   _calibOpen  = false;

function updateVol(level) {
  const badge = document.getElementById('mic-vol-badge');
  if (badge) badge.textContent = level > 0.01 ? Math.round(level*100)+'%' : '—';
  _micHistory.shift();
  _micHistory.push(level);
  // Alimente le visualiseur de vibration micro sur le stage
  window._micVibeLevel = level;
  drawMicWave('mic-wave-canvas', _micHistory, level, false);
  if (_calibOpen) drawMicWave('calib-wave', _micHistory, level, true);
}

function drawMicWave(canvasId, history, level, big) {
  const cv = document.getElementById(canvasId);
  if (!cv) return;
  const cx = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  cx.clearRect(0, 0, W, H);
  const active = currentState.voice_listening;
  const cr = active ? (level>0.6?248:level>0.3?244:56)  : 56;
  const cg = active ? (level>0.6? 81:level>0.3?211:180) : 120;
  const cb = active ? (level>0.6? 73:level>0.3? 94:255) : 200;

  const bgGr = cx.createLinearGradient(0,0,0,H);
  bgGr.addColorStop(0, `rgba(${cr},${cg},${cb},0.08)`);
  bgGr.addColorStop(1, 'transparent');
  cx.fillStyle = bgGr; cx.fillRect(0,0,W,H);

  if (!active) {
    cx.setLineDash([3,5]);
    cx.beginPath(); cx.moveTo(0,H/2); cx.lineTo(W,H/2);
    cx.strokeStyle='rgba(56,180,255,0.2)'; cx.lineWidth=1.5; cx.stroke();
    cx.setLineDash([]);
    return;
  }
  const n = history.length;
  cx.beginPath();
  for (let i=0;i<n;i++) {
    const x = (i/(n-1))*W;
    const v = history[i];
    const noise = (Math.random()-0.5)*v*0.25;
    const y = H/2 - (v+noise)*(H*0.42)*(i%2===0?1:-1);
    i===0 ? cx.moveTo(x,y) : cx.lineTo(x,y);
  }
  cx.strokeStyle=`rgba(${cr},${cg},${cb},0.85)`; cx.lineWidth=big?2:1.5;
  cx.lineJoin='round'; cx.stroke();
  cx.lineTo(W,H/2); cx.lineTo(0,H/2); cx.closePath();
  const fill=cx.createLinearGradient(0,0,0,H);
  fill.addColorStop(0,`rgba(${cr},${cg},${cb},0.15)`);
  fill.addColorStop(1,'transparent');
  cx.fillStyle=fill; cx.fill();
  const px=W-6, py=H/2-history[n-1]*(H*0.38);
  cx.beginPath(); cx.arc(px,py,2.5+level*3,0,Math.PI*2);
  cx.fillStyle=`rgba(${cr},${cg},${cb},${0.6+level*0.4})`; cx.fill();
}

function calibrateMic() {
  _calibOpen=true;
  const ov=document.getElementById('calib-overlay');
  ov.style.display='flex';
  document.getElementById('calib-status').textContent=
    'Cliquez "Tester" et parlez normalement pour vérifier le niveau du micro.';
}
function closeCalib() {
  _calibOpen=false;
  document.getElementById('calib-overlay').style.display='none';
}
async function startCalibTest() {
  document.getElementById('calib-status').textContent='🎙 Écoute 5s… parlez normalement.';
  const wasMicOn=currentState.voice_listening;
  if (!wasMicOn) { try { await safeApi(api => api.start_voice()); } catch(e){} }
  let maxLevel=0;
  const t0=Date.now();
  const iv=setInterval(()=>{
    const cur=currentState.voice_volume||0;
    if (cur>maxLevel) maxLevel=cur;
    if (Date.now()-t0>=5000) {
      clearInterval(iv);
      if (!wasMicOn) safeApi(api => api.stop_voice());
      const pct=Math.round(maxLevel*100);
      let msg=pct>60?'✅ Excellent niveau':pct>30?'✅ Bon niveau':pct>10?'⚠️ Niveau faible — rapprochez-vous':'❌ Signal nul — vérifiez le micro';
      document.getElementById('calib-status').textContent=`Niveau max : ${pct}%  |  ${msg}`;
    }
  },100);
}

/* ══════════════════════════════════════════════════════
   POLLING PRINCIPAL
══════════════════════════════════════════════════════ */
async function pollState() {
  try {
    const s = await safeApi(api => api.get_state());
    if (s) applyState(s);
  } catch(e) {}
  try {
    const cmds = await safeApi(api => api.poll_js());
    if (cmds && cmds.length) {
      cmds.forEach(cmd => { try { eval(cmd); } catch(e){ console.error('JS cmd:', e); } });
    }
  } catch(e) {}
  setTimeout(pollState, 180);
}

function applyState(s) {
  if (!s) return;
  currentState = s;

  /* Chips */
  setChip('mic-chip',
    s.voice_listening ? '🎙 Micro ACTIF' : '🎙 Micro OFF',
    s.voice_listening ? 'active' : '');
  setChip('speak-chip',
    s.voice_speaking ? '🔊 ASSISTA parle' : '🔇 Voix en veille',
    s.voice_speaking ? 'speaking' : '');
  setChip('mode-chip',
    s.voice_awake ? '👁 Éveillée' : (s.autopilot ? '🤖 Autopilot' : '💤 Veille'),
    s.voice_awake ? 'awake' : '');

  const busyChip = document.getElementById('busy-chip');
  if (s.busy) {
    busyChip.style.display='';
    busyChip.textContent = s.status ? '⚙ '+s.status.slice(0,25) : '⚙ Traitement';
  } else {
    busyChip.style.display='none';
  }

  /* Orb */
  const stateEl = document.getElementById('orb-state');
  stateEl.textContent = s.status || (s.busy ? 'Traitement…' : 'Prête');
  stateEl.style.color = s.voice_speaking ? '#a78bfa' : s.voice_listening ? '#38b4ff' : s.busy ? '#f4d35e' : 'var(--accent)';

  /* Plan */
  if (s.plan && s.plan_id && s.plan_id !== pendingPlanId) {
    pendingPlanId = s.plan_id;
    showPlan(s.plan, s.plan_id);
  }

  /* Nouvelle réponse finale */
  if (s.response && s.response !== currentDisplayedResponse) {
    currentDisplayedResponse = s.response;

    // Extrait le texte lisible depuis le JSON si le LLM a répondu en JSON
    let displayText = s.response;
    try {
      const parsed = JSON.parse(s.response);
      if (parsed && parsed.assistant_reply) displayText = parsed.assistant_reply;
    } catch(e) { /* texte brut — ok */ }

    if (_streamActive) {
      // Streaming encore actif : ferme et met à jour la bulle avec le texte final
      if (_streamBubble) {
        const textEl = _streamBubble.querySelector('.bubble-text');
        if (textEl) textEl.innerHTML = renderSimpleMD(displayText);
      }
      assistaStreamEnd();
    } else if (_streamLastBubble) {
      // Streaming vient de finir : met à jour la bulle existante avec le texte propre
      const textEl = _streamLastBubble.querySelector('.bubble-text');
      if (textEl) textEl.innerHTML = renderSimpleMD(displayText);
      _streamLastBubble = null;
    } else {
      // Pas de streaming (plan exécuté, commande directe) : crée une nouvelle bulle
      addFeedMsg('assista', displayText);
    }

    document.getElementById('orb-transcript').textContent =
      displayText.slice(0, 100) + (displayText.length > 100 ? '…' : '');
    document.getElementById('orb-state').textContent = 'Prête';
  }

  /* Volume */
  const vol = (s.voice_volume || 0);
  volSmoothed = volSmoothed*0.7 + vol*0.3;
  updateVol(volSmoothed);

  /* Status footer */
  document.getElementById('status-line').textContent =
    s.voice_status || s.status || (s.busy ? 'Traitement en cours…' : 'Prête.');

  /* Autopilot */
  const toggle = document.getElementById('ap-toggle');
  if (s.autopilot) toggle.classList.add('on');
  else             toggle.classList.remove('on');

  handsFreeOn = !!s.hands_free;
  const hf = document.getElementById('handsfree-btn');
  if (hf) hf.classList.toggle('on', handsFreeOn);

  /* Bouton Relire — affiche Stop si lecture en cours */
  const spBtn = document.getElementById('speak-btn');
  if (spBtn) {
    if (s.voice_speaking) {
      spBtn.classList.add('speaking');
      spBtn.textContent = '⏹ Stop';
    } else {
      spBtn.classList.remove('speaking');
      spBtn.textContent = '🔊 Relire';
    }
  }

  /* Badge mémoire */
  if (s.memory_facts_count !== undefined) {
    const el = document.getElementById('facts-count');
    if (el) el.textContent = s.memory_facts_count ? `(${s.memory_facts_count})` : '';
  }
}

function setChip(id, text, cls) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = 'chip' + (cls ? ' '+cls : '');
}

/* ══════════════════════════════════════════════════════
   STREAMING TOKEN-PAR-TOKEN
══════════════════════════════════════════════════════ */
let _streamBubble     = null;
let _streamLastBubble = null;  // dernière bulle streamée (pour éviter doublon)

function assistaStreamStart() {
  _streamTokens = [];
  _streamActive = true;
  _streamLastBubble = null;
  // Crée une bulle dans le feed avec les 3 points animés
  _streamBubble = addFeedMsg('assista streaming', '', true);
  if (_streamBubble) {
    _streamBubble.querySelector('.bubble-text').innerHTML =
      '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
  }
  const sb = document.getElementById('stream-bubble');
  if (sb) sb.classList.add('show');
  const sc = document.getElementById('stream-cursor');
  if (sc) sc.style.display = 'inline-block';
  const st = document.getElementById('stream-text');
  if (st) st.textContent = '';
}

function assistaStreamToken(token) {
  _streamTokens.push(token);
  const full = _streamTokens.join('');
  // Met à jour la sphere (sous la sphère)
  const st = document.getElementById('stream-text');
  if (st) st.textContent = full.slice(-80);
  // Met à jour la bulle dans le feed en temps réel
  if (_streamBubble) {
    const textEl = _streamBubble.querySelector('.bubble-text');
    if (textEl) {
      textEl.innerHTML = renderSimpleMD(full) + '<span style="opacity:0.6;animation:blink 0.7s step-end infinite">▌</span>';
    }
    const feed = document.getElementById('feed-body');
    if (feed) feed.scrollTop = feed.scrollHeight;
  }
}

function assistaStreamEnd() {
  _streamActive = false;
  // Finalise la bulle de streaming : retire spinner et caret
  if (_streamBubble) {
    _streamBubble.classList.remove('streaming');
    const meta = _streamBubble.querySelector('.msg-meta');
    if (meta) {
      const sp = meta.querySelector('.spinner');
      if (sp) sp.remove();
    }
    const textEl = _streamBubble.querySelector('.bubble-text');
    if (textEl) {
      // Retire le caret clignotant
      textEl.innerHTML = textEl.innerHTML.replace(/<span[^>]*stream-caret[^>]*>.*?<\/span>/g, '');
    }
  }
  // La bulle reste visible — ne pas la supprimer
  _streamLastBubble = _streamBubble;  // mémorise pour éviter doublon
  _streamBubble = null;
  _streamTokens = [];
  const sb = document.getElementById('stream-bubble');
  if (sb) sb.classList.remove('show');
  const sc = document.getElementById('stream-cursor');
  if (sc) sc.style.display = 'none';
}

function assistaSetStatus(msg) {
  document.getElementById('orb-state').textContent = msg;
  document.getElementById('status-line').textContent = msg;
}

function assistaStepDone(title, status) {
  const feed = document.getElementById('feed-body');
  const chip = document.createElement('span');
  chip.className = 'action-chip ' + (status==='ok'?'ok':'err');
  chip.textContent = (status==='ok'?'✓ ':'✗ ') + title;
  // Attache au dernier message ASSISTA
  const msgs = feed.querySelectorAll('.msg-bubble.assista');
  if (msgs.length) {
    const last = msgs[msgs.length-1];
    last.appendChild(chip);
  } else {
    feed.appendChild(chip);
  }
}

/* ══════════════════════════════════════════════════════
   FEED
══════════════════════════════════════════════════════ */
function addFeedMsg(role, text, returnEl) {
  const feed = document.getElementById('feed-body');
  const div  = document.createElement('div');
  const isStreaming = role.includes('streaming');
  const baseRole = isStreaming ? 'assista' : role;
  div.className = 'msg-bubble ' + baseRole + (isStreaming ? ' streaming' : '');
  const ts = new Date().toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit'});
  const label = baseRole==='user' ? 'Vous' : 'ASSISTA';

  const textDiv = document.createElement('div');
  textDiv.className = 'bubble-text';
  textDiv.innerHTML = renderSimpleMD(text);
  div.appendChild(textDiv);

  const metaDiv = document.createElement('div');
  metaDiv.className = 'msg-meta';
  metaDiv.innerHTML = label + ' · ' + ts + (isStreaming ? ' <span class="spinner"></span>' : '');
  div.appendChild(metaDiv);

  feed.appendChild(div);
  feed.scrollTop = feed.scrollHeight;
  if (returnEl) return div;
}

function renderSimpleMD(text) {
  return (text||'')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/```([\s\S]*?)```/g,'<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g,'<code>$1</code>')
    .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')
    .replace(/\*(.*?)\*/g,'<em>$1</em>')
    .replace(/^#{1,3} (.+)/gm,'<strong>$1</strong>')
    .replace(/\n/g,'<br>');
}

function copyFeed() {
  const msgs = document.querySelectorAll('.msg-bubble');
  let txt = '';
  msgs.forEach(m => { txt += m.innerText + '\n\n'; });
  navigator.clipboard.writeText(txt.trim()).then(() => {
    showToast('Conversation copiée ✓');
  });
}

function clearFeed() {
  document.getElementById('feed-body').innerHTML = '';
  currentDisplayedResponse = '';
}

function showToast(msg) {
  const t = document.createElement('div');
  t.style.cssText = 'position:fixed;bottom:50px;left:50%;transform:translateX(-50%);background:rgba(56,180,255,0.15);border:1px solid rgba(56,180,255,0.3);color:var(--accent);padding:7px 18px;border-radius:8px;font-size:11px;z-index:9999;font-family:var(--font-mono)';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2200);
}

/* ══════════════════════════════════════════════════════
   PLAN OVERLAY
══════════════════════════════════════════════════════ */
function showPlan(plan, planId) {
  const overlay = document.getElementById('plan-overlay');
  const steps   = document.getElementById('plan-steps');
  const summary = document.getElementById('plan-summary');
  overlay.classList.add('show');
  const items = Array.isArray(plan) ? plan : (plan.steps || []);
  const planSummary = plan.summary || '';
  if (planSummary) summary.textContent = planSummary;

  const riskLabel = { safe:'✅ Safe', moderate:'⚡ Modéré', dangerous:'⚠ Dangereux', blocked:'🚫 Bloqué' };

  steps.innerHTML = items.map((step,i) => {
    const s = typeof step==='string' ? {title:step, risk:'moderate', command:''} : step;
    const risk = s.risk || 'moderate';
    return `
      <div class="plan-step">
        <div class="step-num">${i+1}</div>
        <div class="plan-step-detail">
          <div class="plan-step-title">${escHtml(s.title||s.description||JSON.stringify(s))}</div>
          ${s.command?`<div class="plan-step-cmd">${escHtml(s.command.slice(0,80))}</div>`:''}
        </div>
        <div class="step-risk ${risk}">${riskLabel[risk]||risk}</div>
      </div>`;
  }).join('');
  pendingPlanId = planId;
}

function escHtml(t) {
  return (t||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

async function approvePlan() {
  if (!pendingPlanId) return;
  document.getElementById('plan-overlay').classList.remove('show');
  await safeApi(api => api.approve_plan(pendingPlanId));
  pendingPlanId = null;
}

async function rejectPlan() {
  if (!pendingPlanId) return;
  document.getElementById('plan-overlay').classList.remove('show');
  await safeApi(api => api.reject_plan(pendingPlanId));
  pendingPlanId = null;
}

/* ══════════════════════════════════════════════════════
   INPUT
══════════════════════════════════════════════════════ */
function autoGrow(el) {
  el.style.height = '44px';
  const h = el.scrollHeight;
  el.style.height = Math.min(h, 120) + 'px';
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendPrompt(); }
}

async function sendPrompt(override) {
  const inp = document.getElementById('prompt-input');
  const val = (override !== undefined ? override : inp.value).trim();
  if (!val) return;
  inp.value = '';
  inp.style.height = '44px';
  addFeedMsg('user', val);
  document.getElementById('orb-transcript').textContent = val.slice(0,90)+(val.length>90?'…':'');
  try {
    await safeApi(api => api.submit_prompt(val));
  } catch(e) {
    addFeedMsg('assista','⚠ Erreur : '+e.toString());
  }
}

/* ══════════════════════════════════════════════════════
   CONTRÔLES
══════════════════════════════════════════════════════ */
async function toggleMic() {
  const btn = document.getElementById('mic-toggle-btn');
  if (currentState.voice_listening) {
    await safeApi(api => api.stop_voice());
    btn.classList.remove('active');
  } else {
    await safeApi(api => api.start_voice());
    btn.classList.add('active');
  }
}

async function toggleAutopilot() {
  autopilotOn = !autopilotOn;
  await safeApi(api => api.set_autopilot(autopilotOn));
}

async function toggleSpeak() {
  const btn = document.getElementById('speak-btn');
  if (currentState.voice_speaking) {
    try { await safeApi(api => api.stop_speaking()); } catch(e){}
    btn.classList.remove('speaking');
    btn.textContent = '🔊 Relire';
  } else {
    try { await safeApi(api => api.speak_last_response()); } catch(e){}
  }
}

async function toggleHandsFree() {
  try {
    if (handsFreeOn) {
      await safeApi(api => api.exit_hands_free());
      handsFreeOn = false;
      showToast('Mode mains libres desactive');
    } else {
      await safeApi(api => api.enter_hands_free());
      handsFreeOn = true;
      showToast('Mode mains libres active');
    }
  } catch(e) {
    showToast('Mains libres indisponible');
  }
}

/* ══════════════════════════════════════════════════════
   CONFIG
══════════════════════════════════════════════════════ */
const FALLBACK_MODELS = [
  "openrouter/free",
  "deepseek/deepseek-r1:free",
  "meta-llama/llama-3.3-70b-instruct:free",
  "qwen/qwen3-coder:free",
  "qwen/qwen-2.5-7b-instruct:free",
];
const DEFAULT_URL = "https://openrouter.ai/api/v1/chat/completions";
let _cfgModelMode = 'auto'; // 'auto' | 'manual'

function setModelMode(mode) {
  _cfgModelMode = mode;
  document.getElementById('btn-mode-auto').classList.toggle('active',   mode === 'auto');
  document.getElementById('btn-mode-manual').classList.toggle('active', mode === 'manual');
  document.getElementById('cfg-model-list').style.display         = mode === 'manual' ? 'flex' : 'none';
  document.getElementById('cfg-model-custom-wrap').style.display  = mode === 'manual' ? 'block' : 'none';
  document.getElementById('cfg-auto-note').style.display          = mode === 'auto'   ? 'block' : 'none';
}

function toggleKeyVisibility() {
  const inp = document.getElementById('cf-api-key');
  const btn = document.getElementById('cf-eye-btn');
  if (inp.type === 'password') { inp.type = 'text';     btn.textContent = '🙈'; }
  else                         { inp.type = 'password'; btn.textContent = '👁'; }
}

async function openConfig() {
  try {
    const cfg = await safeApi(api => api.get_config(), {});
    // Clé API — pré-remplie si disponible
    document.getElementById('cf-api-key').value  = cfg.api_key || '';
    // Note si clé vient de l'env
    const envNote = document.getElementById('cfg-env-note');
    if (!cfg.api_key && cfg.api_key_from_env) {
      envNote.textContent = '✓ Clé chargée depuis OPENROUTER_API_KEY (variable d\'environnement)';
    } else {
      envNote.textContent = '';
    }
    // URL — défaut pré-rempli
    document.getElementById('cf-base-url').value = cfg.base_url || DEFAULT_URL;
    // Modèle : auto ou manuel ?
    const savedModel = cfg.model || '';
    if (!savedModel || savedModel === '__auto__' || !FALLBACK_MODELS.includes(savedModel)) {
      setModelMode('auto');
      // Si modèle custom non-connu
      if (savedModel && savedModel !== '__auto__' && !FALLBACK_MODELS.includes(savedModel)) {
        setModelMode('manual');
        document.getElementById('cf-model-custom').value = savedModel;
        document.querySelectorAll('input[name="cf-model-radio"]').forEach(r => r.checked = false);
      }
    } else {
      setModelMode('manual');
      const radio = document.querySelector(`input[name="cf-model-radio"][value="${savedModel}"]`);
      if (radio) radio.checked = true;
      document.getElementById('cf-model-custom').value = '';
    }
  } catch(e) {
    // Defaults si API indisponible
    document.getElementById('cf-base-url').value = DEFAULT_URL;
    setModelMode('auto');
  }
  document.getElementById('config-overlay').classList.add('show');
}

function closeConfig() { document.getElementById('config-overlay').classList.remove('show'); }

async function saveConfig() {
  const key = document.getElementById('cf-api-key').value.trim();
  const url  = document.getElementById('cf-base-url').value.trim() || DEFAULT_URL;
  let model  = '__auto__';
  if (_cfgModelMode === 'manual') {
    // Radio sélectionné ?
    const checked = document.querySelector('input[name="cf-model-radio"]:checked');
    const custom  = document.getElementById('cf-model-custom').value.trim();
    if (checked)       model = checked.value;
    else if (custom)   model = custom;
    else               model = FALLBACK_MODELS[0]; // fallback : DeepSeek
  }
  try { await safeApi(api => api.save_config(key, model, url)); } catch(e){}
  closeConfig();
  showToast('Configuration enregistrée ✓');
}

/* ══════════════════════════════════════════════════════
   PANNEAU DROIT — Shell Log
══════════════════════════════════════════════════════ */
function switchPanel(tab) {
  document.querySelectorAll('.panel-tab').forEach(t => t.classList.toggle('active', t.dataset.tab===tab));
  document.querySelectorAll('.panel-page').forEach(p => p.classList.remove('active'));
  document.getElementById('panel-'+tab).classList.add('active');
  if (tab==='shell') refreshShellLog();
  if (tab==='mem')   refreshMemory();
  if (tab==='ctx')   refreshCtx();
  if (tab==='ops')   refreshOps();
}

async function refreshShellLog() {
  try {
    const data = await safeApi(api => api.get_shell_log(), {entries:[]});
    const entries = (data && data.entries) ? data.entries : [];
    const el = document.getElementById('shell-log-list');
    if (!entries.length) {
      el.innerHTML = '<div style="color:var(--text-dim);font-size:11px;padding:10px 0">Aucune commande exécutée.</div>';
      return;
    }
    el.innerHTML = entries.slice().reverse().map(e => {
      const statusClass = {OK:'ok', ERROR:'err', BLOCKED:'blocked', TIMEOUT:'timeout'}[e.status] || 'ok';
      return `<div class="log-entry ${statusClass}">
        <div class="log-ts">${e.ts||''} — <strong>${e.status||''}</strong></div>
        <div class="log-cmd">${escHtml((e.command||'').slice(0,120))}</div>
        <div class="log-detail">${escHtml(e.detail||'')}</div>
      </div>`;
    }).join('');
  } catch(e) {
    document.getElementById('shell-log-list').innerHTML = '<div style="color:var(--danger);font-size:11px">Erreur chargement log.</div>';
  }
}

/* ══════════════════════════════════════════════════════
   PANNEAU DROIT — Mémoire
══════════════════════════════════════════════════════ */
async function refreshMemory() {
  try {
    const data = await safeApi(api => api.get_memory(), {facts:[], turns:[]});
    const el = document.getElementById('facts-list');
    const facts = data.facts || [];
    document.getElementById('facts-count').textContent = facts.length ? `(${facts.length})` : '';
    if (!facts.length) {
      el.innerHTML = '<div style="color:var(--text-dim);font-size:11px;padding:10px 0">Aucun fait mémorisé.</div>';
      return;
    }
    el.innerHTML = facts.slice().reverse().map(f =>
      `<div class="fact-item">${escHtml(f)}</div>`
    ).join('');
  } catch(e) {}
}

async function confirmForget() {
  if (!confirm('Effacer toute la mémoire d\'ASSISTA ?')) return;
  try {
    await safeApi(api => api.forget_memory());
    await refreshMemory();
    showToast('Mémoire effacée ✓');
  } catch(e) {}
}

/* ══════════════════════════════════════════════════════
   PANNEAU DROIT — Contexte PC
══════════════════════════════════════════════════════ */
async function refreshCtx() {
  try {
    const s = await safeApi(api => api.get_state());
    if (!s) return;
    const el = document.getElementById('ctx-info');
    const mapper = s.mapper || {};
    const latest = mapper.last_scan || {};
    const db = s.db_stats || {};
    const progress = Math.max(0, Math.min(100, mapper.progress_percent || 0));
    const topExt = ((latest.notes||{}).top_extensions || [])
      .slice(0, 5)
      .map(x => `${escHtml(x.ext||'∅')} (${x.count})`)
      .join(', ') || '—';
    const fill   = document.getElementById('mapper-progress-fill');
    const label  = document.getElementById('mapper-progress-label');
    const status = document.getElementById('mapper-progress-status');
    const detail = document.getElementById('mapper-progress-detail');
    if (fill)   fill.style.width = `${progress}%`;
    if (label)  label.textContent = `${progress}%`;
    if (status) status.textContent = mapper.running ? '⏳ Scan en cours…' : (progress >= 100 ? '✅ Scan terminé' : 'Progression du mapping');
    if (detail) detail.textContent = mapper.message || (mapper.current_path ? `📂 ${mapper.current_path}` : '');
    el.innerHTML = `
      <div class="ctx-item"><div class="ctx-label">OS</div><div class="ctx-val">${escHtml(navigator.platform||'')}</div></div>
      <div class="ctx-item"><div class="ctx-label">Voix</div><div class="ctx-val">${escHtml(s.voice_status||'—')}</div></div>
      <div class="ctx-item"><div class="ctx-label">Autopilot</div><div class="ctx-val">${s.autopilot?'Activé':'Désactivé'}</div></div>
      <div class="ctx-item"><div class="ctx-label">Faits mémorisés</div><div class="ctx-val">${s.memory_facts_count||0}</div></div>
      <div class="ctx-item"><div class="ctx-label">Base SQLite</div><div class="ctx-val">${escHtml(db.db_path||'—')}</div></div>
      <div class="ctx-item"><div class="ctx-label">Messages persistés</div><div class="ctx-val">${db.messages||0}</div></div>
      <div class="ctx-item"><div class="ctx-label">Agents</div><div class="ctx-val">${s.agents_count||0}</div></div>
      <div class="ctx-item"><div class="ctx-label">Routines</div><div class="ctx-val">${s.routines_count||0}</div></div>
      <div class="ctx-item"><div class="ctx-label">PC Mapper</div><div class="ctx-val">${escHtml(mapper.message||'—')}</div></div>
      <div class="ctx-item"><div class="ctx-label">Racine en cours</div><div class="ctx-val">${escHtml(mapper.current_root||'—')}</div></div>
      <div class="ctx-item"><div class="ctx-label">Chemin en cours</div><div class="ctx-val">${escHtml(mapper.current_path||'—')}</div></div>
      <div class="ctx-item"><div class="ctx-label">Fichiers scannés</div><div class="ctx-val">${mapper.scanned_files||latest.scanned_files||0}</div></div>
      <div class="ctx-item"><div class="ctx-label">Dossiers scannés</div><div class="ctx-val">${mapper.scanned_dirs||latest.scanned_dirs||0}</div></div>
      <div class="ctx-item"><div class="ctx-label">Extensions top</div><div class="ctx-val">${topExt}</div></div>
    `;
    if (_ctxRefreshTimer) { clearTimeout(_ctxRefreshTimer); _ctxRefreshTimer = null; }
    if (mapper.running) {
      _ctxRefreshTimer = setTimeout(refreshCtx, 900);
    }
  } catch(e) {}
}

async function startPcMapper() {
  try {
    const res = await safeApi(api => api.start_pc_mapper(true), {});
    showToast(res?.message || 'PC Mapper lancé');
    _ctxRefreshTimer = setTimeout(refreshCtx, 800);
  } catch(e) {}
}

async function startQuickScan() {
  try {
    const res = await safeApi(api => api.start_quick_scan(), {});
    showToast(res?.message || 'Scan rapide lancé');
    _ctxRefreshTimer = setTimeout(refreshCtx, 800);
  } catch(e) {}
}

async function refreshOps() {
  try {
    const data = await safeApi(api => api.get_ops_state(), {});
    const el = document.getElementById('ops-info');
    const audit = data.security_audit || {};
    const sessions = data.agent_sessions || [];
    const runs = data.routine_runs || [];
    const recentActions = data.recent_actions || [];
    const sessionsHtml = sessions.slice(0,4).map(s =>
      `<div class="fact-item"><strong>${escHtml(s.agent_key||'agent')}</strong> — ${escHtml(s.title||'')}</div>`
    ).join('') || '<div class="fact-item">Aucune session agent.</div>';
    const runsHtml = runs.slice(0,4).map(r =>
      `<div class="fact-item"><strong>${escHtml(r.name||'Routine')}</strong> — ${escHtml(r.status||'')}</div>`
    ).join('') || '<div class="fact-item">Aucune exécution de routine.</div>';
    const actionsHtml = recentActions.slice(0,4).map(a =>
      `<div class="fact-item"><strong>${escHtml(a.kind||'action')}</strong> — ${escHtml(a.status||'')}</div>`
    ).join('') || '<div class="fact-item">Aucune action récente.</div>';
    el.innerHTML = `
      <div class="ctx-item"><div class="ctx-label">Audit sécurité</div><div class="ctx-val">${escHtml(audit.summary||'Aucun audit')}</div></div>
      <div class="ctx-item"><div class="ctx-label">Sévérité</div><div class="ctx-val">${escHtml(audit.severity||'—')}</div></div>
      <div class="mem-section-title" style="margin-top:10px">Sessions agents</div>
      ${sessionsHtml}
      <div class="mem-section-title" style="margin-top:10px">Routines exécutées</div>
      ${runsHtml}
      <div class="mem-section-title" style="margin-top:10px">Actions récentes</div>
      ${actionsHtml}
    `;
  } catch(e) {}
}

async function runSecurityAudit() {
  try {
    const res = await safeApi(api => api.run_security_audit(), {});
    showToast(res?.message || 'Audit lancé');
    await refreshOps();
  } catch(e) {}
}

/* ══════════════════════════════════════════════════════
   INIT
══════════════════════════════════════════════════════ */
// Init unique — évite le double appel (pywebviewready + DOMContentLoaded)
let _initDone = false;
function _initAssista() {
  if (_initDone) return;
  _initDone = true;
  waitForApi(async function() {
    try {
      const state = await safeApi(api => api.init_session(), {});
      if (state) {
        applyState(state);
        if (state.message) addFeedMsg('assista', state.message);
      }
      document.getElementById('orb-state').textContent = 'Prête';
    } catch(e) {
      document.getElementById('orb-state').textContent = 'Erreur d\'init';
      console.error('[ASSISTA init]', e);
    }
    pollState();
    setTimeout(refreshShellLog, 1000);
    setTimeout(refreshMemory, 1500);
    setTimeout(refreshCtx, 1800);
    setTimeout(refreshOps, 2100);
  });
}

// Double écoute : pywebviewready + DOMContentLoaded (selon timing pywebview)
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', _initAssista);
} else {
  _initAssista();
}
window.addEventListener('pywebviewready', _initAssista);

document.addEventListener('keydown', e => {
  if ((e.ctrlKey||e.metaKey) && e.key==='m') toggleMic();
  if ((e.ctrlKey||e.metaKey) && e.key==='Enter') sendPrompt();
  if (e.key==='Escape') {
    closeConfig();
    document.getElementById('plan-overlay').classList.remove('show');
  }
});
</script>
</body>
</html>""")
