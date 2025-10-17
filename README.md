# Salary Compare

An interactive web application for comparing net salaries across different countries and employment types.

## Features

- **Interactive Web Interface**: Modern Streamlit-based UI with real-time calculations
- **Multi-Country Support**: Calculate net salary for various employment types across multiple countries
- **Visual Comparisons**: Interactive charts and tables to compare different scenarios
- **Detailed Breakdowns**: Comprehensive tax and deduction calculations
- **Dynamic Currency Conversion**: Automatically fetches current exchange rates
- **Real-time Updates**: Instant recalculation as you change inputs

## Supported Countries and Employment Types

### Western & Central Europe
- **Germany**: Salaried Employee (Tax Class 1)
- **Czechia**: Salaried Employee, Freelancer (60/40 rule)
- **Spain**: Salaried Employee in Madrid, Barcelona, Valencia (regional rates)

### Southern Europe
- **Portugal**: Salaried Employee, Freelancer (Simplified Regime with 75% deemed expenses)
- **Israel**: Salaried Employee

### Eastern Europe (Low-Tax Freelancer Havens)
- **Romania**: Freelancer (Microenterprise 1% revenue tax)
- **Bulgaria**: Freelancer (10% flat income tax)

## Installation

This project uses Poetry for dependency management.

```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies and create virtual environment
poetry install
```

## Usage

### Running the Streamlit App

```bash
# Run the interactive web application
poetry run streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`.

### Using the Web Interface

1. **Enter your gross salary** in the sidebar
2. **Select countries and employment types** you want to compare
3. **View real-time results** with:
   - Summary comparison table
   - Interactive charts
   - Detailed breakdowns for each scenario

## Testing

The project includes comprehensive unit tests for all calculators:

```bash
# Run all tests
poetry run pytest

# Run specific calculator tests
poetry run pytest salary_compare/calculators/tests/test_germany.py -v
poetry run pytest salary_compare/calculators/tests/test_czechia.py -v

# Run tests with coverage
poetry run pytest --cov=salary_compare
```

### Currency Conversion
- **Live rates**: Uses exchangerate-api.com to fetch current EUR/CZK rates
- **Caching**: Rates are cached for 24 hours to reduce API calls
- **Fallback**: If API fails, uses approximate rate of 1 EUR = 25 CZK
- **Testing**: Tests use mocked conversion for predictable results

## Tax Calculation Details

### Germany (Salaried Employee)
- Progressive income tax rates (14%, 42%, 45%)
- Social security contributions: ~20% of gross income
- Health insurance: ~7.3% of gross income
- Pension insurance: ~9.3% of gross income

### Czechia (Salaried Employee)
- Flat income tax: 15% on income up to CZK 1,867,728, 23% above
- Social security: 6.5% of gross income
- Health insurance: 4.5% of gross income

### Czechia (Freelancer - 60/40 Rule)
- 60% of income considered expenses, 40% taxable
- Income tax: 15% on taxable income (40% of gross)
- Social security: 29.2% on 50% of gross income
- Health insurance: 13.5% on 50% of gross income

### Israel (Salaried Employee)
- Progressive income tax with 7 brackets (10% to 50%)
- National Insurance (Bituach Leumi): ~4%
- Health Tax (Mas Briut): ~5%
- Pension (Gemel Pensia): 6% employee contribution
- Keren Hishtalmut (Advanced Training Fund): 2.5% employee contribution
- Note: Employers also contribute to pension (6.5%) and Keren Hishtalmut (7.5%)
