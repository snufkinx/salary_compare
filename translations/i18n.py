"""
Internationalization (i18n) module for the Salary Comparison Tool.
Uses Python's built-in gettext for translations.
"""

import gettext
import os
from typing import Dict, Optional

# Available languages
AVAILABLE_LANGUAGES = {
    'en': 'English',
    'es': 'Español', 
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano',
    'pt': 'Português',
    'cs': 'Čeština',
    'he': 'עברית',
    'ro': 'Română',
    'bg': 'Български'
}

class TranslationManager:
    """Manages translations for the application."""
    
    def __init__(self, language: str = 'en'):
        self.language = language
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, str]:
        """Load translations for the current language."""
        # For now, we'll use a simple dictionary approach
        # In production, you'd load from .po files
        return self._get_translation_dict(self.language)
    
    def _get_translation_dict(self, lang: str) -> Dict[str, str]:
        """Get translation dictionary for a specific language."""
        translations = {
            'en': {
                # App title and description
                'app_title': 'Salary Comparison Tool',
                'app_description': 'Compare net salaries across different countries and employment types',
                'configuration': 'Configuration',
                'gross_salary': 'Gross Salary (€)',
                'display_currency': 'Display Currency',
                'select_tax_regimes': 'Select Tax Regimes',
                'summary_comparison': 'Summary Comparison',
                'comparison_chart': 'Comparison Chart',
                'detailed_breakdowns': 'Detailed Breakdowns',
                'country_comparison': 'Country Comparison',
                'salary_progression': 'Salary Progression',
                'calculating_salaries': 'Calculating salaries...',
                'please_select_regimes': 'Please select at least one tax regime from the sidebar to see calculations.',
                'change_inputs': 'Change inputs in the sidebar to see real-time updates',
                
                # Table headers
                'country': 'Country',
                'gross_annual': 'Gross Annual',
                'net_annual': 'Net Annual', 
                'gross_monthly': 'Gross Monthly',
                'net_monthly': 'Net Monthly',
                'tax_percentage': 'Tax %',
                'gross_salary_metric': 'Gross Salary',
                'net_salary_metric': 'Net Salary',
                'monthly_net_metric': 'Monthly Net',
                'effective_tax_metric': 'Effective Tax',
                'tax_base': 'Tax Base',
                'deductions': 'Deductions',
                'deduction': 'Deduction',
                'amount': 'Amount',
                'rate': 'Rate',
                'details': 'Details',
                'income_tax_brackets': 'Income Tax Brackets',
                'bracket': 'Bracket',
                'taxable_amount': 'Taxable Amount',
                'tax_amount': 'Tax Amount',
                
                # Chart labels
                'net_salary': 'Net Salary',
                'tax_rate': 'Tax Rate %',
                'countries': 'Countries',
                'net_salary_eur': 'Net Salary (€)',
                'tax_rate_percent': 'Tax Rate (%)',
                'gross_salary_eur': 'Gross Salary (€)',
                'net_salary_vs_gross': 'Net Salary vs Gross Salary Progression',
                'current': 'Current',
                
                # Currency names
                'euro': '€ Euro',
                'us_dollar': '$ US Dollar',
                'british_pound': '£ British Pound',
                'czech_koruna': 'Kč Czech Koruna',
                'israeli_shekel': '₪ Israeli Shekel',
                'romanian_leu': 'lei Romanian Leu',
                'bulgarian_lev': 'лв Bulgarian Lev'
            },
            
            'es': {
                'app_title': 'Herramienta de Comparación Salarial',
                'app_description': 'Compara salarios netos entre diferentes países y tipos de empleo',
                'configuration': 'Configuración',
                'gross_salary': 'Salario Bruto (€)',
                'display_currency': 'Moneda de Visualización',
                'select_tax_regimes': 'Seleccionar Regímenes Fiscales',
                'summary_comparison': 'Comparación Resumen',
                'comparison_chart': 'Gráfico de Comparación',
                'detailed_breakdowns': 'Desgloses Detallados',
                'country_comparison': 'Comparación por País',
                'salary_progression': 'Progresión Salarial',
                'calculating_salaries': 'Calculando salarios...',
                'please_select_regimes': 'Por favor selecciona al menos un régimen fiscal del panel lateral para ver los cálculos.',
                'change_inputs': 'Cambia las entradas en el panel lateral para ver actualizaciones en tiempo real',
                
                'country': 'País',
                'gross_annual': 'Bruto Anual',
                'net_annual': 'Neto Anual',
                'gross_monthly': 'Bruto Mensual',
                'net_monthly': 'Neto Mensual',
                'tax_percentage': 'Impuesto %',
                'gross_salary_metric': 'Salario Bruto',
                'net_salary_metric': 'Salario Neto',
                'monthly_net_metric': 'Neto Mensual',
                'effective_tax_metric': 'Impuesto Efectivo',
                'tax_base': 'Base Imponible',
                'deductions': 'Deducciones',
                'deduction': 'Deducción',
                'amount': 'Cantidad',
                'rate': 'Tasa',
                'details': 'Detalles',
                'income_tax_brackets': 'Brackets de Impuesto sobre la Renta',
                'bracket': 'Bracket',
                'taxable_amount': 'Cantidad Tributable',
                'tax_amount': 'Cantidad de Impuesto',
                
                'net_salary': 'Salario Neto',
                'tax_rate': 'Tasa de Impuesto %',
                'countries': 'Países',
                'net_salary_eur': 'Salario Neto (€)',
                'tax_rate_percent': 'Tasa de Impuesto (%)',
                'gross_salary_eur': 'Salario Bruto (€)',
                'net_salary_vs_gross': 'Progresión Salario Neto vs Bruto',
                'current': 'Actual',
                
                'euro': '€ Euro',
                'us_dollar': '$ Dólar Estadounidense',
                'british_pound': '£ Libra Esterlina',
                'czech_koruna': 'Kč Corona Checa',
                'israeli_shekel': '₪ Shekel Israelí',
                'romanian_leu': 'lei Leu Rumano',
                'bulgarian_lev': 'лв Lev Búlgaro'
            },
            
            'fr': {
                'app_title': 'Outil de Comparaison Salariale',
                'app_description': 'Comparez les salaires nets entre différents pays et types d\'emploi',
                'configuration': 'Configuration',
                'gross_salary': 'Salaire Brut (€)',
                'display_currency': 'Devise d\'Affichage',
                'select_tax_regimes': 'Sélectionner les Régimes Fiscaux',
                'summary_comparison': 'Comparaison Résumé',
                'comparison_chart': 'Graphique de Comparaison',
                'detailed_breakdowns': 'Détails Détaillés',
                'country_comparison': 'Comparaison par Pays',
                'salary_progression': 'Progression Salariale',
                'calculating_salaries': 'Calcul des salaires...',
                'please_select_regimes': 'Veuillez sélectionner au moins un régime fiscal dans la barre latérale pour voir les calculs.',
                'change_inputs': 'Modifiez les entrées dans la barre latérale pour voir les mises à jour en temps réel',
                
                'country': 'Pays',
                'gross_annual': 'Brut Annuel',
                'net_annual': 'Net Annuel',
                'gross_monthly': 'Brut Mensuel',
                'net_monthly': 'Net Mensuel',
                'tax_percentage': 'Impôt %',
                'gross_salary_metric': 'Salaire Brut',
                'net_salary_metric': 'Salaire Net',
                'monthly_net_metric': 'Net Mensuel',
                'effective_tax_metric': 'Impôt Effectif',
                'tax_base': 'Base Imposable',
                'deductions': 'Déductions',
                'deduction': 'Déduction',
                'amount': 'Montant',
                'rate': 'Taux',
                'details': 'Détails',
                'income_tax_brackets': 'Tranches d\'Impôt sur le Revenu',
                'bracket': 'Tranche',
                'taxable_amount': 'Montant Imposable',
                'tax_amount': 'Montant d\'Impôt',
                
                'net_salary': 'Salaire Net',
                'tax_rate': 'Taux d\'Impôt %',
                'countries': 'Pays',
                'net_salary_eur': 'Salaire Net (€)',
                'tax_rate_percent': 'Taux d\'Impôt (%)',
                'gross_salary_eur': 'Salaire Brut (€)',
                'net_salary_vs_gross': 'Progression Salaire Net vs Brut',
                'current': 'Actuel',
                
                'euro': '€ Euro',
                'us_dollar': '$ Dollar Américain',
                'british_pound': '£ Livre Sterling',
                'czech_koruna': 'Kč Couronne Tchèque',
                'israeli_shekel': '₪ Shekel Israélien',
                'romanian_leu': 'lei Leu Roumain',
                'bulgarian_lev': 'лв Lev Bulgare'
            }
        }
        
        return translations.get(lang, translations['en'])
    
    def get(self, key: str, **kwargs) -> str:
        """Get translated text for a key."""
        text = self.translations.get(key, key)
        
        # Simple string formatting for placeholders
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                # If formatting fails, return the text as-is
                pass
        
        return text
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages."""
        return AVAILABLE_LANGUAGES

# Global translation manager instance
_translation_manager: Optional[TranslationManager] = None

def set_language(language: str) -> None:
    """Set the current language."""
    global _translation_manager
    _translation_manager = TranslationManager(language)

def get_translation_manager() -> TranslationManager:
    """Get the current translation manager."""
    global _translation_manager
    if _translation_manager is None:
        _translation_manager = TranslationManager('en')
    return _translation_manager

def _(key: str, **kwargs) -> str:
    """Get translated text (convenience function)."""
    return get_translation_manager().get(key, **kwargs)
