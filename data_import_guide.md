# 📥 Oracle SQL Data Import & Pipeline Guide

This guide provides end-to-end instructions for loading the cleaned retail sales dataset (`cleaned_sales_data.csv`) into an **Oracle Database (19c / 21c / 23c / Autonomous DB)**.

It covers 4 industry-standard ingestion pathways:
1. **Method 1: Oracle SQL Developer GUI (Recommended for Students & Quick Setup)**
2. **Method 2: High-Performance Oracle SQL\*Loader (`sqlldr`)**
3. **Method 3: Automated Python Script via `python-oracledb`**
4. **Method 4: Star Schema ETL Execution (`POPULATE_STAR_SCHEMA`)**

---

## Prerequisites & Schema Setup

Before importing data, ensure the target tables exist in your Oracle schema.
Open SQL*Plus, SQL Developer, or VS Code Oracle extension and run:

```sql
@sql/create_tables.sql
```
*(Or run `create_tables.sql` in the project root)*

This initializes:
- `STG_RETAIL_SALES`: Direct staging repository matching CSV columns.
- `DIM_CUSTOMER`: Customer dimension table.
- `DIM_PRODUCT`: Product dimension table.
- `DIM_LOCATION`: Geographic dimension table.
- `DIM_DATE`: Date dimension table.
- `FACT_SALES`: Central sales fact table with foreign key constraints.
- `POPULATE_STAR_SCHEMA`: Automated PL/SQL procedure to populate the Star Schema from staging.

---

## Method 1: Oracle SQL Developer Import Wizard (GUI)

This is the easiest method for college viva and interactive demonstrations:

1. Open **Oracle SQL Developer** and connect to your database user.
2. In the left **Connections** navigation tree, expand **Tables**.
3. Right-click on **`STG_RETAIL_SALES`** and click **Import Data...**.
4. In the Data Import Wizard:
   - **Step 1 (Data Preview):** Click **Browse...** and select `data/cleaned_sales_data.csv`.
   - **Format:** Choose `csv`.
   - **Header:** Check `Header` (Column names are in row 1).
   - **Encoding:** `UTF-8`.
   - Click **Next**.
5. **Step 2 (Import Method):**
   - Import Method: `Insert`.
   - Click **Next**.
6. **Step 3 (Choose Columns):**
   - Ensure all columns from `Order_ID` to `Day_of_Week` are selected.
   - Click **Next**.
7. **Step 4 (Column Definition & Mapping):**
   - Verify column mappings. All column names match 1:1.
   - Click **Next**.
8. Click **Finish**.
9. Once the progress bar reaches 100%, run:
   ```sql
   SELECT COUNT(*) FROM STG_RETAIL_SALES;
   ```
   **Expected Count:** Exactly `3,592` rows.

---

## Method 2: High-Performance Oracle SQL*Loader (`sqlldr`)

In production environments, data analysts and ETL engineers use `sqlldr` for bulk loading millions of records in seconds.

### 2.1 The Control File (`retail_sales.ctl`)
Save the following configuration as `sql/retail_sales.ctl`:

```text
LOAD DATA
INFILE 'data/cleaned_sales_data.csv'
INTO TABLE STG_RETAIL_SALES
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
    Order_ID          CHAR(30),
    Order_Date        CHAR(15),
    Product_ID        CHAR(30),
    Product_Name      CHAR(150),
    Category          CHAR(50),
    Sub_Category      CHAR(50),
    Quantity          INTEGER EXTERNAL,
    Unit_Price        DECIMAL EXTERNAL,
    Discount          DECIMAL EXTERNAL,
    Sales_Amount      DECIMAL EXTERNAL,
    Customer_ID       CHAR(30),
    Customer_Name     CHAR(100),
    Customer_Segment  CHAR(50),
    Region            CHAR(50),
    Country           CHAR(50),
    State             CHAR(50),
    City              CHAR(50),
    Payment_Method    CHAR(50),
    Gross_Amount      DECIMAL EXTERNAL,
    Discount_Amount   DECIMAL EXTERNAL,
    Year              INTEGER EXTERNAL,
    Month_Num         INTEGER EXTERNAL,
    Month_Name        CHAR(20),
    Year_Month        CHAR(10),
    Quarter           CHAR(5),
    Day_of_Week       CHAR(15)
)
```

