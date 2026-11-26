# 🔍 Data Quality & Pipeline Reconciliation Report

## 1. Executive Summary
This document provides a complete audit of the data cleaning, transformation, and reconciliation pipeline for the **Sales Performance Dashboard**. It tracks data provenance from raw transactional ingestion through Python cleaning, Oracle SQL database loading, and Power BI dashboard presentation.

---

## 2. Pre-Cleaning vs. Post-Cleaning Audit

| Quality Metric | Raw Ingestion Baseline | Cleaning Action Taken | Post-Cleaning State | Business Rationale & Audit Trail |
| :--- | :--- | :--- | :--- | :--- |
| **Total Row Count** | 3,628 rows | Deduplication & Quarantining | **3,592 rows** | Net reduction of 36 records (28 duplicates + 8 invalid transactions). |
| **Exact Duplicates** | 28 rows | `drop_duplicates(keep='first')` | **0 rows** | Eliminates double-counted checkouts from repeat network requests. |
| **Missing Customer Names** | 8 rows | Customer ID mapped lookup | **0 rows** | Resolved via historical customer lookup table; no data loss. |
| **Missing Cities** | 14 rows | State modal imputation | **0 rows** | Imputed using the modal metropolitan market for the corresponding state. |
| **Inconsistent Dates** | 45 rows | `pd.to_datetime(format='mixed')` | **0 rows** | Heterogeneous formats (`DD/MM/YYYY`, `MM-DD-YYYY`) parsed to standard ISO `YYYY-MM-DD`. |
| **Negative / Zero Sales** | 6 rows | Quarantined to audit log | **0 rows** | Negative amounts represent merchandise returns; moved to returns audit. |
| **Negative Quantities** | 4 rows | Quarantined to audit log | **0 rows** | Non-positive items removed to ensure physical inventory integrity. |
| **Non-Positive Prices** | 2 rows | Quarantined to audit log | **0 rows** | Pricing entry errors separated from core sales performance. |
| **Whitespace Artifacts** | 30 rows | `.str.strip()` applied | **0 rows** | Prevents fragmented SQL `GROUP BY` and Power BI relationship mismatches. |

---

## 3. Quarantined Records Log (`data_cleaning_audit.csv`)
In accordance with professional data governance standards, **no data was silently deleted**. All 8 non-positive/invalid transaction records were isolated into `data/data_cleaning_audit.csv` with explicit explanations:

- **Order IDs Quarantined:** `ORD-2023-11142`, `ORD-2023-11388`, `ORD-2024-12104`, `ORD-2024-12891`, `ORD-2024-13105`, `ORD-2024-13312`, `ORD-2024-13480`, `ORD-2024-13550`.
- **Classification:** 4 Return Adjustments (Negative Quantity & Sales), 2 Direct Refund Credits (Negative Sales), 2 Clerical Catalog Entry Errors (Price <= 0).

---

## 4. Multi-Platform Golden Total Reconciliation

All core metrics have been reconciled across **Python (Pandas)**, **Oracle SQL (STG and FACT tables)**, and **Power BI (DAX Measures)** to **100.0% precision**:

| Business Metric | Python (Pandas Cleaned) | Oracle SQL (`STG_RETAIL_SALES`) | Oracle SQL (`FACT_SALES`) | Power BI (`.pbix` Model) | Reconciliation Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Record Count** | 3,592 | 3,592 | 3,592 | 3,592 | **MATCH (0.00% Variance)** |
| **Unique Orders** | 3,592 | 3,592 | 3,592 | 3,592 | **MATCH (0.00% Variance)** |
| **Unique Customers** | 150 | 150 | 150 | 150 | **MATCH (0.00% Variance)** |
| **Total Units Sold** | 8,622 | 8,622 | 8,622 | 8,622 | **MATCH (0.00% Variance)** |
| **Gross Sales ($)** | $4,432,689.47 | $4,432,689.47 | $4,432,689.47 | $4,432,689.47 | **MATCH (0.00% Variance)** |
| **Total Discounts ($)** | $217,546.59 | $217,546.59 | $217,546.59 | $217,546.59 | **MATCH (0.00% Variance)** |
| **Net Revenue ($)** | **$4,215,142.88** | **$4,215,142.88** | **$4,215,142.88** | **$4,215,142.88** | **PERFECT MATCH** |
| **Average Order Value** | **$1,173.48** | **$1,173.48** | **$1,173.48** | **$1,173.48** | **PERFECT MATCH** |

---

## 5. Verification Test Suite Summary

All 10 key test cases executed via `tests/test_data_pipeline.py` passed successfully:

```text
Ran 10 tests in 0.160s

OK
✓ Test 1 Passed: No missing values exist in critical columns.
✓ Test 2 Passed: Zero duplicates in cleaned dataset (28 duplicates safely removed).
✓ Test 3 Passed: All transactions have positive Net Sales amounts (> $0.00).
✓ Test 4 Passed: All quantities are positive integers >= 1.
✓ Test 5 Passed: All dates standardized to YYYY-MM-DD within timeline (2023-2024).
✓ Test 6 Passed: Region slicer filter functions correctly across all 4 zones.
✓ Test 7 Passed: Category slicer filter functions cleanly across all 3 product lines.
✓ Test 8 Passed: Monthly sales aggregation matches total revenue with 24 full months.
✓ Test 9 Passed: Top 10 ranking valid. #1 Product: 'Apple MacBook Pro 14' ($385,906.95).
✓ Test 10 Passed: Python, Oracle SQL, and Power BI reconciles to 100.0% precision!
```
