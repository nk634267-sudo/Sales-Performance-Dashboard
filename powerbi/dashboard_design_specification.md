# 🎨 Power BI Dashboard Design Specification

## Overview
This document specifies the exact layout, color palette, visual containers, typography, and interactivity rules implemented in the **Sales Performance Dashboard** (`Sales_Performance_Dashboard.pbix`).

---

## 1. Visual Hierarchy & Theme

- **Design Philosophy:** Executive Corporate BI (Clean Slate & Midnight Navy)
- **Report Canvas Dimensions:** 1920 x 1080 px (16:9 widescreen)
- **Canvas Background:** `#F8FAFC` (Light Slate Tint)
- **Card & Visual Container Background:** `#FFFFFF` (Pure White) with 1px border `#E2E8F0` and subtle drop shadow (blur 8px, opacity 6%).

### Color Palette
| Role | Color Name | Hex Code | Purpose |
| :--- | :--- | :--- | :--- |
| **Primary Accent** | Deep Midnight Navy | `#1E3A8A` | Main headers, Net Sales lines, primary charts |
| **Secondary Accent** | Vibrant Cobalt Blue | `#3B82F6` | Regional charts, interactive selections |
| **Success / Positive**| Emerald Green | `#10B981` | Positive MoM growth, Furniture category |
| **Warning / Amber** | Warm Amber | `#F59E0B` | Units sold, Office Supplies, Order volume |
| **Neutral Dark** | Charcoal Slate | `#0F172A` | KPI values, chart titles |
| **Neutral Muted** | Cool Gray | `#64748B` | Subtitles, axis tick labels, card captions |
| **Neutral Light** | Clean White | `#FFFFFF` | Visual container card backgrounds |

---

## 2. Dashboard Layout Grid

```
+---------------------------------------------------------------------------------------------------------+
| [Header Banner] Sales Performance & Executive Analytics Dashboard      [Date Slicer] [Region] [Category]|
+---------------------------------------------------------------------------------------------------------+
| [KPI 1: Net Sales]   | [KPI 2: Total Orders]  | [KPI 3: Units Sold]   | [KPI 4: AOV]  | [KPI 5: Customers]|
| $4,215,142.88        | 3,592 Orders           | 8,622 Units           | $1,173.48     | 150 Customers     |
+---------------------------------------------------------------------------------------------------------+
| [Visual 1: Monthly Sales & Order Volume Trend]            | [Visual 2: Category Revenue Share]          |
| Multi-year line chart with dual-axis (Revenue $K & Orders)| Donut chart with % contribution & center KPI|
+-----------------------------------------------------------+---------------------------------------------+
| [Visual 3: Top 10 Products by Revenue]                    | [Visual 4: Regional Market Performance]     |
| Horizontal bar chart with data labels & category coloring | Clustered column chart with category split  |
+---------------------------------------------------------------------------------------------------------+
```

---

## 3. Visual Components Specification

### Visual 1: KPI Cards Row (Y: 100px - 220px)
- **Container 1:** `[Total Sales]`
  - Metric: `$4,215,142.88`
  - Sub-label: `vs Prior Month (+8.4%)`
- **Container 2:** `[Total Orders]`
  - Metric: `3,592`
  - Sub-label: `Distinct Order Transactions`
- **Container 3:** `[Total Units Sold]`
  - Metric: `8,622`
  - Sub-label: `Avg 2.40 units/order`
- **Container 4:** `[Average Order Value]`
  - Metric: `$1,173.48`
  - Sub-label: `Net Revenue per Order`
- **Container 5:** `[Total Customers]`
  - Metric: `150`
  - Sub-label: `Active Buyer Accounts`

### Visual 2: Monthly Sales Trajectory (Line Chart)
- **X-Axis:** `DIM_DATE[Year_Month]`
- **Y-Axis (Left):** `[Total Sales]` (Formatted as `$K`)
- **Y-Axis (Right):** `[Total Orders]`
- **Tooltip:** Order Month, Total Sales, Gross Sales, Discounts, Order Count, AOV

### Visual 3: Category Revenue Share (Donut Chart)
- **Legend:** `DIM_PRODUCT[Category]`
- **Values:** `[Total Sales]`
- **Detail Labels:** Category, Data value (`$M`), Percentage of Total (`%`)
- **Center Callout:** Total Portfolio Revenue

### Visual 4: Top 10 Products (Horizontal Bar Chart)
- **Y-Axis:** `DIM_PRODUCT[Product_Name]` (Sorted by `[Total Sales]` descending, Top 10 filter)
- **X-Axis:** `[Total Sales]`
- **Data Labels:** Enabled on outside end (`$K`)
- **Color Saturation:** Category-driven (Technology: Navy, Furniture: Green, Office Supplies: Amber)

### Visual 5: Regional Performance (Bar Chart)
- **X-Axis:** `DIM_LOCATION[Region]`
- **Y-Axis:** `[Total Sales]`
- **Legend:** `DIM_PRODUCT[Category]`
- **Drill-down:** Region -> State -> City

---

## 4. Interactivity & Filter Slicers

1. **Date Range Slicer:** Between slider on `DIM_DATE[Full_Date]`.
2. **Region Slicer:** Horizontal chiclet or dropdown (`Central`, `East`, `South`, `West`).
3. **Category Slicer:** Horizontal chiclet or dropdown (`Technology`, `Furniture`, `Office Supplies`).
4. **Customer Segment Slicer:** Dropdown (`Consumer`, `Corporate`, `Home Office`).
5. **Cross-Filtering:** Selecting any product, category, or region automatically cross-filters all other visuals on the canvas.
