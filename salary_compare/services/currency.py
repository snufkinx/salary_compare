"""Currency conversion service."""

import requests
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime, timedelta
import json
import os


class CurrencyConverter:
    """Currency conversion service with caching."""
    
    def __init__(self, cache_duration_hours: int = 24):
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.cache_file = os.path.expanduser("~/.salary_compare_currency_cache.json")
        self._rates_cache: Optional[Dict[str, Dict]] = None
    
    def get_eur_to_czk_rate(self) -> Decimal:
        """Get current EUR to CZK exchange rate."""
        rates = self._get_exchange_rates()
        czk_rate = rates.get('CZK', {}).get('rate')
        
        if czk_rate is None:
            # Fallback to approximate rate if API fails
            print("Warning: Could not fetch CZK rate, using fallback rate of 25.0")
            return Decimal('25.0')
        
        return Decimal(str(czk_rate))
    
    def convert_czk_to_eur(self, czk_amount: Decimal) -> Decimal:
        """Convert CZK amount to EUR."""
        rate = self.get_eur_to_czk_rate()
        return czk_amount / rate
    
    def convert_eur_to_czk(self, eur_amount: Decimal) -> Decimal:
        """Convert EUR amount to CZK."""
        rate = self.get_eur_to_czk_rate()
        return eur_amount * rate
    
    def _get_exchange_rates(self) -> Dict[str, Dict]:
        """Get exchange rates from cache or API."""
        # Try to load from cache first
        if self._rates_cache is None:
            self._rates_cache = self._load_from_cache()
        
        # Check if cache is valid
        if self._rates_cache and self._is_cache_valid():
            return self._rates_cache
        
        # Fetch fresh data from API
        try:
            self._rates_cache = self._fetch_from_api()
            self._save_to_cache()
            return self._rates_cache
        except Exception as e:
            print(f"Warning: Failed to fetch exchange rates: {e}")
            # Return cached data even if expired, or fallback
            if self._rates_cache:
                return self._rates_cache
            return {}
    
    def _fetch_from_api(self) -> Dict[str, Dict]:
        """Fetch exchange rates from exchangerate-api.com."""
        try:
            # Use exchangerate-api.com (free tier allows 1500 requests/month)
            response = requests.get(
                "https://api.exchangerate-api.com/v4/latest/EUR",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract rates with metadata
            rates = {}
            for currency, rate in data.get('rates', {}).items():
                rates[currency] = {
                    'rate': rate,
                    'timestamp': datetime.now().isoformat(),
                    'base': 'EUR'
                }
            
            return rates
            
        except requests.RequestException:
            # Fallback to fixer.io if available
            return self._fetch_from_fixer()
    
    def _fetch_from_fixer(self) -> Dict[str, Dict]:
        """Fallback: Fetch from fixer.io (requires API key)."""
        api_key = os.getenv('FIXER_API_KEY')
        if not api_key:
            raise Exception("No API key available for currency conversion")
        
        try:
            response = requests.get(
                f"http://data.fixer.io/api/latest?access_key={api_key}&base=EUR&symbols=CZK",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get('success', False):
                raise Exception(f"API error: {data.get('error', {}).get('info', 'Unknown error')}")
            
            return {
                'CZK': {
                    'rate': data['rates']['CZK'],
                    'timestamp': datetime.now().isoformat(),
                    'base': 'EUR'
                }
            }
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch from fixer.io: {e}")
    
    def _load_from_cache(self) -> Optional[Dict[str, Dict]]:
        """Load exchange rates from local cache file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    return data.get('rates', {})
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load currency cache: {e}")
        return None
    
    def _save_to_cache(self):
        """Save exchange rates to local cache file."""
        try:
            cache_data = {
                'rates': self._rates_cache,
                'cached_at': datetime.now().isoformat()
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save currency cache: {e}")
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid."""
        if not self._rates_cache:
            return False
        
        # Check if any rate has a valid timestamp
        for currency_data in self._rates_cache.values():
            if 'timestamp' in currency_data:
                try:
                    cached_time = datetime.fromisoformat(currency_data['timestamp'])
                    return datetime.now() - cached_time < self.cache_duration
                except ValueError:
                    continue
        
        return False


# Global converter instance
_currency_converter = None


def get_currency_converter() -> CurrencyConverter:
    """Get the global currency converter instance."""
    global _currency_converter
    if _currency_converter is None:
        _currency_converter = CurrencyConverter()
    return _currency_converter
