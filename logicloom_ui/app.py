"""Application entry point for the LogicLoom GUI."""

import sys
from pathlib import Path

from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QApplication

from . import __app_name__, __version__
from .main_window import MainWindow

_ICON_PATH = Path(__file__).resolve().parent / "icon.ico"


def main() -> None:
    """Create and run the LogicLoom GUI application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(str(_ICON_PATH)))
    font = QFont("Outfit", 10)
    app.setFont(font)
    window = MainWindow()
    window.setWindowIcon(QIcon(str(_ICON_PATH)))
    window.show()
    sys.exit(app.exec())


def _parse_args() -> bool:
    """Parse command-line arguments; return True if version was printed and app should exit."""
    import argparse

    parser = argparse.ArgumentParser(prog=__app_name__)
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()
    if args.version:
        print(__version__)
        return True
    return False


if __name__ == "__main__":
    if not _parse_args():
        main()
