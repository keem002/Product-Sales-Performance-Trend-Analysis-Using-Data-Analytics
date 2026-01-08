import sqlite3
import pandas as pd

DB_PATH = "database/sales.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def insert_excel_data(excel_path):
    df = pd.read_excel(excel_path)

    df["total_amount"] = df["quantity"] * df["price"]

    conn = get_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO sales (
                order_id, order_date, product_name, category,
                quantity, price, total_amount, customer_name, region
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["order_id"],
            str(row["order_date"].date()),
            row["product_name"],
            row["category"],
            int(row["quantity"]),
            float(row["price"]),
            float(row["total_amount"]),
            row["customer_name"],
            row["region"]
        ))

    conn.commit()
    conn.close()
    print("Excel data inserted successfully!")

if __name__ == "__main__":
    insert_excel_data("data/sales_data.xlsx")


import pandas as pd

def fetch_sales_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM sales", conn)
    conn.close()
    return df
