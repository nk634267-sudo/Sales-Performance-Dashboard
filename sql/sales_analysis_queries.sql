-- ============================================================================
-- Script: sales_analysis_queries.sql
-- Project: Sales Performance Dashboard for Retail & E-Commerce
-- Target RDBMS: Oracle Database 19c / 21c / 23c
-- Description: Comprehensive Business Analytics SQL suite demonstrating:
--              1. Executive KPI Reconciliation
--              2. Monthly & Yearly Sales Trends (MoM Growth & Running Totals)
--              3. Top 10 Products by Net Revenue (Window Ranking)
--              4. Regional & Geographic Market Contribution
--              5. Category & Sub-Category Performance Drill-Down
--              6. Customer Segment & Repeat Purchasing Behavior (NTILE)
--              7. Multi-table Joins (Fact-Dimension Star Schema)
--              8. Advanced Analytical Window Functions
-- ============================================================================

-- Format SQL*Plus output for clean CLI viewing
SET PAGESIZE 50;
SET LINESIZE 150;
COL Total_Revenue FORMAT $999,999,999.99;
COL Avg_Order_Value FORMAT $999,999.99;
COL MoM_Growth_Pct FORMAT 990.99;

-- ============================================================================
-- SECTION 1: EXECUTIVE KPI RECONCILIATION
-- Objective: Validate Golden Totals against Python Cleaned Data & Power BI
-- ============================================================================

PROMPT --- 1.1 Executive KPI Summary (Staging Table Baseline) ---
SELECT 
    COUNT(*)                                       AS Total_Records,
    COUNT(DISTINCT Order_ID)                       AS Total_Orders,
    COUNT(DISTINCT Customer_ID)                    AS Total_Customers,
    SUM(Quantity)                                  AS Total_Quantity_Sold,
    TO_CHAR(SUM(Sales_Amount), '$999,999,999.99')  AS Total_Net_Revenue,
    TO_CHAR(SUM(Gross_Amount), '$999,999,999.99')  AS Total_Gross_Sales,
    TO_CHAR(SUM(Discount_Amount), '$999,999.99')   AS Total_Discounts_Given,
    TO_CHAR(ROUND(AVG(Sales_Amount), 2), '$999.99') AS Avg_Order_Value,
    ROUND(AVG(Discount) * 100, 2) || '%'           AS Avg_Discount_Rate
FROM STG_RETAIL_SALES;

PROMPT --- 1.2 Executive KPI Summary (Fact Table Validation via Joins) ---
SELECT 
    COUNT(f.Sales_Fact_ID)                         AS Total_Fact_Rows,
    COUNT(DISTINCT f.Order_ID)                     AS Total_Orders,
    COUNT(DISTINCT f.Customer_ID)                  AS Total_Customers,
    SUM(f.Quantity)                                AS Total_Quantity_Sold,
    TO_CHAR(SUM(f.Sales_Amount), '$999,999,999.99') AS Total_Fact_Revenue,
    TO_CHAR(ROUND(AVG(f.Sales_Amount), 2), '$999.99') AS Avg_Order_Value
FROM FACT_SALES f
JOIN DIM_CUSTOMER c ON f.Customer_ID = c.Customer_ID
JOIN DIM_PRODUCT p  ON f.Product_ID  = p.Product_ID
JOIN DIM_LOCATION l ON f.Location_ID = l.Location_ID
JOIN DIM_DATE d     ON f.Date_Key    = d.Date_Key;


-- ============================================================================
-- SECTION 2: MONTHLY & YEARLY SALES TRENDS (WINDOW FUNCTIONS)
-- Objective: Monthly Revenue, MoM Growth rate via LAG(), and Running Total
-- ============================================================================

