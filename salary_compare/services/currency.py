"""Refactored currency conversion service."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Optional

import requests


class CurrencyConverter:
    """Currency conversion service for a specific currency pair."""

    # Shared cache across all instances
    _exchange_rates_cache: Optional[Dict] = None
    _cache_timestamp: Optional[datetime] = None
    _cache_duration = timedelta(hours=24)

    def __init__(self, from_currency: str = "EUR", to_currency: str = "EUR"):
        """
        Initialize currency converter for a specific pair.

        Args:
            from_currency: Source currency code (e.g., "EUR", "CZK", "ILS")
            to_currency: Target currency code
        """
        self.from_currency = from_currency.upper()
        self.to_currency = to_currency.upper()
        self._rate: Optional[Decimal] = None

    @property
    def rate(self) -> Decimal:
        """Get the conversion rate from source to target currency."""
        if self._rate is None:
            self._rate = self._fetch_rate()
        return self._rate

    @property
    def symbol(self) -> str:
        """Get the currency symbol for the target currency."""
        symbols = {
            "EUR": "€",
            "CZK": "Kč",
            "ILS": "₪",
            "USD": "$",
            "GBP": "£",
        }
        return symbols.get(self.to_currency, self.to_currency)

    def convert(self, amount: Decimal) -> Decimal:
        """Convert amount from source to target currency."""
        if self.from_currency == self.to_currency:
            return amount
        return amount * self.rate

    def _fetch_rate(self) -> Decimal:
        """Fetch the conversion rate."""
        # Same currency - no conversion needed
        if self.from_currency == self.to_currency:
            return Decimal("1.0")

        # Get rates from cache or API
        rates = self._get_all_rates()

        # Calculate conversion rate
        if self.from_currency == "EUR":
            # EUR to other currency
            target_rate = rates.get(self.to_currency)
            if target_rate:
                return Decimal(str(target_rate))
        elif self.to_currency == "EUR":
            # Other currency to EUR
            source_rate = rates.get(self.from_currency)
            if source_rate:
                return Decimal("1") / Decimal(str(source_rate))
        else:
            # Cross-currency conversion (via EUR)
            source_rate = rates.get(self.from_currency)
            target_rate = rates.get(self.to_currency)
            if source_rate and target_rate:
                # Convert: from -> EUR -> to
                eur_amount = Decimal("1") / Decimal(str(source_rate))
                return eur_amount * Decimal(str(target_rate))

        # Fallback to default rates
        fallback_rates = {"CZK": 25.0, "ILS": 4.0, "USD": 1.1, "GBP": 0.85}
        if self.from_currency == "EUR":
            return Decimal(str(fallback_rates.get(self.to_currency, 1.0)))
        elif self.to_currency == "EUR":
            return Decimal("1") / Decimal(str(fallback_rates.get(self.from_currency, 1.0)))
        else:
            return Decimal("1.0")

    @classmethod
    def _get_all_rates(cls) -> Dict[str, float]:
        """Get all exchange rates from cache or API."""
        # Check if cache is valid
        if cls._exchange_rates_cache and cls._cache_timestamp:
            if datetime.now() - cls._cache_timestamp < cls._cache_duration:
                return cls._exchange_rates_cache

        # Fetch from API
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/EUR", timeout=10)
            response.raise_for_status()
            data = response.json()
            cls._exchange_rates_cache = data.get("rates", {})
            cls._cache_timestamp = datetime.now()
            return cls._exchange_rates_cache
        except Exception as e:
            print(f"Warning: Failed to fetch exchange rates: {e}")
            # Use fallback or cached data
            if cls._exchange_rates_cache:
                return cls._exchange_rates_cache
            return {}


def get_currency_converter(
    from_currency: str = "EUR", to_currency: str = "EUR"
) -> CurrencyConverter:
    """
    Get a currency converter instance for a specific pair.

    Args:
        from_currency: Source currency code
        to_currency: Target currency code

    Returns:
        CurrencyConverter instance
    """
    return CurrencyConverter(from_currency, to_currency)
