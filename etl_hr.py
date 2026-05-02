import pandas as pd
from sqlalchemy import create_engine

# Konfigurasi Koneksi (Pastikan kredensial sesuai)
engine_oltp = create_engine("postgresql://postgres:1234@localhost:5432/adventureworks")
engine_stg = create_engine("postgresql://postgres:1234@localhost:5432/aw_staging_master")
engine_dw = create_engine("postgresql://postgres:1234@localhost:5432/aw_dw_galaxy")

def extract_hr():
    print("HR: Extracting data to Staging...")
    # Employee
    df_emp = pd.read_sql("""
        SELECT e.businessentityid, p.firstname, p.lastname, e.jobtitle, 
               e.gender, e.maritalstatus, e.birthdate, e.hiredate, e.salariedflag
        FROM humanresources.employee e
        JOIN person.person p ON e.businessentityid = p.businessentityid
    """, engine_oltp)
    df_emp.columns = [c.lower() for c in df_emp.columns] # Standarisasi huruf kecil
    df_emp.to_sql('stg_employee', engine_stg, if_exists='replace', index=False)

    # Department
    df_dept = pd.read_sql("SELECT departmentid, name as departmentname, groupname FROM humanresources.department", engine_oltp)
    df_dept.columns = [c.lower() for c in df_dept.columns]
    df_dept.to_sql('stg_department', engine_stg, if_exists='replace', index=False)

    # Pay History
    df_pay = pd.read_sql("""
        SELECT eph.businessentityid, eph.ratechangedate, eph.rate, eph.payfrequency, edh.departmentid
        FROM humanresources.employeepayhistory eph
        JOIN humanresources.employeedepartmenthistory edh 
          ON eph.businessentityid = edh.businessentityid
         AND eph.ratechangedate BETWEEN edh.startdate AND COALESCE(edh.enddate, '9999-12-31')
    """, engine_oltp)
    df_pay.columns = [c.lower() for c in df_pay.columns]
    df_pay.to_sql('stg_pay', engine_stg, if_exists='replace', index=False)
    print("HR: Extraction complete.")

def load_dim_hr():
    print("HR: Loading Dimensions to DW...")
    df_emp = pd.read_sql("SELECT * FROM stg_employee", engine_stg)
    df_dept = pd.read_sql("SELECT * FROM stg_department", engine_stg)
    
    # Insert ke DW (Surrogate Key akan ter-generate otomatis karena SERIAL)
    df_emp.to_sql('dim_employee', engine_dw, if_exists='append', index=False)
    df_dept.to_sql('dim_department', engine_dw, if_exists='append', index=False)
    print("HR: Dimensions loaded.")

def load_fact_hr():
    print("HR: Loading Fact Table to DW...")
    df_pay = pd.read_sql("SELECT * FROM stg_pay", engine_stg)
    
    # Baca Dimensi dari DW untuk mendapatkan Surrogate Key
    dim_emp = pd.read_sql("SELECT employeekey, businessentityid FROM dim_employee", engine_dw)
    dim_dept = pd.read_sql("SELECT departmentkey, departmentid FROM dim_department", engine_dw)
    
    # Generate DateKey dari ratechangedate
    df_pay['datekey'] = pd.to_datetime(df_pay['ratechangedate']).dt.strftime('%Y%m%d').astype(int)
    
    # Lookup Surrogate Keys menggunakan MERGE (Sangat Cepat)
    df_fact = pd.merge(df_pay, dim_emp, how='inner', on='businessentityid')
    df_fact = pd.merge(df_fact, dim_dept, how='inner', on='departmentid')
    
    # Pilih kolom final sesuai DDL Fact Table
    final_cols = ['employeekey', 'departmentkey', 'datekey', 'rate', 'payfrequency']
    df_fact_final = df_fact[final_cols]
    
    df_fact_final.to_sql('fact_employee_pay_history', engine_dw, if_exists='append', index=False)
    print("HR: Fact Table loaded.")