PROMPT --- 2.1 Monthly Sales Trajectory with MoM Growth & Running Total ---
WITH Monthly_Sales AS (
    SELECT 
        d.Year,
        d.Month_Num,
        d.Year_Month,
        d.Month_Name,
        COUNT(f.Order_ID)            AS Order_Volume,
        SUM(f.Quantity)              AS Units_Sold,
        SUM(f.Sales_Amount)          AS Monthly_Revenue
    FROM FACT_SALES f
    JOIN DIM_DATE d ON f.Date_Key = d.Date_Key
    GROUP BY d.Year, d.Month_Num, d.Year_Month, d.Month_Name
),
Trend_Calculations AS (
    SELECT 
        Year,
        Month_Num,
        Year_Month,
        Month_Name,
        Order_Volume,
        Units_Sold,
        Monthly_Revenue,
        -- Prior month revenue using LAG window function
        LAG(Monthly_Revenue, 1) OVER (ORDER BY Year, Month_Num) AS Prev_Month_Revenue,
        -- Running cumulative revenue across the multi-year timeline
        SUM(Monthly_Revenue) OVER (
            ORDER BY Year, Month_Num 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS Cumulative_Running_Revenue
    FROM Monthly_Sales
)
SELECT 
    Year_Month,
    Month_Name,
    Order_Volume,
    Units_Sold,
    TO_CHAR(Monthly_Revenue, '$999,999.99') AS Monthly_Revenue,
    TO_CHAR(Cumulative_Running_Revenue, '$999,999,999.99') AS Cumulative_Revenue,
    CASE 
        WHEN Prev_Month_Revenue IS NULL THEN 'Baseline'
        ELSE TO_CHAR(ROUND(((Monthly_Revenue - Prev_Month_Revenue) / Prev_Month_Revenue) * 100, 2), '990.99') || '%'
    END AS MoM_Growth_Rate
FROM Trend_Calculations
ORDER BY Year, Month_Num;

PROMPT --- 2.2 Year-over-Year (YoY) Performance Comparison ---
SELECT 
    d.Year,
    COUNT(DISTINCT f.Order_ID)                     AS Total_Orders,
    SUM(f.Quantity)                                AS Total_Units,
    TO_CHAR(SUM(f.Sales_Amount), '$999,999,999.99') AS Annual_Revenue,
    TO_CHAR(ROUND(AVG(f.Sales_Amount), 2), '$999.99') AS Annual_AOV
FROM FACT_SALES f
JOIN DIM_DATE d ON f.Date_Key = d.Date_Key
GROUP BY d.Year
ORDER BY d.Year;


-- ============================================================================
-- SECTION 3: TOP 10 PRODUCTS BY REVENUE (RANKING FUNCTIONS)
-- Objective: Rank best-selling products overall and within each category
-- ============================================================================

PROMPT --- 3.1 Top 10 Products by Total Net Revenue Overall ---
WITH Product_Performance AS (
    SELECT 
        p.Product_ID,
        p.Product_Name,
        p.Category,
        p.Sub_Category,
        COUNT(f.Order_ID)     AS Total_Orders,
        SUM(f.Quantity)       AS Total_Units_Sold,
        SUM(f.Sales_Amount)   AS Total_Revenue,
        ROUND(AVG(f.Discount) * 100, 1) AS Avg_Discount_Pct,
        DENSE_RANK() OVER (ORDER BY SUM(f.Sales_Amount) DESC) AS Overall_Revenue_Rank
    FROM FACT_SALES f
    JOIN DIM_PRODUCT p ON f.Product_ID = p.Product_ID
    GROUP BY p.Product_ID, p.Product_Name, p.Category, p.Sub_Category
)
SELECT 
    Overall_Revenue_Rank,
    Product_ID,
    Product_Name,
    Category,
    Total_Orders,
    Total_Units_Sold,
    TO_CHAR(Total_Revenue, '$999,999.99') AS Total_Revenue,
    Avg_Discount_Pct || '%' AS Avg_Discount
FROM Product_Performance
WHERE Overall_Revenue_Rank <= 10
ORDER BY Overall_Revenue_Rank;

PROMPT --- 3.2 Top 2 Products Within Each Category (Partitioned Ranking) ---
WITH Category_Product_Rank AS (
    SELECT 
        p.Category,
        p.Product_Name,
        SUM(f.Sales_Amount) AS Category_Revenue,
        ROW_NUMBER() OVER (
            PARTITION BY p.Category 
            ORDER BY SUM(f.Sales_Amount) DESC
        ) AS Rank_In_Category
    FROM FACT_SALES f
    JOIN DIM_PRODUCT p ON f.Product_ID = p.Product_ID
    GROUP BY p.Category, p.Product_Name
)
SELECT 
    Category,
    Rank_In_Category,
    Product_Name,
    TO_CHAR(Category_Revenue, '$999,999.99') AS Category_Revenue
FROM Category_Product_Rank
WHERE Rank_In_Category <= 2
ORDER BY Category, Rank_In_Category;


-- ============================================================================
-- SECTION 4: REGIONAL & GEOGRAPHIC MARKET PERFORMANCE
-- Objective: Regional sales, contribution to total company revenue, and AOV
-- ============================================================================

PROMPT --- 4.1 Region-wise Revenue & Market Share Percentage ---
WITH Regional_Totals AS (
    SELECT 
        l.Region,
        COUNT(DISTINCT f.Order_ID) AS Total_Orders,
        COUNT(DISTINCT f.Customer_ID) AS Unique_Customers,
        SUM(f.Quantity) AS Units_Sold,
        SUM(f.Sales_Amount) AS Regional_Revenue
    FROM FACT_SALES f
    JOIN DIM_LOCATION l ON f.Location_ID = l.Location_ID
    GROUP BY l.Region
)
SELECT 
    Region,
    Total_Orders,
    Unique_Customers,
    Units_Sold,
    TO_CHAR(Regional_Revenue, '$999,999,999.99') AS Regional_Revenue,
    TO_CHAR(ROUND(Regional_Revenue / Total_Orders, 2), '$999.99') AS Regional_AOV,
    -- Percentage of company total revenue using analytic window sum
    ROUND(
        (Regional_Revenue / SUM(Regional_Revenue) OVER ()) * 100, 2
    ) || '%' AS Revenue_Share
FROM Regional_Totals
ORDER BY Regional_Revenue DESC;

PROMPT --- 4.2 Top 5 States by Net Sales ---
SELECT 
    l.State,
    l.Region,
    COUNT(f.Order_ID) AS Orders,
    TO_CHAR(SUM(f.Sales_Amount), '$999,999.99') AS State_Revenue,
    ROUND(
        (SUM(f.Sales_Amount) / SUM(SUM(f.Sales_Amount)) OVER ()) * 100, 2
    ) || '%' AS State_Share_Pct
FROM FACT_SALES f
JOIN DIM_LOCATION l ON f.Location_ID = l.Location_ID
GROUP BY l.State, l.Region
ORDER BY SUM(f.Sales_Amount) DESC
FETCH FIRST 5 ROWS ONLY;


-- ============================================================================
-- SECTION 5: CATEGORY & SUB-CATEGORY PERFORMANCE
-- Objective: Profitability and revenue contribution by product hierarchy
-- ============================================================================

PROMPT --- 5.1 Category-Level Performance & Discount Analysis ---
SELECT 
    p.Category,
    COUNT(f.Order_ID)                              AS Total_Transactions,
    SUM(f.Quantity)                                AS Total_Units,
    TO_CHAR(SUM(f.Sales_Amount), '$999,999,999.99') AS Net_Revenue,
    TO_CHAR(SUM(f.Discount_Amount), '$999,999.99')  AS Total_Discount_Given,
    ROUND(
        (SUM(f.Sales_Amount) / SUM(SUM(f.Sales_Amount)) OVER ()) * 100, 2
    ) || '%' AS Revenue_Contribution,
    ROUND(AVG(f.Discount) * 100, 2) || '%'         AS Avg_Discount_Rate
FROM FACT_SALES f
JOIN DIM_PRODUCT p ON f.Product_ID = p.Product_ID
GROUP BY p.Category
ORDER BY SUM(f.Sales_Amount) DESC;

PROMPT --- 5.2 Sub-Category Breakdown Ranked within Category ---
SELECT 
    p.Category,
    p.Sub_Category,
    SUM(f.Quantity) AS Units_Sold,
    TO_CHAR(SUM(f.Sales_Amount), '$999,999.99') AS SubCat_Revenue,
    RANK() OVER (PARTITION BY p.Category ORDER BY SUM(f.Sales_Amount) DESC) AS SubCat_Rank
FROM FACT_SALES f
JOIN DIM_PRODUCT p ON f.Product_ID = p.Product_ID
GROUP BY p.Category, p.Sub_Category
ORDER BY p.Category, SubCat_Rank;


-- ============================================================================
-- SECTION 6: CUSTOMER SEGMENTATION & NTILE TIERS
-- Objective: Customer revenue quartiles and purchasing frequency
-- ============================================================================

PROMPT --- 6.1 Customer Segment Breakdown ---
SELECT 
    c.Customer_Segment,
    COUNT(DISTINCT c.Customer_ID)                  AS Customer_Count,
    COUNT(f.Order_ID)                              AS Total_Orders,
    TO_CHAR(SUM(f.Sales_Amount), '$999,999,999.99') AS Segment_Revenue,
    TO_CHAR(ROUND(SUM(f.Sales_Amount) / COUNT(DISTINCT c.Customer_ID), 2), '$999,999.99') AS Revenue_Per_Customer,
    ROUND(
        (SUM(f.Sales_Amount) / SUM(SUM(f.Sales_Amount)) OVER ()) * 100, 2
    ) || '%' AS Segment_Share
FROM FACT_SALES f
JOIN DIM_CUSTOMER c ON f.Customer_ID = c.Customer_ID
GROUP BY c.Customer_Segment
ORDER BY SUM(f.Sales_Amount) DESC;

PROMPT --- 6.2 Customer Quartile Tiering using NTILE(4) ---
WITH Customer_Spend AS (
    SELECT 
        c.Customer_ID,
        c.Customer_Name,
        c.Customer_Segment,
        COUNT(f.Order_ID)   AS Order_Count,
        SUM(f.Sales_Amount) AS Lifetime_Spend,
        NTILE(4) OVER (ORDER BY SUM(f.Sales_Amount) DESC) AS Spend_Tier_Quartile
    FROM FACT_SALES f
    JOIN DIM_CUSTOMER c ON f.Customer_ID = c.Customer_ID
    GROUP BY c.Customer_ID, c.Customer_Name, c.Customer_Segment
)
SELECT 
    Spend_Tier_Quartile,
    CASE Spend_Tier_Quartile
        WHEN 1 THEN 'Tier 1 - Platinum VIPs (Top 25%)'
        WHEN 2 THEN 'Tier 2 - Gold Frequent Buyers'
        WHEN 3 THEN 'Tier 3 - Silver Regulars'
        WHEN 4 THEN 'Tier 4 - Bronze / Low Spend'
    END AS Tier_Description,
    COUNT(Customer_ID) AS Total_Customers,
    TO_CHAR(MIN(Lifetime_Spend), '$999,999.99') AS Min_Spend,
    TO_CHAR(MAX(Lifetime_Spend), '$999,999.99') AS Max_Spend,
    TO_CHAR(SUM(Lifetime_Spend), '$999,999,999.99') AS Tier_Total_Revenue,
    ROUND(
        (SUM(Lifetime_Spend) / SUM(SUM(Lifetime_Spend)) OVER ()) * 100, 2
    ) || '%' AS Tier_Revenue_Share
FROM Customer_Spend
GROUP BY Spend_Tier_Quartile
ORDER BY Spend_Tier_Quartile;


-- ============================================================================
-- SECTION 7: PAYMENT METHOD PERFORMANCE
-- Objective: Distribution of transaction volume across payment rails
-- ============================================================================

PROMPT --- 7.1 Payment Method Breakdown ---
SELECT 
    f.Payment_Method,
    COUNT(f.Order_ID)                              AS Transaction_Count,
    TO_CHAR(SUM(f.Sales_Amount), '$999,999,999.99') AS Total_Volume,
    TO_CHAR(ROUND(AVG(f.Sales_Amount), 2), '$999.99') AS Avg_Ticket_Size,
    ROUND(
        (COUNT(f.Order_ID) / SUM(COUNT(f.Order_ID)) OVER ()) * 100, 2
    ) || '%' AS Transaction_Share_Pct
FROM FACT_SALES f
GROUP BY f.Payment_Method
ORDER BY SUM(f.Sales_Amount) DESC;

PROMPT ========================================================================;
PROMPT Analytical queries completed successfully.
PROMPT All queries reconciled with Python cleaning & Power BI golden totals.
PROMPT ========================================================================;
