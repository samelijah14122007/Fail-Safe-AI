"""
components.py — reusable UI fragments for FailSafe AI.

Keeps app.py focused on flow/logic; this module only renders markup.
Nothing here touches model inference or risk math.
"""

import streamlit as st


def load_css(path: str = "style.css") -> None:
    """Inject the design-system stylesheet once per page."""
    with open(path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="fs-eyebrow">{eyebrow}</div>
        <div class="fs-h1">{title}</div>
        <div class="fs-sub">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    st.markdown(f'<div class="fs-section-label">{text}</div>', unsafe_allow_html=True)


def divider() -> None:
    st.markdown('<hr class="fs-divider">', unsafe_allow_html=True)


def risk_pill(level: str) -> str:
    """Return an HTML pill for 'low' | 'medium' | 'high'."""
    mapping = {
        "low": ("fs-pill-low", "● LOW RISK"),
        "medium": ("fs-pill-med", "● MEDIUM RISK"),
        "high": ("fs-pill-high", "● HIGH RISK"),
    }
    cls, label = mapping[level]
    return f'<span class="fs-pill {cls}">{label}</span>'


def risk_gauge(risk_score: int, size: int = 220) -> str:
    """
    Build an SVG semicircular gauge (0-100 risk score).
    Color ramps slate -> amber -> rose as risk increases.
    Returns raw SVG markup (caller wraps it in st.markdown).
    """
    risk_score = max(0, min(100, risk_score))

    if risk_score < 30:
        color = "#2DD4BF"
    elif risk_score < 60:
        color = "#F5A524"
    else:
        color = "#FB7185"

    cx, cy, r = 110, 110, 86
    start_angle = 180
    end_angle = 180 - (risk_score / 100) * 180

    def polar(angle_deg, radius):
        import math
        rad = math.radians(angle_deg)
        return cx + radius * math.cos(rad), cy - radius * math.sin(rad)

    x1, y1 = polar(start_angle, r)
    x2, y2 = polar(end_angle, r)
    large_arc = 1 if risk_score > 50 else 0

    needle_angle = start_angle - (risk_score / 100) * 180
    nx, ny = polar(needle_angle, r - 18)

    svg = f"""
    <svg viewBox="0 0 220 140" width="{size}" height="{size * 140 // 220}"
         xmlns="http://www.w3.org/2000/svg">
      <path d="M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}"
            fill="none" stroke="#233047" stroke-width="14" stroke-linecap="round"/>
      <path d="M {x1:.2f} {y1:.2f} A {r} {r} 0 {large_arc} 1 {x2:.2f} {y2:.2f}"
            fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round"/>
      <line x1="{cx}" y1="{cy}" x2="{nx:.2f}" y2="{ny:.2f}"
            stroke="#E7ECF5" stroke-width="3" stroke-linecap="round"/>
      <circle cx="{cx}" cy="{cy}" r="6" fill="#E7ECF5"/>
      <text x="{cx}" y="{cy - 28}" text-anchor="middle"
            font-family="Space Grotesk, sans-serif" font-size="30" font-weight="700"
            fill="{color}">{risk_score}</text>
      <text x="{cx}" y="{cy - 6}" text-anchor="middle"
            font-family="JetBrains Mono, monospace" font-size="11"
            letter-spacing="1.5" fill="#94A3B8">RISK SCORE</text>
    </svg>
    """
    return svg


def metric_tile(label: str, value: str, tone: str = "") -> str:
    """tone: '' | 'accent' | 'good' | 'bad'"""
    return f"""
    <div class="fs-metric">
      <div class="fs-metric-label">{label}</div>
      <div class="fs-metric-value {tone}">{value}</div>
    </div>
    """


def persona_banner(level: str, name: str, desc: str) -> str:
    mapping = {
        "low": ("#2DD4BF", "🟢"),
        "medium": ("#F5A524", "🟡"),
        "high": ("#FB7185", "🔴"),
    }
    color, icon = mapping[level]
    return f"""
    <div class="fs-persona" style="background:rgba(255,255,255,0.02); border-left:3px solid {color};">
      <div class="fs-persona-icon">{icon}</div>
      <div>
        <div class="fs-persona-title" style="color:{color};">{name}</div>
        <div class="fs-persona-desc">{desc}</div>
      </div>
    </div>
    """
