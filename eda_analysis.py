"""
eda_analysis.py
===============
Exploratory Data Analysis (EDA) & Visualization script for Sales Performance Dashboard.
Calculates key business metrics and exports presentation-ready visual charts for portfolio,
viva, and dashboard validation.
"""

import os
import sys
import tempfile
import pandas as pd
import numpy as np

# Ensure matplotlib has a writeable temp config dir
os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "matplotlib_cache")
import matplotlib.pyplot as plt
import seaborn as sns

# Set visual styling for modern corporate / business analytics look
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 10
plt.rcParams["axes.labelweight"] = "semibold"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "cleaned_sales_data.csv")
if not os.path.exists(DATA_PATH):
    DATA_PATH = os.path.join(BASE_DIR, "cleaned_sales_data.csv")

VIS_DIR = os.path.join(BASE_DIR, "visualizations")
os.makedirs(VIS_DIR, exist_ok=True)


def load_cleaned_data() -> pd.DataFrame:
    """Load cleaned dataset."""
    df = pd.read_csv(DATA_PATH)
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    return df


def print_executive_kpis(df: pd.DataFrame):
    """Calculate and display high-level executive KPIs."""
    total_revenue = df["Sales_Amount"].sum()
    total_orders = df["Order_ID"].nunique()
    total_units = df["Quantity"].sum()
    total_customers = df["Customer_ID"].nunique()
    avg_order_value = total_revenue / total_orders if total_orders else 0
    avg_discount = df["Discount"].mean() * 100

    print("=" * 60)
    print("           RETAIL SALES EXECUTIVE KPI SUMMARY")
    print("=" * 60)
    print(f"Total Net Revenue          : ${total_revenue:,.2f}")
    print(f"Total Orders Placed        : {total_orders:,}")
    print(f"Total Quantity Sold (Units): {total_units:,}")
    print(f"Unique Customers           : {total_customers:,}")
    print(f"Average Order Value (AOV)  : ${avg_order_value:,.2f}")
    print(f"Average Discount Rate      : {avg_discount:.2f}%")
    print("=" * 60)


