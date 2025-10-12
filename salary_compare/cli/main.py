"""Main CLI interface for salary calculations."""

from decimal import Decimal
from typing import Tuple, Union

import click

from ..output import ConsoleOutput, CSVOutput, HTMLOutput
from ..registry import TaxRegimeRegistry
from ..universal_calculator import UniversalTaxCalculator


def parse_calculation_input(calc_input: str, salary: str) -> Tuple[str, Decimal]:
    """Parse calculation input string into country-employment type and salary."""
    try:
        # Remove commas from salary input for thousands separators
        salary_clean = salary.replace(",", "")
        salary_decimal = Decimal(salary_clean)
        return calc_input, salary_decimal
    except Exception:
        raise click.ClickException(
            f"Invalid salary amount: {salary}. Expected format: 100000 or 100,000"
        )


def get_calculator(calc_type: str, salary: Decimal):
    """Get calculator instance for the given type and salary."""
    try:
        regime = TaxRegimeRegistry.get(calc_type)
        return UniversalTaxCalculator(salary, regime)
    except KeyError as e:
        raise click.ClickException(str(e))


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Salary Compare - Calculate and compare net salaries across countries."""
    pass


@cli.command()
@click.argument("calc_type", type=str)
@click.argument("salary", type=str)
@click.option(
    "-o",
    "--output",
    "output_format",
    type=click.Choice(["console", "HTML", "CSV"], case_sensitive=False),
    default="console",
    help="Output format",
)
@click.option("--output-file", "-f", type=str, help="Output file path (optional)")
def calculate(calc_type: str, salary: str, output_format: str, output_file: str):
    """Calculate net salary for a specific country and employment type.

    Examples:
    salary czechia-freelancer 100000
    salary czechia-freelancer 100,000
    salary germany-salaried 50000 -o HTML
    salary czechia-salaried 80,000 -o CSV -f results.csv
    """
    try:
        calc_type, salary_decimal = parse_calculation_input(calc_type, salary)
        calculator = get_calculator(calc_type, salary_decimal)
        result = calculator.calculate_net_salary()

        # Output based on format
        output: Union[HTMLOutput, CSVOutput, ConsoleOutput]
        if output_format.upper() == "HTML":
            output = HTMLOutput()
            output.render_single(result, output_file)
        elif output_format.upper() == "CSV":
            output = CSVOutput()
            output.render_single(result, output_file)
        else:
            output = ConsoleOutput()
            output.render_single(result)

    except Exception as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument("salary", type=str)
@click.argument("calc_types", nargs=-1, required=True)
@click.option(
    "-o",
    "--output",
    "output_format",
    type=click.Choice(["console", "HTML", "CSV"], case_sensitive=False),
    default="console",
    help="Output format",
)
@click.option("--output-file", "-f", type=str, help="Output file path (optional)")
def compare(salary: str, calc_types: tuple, output_format: str, output_file: str):
    """Compare net salaries across multiple countries and employment types using a single salary.

    Format: salary compare <salary> <calc_type1> <calc_type2> ...

    Examples:
    salary compare 100000 czechia-freelancer germany-salaried
    salary compare 100,000 czechia-freelancer czechia-salaried germany-salaried
    salary compare 75,500 czechia-freelancer germany-salaried -o HTML
    """
    try:
        # Parse salary once
        salary_clean = salary.replace(",", "")
        salary_decimal = Decimal(salary_clean)

        # Calculate for each type
        results = []
        for calc_type in calc_types:
            try:
                calculator = get_calculator(calc_type, salary_decimal)
                result = calculator.calculate_net_salary()
                results.append(result)
            except KeyError as e:
                raise click.ClickException(str(e))

        # Output based on format
        output: Union[HTMLOutput, CSVOutput, ConsoleOutput]
        if output_format.upper() == "HTML":
            output = HTMLOutput()
            output.render_comparison(results, output_file)
        elif output_format.upper() == "CSV":
            output = CSVOutput()
            output.render_comparison(results, output_file)
        else:
            output = ConsoleOutput()
            output.render_comparison(results)

    except Exception as e:
        raise click.ClickException(str(e))


@cli.command()
def list_types():
    """List all available calculation types."""
    click.echo("Available calculation types:")
    for calc_type in TaxRegimeRegistry.get_keys():
        regime = TaxRegimeRegistry.get(calc_type)
        # Get first meaningful line of description
        description_lines = [
            line.strip() for line in regime.description.strip().split("\n") if line.strip()
        ]
        description = (
            description_lines[0]
            if description_lines
            else f"{regime.country.value} {regime.employment_type.value}"
        )
        # Remove trailing colon if present
        description = description.rstrip(":")
        click.echo(f"  {calc_type:<20} - {description}")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
