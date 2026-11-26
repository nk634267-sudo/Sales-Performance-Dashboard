"""
build_notebook.py
Generates the complete, runnable Jupyter Notebook 'sales_analysis.ipynb'
with rich markdown explanations, student-friendly comments, data cleaning,
and exploratory visualizations.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTEBOOK_PATH = os.path.join(BASE_DIR, "sales_analysis.ipynb")
NOTEBOOKS_DIR = os.path.join(BASE_DIR, "notebooks")
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)
NOTEBOOK_PATH_SUB = os.path.join(NOTEBOOKS_DIR, "sales_analysis.ipynb")

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# 📊 Sales Performance Analysis & Data Cleaning Pipeline\n",
            "### Course / Project: Retail & E-Commerce Business Intelligence\n",
            "**Author:** Data Analyst Project (B.Tech Level)\n",
            "**Tech Stack:** Python (Pandas, NumPy, Matplotlib, Seaborn) | Oracle SQL | Power BI\n",
            "\n",
            "---\n",
            "\n",
            "## 1. Project Objective & Problem Statement\n",
            "Modern retail and e-commerce enterprises capture thousands of transactional records daily across multiple product lines, regions, and customer segments. However, raw transactional data often contains real-world quality issues such as duplicate orders, missing customer details, negative return adjustments, and unstandardized dates.\n",
            "\n",
            "This notebook establishes an industry-standard **Data Analyst workflow**:\n",
            "1. **Ingest Raw Data:** Load the raw retail transactions dataset.\n",
            "2. **Data Profiling & Audit:** Assess data shape, column data types, missing rates, and duplicates.\n",
            "3. **Data Cleaning & Quality Control:** Rectify anomalies, standardize date formats, handle null values, and quarantine non-positive transactions.\n",
            "4. **Feature Engineering:** Derive business metrics (`Gross Sales`, `Discount Amount`, `Net Revenue`, `Year`, `Month`, `Quarter`).\n",
            "5. **Exploratory Data Analysis (EDA):** Identify revenue drivers, seasonal trends, top-selling products, and regional sales distribution.\n",
            "6. **Database Export:** Export the verified clean dataset for Oracle SQL database ingestion and Power BI dashboard reporting."
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Environment Setup & Library Imports\n",
            "We import standard scientific computing and visualization packages."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import os\n",
            "import tempfile\n",
            "import pandas as pd\n",
            "import numpy as np\n",
            "\n",
            "# Configure matplotlib cache directory to avoid system temp warnings\n",
            "os.environ['MPLCONFIGDIR'] = os.path.join(tempfile.gettempdir(), 'matplotlib_cache')\n",
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n",
            "\n",
            "# Visual styling settings\n",
            "plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')\n",
            "plt.rcParams['figure.figsize'] = (10, 5)\n",
            "plt.rcParams['font.size'] = 10\n",
            "pd.set_option('display.max_columns', None)\n",
            "pd.set_option('display.float_format', lambda x: f'${x:,.2f}' if abs(x) > 10 else f'{x:,.2f}')\n",
            "\n",
            "print('Libraries successfully loaded.')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Data Ingestion & Preliminary Inspection\n",
            "Let's load `raw_sales_data.csv` and inspect its structure, dimensions, and initial rows."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "raw_data_path = 'data/raw_sales_data.csv' if os.path.exists('data/raw_sales_data.csv') else 'raw_sales_data.csv'\n",
            "df_raw = pd.read_csv(raw_data_path)\n",
            "\n",
            "print(f'Raw Dataset Dimensions: {df_raw.shape[0]} rows and {df_raw.shape[1]} columns')\n",
            "df_raw.head()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 3.1 Data Types & Schema Overview"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "df_raw.info()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Data Quality Audit\n",
            "Before modifying the dataset, we conduct a structured audit across four key dimensions:\n",
            "- **Duplicates:** Repeated records from double checkout submissions.\n",
            "- **Missing Values:** Null entries in customer or geographic identifiers.\n",
            "- **Date Formats:** Inconsistent date strings (`YYYY-MM-DD`, `DD/MM/YYYY`, `MM-DD-YYYY`).\n",
            "- **Value Validity:** Negative prices, quantities, or sales amounts."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "print('--- DATA QUALITY AUDIT REPORT ---')\n",
            "num_duplicates = df_raw.duplicated().sum()\n",
            "print(f'1. Exact Duplicate Rows: {num_duplicates}')\n",
            "\n",
            "missing_summary = df_raw.isnull().sum()\n",
            "print('\\n2. Missing Values per Column:')\n",
            "print(missing_summary[missing_summary > 0])\n",
            "\n",
            "neg_sales = (df_raw['Sales Amount'] < 0).sum()\n",
            "neg_qty = (df_raw['Quantity'] < 0).sum()\n",
            "invalid_price = (df_raw['Unit Price'] <= 0).sum()\n",
            "print(f'\\n3. Negative Sales Records : {neg_sales}')\n",
            "print(f'4. Negative Quantity Records: {neg_qty}')\n",
            "print(f'5. Non-Positive Price Records: {invalid_price}')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 5. Data Cleaning Pipeline\n",
            "\n",
            "### 5.1 Step 1: Duplicate Removal\n",
            "Duplicate orders distort financial reporting by overstating revenue. We drop exact duplicates, retaining the first instance."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "df_clean = df_raw.drop_duplicates(keep='first').copy()\n",
            "print(f'Rows before: {len(df_raw)} | Rows after duplicate removal: {len(df_clean)}')\n",
            "print(f'Total duplicates removed: {len(df_raw) - len(df_clean)}')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 5.2 Step 2: String Trimming & Normalization\n",
            "Leading or trailing whitespaces cause SQL `GROUP BY` and Power BI relationships to fail (e.g. `'Technology '` vs `'Technology'`). We strip all string fields."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "str_columns = df_clean.select_dtypes(include=['object', 'string']).columns\n",
            "for col in str_columns:\n",
            "    df_clean[col] = df_clean[col].astype(str).str.strip()\n",
            "    df_clean[col] = df_clean[col].replace({'nan': np.nan, '': np.nan})\n",
            "print(f'Normalized whitespace across {len(str_columns)} text columns.')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 5.3 Step 3: Date Standardization\n",
            "We parse heterogeneous date representations into standard pandas datetime objects and format as `YYYY-MM-DD`."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "df_clean['Order Date'] = pd.to_datetime(df_clean['Order Date'], format='mixed', errors='coerce')\n",
            "print(f'Date parsing complete. Null date records: {df_clean[\"Order Date\"].isnull().sum()}')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 5.4 Step 4: Missing Value Imputation\n",
            "- **Customer Name:** Imputed using known `Customer ID` mapping; remaining nulls default to `'Valued Customer'`.\n",
            "- **City:** Imputed using the modal city for the given `State`."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Impute missing Customer Names via Customer ID lookup\n",
            "cust_id_map = df_clean.dropna(subset=['Customer Name']).groupby('Customer ID')['Customer Name'].first().to_dict()\n",
            "df_clean['Customer Name'] = df_clean['Customer Name'].fillna(df_clean['Customer ID'].map(cust_id_map))\n",
            "df_clean['Customer Name'] = df_clean['Customer Name'].fillna('Valued Customer')\n",
            "\n",
            "# Impute missing Cities via State mode\n",
            "state_city_mode = df_clean.dropna(subset=['City']).groupby('State')['City'].agg(lambda x: x.mode()[0]).to_dict()\n",
            "df_clean['City'] = df_clean['City'].fillna(df_clean['State'].map(state_city_mode))\n",
            "\n",
            "print('Missing values after imputation:')\n",
            "print(df_clean[['Customer Name', 'City']].isnull().sum())"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 5.5 Step 5: Handling Negative & Invalid Transactions\n",
            "Transactions with non-positive quantities, unit prices, or sales amounts represent returns or entry errors. To prevent skewed revenue calculations, we isolate these into an audit trail and restrict our sales analysis to positive, completed sales."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "invalid_filter = (\n",
            "    (df_clean['Quantity'] <= 0) |\n",
            "    (df_clean['Unit Price'] <= 0) |\n",
            "    (df_clean['Sales Amount'] <= 0)\n",
            ")\n",
            "\n",
            "excluded_audit = df_clean[invalid_filter].copy()\n",
            "print(f'Quarantining {len(excluded_audit)} invalid / return transaction records.')\n",
            "\n",
            "df_clean = df_clean[~invalid_filter].copy().reset_index(drop=True)\n",
            "print(f'Pristine records retained for analysis: {len(df_clean)}')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 6. Feature Engineering\n",
            "To support rich temporal and financial dimensions in Oracle SQL and Power BI, we engineer:\n",
            "- `Gross Amount`: $Quantity \\times Unit\\ Price$\n",
            "- `Discount Amount`: $Gross\\ Amount \\times Discount$\n",
            "- `Sales Amount` (Net Revenue): $Gross\\ Amount - Discount\\ Amount$\n",
            "- `Year`, `Month_Num`, `Month_Name`, `Year_Month`, `Quarter`, `Day_of_Week`"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "df_clean['Quantity'] = df_clean['Quantity'].astype(int)\n",
            "df_clean['Unit Price'] = df_clean['Unit Price'].astype(float).round(2)\n",
            "df_clean['Discount'] = df_clean['Discount'].astype(float).round(2)\n",
            "\n",
            "# Financial recalculations for mathematical integrity\n",
            "df_clean['Gross Amount'] = (df_clean['Quantity'] * df_clean['Unit Price']).round(2)\n",
            "df_clean['Discount Amount'] = (df_clean['Gross Amount'] * df_clean['Discount']).round(2)\n",
            "df_clean['Sales Amount'] = (df_clean['Gross Amount'] - df_clean['Discount Amount']).round(2)\n",
            "\n",
            "# Date hierarchy\n",
            "df_clean['Year'] = df_clean['Order Date'].dt.year\n",
            "df_clean['Month_Num'] = df_clean['Order Date'].dt.month\n",
            "df_clean['Month_Name'] = df_clean['Order Date'].dt.strftime('%B')\n",
            "df_clean['Year_Month'] = df_clean['Order Date'].dt.strftime('%Y-%m')\n",
            "df_clean['Quarter'] = 'Q' + df_clean['Order Date'].dt.quarter.astype(str)\n",
            "df_clean['Day_of_Week'] = df_clean['Order Date'].dt.strftime('%A')\n",
            "df_clean['Order Date'] = df_clean['Order Date'].dt.strftime('%Y-%m-%d')\n",
            "\n",
            "# Standardize column naming for Oracle SQL compliance\n",
            "df_clean.columns = [c.strip().replace(' ', '_').replace('-', '_') for c in df_clean.columns]\n",
            "\n",
            "df_clean.head(3)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 7. Executive KPI Reconciliation\n",
            "We verify core metrics that will serve as the golden baseline across Python, Oracle SQL, and Power BI."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "total_rev = df_clean['Sales_Amount'].sum()\n",
            "total_orders = df_clean['Order_ID'].nunique()\n",
            "total_qty = df_clean['Quantity'].sum()\n",
            "total_cust = df_clean['Customer_ID'].nunique()\n",
            "aov = total_rev / total_orders\n",
            "\n",
            "print('=' * 50)\n",
            "print('        GOLDEN KPI RECONCILIATION BASELINE')\n",
            "print('=' * 50)\n",
            "print(f'Clean Row Count       : {len(df_clean):,}')\n",
            "print(f'Total Revenue         : ${total_rev:,.2f}')\n",
            "print(f'Total Unique Orders   : {total_orders:,}')\n",
            "print(f'Total Quantity Sold   : {total_qty:,}')\n",
            "print(f'Total Unique Customers: {total_cust:,}')\n",
            "print(f'Average Order Value   : ${aov:,.2f}')\n",
            "print('=' * 50)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 8. Exploratory Data Analysis & Visualizations\n",
            "\n",
            "### 8.1 Monthly Revenue & Order Volume Trends"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "monthly_summary = df_clean.groupby('Year_Month').agg(\n",
            "    Monthly_Revenue=('Sales_Amount', 'sum'),\n",
            "    Order_Count=('Order_ID', 'count')\n",
            ").reset_index()\n",
            "\n",
            "fig, ax1 = plt.subplots(figsize=(12, 5))\n",
            "ax1.plot(monthly_summary['Year_Month'], monthly_summary['Monthly_Revenue'] / 1000, \n",
            "         marker='o', color='#1E3A8A', linewidth=2.5, label='Net Revenue ($K)')\n",
            "ax1.set_xlabel('Year-Month')\n",
            "ax1.set_ylabel('Net Revenue ($K)', color='#1E3A8A')\n",
            "ax1.tick_params(axis='x', rotation=45)\n",
            "\n",
            "ax2 = ax1.twinx()\n",
            "ax2.plot(monthly_summary['Year_Month'], monthly_summary['Order_Count'], \n",
            "         marker='s', linestyle='--', color='#F59E0B', linewidth=2, label='Orders')\n",
            "ax2.set_ylabel('Order Count', color='#F59E0B')\n",
            "ax2.grid(False)\n",
            "\n",
            "plt.title('Monthly Sales Revenue and Order Volume (2023 - 2024)')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 8.2 Top 10 Revenue-Generating Products"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "top10_prods = df_clean.groupby(['Product_Name', 'Category'])['Sales_Amount'].sum() \\\n",
            "    .reset_index().sort_values(by='Sales_Amount', ascending=False).head(10)\n",
            "\n",
            "plt.figure(figsize=(10, 5))\n",
            "palette = {'Technology': '#2563EB', 'Furniture': '#059669', 'Office Supplies': '#D97706'}\n",
            "colors = [palette.get(c, '#6B7280') for c in top10_prods['Category']]\n",
            "\n",
            "bars = plt.barh(top10_prods['Product_Name'][::-1], top10_prods['Sales_Amount'][::-1], color=colors[::-1])\n",
            "plt.xlabel('Total Revenue ($)')\n",
            "plt.title('Top 10 Products by Total Net Revenue')\n",
            "\n",
            "for bar in bars:\n",
            "    w = bar.get_width()\n",
            "    plt.text(w + 3000, bar.get_y() + bar.get_height()/2, f'${w:,.0f}', va='center', fontsize=9)\n",
            "\n",
            "plt.xlim(0, top10_prods['Sales_Amount'].max() * 1.15)\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 8.3 Revenue Share by Product Category"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "cat_summary = df_clean.groupby('Category')['Sales_Amount'].sum()\n",
            "plt.figure(figsize=(7, 7))\n",
            "plt.pie(cat_summary, labels=cat_summary.index, autopct='%1.1f%%', startangle=140,\n",
            "        colors=['#059669', '#D97706', '#1E3A8A'],\n",
            "        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2))\n",
            "plt.title('Revenue Contribution by Product Category')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 8.4 Regional Performance Breakdown"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "region_summary = df_clean.groupby(['Region', 'Category'])['Sales_Amount'].sum().unstack()\n",
            "region_summary.plot(kind='bar', figsize=(10, 5), color=['#059669', '#D97706', '#2563EB'], width=0.75)\n",
            "plt.title('Regional Revenue Breakdown by Category')\n",
            "plt.xlabel('Region')\n",
            "plt.ylabel('Revenue ($)')\n",
            "plt.xticks(rotation=0)\n",
            "plt.legend(title='Category')\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 9. Export Cleaned Dataset for Oracle SQL & Power BI\n",
            "We export `cleaned_sales_data.csv` to ensure consistent data structures for Oracle DDL loading and Power BI data modeling."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "out_clean_path = 'data/cleaned_sales_data.csv' if os.path.exists('data') else 'cleaned_sales_data.csv'\n",
            "df_clean.to_csv(out_clean_path, index=False)\n",
            "if out_clean_path != 'cleaned_sales_data.csv':\n",
            "    df_clean.to_csv('cleaned_sales_data.csv', index=False)\n",
            "\n",
            "print(f'Successfully exported cleaned dataset to {out_clean_path} ({len(df_clean)} records).')\n",
            "print('Ready for Oracle SQL database ingestion and Power BI reporting!')"
        ]
    }
]

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.11"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

with open(NOTEBOOK_PATH_SUB, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print(f"Jupyter notebook saved successfully to:\n -> {NOTEBOOK_PATH}\n -> {NOTEBOOK_PATH_SUB}")
