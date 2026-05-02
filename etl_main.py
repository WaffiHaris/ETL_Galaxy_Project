import etl_conformed
import etl_hr
import etl_sales
import etl_purchasing

if __name__ == "__main__":
    print("=== MEMULAI PROSES ETL GALAXY SCHEMA ===")
    
    # ---------------------------------------------------------
    # FASE 1: EXTRACT KE STAGING (INI YANG TERLEWAT SEBELUMNYA)
    # ---------------------------------------------------------
    # Fungsi ini yang bertugas membuat tabel stg_employee, dll.
    etl_hr.extract_hr()
    etl_sales.extract_sales()
    etl_purchasing.extract_purchasing()
    
    # ---------------------------------------------------------
    # FASE 2: LOAD CONFORMED DIMENSIONS
    # ---------------------------------------------------------
    etl_conformed.etl_dim_date()
    etl_conformed.etl_dim_product()
    
    # ---------------------------------------------------------
    # FASE 3: LOAD SPECIFIC DIMENSIONS
    # ---------------------------------------------------------
    etl_hr.load_dim_hr()
    etl_sales.load_dim_sales()
    etl_purchasing.load_dim_purchasing()
    
    # ---------------------------------------------------------
    # FASE 4: LOAD FACT TABLES (HARUS TERAKHIR)
    # ---------------------------------------------------------
    etl_hr.load_fact_hr()
    etl_sales.load_fact_sales()
    etl_purchasing.load_fact_purchasing()
    
    print("=== PROSES ETL SELESAI ===")