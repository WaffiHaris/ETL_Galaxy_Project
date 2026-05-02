import etl_conformed
import etl_hr
import etl_sales
import etl_purchasing

def run_load_dw():
    print("=== FASE 2: TRANSFORM & LOAD (STAGING -> DW) ===")
    
    # 1. Load Conformed Dimensions (Pondasi Galaxy Schema)
    etl_conformed.etl_dim_date()
    etl_conformed.etl_dim_product()
    
    # 2. Load Specific Dimensions
    etl_hr.load_dim_hr()
    etl_sales.load_dim_sales()
    etl_purchasing.load_dim_purchasing()
    
    # 3. Load Fact Tables (Tahap Akhir)
    etl_hr.load_fact_hr()
    etl_sales.load_fact_sales()
    etl_purchasing.load_fact_purchasing()
    
    print("✅ Tahap Load Data Warehouse Selesai. Galaxy Schema siap digunakan!")

if __name__ == "__main__":
    run_load_dw()