import sqlite3
import pandas as pd

# Load CSV data
file_path = r"C:\66\supermarket_sales.csv"  # Ensure this path is correct
df = pd.read_csv(file_path)

# Rename columns to match SQLite schema
df.rename(columns={
    "Invoice ID": "invoice_id",
    "Customer type": "customer_type",
    "Gender": "gender",
    "Product line": "product_line",
    "Total": "total",
    "Date": "date",
    "Time": "time"
}, inplace=True)

# Connect to SQLite database (creates supermarket.db if not exists)
conn = sqlite3.connect("supermarket.db")
cursor = conn.cursor()

# ✅ Drop existing tables to clean up data
cursor.executescript("""
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS sales;
""")

# ✅ Recreate tables
cursor.executescript("""
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_type TEXT NOT NULL,
    gender TEXT NOT NULL
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_line TEXT NOT NULL
);

CREATE TABLE sales (
    sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
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

# ✅ Insert unique customers and store their IDs
customers = df[['customer_type', 'gender']].drop_duplicates().reset_index(drop=True)
customers.to_sql('customers', conn, if_exists='append', index=False)

# Retrieve assigned customer IDs
customer_df = pd.read_sql("SELECT customer_id, customer_type, gender FROM customers", conn)
customer_map = {(row['customer_type'], row['gender']): row['customer_id'] for _, row in customer_df.iterrows()}

# ✅ Insert unique products and store their IDs
products = df[['product_line']].drop_duplicates().reset_index(drop=True)
products.to_sql('products', conn, if_exists='append', index=False)

# Retrieve assigned product IDs
product_df = pd.read_sql("SELECT product_id, product_line FROM products", conn)
product_map = {row['product_line']: row['product_id'] for _, row in product_df.iterrows()}

# ✅ Map customer_id and product_id in sales table
df['customer_id'] = df.apply(lambda row: customer_map.get((row['customer_type'], row['gender'])), axis=1)
df['product_id'] = df['product_line'].map(product_map)

# Select only necessary columns for sales
sales = df[['invoice_id', 'customer_id', 'product_id', 'total', 'date', 'time']]

# ✅ Insert sales data
sales.to_sql('sales', conn, if_exists='append', index=False)

# Commit & Close
conn.commit()
conn.close()

print("✅ Database reset and data successfully inserted into SQLite!")
