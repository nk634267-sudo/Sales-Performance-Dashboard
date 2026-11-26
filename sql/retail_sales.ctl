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
