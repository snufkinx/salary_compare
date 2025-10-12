"""HTML output formatter with interactive elements."""

from typing import List, Optional

from jinja2 import Template

from ..models.tax_result import TaxResult


class HTMLOutput:
    """HTML output formatter with interactive elements."""

    def __init__(self):
        self.template = self._load_template()

    def _load_template(self) -> Template:
        """Load HTML template."""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Salary Calculation Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 30px;
        }
        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }
        .comparison-table th {
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
            font-weight: 600;
            color: #495057;
        }
        .comparison-table th.number-header {
            text-align: center;
        }
        .comparison-table td {
            padding: 15px;
            border-bottom: 1px solid #dee2e6;
        }
        .comparison-table tr:hover {
            background-color: #f8f9fa;
        }
        .number {
            text-align: center;
            font-family: 'Courier New', monospace;
        }
        .positive {
            color: #28a745;
            font-weight: 600;
        }
        .negative {
            color: #dc3545;
            font-weight: 600;
        }
        .local-currency {
            display: block;
            font-size: 0.85em;
            color: #2d7a3e;
            margin-top: 4px;
            font-weight: normal;
        }
        .detail-section {
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .detail-section h3 {
            margin-top: 0;
            color: #495057;
        }
        .detail-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        .detail-table th {
            background: #e9ecef;
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
            font-weight: 600;
            font-size: 13px;
        }
        .detail-table th.number-header {
            text-align: center;
        }
        .detail-table td {
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
            font-size: 13px;
        }
        .detail-table tr:hover {
            background-color: #f1f3f4;
        }
        .clickable {
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .clickable:hover {
            background-color: #e3f2fd !important;
        }
        .popup {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        .popup-content {
            background-color: white;
            margin: 15% auto;
            padding: 20px;
            border-radius: 8px;
            width: 80%;
            max-width: 600px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            position: relative;
        }
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            position: absolute;
            right: 15px;
            top: 10px;
        }
        .close:hover {
            color: #000;
        }
        .description {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #2196f3;
            white-space: pre-line;
            font-size: 14px;
            line-height: 1.6;
        }
        .highlight {
            background: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid #ffc107;
        }
        .expand-icon {
            cursor: pointer;
            color: #667eea;
            font-weight: bold;
            font-size: 16px;
            margin-right: 5px;
            user-select: none;
            display: inline-block;
            width: 20px;
            text-align: center;
        }
        .expand-icon:hover {
            color: #764ba2;
        }
        .bracket-row {
            display: none;
            background-color: #f8f9fa;
        }
        .bracket-row.expanded {
            display: table-row;
        }
        .bracket-row td {
            padding: 8px 12px 8px 40px;
            font-size: 12px;
            color: #6c757d;
            border-bottom: 1px solid #e9ecef;
        }
        .bracket-label {
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Salary Calculation Report</h1>
            <p>Comprehensive tax analysis and net salary calculation</p>
        </div>

        <div class="content">
            {% if results|length == 1 %}
                {% set result = results[0] %}
                <div class="highlight">
                    <h3>Calculation Summary</h3>
                    <p><strong>Country:</strong> {{ result.country }}</p>
                    <p><strong>Employment Type:</strong> {{ result.employment_type }}</p>
                    <p><strong>Gross Salary:</strong> {{ "{:,.2f}".format(result.gross_salary) }} €</p>
                    <p><strong>Tax Base:</strong> {{ "{:,.2f}".format(result.tax_base) }} €</p>
                    <p><strong>Net Salary:</strong> {{ "{:,.2f}".format(result.net_salary) }} €</p>
                    <p><strong>Total Deductions:</strong> {{ "{:,.2f}".format(result.total_deductions) }} €</p>
                </div>

                <div class="detail-section">
                    <h3>Detailed Breakdown</h3>
                    <table class="detail-table">
                        <thead>
                            <tr>
                                <th>Deduction Type</th>
                                <th class="number-header">Amount</th>
                                <th class="number-header">Rate</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for deduction in result.deductions %}
                            <tr class="clickable" onclick="showPopup('{{ deduction.name }}', '{{ deduction.calculation_details }}')">
                                <td>
                                    {% if deduction.name == "Income Tax" and result.income_tax_brackets|length > 0 %}
                                    <span class="expand-icon" onclick="event.stopPropagation(); toggleBrackets('single-brackets')">+</span>
                                    {% endif %}
                                    {{ deduction.name }}
                                </td>
                                <td class="number">{{ "{:,.2f}".format(deduction.amount) }} €</td>
                                <td class="number">{{ "%.1f"|format(deduction.rate * 100) }}%</td>
                                <td>{{ deduction.description }}</td>
                            </tr>
                            {% if deduction.name == "Income Tax" and result.income_tax_brackets|length > 0 %}
                                {% for bracket in result.income_tax_brackets %}
                                <tr class="bracket-row" data-group="single-brackets">
                                    <td class="bracket-label">↳ Bracket: {{ "{:,.0f}".format(bracket.lower_bound) }} - {{ "{:,.0f}".format(bracket.upper_bound) }} €</td>
                                    <td class="number">{{ "{:,.2f}".format(bracket.tax_amount) }} €</td>
                                    <td class="number">{{ "%.1f"|format(bracket.rate * 100) }}%</td>
                                    <td>Taxable: {{ "{:,.2f}".format(bracket.taxable_amount) }} €</td>
                                </tr>
                                {% endfor %}
                            {% endif %}
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

                {% if result.description %}
                <div class="description">
                    <h4>Tax Regime Description</h4>
                    {{ result.description }}
                </div>
                {% endif %}

            {% else %}
                <h2>Comparison Results</h2>
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Country/Type</th>
                            <th class="number-header">Gross Salary</th>
                            <th class="number-header">Tax Base</th>
                            <th class="number-header">Total Deductions</th>
                            <th class="number-header">Net Salary (Annual)</th>
                            <th class="number-header">Net Salary (Monthly)</th>
                            <th class="number-header">Net %</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for result in results %}
                        {% set net_percentage = (result.net_salary / result.gross_salary * 100) if result.gross_salary > 0 else 0 %}
                        {% set monthly_net = result.net_salary / 12 %}
                        <tr>
                            <td>{{ result.country }} {{ result.employment_type }}</td>
                            <td class="number">
                                {{ "{:,.2f}".format(result.gross_salary) }} €
                                {% if result.local_currency != "EUR" %}
                                    {% set gross_local = result.gross_salary * result.local_currency_rate %}
                                    {% if result.local_currency == "CZK" %}
                                        {% set currency_symbol = "Kč" %}
                                    {% elif result.local_currency == "ILS" %}
                                        {% set currency_symbol = "₪" %}
                                    {% else %}
                                        {% set currency_symbol = result.local_currency %}
                                    {% endif %}
                                    <span class="local-currency">({{ "{:,.0f}".format(gross_local) }} {{ currency_symbol }})</span>
                                {% endif %}
                            </td>
                            <td class="number">{{ "{:,.2f}".format(result.tax_base) }} €</td>
                            <td class="number negative">{{ "{:,.2f}".format(result.total_deductions) }} €</td>
                            <td class="number positive">
                                {{ "{:,.2f}".format(result.net_salary) }} €
                                {% if result.local_currency != "EUR" %}
                                    {% set net_annual_local = result.net_salary * result.local_currency_rate %}
                                    {% if result.local_currency == "CZK" %}
                                        {% set currency_symbol = "Kč" %}
                                    {% elif result.local_currency == "ILS" %}
                                        {% set currency_symbol = "₪" %}
                                    {% else %}
                                        {% set currency_symbol = result.local_currency %}
                                    {% endif %}
                                    <span class="local-currency">({{ "{:,.0f}".format(net_annual_local) }} {{ currency_symbol }})</span>
                                {% endif %}
                            </td>
                            <td class="number positive">
                                {{ "{:,.2f}".format(monthly_net) }} €
                                {% if result.local_currency != "EUR" %}
                                    {% set net_monthly_local = monthly_net * result.local_currency_rate %}
                                    {% if result.local_currency == "CZK" %}
                                        {% set currency_symbol = "Kč" %}
                                    {% elif result.local_currency == "ILS" %}
                                        {% set currency_symbol = "₪" %}
                                    {% else %}
                                        {% set currency_symbol = result.local_currency %}
                                    {% endif %}
                                    <span class="local-currency">({{ "{:,.0f}".format(net_monthly_local) }} {{ currency_symbol }})</span>
                                {% endif %}
                            </td>
                            <td class="number">{{ "%.1f"|format(net_percentage) }}%</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>

                {% for result in results %}
                {% set result_idx = loop.index0 %}
                <div class="detail-section">
                    <h3>{{ result.country }} {{ result.employment_type }}</h3>
                    <table class="detail-table">
                        <thead>
                            <tr>
                                <th>Deduction Type</th>
                                <th class="number-header">Amount</th>
                                <th class="number-header">Rate</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for deduction in result.deductions %}
                            <tr class="clickable" onclick="showPopup('{{ deduction.name }}', '{{ deduction.calculation_details }}')">
                                <td>
                                    {% if deduction.name == "Income Tax" and result.income_tax_brackets|length > 0 %}
                                    <span class="expand-icon" onclick="event.stopPropagation(); toggleBrackets('result-{{ result_idx }}-brackets')">+</span>
                                    {% endif %}
                                    {{ deduction.name }}
                                </td>
                                <td class="number">{{ "{:,.2f}".format(deduction.amount) }} €</td>
                                <td class="number">{{ "%.1f"|format(deduction.rate * 100) }}%</td>
                                <td>{{ deduction.description }}</td>
                            </tr>
                            {% if deduction.name == "Income Tax" and result.income_tax_brackets|length > 0 %}
                                {% for bracket in result.income_tax_brackets %}
                                <tr class="bracket-row" data-group="result-{{ result_idx }}-brackets">
                                    <td class="bracket-label">↳ Bracket: {{ "{:,.0f}".format(bracket.lower_bound) }} - {{ "{:,.0f}".format(bracket.upper_bound) }} €</td>
                                    <td class="number">{{ "{:,.2f}".format(bracket.tax_amount) }} €</td>
                                    <td class="number">{{ "%.1f"|format(bracket.rate * 100) }}%</td>
                                    <td>Taxable: {{ "{:,.2f}".format(bracket.taxable_amount) }} €</td>
                                </tr>
                                {% endfor %}
                            {% endif %}
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% endfor %}
            {% endif %}
        </div>
    </div>

    <!-- Popup Modal -->
    <div id="popup" class="popup">
        <div class="popup-content">
            <span class="close" onclick="closePopup()">&times;</span>
            <h3 id="popup-title"></h3>
            <p id="popup-content"></p>
        </div>
    </div>

    <script>
        function showPopup(title, content) {
            document.getElementById('popup-title').textContent = title;
            document.getElementById('popup-content').textContent = content;
            document.getElementById('popup').style.display = 'block';
        }

        function closePopup() {
            document.getElementById('popup').style.display = 'none';
        }

        function toggleBrackets(groupId) {
            var brackets = document.querySelectorAll('[data-group="' + groupId + '"]');
            var icon = event.target;

            // Check if brackets exist
            if (brackets.length === 0) {
                return;
            }

            var isExpanded = brackets[0].classList.contains('expanded');

            brackets.forEach(function(bracket) {
                if (isExpanded) {
                    bracket.classList.remove('expanded');
                } else {
                    bracket.classList.add('expanded');
                }
            });

            // Toggle icon
            icon.textContent = isExpanded ? '+' : '−';
        }

        // Close popup when clicking outside
        window.onclick = function(event) {
            var popup = document.getElementById('popup');
            if (event.target == popup) {
                popup.style.display = 'none';
            }
        }
    </script>
</body>
</html>
        """
        return Template(template_content)

    def render_single(self, result: TaxResult, output_file: Optional[str] = None):
        """Render single calculation result to HTML."""
        html_content = self.template.render(results=[result])
        self._write_html(html_content, output_file)

    def render_comparison(self, results: List[TaxResult], output_file: Optional[str] = None):
        """Render comparison of multiple calculations to HTML."""
        html_content = self.template.render(results=results)
        self._write_html(html_content, output_file)

    def _write_html(self, html_content: str, output_file: Optional[str] = None):
        """Write HTML content to file."""
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"HTML report saved to: {output_file}")
        else:
            # Default filename
            filename = "salary_report.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"HTML report saved to: {filename}")
