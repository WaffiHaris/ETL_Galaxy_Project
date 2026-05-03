-- ==============================================================================
-- 0. BUAT DATABASE (Jalankan blok ini saja terlebih dahulu)
-- ==============================================================================
CREATE DATABASE aw_staging_master;
CREATE DATABASE aw_dw_galaxy;

-- ******************************************************************************
-- BERHENTI DI SINI! 
-- Jangan di-run sekaligus.
-- Buka "New SQL script" yang terkoneksi khusus ke database 'aw_dw_galaxy' 
-- sebelum menjalankan baris-baris di bawah ini.
-- ******************************************************************************

-- ==============================================================================
-- 1. CONFORMED DIMENSIONS (Dimensi Bersama)
-- ==============================================================================

CREATE TABLE dim_date (
    DateKey INT PRIMARY KEY, 
    FullDate DATE,
    Year INT,
    Quarter INT,
    MonthNum INT,
    MonthName VARCHAR(50),
    Day INT,
    DayOfWeek VARCHAR(50)
);

CREATE TABLE dim_product (
    ProductKey SERIAL PRIMARY KEY, 
    ProductID INT,
    ProductName VARCHAR(255),
    ProductNumber VARCHAR(100),
    Color VARCHAR(50),
    Size VARCHAR(50),
    ProductLine VARCHAR(50),
    Class VARCHAR(50),
    Style VARCHAR(50),
    StandardCost NUMERIC(19,2),
    ListPrice NUMERIC(19,2),
    SubCategory VARCHAR(100),
    Category VARCHAR(100)
);

-- ==============================================================================
-- 2. SPECIFIC DIMENSIONS (Dimensi Masing-Masing Departemen)
-- ==============================================================================

-- --- Dimensi HR ---
CREATE TABLE dim_department (
    DepartmentKey SERIAL PRIMARY KEY,
    DepartmentID INT,
    DepartmentName VARCHAR(100),
    GroupName VARCHAR(100)
);

CREATE TABLE dim_employee (
    EmployeeKey SERIAL PRIMARY KEY,
    BusinessEntityID INT,
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    JobTitle VARCHAR(100),
    Gender VARCHAR(10),
    MaritalStatus VARCHAR(10),
    BirthDate DATE,
    HireDate DATE,
    SalariedFlag BOOLEAN
);

-- --- Dimensi Sales Online ---
CREATE TABLE dim_customer (
    CustomerKey SERIAL PRIMARY KEY,
    CustomerID INT,
    FullName VARCHAR(255),
    EmailAddress VARCHAR(255),
    Gender VARCHAR(10),
    BirthDate DATE,
    City VARCHAR(100),
    StateProvince VARCHAR(100),
    Country VARCHAR(100)
);

CREATE TABLE dim_territory (
    TerritoryKey SERIAL PRIMARY KEY,
    TerritoryID INT,
    TerritoryName VARCHAR(100),
    Region VARCHAR(100),
    Country VARCHAR(100),
    TerritoryGroup VARCHAR(100) -- Sudah diganti dari "Group" menjadi TerritoryGroup
);

-- --- Dimensi Purchasing ---
CREATE TABLE dim_vendor (
    VendorKey SERIAL PRIMARY KEY,
    BusinessEntityID INT,
    VendorName VARCHAR(255),
    AccountNumber VARCHAR(100),
    CreditRating INT,
    ActiveFlag INT
);

CREATE TABLE dim_ship_method (
    ShipMethodKey SERIAL PRIMARY KEY,
    ShipMethodID INT,
    Name VARCHAR(100),
    ShipBase NUMERIC(19,2),
    ShipRate NUMERIC(19,2)
);

-- ==============================================================================
-- 3. FACT TABLES (Tabel Fakta)
-- ==============================================================================

-- --- Fact Table HR ---
CREATE TABLE fact_employee_pay_history (
    FactPayID SERIAL PRIMARY KEY,
    EmployeeKey INT,
    DepartmentKey INT,
    DateKey INT,
    Rate NUMERIC(19,4),
    PayFrequency INT,
    
    -- Foreign Keys
    FOREIGN KEY (EmployeeKey) REFERENCES dim_employee(EmployeeKey),
    FOREIGN KEY (DepartmentKey) REFERENCES dim_department(DepartmentKey),
    FOREIGN KEY (DateKey) REFERENCES dim_date(DateKey)
);

-- --- Fact Table Sales Online ---
CREATE TABLE fact_sales_online (
    SalesKey SERIAL PRIMARY KEY,
    DateKey INT,
    CustomerKey INT,
    ProductKey INT,
    TerritoryKey INT,
    OrderQty INT,
    UnitPrice NUMERIC(19,4),
    UnitPriceDiscount NUMERIC(19,4),
    LineTotal NUMERIC(19,4),
    TaxAmt NUMERIC(19,4),
    Freight NUMERIC(19,4),
    
    -- Foreign Keys
    FOREIGN KEY (DateKey) REFERENCES dim_date(DateKey),
    FOREIGN KEY (CustomerKey) REFERENCES dim_customer(CustomerKey),
    FOREIGN KEY (ProductKey) REFERENCES dim_product(ProductKey),
    FOREIGN KEY (TerritoryKey) REFERENCES dim_territory(TerritoryKey)
);

-- --- Fact Table Purchasing ---
CREATE TABLE fact_purchasing (
    FactPurchasingID SERIAL PRIMARY KEY,
    ProductKey INT,
    VendorKey INT,
    ShipMethodKey INT,
    DateKey INT,
    OrderQty INT,
    UnitPrice NUMERIC(19,4),
    LineTotal NUMERIC(19,4),
    ReceivedQty INT,
    RejectedQty INT,
    StockedQty INT,
    TaxAmt NUMERIC(19,4),
    Freight NUMERIC(19,4),
    
    -- Foreign Keys
    FOREIGN KEY (ProductKey) REFERENCES dim_product(ProductKey),
    FOREIGN KEY (VendorKey) REFERENCES dim_vendor(VendorKey),
    FOREIGN KEY (ShipMethodKey) REFERENCES dim_ship_method(ShipMethodKey),
    FOREIGN KEY (DateKey) REFERENCES dim_date(DateKey)
);