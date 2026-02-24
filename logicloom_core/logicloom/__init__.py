"""LogicLoom: boolean logic minimization (prime implicants, Petrick)."""

from __future__ import annotations

__app_name__ = "LogicLoom"
__version__ = "0.1.0"
__version_info__ = (0, 1, 0)
__author__ = "Mojtaba Akhbari"
__email__ = "mojtabaakhbari.cs@gmail.com"
__github__ = "https://github.com/mojtabaakhbari"
__license__ = "MIT"
__status__ = "Development"

from .types import PIChartData, PIChartRow, Term
from .simplifier import LogicGateSimplifier

__all__ = [
    "LogicGateSimplifier",
    "Term",
    "PIChartRow",
    "PIChartData",
    "__app_name__",
    "__version__",
    "__version_info__",
    "__author__",
    "__email__",
    "__github__",
    "__license__",
    "__status__",
]
