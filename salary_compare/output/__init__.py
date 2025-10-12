"""Output formatters for salary calculations."""

from .console import ConsoleOutput
from .csv import CSVOutput
from .html import HTMLOutput

__all__ = ["ConsoleOutput", "HTMLOutput", "CSVOutput"]
