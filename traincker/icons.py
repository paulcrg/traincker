"""
Icônes SVG minimalistes faites maison, pour remplacer les emojis dans le
dashboard. Traits fins (line icons), monochromes, héritent de la couleur du
texte via currentColor.
"""

_ICONES = {
    "search": '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/>',
    "alert": (
        '<path d="M12 3 L22 20 L2 20 Z"/>'
        '<line x1="12" y1="9" x2="12" y2="14"/>'
        '<circle cx="12" cy="17.2" r="0.6" fill="currentColor" stroke="none"/>'
    ),
    "clock": '<circle cx="12" cy="12" r="9"/><line x1="12" y1="12" x2="12" y2="7"/><line x1="12" y1="12" x2="16" y2="14"/>',
    "star": '<path d="M12 2 L15 9 L22 9.5 L17 14.5 L18.5 21 L12 17.5 L5.5 21 L7 14.5 L2 9.5 L9 9 Z"/>',
    "chart": '<line x1="6" y1="20" x2="6" y2="12"/><line x1="12" y1="20" x2="12" y2="7"/><line x1="18" y1="20" x2="18" y2="3"/>',
    "pin": '<path d="M12 21C12 21 19 14.5 19 9.5C19 5.9 15.9 3 12 3C8.1 3 5 5.9 5 9.5C5 14.5 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.3"/>',
    "plus": '<line x1="12" y1="4" x2="12" y2="20"/><line x1="4" y1="12" x2="20" y2="12"/>',
    "download": '<line x1="12" y1="3" x2="12" y2="15"/><polyline points="6,11 12,17 18,11"/><line x1="4" y1="20" x2="20" y2="20"/>',
    "refresh": (
        '<path d="M4 12a8 8 0 0 1 14.5-4.7"/><polyline points="18,3 18.5,7.3 14,7"/>'
        '<path d="M20 12a8 8 0 0 1-14.5 4.7"/><polyline points="6,21 5.5,16.7 10,17"/>'
    ),
}


def icono(nombre: str, size: int = 16, color: str = "currentColor", stroke_width: float = 2) -> str:
    """Retourne le markup SVG inline d'une icône, prête à insérer via st.markdown."""
    interieur = _ICONES.get(nombre, "")
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" '
        f'stroke-linejoin="round" style="display:inline-block;vertical-align:middle;flex-shrink:0;">'
        f"{interieur}</svg>"
    )


def titre_section(nombre_icone: str, texte: str) -> str:
    """Titre de section stylé (remplace st.subheader avec une icône)."""
    return (
        f'<div class="tk-section-title">{icono(nombre_icone, size=18)}'
        f"<span>{texte}</span></div>"
    )
