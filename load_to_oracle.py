"""
load_to_oracle.py
Automated Python script to load cleaned_sales_data.csv into Oracle SQL database
using the modern python-oracledb driver.
"""

import os
import sys
import pandas as pd

try:
    import oracledb
except ImportError:
    print("Notice: 'oracledb' library is not currently installed.")
    print("To install: pip install oracledb")
    oracledb = None

DB_USER = os.getenv("ORACLE_USER", "system")
DB_PASSWORD = os.getenv("ORACLE_PASSWORD", "oracle")
DB_DSN = os.getenv("ORACLE_DSN", "localhost:1521/XE")

def load_data():
    if oracledb is None:
        print("Please install oracledb before running this loader.")
        return

    csv_path = "data/cleaned_sales_data.csv"
    if not os.path.exists(csv_path):
        csv_path = "cleaned_sales_data.csv"
        
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from {csv_path}.")

    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = conn.cursor()

        print("Connected to Oracle Database. Truncating STG_RETAIL_SALES...")
        cursor.execute("TRUNCATE TABLE STG_RETAIL_SALES")

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

        print("Executing POPULATE_STAR_SCHEMA stored procedure...")
        cursor.callproc("POPULATE_STAR_SCHEMA")
        print("Star schema populated successfully!")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Oracle connection / load error: {e}")

if __name__ == "__main__":
    load_data()
