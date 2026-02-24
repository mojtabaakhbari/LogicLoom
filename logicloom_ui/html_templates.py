"""HTML templates for equation and LaTeX result views."""

from __future__ import annotations


def empty_html(placeholder: str) -> str:
    """Return a minimal dark-themed HTML page with the given placeholder text."""
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="background:#1a2332;color:#8b9cb8;font-size:14px;padding:16px;margin:0;">
    <p style="margin:0;">{placeholder}</p>
    </body>
    </html>
    """


def render_equations_html(equations: list[dict[str, str]]) -> str:
    """Return full HTML page with equation strings escaped and styled."""
    parts = []
    for eq in equations:
        text = (
            eq["string"]
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        parts.append(
            "<p style=\"margin:0 0 6px 0;font-size:18px;"
            "font-family:'JetBrains Mono',Consolas,monospace;\">"
            f"{text}</p>"
        )
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="background:#1a2332;color:#e6edf3;font-size:18px;padding:6px 12px;margin:0;">
    {"".join(parts)}
    </body>
    </html>
    """


def render_latex_html(equations: list[dict[str, str]]) -> str:
    """Return full HTML page with LaTeX equations rendered via MathJax (js/tex-mml-chtml.js)."""
    latex_parts = [f'<p>$${eq["latex"]}$$</p>' for eq in equations]
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <!-- Loaded from repo root js/; base URL set in MainWindow so js/tex-mml-chtml.js resolves -->
    <script src="js/tex-mml-chtml.js"></script>
    </head>
    <body style="background:#1a2332;color:#e6edf3;font-size:16px;padding:12px;margin:0;">
    {"".join(latex_parts)}
    </body>
    </html>
    """
