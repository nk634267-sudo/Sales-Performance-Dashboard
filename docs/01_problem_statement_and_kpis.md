# Project: Retail & E-Commerce Sales Performance Dashboard

## 1. Problem Statement

### 1.1 Business Context
In multi-channel retail and e-commerce enterprises, sales transactions occur across multiple regions, customer segments, product categories, and fulfillment tiers. Without a unified analytical pipeline, business leadership faces significant operational blind spots:
- Inability to quickly pinpoint underperforming regions or product categories.
- Erosion of profit margins due to aggressive, unmonitored discounting strategies.
- Fragmented reporting where numbers reported by marketing, regional operations, and finance conflict due to inconsistent data cleaning and transformation logic.

### 1.2 Objective
Design, build, and deploy an enterprise-grade end-to-end data pipeline and business intelligence dashboard using **Python (Pandas)**, **Oracle SQL**, and **Power BI**. 

The system must:
1. Ingest raw retail transaction records (e.g., Kaggle Superstore Sales).
2. Cleanse anomalies (nulls, duplicate transactions, negative revenues, invalid dates).
3. Structure data into an optimized Kimball Star Schema in an Oracle database.
4. Deliver high-performance analytical views and window function metrics (running totals, ranking, MoM growth).
5. Expose an interactive, self-service Power BI dashboard with 100% data reconciliation (within 0.1% tolerance) across CSV, database, and presentation layers.

---

## 2. Core Business KPIs & Mathematical Definitions

| KPI Name | Formula | Business Interpretation | Oracle SQL Definition | Power BI DAX Expression |
| :--- | :--- | :--- | :--- | :--- |
| **Total Sales** | $$\sum \text{Sales}$$ | Total revenue generated before deducting costs or expenses. | `SUM(sales_amount)` | `Total Sales = SUM(fact_sales[sales_amount])` |
| **Total Profit** | $$\sum \text{Profit}$$ | Net earnings after accounting for cost of goods sold (COGS) and fulfillment. | `SUM(profit_amount)` | `Total Profit = SUM(fact_sales[profit_amount])` |
| **Profit Margin (%)** | $$\frac{\sum \text{Profit}}{\sum \text{Sales}} \times 100$$ | Percentage of revenue converted into gross profit; measures pricing efficiency. | `ROUND((SUM(profit_amount) / NULLIF(SUM(sales_amount), 0)) * 100, 2)` | `Profit Margin = DIVIDE([Total Profit], [Total Sales], 0)` |
| **Total Orders** | $\text{CountDistinct}(\text{Order ID})$ | Total number of unique purchase transactions completed. | `COUNT(DISTINCT order_id)` | `Total Orders = DISTINCTCOUNT(fact_sales[order_id])` |
| **Average Order Value (AOV)** | $\frac{\text{Total Sales}}{\text{Total Orders}}$ | Average dollar amount spent per transaction; key metric for checkout growth. | `ROUND(SUM(sales_amount) / NULLIF(COUNT(DISTINCT order_id), 0), 2)` | `Average Order Value = DIVIDE([Total Sales], [Total Orders], 0)` |
| **Total Quantity Sold** | $$\sum \text{Quantity}$$ | Physical volume of goods shipped across all order lines. | `SUM(quantity)` | `Total Quantity = SUM(fact_sales[quantity])` |
| **Average Discount** | $\text{Avg}(\text{Discount})$ | Weighted or mean markdown given to customers; tracks discount dependency. | `ROUND(AVG(discount_rate) * 100, 2)` | `Average Discount = AVERAGE(fact_sales[discount_rate])` |
| **Loss-Making Orders Count** | $\text{CountDistinct}(\text{Order ID where Profit} < 0)$ | Orders where fulfillment/discounting costs exceeded revenue. | `COUNT(DISTINCT CASE WHEN profit_amount < 0 THEN order_id END)` | `Loss Orders = CALCULATE(DISTINCTCOUNT(fact_sales[order_id]), fact_sales[profit_amount] < 0)` |

---

## 3. Data Reconciliation & Audit Acceptance Criteria

To guarantee data integrity across all 3 tiers (Python -> Oracle SQL -> Power BI), the following checks must pass:

| Check Item | Python (Pandas) Target | Oracle SQL Target | Power BI Model Target | Allowable Variance |
| :--- | :--- | :--- | :--- | :--- |
| **Total Row Count** | Cleaned DataFrame row count | `SELECT COUNT(*) FROM fact_sales;` | `COUNTROWS(fact_sales)` | 0% (Exact match) |
| **Total Sales** | `df['sales'].sum()` | `SELECT SUM(sales_amount) FROM fact_sales;` | `[Total Sales]` | < 0.1% (Rounding differences only) |
| **Total Profit** | `df['profit'].sum()` | `SELECT SUM(profit_amount) FROM fact_sales;` | `[Total Profit]` | < 0.1% |
| **Distinct Orders** | `df['order_id'].nunique()` | `SELECT COUNT(DISTINCT order_id) FROM fact_sales;` | `[Total Orders]` | 0% (Exact match) |
| **Top 1 Product by Sales**| Matches output of `groupby('product_name')` | Matches `DENSE_RANK() OVER (ORDER BY SUM(sales) DESC)` | Matches visual top product filter | Identical product name & amount |
