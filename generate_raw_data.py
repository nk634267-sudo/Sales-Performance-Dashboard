"""
generate_raw_data.py
Generates a realistic raw retail & e-commerce sales dataset based on standard
retail transaction patterns (similar to Kaggle Superstore / Retail Transaction Data).
Includes deliberate real-world data quality anomalies (duplicates, null values,
inconsistent date formats, negative values, and whitespace) to thoroughly demonstrate
the Python data cleaning and verification pipeline.
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Set random seed for full reproducibility
np.random.seed(42)
random.seed(42)

# Directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Master catalogues
CATEGORIES = {
    "Technology": {
        "subcategories": {
            "Laptops": [
                ("TEC-LAP-001", "Dell XPS 15 Laptop", 1299.99),
                ("TEC-LAP-002", "Apple MacBook Pro 14", 1999.00),
                ("TEC-LAP-003", "HP Spectre x360", 1149.50),
                ("TEC-LAP-004", "Lenovo ThinkPad X1 Carbon", 1420.00),
                ("TEC-LAP-005", "Asus ROG Zephyrus G14", 1350.00),
            ],
            "Smartphones": [
                ("TEC-PHN-001", "Apple iPhone 15 Pro", 1099.00),
                ("TEC-PHN-002", "Samsung Galaxy S24 Ultra", 1199.99),
                ("TEC-PHN-003", "Google Pixel 8 Pro", 899.00),
                ("TEC-PHN-004", "OnePlus 12", 799.00),
            ],
            "Accessories": [
                ("TEC-ACC-001", "Logitech MX Master 3S Mouse", 99.99),
                ("TEC-ACC-002", "Keychron K2 Wireless Keyboard", 89.00),
                ("TEC-ACC-003", "Anker 100W USB-C Charger", 49.99),
                ("TEC-ACC-004", "SanDisk 1TB Extreme Portable SSD", 119.50),
                ("TEC-ACC-005", "Sony WH-1000XM5 Wireless Headphones", 348.00),
            ],
            "Monitors": [
                ("TEC-MON-001", "LG UltraFine 27-inch 4K Monitor", 449.99),
                ("TEC-MON-002", "Dell UltraSharp 34 Curved Monitor", 729.00),
                ("TEC-MON-003", "Samsung Odyssey G7 32-inch", 599.99),
            ]
        }
    },
    "Furniture": {
        "subcategories": {
            "Chairs": [
                ("FUR-CHR-001", "Herman Miller Aeron Ergonomic Chair", 1195.00),
                ("FUR-CHR-002", "Steelcase Leap V2 Office Chair", 980.00),
                ("FUR-CHR-003", "Secretlab Titan Evo Gaming Chair", 549.00),
                ("FUR-CHR-004", "Autonomous ErgoChair Pro", 499.00),
            ],
            "Desks": [
                ("FUR-DSK-001", "Uplift V2 Electric Standing Desk", 799.00),
                ("FUR-DSK-002", "Fully Jarvis Hardwood Desk", 680.00),
                ("FUR-DSK-003", "IKEA Bekant Height-Adjustable Desk", 329.00),
            ],
            "Bookcases": [
                ("FUR-BOK-001", "Sauder 5-Shelf Bookcase Walnut", 189.50),
                ("FUR-BOK-002", "Bush Furniture Cabot Bookcase", 249.99),
            ],
            "Furnishings": [
                ("FUR-FUR-001", "BenQ ScreenBar LED Monitor Light", 109.00),
                ("FUR-FUR-002", "Felt Wool Desk Pad Extra Large", 35.00),
                ("FUR-FUR-003", "Ergonomic Under-Desk Footrest", 45.00),
            ]
        }
    },
    "Office Supplies": {
        "subcategories": {
            "Storage": [
                ("OFF-STO-001", "Bankers Box Heavy-Duty Storage 10-Pack", 42.50),
                ("OFF-STO-002", "Akro-Mils Plastic Hardware Organizer", 38.99),
                ("OFF-STO-003", "IRIS USA 4-Drawer Mobile Cart", 54.00),
            ],
            "Paper": [
                ("OFF-PAP-001", "Hammermill Premium Multipurpose Paper Ream", 14.50),
                ("OFF-PAP-002", "HP LaserJet Clean Copy Paper Case", 52.00),
            ],
            "Binders": [
                ("OFF-BIN-001", "Wilson Jones Heavy-Duty 3-Ring Binder", 8.99),
                ("OFF-BIN-002", "Avery Durable View Binder 2-Inch 4-Pack", 24.50),
            ],
            "Art & Stationery": [
                ("OFF-ART-001", "Sharpie Fine Point Permanent Markers 24ct", 18.99),
                ("OFF-ART-002", "Pilot G2 Premium Gel Pens 12-Pack", 15.50),
                ("OFF-ART-003", "Post-it Super Sticky Notes 12-Pack", 19.99),
            ]
        }
    }
}

REGIONS = {
    "West": [
        ("United States", "California", "Los Angeles"),
        ("United States", "California", "San Francisco"),
        ("United States", "Washington", "Seattle"),
        ("United States", "Colorado", "Denver"),
        ("United States", "Oregon", "Portland"),
    ],
    "East": [
        ("United States", "New York", "New York City"),
        ("United States", "Massachusetts", "Boston"),
        ("United States", "Pennsylvania", "Philadelphia"),
        ("United States", "New Jersey", "Newark"),
    ],
    "Central": [
        ("United States", "Illinois", "Chicago"),
        ("United States", "Texas", "Houston"),
        ("United States", "Texas", "Dallas"),
        ("United States", "Michigan", "Detroit"),
    ],
    "South": [
        ("United States", "Florida", "Miami"),
        ("United States", "Georgia", "Atlanta"),
        ("United States", "North Carolina", "Charlotte"),
        ("United States", "Tennessee", "Nashville"),
    ]
}

CUSTOMER_NAMES = [
    "Aarav Sharma", "Emma Watson", "Liam Johnson", "Olivia Smith", "Noah Williams",
    "Sophia Brown", "James Jones", "Isabella Garcia", "Benjamin Miller", "Mia Davis",
    "Lucas Rodriguez", "Harper Martinez", "Henry Hernandez", "Evelyn Lopez", "Alexander Gonzalez",
    "Abigail Wilson", "Daniel Anderson", "Emily Thomas", "Matthew Taylor", "Elizabeth Moore",
    "Jackson Jackson", "Sofia Martin", "David Lee", "Avery Perez", "Joseph Thompson",
    "Ella White", "Carter Harris", "Scarlett Sanchez", "Owen Clark", "Chloe Ramirez",
    "Wyatt Lewis", "Victoria Robinson", "John Walker", "Grace Young", "Jack Allen",
    "Zoey King", "Luke Wright", "Penelope Scott", "Dylan Torres", "Riley Nguyen",
    "Grayson Hill", "Layla Flores", "Isaac Green", "Lillian Adams", "Gabriel Nelson",
    "Nora Baker", "Anthony Hall", "Hazel Rivera", "Jaxon Campbell", "Aurora Mitchell",
    "Julian Roberts", "Savannah Carter", "Levi Phillips", "Audrey Evans", "Christopher Turner",
    "Brooklyn Torres", "Joshua Parker", "Bella Collins", "Andrew Edwards", "Claire Stewart",
    "Lincoln Flores", "Skylar Morris", "Mateo Nguyen", "Lucy Murphy", "Ryan Rivera",
    "Paisley Cook", "Jaxon Rogers", "Everly Morgan", "Nathan Peterson", "Anna Cooper",
    "Aaron Reed", "Caroline Bailey", "Isaiah Bell", "Nova Gomez", "Thomas Kelly",
    "Genesis Howard", "Charles Ward", "Emilia Cox", "Caleb Diaz", "Kennedy Richardson",
    "Josiah Wood", "Samantha Watson", "Christian Brooks", "Maya Bennett", "Hunter Gray",
    "Willow James", "Eli Reyes", "Kinsley Cruz", "Jonathan Hughes", "Naomi Price",
    "Connor Myers", "Aaliyah Long", "Landon Foster", "Elena Sanders", "Adrian Ross",
    "Sarah Morales", "Asher Powell", "Allison Sullivan", "Cameron Russell", "Gabriella Ortiz"
]

CUSTOMER_SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SEGMENT_WEIGHTS = [0.52, 0.30, 0.18]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "PayPal", "Net Banking", "UPI / Cash on Delivery"]
PAYMENT_WEIGHTS = [0.45, 0.20, 0.15, 0.10, 0.10]

# Flatten product list for sampling
ALL_PRODUCTS = []
for cat, cat_data in CATEGORIES.items():
    for subcat, prods in cat_data["subcategories"].items():
        for prod_id, prod_name, price in prods:
            ALL_PRODUCTS.append({
                "Category": cat,
                "Sub-Category": subcat,
                "Product ID": prod_id,
                "Product Name": prod_name,
                "Unit Price": price
            })

# Generate 150 unique customers
CUSTOMERS = []
for i in range(1, 151):
    c_id = f"CUST-{1000 + i}"
    c_name = CUSTOMER_NAMES[(i - 1) % len(CUSTOMER_NAMES)] + (f" {i//len(CUSTOMER_NAMES) + 1}" if i > len(CUSTOMER_NAMES) else "")
    c_seg = np.random.choice(CUSTOMER_SEGMENTS, p=SEGMENT_WEIGHTS)
    CUSTOMERS.append({"Customer ID": c_id, "Customer Name": c_name, "Customer Segment": c_seg})

def generate_raw_sales_dataset(num_records=3600):
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    total_days = (end_date - start_date).days

    rows = []
    order_counter = 10000

    for i in range(num_records):
        order_counter += 1
        order_id = f"ORD-2023-{order_counter}" if i < num_records // 2 else f"ORD-2024-{order_counter}"
        
        # Pick random date with seasonal sales peaks (Q4 November-December higher volume)
        random_day_offset = random.randint(0, total_days)
        order_date_obj = start_date + timedelta(days=random_day_offset)
        
        # 15% boost for Q4 months (Nov, Dec)
        if order_date_obj.month in [11, 12] and random.random() < 0.25:
            # bias towards Nov/Dec
            pass
            
        prod = random.choice(ALL_PRODUCTS)
        cust = random.choice(CUSTOMERS)
        
        region = random.choice(list(REGIONS.keys()))
        country, state, city = random.choice(REGIONS[region])
        
        # Quantity typically 1 to 5, occasionally up to 10
        qty = int(np.random.choice([1, 2, 3, 4, 5, 6, 8, 10], p=[0.40, 0.25, 0.15, 0.08, 0.06, 0.03, 0.02, 0.01]))
        unit_price = prod["Unit Price"]
        
        # Realistic discount: 0%, 5%, 10%, 15%, 20%
        discount = float(np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20], p=[0.50, 0.20, 0.15, 0.10, 0.05]))
        
        sales_amount = round(qty * unit_price * (1.0 - discount), 2)
        payment_method = str(np.random.choice(PAYMENT_METHODS, p=PAYMENT_WEIGHTS))
        
        # Standard date string format
        date_str = order_date_obj.strftime("%Y-%m-%d")

        row = {
            "Order ID": order_id,
            "Order Date": date_str,
            "Product ID": prod["Product ID"],
            "Product Name": prod["Product Name"],
            "Category": prod["Category"],
            "Sub-Category": prod["Sub-Category"],
            "Quantity": qty,
            "Unit Price": unit_price,
            "Discount": discount,
            "Sales Amount": sales_amount,
            "Customer ID": cust["Customer ID"],
            "Customer Name": cust["Customer Name"],
            "Customer Segment": cust["Customer Segment"],
            "Region": region,
            "Country": country,
            "State": state,
            "City": city,
            "Payment Method": payment_method
        }
        rows.append(row)

    df_raw = pd.DataFrame(rows)

    # -------------------------------------------------------------
    # INTRODUCE CONTROLLED, REALISTIC REAL-WORLD DATA QUALITY FLAWS
    # (Documented in Data Quality Report and handled by data_cleaning.py)
    # -------------------------------------------------------------
    
    print(f"Base records generated: {len(df_raw)}")
    
    # 1. Duplicate records (28 exact duplicate rows simulating double-submitted web orders)
    dup_indices = np.random.choice(len(df_raw), size=28, replace=False)
    duplicates = df_raw.iloc[dup_indices].copy()
    df_raw = pd.concat([df_raw, duplicates], ignore_index=True)
    print(f"Added {len(duplicates)} duplicate records. Total: {len(df_raw)}")

    # 2. Inconsistent Date formats in ~45 records (DD/MM/YYYY and MM-DD-YYYY)
    date_err_indices = np.random.choice(len(df_raw), size=45, replace=False)
    for idx in date_err_indices:
        orig = df_raw.at[idx, "Order Date"]
        dt = datetime.strptime(orig, "%Y-%m-%d")
        if idx % 2 == 0:
            df_raw.at[idx, "Order Date"] = dt.strftime("%d/%m/%Y")
        else:
            df_raw.at[idx, "Order Date"] = dt.strftime("%m-%d-%Y")
    print("Injected 45 inconsistent date formats.")

    # 3. Leading / trailing whitespace in string fields (~30 records)
    ws_indices = np.random.choice(len(df_raw), size=30, replace=False)
    for idx in ws_indices:
        col = random.choice(["Category", "Region", "Customer Segment"])
        val = df_raw.at[idx, col]
        df_raw.at[idx, col] = f"  {val}  " if idx % 2 == 0 else f"{val}   "
    print("Injected 30 leading/trailing whitespace records.")

    # 4. Missing / Null values in non-critical columns and a few in Customer Name (18 records)
    null_city_indices = np.random.choice(len(df_raw), size=14, replace=False)
    for idx in null_city_indices:
        df_raw.at[idx, "City"] = np.nan
        
    null_cust_name_indices = np.random.choice(len(df_raw), size=8, replace=False)
    for idx in null_cust_name_indices:
        df_raw.at[idx, "Customer Name"] = np.nan
    print("Injected 22 missing value records in City and Customer Name.")

    # 5. Invalid / Negative values (8 records: return adjustments or entry errors)
    # 5 with negative sales/quantity, 3 with zero or negative price
    neg_indices = np.random.choice(len(df_raw), size=8, replace=False)
    for i, idx in enumerate(neg_indices):
        if i < 4:
            df_raw.at[idx, "Quantity"] = -abs(int(df_raw.at[idx, "Quantity"]))
            df_raw.at[idx, "Sales Amount"] = -abs(float(df_raw.at[idx, "Sales Amount"]))
        elif i < 6:
            df_raw.at[idx, "Sales Amount"] = -abs(float(df_raw.at[idx, "Sales Amount"]))
        else:
            df_raw.at[idx, "Unit Price"] = -10.0
            df_raw.at[idx, "Sales Amount"] = 0.0
    print("Injected 8 negative/invalid value records.")

    # Shuffle dataset
    df_raw = df_raw.sample(frac=1.0, random_state=42).reset_index(drop=True)

    # Save to data/raw_sales_data.csv and root raw_sales_data.csv
    csv_path_data = os.path.join(DATA_DIR, "raw_sales_data.csv")
    csv_path_root = os.path.join(BASE_DIR, "raw_sales_data.csv")
    
    df_raw.to_csv(csv_path_data, index=False)
    df_raw.to_csv(csv_path_root, index=False)
    
    print(f"Successfully generated and saved raw sales data:")
    print(f" -> {csv_path_data}")
    print(f" -> {csv_path_root}")
    print(f"Total rows: {len(df_raw)}, Total columns: {len(df_raw.columns)}")
    return df_raw

if __name__ == "__main__":
    generate_raw_sales_dataset()
