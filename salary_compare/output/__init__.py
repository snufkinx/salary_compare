"""Output formatters for salary calculations."""

from .console import ConsoleOutput
from .html import HTMLOutput
from .csv import CSVOutput

__all__ = ["ConsoleOutput", "HTMLOutput", "CSVOutput"]
