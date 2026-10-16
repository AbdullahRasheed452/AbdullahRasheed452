#!/usr/bin/env python3
"""Generate the animated SVG assets used by the profile README.

Every asset is written twice, as ``*-dark.svg`` and ``*-light.svg``; README.md
picks the right one with <picture> + prefers-color-scheme. Animations use SMIL
(<animate>), which keeps running when GitHub serves an SVG through an <img>.
Each SVG's static state is its finished state, so nothing is lost if a viewer
does not animate.

To change content, edit PROJECTS / TIMELINE below, then run:

    python scripts/build_assets.py
"""

import math
import textwrap
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"
MONO_EM = 0.6  # monospace advance per char; forced with textLength so layout is font-independent

THEMES = {
    "dark": {
        "bg": "#0d1117", "card": "#161b22", "border": "#30363d", "grid": "#30363d",
        "text": "#e6edf3", "body": "#c9d1d9", "muted": "#8b949e",
        "blue": "#58a6ff", "purple": "#a371f7", "green": "#3fb950", "pink": "#f778ba",
        "orange": "#e3b341", "teal": "#39c5cf", "glow": 0.22,
    },
    "light": {
        "bg": "#ffffff", "card": "#f6f8fa", "border": "#d0d7de", "grid": "#d0d7de",
        "text": "#1f2328", "body": "#3d444d", "muted": "#59636e",
        "blue": "#0969da", "purple": "#8250df", "green": "#1a7f37", "pink": "#bf3989",
        "orange": "#9a6700", "teal": "#1b7c83", "glow": 0.12,
    },
}

GH = "https://github.com/AbdullahRasheed452/"

PROJECTS = [
    {
        "slug": "restoration-studio", "title": "Restoration & Sketch Studio", "accent": "purple",
        "category": "GENERATIVE AI", "date": "SEP 2026", "icon": "sparkle", "url": GH + "GENAI-1",
        "desc": "Four generative models in one web app: a universal autoencoder, hard-routed "
                "specialists, a soft mixture-of-experts and a face-to-sketch cGAN.",
        "tags": ["PyTorch", "ONNX", "FastAPI", "Docker"],
    },
    {
        "slug": "voiceflow", "title": "VoiceFlow AI", "accent": "blue",
        "category": "REAL-TIME SPEECH · NLP", "date": "JUN 2026", "icon": "wave",
        "url": GH + "voice_translator",
        "desc": "Real-time speech-to-speech translation across Urdu, English, Spanish, French, "
                "German and Arabic, with live transcription and spoken output.",
        "tags": ["Python", "Flask", "Whisper", "gTTS"],
    },
    {
        "slug": "quiz-generator", "title": "Quiz Generation System", "accent": "orange",
        "category": "CLASSICAL ML · NLP", "date": "APR 2026", "icon": "quiz",
        "url": GH + "Intelligent-Reading-Comprehension-Quiz-Generator",
        "desc": "Logistic Regression, SVM and Naive Bayes on RACE TF-IDF vectors, with a "
                "cosine-similarity distractor pipeline served in Streamlit.",
        "tags": ["Python", "scikit-learn", "TF-IDF", "Streamlit"],
    },
    {
        "slug": "stochastic-battlefield", "title": "Stochastic Battlefield", "accent": "pink",
        "category": "GAME AI", "date": "MAR 2026", "icon": "tree", "url": None,
        "desc": "Multi-agent stochastic game with three asymmetric AI agents using "
                "configurable-depth Expectiminimax and Alpha-Beta pruning.",
        "tags": ["Python", "Expectiminimax", "Alpha-Beta", "DearPyGui"],
    },
    {
        "slug": "warehouse-optimization", "title": "Warehouse Optimization", "accent": "teal",
        "category": "EVOLUTIONARY COMPUTING", "date": "FEB 2026", "icon": "genes", "url": None,
        "desc": "Genetic algorithm for warehouse layouts with minimal retrieval distance, "
                "benchmarked across population sizes and mutation rates.",
        "tags": ["Python", "Genetic Algorithms", "Benchmarking"],
    },
]

