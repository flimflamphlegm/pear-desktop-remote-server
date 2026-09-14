"""HTML template rendering."""

from pathlib import Path

import config

_TEMPLATE_PATH = Path(__file__).with_name("index.html")

_PLACEHOLDERS = {
    "{{BACKGROUND_COLOR}}": config.BACKGROUND_COLOR,
    "{{CARD_BACKGROUND}}": config.CARD_BACKGROUND,
    "{{CARD_MAX_WIDTH}}": config.CARD_MAX_WIDTH,
    "{{ARTWORK_MAX_HEIGHT}}": config.ARTWORK_MAX_HEIGHT,
    "{{TRACK_BAR_HEIGHT}}": config.TRACK_BAR_HEIGHT,
    "{{BUTTON_MIN_HEIGHT}}": config.BUTTON_MIN_HEIGHT,
    "{{ACCENT_COLOR}}": config.ACCENT_COLOR,
    "{{POLL_INTERVAL_MS}}": str(config.POLL_INTERVAL_MS),
}


def render_index_html() -> str:
    html = _TEMPLATE_PATH.read_text(encoding="utf-8")
    for placeholder, value in _PLACEHOLDERS.items():
        html = html.replace(placeholder, value)
    return html