def plot_monthly_sales_trend(df: pd.DataFrame):
    """Plot monthly sales revenue and order volume trends across years."""
    monthly_sales = df.groupby(["Year", "Month_Num", "Month_Name", "Year_Month"]).agg(
        Total_Revenue=("Sales_Amount", "sum"),
        Order_Count=("Order_ID", "count")
    ).reset_index().sort_values(by=["Year", "Month_Num"])

    fig, ax1 = plt.subplots(figsize=(13, 6), dpi=300)

    # Palette
    color_revenue = "#1E3A8A"  # Deep Navy
    color_orders = "#F59E0B"   # Warm Amber

    ax1.plot(monthly_sales["Year_Month"], monthly_sales["Total_Revenue"] / 1000, 
             marker="o", color=color_revenue, linewidth=2.5, label="Net Revenue ($K)")
    ax1.set_xlabel("Year-Month", labelpad=10)
    ax1.set_ylabel("Net Revenue in Thousands ($K)", color=color_revenue, labelpad=10)
    ax1.tick_params(axis="y", labelcolor=color_revenue)
    plt.xticks(rotation=45, ha="right")

    # Secondary axis for order count
    ax2 = ax1.twinx()
    ax2.plot(monthly_sales["Year_Month"], monthly_sales["Order_Count"], 
             marker="s", linestyle="--", color=color_orders, linewidth=2, label="Order Count")
    ax2.set_ylabel("Order Count", color=color_orders, labelpad=10)
    ax2.tick_params(axis="y", labelcolor=color_orders)
    ax2.grid(False)

    plt.title("Monthly Sales Revenue and Order Volume Trend (2023 - 2024)", pad=15)
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=True)

    plt.tight_layout()
    out_path = os.path.join(VIS_DIR, "monthly_sales_trend.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_top_10_products(df: pd.DataFrame):
    """Plot Top 10 products by total revenue."""
    top_prods = df.groupby(["Product_ID", "Product_Name", "Category"]).agg(
        Total_Revenue=("Sales_Amount", "sum"),
        Total_Units=("Quantity", "sum")
    ).reset_index().sort_values(by="Total_Revenue", ascending=False).head(10)

    plt.figure(figsize=(12, 6.5), dpi=300)
    
    # Category color mapping
    cat_palette = {"Technology": "#2563EB", "Furniture": "#059669", "Office Supplies": "#D97706"}
    colors = [cat_palette.get(c, "#4B5563") for c in top_prods["Category"]]

    bars = plt.barh(top_prods["Product_Name"][::-1], top_prods["Total_Revenue"][::-1], color=colors[::-1], edgecolor="none", height=0.65)
    
    # Add revenue text labels
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 4000, bar.get_y() + bar.get_height()/2, f"${width:,.0f}",
                 va="center", ha="left", fontsize=9, fontweight="bold", color="#1F2937")

    plt.xlabel("Total Revenue ($)", labelpad=10)
    plt.title("Top 10 Products by Total Net Revenue", pad=15)
    plt.xlim(0, top_prods["Total_Revenue"].max() * 1.15)
    
    # Custom legend for categories
    handles = [plt.Rectangle((0,0),1,1, color=cat_palette[c]) for c in cat_palette]
    plt.legend(handles, cat_palette.keys(), title="Category", loc="lower right", frameon=True)

    plt.tight_layout()
    out_path = os.path.join(VIS_DIR, "top_10_products.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_category_breakdown(df: pd.DataFrame):
    """Plot Category revenue contribution donut chart."""
    cat_sales = df.groupby("Category")["Sales_Amount"].sum().reset_index()
    cat_sales = cat_sales.sort_values(by="Sales_Amount", ascending=False)

    plt.figure(figsize=(8, 8), dpi=300)
    colors = ["#1E3A8A", "#0D9488", "#F59E0B"]
    
    wedges, texts, autotexts = plt.pie(
        cat_sales["Sales_Amount"],
        labels=cat_sales["Category"],
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        pctdistance=0.75,
        explode=(0.04, 0.04, 0.04),
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2)
    )

    for at in autotexts:
        at.set_fontsize(11)
        at.set_fontweight("bold")
        at.set_color("white")

    for t in texts:
        t.set_fontsize(11)
        t.set_fontweight("semibold")

    # Center label with Total Revenue
    total_rev = cat_sales["Sales_Amount"].sum()
    plt.text(0, 0, f"Total Revenue\n${total_rev:,.0f}", ha="center", va="center",
             fontsize=12, fontweight="bold", color="#111827")

    plt.title("Revenue Share by Product Category", pad=20)
    plt.tight_layout()
    out_path = os.path.join(VIS_DIR, "category_sales_distribution.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_region_performance(df: pd.DataFrame):
    """Plot Region-wise Sales Performance grouped by Category."""
    region_cat = df.groupby(["Region", "Category"])["Sales_Amount"].sum().unstack().fillna(0)
    region_cat["Total"] = region_cat.sum(axis=1)
    region_cat = region_cat.sort_values(by="Total", ascending=False)
    region_cat = region_cat.drop(columns=["Total"])

    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    colors = ["#10B981", "#F59E0B", "#3B82F6"] # Furniture, Office Supplies, Technology
    region_cat.plot(kind="bar", stacked=False, ax=ax, color=colors, width=0.75, edgecolor="none")

    plt.xlabel("Sales Region", labelpad=10)
    plt.ylabel("Revenue ($)", labelpad=10)
    plt.title("Regional Performance by Product Category", pad=15)
    plt.xticks(rotation=0)
    plt.legend(title="Category", frameon=True)
    
    # Format y-axis with dollar commas
    ax.yaxis.set_major_formatter("${x:,.0f}")

    plt.tight_layout()
    out_path = os.path.join(VIS_DIR, "region_wise_sales.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_executive_summary_dashboard(df: pd.DataFrame):
    """Create a unified, multi-panel executive summary dashboard visual."""
    fig = plt.figure(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor("#F8FAFC")
    
    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.25)

    # 1. KPI Cards Row (Row 0)
    total_revenue = df["Sales_Amount"].sum()
    total_orders = df["Order_ID"].nunique()
    total_units = df["Quantity"].sum()
    total_customers = df["Customer_ID"].nunique()
    aov = total_revenue / total_orders

    kpis = [
        ("TOTAL REVENUE", f"${total_revenue:,.2f}", "#1E3A8A"),
        ("TOTAL ORDERS", f"{total_orders:,}", "#0284C7"),
        ("AVERAGE ORDER VALUE", f"${aov:,.2f}", "#0D9488"),
        ("UNITS SOLD", f"{total_units:,}", "#D97706"),
    ]

    # Clear top row and create 4 distinct subplots for KPI cards
    gs_kpi = gs[0, :].subgridspec(1, 4, wspace=0.15)
    for i, (title, val, color) in enumerate(kpis):
        ax = fig.add_subplot(gs_kpi[0, i])
        ax.set_facecolor("#FFFFFF")
        ax.axis("off")
        
        # Border box using Rectangle
        rect = plt.Rectangle((0.02, 0.05), 0.96, 0.90, transform=ax.transAxes, 
                             facecolor="#FFFFFF", edgecolor="#CBD5E1", linewidth=1.5)
        ax.add_patch(rect)
        
        ax.text(0.5, 0.65, title, transform=ax.transAxes, ha="center", va="center",
                fontsize=9, fontweight="bold", color="#64748B")
        ax.text(0.5, 0.32, val, transform=ax.transAxes, ha="center", va="center",
                fontsize=15, fontweight="bold", color=color)

    # 2. Monthly Trend (Row 1, Span columns 0 to 2)
    ax_trend = fig.add_subplot(gs[1, :2])
    ax_trend.set_facecolor("#FFFFFF")
    monthly = df.groupby("Year_Month")["Sales_Amount"].sum().reset_index()
    ax_trend.plot(monthly["Year_Month"], monthly["Sales_Amount"] / 1000, 
                  marker="o", color="#1E3A8A", linewidth=2.2, label="Revenue ($K)")
    ax_trend.set_title("Monthly Revenue Trajectory ($K)", fontsize=11, fontweight="bold", color="#1E293B")
    ax_trend.tick_params(axis="x", rotation=45, labelsize=8)
    ax_trend.yaxis.set_major_formatter("${x:,.0f}K")
    ax_trend.grid(True, linestyle=":", alpha=0.6)

    # 3. Category Donut (Row 1, Column 2)
    ax_cat = fig.add_subplot(gs[1, 2])
    ax_cat.set_facecolor("#FFFFFF")
    cat_sales = df.groupby("Category")["Sales_Amount"].sum()
    ax_cat.pie(cat_sales, labels=cat_sales.index, autopct="%1.0f%%", 
               colors=["#1E3A8A", "#0D9488", "#F59E0B"], 
               wedgeprops=dict(width=0.45, edgecolor="white", linewidth=1.5),
               textprops={'fontsize': 8, 'fontweight': 'bold'})
    ax_cat.set_title("Revenue by Category", fontsize=11, fontweight="bold", color="#1E293B")

    # 4. Regional Breakdown (Row 2, Column 0)
    ax_reg = fig.add_subplot(gs[2, 0])
    ax_reg.set_facecolor("#FFFFFF")
    reg_sales = df.groupby("Region")["Sales_Amount"].sum().sort_values(ascending=True)
    bars = ax_reg.barh(reg_sales.index, reg_sales / 1000, color="#3B82F6", height=0.6)
    ax_reg.set_title("Sales by Region ($K)", fontsize=11, fontweight="bold", color="#1E293B")
    ax_reg.xaxis.set_major_formatter("${x:,.0f}K")
    ax_reg.grid(True, linestyle=":", alpha=0.6)

    # 5. Top 5 Products (Row 2, Spans Columns 1 to 2)
    ax_prod = fig.add_subplot(gs[2, 1:])
    ax_prod.set_facecolor("#FFFFFF")
    top5 = df.groupby("Product_Name")["Sales_Amount"].sum().sort_values(ascending=True).tail(5)
    bars5 = ax_prod.barh(top5.index, top5 / 1000, color="#059669", height=0.6)
    ax_prod.set_title("Top 5 Revenue Generating Products ($K)", fontsize=11, fontweight="bold", color="#1E293B")
    ax_prod.xaxis.set_major_formatter("${x:,.0f}K")
    for bar in bars5:
        width = bar.get_width()
        ax_prod.text(width + 5, bar.get_y() + bar.get_height()/2, f"${width:,.0f}K",
                     va="center", ha="left", fontsize=8, fontweight="bold", color="#1F2937")
    ax_prod.set_xlim(0, top5.max()/1000 * 1.15)
    ax_prod.grid(True, linestyle=":", alpha=0.6)

    # Overall title
    fig.suptitle("RETAIL & E-COMMERCE SALES EXECUTIVE DASHBOARD", 
                 fontsize=14, fontweight="bold", color="#0F172A", y=0.98)

    out_path = os.path.join(VIS_DIR, "sales_kpi_summary_dashboard.png")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def main():
    print("Loading cleaned dataset for Exploratory Data Analysis...")
    df = load_cleaned_data()
    print(f"Loaded {len(df)} cleaned records.")
    
    print_executive_kpis(df)
    
    print("\nGenerating visual charts...")
    plot_monthly_sales_trend(df)
    plot_top_10_products(df)
    plot_category_breakdown(df)
    plot_region_performance(df)
    plot_executive_summary_dashboard(df)
    
    print("\nAll EDA visualizations successfully generated in 'visualizations/' directory!")


if __name__ == "__main__":
    main()