# state: "done" | "active" | "next"
TIMELINE = [
    ("LATE 2024", "Game Boy Emulator", "SOFTWARE ARCHITECTURE", "blue", "done",
     "Object-oriented design in C++: encapsulation, class hierarchies and persistent state."),
    ("MID 2025", "Xonix Game Engine", "DATA STRUCTURES", "teal", "done",
     "Min-heap leaderboards, priority queues, hash-table social graphs and AVL trees in C++."),
    ("EARLY 2026", "CureShare Medicine System", "SYSTEM DESIGN", "orange", "done",
     "Multi-role Java desktop platform with FIFO allocation, inventory alerts and dashboards."),
    ("FEB 2026", "Warehouse Optimization", "EVOLUTIONARY COMPUTING", "teal", "done",
     "Genetic algorithms (selection, crossover, mutation) minimising retrieval distance."),
    ("MAR 2026", "Stochastic Battlefield", "GAME AI", "pink", "done",
     "Multi-agent stochastic decision making with Expectiminimax and Alpha-Beta pruning."),
    ("APR 2026", "Quiz Generation System", "CLASSICAL ML", "orange", "done",
     "Logistic Regression and SVM on RACE TF-IDF vectors with cosine-similarity distractors."),
    ("JUN 2026", "VoiceFlow AI", "SPEECH · NLP", "blue", "done",
     "Real-time speech-to-speech translation with Web Speech, Whisper, Flask and gTTS."),
    ("JUL 2026", "FlyRank AI · ML Intern", "INTERNSHIP", "purple", "done",
     "Data preprocessing, model evaluation and Python pipelines on real search-ranking data."),
    ("SEP 2026", "Restoration & Sketch Studio", "GENERATIVE AI", "purple", "done",
     "Autoencoders, mixture-of-experts and a conditional GAN, served via ONNX and FastAPI."),
    ("NEXT", "Production AI", "ROADMAP", "muted", "next",
     "Large language models, RAG system design and production MLOps pipelines."),
]

TYPING = [
    "building machine learning systems",
    "deep learning · generative models",
    "multi-agent & agentic AI",
    "algorithms -> reproducible software",
]


# ───────────────────────────── primitives ─────────────────────────────

def esc(s):
    return escape(s, quote=True)


def mono(x, y, s, size, fill, anchor="start", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" textLength="{len(s) * size * MONO_EM:.1f}" '
            f'lengthAdjust="spacingAndGlyphs"{extra}>{esc(s)}</text>')


