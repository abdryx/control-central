#!/usr/bin/env python3
"""
MISSION CONTROL // AI Build Console
------------------------------------
A single-file Python web server that serves the Mission Control page
exactly as-is (same HTML, CSS, and JavaScript, all embedded below).

Usage:
    python3 mission_control.py [port]

Then open:
    http://localhost:8000   (or whichever port you specify)
"""

import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MISSION CONTROL // AI Build Console</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/4.3.0/marked.min.js"></script>
<style>
:root{
  --bg:#05060b;
  --bg2:#080a13;
  --panel:#0d1020;
  --panel2:#101324;
  --line: rgba(148,140,255,0.14);
  --line-soft: rgba(148,140,255,0.08);
  --violet:#7c5cff;
  --violet-soft: rgba(124,92,255,0.15);
  --amber:#ff9a4d;
  --amber-soft: rgba(255,154,77,0.15);
  --mint:#3ddc97;
  --mint-soft: rgba(61,220,151,0.15);
  --red:#ff5c6c;
  --text:#eceafc;
  --muted:#8a8fb3;
  --muted2:#5c6086;
  --accent: var(--violet);
  --accent-soft: var(--violet-soft);
  --radius: 14px;
  font-size: 16px;
}
[data-accent="amber"]{ --accent: var(--amber); --accent-soft: var(--amber-soft); }
[data-accent="mint"]{ --accent: var(--mint); --accent-soft: var(--mint-soft); }
[data-accent="red"]{ --accent: var(--red); --accent-soft: rgba(255,92,108,0.15); }

*{box-sizing:border-box; margin:0; padding:0;}
html,body{height:100%;}
body{
  background: var(--bg);
  color: var(--text);
  font-family: 'Inter', sans-serif;
  overflow-x:hidden;
  min-height:100vh;
  position:relative;
}
@media (prefers-reduced-motion: reduce){
  *{ animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; }
}

/* ambient backdrop */
.backdrop{
  position:fixed; inset:0; z-index:0; pointer-events:none;
  background:
    radial-gradient(ellipse 900px 500px at 15% -10%, var(--accent-soft), transparent 60%),
    radial-gradient(ellipse 700px 600px at 110% 20%, rgba(255,154,77,0.08), transparent 60%),
    radial-gradient(ellipse 800px 800px at 50% 120%, rgba(61,220,151,0.06), transparent 60%),
    var(--bg);
  transition: background 0.6s ease;
}
.backdrop::before{
  content:'';
  position:absolute; inset:0;
  background-image:
    linear-gradient(var(--line-soft) 1px, transparent 1px),
    linear-gradient(90deg, var(--line-soft) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: radial-gradient(ellipse 80% 60% at 50% 0%, black 40%, transparent 100%);
  opacity:0.5;
}

/* ---------- BOOT SEQUENCE ---------- */
#boot{
  position:fixed; inset:0; z-index:999;
  background:#05060b;
  display:flex; align-items:center; justify-content:center;
  flex-direction:column;
  font-family:'IBM Plex Mono', monospace;
  transition: opacity 0.6s ease, visibility 0.6s ease;
}
#boot.hide{ opacity:0; visibility:hidden; pointer-events:none; }
#boot .lines{ width:min(560px, 86vw); }
#boot .line{ color:var(--mint); font-size:13px; line-height:1.9; opacity:0; white-space:pre; overflow:hidden; }
#boot .line.show{ opacity:1; }
#boot .cursor{ display:inline-block; width:8px; height:14px; background:var(--mint); margin-left:4px; animation: blink 1s step-end infinite; vertical-align:-2px;}
@keyframes blink{ 50%{opacity:0;} }
#boot .skip{
  position:absolute; bottom:28px; right:28px; color:var(--muted); font-size:11px; letter-spacing:0.08em;
  background:none; border:1px solid var(--line); padding:8px 14px; border-radius:20px; cursor:pointer; font-family:'IBM Plex Mono',monospace;
}
#boot .skip:hover{ color:var(--text); border-color:var(--accent); }

/* ---------- LAYOUT ---------- */
.app{ position:relative; z-index:1; display:flex; min-height:100vh; }

.sidebar{
  width:272px; flex-shrink:0;
  border-right:1px solid var(--line);
  background: linear-gradient(180deg, rgba(13,16,32,0.7), rgba(8,10,19,0.4));
  backdrop-filter: blur(6px);
  padding:22px 18px;
  display:flex; flex-direction:column;
  position:sticky; top:0; height:100vh; overflow-y:auto;
  transition: transform 0.3s ease;
}
.brand{ display:flex; align-items:center; gap:10px; margin-bottom:22px; cursor:pointer; }
.brand .dot{ width:9px; height:9px; border-radius:50%; background:var(--mint); box-shadow:0 0 10px var(--mint); animation: pulse 2s ease-in-out infinite; }
@keyframes pulse{ 0%,100%{opacity:1;} 50%{opacity:0.35;} }
.brand .name{ font-family:'Space Grotesk', sans-serif; font-weight:700; font-size:15px; letter-spacing:0.02em; }
.brand .name span{ color: var(--accent); }

.panel-box{
  border:1px solid var(--line); border-radius:var(--radius);
  background: rgba(255,255,255,0.02);
  padding:14px; margin-bottom:16px;
}
.panel-box .label{ font-family:'IBM Plex Mono', monospace; font-size:10px; letter-spacing:0.12em; color:var(--muted); margin-bottom:8px; text-transform:uppercase;}
.stat-row{ display:flex; justify-content:space-between; font-family:'IBM Plex Mono', monospace; font-size:11.5px; padding:3px 0; color:var(--muted);}
.stat-row b{ color:var(--text); font-weight:500;}
.rank-name{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:15px; color:var(--accent); margin:4px 0 8px;}
.xp-bar{ height:6px; border-radius:4px; background:rgba(255,255,255,0.06); overflow:hidden; margin-top:6px;}
.xp-fill{ height:100%; background:linear-gradient(90deg, var(--accent), var(--mint)); border-radius:4px; transition: width 0.6s cubic-bezier(.2,.9,.3,1); }
.xp-caption{ font-size:10px; color:var(--muted2); margin-top:5px; font-family:'IBM Plex Mono',monospace;}

.nav-title{ font-family:'IBM Plex Mono',monospace; font-size:10px; letter-spacing:0.14em; color:var(--muted2); margin:6px 4px 8px; text-transform:uppercase;}
.nav-list{ list-style:none; display:flex; flex-direction:column; gap:2px; flex:1;}
.nav-item{
  display:flex; align-items:center; gap:10px;
  padding:9px 10px; border-radius:9px; cursor:pointer;
  font-size:13px; color:var(--muted); transition: all 0.15s ease;
  border:1px solid transparent;
}
.nav-item:hover{ background:rgba(255,255,255,0.03); color:var(--text); }
.nav-item.active{ background:var(--accent-soft); color:var(--text); border-color:var(--line);}
.nav-item .num{ font-family:'IBM Plex Mono',monospace; font-size:10px; color:var(--muted2); width:16px;}
.nav-item.active .num{ color:var(--accent); }
.nav-item .bullet{ width:5px; height:5px; border-radius:50%; background:var(--muted2); margin-left:auto; flex-shrink:0;}
.nav-item.active .bullet{ background:var(--mint); box-shadow:0 0 6px var(--mint);}

