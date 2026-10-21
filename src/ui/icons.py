"""
Custom SVG Icon System for Automata Lab.
Provides crisp, consistent vector icons with standard stroke widths and alignment.
Replaces emoji throughout the interface with professional developer-tool icons.
"""

from typing import Dict, Optional
import html


# Dictionary of pure SVG paths (24x24 viewBox, stroke-based)
SVG_PATHS: Dict[str, str] = {
    "logo": """
        <circle cx="6" cy="12" r="3.5" fill="none" stroke="currentColor" stroke-width="1.8"/>
        <circle cx="18" cy="7" r="3.5" fill="none" stroke="currentColor" stroke-width="1.8"/>
        <circle cx="18" cy="17" r="3.5" fill="none" stroke="currentColor" stroke-width="1.8"/>
        <path d="M9.5 11L14.5 8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M9.5 13L14.5 16" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <circle cx="6" cy="12" r="1.5" fill="currentColor"/>
    """,
    "overview": """
        <rect width="7" height="9" x="3" y="3" rx="1.5" stroke="currentColor" stroke-width="1.8" fill="none"/>
        <rect width="7" height="5" x="14" y="3" rx="1.5" stroke="currentColor" stroke-width="1.8" fill="none"/>
        <rect width="7" height="9" x="14" y="12" rx="1.5" stroke="currentColor" stroke-width="1.8" fill="none"/>
        <rect width="7" height="5" x="3" y="16" rx="1.5" stroke="currentColor" stroke-width="1.8" fill="none"/>
    """,
    "conversion": """
        <path d="M16 3h5v5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        <path d="M4 20L21 3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" fill="none"/>
        <path d="M21 16v5h-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        <path d="M15 15l6 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" fill="none"/>
        <path d="M4 4l5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" fill="none"/>
    """,
    "machine": """
        <circle cx="7" cy="12" r="4" stroke="currentColor" stroke-width="1.8" fill="none"/>
        <circle cx="17" cy="12" r="4" stroke="currentColor" stroke-width="1.8" fill="none"/>
        <path d="M11 12h2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M2 12h1" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
    """,
    "transition": """
        <path d="M4 12h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" fill="none"/>
        <path d="M14 8l4 4-4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        <circle cx="4" cy="12" r="1.5" fill="currentColor"/>
    """,
    "input": """
        <path d="M4 12h12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" fill="none"/>
        <path d="M12 8l4 4-4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        <rect x="18" y="5" width="2" height="14" rx="1" fill="currentColor"/>
    """,
    "output": """
        <rect x="4" y="5" width="2" height="14" rx="1" fill="currentColor"/>
        <path d="M8 12h12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" fill="none"/>
        <path d="M16 8l4 4-4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    """,
    "simulation": """
        <polygon points="5 3 19 12 5 21 5 3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
        <circle cx="19" cy="12" r="2" fill="currentColor"/>
    """,
    "validation": """
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    """,
    "documentation": """
        <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M6 6h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M6 10h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M6 14h6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
    """,
    "settings": """
        <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" fill="none" stroke="currentColor" stroke-width="1.8"/>
    """,
    "reset": """
        <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M3 3v5h5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    """,
    "download": """
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline points="7 10 12 15 17 10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="12" y1="15" x2="12" y2="3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
    """,
    "play": """
        <polygon points="5 3 19 12 5 21 5 3" fill="currentColor"/>
    """,
    "pause": """
        <rect x="6" y="4" width="4" height="16" rx="1" fill="currentColor"/>
        <rect x="14" y="4" width="4" height="16" rx="1" fill="currentColor"/>
    """,
    "step_forward": """
        <polygon points="5 4 15 12 5 20 5 4" fill="currentColor"/>
        <line x1="19" y1="5" x2="19" y2="19" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
    """,
    "step_backward": """
        <polygon points="19 20 9 12 19 4 19 20" fill="currentColor"/>
        <line x1="5" y1="19" x2="5" y2="5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
    """,
    "restart": """
        <path d="M1 4v6h6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    """,
    "success": """
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.8" fill="none"/>
        <path d="m9 12 2 2 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    """,
    "warning": """
        <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="12" y1="9" x2="12" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="12" y1="17" x2="12.01" y2="17" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
    """,
    "error": """
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.8" fill="none"/>
        <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    """,
    "expand": """
        <polyline points="15 3 21 3 21 9" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline points="9 21 3 21 3 15" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="21" y1="3" x2="14" y2="10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <line x1="3" y1="21" x2="10" y2="14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
    """,
    "collapse": """
        <polyline points="4 14 10 14 10 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline points="20 10 14 10 14 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="14" y1="10" x2="21" y2="3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <line x1="3" y1="21" x2="10" y2="14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
    """,
    "arrow_right": """
        <line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <polyline points="12 5 19 12 12 19" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    """,
    "check": """
        <polyline points="20 6 9 17 4 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    """,
    "sparkles": """
        <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    """,
    "cpu": """
        <rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" stroke-width="1.8" fill="none"/>
        <rect x="9" y="9" width="6" height="6" stroke="currentColor" stroke-width="1.8" fill="none"/>
        <path d="M15 2v2M9 2v2M15 20v2M9 20v2M2 15h2M2 9h2M20 15h2M20 9h2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
    """,
    "code": """
        <polyline points="16 18 22 12 16 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline points="8 6 2 12 8 18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    """,
    "info": """
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.8" fill="none"/>
        <line x1="12" y1="16" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="12" y1="8" x2="12.01" y2="8" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
    """,
    "split": """
        <path d="M6 3v12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <circle cx="6" cy="18" r="3" stroke="currentColor" stroke-width="1.8" fill="none"/>
        <circle cx="6" cy="6" r="3" stroke="currentColor" stroke-width="1.8" fill="none"/>
        <path d="M18 9a9 9 0 0 1-9 9" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round"/>
        <circle cx="18" cy="9" r="3" stroke="currentColor" stroke-width="1.8" fill="none"/>
    """
}


def get_svg_icon(
    name: str,
    size: int = 18,
    color: Optional[str] = None,
    extra_class: str = ""
) -> str:
    """
    Renders an inline SVG string for the specified icon name.
    Safely sanitizes parameters to prevent injection.
    """
    path_markup = SVG_PATHS.get(name, SVG_PATHS["info"])
    clean_path = " ".join(path_markup.split())
    style_attr = f'style="vertical-align: middle; display: inline-block; color: {html.escape(color)};"' if color else 'style="vertical-align: middle; display: inline-block;"'
    class_attr = f'class="automata-icon {html.escape(extra_class)}"' if extra_class else 'class="automata-icon"'
    
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(size)}" height="{int(size)}" viewBox="0 0 24 24" {class_attr} {style_attr}>{clean_path}</svg>'