def sans(x, y, s, size, fill, weight=400, anchor="start", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{SANS}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{extra}>{esc(s)}</text>')


def pill(x, y, s, size, color, h=24):
    w = len(s) * size * MONO_EM + 20
    return w, (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{color}" '
               f'fill-opacity="0.12" stroke="{color}" stroke-opacity="0.4"/>'
               + mono(x + 10, y + h / 2 + size * 0.36, s, size, color))


def document(w, h, label, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(label)}">\n<title>{esc(label)}</title>\n{body}\n</svg>\n')


def discrete(attr, events, total, base):
    """A discrete SMIL animation stepping through (time, value) events over a `total`-second loop."""
    pts = {0.0: base}
    for tm, v in events:
        pts[round(tm / total, 4)] = v
    keys = sorted(pts)
    return (f'<animate attributeName="{attr}" dur="{total:.2f}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="{";".join(f"{k:.4f}" for k in keys)}" '
            f'values="{";".join(f"{pts[k]:.1f}" for k in keys)}"/>')


def typewriter(phrases, x, y, size, color, cursor):
    type_s, hold_s, erase_s, gap_s = 0.065, 1.9, 0.03, 0.45
    cw = size * MONO_EM
    timelines, t = [], 0.0
    for p in phrases:
        n = len(p)
        ev = [(t + k * type_s, k) for k in range(n + 1)]
        hold_end = t + n * type_s + hold_s
        ev += [(hold_end + (n - k) * erase_s, k) for k in range(n - 1, -1, -1)]
        timelines.append(ev)
        t = hold_end + n * erase_s + gap_s
    total = t

    out = []
    for i, (p, ev) in enumerate(zip(phrases, timelines)):
        full = len(p) * cw if i == 0 else 0
        anim = discrete("width", [(tm, k * cw) for tm, k in ev], total, 0)
        out.append(f'<clipPath id="type{i}"><rect x="{x}" y="{y - size}" height="{size * 1.6}" '
                   f'width="{full:.1f}">{anim}</rect></clipPath>')
        out.append(f'<g clip-path="url(#type{i})">{mono(x, y, p, size, color)}</g>')
    cx = x + 2
    anim = discrete("x", [(tm, cx + k * cw) for ev in timelines for tm, k in ev], total, cx)
    out.append(f'<rect x="{cx + len(phrases[0]) * cw:.1f}" y="{y - size * 0.82:.1f}" width="{size * 0.5:.1f}" '
               f'height="{size * 1.04:.1f}" fill="{cursor}">{anim}'
               f'<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" '
               f'repeatCount="indefinite"/></rect>')
    return "\n".join(out)


# ───────────────────────────── header ─────────────────────────────

def header(t):
    W, H = 1200, 340
    out = [f'''<defs>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="20"/></clipPath>
  <linearGradient id="bgfill" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{t['card']}"/><stop offset="1" stop-color="{t['bg']}"/>
  </linearGradient>
  <pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1.1" fill="{t['grid']}"/>
  </pattern>
  <filter id="blur" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="60"/></filter>
  <linearGradient id="name" gradientUnits="userSpaceOnUse" x1="60" y1="0" x2="700" y2="0" spreadMethod="repeat">
    <stop offset="0" stop-color="{t['blue']}"/>
    <stop offset="0.5" stop-color="{t['purple']}"/>
    <stop offset="1" stop-color="{t['blue']}"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="640 0" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bgfill)"/>
  <rect width="{W}" height="{H}" fill="url(#dots)" opacity="0.55"/>
  <circle cx="960" cy="70" r="170" fill="{t['blue']}" opacity="{t['glow']}" filter="url(#blur)">
    <animate attributeName="cx" values="960;1040;960" dur="14s" repeatCount="indefinite"/>
  </circle>
  <circle cx="200" cy="330" r="190" fill="{t['purple']}" opacity="{t['glow'] * 0.9:.2f}" filter="url(#blur)">
    <animate attributeName="cx" values="200;300;200" dur="17s" repeatCount="indefinite"/>
  </circle>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="{t['border']}"/>''']

    out.append(mono(64, 94, ">", 15, t["green"]) + mono(82, 94, "whoami", 15, t["muted"]))
    out.append(sans(60, 166, "Abdullah Rasheed", 64, "url(#name)", 700, extra=' letter-spacing="-1.5"'))
    out.append(
        f'<text x="64" y="212" font-family="{SANS}" font-size="20" font-weight="500" fill="{t["text"]}">'
        f'Computer Science<tspan fill="{t["muted"]}"> @ </tspan><tspan fill="{t["blue"]}">FAST NUCES</tspan>'
        f'<tspan fill="{t["muted"]}">  ·  ex-</tspan>ML Engineering Intern<tspan fill="{t["muted"]}"> @ </tspan>'
        f'<tspan fill="{t["purple"]}">FlyRank AI</tspan></text>')
    out.append(mono(64, 272, "$", 19, t["green"]))
    out.append(typewriter(TYPING, 64 + 2 * 19 * MONO_EM, 272, 19, t["body"], t["blue"]))

    # neural network: signals travel layer by layer, nodes light up as they arrive
    layers, xs, colors = [3, 5, 5, 2], [850, 940, 1030, 1120], ["blue", "purple", "purple", "green"]
    step, cycle = 0.6, 2.4
    pos = [[(xs[l], 165 + (j - (n - 1) / 2) * 50) for j in range(n)] for l, n in enumerate(layers)]
    edges, signals, idx = [], [], 0
    for l in range(len(layers) - 1):
        for a in pos[l]:
            for b in pos[l + 1]:
                edges.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" '
                             f'stroke="{t["muted"]}" stroke-opacity="0.3" stroke-width="1"/>')
                if idx % 3 == 0:
                    L = math.dist(a, b)
                    begin = l * step + (idx % 4) * 0.05
                    signals.append(
                        f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{t[colors[l + 1]]}" '
                        f'stroke-width="2.2" stroke-linecap="round" stroke-dasharray="14 {L:.1f}" stroke-dashoffset="14">'
                        f'<animate attributeName="stroke-dashoffset" values="14;{-L:.1f};{-L:.1f}" keyTimes="0;0.25;1" '
                        f'dur="{cycle}s" begin="{begin:.2f}s" repeatCount="indefinite"/></line>')
                idx += 1
    nodes = []
    for l, col in enumerate(pos):
        c = t[colors[l]]
        for (x, y) in col:
            nodes.append(
                f'<circle cx="{x}" cy="{y}" r="9" fill="{t["card"]}" stroke="{c}" stroke-width="2"/>'
                f'<circle cx="{x}" cy="{y}" r="4" fill="{c}" opacity="0.9">'
                f'<animate attributeName="opacity" values="0.3;1;0.3;0.3" keyTimes="0;0.12;0.4;1" '
                f'dur="{cycle}s" begin="{l * step:.2f}s" repeatCount="indefinite"/></circle>')
    labels = [mono(x, 312, s, 11, t["muted"], anchor="middle")
              for x, s in zip(xs, ["input", "h1", "h2", "output"])]
    out += edges + signals + nodes + labels
    return document(W, H, "Abdullah Rasheed — Computer Science at FAST NUCES, former ML Engineering Intern at FlyRank AI",
                    "\n".join(out))


