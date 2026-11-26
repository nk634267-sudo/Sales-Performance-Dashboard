"""
data_cleaning.py
================
Enterprise-grade, modular Python script for cleaning and transforming retail sales data.
Designed for B.Tech Data Analyst portfolio and production data pipeline.

Key Steps:
1. Load raw CSV data.
2. Inspect schema, summary statistics, missing values, and duplicates.
3. Clean strings (strip whitespace, normalize casing).
4. Resolve multiple date formats into standard ISO YYYY-MM-DD.
5. Impute / handle missing values with complete business justifications.
6. Investigate and filter negative / invalid transactions (logged to audit).
7. Feature Engineering (Year, Month, Quarter, Day of Week, Gross Sales, Net Revenue).
8. Reconcile record counts and totals.
9. Save pristine cleaned dataset for Oracle SQL database loading and Power BI.
"""

import os
import sys
import logging
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DataCleaning")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

RAW_DATA_PATH = os.path.join(DATA_DIR, "raw_sales_data.csv")
CLEANED_DATA_PATH = os.path.join(DATA_DIR, "cleaned_sales_data.csv")
AUDIT_LOG_PATH = os.path.join(DATA_DIR, "data_cleaning_audit.csv")

# Also sync paths to root for convenience
ROOT_RAW_PATH = os.path.join(BASE_DIR, "raw_sales_data.csv")
ROOT_CLEANED_PATH = os.path.join(BASE_DIR, "cleaned_sales_data.csv")


def load_raw_data(filepath: str) -> pd.DataFrame:
    """Load raw dataset from CSV and log initial properties."""
    if not os.path.exists(filepath):
        if os.path.exists(ROOT_RAW_PATH):
            filepath = ROOT_RAW_PATH
        else:
            raise FileNotFoundError(f"Raw data file not found at {filepath}")
            
    logger.info("Loading raw dataset from %s", filepath)
    df = pd.read_csv(filepath)
    logger.info("Dataset loaded successfully. Shape: %d rows x %d columns", df.shape[0], df.shape[1])
    return df


def audit_raw_data(df: pd.DataFrame) -> dict:
    """Perform preliminary diagnostic checks on raw data."""
    logger.info("--- START PRE-CLEANING AUDIT ---")
    audit_stats = {
        "initial_row_count": len(df),
        "initial_column_count": len(df.columns),
        "exact_duplicates": int(df.duplicated().sum()),
        "missing_values_by_col": df.isnull().sum().to_dict(),
        "negative_sales": int((df["Sales Amount"] < 0).sum()) if "Sales Amount" in df else 0,
        "negative_quantity": int((df["Quantity"] < 0).sum()) if "Quantity" in df else 0,
        "zero_or_negative_price": int((df["Unit Price"] <= 0).sum()) if "Unit Price" in df else 0,
    }
    
    logger.info("Total Rows: %d", audit_stats["initial_row_count"])
    logger.info("Exact Duplicates Found: %d", audit_stats["exact_duplicates"])
    
    missing_cols = {k: v for k, v in audit_stats["missing_values_by_col"].items() if v > 0}
    logger.info("Columns with Missing Values: %s", missing_cols)
    logger.info("Negative Sales Records: %d", audit_stats["negative_sales"])
    logger.info("Negative Quantity Records: %d", audit_stats["negative_quantity"])
    logger.info("Non-positive Unit Price Records: %d", audit_stats["zero_or_negative_price"])
    logger.info("--- END PRE-CLEANING AUDIT ---")
    return audit_stats