.sidebar-foot{ margin-top:14px; padding-top:14px; border-top:1px solid var(--line); display:flex; flex-direction:column; gap:8px;}
.mini-btn{
  display:flex; align-items:center; justify-content:space-between; gap:8px;
  background:rgba(255,255,255,0.02); border:1px solid var(--line); color:var(--muted);
  font-family:'IBM Plex Mono',monospace; font-size:11px; padding:8px 10px; border-radius:9px; cursor:pointer;
  transition: all 0.15s ease;
}
.mini-btn:hover{ color:var(--text); border-color:var(--accent); }
.theme-dots{ display:flex; gap:7px; padding:2px 2px;}
.theme-dot{ width:16px; height:16px; border-radius:50%; cursor:pointer; border:2px solid rgba(255,255,255,0.15); }
.theme-dot.active{ border-color:#fff; }
.foot-note{ font-family:'IBM Plex Mono',monospace; font-size:9.5px; color:var(--muted2); text-align:center; margin-top:6px; letter-spacing:0.04em;}

.main{ flex:1; min-width:0; position:relative; }
.topbar{
  position:sticky; top:0; z-index:5;
  display:flex; align-items:center; gap:14px;
  padding:14px 28px; border-bottom:1px solid var(--line);
  background: rgba(5,6,11,0.75); backdrop-filter: blur(10px);
}
.hamburger{ display:none; background:none; border:1px solid var(--line); color:var(--text); width:34px; height:34px; border-radius:8px; cursor:pointer;}
.mission-field{
  flex:1; display:flex; align-items:center; gap:10px;
  background:rgba(255,255,255,0.02); border:1px solid var(--line); border-radius:10px; padding:9px 14px;
}
.mission-field .tag{ font-family:'IBM Plex Mono',monospace; font-size:10px; color:var(--muted2); letter-spacing:0.1em; white-space:nowrap;}
.mission-field input{
  flex:1; background:none; border:none; outline:none; color:var(--text); font-family:'IBM Plex Mono',monospace; font-size:13px;
}
.mission-field input::placeholder{ color:var(--muted2); }
.topbar .icon-btn{
  background:none; border:1px solid var(--line); color:var(--muted); width:36px; height:36px; border-radius:9px; cursor:pointer;
  display:flex; align-items:center; justify-content:center; font-size:15px; transition: all 0.15s ease; flex-shrink:0;
}
.topbar .icon-btn:hover{ color:var(--text); border-color:var(--accent); }

.view{ padding:34px 40px 80px; max-width:1080px; }

/* ---------- HOME / RADAR ---------- */
.hero{ margin-bottom:8px; }
.eyebrow{ font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:0.18em; color:var(--accent); text-transform:uppercase; display:flex; align-items:center; gap:8px;}
.eyebrow::before{ content:''; width:18px; height:1px; background:var(--accent); display:inline-block;}
h1.title{ font-family:'Space Grotesk',sans-serif; font-size:44px; font-weight:700; line-height:1.05; margin:14px 0 10px; letter-spacing:-0.01em;}
.subtitle{ color:var(--muted); font-size:15px; max-width:560px; line-height:1.6; margin-bottom:26px;}

.radar-wrap{ display:flex; gap:40px; align-items:center; margin: 18px 0 40px; flex-wrap:wrap;}
.radar{ position:relative; width:360px; height:360px; flex-shrink:0; }
.radar svg{ width:100%; height:100%; }
.radar-node{ cursor:pointer; }
.radar-node circle.core{ transition: r 0.2s ease; }
.radar-node:hover circle.core{ r:9; }
.radar-node text{ font-family:'IBM Plex Mono',monospace; fill:var(--muted); font-size:9px; pointer-events:none;}
.radar-center{ font-family:'Space Grotesk',sans-serif; }

.mission-hero-field{
  display:flex; align-items:center; gap:10px; max-width:440px;
  background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:5px 5px 5px 16px;
  box-shadow: 0 0 0 1px rgba(255,255,255,0.01), 0 20px 40px -20px rgba(0,0,0,0.6);
}
.mission-hero-field input{ flex:1; background:none; border:none; outline:none; color:var(--text); font-family:'IBM Plex Mono',monospace; font-size:13.5px; padding:10px 0;}
.mission-hero-field input::placeholder{ color:var(--muted2); }
.mission-hero-field button{
  background:var(--accent); color:#05060b; border:none; padding:10px 16px; border-radius:8px; font-weight:600; font-size:12.5px; cursor:pointer;
  font-family:'Space Grotesk',sans-serif; white-space:nowrap; transition: transform 0.15s ease, filter 0.15s ease;
}
.mission-hero-field button:hover{ filter:brightness(1.12); transform:translateY(-1px); }
.chips{ display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; max-width:460px;}
.chip{
  font-family:'IBM Plex Mono',monospace; font-size:11px; color:var(--muted); border:1px dashed var(--line); border-radius:20px;
  padding:6px 12px; cursor:pointer; transition: all 0.15s ease;
}
.chip:hover{ color:var(--text); border-color:var(--accent); border-style:solid; }

.module-grid{ display:grid; grid-template-columns:repeat(auto-fill, minmax(300px,1fr)); gap:14px; margin-top:10px;}
.module-card{
  border:1px solid var(--line); border-radius:var(--radius); background:var(--panel);
  padding:18px; cursor:pointer; position:relative; overflow:hidden;
  transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease;
}
.module-card:hover{ transform:translateY(-3px); border-color:var(--accent); background:var(--panel2); }
.module-card .glyph{ font-size:20px; color:var(--accent); margin-bottom:10px; display:block;}
.module-card .mnum{ font-family:'IBM Plex Mono',monospace; font-size:10px; color:var(--muted2); letter-spacing:0.1em; margin-bottom:4px;}
.module-card h3{ font-family:'Space Grotesk',sans-serif; font-size:16px; margin-bottom:6px; }
.module-card p{ font-size:12.5px; color:var(--muted); line-height:1.5; }
.module-card .live-tag{
  position:absolute; top:16px; right:16px; font-family:'IBM Plex Mono',monospace; font-size:8.5px; color:var(--mint);
  border:1px solid rgba(61,220,151,0.35); padding:2px 6px; border-radius:10px; letter-spacing:0.08em;
}

/* ---------- MODULE VIEW ---------- */
.module-header{ margin-bottom:24px; }
.module-header .mnum-big{ font-family:'IBM Plex Mono',monospace; color:var(--accent); font-size:13px; letter-spacing:0.1em;}
.module-header h1{ font-family:'Space Grotesk',sans-serif; font-size:32px; margin:8px 0 8px; display:flex; align-items:center; gap:12px;}
.module-header .glyph{ color:var(--accent); }
.module-header p{ color:var(--muted); font-size:14px; max-width:560px; line-height:1.6;}

.field-block{ margin-bottom:16px; }
.field-label{ font-family:'IBM Plex Mono',monospace; font-size:10.5px; letter-spacing:0.1em; color:var(--muted); text-transform:uppercase; margin-bottom:8px; display:block;}
.field-value{
  border:1px solid var(--line); background:var(--panel); border-radius:10px; padding:13px 15px;
  font-family:'IBM Plex Mono',monospace; font-size:13.5px; color:var(--text); width:100%; outline:none;
}
.field-value:focus{ border-color:var(--accent); }
.select-row{ display:flex; gap:12px; flex-wrap:wrap; }
.select-row .field-block{ flex:1; min-width:200px; }
select.field-value{ appearance:none; cursor:pointer; background-image: linear-gradient(45deg, transparent 50%, var(--muted) 50%), linear-gradient(135deg, var(--muted) 50%, transparent 50%); background-position: calc(100% - 18px) center, calc(100% - 13px) center; background-size:5px 5px, 5px 5px; background-repeat:no-repeat;}

.run-btn{
  display:inline-flex; align-items:center; gap:10px;
  background:var(--accent); color:#05060b; border:none; padding:13px 22px; border-radius:10px;
  font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:13px; letter-spacing:0.03em; cursor:pointer;
  transition: transform 0.15s ease, filter 0.15s ease; text-transform:uppercase;
}
.run-btn:hover{ filter:brightness(1.1); transform:translateY(-1px); }
.run-btn:disabled{ opacity:0.55; cursor:wait; transform:none;}
.run-btn .spinner{ width:13px; height:13px; border-radius:50%; border:2px solid rgba(5,6,11,0.3); border-top-color:#05060b; animation:spin 0.7s linear infinite; display:none;}
.run-btn.loading .spinner{ display:inline-block; }

.log-console{
  margin-top:16px; font-family:'IBM Plex Mono',monospace; font-size:12px; color:var(--mint);
  background:rgba(0,0,0,0.35); border:1px solid var(--line); border-radius:10px; padding:14px 16px; display:none;
}
.log-console.show{ display:block; }
.log-console .lg{ opacity:0; animation: fadeUp 0.35s ease forwards; margin-bottom:4px;}
@keyframes fadeUp{ from{opacity:0; transform:translateY(4px);} to{opacity:1; transform:translateY(0);} }
@keyframes spin{ to{ transform:rotate(360deg); } }

.error-box{
  margin-top:18px; border:1px solid rgba(255,92,108,0.4); background:rgba(255,92,108,0.06); border-radius:10px;
  padding:16px 18px; color:#ffb3ba; font-size:13px; display:flex; justify-content:space-between; align-items:center; gap:12px;
}
.error-box button{ background:none; border:1px solid rgba(255,92,108,0.5); color:#ffb3ba; padding:7px 12px; border-radius:8px; font-size:11px; cursor:pointer; white-space:nowrap; font-family:'IBM Plex Mono',monospace;}

.output-card{
  margin-top:22px; border:1px solid var(--line); border-radius:var(--radius); background:var(--panel);
  overflow:hidden; opacity:0; transform:translateY(10px); animation: revealCard 0.5s ease forwards;
}
@keyframes revealCard{ to{opacity:1; transform:translateY(0);} }
.output-head{
  display:flex; align-items:center; justify-content:space-between; padding:14px 18px;
  border-bottom:1px solid var(--line); background:rgba(255,255,255,0.015);
}
.output-head .oh-left{ display:flex; align-items:center; gap:9px; }
.output-head .oh-left .d{ width:7px; height:7px; border-radius:50%; background:var(--mint); box-shadow:0 0 8px var(--mint);}
.output-head .oh-title{ font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:0.08em; color:var(--muted); text-transform:uppercase;}
.output-actions{ display:flex; gap:8px; }
.output-actions button{
  background:none; border:1px solid var(--line); color:var(--muted); padding:6px 11px; border-radius:7px; font-size:11px; cursor:pointer;
  font-family:'IBM Plex Mono',monospace; transition: all 0.15s ease;
}
.output-actions button:hover{ color:var(--text); border-color:var(--accent); }
.output-body{ padding:24px 26px; }
.output-body h1,.output-body h2,.output-body h3{ font-family:'Space Grotesk',sans-serif; color:var(--text); margin:20px 0 10px; }
.output-body h2:first-child, .output-body h1:first-child{ margin-top:0; }
.output-body h2{ font-size:18px; color:var(--accent); border-top:1px solid var(--line); padding-top:16px; }
.output-body h2:first-child{ border-top:none; padding-top:0; }
.output-body h3{ font-size:15px; }
.output-body p{ color:#cfd0e8; font-size:13.8px; line-height:1.75; margin-bottom:10px; }
.output-body ul,.output-body ol{ margin:0 0 12px 20px; color:#cfd0e8; font-size:13.8px; line-height:1.75; }
.output-body li{ margin-bottom:5px; }
.output-body strong{ color:var(--text); }
.output-body code{ background:rgba(255,255,255,0.06); padding:2px 6px; border-radius:5px; font-family:'IBM Plex Mono',monospace; font-size:0.9em; color:var(--mint);}
.output-body pre{ background:rgba(0,0,0,0.4); border:1px solid var(--line); border-radius:10px; padding:16px; overflow-x:auto; margin-bottom:14px;}
.output-body pre code{ background:none; padding:0; color:#cfe8ff; }
.output-body a{ color:var(--accent); }

/* pitch slides */
.pitch-top{ display:grid; grid-template-columns: 1fr; gap:14px; margin-bottom:20px;}
.pitch-block{ border:1px solid var(--line); border-radius:12px; padding:16px 18px; background:rgba(255,255,255,0.02);}
.pitch-block .pl{ font-family:'IBM Plex Mono',monospace; font-size:10px; letter-spacing:0.1em; color:var(--accent); text-transform:uppercase; margin-bottom:8px;}
.pitch-block .hook{ font-family:'Space Grotesk',sans-serif; font-size:19px; font-weight:600;}
.pitch-block .pitch-text{ font-size:14px; color:#cfd0e8; line-height:1.7;}
.slides-wrap{ margin-top:6px; }
.slide-stage{
  border:1px solid var(--line); border-radius:14px; background: linear-gradient(160deg, rgba(124,92,255,0.08), rgba(255,255,255,0.01));
  padding:34px; min-height:220px; position:relative; overflow:hidden;
}
.slide-stage .sn{ font-family:'IBM Plex Mono',monospace; font-size:11px; color:var(--muted2); letter-spacing:0.1em; margin-bottom:14px;}
.slide-stage h3{ font-family:'Space Grotesk',sans-serif; font-size:25px; margin-bottom:16px;}
.slide-stage ul{ margin-left:20px; }
.slide-stage li{ font-size:14.5px; color:#dcdcf3; line-height:1.8; margin-bottom:6px;}
.slide-nav{ display:flex; align-items:center; justify-content:center; gap:14px; margin-top:16px;}
.slide-nav button{
  background:var(--panel); border:1px solid var(--line); color:var(--text); width:36px; height:36px; border-radius:50%;
  cursor:pointer; font-size:14px; display:flex; align-items:center; justify-content:center; transition: all 0.15s ease;
}
.slide-nav button:hover{ border-color:var(--accent); color:var(--accent); }
.dots{ display:flex; gap:7px; }
.dots .dt{ width:7px; height:7px; border-radius:50%; background:var(--line); cursor:pointer; transition: all 0.2s ease;}
.dots .dt.active{ background:var(--accent); width:20px; border-radius:4px; }

/* ---------- DRAWERS / MODALS ---------- */
.overlay{ position:fixed; inset:0; background:rgba(0,0,0,0.55); backdrop-filter: blur(3px); z-index:50; opacity:0; pointer-events:none; transition:opacity 0.2s ease;}
.overlay.show{ opacity:1; pointer-events:auto; }
.drawer{
  position:fixed; top:0; right:0; height:100vh; width:min(420px,92vw); background:var(--bg2); border-left:1px solid var(--line);
  z-index:51; transform:translateX(100%); transition:transform 0.28s cubic-bezier(.2,.9,.3,1); display:flex; flex-direction:column;
}
.drawer.show{ transform:translateX(0); }
.drawer-head{ display:flex; align-items:center; justify-content:space-between; padding:18px 20px; border-bottom:1px solid var(--line);}
.drawer-head h2{ font-family:'Space Grotesk',sans-serif; font-size:16px;}
.drawer-head button{ background:none; border:1px solid var(--line); color:var(--muted); width:30px; height:30px; border-radius:8px; cursor:pointer;}
.drawer-body{ padding:16px 20px; overflow-y:auto; flex:1; }
.log-item{ border:1px solid var(--line); border-radius:10px; padding:12px 14px; margin-bottom:10px; cursor:pointer; transition: all 0.15s ease;}
.log-item:hover{ border-color:var(--accent); background:rgba(255,255,255,0.02);}
.log-item .li-top{ display:flex; justify-content:space-between; font-family:'IBM Plex Mono',monospace; font-size:10px; color:var(--muted2); margin-bottom:6px;}
.log-item .li-title{ font-size:13px; font-weight:600; margin-bottom:2px;}
.log-item .li-mission{ font-size:11.5px; color:var(--muted); }
.empty-note{ color:var(--muted2); font-size:12.5px; text-align:center; margin-top:40px; font-family:'IBM Plex Mono',monospace; line-height:1.7;}

.cmdk{
  position:fixed; top:14vh; left:50%; transform:translateX(-50%); width:min(560px,90vw);
  background:var(--panel2); border:1px solid var(--line); border-radius:14px; z-index:60;
  opacity:0; pointer-events:none; transition: opacity 0.15s ease, transform 0.15s ease; box-shadow:0 30px 60px -20px rgba(0,0,0,0.7);
}
.cmdk.show{ opacity:1; pointer-events:auto; transform:translateX(-50%) translateY(0); }
.cmdk input{ width:100%; background:none; border:none; outline:none; color:var(--text); font-family:'IBM Plex Mono',monospace; font-size:15px; padding:18px 20px; border-bottom:1px solid var(--line);}
.cmdk-list{ max-height:320px; overflow-y:auto; padding:8px; }
.cmdk-item{ display:flex; align-items:center; gap:10px; padding:11px 12px; border-radius:9px; cursor:pointer; font-size:13.5px;}
.cmdk-item:hover, .cmdk-item.sel{ background:var(--accent-soft); }
.cmdk-item .num{ font-family:'IBM Plex Mono',monospace; color:var(--muted2); font-size:11px; width:20px;}

.toast-wrap{ position:fixed; bottom:24px; right:24px; z-index:70; display:flex; flex-direction:column; gap:8px; align-items:flex-end;}
.toast{
  background:var(--panel2); border:1px solid var(--line); color:var(--text); padding:11px 16px; border-radius:10px; font-size:12.5px;
  font-family:'IBM Plex Mono',monospace; box-shadow:0 12px 30px -10px rgba(0,0,0,0.6); animation: toastIn 0.25s ease, toastOut 0.3s ease 2.4s forwards;
  display:flex; align-items:center; gap:8px;
}
.toast .td{ width:6px; height:6px; border-radius:50%; background:var(--mint);}
@keyframes toastIn{ from{opacity:0; transform:translateY(8px);} to{opacity:1; transform:translateY(0);} }
@keyframes toastOut{ to{opacity:0; transform:translateY(-6px);} }

@media (max-width: 860px){
  .sidebar{ position:fixed; z-index:40; transform:translateX(-100%); box-shadow:20px 0 40px rgba(0,0,0,0.5); }
  .sidebar.open{ transform:translateX(0); }
  .hamburger{ display:flex; align-items:center; justify-content:center; }
  .view{ padding:24px 18px 70px; }
  h1.title{ font-size:32px; }
  .radar{ width:280px; height:280px; }
}
</style>
</head>
<body data-accent="violet">
<div class="backdrop"></div>

<div id="boot">
  <div class="lines" id="bootLines"></div>
  <button class="skip" id="bootSkip">SKIP INTRO →</button>
</div>

<div class="app">
  <aside class="sidebar" id="sidebar">
    <div class="brand" id="brandHome">
      <div class="dot"></div>
      <div class="name">MISSION<span>CONTROL</span></div>
    </div>

    <div class="panel-box">
      <div class="label">Operator Status</div>
      <div class="rank-name" id="rankName">Cadet</div>
      <div class="xp-bar"><div class="xp-fill" id="xpFill" style="width:0%"></div></div>
      <div class="xp-caption" id="xpCaption">0 XP // NEXT RANK AT 50</div>
    </div>

    <div class="panel-box" style="padding-bottom:10px;">
      <div class="label">Active Mission</div>
      <div style="font-family:'IBM Plex Mono',monospace; font-size:12px; color:var(--text); line-height:1.5; word-break:break-word;" id="sideMissionLabel">— none set —</div>
    </div>

    <div class="nav-title">Navigation</div>
    <ul class="nav-list" id="navList"></ul>

    <div class="sidebar-foot">
      <button class="mini-btn" id="openCmdk"><span>Search modules</span><span>/</span></button>
      <button class="mini-btn" id="openLog"><span>Mission Log</span><span id="logCount">0</span></button>
      <button class="mini-btn" id="exportDossier"><span>Export dossier</span><span>⤓</span></button>
      <div class="theme-dots" id="themeDots" style="justify-content:center; margin-top:2px;">
        <div class="theme-dot active" data-c="violet" style="background:#7c5cff;"></div>
        <div class="theme-dot" data-c="amber" style="background:#ff9a4d;"></div>
        <div class="theme-dot" data-c="mint" style="background:#3ddc97;"></div>
        <div class="theme-dot" data-c="red" style="background:#ff5c6c;"></div>
      </div>
      <div class="foot-note">MISSION CONTROL V2.0 // LIVE AI CORE</div>
    </div>
  </aside>

  <main class="main">
    <div class="topbar">
      <button class="hamburger" id="hamburger">☰</button>
      <div class="mission-field">
        <span class="tag">ACTIVE MISSION:</span>
        <input id="topMissionInput" placeholder="Name your project idea…" />
      </div>
      <button class="icon-btn" id="topLog" title="Mission Log">☰</button>
    </div>
    <div class="view" id="view"></div>
  </main>
</div>

<div class="overlay" id="overlay"></div>

<div class="drawer" id="logDrawer">
  <div class="drawer-head"><h2>Mission Log</h2><button id="closeLog">✕</button></div>
  <div class="drawer-body" id="logBody"></div>
</div>

<div class="cmdk" id="cmdk">
  <input id="cmdkInput" placeholder="Jump to a module…" />
  <div class="cmdk-list" id="cmdkList"></div>
</div>

<div class="toast-wrap" id="toastWrap"></div>

<script>
/* ============ CONFIG ============ */
const MODEL = "claude-sonnet-4-6";

const MODULES = [
  { id:'idea', num:'01', title:'Idea Scanner', tag:'Feasibility, complexity & score for your concept.', glyph:'◎', search:false,
    build:(m)=>({
      system:"You are a blunt, expert startup CTO advisor. You evaluate app and project ideas fast and honestly, in tight structured markdown. No fluff, no disclaimers, no generic filler.",
      user:'Evaluate this project idea: "'+m+'".\\n\\nRespond in markdown with EXACTLY these section headers:\\n## Verdict\\n(one line: Feasible / Ambitious / High-Risk, plus a punchy one-sentence reason)\\n## Feasibility Score\\n(state as X/100)\\n## Complexity\\n(Low / Medium / High)\\n## Estimated Build Time\\n(for a solo builder MVP)\\n## Core Tech Stack\\n(bulleted, 4-6 items, specific to this idea)\\n## Top 3 Risks\\n(bulleted, one line each)\\n## The One Feature That Would Make This Stand Out\\n(1-2 sentences)\\n\\nKeep the whole response under 550 words. Be specific to the idea, never generic.'
    })},
  { id:'blueprint', num:'02', title:'Blueprint Architect', tag:'System architecture, data flow & API map.', glyph:'▦', search:false,
    build:(m)=>({
      system:"You are a principal software architect. You produce crisp, production-grade technical blueprints in markdown. No fluff.",
      user:'Produce a technical architecture blueprint for: "'+m+'".\\n\\nUse EXACTLY these markdown headers:\\n## System Overview\\n(2-3 sentences)\\n## Components\\n(bulleted: Frontend, Backend, Database, key 3rd-party services, one line each)\\n## Data Flow\\n(numbered steps, 4-6 steps)\\n## Suggested Schema\\n(a short fenced code block, key tables and fields only)\\n## Key API Endpoints\\n(bulleted, 5-8, formatted as METHOD /path — purpose)\\n## Scalability Note\\n(2-3 sentences)\\n\\nKeep under 650 words total, dense and specific to the idea.'
    })},
  { id:'explainer', num:'03', title:'Explain It 3 Ways', tag:'Beginner, developer & interview-ready breakdowns.', glyph:'◈', search:false,
    build:(m)=>({
      system:"You are a brilliant teacher who can explain any technical project clearly at any level.",
      user:'Explain the project "'+m+'" three ways, using EXACTLY these markdown headers:\\n## For a Beginner\\n(plain language, no jargon, 3-4 sentences, use an everyday analogy)\\n## For a Developer\\n(technical, 4-6 sentences, name real components and patterns)\\n## For Your Interview or Viva\\n(3 likely questions an interviewer would ask about this project, each followed by a sharp 2-sentence model answer)\\n\\nUnder 600 words total.'
    })},
  { id:'prompt-forge', num:'04', title:'Prompt Forge', tag:'A ready-to-paste master build prompt.', glyph:'▷', search:false,
    build:(m, extra)=>({
      system:"You are an elite prompt engineer who writes production-grade prompts for AI coding assistants.",
      user:'Write a single, ready-to-paste master build prompt for the AI coding assistant "'+extra.assistant+'" to build this project: "'+m+'".\\n\\nTarget depth: '+extra.depth+'.\\n\\nOutput ONLY one fenced markdown code block containing the prompt itself. Inside the prompt, include: role and context for the AI, core requirements (bulleted), tech constraints, and a definition of done. Keep the prompt itself under 380 words so it reads cleanly.'
    })},
  { id:'research', num:'05', title:'Research Lab', tag:'Real sources, found live, with citations.', glyph:'✦', search:true,
    build:(m)=>({
      system:"You are a meticulous researcher. You only reference sources you actually found via search just now. Never invent citations, titles, or URLs.",
      user:'Search for and summarize 3 real, relevant sources (academic papers, industry reports, or authoritative articles) related to building: "'+m+'".\\n\\nFor each source use this markdown format:\\n### [Title]\\n- **Source & year:**\\n- **Why it is relevant:** (1-2 sentences)\\n- **Key takeaway:** (1-2 sentences)\\n- **Link:** (the real URL)\\n\\nUnder 500 words total.'
    })},
  { id:'trend-radar', num:'06', title:'Trend Radar', tag:'Live scan of current tech trends & signals.', glyph:'◉', search:true,
    build:(m)=>({
      system:"You are a sharp technology analyst scanning the current landscape in real time via search.",
      user:'Search the web for current, recent trends, tools, or signals relevant to building: "'+m+'".\\n\\nRespond in markdown:\\n## Signals Detected\\n(bulleted, 4-5 current trends, tools or news items relevant to this idea, each one line, naming the real source)\\n## What This Means For You\\n(2-3 sentences of practical implication for someone building this now)\\n\\nUnder 450 words.'
    })},
  { id:'risk-radar', num:'07', title:'Risk & Pitfall Radar', tag:'Failure modes, edge cases & blind spots.', glyph:'▲', search:false,
    build:(m)=>({
      system:"You are a paranoid, experienced staff engineer who has seen every kind of project fail.",
      user:'List the biggest risks and pitfalls for building: "'+m+'".\\n\\nGroup into EXACTLY these markdown sections:\\n## Technical Risks\\n## UX Risks\\n## Security & Privacy Risks\\n## Business Risks\\n\\nEach section gets 2 bullets, each formatted as **Risk name** — mitigation, in one line.\\n\\nUnder 550 words.'
    })},
  { id:'rival-scan', num:'08', title:'Rival Scan', tag:'Live search for existing competitors.', glyph:'⌖', search:true,
    build:(m)=>({
      system:"You are a competitive intelligence analyst who researches live via search, never from memory alone.",
      user:'Search the web for existing products, apps, or open-source projects that already do something similar to: "'+m+'".\\n\\nRespond in markdown:\\n## Existing Players\\n(bulleted, up to 4, each formatted as **Name** — one-line description — how this new idea differs)\\n## The Gap\\n(2-3 sentences on what is missing that this project could own)\\n\\nUnder 450 words. If genuinely nothing similar turns up, say so plainly.'
    })},
  { id:'pitch-studio', num:'09', title:'Pitch Studio', tag:'Elevator pitch + 5-slide deck, live.', glyph:'▶', search:false, json:true,
    build:(m)=>({
      system:"You are a startup pitch coach. You respond ONLY with valid JSON. No markdown, no commentary, no code fences, no leading or trailing text.",
      user:'Create a pitch package for the project "'+m+'". Respond with ONLY this exact JSON shape (valid JSON, nothing else):\\n{"pitch":"a punchy 3-sentence elevator pitch","hook":"a tweet-length one-line hook","slides":[{"title":"Problem","bullets":["...","..."]},{"title":"Solution","bullets":["...","..."]},{"title":"How It Works","bullets":["...","..."]},{"title":"Why Now","bullets":["...","..."]},{"title":"The Ask","bullets":["...","..."]}]}\\nEach bullets array should have 2-3 short bullets specific to the idea.'
    })},
];

const EXAMPLES = ["Smart Plant-Watering App", "AI Recipe Generator From Fridge Photos", "Campus Lost & Found Board", "Habit-Streak Accountability Bot"];

/* ============ STATE ============ */
const state = {
  mission: "",
  xp: 0,
  history: [],
  route: "home",
  slideIdx: {},
};

/* ============ BOOT SEQUENCE ============ */
const bootLinesText = [
  "> INITIALIZING MISSION CONTROL v2.0 ...",
  "> ESTABLISHING NEURAL UPLINK ...",
  "> CALIBRATING RADAR ARRAY ...",
  "> LOADING 9 INTEL MODULES ...",
  "> ALL SUBROUTINES NOMINAL.",
  "> WELCOME, OPERATOR."
];
function runBoot(){
  const wrap = document.getElementById('bootLines');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduced){ finishBoot(); return; }
  let i=0;
  function step(){
    if(i>=bootLinesText.length){ setTimeout(finishBoot, 500); return; }
    const d = document.createElement('div');
    d.className='line';
    d.textContent = bootLinesText[i];
    wrap.appendChild(d);
    requestAnimationFrame(()=> d.classList.add('show'));
    i++;
    setTimeout(step, 320);
  }
  step();
}
function finishBoot(){
  document.getElementById('boot').classList.add('hide');
}
document.getElementById('bootSkip').addEventListener('click', finishBoot);
setTimeout(runBoot, 200);
setTimeout(finishBoot, 4500);

/* ============ TOASTS ============ */
function toast(msg){
  const wrap = document.getElementById('toastWrap');
  const t = document.createElement('div');
  t.className='toast';
  t.innerHTML = '<span class="td"></span>' + msg;
  wrap.appendChild(t);
  setTimeout(()=> t.remove(), 2800);
}

/* ============ RANK / XP ============ */
function getRank(xp){
  if(xp>=500) return {name:"Mission Director", next:null, floor:500};
  if(xp>=300) return {name:"Commander", next:500, floor:300};
  if(xp>=150) return {name:"Architect", next:300, floor:150};
  if(xp>=50) return {name:"Analyst", next:150, floor:50};
  return {name:"Cadet", next:50, floor:0};
}
function renderRank(){
  const r = getRank(state.xp);
  document.getElementById('rankName').textContent = r.name;
  const pct = r.next ? Math.min(100, Math.round(((state.xp - r.floor) / (r.next - r.floor)) * 100)) : 100;
  document.getElementById('xpFill').style.width = pct + '%';
  document.getElementById('xpCaption').textContent = r.next ? (state.xp + ' XP // NEXT RANK AT ' + r.next) : (state.xp + ' XP // MAX RANK REACHED');
}
function addXP(amount){
  state.xp += amount;
  renderRank();
  toast('+' + amount + ' XP earned');
}

/* ============ MISSION SYNC ============ */
function setMission(val, opts){
  state.mission = val;
  document.getElementById('topMissionInput').value = val;
  document.getElementById('sideMissionLabel').textContent = val ? val : '— none set —';
  const heroInput = document.getElementById('heroMissionInput');
  if(heroInput) heroInput.value = val;
  const modMissionField = document.getElementById('modMissionField');
  if(modMissionField) modMissionField.value = val;
}
document.getElementById('topMissionInput').addEventListener('input', (e)=> setMission(e.target.value));

/* ============ RENDER: SIDEBAR NAV ============ */
function renderNav(){
  const ul = document.getElementById('navList');
  ul.innerHTML = '';
  const homeLi = document.createElement('li');
  homeLi.className = 'nav-item' + (state.route==='home' ? ' active' : '');
  homeLi.innerHTML = '<span class="num">◆</span><span>Mission Control</span>' + (state.route==='home' ? '<span class="bullet"></span>' : '');
  homeLi.addEventListener('click', ()=> navigate('home'));
  ul.appendChild(homeLi);
  MODULES.forEach(mod=>{
    const li = document.createElement('li');
    li.className = 'nav-item' + (state.route===mod.id ? ' active' : '');
    li.innerHTML = '<span class="num">'+mod.num+'</span><span>'+mod.title+'</span>' + (state.route===mod.id ? '<span class="bullet"></span>' : '');
    li.addEventListener('click', ()=> navigate(mod.id));
    ul.appendChild(li);
  });
}

/* ============ NAVIGATE ============ */
function navigate(route){
  state.route = route;
  renderNav();
  if(route==='home') renderHome(); else renderModule(route);
  document.getElementById('sidebar').classList.remove('open');
  window.scrollTo(0,0);
}
document.getElementById('brandHome').addEventListener('click', ()=> navigate('home'));

/* ============ RADAR (HOME HERO) ============ */
function buildRadarSVG(){
  const size=360, cx=size/2, cy=size/2;
  const rings=[150,110,70];
  let svg = '<svg viewBox="0 0 '+size+' '+size+'">';
  svg += '<defs><radialGradient id="sweepGrad" cx="50%" cy="50%" r="50%">'+
         '<stop offset="0%" stop-color="var(--accent)" stop-opacity="0.35"/>'+
         '<stop offset="100%" stop-color="var(--accent)" stop-opacity="0"/></radialGradient></defs>';
  rings.forEach(r=>{
    svg += '<circle cx="'+cx+'" cy="'+cy+'" r="'+r+'" fill="none" stroke="var(--line)" stroke-width="1"/>';
  });
  svg += '<line x1="'+cx+'" y1="'+(cy-150)+'" x2="'+cx+'" y2="'+(cy+150)+'" stroke="var(--line)" stroke-width="1"/>';
  svg += '<line x1="'+(cx-150)+'" y1="'+cy+'" x2="'+(cx+150)+'" y2="'+cy+'" stroke="var(--line)" stroke-width="1"/>';
  // sweep
  svg += '<g style="transform-origin:'+cx+'px '+cy+'px; animation: spin 6s linear infinite;">'+
         '<path d="M '+cx+' '+cy+' L '+cx+' '+(cy-150)+' A 150 150 0 0 1 '+(cx+106)+' '+(cy-106)+' Z" fill="url(#sweepGrad)"/></g>';
  // center
  svg += '<circle cx="'+cx+'" cy="'+cy+'" r="4" fill="var(--accent)"/>';
  // nodes
  const n = MODULES.length;
  MODULES.forEach((mod, i)=>{
    const angle = (i / n) * Math.PI * 2 - Math.PI/2;
    const r = 150 - (i%2===0?0:36);
    const x = cx + r*Math.cos(angle);
    const y = cy + r*Math.sin(angle);
    const lx = cx + (r+16)*Math.cos(angle);
    const ly = cy + (r+16)*Math.sin(angle);
    svg += '<g class="radar-node" data-mod="'+mod.id+'">'+
           '<circle class="core" cx="'+x+'" cy="'+y+'" r="6" fill="var(--bg)" stroke="var(--accent)" stroke-width="2"/>'+
           '<circle cx="'+x+'" cy="'+y+'" r="2" fill="var(--accent)"/>'+
           '</g>';
  });
  svg += '</svg>';
  return svg;
}
function wireRadarNodes(){
  document.querySelectorAll('.radar-node').forEach(node=>{
    node.addEventListener('click', ()=> navigate(node.getAttribute('data-mod')));
  });
}

/* ============ RENDER: HOME ============ */
function renderHome(){
  const view = document.getElementById('view');
  view.innerHTML =
    '<div class="hero">'+
      '<div class="eyebrow">AI Build Console // v2.0</div>'+
      '<h1 class="title">Mission Control</h1>'+
      '<p class="subtitle">Feed it one idea. Nine live AI modules interrogate it — feasibility, architecture, research, competitors, risk, pitch — for real, powered by Claude.</p>'+
    '</div>'+
    '<div class="radar-wrap">'+
      '<div class="radar" id="radarHost">'+buildRadarSVG()+'</div>'+
      '<div>'+
        '<div class="mission-hero-field">'+
          '<input id="heroMissionInput" placeholder="e.g. Smart plant-watering app" value="'+escapeAttr(state.mission)+'"/>'+
          '<button id="heroSetBtn">Set Mission</button>'+
        '</div>'+
        '<div class="chips" id="chipRow"></div>'+
      '</div>'+
    '</div>'+
    '<div class="nav-title" style="margin:8px 0 12px;">All Modules</div>'+
    '<div class="module-grid" id="moduleGrid"></div>';

  const chipRow = document.getElementById('chipRow');
  EXAMPLES.forEach(ex=>{
    const c = document.createElement('div');
    c.className='chip';
    c.textContent = ex;
    c.addEventListener('click', ()=>{ setMission(ex); toast('Mission set: ' + ex); });
    chipRow.appendChild(c);
  });

  document.getElementById('heroSetBtn').addEventListener('click', ()=>{
    setMission(document.getElementById('heroMissionInput').value.trim());
    toast('Mission locked in');
  });
  document.getElementById('heroMissionInput').addEventListener('keydown', (e)=>{
    if(e.key==='Enter'){ setMission(e.target.value.trim()); toast('Mission locked in'); }
  });

  const grid = document.getElementById('moduleGrid');
  MODULES.forEach(mod=>{
    const card = document.createElement('div');
    card.className='module-card';
    card.innerHTML =
      (mod.search ? '<span class="live-tag">● LIVE SEARCH</span>' : '') +
      '<span class="glyph">'+mod.glyph+'</span>'+
      '<div class="mnum">'+mod.num+' // MODULE</div>'+
      '<h3>'+mod.title+'</h3><p>'+mod.tag+'</p>';
    card.addEventListener('click', ()=> navigate(mod.id));
    grid.appendChild(card);
  });

  wireRadarNodes();
}

/* ============ RENDER: MODULE ============ */
function escapeAttr(s){ return (s||'').replace(/"/g,'&quot;'); }
function escapeHtml(s){ return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function renderModule(id){
  const mod = MODULES.find(m=>m.id===id);
  const view = document.getElementById('view');
  let extraHtml = '';
  if(id==='prompt-forge'){
    extraHtml =
      '<div class="select-row">'+
        '<div class="field-block"><label class="field-label">Target AI Assistant</label>'+
        '<select class="field-value" id="pfAssistant">'+
          '<option>Claude Code</option><option>Cursor</option><option>ChatGPT</option><option>Windsurf</option><option>General LLM</option>'+
        '</select></div>'+
        '<div class="field-block"><label class="field-label">Depth</label>'+
        '<select class="field-value" id="pfDepth">'+
          '<option>Quick MVP</option><option>Full Production Build</option>'+
        '</select></div>'+
      '</div>';
  }
  view.innerHTML =
    '<div class="module-header">'+
      '<div class="mnum-big">'+mod.num+' // INTEL MODULE'+(mod.search?' // LIVE SEARCH ENABLED':'')+'</div>'+
      '<h1><span class="glyph">'+mod.glyph+'</span>'+mod.title+'</h1>'+
      '<p>'+mod.tag+'</p>'+
    '</div>'+
    '<div class="field-block">'+
      '<label class="field-label">Mission Target</label>'+
      '<input class="field-value" id="modMissionField" placeholder="Type or set a mission from the top bar…" value="'+escapeAttr(state.mission)+'"/>'+
    '</div>'+
    extraHtml+
    '<button class="run-btn" id="runBtn"><span class="spinner"></span><span id="runBtnLabel">Initialize '+mod.title+'</span></button>'+
    '<div class="log-console" id="logConsole"></div>'+
    '<div id="errorZone"></div>'+
    '<div id="outputZone"></div>';

  document.getElementById('modMissionField').addEventListener('input', (e)=> setMission(e.target.value));

  document.getElementById('runBtn').addEventListener('click', ()=> runModule(mod));
}

/* ============ RUN MODULE (API CALL) ============ */
const LOG_STAGES = [
  "> establishing uplink to model core...",
  "> transmitting mission parameters...",
  "> parsing telemetry stream...",
  "> compiling report..."
];
const LOG_STAGES_SEARCH = [
  "> establishing uplink to model core...",
  "> dispatching live web query...",
  "> cross-referencing sources...",
  "> compiling report..."
];

async function runModule(mod){
  const missionVal = document.getElementById('modMissionField').value.trim();
  if(!missionVal){ toast('Enter a mission target first'); document.getElementById('modMissionField').focus(); return; }
  setMission(missionVal);

  const btn = document.getElementById('runBtn');
  const label = document.getElementById('runBtnLabel');
  const errZone = document.getElementById('errorZone');
  const outZone = document.getElementById('outputZone');
  const logConsole = document.getElementById('logConsole');
  errZone.innerHTML=''; outZone.innerHTML='';
  btn.disabled = true; btn.classList.add('loading');
  label.textContent = 'Scanning…';
  logConsole.classList.add('show'); logConsole.innerHTML='';

  const stages = mod.search ? LOG_STAGES_SEARCH : LOG_STAGES;
  let stageI=0;
  const stageTimer = setInterval(()=>{
    if(stageI < stages.length){
      const d = document.createElement('div');
      d.className='lg'; d.textContent = stages[stageI];
      logConsole.appendChild(d);
      stageI++;
    }
  }, 550);

  let extra = {};
  if(mod.id==='prompt-forge'){
    extra.assistant = document.getElementById('pfAssistant').value;
    extra.depth = document.getElementById('pfDepth').value;
  }

  try{
    const built = mod.build(missionVal, extra);
    const body = {
      model: MODEL,
      max_tokens: 1000,
      system: built.system,
      messages: [{ role:"user", content: built.user }]
    };
    if(mod.search){ body.tools = [{ type:"web_search_20250305", name:"web_search" }]; }

    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    if(data.error){ throw new Error(data.error.message || "Model core rejected the request."); }
    const textBlocks = (data.content || []).filter(b=>b.type==="text").map(b=>b.text);
    const rawText = textBlocks.join("\\n\\n").trim();
    if(!rawText){ throw new Error("Empty response from model core."); }

    clearInterval(stageTimer);
    const doneLine = document.createElement('div');
    doneLine.className='lg'; doneLine.textContent='> report ready.';
    logConsole.appendChild(doneLine);

    renderOutput(mod, missionVal, rawText, outZone);

    state.history.unshift({ id: Date.now(), moduleTitle: mod.title, moduleNum: mod.num, mission: missionVal, content: rawText, json: !!mod.json, ts: new Date() });
    renderLogDrawer();
    document.getElementById('logCount').textContent = state.history.length;
    addXP(mod.search ? 25 : 15);

  }catch(err){
    clearInterval(stageTimer);
    logConsole.classList.remove('show');
    errZone.innerHTML =
      '<div class="error-box"><span>⚠ Uplink failed: '+escapeHtml(err.message || 'Unknown error')+'</span>'+
      '<button id="retryBtn">Retry</button></div>';
    document.getElementById('retryBtn').addEventListener('click', ()=> runModule(mod));
  }finally{
    btn.disabled=false; btn.classList.remove('loading');
    label.textContent = 'Initialize ' + mod.title;
  }
}

/* ============ RENDER OUTPUT ============ */
function renderOutput(mod, missionVal, rawText, outZone){
  if(mod.json){
    renderPitchOutput(missionVal, rawText, outZone);
    return;
  }
  const html = marked.parse(rawText);
  outZone.innerHTML =
    '<div class="output-card">'+
      '<div class="output-head">'+
        '<div class="oh-left"><span class="d"></span><span class="oh-title">'+mod.title+' // Report</span></div>'+
        '<div class="output-actions">'+
          '<button id="copyBtn">Copy</button>'+
          '<button id="downloadBtn">Download .md</button>'+
        '</div>'+
      '</div>'+
      '<div class="output-body">'+html+'</div>'+
    '</div>';
  document.getElementById('copyBtn').addEventListener('click', ()=>{
    navigator.clipboard.writeText(rawText).then(()=> toast('Copied to clipboard'));
  });
  document.getElementById('downloadBtn').addEventListener('click', ()=> downloadMd(mod.title, missionVal, rawText));
}

function renderPitchOutput(missionVal, rawText, outZone){
  let data;
  try{
    let cleaned = rawText.trim().replace(/^```json/,'').replace(/^```/,'').replace(/```$/,'').trim();
    data = JSON.parse(cleaned);
  }catch(e){
    outZone.innerHTML = '<div class="output-card"><div class="output-body">'+marked.parse(rawText)+'</div></div>';
    return;
  }
  const slideId = 'pitch-'+Date.now();
  state.slideIdx[slideId]=0;
  outZone.innerHTML =
    '<div class="output-card">'+
      '<div class="output-head">'+
        '<div class="oh-left"><span class="d"></span><span class="oh-title">Pitch Studio // Deck</span></div>'+
        '<div class="output-actions"><button id="copyPitchBtn">Copy pitch</button><button id="downloadPitchBtn">Download .md</button></div>'+
      '</div>'+
      '<div class="output-body">'+
        '<div class="pitch-top">'+
          '<div class="pitch-block"><div class="pl">Hook</div><div class="hook">"'+escapeHtml(data.hook||'')+'"</div></div>'+
          '<div class="pitch-block"><div class="pl">Elevator Pitch</div><div class="pitch-text">'+escapeHtml(data.pitch||'')+'</div></div>'+
        '</div>'+
        '<div class="slides-wrap">'+
          '<div class="slide-stage" id="slideStage-'+slideId+'"></div>'+
          '<div class="slide-nav">'+
            '<button id="prevSlide-'+slideId+'">‹</button>'+
            '<div class="dots" id="dots-'+slideId+'"></div>'+
            '<button id="nextSlide-'+slideId+'">›</button>'+
          '</div>'+
        '</div>'+
      '</div>'+
    '</div>';

  function renderSlide(){
    const idx = state.slideIdx[slideId];
    const s = data.slides[idx];
    document.getElementById('slideStage-'+slideId).innerHTML =
      '<div class="sn">SLIDE '+(idx+1)+' / '+data.slides.length+'</div>'+
      '<h3>'+escapeHtml(s.title)+'</h3>'+
      '<ul>'+ s.bullets.map(b=>'<li>'+escapeHtml(b)+'</li>').join('') +'</ul>';
    const dotsHost = document.getElementById('dots-'+slideId);
    dotsHost.innerHTML = data.slides.map((_,i)=> '<div class="dt'+(i===idx?' active':'')+'" data-i="'+i+'"></div>').join('');
    dotsHost.querySelectorAll('.dt').forEach(dt=> dt.addEventListener('click', ()=>{ state.slideIdx[slideId]=parseInt(dt.getAttribute('data-i')); renderSlide(); }));
  }
  renderSlide();
  document.getElementById('prevSlide-'+slideId).addEventListener('click', ()=>{
    state.slideIdx[slideId] = (state.slideIdx[slideId]-1+data.slides.length)%data.slides.length; renderSlide();
  });
  document.getElementById('nextSlide-'+slideId).addEventListener('click', ()=>{
    state.slideIdx[slideId] = (state.slideIdx[slideId]+1)%data.slides.length; renderSlide();
  });
  document.getElementById('copyPitchBtn').addEventListener('click', ()=>{
    navigator.clipboard.writeText(data.hook+'\\n\\n'+data.pitch).then(()=> toast('Pitch copied'));
  });
  document.getElementById('downloadPitchBtn').addEventListener('click', ()=>{
    let md = '# Pitch: '+missionVal+'\\n\\n**Hook:** '+data.hook+'\\n\\n**Elevator Pitch:** '+data.pitch+'\\n\\n## Slides\\n\\n';
    data.slides.forEach((s,i)=>{ md += (i+1)+'. **'+s.title+'**\\n' + s.bullets.map(b=>'   - '+b).join('\\n') + '\\n\\n'; });
    downloadMd('Pitch Studio', missionVal, md, true);
  });
}

function downloadMd(title, missionVal, content, preformatted){
  const md = preformatted ? content : ('# ' + title + '\\n### Mission: ' + missionVal + '\\n\\n' + content);
  const blob = new Blob([md], {type:'text/markdown'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = title.toLowerCase().replace(/\\s+/g,'-') + '.md';
  a.click();
  URL.revokeObjectURL(url);
  toast('Downloaded ' + a.download);
}

/* ============ MISSION LOG DRAWER ============ */
function renderLogDrawer(){
  const body = document.getElementById('logBody');
  if(state.history.length===0){
    body.innerHTML = '<div class="empty-note">No reports yet.<br/>Run a module to populate your mission log.</div>';
    return;
  }
  body.innerHTML='';
  state.history.forEach(entry=>{
    const div = document.createElement('div');
    div.className='log-item';
    div.innerHTML =
      '<div class="li-top"><span>'+entry.moduleNum+' // '+entry.moduleTitle.toUpperCase()+'</span><span>'+timeAgo(entry.ts)+'</span></div>'+
      '<div class="li-title">'+escapeHtml(entry.mission)+'</div>'+
      '<div class="li-mission">Tap to reopen report</div>';
    div.addEventListener('click', ()=>{
      const mod = MODULES.find(m=>m.title===entry.moduleTitle);
      navigate(mod.id);
      setTimeout(()=>{
        document.getElementById('modMissionField').value = entry.mission;
        const outZone = document.getElementById('outputZone');
        renderOutput(mod, entry.mission, entry.content, outZone);
      }, 30);
      closeDrawer();
    });
    body.appendChild(div);
  });
}
function timeAgo(ts){
  const s = Math.floor((new Date() - ts)/1000);
  if(s<60) return 'just now';
  if(s<3600) return Math.floor(s/60)+'m ago';
  return Math.floor(s/3600)+'h ago';
}

/* ============ DRAWER / OVERLAY / CMDK WIRING ============ */
const overlay = document.getElementById('overlay');
const logDrawer = document.getElementById('logDrawer');
function openDrawer(){ logDrawer.classList.add('show'); overlay.classList.add('show'); renderLogDrawer(); }
function closeDrawer(){ logDrawer.classList.remove('show'); overlay.classList.remove('show'); }
document.getElementById('openLog').addEventListener('click', openDrawer);
document.getElementById('topLog').addEventListener('click', openDrawer);
document.getElementById('closeLog').addEventListener('click', closeDrawer);
overlay.addEventListener('click', ()=>{ closeDrawer(); closeCmdk(); });

document.getElementById('exportDossier').addEventListener('click', ()=>{
  if(state.history.length===0){ toast('No reports to export yet'); return; }
  let md = '# Mission Dossier\\n\\n**Active Mission:** ' + (state.mission||'—') + '\\n\\n---\\n\\n';
  state.history.slice().reverse().forEach(entry=>{
    md += '## ' + entry.moduleNum + ' — ' + entry.moduleTitle + '\\n*Mission: ' + entry.mission + '*\\n\\n' + entry.content + '\\n\\n---\\n\\n';
  });
  downloadMd('Mission Dossier', state.mission, md, true);
});

/* command palette */
const cmdk = document.getElementById('cmdk');
function openCmdk(){ cmdk.classList.add('show'); overlay.classList.add('show'); document.getElementById('cmdkInput').value=''; renderCmdkList(''); document.getElementById('cmdkInput').focus(); }
function closeCmdk(){ cmdk.classList.remove('show'); overlay.classList.remove('show'); }
document.getElementById('openCmdk').addEventListener('click', openCmdk);
function renderCmdkList(q){
  const list = document.getElementById('cmdkList');
  const filtered = MODULES.filter(m=> m.title.toLowerCase().includes(q.toLowerCase()) || m.tag.toLowerCase().includes(q.toLowerCase()));
  list.innerHTML='';
  if(filtered.length===0){ list.innerHTML='<div class="empty-note">No modules match.</div>'; return; }
  filtered.forEach(mod=>{
    const item = document.createElement('div');
    item.className='cmdk-item';
    item.innerHTML = '<span class="num">'+mod.num+'</span><span>'+mod.title+'</span>';
    item.addEventListener('click', ()=>{ navigate(mod.id); closeCmdk(); });
    list.appendChild(item);
  });
}
document.getElementById('cmdkInput').addEventListener('input', (e)=> renderCmdkList(e.target.value));
document.addEventListener('keydown', (e)=>{
  if(e.key==='/' && document.activeElement.tagName!=='INPUT' && document.activeElement.tagName!=='TEXTAREA'){
    e.preventDefault(); openCmdk();
  } else if(e.key==='Escape'){ closeCmdk(); closeDrawer(); }
});

/* hamburger for mobile */
document.getElementById('hamburger').addEventListener('click', ()=> document.getElementById('sidebar').classList.toggle('open'));

/* theme switcher */
document.querySelectorAll('.theme-dot').forEach(dot=>{
  dot.addEventListener('click', ()=>{
    document.body.setAttribute('data-accent', dot.getAttribute('data-c'));
    document.querySelectorAll('.theme-dot').forEach(d=>d.classList.remove('active'));
    dot.classList.add('active');
  });
});

/* ============ INIT ============ */
renderNav();
renderRank();
renderHome();
</script>
</body>
</html>
"""


class MissionControlHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            body = PAGE_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def log_message(self, format, *args):
        # Quieter server logs
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))


def run(port=8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, MissionControlHandler)
    print(f"MISSION CONTROL is live at http://localhost:{port}")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run(port)