# ───────────────────────────── project cards ─────────────────────────────

def icon(kind, c):
    if kind == "sparkle":
        return (f'<path d="M20 8C21.6 17 24 19.4 33 21C24 22.6 21.6 25 20 34C18.4 25 16 22.6 7 21C16 19.4 18.4 17 20 8Z" fill="{c}"/>'
                f'<path d="M33 6C33.5 8.6 34.4 9.5 37 10C34.4 10.5 33.5 11.4 33 14C32.5 11.4 31.6 10.5 29 10C31.6 9.5 32.5 8.6 33 6Z" fill="{c}">'
                f'<animate attributeName="opacity" values="1;0.15;1" dur="2.2s" repeatCount="indefinite"/></path>')
    if kind == "wave":
        bars = []
        for i, (lo, hi, d) in enumerate([(6, 14, 1.1), (10, 24, 0.9), (8, 30, 1.2), (10, 22, 0.8), (6, 14, 1.0)]):
            x = 9 + i * 6
            bars.append(f'<rect x="{x}" y="{22 - hi / 2}" width="3.6" height="{hi}" rx="1.8" fill="{c}">'
                        f'<animate attributeName="height" values="{hi};{lo};{hi}" dur="{d}s" repeatCount="indefinite"/>'
                        f'<animate attributeName="y" values="{22 - hi / 2};{22 - lo / 2};{22 - hi / 2}" dur="{d}s" repeatCount="indefinite"/></rect>')
        return "".join(bars)
    if kind == "doc":
        return (f'<rect x="11" y="7" width="22" height="30" rx="4" fill="none" stroke="{c}" stroke-width="2.4"/>'
                + "".join(f'<rect x="16" y="{y}" width="{w}" height="2.6" rx="1.3" fill="{c}" opacity="0.7"/>'
                          for y, w in [(14, 12), (19.5, 9), (25, 12)])
                + f'<rect x="8" y="12" width="28" height="2" rx="1" fill="{c}">'
                  f'<animate attributeName="y" values="11;31;11" dur="2.6s" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" values="0.9;0.3;0.9" dur="2.6s" repeatCount="indefinite"/></rect>')
    if kind == "quiz":
        return (sans(22, 31, "?", 27, c, 700, anchor="middle")
                + f'<circle cx="22" cy="22" r="15" fill="none" stroke="{c}" stroke-width="2" stroke-dasharray="6 4">'
                  f'<animateTransform attributeName="transform" type="rotate" from="0 22 22" to="360 22 22" dur="12s" repeatCount="indefinite"/></circle>')
    if kind == "tree":
        pts = {"r": (22, 9), "a": (13, 21), "b": (31, 21), "a1": (8, 34), "a2": (18, 34), "b1": (26, 34), "b2": (36, 34)}
        links = [("r", "a"), ("r", "b"), ("a", "a1"), ("a", "a2"), ("b", "b1"), ("b", "b2")]
        s = "".join(f'<line x1="{pts[p][0]}" y1="{pts[p][1]}" x2="{pts[q][0]}" y2="{pts[q][1]}" stroke="{c}" stroke-width="1.6" opacity="0.6"/>'
                    for p, q in links)
        for i, (k, (x, y)) in enumerate(pts.items()):
            s += (f'<circle cx="{x}" cy="{y}" r="3.2" fill="{c}"><animate attributeName="opacity" '
                  f'values="1;0.25;1" dur="2.8s" begin="{i * 0.35:.2f}s" repeatCount="indefinite"/></circle>')
        return s
    if kind == "genes":
        s = ""
        for r in range(3):
            for col in range(3):
                i = r * 3 + col
                op = [0.9, 0.35, 0.6, 0.35, 0.9, 0.5, 0.6, 0.5, 0.9][i]
                anim = (f'<animate attributeName="opacity" values="{op};0.15;{op}" dur="3s" begin="{i * 0.33:.2f}s" '
                        f'repeatCount="indefinite"/>') if i in (1, 5, 6) else ""
                s += f'<rect x="{9 + col * 9.5}" y="{9 + r * 9.5}" width="7.5" height="7.5" rx="2" fill="{c}" opacity="{op}">{anim}</rect>'
        return s
    raise ValueError(kind)


