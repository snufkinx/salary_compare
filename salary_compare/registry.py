"""Tax regime registry."""

from typing import Dict

from .configs import (
    BULGARIA_FREELANCER,
    CZECHIA_FREELANCER,
    CZECHIA_SALARIED,
    GERMANY_SALARIED,
    ISRAEL_SALARIED,
    PORTUGAL_FREELANCER,
    PORTUGAL_SALARIED,
    ROMANIA_FREELANCER_MICRO,
    SPAIN_BARCELONA,
    SPAIN_MADRID,
    SPAIN_VALENCIA,
)
from .models.config import TaxRegimeConfig


class TaxRegimeRegistry:
    """Registry of all available tax regimes."""

    _regimes: Dict[str, TaxRegimeConfig] = {}

    @classmethod
    def register(cls, key: str, regime: TaxRegimeConfig) -> None:
        """
        Register a tax regime.

        Args:
            key: Unique key for the regime (e.g., "germany-salaried")
            regime: Tax regime configuration
        """
        cls._regimes[key] = regime

    @classmethod
    def get(cls, key: str) -> TaxRegimeConfig:
        """
        Get a tax regime by key.

        Args:
            key: The regime key

        Returns:
            Tax regime configuration

        Raises:
            KeyError: If regime not found
        """
        if key not in cls._regimes:
            available = ", ".join(cls._regimes.keys())
            raise KeyError(f"Unknown regime: {key}. Available regimes: {available}")
        return cls._regimes[key]

    @classmethod
    def list_all(cls) -> Dict[str, TaxRegimeConfig]:
        """
        List all available regimes.

        Returns:
            Dictionary of regime_key -> TaxRegimeConfig
        """
        return cls._regimes.copy()

    @classmethod
    def get_keys(cls) -> list:
        """Get list of all registered regime keys."""
        return list(cls._regimes.keys())


# Register all available regimes
TaxRegimeRegistry.register("germany-salaried", GERMANY_SALARIED)
TaxRegimeRegistry.register("czechia-salaried", CZECHIA_SALARIED)
TaxRegimeRegistry.register("czechia-freelancer", CZECHIA_FREELANCER)
TaxRegimeRegistry.register("israel-salaried", ISRAEL_SALARIED)
TaxRegimeRegistry.register("spain-madrid", SPAIN_MADRID)
TaxRegimeRegistry.register("spain-barcelona", SPAIN_BARCELONA)
TaxRegimeRegistry.register("spain-valencia", SPAIN_VALENCIA)
TaxRegimeRegistry.register("romania-freelancer-micro", ROMANIA_FREELANCER_MICRO)
TaxRegimeRegistry.register("bulgaria-freelancer", BULGARIA_FREELANCER)
TaxRegimeRegistry.register("portugal-salaried", PORTUGAL_SALARIED)
TaxRegimeRegistry.register("portugal-freelancer", PORTUGAL_FREELANCER)
