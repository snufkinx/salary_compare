"""Console output formatter."""

from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..models.tax_result import TaxResult


class ConsoleOutput:
    """Console output formatter using Rich library."""

    def __init__(self):
        self.console = Console()

    def render_single(self, result: TaxResult):
        """Render single calculation result."""
        # Main result table
        table = Table(title=f"Salary Calculation - {result.country} {result.employment_type}")
        table.add_column("Item", style="cyan", no_wrap=True)
        table.add_column("Amount", style="green", justify="right")
        table.add_column("Rate", style="yellow", justify="right")
        table.add_column("Details", style="white")

        # Add basic info
        table.add_row("Gross Salary", f"{result.gross_salary:,.2f}", "", "")
        table.add_row("Tax Base", f"{result.tax_base:,.2f}", "", "")

        # Add deductions
        for deduction in result.deductions:
            table.add_row(
                deduction.name,
                f"{deduction.amount:,.2f}",
                f"{deduction.rate:.1%}" if deduction.rate > 0 else "",
                deduction.description,
            )

        # Add total deductions and net salary
        table.add_row("", "", "", "", style="bold")
        table.add_row(
            "Total Deductions", f"{result.total_deductions:,.2f}", "", "", style="bold red"
        )
        table.add_row("Net Salary", f"{result.net_salary:,.2f}", "", "", style="bold green")

        self.console.print(table)

        # Add description panel
        if result.description:
            description_panel = Panel(
                Text(result.description.strip()),
                title="Tax Regime Description",
                border_style="blue",
            )
            self.console.print(description_panel)

    def render_comparison(self, results: List[TaxResult]):
        """Render comparison of multiple calculations."""
        # Summary comparison table
        table = Table(title="Salary Comparison")
        table.add_column("Country/Type", style="cyan", no_wrap=True)
        table.add_column("Gross Salary", style="white", justify="right")
        table.add_column("Tax Base", style="white", justify="right")
        table.add_column("Total Deductions", style="red", justify="right")
        table.add_column("Net Salary (Annual)", style="green", justify="right")
        table.add_column("Net Salary (Monthly)", style="green", justify="right")
        table.add_column("Net %", style="yellow", justify="right")

        for result in results:
            net_percentage = (
                (result.net_salary / result.gross_salary) * 100 if result.gross_salary > 0 else 0
            )
            monthly_net = result.net_salary / 12

            # Add local currency in brackets if not EUR
            if result.local_currency != "EUR":
                gross_local = result.gross_salary * result.local_currency_rate
                net_annual_local = result.net_salary * result.local_currency_rate
                net_monthly_local = monthly_net * result.local_currency_rate
                
                # Get currency symbol
                currency_symbol = {"CZK": "Kč", "ILS": "₪"}.get(result.local_currency, result.local_currency)

                gross_str = (
                    f"{result.gross_salary:,.2f}\n({gross_local:,.0f} {currency_symbol})"
                )
                net_annual_str = (
                    f"{result.net_salary:,.2f}\n({net_annual_local:,.0f} {currency_symbol})"
                )
                net_monthly_str = (
                    f"{monthly_net:,.2f}\n({net_monthly_local:,.0f} {currency_symbol})"
                )
            else:
                gross_str = f"{result.gross_salary:,.2f}"
                net_annual_str = f"{result.net_salary:,.2f}"
                net_monthly_str = f"{monthly_net:,.2f}"

            table.add_row(
                f"{result.country} {result.employment_type}",
                gross_str,
                f"{result.tax_base:,.2f}",
                f"{result.total_deductions:,.2f}",
                net_annual_str,
                net_monthly_str,
                f"{net_percentage:.1f}%",
            )

        self.console.print(table)

        # Detailed breakdown for each result
        for i, result in enumerate(results):
            self.console.print(
                f"\n[bold blue]Detailed Breakdown {i+1}: {result.country} {result.employment_type}[/bold blue]"
            )

            detail_table = Table()
            detail_table.add_column("Deduction", style="cyan")
            detail_table.add_column("Amount", style="green", justify="right")
            detail_table.add_column("Rate", style="yellow", justify="right")
            detail_table.add_column("Description", style="white")

            for deduction in result.deductions:
                detail_table.add_row(
                    deduction.name,
                    f"{deduction.amount:,.2f}",
                    f"{deduction.rate:.1%}" if deduction.rate > 0 else "",
                    deduction.description,
                )

            self.console.print(detail_table)