def project_card(t, p, delay):
    W, H = 460, 232
    a = t[p["accent"]]
    sid = "shine"
    out = [f'''<defs>
  <linearGradient id="{sid}" gradientUnits="userSpaceOnUse" x1="-300" y1="0" x2="0" y2="0">
    <stop offset="0" stop-color="{a}" stop-opacity="0"/>
    <stop offset="0.5" stop-color="{a}" stop-opacity="0.95"/>
    <stop offset="1" stop-color="{a}" stop-opacity="0"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;0 0;{W + 300} 0" keyTimes="0;0.45;1" dur="7s" begin="{delay}s" repeatCount="indefinite"/>
  </linearGradient>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{t['card']}" stroke="{t['border']}"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="none" stroke="url(#{sid})" stroke-width="1.6"/>
<rect x="24" y="24" width="44" height="44" rx="11" fill="{a}" fill-opacity="0.14"/>
<g transform="translate(24 24)">{icon(p["icon"], a)}</g>''']
    out.append(sans(84, 45, p["title"], 17, t["text"], 600))
    out.append(mono(84, 65, p["category"], 10.5, a))
    if p["date"] == "ACTIVE":
        out.append(f'<circle cx="{W - 80}" cy="41" r="4" fill="{t["green"]}"/>'
                   f'<circle cx="{W - 80}" cy="41" r="4" fill="none" stroke="{t["green"]}" stroke-width="1.5">'
                   f'<animate attributeName="r" values="4;11" dur="1.8s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0.9;0" dur="1.8s" repeatCount="indefinite"/></circle>')
        out.append(mono(W - 24, 45, "ACTIVE", 11, t["green"], anchor="end"))
    else:
        out.append(mono(W - 24, 45, p["date"], 11, t["muted"], anchor="end"))
    if p["url"]:
        out.append(mono(W - 24, 65, "repo ->", 10.5, t["muted"], anchor="end"))
    for i, line in enumerate(textwrap.wrap(p["desc"], 58, break_on_hyphens=False)[:3]):
        out.append(sans(24, 104 + i * 21, line, 13.5, t["body"]))
    x = 24
    for tag in p["tags"]:
        w, s = pill(x, H - 48, tag, 11, a)
        out.append(s)
        x += w + 8
    return document(W, H, f'{p["title"]}: {p["desc"]}', "\n".join(out))


