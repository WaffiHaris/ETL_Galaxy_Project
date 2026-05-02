import pandas as pd
from sqlalchemy import create_engine

# ==========================================
# 1. SETUP KONEKSI DATABASE (SQLAlchemy)
# ==========================================
# Ganti dengan kredensial PostgreSQL kalian yang sudah disepakati
# Format: postgresql://username:password@host:port/database_name

engine_oltp = create_engine("postgresql://postgres:1234@localhost:5432/adventureworks")
engine_stg = create_engine("postgresql://postgres:1234@localhost:5432/aw_staging_master")
engine_dw = create_engine("postgresql://postgres:1234@localhost:5432/aw_dw_galaxy")

# ==========================================
# 2. ETL DIMENSI PRODUCT
# ==========================================
def etl_dim_product():
    print("Mulai proses ETL Conformed Dimension: PRODUCT...")
    
    # EXTRACT & TRANSFORM DARI OLTP
    # Mengambil gabungan atribut yang dibutuhkan Sales dan Purchasing
    query_product = """
    SELECT 
        p.productid, 
        p.name as productname, 
        p.productnumber, 
        COALESCE(p.color, 'No Color') as color, 
        p.size, 
        p.productline, 
        p.class, 
        p.style, 
        p.standardcost, 
        p.listprice,
        ps.name as subcategory,
        pc.name as category
    FROM production.product p
    LEFT JOIN production.productsubcategory ps ON p.productsubcategoryid = ps.productsubcategoryid
    LEFT JOIN production.productcategory pc ON ps.productcategoryid = pc.productcategoryid
    """
    
    df_product = pd.read_sql(query_product, engine_oltp)
    
    # LOAD KE STAGING
    df_product.to_sql('stg_product', engine_stg, if_exists='replace', index=False)
    
    # LOAD DARI STAGING KE DATA WAREHOUSE
    # Note: Di DW, pastikan tabel dim_product punya kolom 'productkey' bertipe SERIAL (Auto Increment) sebagai Primary Key
    df_product_stg = pd.read_sql("SELECT * FROM stg_product", engine_stg)
    df_product_stg.to_sql('dim_product', engine_dw, if_exists='append', index=False)
    
    print("✅ Dimensi Product berhasil di-load ke Data Warehouse!")

# ==========================================
# 3. ETL DIMENSI DATE
# ==========================================
def etl_dim_date():
    print("Mulai proses ETL Conformed Dimension: DATE...")
    
    # EXTRACT TANGGAL DARI 3 DEPARTEMEN BERBEDA DI OLTP
    query_hr_dates = "SELECT ratechangedate AS raw_date FROM humanresources.employeepayhistory"
    query_sales_dates = "SELECT orderdate AS raw_date FROM sales.salesorderheader"
    query_purchasing_dates = "SELECT orderdate AS raw_date FROM purchasing.purchaseorderheader"
    
    df_hr = pd.read_sql(query_hr_dates, engine_oltp)
    df_sales = pd.read_sql(query_sales_dates, engine_oltp)
    df_purchasing = pd.read_sql(query_purchasing_dates, engine_oltp)
    
    # TRANSFORM: Gabungkan semua, jadikan datetime, dan hapus duplikat
    df_all_dates = pd.concat([df_hr, df_sales, df_purchasing])
    df_all_dates['raw_date'] = pd.to_datetime(df_all_dates['raw_date']).dt.date # Ambil tanggalnya saja
    df_unique_dates = df_all_dates.drop_duplicates().dropna().reset_index(drop=True)
    
    # TRANSFORM: Ekstrak komponen kalender
    df_date = pd.DataFrame()
    df_date['fulldate'] = pd.to_datetime(df_unique_dates['raw_date'])
    df_date['datekey'] = df_date['fulldate'].dt.strftime('%Y%m%d').astype(int)
    df_date['year'] = df_date['fulldate'].dt.year
    df_date['quarter'] = df_date['fulldate'].dt.quarter
    df_date['monthnum'] = df_date['fulldate'].dt.month
    df_date['monthname'] = df_date['fulldate'].dt.month_name()
    df_date['day'] = df_date['fulldate'].dt.day
    df_date['dayofweek'] = df_date['fulldate'].dt.day_name()
    
    # LOAD KE STAGING
    df_date.to_sql('stg_date', engine_stg, if_exists='replace', index=False)
    
    # LOAD DARI STAGING KE DATA WAREHOUSE
    # Susun ulang kolom agar datekey di depan
    df_date_dw = df_date[['datekey', 'fulldate', 'year', 'quarter', 'monthnum', 'monthname', 'day', 'dayofweek']]
    
    # Menggunakan if_exists='append' agar tidak menghapus struktur tabel DW yang sudah disiapkan primary key-nya
    df_date_dw.to_sql('dim_date', engine_dw, if_exists='append', index=False)
    
    print("✅ Dimensi Date berhasil di-load ke Data Warehouse!")

# ==========================================
# 4. EKSEKUSI UTAMA
# ==========================================
if __name__ == "__main__":
    etl_dim_product()
    etl_dim_date()