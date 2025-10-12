"""Pytest configuration and fixtures."""

from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from salary_compare.services.currency import CurrencyConverter


@pytest.fixture(autouse=True)
def mock_currency_converter():
    """Mock currency converter with fixed rates: 1 EUR = 25 CZK, 1 EUR = 4 ILS."""

    def get_mock_converter(from_currency="EUR", to_currency="EUR"):
        mock = Mock(spec=CurrencyConverter)
        mock.from_currency = from_currency
        mock.to_currency = to_currency

        # Set conversion rate based on currency pair
        if from_currency == "CZK" and to_currency == "EUR":
            mock.rate = Decimal("0.04")  # 1 CZK = 0.04 EUR (i.e., 1 EUR = 25 CZK)
            mock.convert.side_effect = lambda czk: czk * Decimal("0.04")
        elif from_currency == "ILS" and to_currency == "EUR":
            mock.rate = Decimal("0.25")  # 1 ILS = 0.25 EUR (i.e., 1 EUR = 4 ILS)
            mock.convert.side_effect = lambda ils: ils * Decimal("0.25")
        else:
            mock.rate = Decimal("1.0")
            mock.convert.side_effect = lambda x: x

        mock.symbol = {"EUR": "€", "CZK": "Kč", "ILS": "₪"}.get(to_currency, to_currency)

        return mock

    with patch(
        "salary_compare.services.currency.get_currency_converter",
        side_effect=get_mock_converter,
    ):
        yield