### 2.2 Execute SQL*Loader Command
Run from terminal / command prompt:

```bash
sqlldr userid=sales_user/password@localhost:1521/ORCL control=sql/retail_sales.ctl skip=1 log=sql/retail_sales.log
```

---

## Method 3: Automated Python Script (`oracledb`)

For seamless integration in a Python-to-Oracle pipeline, use the provided script `load_to_oracle.py`.

```python
# load_to_oracle.py
import os
import pandas as pd
import oracledb

# Database connection credentials (adjust to your environment)
DB_USER = os.getenv("ORACLE_USER", "sales_user")
DB_PASSWORD = os.getenv("ORACLE_PASSWORD", "sales_pwd")
DB_DSN = os.getenv("ORACLE_DSN", "localhost:1521/ORCL")

def load_data():
    df = pd.read_csv("data/cleaned_sales_data.csv")
    print(f"Loaded {len(df)} rows from CSV.")

    conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
    cursor = conn.cursor()

    # Truncate staging table
    cursor.execute("TRUNCATE TABLE STG_RETAIL_SALES")

    # Fast batch insert
    records = [tuple(row) for row in df.itertuples(index=False)]
    sql = """
    INSERT INTO STG_RETAIL_SALES (
        Order_ID, Order_Date, Product_ID, Product_Name, Category, Sub_Category,
        Quantity, Unit_Price, Discount, Sales_Amount, Customer_ID, Customer_Name,
        Customer_Segment, Region, Country, State, City, Payment_Method,
        Gross_Amount, Discount_Amount, Year, Month_Num, Month_Name, Year_Month,
        Quarter, Day_of_Week
    ) VALUES (
        :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18,
        :19, :20, :21, :22, :23, :24, :25, :26
    )
    """
    cursor.executemany(sql, records)
    conn.commit()
    print(f"Successfully loaded {len(records)} records into STG_RETAIL_SALES.")

    # Execute Star Schema ETL
    cursor.callproc("POPULATE_STAR_SCHEMA")
    print("Executed POPULATE_STAR_SCHEMA successfully!")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    load_data()
```

---

## Method 4: Populating the Star Schema

Once the staging table `STG_RETAIL_SALES` is loaded with `3,592` rows, transform and populate the dimension and fact tables by calling the stored procedure:

```sql
EXEC POPULATE_STAR_SCHEMA;
```

### Verification & Reconciliation Query:
Run this quick query to confirm everything migrated properly:

```sql
SELECT 
    (SELECT COUNT(*) FROM STG_RETAIL_SALES) AS STG_ROWS,
    (SELECT COUNT(*) FROM FACT_SALES)       AS FACT_ROWS,
    (SELECT COUNT(*) FROM DIM_CUSTOMER)     AS CUST_COUNT,
    (SELECT COUNT(*) FROM DIM_PRODUCT)      AS PROD_COUNT,
    (SELECT COUNT(*) FROM DIM_LOCATION)     AS LOC_COUNT,
    (SELECT COUNT(*) FROM DIM_DATE)         AS DATE_COUNT
FROM DUAL;
```

**Expected Results:**
| STG_ROWS | FACT_ROWS | CUST_COUNT | PROD_COUNT | LOC_COUNT | DATE_COUNT |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **3,592** | **3,592** | **150** | **31** | **17** | **668** |

---

## Common Troubleshooting & FAQ

1. **ORA-01861: Literal does not match format string**
   - Cause: The date string is being read as text in SQL without standard ISO parsing.
   - Fix: Our DDL stores `Order_Date` in staging as `VARCHAR2(15)` and converts it to `DATE` using `TO_DATE(Order_Date, 'YYYY-MM-DD')` inside `POPULATE_STAR_SCHEMA`.

2. **ORA-00001: Unique constraint violated**
   - Cause: Re-running inserts without clearing previous data.
   - Fix: The `POPULATE_STAR_SCHEMA` uses Oracle `MERGE INTO` for dimensions and `TRUNCATE TABLE FACT_SALES` before fact loading to ensure idempotency.

3. **Reconciling Sales Totals:**
   ```sql
   SELECT SUM(Sales_Amount) FROM FACT_SALES;
   ```
   Must yield **`$4,215,142.88`**, identical to Python and Power BI!