# ───────────────────────────── timeline ─────────────────────────────

def timeline(t):
    W, spine, cw, ch, step, top = 900, 450, 400, 104, 74, 20
    H = top * 2 + step * (len(TIMELINE) - 1) + ch
    states = [e[4] for e in TIMELINE]
    reached = states.index("active") if "active" in states else len(states) - 1 - states[::-1].index("done")
    active_y = top + step * reached + ch / 2
    end_y = top + step * (len(TIMELINE) - 1) + ch / 2
    first_y = top + ch / 2
    L = active_y - first_y
    out = [f'''<defs>
  <linearGradient id="spinegrad" gradientUnits="userSpaceOnUse" x1="{spine}" y1="{first_y}" x2="{spine}" y2="{active_y}">
    <stop offset="0" stop-color="{t['blue']}"/><stop offset="0.6" stop-color="{t['purple']}"/><stop offset="1" stop-color="{t['green']}"/>
  </linearGradient>
</defs>
<line x1="{spine}" y1="{first_y}" x2="{spine}" y2="{end_y}" stroke="{t['border']}" stroke-width="2" stroke-dasharray="4 5"/>
<line x1="{spine}" y1="{first_y}" x2="{spine}" y2="{active_y}" stroke="url(#spinegrad)" stroke-width="2.5"
      stroke-dasharray="{L:.0f}" stroke-dashoffset="0">
  <animate attributeName="stroke-dashoffset" values="{L:.0f};0" dur="2.4s" calcMode="spline" keySplines="0.3 0 0.2 1" fill="freeze"/>
</line>
<line x1="{spine}" y1="{first_y}" x2="{spine}" y2="{active_y}" stroke="{t['text']}" stroke-opacity="0.85" stroke-width="2.5"
      stroke-linecap="round" stroke-dasharray="26 {L:.0f}" stroke-dashoffset="26">
  <animate attributeName="stroke-dashoffset" values="26;{-L:.0f};{-L:.0f}" keyTimes="0;0.7;1" dur="4.5s" begin="2.4s" repeatCount="indefinite"/>
</line>''']
    for i, (date, title, cat, accent, state, desc) in enumerate(TIMELINE):
        y = top + i * step
        ny = y + ch / 2
        left = i % 2 == 0
        x = spine - 26 - cw if left else spine + 26
        a = t[accent]
        edge = x + cw if left else x
        out.append(f'<line x1="{edge}" y1="{ny}" x2="{spine}" y2="{ny}" stroke="{t["border"]}" stroke-width="1.5"/>')
        if state == "active":
            card = f'fill="{a}" fill-opacity="0.08" stroke="{a}" stroke-width="1.6"'
        elif state == "next":
            card = f'fill="none" stroke="{t["border"]}" stroke-width="1.5" stroke-dasharray="6 5"'
        else:
            card = f'fill="{t["card"]}" stroke="{t["border"]}"'
        out.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="12" {card}/>')
        out.append(mono(x + 18, y + 25, date, 11, a))
        out.append(mono(x + cw - 18, y + 25, cat, 9.5, t["muted"], anchor="end"))
        out.append(sans(x + 18, y + 50, title, 16, t["text"], 600))
        for j, line in enumerate(textwrap.wrap(desc, 56, break_on_hyphens=False)[:2]):
            out.append(sans(x + 18, y + 72 + j * 18, line, 12.5, t["body"]))
        if state == "active":
            out.append(f'<circle cx="{spine}" cy="{ny}" r="8" fill="{a}"/>'
                       f'<circle cx="{spine}" cy="{ny}" r="8" fill="none" stroke="{a}" stroke-width="2">'
                       f'<animate attributeName="r" values="8;22" dur="2s" repeatCount="indefinite"/>'
                       f'<animate attributeName="opacity" values="0.9;0" dur="2s" repeatCount="indefinite"/></circle>')
        elif state == "next":
            out.append(f'<circle cx="{spine}" cy="{ny}" r="8" fill="{t["bg"]}" stroke="{t["muted"]}" stroke-width="2" stroke-dasharray="3 3">'
                       f'<animateTransform attributeName="transform" type="rotate" from="0 {spine} {ny}" to="360 {spine} {ny}" dur="8s" repeatCount="indefinite"/></circle>')
        else:
            out.append(f'<circle cx="{spine}" cy="{ny}" r="7" fill="{t["bg"]}" stroke="{a}" stroke-width="2.5"/>'
                       f'<circle cx="{spine}" cy="{ny}" r="2.6" fill="{a}"/>')
    return document(W, H, "Timeline of projects from late 2024 to now", "\n".join(out))