def clean_sales_data(df_raw: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    """
    Execute full cleaning pipeline according to business analyst requirements.
    Returns:
        df_clean: Pristine DataFrame ready for Oracle SQL and Power BI.
        audit_records: DataFrame containing logged excluded/altered records.
    """
    df = df_raw.copy()
    audit_trail = []

    # 1. REMOVE EXACT DUPLICATES
    initial_len = len(df)
    duplicates = df[df.duplicated(keep="first")]
    for _, row in duplicates.iterrows():
        audit_trail.append({
            "Order_ID": row.get("Order ID", "N/A"),
            "Reason": "Exact Duplicate Transaction Removed",
            "Action": "Dropped"
        })
    df = df.drop_duplicates(keep="first").reset_index(drop=True)
    logger.info("Step 1 [Duplicates]: Dropped %d duplicate rows. Rows remaining: %d", initial_len - len(df), len(df))

    # 2. STRIP LEADING & TRAILING WHITESPACE FROM STRING COLUMNS
    str_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
        # Replace string 'nan' with actual NaN
        df[col] = df[col].replace({"nan": np.nan, "": np.nan})
    logger.info("Step 2 [Whitespace]: Normalized text and trimmed whitespace across %d columns.", len(str_cols))

    # 3. STANDARDIZE DATES
    # The dataset has mixed formats: YYYY-MM-DD, DD/MM/YYYY, MM-DD-YYYY
    logger.info("Step 3 [Dates]: Standardizing date format to ISO YYYY-MM-DD...")
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="mixed", errors="coerce")
    invalid_dates = df["Order Date"].isnull().sum()
    if invalid_dates > 0:
        logger.warning("Found %d unparseable dates! Dropping them.", invalid_dates)
        df = df.dropna(subset=["Order Date"]).reset_index(drop=True)
    
    # 4. HANDLE MISSING VALUES
    # (a) Customer Name: Impute from known Customer ID lookup if available, else 'Valued Customer'
    cust_map = df.dropna(subset=["Customer Name"]).groupby("Customer ID")["Customer Name"].first().to_dict()
    missing_cust_count = df["Customer Name"].isnull().sum()
    if missing_cust_count > 0:
        logger.info("Step 4a [Missing Customers]: Imputing %d missing Customer Names via Customer ID lookup.", missing_cust_count)
        df["Customer Name"] = df["Customer Name"].fillna(df["Customer ID"].map(cust_map))
        df["Customer Name"] = df["Customer Name"].fillna("Valued Customer")

    # (b) City: Impute from known State default / mode
    missing_city_count = df["City"].isnull().sum()
    if missing_city_count > 0:
        logger.info("Step 4b [Missing Cities]: Imputing %d missing City values using State mode.", missing_city_count)
        state_city_mode = df.dropna(subset=["City"]).groupby("State")["City"].agg(lambda x: x.mode()[0]).to_dict()
        df["City"] = df["City"].fillna(df["State"].map(state_city_mode))
        df["City"] = df["City"].fillna("Metro Area")

    # 5. INVESTIGATE & HANDLE INVALID / NEGATIVE TRANSACTIONS
    # Real-world explanation: Negative sales or quantities represent returns / chargebacks.
    # For a sales performance & revenue dashboard, returns are logged into an audit table
    # so we analyze clean completed sales transactions.
    invalid_mask = (
        (df["Quantity"] <= 0) | 
        (df["Sales Amount"] <= 0) | 
        (df["Unit Price"] <= 0)
    )
    invalid_rows = df[invalid_mask]
    for _, row in invalid_rows.iterrows():
        audit_trail.append({
            "Order_ID": row.get("Order ID", "N/A"),
            "Reason": f"Invalid Value: Qty={row.get('Quantity')}, Price={row.get('Unit Price')}, Sales={row.get('Sales Amount')}",
            "Action": "Excluded from Core Sales (Moved to Returns/Audit Log)"
        })
    df_clean = df[~invalid_mask].copy().reset_index(drop=True)
    logger.info("Step 5 [Invalid/Negative Values]: Excluded %d records with non-positive values. Remaining: %d", len(invalid_rows), len(df_clean))

    # 6. FEATURE ENGINEERING & RECALCULATION
    # Ensure Sales Amount strictly equals Quantity * Unit Price * (1 - Discount)
    df_clean["Unit Price"] = df_clean["Unit Price"].astype(float).round(2)
    df_clean["Discount"] = df_clean["Discount"].astype(float).round(2)
    df_clean["Quantity"] = df_clean["Quantity"].astype(int)
    
    # Gross Sales
    df_clean["Gross Amount"] = (df_clean["Quantity"] * df_clean["Unit Price"]).round(2)
    # Discount Amount
    df_clean["Discount Amount"] = (df_clean["Gross Amount"] * df_clean["Discount"]).round(2)
    # Net Sales / Revenue
    df_clean["Sales Amount"] = (df_clean["Gross Amount"] - df_clean["Discount Amount"]).round(2)

    # Date dimensional attributes
    df_clean["Year"] = df_clean["Order Date"].dt.year
    df_clean["Month_Num"] = df_clean["Order Date"].dt.month
    df_clean["Month_Name"] = df_clean["Order Date"].dt.strftime("%B")
    df_clean["Year_Month"] = df_clean["Order Date"].dt.strftime("%Y-%m")
    df_clean["Quarter"] = "Q" + df_clean["Order Date"].dt.quarter.astype(str)
    df_clean["Day_of_Week"] = df_clean["Order Date"].dt.strftime("%A")
    df_clean["Order Date"] = df_clean["Order Date"].dt.strftime("%Y-%m-%d")

    # Rename / align columns for database import
    df_clean.columns = [c.strip().replace(" ", "_").replace("-", "_") for c in df_clean.columns]
    
    audit_df = pd.DataFrame(audit_trail)
    return df_clean, audit_df


def save_cleaned_data(df_clean: pd.DataFrame, audit_df: pd.DataFrame):
    """Save cleaned datasets to both data/ directory and project root."""
    df_clean.to_csv(CLEANED_DATA_PATH, index=False)
    df_clean.to_csv(ROOT_CLEANED_PATH, index=False)
    audit_df.to_csv(AUDIT_LOG_PATH, index=False)
    
    logger.info("Cleaned dataset successfully saved:")
    logger.info(" -> %s", CLEANED_DATA_PATH)
    logger.info(" -> %s", ROOT_CLEANED_PATH)
    logger.info("Audit log saved to: %s", AUDIT_LOG_PATH)
    
    # Print Executive Summary for immediate reconciliation
    total_revenue = df_clean["Sales_Amount"].sum()
    total_orders = df_clean["Order_ID"].nunique()
    total_qty = df_clean["Quantity"].sum()
    total_customers = df_clean["Customer_ID"].nunique()
    aov = total_revenue / total_orders if total_orders else 0
    
    print("\n" + "="*55)
    print("      DATA CLEANING SUMMARY & RECONCILIATION BASELINE")
    print("="*55)
    print(f"Cleaned Row Count      : {len(df_clean):,}")
    print(f"Total Unique Orders    : {total_orders:,}")
    print(f"Total Unique Customers : {total_customers:,}")
    print(f"Total Quantity Sold    : {total_qty:,}")
    print(f"Total Net Revenue      : ${total_revenue:,.2f}")
    print(f"Average Order Value    : ${aov:,.2f}")
    print("="*55 + "\n")


def main():
    logger.info("Starting Sales Data Cleaning Pipeline...")
    df_raw = load_raw_data(RAW_DATA_PATH)
    audit_raw_data(df_raw)
    df_clean, audit_df = clean_sales_data(df_raw)
    save_cleaned_data(df_clean, audit_df)
    logger.info("Data cleaning pipeline completed successfully!")


if __name__ == "__main__":
    main()
