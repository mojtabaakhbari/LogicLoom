"""Main window and UI for the LogicLoom Simplifier application."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

from .html_templates import empty_html, render_equations_html, render_latex_html
from .validation import validate_minterms, validate_variables
from .workers import ComputeWorker

_APP_ROOT = Path(__file__).resolve().parents[1]


class MainWindow(QMainWindow):
    """Main application window with input fields, tabs for results, and compute workflow."""

    def __init__(self) -> None:
        """Initialize window, UI, styles, signals, and status bar."""
        super().__init__()
        self.setWindowTitle("LogicLoom Simplifier")
        self.resize(1000, 720)
        self._worker = None
        self._simplifier = None
        self.setup_ui()
        self.apply_styles()
        self.connect_signals()
        self.statusBar().showMessage(
            "Ready. Enter variables and minterms, then press Compute."
        )

    def setup_ui(self) -> None:
        """Build the central widget, input card, tabs, and author credit."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)

        input_card = QFrame()
        input_card.setObjectName("inputCard")
        input_layout = QVBoxLayout(input_card)
        input_layout.setSpacing(12)

        input_layout.addWidget(QLabel("Variables (comma-separated)"))
        self.var_input = QLineEdit()
        self.var_input.setPlaceholderText("e.g. x, y, z")
        self.var_input.setClearButtonEnabled(True)
        input_layout.addWidget(self.var_input)
        self.var_error = QLabel()
        self.var_error.setObjectName("inputError")
        self.var_error.setWordWrap(True)
        self.var_error.hide()
        input_layout.addWidget(self.var_error)

        input_layout.addWidget(QLabel("Minterms (comma-separated)"))
        self.minterm_input = QLineEdit()
        self.minterm_input.setPlaceholderText("e.g. 0, 2, 4, 5, 6")
        self.minterm_input.setClearButtonEnabled(True)
        input_layout.addWidget(self.minterm_input)
        self.minterm_error = QLabel()
        self.minterm_error.setObjectName("inputError")
        self.minterm_error.setWordWrap(True)
        self.minterm_error.hide()
        input_layout.addWidget(self.minterm_error)

        self.compute_btn = QPushButton("Compute")
        self.compute_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        input_layout.addWidget(self.compute_btn)

        main_layout.addWidget(input_card)

        self.tabs = QTabWidget()

        self.pi_table = QTableWidget()
        self.tabs.addTab(self.pi_table, "Prime Implicants")

        self.essentials_table = QTableWidget()
        self.tabs.addTab(self.essentials_table, "Essentials")

        self.chart_table = QTableWidget()
        self.tabs.addTab(self.chart_table, "PI Chart")

        self.normal_form_view = QWebEngineView()
        self.normal_form_view.setHtml(
            empty_html("Results will appear here after Compute."),
            QUrl.fromLocalFile(str(_APP_ROOT) + "/"),
        )
        self.normal_form_scroll = QScrollArea()
        self.normal_form_scroll.setWidgetResizable(True)
        self.normal_form_scroll.setWidget(self.normal_form_view)
        self.tabs.addTab(self.normal_form_scroll, "Results")

        self.latex_view = QWebEngineView()
        self.latex_view.setHtml(
            empty_html("LaTeX results will appear here after Compute."),
            QUrl.fromLocalFile(str(_APP_ROOT) + "/"),
        )
        self.latex_scroll = QScrollArea()
        self.latex_scroll.setWidgetResizable(True)
        self.latex_scroll.setWidget(self.latex_view)
        self.tabs.addTab(self.latex_scroll, "LaTeX Results")

        main_layout.addWidget(self.tabs)

        author_label = QLabel(
            "Author: <b>Mojtaba Akhbari</b> · "
            '<a href="mailto:mojtabaakhbari.cs@gmail.com" style="color:#60a5fa;">Email</a>'
        )
        author_label.setOpenExternalLinks(True)
        author_label.setObjectName("authorCredit")
        main_layout.addWidget(author_label)

        self._validation_timer = QTimer(self)
        self._validation_timer.setSingleShot(True)
        self._validation_timer.timeout.connect(self._run_validation)

        self.statusBar().setStyleSheet("")

    def apply_styles(self) -> None:
        """Apply dark-theme stylesheet to the window and widgets."""
        self.setStyleSheet(
            """
            QMainWindow { background-color: #0f1419; }
            QWidget { background-color: transparent; color: #e6edf3; }
            QLabel { color: #8b9cb8; font-size: 13px; }
            #inputCard {
                background-color: #1a2332;
                border: 1px solid #2d3a4f;
                border-radius: 12px;
                padding: 16px;
            }
            QLineEdit {
                background-color: #243044;
                border: 1px solid #2d3a4f;
                border-radius: 8px;
                padding: 10px 12px;
                color: #e6edf3;
                font-size: 14px;
                font-family: "JetBrains Mono", "Consolas", monospace;
            }
            QLineEdit:focus { border-color: #3b82f6; }
            QLineEdit:disabled { color: #6b7a8e; }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover:!disabled { background-color: #60a5fa; }
            QPushButton:pressed:!disabled { background-color: #2563eb; }
            QPushButton:disabled { background-color: #2d3a4f; color: #6b7a8e; }
            QTabWidget::pane {
                background-color: #1a2332;
                border: 1px solid #2d3a4f;
                border-radius: 12px;
                margin-top: -1px;
            }
            QTabBar::tab {
                background-color: #243044;
                color: #8b9cb8;
                padding: 10px 20px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected { background-color: #1a2332; color: #e6edf3; }
            QTabBar::tab:hover:!selected { background-color: #2d3a4f; }
            QTableWidget {
                background-color: #1a2332;
                color: #e6edf3;
                gridline-color: #2d3a4f;
                border: none;
            }
            QTableWidget::item { padding: 8px; }
            QHeaderView::section {
                background-color: #243044;
                color: #8b9cb8;
                padding: 10px;
                border: none;
                font-weight: 600;
            }
            QScrollArea { background-color: #1a2332; border: none; }
            QStatusBar { background-color: #1a2332; color: #8b9cb8; }
            #authorCredit {
                color: #6b7a8e;
                font-size: 12px;
                padding: 8px 0 4px 0;
            }
            #authorCredit a { color: #60a5fa; text-decoration: none; }
            QLabel#inputError {
                color: #ef4444;
                font-size: 12px;
                padding: 4px 0 0 0;
            }
        """
        )

    def connect_signals(self) -> None:
        """Connect compute button and input change signals to slots."""
        self.compute_btn.clicked.connect(self.start_compute)
        self.var_input.textChanged.connect(self._on_input_changed)
        self.minterm_input.textChanged.connect(self._on_input_changed)

    def _on_input_changed(self) -> None:
        """Restart debounced validation timer when input text changes."""
        self._validation_timer.stop()
        self._validation_timer.start(500)

    def _run_validation(self) -> None:
        """Validate variables and minterms and show or hide error labels."""
        v_ok, v_err = validate_variables(self.var_input.text())
        m_ok, m_err = validate_minterms(self.minterm_input.text())
        if v_ok:
            self.var_error.hide()
            self.var_error.clear()
        else:
            self.var_error.setText(v_err or "")
            self.var_error.show()
        if m_ok:
            self.minterm_error.hide()
            self.minterm_error.clear()
        else:
            self.minterm_error.setText(m_err or "")
            self.minterm_error.show()

    def set_computing(self, computing: bool) -> None:
        """Enable or disable inputs and compute button; update status bar message."""
        self.var_input.setEnabled(not computing)
        self.minterm_input.setEnabled(not computing)
        self.compute_btn.setEnabled(not computing)
        if computing:
            self.statusBar().showMessage("Computing...")
        else:
            self.statusBar().showMessage("Ready.")

    def start_compute(self) -> None:
        """Validate inputs, start ComputeWorker, and run simplification in a background thread."""
        self._validation_timer.stop()
        self._run_validation()
        variables = self.var_input.text().strip()
        minterms = self.minterm_input.text().strip()
        if not variables or not minterms:
            self.statusBar().showMessage("Please enter both variables and minterms.")
            return
        v_ok, v_err = validate_variables(variables)
        m_ok, m_err = validate_minterms(minterms)
        if not v_ok:
            self.var_error.setText(v_err or "")
            self.var_error.show()
            self.statusBar().showMessage("Fix variables input.")
            return
        if not m_ok:
            self.minterm_error.setText(m_err or "")
            self.minterm_error.show()
            self.statusBar().showMessage("Fix minterms input.")
            return
        self.set_computing(True)
        self._worker = ComputeWorker(variables, minterms)
        self._worker.finished.connect(self.on_compute_finished)
        self._worker.error.connect(self.on_compute_error)
        self._worker.start()

    def on_compute_finished(self, simplifier) -> None:
        """Store simplifier result, clear worker, and populate result tabs."""
        self._simplifier = simplifier
        self._worker = None
        self.set_computing(False)
        self.statusBar().showMessage("Done.")
        self.fill_tabs()

    def on_compute_error(self, message: str) -> None:
        """Handle worker error: clear worker, re-enable UI, show error in status bar."""
        self._worker = None
        self.set_computing(False)
        self.statusBar().showMessage(f"Error: {message}")

    def fill_tabs(self) -> None:
        """Populate Prime Implicants, Essentials, PI Chart, Results, and LaTeX tabs from current simplifier."""
        if not self._simplifier:
            return
        simplifier = self._simplifier
        vars_list = simplifier.variables

        pis = sorted(simplifier.prime_implicants, key=lambda t: t.binary_form)
        self.pi_table.setRowCount(len(pis))
        self.pi_table.setColumnCount(2)
        self.pi_table.setHorizontalHeaderLabels(["Binary", "Literal"])
        for row, term in enumerate(pis):
            self.pi_table.setItem(row, 0, QTableWidgetItem(term.binary_form))
            self.pi_table.setItem(
                row, 1, QTableWidgetItem(term.to_normal_expression(vars_list))
            )
        self.pi_table.resizeColumnsToContents()

        self.essentials_table.setRowCount(len(simplifier.essentials))
        self.essentials_table.setColumnCount(2)
        self.essentials_table.setHorizontalHeaderLabels(["Binary", "Literal"])
        for row, term in enumerate(simplifier.essentials):
            self.essentials_table.setItem(row, 0, QTableWidgetItem(term.binary_form))
            self.essentials_table.setItem(
                row, 1, QTableWidgetItem(term.to_normal_expression(vars_list))
            )
        self.essentials_table.resizeColumnsToContents()

        pis_sorted = sorted(simplifier.prime_implicants, key=lambda t: t.binary_form)
        self.chart_table.setRowCount(len(simplifier.pichart))
        self.chart_table.setColumnCount(len(pis_sorted) + 1)
        self.chart_table.setHorizontalHeaderLabels(
            ["Minterm"] + [t.binary_form for t in pis_sorted]
        )
        for row_idx, chart_row in enumerate(simplifier.pichart):
            self.chart_table.setVerticalHeaderItem(
                row_idx, QTableWidgetItem(str(chart_row.minterm.number))
            )
            self.chart_table.setItem(
                row_idx, 0, QTableWidgetItem(chart_row.minterm.binary_form)
            )
            for col_idx, pi in enumerate(pis_sorted):
                cell = QTableWidgetItem("x" if pi in chart_row.prime_implicants else "")
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.chart_table.setItem(row_idx, col_idx + 1, cell)
        self.chart_table.resizeColumnsToContents()

        equations = simplifier.get_all_equations()
        self.normal_form_view.setHtml(render_equations_html(equations))

        latex_html = render_latex_html(equations)
        base_url = QUrl.fromLocalFile(str(_APP_ROOT) + "/")
        self.latex_view.setHtml(latex_html, base_url)
