"""
Thème visuel du dashboard Traincker.

Esthétique "Liquid Glass" sur fond sombre : cartes translucides à effet de
flou (glassmorphism), halos de couleur doux façon lueur ambiante, typographie
Inter — minimaliste et épuré, inspiré du langage visuel d'Apple en dark mode.
"""

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

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

html, body, [data-testid="stAppViewContainer"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--tk-text);
    background: linear-gradient(160deg, var(--tk-bg-1) 0%, var(--tk-bg-2) 100%);
}

[data-testid="stHeader"] {
    background: transparent;
}

/* Halos de couleur flous en arrière-plan (lueur ambiante sur fond sombre) */
.tk-blob {
    position: fixed;
    border-radius: 50%;
    filter: blur(100px);
    opacity: 0.35;
    z-index: 0;
    pointer-events: none;
    mix-blend-mode: screen;
}
.tk-blob-1 {
    width: 460px; height: 460px;
    background: #3b6fe0;
    top: -140px; left: -110px;
    animation: tk-float-1 22s ease-in-out infinite;
}
.tk-blob-2 {
    width: 420px; height: 420px;
    background: #1fa679;
    bottom: -160px; right: -90px;
    animation: tk-float-2 26s ease-in-out infinite;
}
@keyframes tk-float-1 {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(40px, 30px); }
}
@keyframes tk-float-2 {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(-30px, -40px); }
}

@media (prefers-reduced-motion: reduce) {
    .tk-blob-1, .tk-blob-2 { animation: none; }
}

h1, h2, h3 {
    font-weight: 700 !important;
    letter-spacing: -0.02em;
    color: var(--tk-text);
}

p, span, label, div {
    color: var(--tk-text);
}

/* Cartes en verre : conteneurs créés avec st.container(border=True, key=...) */
div[class*="st-key-card_"] {
    background: var(--tk-glass) !important;
    backdrop-filter: blur(20px) saturate(160%);
    -webkit-backdrop-filter: blur(20px) saturate(160%);
    border: 1px solid var(--tk-glass-border) !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255,255,255,0.04);
    padding: 1.2rem 1.4rem !important;
}

/* Onglets en pilule */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--tk-glass);
    backdrop-filter: blur(14px);
    border-radius: 999px;
    padding: 6px;
    border: 1px solid var(--tk-glass-border);
    width: fit-content;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 999px !important;
    font-weight: 600;
    color: var(--tk-text-muted) !important;
}
.stTabs [aria-selected="true"] {
    background: var(--tk-accent) !important;
    color: #0a0d12 !important;
}

/* Boutons */
.stButton > button {
    border-radius: 999px !important;
    border: 1px solid var(--tk-glass-border) !important;
    background: rgba(255, 255, 255, 0.06) !important;
    backdrop-filter: blur(10px);
    color: var(--tk-text) !important;
    font-weight: 600;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    border-color: var(--tk-accent) !important;
    color: var(--tk-accent) !important;
    transform: translateY(-1px);
}
.stButton > button[kind="primary"] {
    background: var(--tk-accent) !important;
    color: #0a0d12 !important;
    border: none !important;
}

/* Champs de saisie / select */
.stTextInput input, .stSelectbox > div > div {
    border-radius: 14px !important;
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid var(--tk-glass-border) !important;
    color: var(--tk-text) !important;
}

.block-container {
    padding-top: 2rem;
    z-index: 1;
    position: relative;
}

.tk-logo-wrap {
    text-align: center;
    margin-bottom: 0.3rem;
}
.tk-caption {
    text-align: center;
    color: var(--tk-text-muted) !important;
    margin-bottom: 1.5rem;
}
</style>

<div class="tk-blob tk-blob-1"></div>
<div class="tk-blob tk-blob-2"></div>
"""
