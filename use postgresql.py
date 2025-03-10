import psycopg2
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine

# ✅ Use your actual Render PostgreSQL database URL
DATABASE_URL = "postgresql://supermarket_fm98_user:TMm5U0YeBBTLmNVYlEJQ3SG69hnXPPS1@dpg-cv643oggph6c73djqm4g-a.oregon-postgres.render.com/supermarket_fm98"

# ✅ Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# ✅ Drop existing tables (cleanup)
cursor.execute("""
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
""")
conn.commit()

# ✅ Create new tables
cursor.execute("""
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_type TEXT NOT NULL,
    gender TEXT NOT NULL
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_line TEXT NOT NULL
);

CREATE TABLE sales (
    sales_id SERIAL PRIMARY KEY,
    invoice_id TEXT UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    total FLOAT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);
""")
conn.commit()

# ✅ Load CSV data
file_path = r"C:\66\supermarket_sales.csv"  # Ensure this path is correct
df = pd.read_csv(file_path)

# ✅ Rename columns to match PostgreSQL schema
df.rename(columns={
    "Invoice ID": "invoice_id",
    "Customer type": "customer_type",
    "Gender": "gender",
    "Product line": "product_line",
    "Total": "total",
    "Date": "date",
    "Time": "time"
}, inplace=True)

# ✅ Use SQLAlchemy to insert DataFrames into PostgreSQL
engine = create_engine(DATABASE_URL)

# Insert unique customers
customers = df[['customer_type', 'gender']].drop_duplicates().reset_index(drop=True)
customers.to_sql('customers', engine, if_exists='append', index=False)

# Insert unique products
products = df[['product_line']].drop_duplicates().reset_index(drop=True)
products.to_sql('products', engine, if_exists='append', index=False)

# Retrieve assigned IDs
customer_df = pd.read_sql("SELECT * FROM customers", engine)
product_df = pd.read_sql("SELECT * FROM products", engine)

# Map IDs for sales table
customer_map = {(row['customer_type'], row['gender']): row['customer_id'] for _, row in customer_df.iterrows()}
product_map = {row['product_line']: row['product_id'] for _, row in product_df.iterrows()}

df['customer_id'] = df.apply(lambda row: customer_map.get((row['customer_type'], row['gender'])), axis=1)
df['product_id'] = df['product_line'].map(product_map)

# ✅ Insert sales data
sales = df[['invoice_id', 'customer_id', 'product_id', 'total', 'date', 'time']]
sales.to_sql('sales', engine, if_exists='append', index=False)

# ✅ Close connection
conn.close()

print("✅ PostgreSQL setup on Render completed successfully!")