# ───────────────────────────── footer ─────────────────────────────

def wave_path(W, H, base, amp, phase, freq):
    pts = []
    for i in range(61):
        x = W * i / 60
        y = base + amp * math.sin(freq * 2 * math.pi * i / 60 + phase) \
            + amp * 0.45 * math.sin(2.3 * freq * 2 * math.pi * i / 60 + phase * 1.7)
        pts.append(f"{x:.1f} {y:.1f}")
    return f"M0 {H} L" + " L".join(pts) + f" L{W} {H} Z"


def footer(t):
    W, H = 1200, 170
    out = [f'''<defs>
  <linearGradient id="wavegrad" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{t['blue']}"/><stop offset="0.5" stop-color="{t['purple']}"/><stop offset="1" stop-color="{t['blue']}"/>
  </linearGradient>
</defs>''']
    for base, amp, freq, op, dur in [(100, 14, 1.0, 0.18, 11), (112, 12, 1.4, 0.28, 8), (126, 9, 1.8, 0.45, 6)]:
        frames = [wave_path(W, H, base, amp, ph, freq) for ph in (0, math.pi, 2 * math.pi)]
        out.append(f'<path d="{frames[0]}" fill="url(#wavegrad)" opacity="{op}">'
                   f'<animate attributeName="d" values="{";".join(frames)}" dur="{dur}s" repeatCount="indefinite"/></path>')
    s1, s2, s3 = "print(", '"thanks for visiting"', ")"
    x0 = W / 2 - (len(s1 + s2 + s3) * 20 * MONO_EM) / 2
    cw = 20 * MONO_EM
    out.append(mono(x0, 58, s1, 20, t["purple"]) + mono(x0 + len(s1) * cw, 58, s2, 20, t["green"])
               + mono(x0 + len(s1 + s2) * cw, 58, s3, 20, t["purple"]))
    return document(W, H, "Thanks for visiting", "\n".join(out))


def main():
    (OUT / "projects").mkdir(parents=True, exist_ok=True)
    for name, t in THEMES.items():
        (OUT / f"header-{name}.svg").write_text(header(t), encoding="utf-8")
        (OUT / f"timeline-{name}.svg").write_text(timeline(t), encoding="utf-8")
        (OUT / f"footer-{name}.svg").write_text(footer(t), encoding="utf-8")
        for i, p in enumerate(PROJECTS):
            (OUT / "projects" / f'{p["slug"]}-{name}.svg').write_text(project_card(t, p, i * 1.1), encoding="utf-8")
    print(f"wrote assets to {OUT}")


if __name__ == "__main__":
    main()
