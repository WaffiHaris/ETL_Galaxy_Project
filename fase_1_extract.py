import etl_hr
import etl_sales
import etl_purchasing

def run_extraction():
    print("=== FASE 1: EXTRACTION (OLTP -> STAGING) ===")
    
    # Menjalankan fungsi extract dari tiap departemen
    etl_hr.extract_hr()
    etl_sales.extract_sales()
    etl_purchasing.extract_purchasing()
    
    print("✅ Tahap Ekstraksi Selesai. Data mentah aman di aw_staging_master.")

if __name__ == "__main__":
    run_extraction()