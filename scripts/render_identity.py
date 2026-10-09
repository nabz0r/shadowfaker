#!/usr/bin/env python3
"""Self-contained fan-made vector identity for README and documentation."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIGURES=ROOT/"docs"/"figures"

def poster(language: str) -> str:
    lead="DÉCODER FAKER." if language=="fr" else "DECODE FAKER."
    second="INVENTER L'APRÈS." if language=="fr" else "IMAGINE WHAT'S NEXT."
    note="LABORATOIRE INDÉPENDANT · 465 PARTIES · 12 510 TRANSITIONS" if language=="fr" else "INDEPENDENT RESEARCH LAB · 465 GAMES · 12,510 TRANSITIONS"
    caveat="CONCEPT FAN-MADE · SANS AFFILIATION T1 / RIOT" if language=="fr" else "FAN-MADE CONCEPT · NO T1 / RIOT AFFILIATION"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="620" viewBox="0 0 1400 620" role="img" aria-label="Shadow Faker five star research edition poster">
<defs><linearGradient id="back" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#130d16"/><stop offset=".6" stop-color="#28121f"/><stop offset="1" stop-color="#100c13"/></linearGradient><linearGradient id="slash" x1="0" x2="1"><stop stop-color="#8d2341"/><stop offset=".6" stop-color="#ff4967"/><stop offset="1" stop-color="#6a1b35"/></linearGradient><linearGradient id="word" x1="0" x2="1"><stop stop-color="#fffaf4"/><stop offset=".65" stop-color="#ffc7cf"/><stop offset="1" stop-color="#ff6680"/></linearGradient><filter id="glow"><feGaussianBlur stdDeviation="32"/></filter></defs>
<rect width="1400" height="620" fill="url(#back)"/><ellipse cx="1170" cy="155" rx="250" ry="180" fill="#e02f54" opacity=".16" filter="url(#glow)"/>
<g opacity=".22" stroke="#be4862" stroke-width="1">{''.join(f'<path d="M {i*62-220} 0 L {i*62+260} 620"/>' for i in range(29))}</g>
<path d="M 1080 0 H 1400 V 620 H 1235 Z" fill="url(#slash)" opacity=".75"/>
<text x="910" y="445" font-family="Arial Black,Arial,sans-serif" font-size="410" font-weight="900" font-style="italic" fill="#ff526d" opacity=".16">05</text>
<rect x="70" y="48" width="58" height="58" fill="#75243b" stroke="#ff6380" stroke-width="3"/><text x="80" y="88" font-family="Arial Black,Arial,sans-serif" font-size="28" font-weight="900" font-style="italic" fill="#fff8f5">SF</text>
<text x="150" y="85" font-family="Arial Black,Arial,sans-serif" font-size="24" font-weight="900" letter-spacing="5" fill="#fff4ee">SHADOW <tspan fill="#ff617b">FAKER</tspan></text>
<text x="72" y="164" font-family="Arial, sans-serif" font-size="24" letter-spacing="9" fill="#ffd895">★ ★ ★ ★ ★</text>
<text x="315" y="162" font-family="Arial,sans-serif" font-size="14" font-weight="700" letter-spacing="4" fill="#e8b9c3">FIVE STAR RESEARCH EDITION</text>
<path d="M 70 186 H 790" stroke="#a84a61" stroke-width="2"/>
<text x="68" y="290" font-family="Arial Black,Arial,sans-serif" font-size="71" font-weight="900" font-style="italic" letter-spacing="-4" fill="url(#word)">{lead}</text>
<text x="68" y="377" font-family="Arial Black,Arial,sans-serif" font-size="67" font-weight="900" font-style="italic" letter-spacing="-4" fill="url(#word)">{second}</text>
<rect x="70" y="427" width="650" height="4" fill="#ff526d"/><text x="71" y="479" font-family="Arial,sans-serif" font-size="19" font-weight="700" letter-spacing="2" fill="#f0d8df">{note}</text>
<text x="72" y="558" font-family="Arial,sans-serif" font-size="12" letter-spacing="2" fill="#c798a7">{caveat}</text>
</svg>'''

def main():
    FIGURES.mkdir(parents=True,exist_ok=True)
    for language in ("en","fr"):
        (FIGURES/f"readme_hero_{language}.svg").write_text(poster(language),encoding="utf-8")
    print("Rendered two fan-made five-star SVG posters")

if __name__=="__main__": main()
