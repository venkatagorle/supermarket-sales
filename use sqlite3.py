import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect("supermarket.db")

# SQL Query
query = """
SELECT 
    s.invoice_id, c.customer_type, c.gender, p.product_line, 
    s.total, s.date, s.time, 
    SUM(s.total) OVER (PARTITION BY p.product_line) AS total_sales_by_product
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
JOIN products p ON s.product_id = p.product_id
ORDER BY s.date DESC;
"""

# Read SQL Query into a DataFrame
df_report = pd.read_sql(query, conn)

# Print first few rows
print(df_report.head())

# Close connection
conn.close()
