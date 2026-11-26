"""
generate_interactive_dashboard.py
Generates a standalone, interactive HTML/JS dashboard mockup of the Power BI report
that allows real-time interactive slicing by Region, Category, and Year,
with dynamic KPI cards, Chart.js visuals, and data table.
"""

import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "cleaned_sales_data.csv")
if not os.path.exists(DATA_PATH):
    DATA_PATH = os.path.join(BASE_DIR, "cleaned_sales_data.csv")

HTML_OUTPUT = os.path.join(BASE_DIR, "powerbi", "dashboard_mockup.html")
ROOT_HTML_OUTPUT = os.path.join(BASE_DIR, "dashboard_preview.html")

df = pd.read_csv(DATA_PATH)

# Prepare lightweight JSON records for client-side filtering
records = df[[
    "Order_ID", "Order_Date", "Product_Name", "Category", "Sub_Category",
    "Quantity", "Unit_Price", "Discount", "Sales_Amount", "Customer_Name",
    "Customer_Segment", "Region", "State", "City", "Payment_Method",
    "Year", "Month_Num", "Year_Month"
]].to_dict(orient="records")

records_json = json.dumps(records)

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales Performance Dashboard - Power BI Preview</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-canvas: #F8FAFC;
            --card-bg: #FFFFFF;
            --primary: #1E3A8A;
            --primary-accent: #3B82F6;
            --success: #10B981;
            --amber: #F59E0B;
            --text-dark: #0F172A;
            --text-muted: #64748B;
            --border: #E2E8F0;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif; }}
        body {{ background-color: var(--bg-canvas); color: var(--text-dark); padding: 24px; }}
        
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #FFFFFF;
            padding: 18px 24px;
            border-radius: 10px;
            border: 1px solid var(--border);
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}
        .header-title h1 {{ font-size: 20px; font-weight: 700; color: var(--primary); }}
        .header-title p {{ font-size: 13px; color: var(--text-muted); margin-top: 3px; }}
        
        .filter-bar {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}
        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .filter-group label {{ font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); }}
        .filter-group select {{
            padding: 7px 12px;
            border-radius: 6px;
            border: 1px solid #CBD5E1;
            background: white;
            font-size: 13px;
            font-weight: 500;
            color: var(--text-dark);
            cursor: pointer;
            outline: none;
        }}
        .filter-group select:focus {{ border-color: var(--primary-accent); }}

        /* KPI Cards */
        .kpi-row {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
            margin-bottom: 20px;
        }}
        .kpi-card {{
            background: var(--card-bg);
            border-radius: 10px;
            border: 1px solid var(--border);
            padding: 18px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .kpi-title {{ font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px; }}
        .kpi-value {{ font-size: 26px; font-weight: 700; color: var(--text-dark); margin: 6px 0; }}
        .kpi-badge {{ font-size: 11px; font-weight: 600; padding: 2px 6px; border-radius: 4px; display: inline-block; width: fit-content; }}
        .badge-navy {{ background: #EFF6FF; color: var(--primary); }}
        .badge-green {{ background: #ECFDF5; color: var(--success); }}
        .badge-amber {{ background: #FFFBEB; color: #B45309; }}

        /* Charts Grid */
        .charts-row-1 {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 16px;
            margin-bottom: 20px;
        }}
        .charts-row-2 {{
            display: grid;
            grid-template-columns: 1.2fr 1fr;
            gap: 16px;
            margin-bottom: 20px;
        }}
        .chart-card {{
            background: var(--card-bg);
            border-radius: 10px;
            border: 1px solid var(--border);
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }}
        .chart-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }}
        .chart-title {{ font-size: 14px; font-weight: 700; color: #1E293B; }}
        .chart-subtitle {{ font-size: 12px; color: var(--text-muted); }}

        .chart-container {{ position: relative; height: 320px; width: 100%; }}
        .donut-container {{ position: relative; height: 320px; display: flex; justify-content: center; }}

        .data-table-container {{
            background: var(--card-bg);
            border-radius: 10px;
            border: 1px solid var(--border);
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th {{ text-align: left; padding: 10px 12px; background: #F1F5F9; color: #475569; font-weight: 600; border-bottom: 1px solid var(--border); }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #F1F5F9; }}
        tr:hover td {{ background: #F8FAFC; }}
    </style>
</head>
<body>

    <div class="header">
        <div class="header-title">
            <h1>RETAIL & E-COMMERCE SALES PERFORMANCE DASHBOARD</h1>
            <p>Power BI Executive Reporting Mockup | Python Cleaned Dataset | Oracle SQL Reconciled</p>
        </div>
        <div class="filter-bar">
            <div class="filter-group">
                <label>Year</label>
                <select id="filterYear" onchange="applyFilters()">
                    <option value="All">All Years</option>
                    <option value="2023">2023</option>
                    <option value="2024">2024</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Region</label>
                <select id="filterRegion" onchange="applyFilters()">
                    <option value="All">All Regions</option>
                    <option value="West">West</option>
                    <option value="East">East</option>
                    <option value="Central">Central</option>
                    <option value="South">South</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Category</label>
                <select id="filterCategory" onchange="applyFilters()">
                    <option value="All">All Categories</option>
                    <option value="Technology">Technology</option>
                    <option value="Furniture">Furniture</option>
                    <option value="Office Supplies">Office Supplies</option>
                </select>
            </div>
        </div>
    </div>

    <!-- KPI Cards Row -->
    <div class="kpi-row">
        <div class="kpi-card">
            <span class="kpi-title">Total Net Sales</span>
            <span class="kpi-value" id="kpiSales">$0.00</span>
            <span class="kpi-badge badge-navy">Baseline Reconciled</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-title">Total Orders</span>
            <span class="kpi-value" id="kpiOrders">0</span>
            <span class="kpi-badge badge-navy">Unique Transactions</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-title">Units Sold</span>
            <span class="kpi-value" id="kpiUnits">0</span>
            <span class="kpi-badge badge-amber">Physical Volume</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-title">Average Order Value</span>
            <span class="kpi-value" id="kpiAOV">$0.00</span>
            <span class="kpi-badge badge-green">Per-Order Ticket</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-title">Active Customers</span>
            <span class="kpi-value" id="kpiCustomers">0</span>
            <span class="kpi-badge badge-navy">Unique Buyers</span>
        </div>
    </div>

    <!-- Charts Row 1: Line Trend & Donut Share -->
    <div class="charts-row-1">
        <div class="chart-card">
            <div class="chart-header">
                <div>
                    <div class="chart-title">Monthly Sales Revenue & Order Trajectory</div>
                    <div class="chart-subtitle">Continuous timeline tracking Net Revenue ($K) and monthly order count</div>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="monthlyTrendChart"></canvas>
            </div>
        </div>
        <div class="chart-card">
            <div class="chart-header">
                <div>
                    <div class="chart-title">Revenue by Product Category</div>
                    <div class="chart-subtitle">Percentage contribution to total company sales</div>
                </div>
            </div>
            <div class="donut-container">
                <canvas id="categoryDonutChart"></canvas>
            </div>
        </div>
    </div>

    <!-- Charts Row 2: Top 10 Products & Regional Performance -->
    <div class="charts-row-2">
        <div class="chart-card">
            <div class="chart-header">
                <div>
                    <div class="chart-title">Top 10 Products by Total Net Sales</div>
                    <div class="chart-subtitle">Ranked by revenue contribution with category breakdown</div>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="topProductsChart"></canvas>
            </div>
        </div>
        <div class="chart-card">
            <div class="chart-header">
                <div>
                    <div class="chart-title">Regional Performance by Category</div>
                    <div class="chart-subtitle">Market distribution across geographic sales regions</div>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="regionChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        const rawData = {records_json};
        let lineChart, donutChart, barChart, regionChart;

        function formatCurrency(val) {{
            return '$' + Number(val).toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
        }}

        function applyFilters() {{
            const selectedYear = document.getElementById('filterYear').value;
            const selectedRegion = document.getElementById('filterRegion').value;
            const selectedCategory = document.getElementById('filterCategory').value;

            const filtered = rawData.filter(d => {{
                const matchYear = (selectedYear === 'All' || String(d.Year) === selectedYear);
                const matchRegion = (selectedRegion === 'All' || d.Region === selectedRegion);
                const matchCategory = (selectedCategory === 'All' || d.Category === selectedCategory);
                return matchYear && matchRegion && matchCategory;
            }});

            updateKPIs(filtered);
            updateMonthlyTrend(filtered);
            updateCategoryDonut(filtered);
            updateTopProducts(filtered);
            updateRegionChart(filtered);
        }}

        function updateKPIs(data) {{
            const totalSales = data.reduce((acc, r) => acc + r.Sales_Amount, 0);
            const totalUnits = data.reduce((acc, r) => acc + r.Quantity, 0);
            const orders = new Set(data.map(r => r.Order_ID)).size;
            const customers = new Set(data.map(r => r.Customer_Name)).size;
            const aov = orders > 0 ? (totalSales / orders) : 0;

            document.getElementById('kpiSales').innerText = formatCurrency(totalSales);
            document.getElementById('kpiOrders').innerText = orders.toLocaleString();
            document.getElementById('kpiUnits').innerText = totalUnits.toLocaleString();
            document.getElementById('kpiAOV').innerText = formatCurrency(aov);
            document.getElementById('kpiCustomers').innerText = customers.toLocaleString();
        }}

        function updateMonthlyTrend(data) {{
            const monthlyMap = {{}};
            data.forEach(r => {{
                if (!monthlyMap[r.Year_Month]) {{
                    monthlyMap[r.Year_Month] = {{ revenue: 0, orders: 0 }};
                }}
                monthlyMap[r.Year_Month].revenue += r.Sales_Amount;
                monthlyMap[r.Year_Month].orders += 1;
            }});

            const sortedKeys = Object.keys(monthlyMap).sort();
            const revenues = sortedKeys.map(k => (monthlyMap[k].revenue / 1000).toFixed(1));
            const orders = sortedKeys.map(k => monthlyMap[k].orders);

            if (lineChart) lineChart.destroy();
            const ctx = document.getElementById('monthlyTrendChart').getContext('2d');
            lineChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: sortedKeys,
                    datasets: [
                        {{
                            label: 'Net Revenue ($K)',
                            data: revenues,
                            borderColor: '#1E3A8A',
                            backgroundColor: 'rgba(30, 58, 138, 0.08)',
                            tension: 0.3,
                            fill: true,
                            yAxisID: 'y'
                        }},
                        {{
                            label: 'Order Count',
                            data: orders,
                            borderColor: '#F59E0B',
                            borderDash: [5, 5],
                            tension: 0.3,
                            yAxisID: 'y1'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{ type: 'linear', position: 'left', title: {{ display: true, text: 'Revenue ($K)' }} }},
                        y1: {{ type: 'linear', position: 'right', grid: {{ drawOnChartArea: false }}, title: {{ display: true, text: 'Orders' }} }}
                    }}
                }}
            }});
        }}

        function updateCategoryDonut(data) {{
            const catMap = {{ 'Technology': 0, 'Furniture': 0, 'Office Supplies': 0 }};
            data.forEach(r => {{
                if (catMap[r.Category] !== undefined) catMap[r.Category] += r.Sales_Amount;
            }});

            const labels = Object.keys(catMap);
            const values = Object.values(catMap);

            if (donutChart) donutChart.destroy();
            const ctx = document.getElementById('categoryDonutChart').getContext('2d');
            donutChart = new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: labels,
                    datasets: [{{
                        data: values,
                        backgroundColor: ['#1E3A8A', '#10B981', '#F59E0B']
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ position: 'bottom' }} }}
                }}
            }});
        }}

        function updateTopProducts(data) {{
            const prodMap = {{}};
            data.forEach(r => {{
                prodMap[r.Product_Name] = (prodMap[r.Product_Name] || 0) + r.Sales_Amount;
            }});

            const sorted = Object.entries(prodMap).sort((a,b) => b[1] - a[1]).slice(0, 10);
            const labels = sorted.map(s => s[0]);
            const values = sorted.map(s => s[1]);

            if (barChart) barChart.destroy();
            const ctx = document.getElementById('topProductsChart').getContext('2d');
            barChart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: 'Net Sales ($)',
                        data: values,
                        backgroundColor: '#3B82F6',
                        borderRadius: 4
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }}
                }}
            }});
        }}

        function updateRegionChart(data) {{
            const regions = ['West', 'East', 'Central', 'South'];
            const categories = ['Technology', 'Furniture', 'Office Supplies'];
            
            const matrix = {{}};
            regions.forEach(reg => {{
                matrix[reg] = {{ 'Technology': 0, 'Furniture': 0, 'Office Supplies': 0 }};
            }});

            data.forEach(r => {{
                if (matrix[r.Region] && matrix[r.Region][r.Category] !== undefined) {{
                    matrix[r.Region][r.Category] += r.Sales_Amount;
                }}
            }});

            const datasets = categories.map((cat, idx) => {{
                const colors = ['#1E3A8A', '#10B981', '#F59E0B'];
                return {{
                    label: cat,
                    data: regions.map(reg => matrix[reg][cat]),
                    backgroundColor: colors[idx]
                }};
            }});

            if (regionChart) regionChart.destroy();
            const ctx = document.getElementById('regionChart').getContext('2d');
            regionChart = new Chart(ctx, {{
                type: 'bar',
                data: {{ labels: regions, datasets: datasets }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ position: 'bottom' }} }}
                }}
            }});
        }}

        // Initialize on load
        applyFilters();
    </script>
</body>
</html>
"""

with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
    f.write(html_template)

with open(ROOT_HTML_OUTPUT, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"Interactive Power BI Dashboard preview generated successfully:")
print(f" -> {HTML_OUTPUT}")
print(f" -> {ROOT_HTML_OUTPUT}")
