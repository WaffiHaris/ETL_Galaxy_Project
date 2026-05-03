**AdventureWorks ETL: Galaxy Schema Data Warehouse**

Proyek ini mendemonstrasikan proses ETL (Extract, Transform, Load) modular menggunakan Python dan PostgreSQL untuk membangun Enterprise Data Warehouse dengan arsitektur Galaxy Schema. Data bersumber dari database operasional AdventureWorks (OLTP) dan diproses melalui dua fase besar: Staging dan Loading ke Data Warehouse.

**Arsitektur Data**

Proyek ini mengintegrasikan data dari tiga departemen utama:

1. Human Resources (HR)
2. Sales Online
3. Purchasing

Ketiga departemen ini dihubungkan melalui Conformed Dimensions (Dimensi Bersama) yaitu dim_date dan dim_product, membentuk struktur Galaxy Schema.

**Alur Data:**

1. OLTP (adventureworks): Database sumber transaksional.
2. Staging (aw_staging_master): Area transit data mentah untuk standarisasi (cleaning & case folding).
3. Data Warehouse (aw_dw_galaxy): Tujuan akhir dengan skema bintang yang saling terhubung menggunakan Surrogate Keys.

**📂 Struktur File**

1. fase_1_extract.py: Menarik data dari OLTP ke Staging.
2. fase_2_load_dw.py: Melakukan transformasi berat dan memuat data ke Data Warehouse.
3. etl_conformed.py: Logika untuk dimensi bersama (Date & Product).
4. etl_hr.py, etl_sales.py, etl_purchasing.py: Modul spesifik tiap departemen.
5. schema.sql: Script DDL untuk membangun kerangka tabel di Data Warehouse.

**🚀 Cara Menjalankan**

**1. Prasyarat**

Pastikan Anda memiliki PostgreSQL dan library Python berikut:

Bash

    pip install pandas sqlalchemy psycopg2-binary

**2. Inisialisasi Database**

Jalankan script SQL yang ada di file schema.sql pada PostgreSQL Anda untuk membuat database:

    aw_staging_master
    
    aw_dw_galaxy

**3. Eksekusi ETL**

Jalankan proses secara modular sesuai urutan fase:

**Langkah 1: Ekstraksi ke Staging**

Bash

    python fase_1_extract.py

Script ini akan menarik data dari OLTP dan membuat tabel stg_... secara otomatis di database staging.

**Langkah 2: Transformasi dan Load ke DW**

Bash

    python fase_2_load_dw.py

Script ini akan memproses data staging, melakukan lookup surrogate keys, dan mengisi tabel dimensi serta fakta di database data warehouse.

**📊 Verifikasi Hasil**

Setelah eksekusi selesai, Anda dapat menjalankan query analitik lintas departemen di database aw_dw_galaxy. Contoh:

SQL -- Perbandingan unit terjual vs unit dibeli per Produk

    SELECT 
    
        p.productname,
        
        SUM(fs.orderqty) as total_sold,
        
        SUM(fp.orderqty) as total_purchased
    
    FROM dim_product p
    
    LEFT JOIN fact_sales_online fs ON p.productkey = fs.productkey
    
    LEFT JOIN fact_purchasing fp ON p.productkey = fp.productkey
    
    GROUP BY p.productname;


**🛠️ Teknologi yang Digunakan**

Python 3.x

Pandas: Untuk manipulasi dan transformasi data.

SQLAlchemy: Sebagai engine ORM untuk koneksi database.

PostgreSQL: Sebagai media penyimpanan OLTP, Staging, dan Data Warehouse.


**Kontributor:**


Kelompok 14

Waffi Haris Ashari - 5026241020

Ary Ratna Aida Safa - 5026241029

Alwida Rahmat - 5026241090


Record Youtube (Simulasi)
https://www.youtube.com/watch?v=clWI3fi0F0c

Mata Kuliah Data Lakehouse - Kelas B

Departemen Sistem Informasi - Institut Teknologi Sepuluh Nopember (ITS)
