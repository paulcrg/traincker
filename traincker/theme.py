"""
Thème visuel du dashboard Traincker.

Esthétique "Liquid Glass" : cartes translucides à effet de flou (glassmorphism),
halos de couleur doux en arrière-plan, typographie Inter — inspiré du langage
visuel minimaliste d'Apple, appliqué à un dashboard type SaaS.
"""

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --tk-bg-1: #eef3fb;
    --tk-bg-2: #dfe9fa;
    --tk-glass: rgba(255, 255, 255, 0.55);
    --tk-glass-border: rgba(255, 255, 255, 0.65);
    --tk-accent: #2d6cdf;
    --tk-positive: #2fbf8f;
    --tk-text: #1b2430;
    --tk-text-muted: #5b6673;
}

html, body, [data-testid="stAppViewContainer"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--tk-text);
    background: linear-gradient(160deg, var(--tk-bg-1) 0%, var(--tk-bg-2) 100%);
}

[data-testid="stHeader"] {
    background: transparent;
}

/* Halos de couleur flous en arrière-plan (signature "liquid glass") */
.tk-blob {
    position: fixed;
    border-radius: 50%;
    filter: blur(90px);
    opacity: 0.4;
    z-index: 0;
    pointer-events: none;
}
.tk-blob-1 {
    width: 420px; height: 420px;
    background: #7db8ff;
    top: -120px; left: -100px;
    animation: tk-float-1 22s ease-in-out infinite;
}
.tk-blob-2 {
    width: 380px; height: 380px;
    background: #9be8c9;
    bottom: -140px; right: -80px;
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

h1 {
    font-weight: 800 !important;
    letter-spacing: -0.03em;
    font-size: 2.3rem !important;
}
h2, h3 {
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}

/* Cartes en verre : conteneurs créés avec st.container(border=True, key=...) */
div[class*="st-key-card_"] {
    background: var(--tk-glass) !important;
    backdrop-filter: blur(18px) saturate(160%);
    -webkit-backdrop-filter: blur(18px) saturate(160%);
    border: 1px solid var(--tk-glass-border) !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 32px rgba(27, 36, 48, 0.08);
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
    color: var(--tk-text-muted);
}
.stTabs [aria-selected="true"] {
    background: var(--tk-accent) !important;
    color: white !important;
}

/* Boutons */
.stButton > button {
    border-radius: 999px !important;
    border: 1px solid var(--tk-glass-border) !important;
    background: rgba(255, 255, 255, 0.6) !important;
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
    color: white !important;
    border: none !important;
}

/* Champs de saisie / select */
.stTextInput input, .stSelectbox > div > div {
    border-radius: 14px !important;
    background: rgba(255, 255, 255, 0.65) !important;
    border: 1px solid var(--tk-glass-border) !important;
}

.block-container {
    padding-top: 2.5rem;
    z-index: 1;
    position: relative;
}
</style>

<div class="tk-blob tk-blob-1"></div>
<div class="tk-blob tk-blob-2"></div>
"""
