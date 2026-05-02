import pandas as pd
from sqlalchemy import create_engine

engine_oltp = create_engine("postgresql://postgres:123@localhost:5432/adventureworks")
engine_stg = create_engine("postgresql://postgres:123@localhost:5432/aw_staging_master")
engine_dw = create_engine("postgresql://postgres:123@localhost:5432/aw_dw_galaxy")

def extract_sales():
    print("SALES: Extracting data to Staging...")
    # Customer (Gabungan sederhana untuk contoh, sesuaikan dengan query sales sebenarnya jika lebih kompleks)
    df_cust = pd.read_sql("""
        SELECT c.customerid, p.firstname || ' ' || COALESCE(p.lastname, '') as fullname,
               ea.emailaddress, NULL as gender, NULL as birthdate, NULL as city, NULL as stateprovince, NULL as country
        FROM sales.customer c
        JOIN person.person p ON c.personid = p.businessentityid
        LEFT JOIN person.emailaddress ea ON p.businessentityid = ea.businessentityid
    """, engine_oltp)
    df_cust.columns = [c.lower() for c in df_cust.columns]
    df_cust.to_sql('stg_customer', engine_stg, if_exists='replace', index=False)

    # Territory
    df_terr = pd.read_sql("SELECT territoryid, name as territoryname, countryregioncode as country, \"group\" FROM sales.salesterritory", engine_oltp)
    df_terr.columns = [c.lower() for c in df_terr.columns]
    df_terr.to_sql('stg_territory', engine_stg, if_exists='replace', index=False)

    # Sales Data (Fact Source)
    df_sales = pd.read_sql("""
        SELECT d.productid, h.customerid, h.orderdate, h.territoryid,
               d.orderqty, d.unitprice, d.unitpricediscount, (d.orderqty * d.unitprice) as linetotal,
               h.taxamt, h.freight
        FROM sales.salesorderdetail d
        JOIN sales.salesorderheader h ON d.salesorderid = h.salesorderid
    """, engine_oltp)
    df_sales.columns = [c.lower() for c in df_sales.columns]
    df_sales.to_sql('stg_sales', engine_stg, if_exists='replace', index=False)
    print("SALES: Extraction complete.")

def load_dim_sales():
    print("SALES: Loading Dimensions to DW...")
    pd.read_sql("SELECT * FROM stg_customer", engine_stg).to_sql('dim_customer', engine_dw, if_exists='append', index=False)
    pd.read_sql("SELECT * FROM stg_territory", engine_stg).to_sql('dim_territory', engine_dw, if_exists='append', index=False)
    print("SALES: Dimensions loaded.")

def load_fact_sales():
    print("SALES: Loading Fact Table to DW...")
    df_sales = pd.read_sql("SELECT * FROM stg_sales", engine_stg)
    
    # Ambil Dimensi untuk Lookup
    dim_cust = pd.read_sql("SELECT customerkey, customerid FROM dim_customer", engine_dw)
    dim_terr = pd.read_sql("SELECT territorykey, territoryid FROM dim_territory", engine_dw)
    dim_prod = pd.read_sql("SELECT productkey, productid FROM dim_product", engine_dw) # Conformed Dimension
    
    # Generate DateKey
    df_sales['datekey'] = pd.to_datetime(df_sales['orderdate']).dt.strftime('%Y%m%d').astype(int)
    
    # MERGE Lookup
    df_fact = pd.merge(df_sales, dim_cust, how='inner', on='customerid')
    df_fact = pd.merge(df_fact, dim_terr, how='inner', on='territoryid')
    df_fact = pd.merge(df_fact, dim_prod, how='inner', on='productid')
    
    final_cols = ['datekey', 'customerkey', 'productkey', 'territorykey', 
                  'orderqty', 'unitprice', 'unitpricediscount', 'linetotal', 'taxamt', 'freight']
    df_fact[final_cols].to_sql('fact_sales_online', engine_dw, if_exists='append', index=False)
    print("SALES: Fact Table loaded.")