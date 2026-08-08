"""
Thème visuel du dashboard Traincker.

Esthétique "Liquid Glass" sur fond sombre : cartes translucides à effet de
flou (glassmorphism), halos de couleur doux façon lueur ambiante, typographie
Inter — minimaliste et épuré, inspiré du langage visuel d'Apple en dark mode.
"""

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@700&display=swap');

:root {
    --tk-bg-1: #0a0d12;
    --tk-bg-2: #161b23;
    --tk-glass: rgba(255, 255, 255, 0.05);
    --tk-glass-border: rgba(255, 255, 255, 0.10);
    --tk-accent: #5b8def;
    --tk-positive: #34d1a0;
    --tk-text: #e7ebf1;
    --tk-text-muted: #8a94a6;
}

html, body {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

html, body, [data-testid="stAppViewContainer"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--tk-text);
    background: linear-gradient(160deg, var(--tk-bg-1) 0%, var(--tk-bg-2) 100%);
}

[data-testid="stHeader"] { background: transparent; }

.tk-blob {
    position: fixed;
    border-radius: 50%;
    filter: blur(100px);
    opacity: 0.35;
    z-index: 0;
    pointer-events: none;
    mix-blend-mode: screen;
}
.tk-blob-1 { width: 460px; height: 460px; background: #3b6fe0; top: -140px; left: -110px; animation: tk-float-1 22s ease-in-out infinite; }
.tk-blob-2 { width: 420px; height: 420px; background: #1fa679; bottom: -160px; right: -90px; animation: tk-float-2 26s ease-in-out infinite; }
@keyframes tk-float-1 { 0%, 100% { transform: translate(0, 0); } 50% { transform: translate(40px, 30px); } }
@keyframes tk-float-2 { 0%, 100% { transform: translate(0, 0); } 50% { transform: translate(-30px, -40px); } }
@media (prefers-reduced-motion: reduce) { .tk-blob-1, .tk-blob-2 { animation: none; } }

h1, h2, h3 { font-weight: 700 !important; letter-spacing: -0.02em; color: var(--tk-text); }
p, span, label, div { color: var(--tk-text); }

.tk-logo-wrap { text-align: center; margin-bottom: 0.3rem; }
.tk-caption { text-align: center; color: var(--tk-text-muted) !important; margin-bottom: 1.6rem; }

div[class*="st-key-card_"] {
    background: var(--tk-glass) !important;
    backdrop-filter: blur(20px) saturate(160%);
    -webkit-backdrop-filter: blur(20px) saturate(160%);
    border: 1px solid var(--tk-glass-border) !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255,255,255,0.04);
    padding: 1.5rem 1.7rem !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
div[class*="st-key-card_"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255,255,255,0.05);
}

.stTabs [data-baseweb="tab-list"] {
    position: relative;
    gap: 2px;
    background: var(--tk-glass);
    backdrop-filter: blur(14px);
    border-radius: 999px;
    padding: 8px;
    border: 1px solid var(--tk-glass-border);
    width: fit-content;
    margin: 0 auto 2rem auto;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.25);
}
.stTabs [data-baseweb="tab"] {
    position: relative;
    z-index: 1;
    border-radius: 999px !important;
    font-weight: 600;
    font-size: 0.95rem;
    padding: 10px 24px !important;
    color: var(--tk-text-muted) !important;
    transition: color 0.3s ease;
}
.stTabs [aria-selected="true"] { color: var(--tk-accent) !important; }
.tk-slider-ready [aria-selected="true"] { color: #0a0d12 !important; }
.tk-tab-slider {
    position: absolute;
    top: 8px; bottom: 8px; left: 8px;
    background: var(--tk-accent);
    border-radius: 999px;
    box-shadow: 0 2px 10px rgba(91, 141, 239, 0.35);
    transition: left 0.35s cubic-bezier(0.4, 0, 0.2, 1), width 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 0;
    pointer-events: none;
}

.stButton > button {
    border-radius: 999px !important;
    border: 1px solid var(--tk-glass-border) !important;
    background: rgba(255, 255, 255, 0.06) !important;
    backdrop-filter: blur(10px);
    color: var(--tk-text) !important;
    font-weight: 600;
    transition: all 0.2s ease;
}
.stButton > button:hover { border-color: var(--tk-accent) !important; color: var(--tk-accent) !important; transform: translateY(-1px); }
.stButton > button[kind="primary"] { background: var(--tk-accent) !important; color: #0a0d12 !important; border: none !important; }

.stTextInput input, .stSelectbox > div > div {
    border-radius: 14px !important;
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid var(--tk-glass-border) !important;
    color: var(--tk-text) !important;
}

.block-container { padding-top: 2.5rem; z-index: 1; position: relative; animation: tk-fade-in 0.5s ease; }
@keyframes tk-fade-in { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

.tk-banner-alert {
    background: linear-gradient(90deg, rgba(239,91,91,0.18), rgba(239,91,91,0.06));
    border: 1px solid rgba(239,91,91,0.35);
    border-radius: 14px;
    padding: 0.7rem 1rem;
    margin-bottom: 1.2rem;
    font-weight: 600;
    color: var(--tk-text);
}

.tk-banner-degrade {
    background: linear-gradient(90deg, rgba(226,147,60,0.18), rgba(226,147,60,0.06));
    border: 1px solid rgba(226,147,60,0.35);
    border-radius: 14px;
    padding: 0.7rem 1rem;
    margin-bottom: 1rem;
    font-weight: 600;
    color: var(--tk-text);
}

.tk-next-train { display: flex; align-items: baseline; gap: 10px; margin: 0.3rem 0 0.6rem 0; }
.tk-next-train-time { font-size: 1.7rem; font-weight: 800; color: var(--tk-text); letter-spacing: -0.02em; }
.tk-next-train-countdown { font-size: 0.95rem; font-weight: 600; color: var(--tk-accent); background: rgba(91, 141, 239, 0.12); padding: 2px 10px; border-radius: 999px; }

div[data-testid="column"] { padding: 2px 4px; }
.stButton > button { margin-top: 2px; }

.tk-history-label { font-size: 0.78rem; color: var(--tk-text-muted); margin: 0.4rem 0 0.3rem 0; }

.tk-footer {
    display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 10px;
    text-align: center; color: var(--tk-text-muted); font-size: 0.85rem; font-weight: 500;
    letter-spacing: 0.01em; margin-top: 3rem; padding: 1.5rem 0 1rem 0;
    border-top: 1px solid var(--tk-glass-border);
}
.tk-footer-sep { color: var(--tk-glass-border); }
.tk-footer-link { color: var(--tk-text-muted); font-weight: 600; }

.tk-section-title { display: flex; align-items: center; gap: 8px; font-size: 1.15rem; font-weight: 700; color: var(--tk-text); margin: 0.2rem 0 0.8rem 0; }

div[class*="st-key-suggest_box"] {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--tk-glass-border);
    border-radius: 12px;
    overflow: hidden;
    margin: -4px 0 12px 0;
    padding: 4px 0;
}
div[class*="st-key-suggest_box"] .stButton > button {
    width: 100%; text-align: left; justify-content: flex-start;
    border-radius: 0 !important; border: none !important; background: transparent !important;
    font-weight: 500; padding: 0.55rem 0.9rem; margin: 0 !important;
}
div[class*="st-key-suggest_box"] .stButton > button:hover { background: rgba(91, 141, 239, 0.14) !important; color: var(--tk-accent) !important; transform: none; }

.tk-divider { border-bottom: 1px solid var(--tk-glass-border); margin: 0.6rem 0; }
.tk-compact-btn button { padding: 0.3rem 0.6rem !important; font-size: 0.85rem !important; }

.tk-insight {
    background: rgba(91, 141, 239, 0.08);
    border: 1px solid rgba(91, 141, 239, 0.25);
    border-radius: 12px;
    padding: 0.8rem 1.1rem;
    margin-bottom: 1rem;
    font-size: 0.95rem;
    line-height: 1.6;
    color: var(--tk-text);
}

.tk-legend { font-size: 0.78rem; color: var(--tk-text-muted); margin-top: 0.5rem; }
.tk-confirm-text { font-size: 0.9rem; color: #ef5b5b; font-weight: 600; margin-bottom: 0.5rem; }
.tk-hint { font-size: 0.85rem; color: var(--tk-text-muted); margin: -0.4rem 0 1rem 0; }

.tk-log-line {
    font-family: 'Courier New', monospace;
    font-size: 0.78rem;
    color: var(--tk-text-muted);
    padding: 2px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

/* Chips de statistiques rapides (KPI en haut du dashboard) */
.tk-chip-row {
    display: flex;
    gap: 12px;
    margin-bottom: 1.4rem;
}
.tk-chip {
    flex: 1;
    background: var(--tk-glass);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--tk-glass-border);
    border-radius: 16px;
    padding: 0.7rem 1rem;
    text-align: center;
    transition: transform 0.2s ease;
}
.tk-chip:hover { transform: translateY(-2px); }
.tk-chip-label {
    display: block;
    font-size: 0.72rem;
    color: var(--tk-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 2px;
}
.tk-chip-value {
    display: block;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--tk-text);
}

/* Points de statut pulsants (perturbation / RAS) */
.tk-dot {
    display: inline-block;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    margin-right: 8px;
    position: relative;
    top: -1px;
}
.tk-dot-ok { background: var(--tk-positive); animation: tk-pulse-ok 2s infinite; }
.tk-dot-alert { background: #ef5b5b; animation: tk-pulse-alert 1.4s infinite; }
@keyframes tk-pulse-ok {
    0% { box-shadow: 0 0 0 0 rgba(52, 209, 160, 0.5); }
    70% { box-shadow: 0 0 0 8px rgba(52, 209, 160, 0); }
    100% { box-shadow: 0 0 0 0 rgba(52, 209, 160, 0); }
}
@keyframes tk-pulse-alert {
    0% { box-shadow: 0 0 0 0 rgba(239, 91, 91, 0.5); }
    70% { box-shadow: 0 0 0 8px rgba(239, 91, 91, 0); }
    100% { box-shadow: 0 0 0 0 rgba(239, 91, 91, 0); }
}
.tk-status-line { font-weight: 600; margin: 0.4rem 0 0.8rem 0; }
</style>

<div class="tk-blob tk-blob-1"></div>
<div class="tk-blob tk-blob-2"></div>
"""

TAB_SLIDER_JS = """
<script>
(function() {
    function setupTabSlider() {
        const tabList = document.querySelector('.stTabs [data-baseweb="tab-list"]');
        if (!tabList) return;
        let slider = tabList.querySelector('.tk-tab-slider');
        if (!slider) {
            slider = document.createElement('div');
            slider.className = 'tk-tab-slider';
            tabList.insertBefore(slider, tabList.firstChild);
        }

        function moveSlider() {
            const active = tabList.querySelector('[aria-selected="true"]');
            if (!active) return;
            const tabRect = active.getBoundingClientRect();
            const listRect = tabList.getBoundingClientRect();
            slider.style.width = tabRect.width + 'px';
            slider.style.left = (tabRect.left - listRect.left) + 'px';
            tabList.classList.add('tk-slider-ready');
        }

        tabList.querySelectorAll('[data-baseweb="tab"]').forEach(function(tab) {
            if (tab.dataset.tkBound) return;
            tab.dataset.tkBound = "1";
            tab.addEventListener('click', function() { setTimeout(moveSlider, 10); });
        });

        moveSlider();
    }

    setTimeout(setupTabSlider, 150);
    setInterval(setupTabSlider, 800);
    window.addEventListener('resize', setupTabSlider);
})();
</script>
"""


def css_accessibilite(contraste_eleve: bool, taille_police: str) -> str:
    """
    Génère un bloc CSS additionnel (à injecter après THEME_CSS) pour
    l'accessibilité : taille de police ajustable et mode contraste élevé.
    """
    facteur = {"normale": "1", "grande": "1.15", "tres_grande": "1.3"}.get(taille_police, "1")

    css = f"<style>\nhtml {{ font-size: calc(16px * {facteur}); }}\n"

    if contraste_eleve:
        css += """
:root {
    --tk-bg-1: #000000 !important;
    --tk-bg-2: #0a0a0a !important;
    --tk-glass: rgba(255,255,255,0.14) !important;
    --tk-glass-border: rgba(255,255,255,0.5) !important;
    --tk-text: #ffffff !important;
    --tk-text-muted: #e0e0e0 !important;
    --tk-accent: #8ab4ff !important;
}
.tk-blob { display: none !important; }
"""

    css += "</style>"
    return css


CSS_THEME_CLAIR = """
<style>
:root {
    --tk-bg-1: #f5f7fb !important;
    --tk-bg-2: #e9eef8 !important;
    --tk-glass: rgba(255, 255, 255, 0.78) !important;
    --tk-glass-border: rgba(20, 30, 50, 0.12) !important;
    --tk-accent: #2d6cdf !important;
    --tk-positive: #189968 !important;
    --tk-text: #141c28 !important;
    --tk-text-muted: #56606f !important;
}
.tk-blob { opacity: 0.16 !important; }
[data-testid="stHeader"] { background: transparent !important; }
div[class*="st-key-card_"] {
    box-shadow: 0 10px 30px rgba(20, 30, 50, 0.10) !important;
    border: 1px solid rgba(20, 30, 50, 0.08) !important;
}
.tk-slider-ready [aria-selected="true"] { color: #ffffff !important; }
.tk-chip {
    background: rgba(255, 255, 255, 0.85) !important;
    box-shadow: 0 2px 10px rgba(20, 30, 50, 0.06) !important;
}
.tk-logo-wrap {
    background: radial-gradient(ellipse at center, rgba(45,108,223,0.10) 0%, rgba(45,108,223,0) 72%);
    display: inline-block;
    padding: 14px 30px;
    border-radius: 20px;
}
</style>
"""
