# Isi dari main_etl.py
import etl_conformed
import etl_hr
import etl_sales
import etl_purchasing

if __name__ == "__main__":
    print("=== MEMULAI PROSES ETL GALAXY SCHEMA ===")
    
    # 1. Jalankan Conformed Dimensions DULUAN
    etl_conformed.etl_dim_date()
    etl_conformed.etl_dim_product()
    
    # 2. Jalankan Specific Dimensions (Boleh acak urutannya)
    etl_hr.load_dim_hr()
    etl_sales.load_dim_sales()
    etl_purchasing.load_dim_purchasing()
    
    # 3. Jalankan Fact Tables (Tabel Fakta HARUS TERAKHIR)
    etl_hr.load_fact_hr()
    etl_sales.load_fact_sales()
    etl_purchasing.load_fact_purchasing()
    
    print("=== PROSES ETL SELESAI ===")