"""Pytest configuration and fixtures."""

from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from salary_compare.services.currency import CurrencyConverter


@pytest.fixture(autouse=True)
def mock_currency_converter():
    """Mock currency converter with fixed EUR to CZK rate of 25.0."""
    mock_converter = Mock(spec=CurrencyConverter)
    mock_converter.get_eur_to_czk_rate.return_value = Decimal("25.0")
    mock_converter.convert_czk_to_eur.side_effect = lambda czk: czk / Decimal("25.0")
    mock_converter.convert_eur_to_czk.side_effect = lambda eur: eur * Decimal("25.0")

    with patch(
        "salary_compare.services.currency.get_currency_converter", return_value=mock_converter
    ):
        yield mock_converter
