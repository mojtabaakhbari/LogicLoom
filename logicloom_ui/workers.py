"""Background worker for running LogicGateSimplifier.simplify()."""

from PyQt6.QtCore import QThread, pyqtSignal

from .logicloom_client import LogicGateSimplifier


class ComputeWorker(QThread):
    """QThread that builds a LogicGateSimplifier from strings and runs simplify(); emits result or error."""

    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, variables_str: str, minterms_str: str):
        """Store comma-separated variable and minterm strings for the worker."""
        super().__init__()
        self.variables_str = variables_str
        self.minterms_str = minterms_str

    def run(self) -> None:
        """Create simplifier, call simplify(), and emit finished(simplifier) or error(message)."""
        try:
            simplifier = LogicGateSimplifier.from_strings(
                self.variables_str, self.minterms_str
            )
            simplifier.simplify()
            self.finished.emit(simplifier)
        except Exception as exc:
            self.error.emit(str(exc))
