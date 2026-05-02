import pandas as pd
from sqlalchemy import create_engine

engine_oltp = create_engine("postgresql://postgres:1234@localhost:5432/adventureworks")
engine_stg = create_engine("postgresql://postgres:1234@localhost:5432/aw_staging_master")
engine_dw = create_engine("postgresql://postgres:1234@localhost:5432/aw_dw_galaxy")

def extract_purchasing():
    print("PURCHASING: Extracting data to Staging...")
    # Vendor
    df_vendor = pd.read_sql("SELECT businessentityid, name as vendorname, accountnumber, creditrating, activeflag FROM purchasing.vendor", engine_oltp)
    df_vendor.columns = [c.lower() for c in df_vendor.columns]
    df_vendor.to_sql('stg_vendor', engine_stg, if_exists='replace', index=False)

    # Ship Method
    df_ship = pd.read_sql("SELECT shipmethodid, name, shipbase, shiprate FROM purchasing.shipmethod", engine_oltp)
    df_ship.columns = [c.lower() for c in df_ship.columns]
    df_ship.to_sql('stg_shipmethod', engine_stg, if_exists='replace', index=False)

    # Purchasing Data (Fact Source)
    df_purch = pd.read_sql("""
        SELECT d.productid, h.vendorid as businessentityid, h.shipmethodid, h.orderdate, 
               d.orderqty, d.unitprice, (d.orderqty * d.unitprice) as linetotal, 
               d.receivedqty, d.rejectedqty, (d.receivedqty - d.rejectedqty) as stockedqty, 
               h.taxamt, h.freight
        FROM purchasing.purchaseorderheader h
        JOIN purchasing.purchaseorderdetail d ON h.purchaseorderid = d.purchaseorderid
    """, engine_oltp)
    df_purch.columns = [c.lower() for c in df_purch.columns]
    df_purch.to_sql('stg_purchasing', engine_stg, if_exists='replace', index=False)
    print("PURCHASING: Extraction complete.")

def load_dim_purchasing():
    print("PURCHASING: Loading Dimensions to DW...")
    pd.read_sql("SELECT * FROM stg_vendor", engine_stg).to_sql('dim_vendor', engine_dw, if_exists='append', index=False)
    pd.read_sql("SELECT * FROM stg_shipmethod", engine_stg).to_sql('dim_ship_method', engine_dw, if_exists='append', index=False)
    print("PURCHASING: Dimensions loaded.")

def load_fact_purchasing():
    print("PURCHASING: Loading Fact Table to DW...")
    df_purch = pd.read_sql("SELECT * FROM stg_purchasing", engine_stg)
    
    # Ambil Dimensi untuk Lookup
    dim_vendor = pd.read_sql("SELECT vendorkey, businessentityid FROM dim_vendor", engine_dw)
    dim_ship = pd.read_sql("SELECT shipmethodkey, shipmethodid FROM dim_ship_method", engine_dw)
    dim_prod = pd.read_sql("SELECT productkey, productid FROM dim_product", engine_dw) # Conformed Dimension
    
    # Generate DateKey
    df_purch['datekey'] = pd.to_datetime(df_purch['orderdate']).dt.strftime('%Y%m%d').astype(int)
    
    # MERGE Lookup
    df_fact = pd.merge(df_purch, dim_vendor, how='inner', on='businessentityid')
    df_fact = pd.merge(df_fact, dim_ship, how='inner', on='shipmethodid')
    df_fact = pd.merge(df_fact, dim_prod, how='inner', on='productid')
    
    final_cols = ['productkey', 'vendorkey', 'shipmethodkey', 'datekey', 
                  'orderqty', 'unitprice', 'linetotal', 'receivedqty', 
                  'rejectedqty', 'stockedqty', 'taxamt', 'freight']
    df_fact[final_cols].to_sql('fact_purchasing', engine_dw, if_exists='append', index=False)
    print("PURCHASING: Fact Table loaded.")