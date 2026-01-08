import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

from scripts.data_processing import insert_excel_data, fetch_sales_data

st.set_page_config(page_title="Product Sales Dashboard", layout="wide")
st.title("📊 Product Sales Performance Dashboard")

# ------------------ EXCEL UPLOAD ------------------
st.subheader("📤 Upload Sales Excel")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    with open("data/temp_sales.xlsx", "wb") as f:
        f.write(uploaded_file.getbuffer())

    insert_excel_data("data/temp_sales.xlsx")
    st.success("✅ Excel data uploaded successfully!")

st.divider()

# ------------------ MANUAL ENTRY ------------------
st.subheader("➕ Add Sale Manually")

with st.form("manual_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        order_id = st.text_input("Order ID")
        order_date = st.date_input("Order Date")
        product_name = st.text_input("Product Name")

    with col2:
        category = st.text_input("Category")
        quantity = st.number_input("Quantity", min_value=1)
        price = st.number_input("Price", min_value=0.0)

    with col3:
        customer_name = st.text_input("Customer Name")
        region = st.text_input("Region")

    submit = st.form_submit_button("Add Sale")

    if submit:
        conn = sqlite3.connect("database/sales.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO sales (
                order_id, order_date, product_name, category,
                quantity, price, total_amount, customer_name, region
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_id,
            str(order_date),
            product_name,
            category,
            quantity,
            price,
            quantity * price,
            customer_name,
            region
        ))

        conn.commit()
        conn.close()
        st.success("✅ Sale added successfully!")

st.divider()

# ------------------ DASHBOARD ------------------
st.subheader("📈 Sales Analytics Dashboard")

df = fetch_sales_data()

if df.empty:
    st.warning("No data available")
else:
    # Normalize category names
    df["category"] = df["category"].str.strip().str.title()

    # ------------------ KPI CARDS ------------------
    col1, col2, col3 = st.columns(3)

    col1.markdown(
        f"""
        <div style="background-color:#E8F5E9;padding:20px;border-radius:10px">
        <h4>💰 Total Revenue</h4>
        <h2>₹ {df['total_amount'].sum():,.2f}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    col2.markdown(
        f"""
        <div style="background-color:#E3F2FD;padding:20px;border-radius:10px">
        <h4>🧾 Total Orders</h4>
        <h2>{df.shape[0]}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    col3.markdown(
        f"""
        <div style="background-color:#FFF3E0;padding:20px;border-radius:10px">
        <h4>📦 Total Quantity</h4>
        <h2>{df['quantity'].sum()}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ------------------ SALES BY CATEGORY ------------------
    cat_data = df.groupby("category", as_index=False)["total_amount"].sum()

    cat_fig = px.bar(
        cat_data,
        x="category",
        y="total_amount",
        title="Sales by Category",
        color="category",
        text_auto=True,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(cat_fig, use_container_width=True)

    # ------------------ SALES TREND ------------------
    df["order_date"] = pd.to_datetime(df["order_date"])

    trend_data = df.groupby("order_date", as_index=False)["total_amount"].sum()

    trend_fig = px.line(
        trend_data,
        x="order_date",
        y="total_amount",
        markers=True,
        title="Sales Trend Over Time",
        color_discrete_sequence=["#00E5FF"]
    )
    st.plotly_chart(trend_fig, use_container_width=True)

    # ------------------ TOP PRODUCTS ------------------
    st.subheader("🏆 Top Products")

    top_products = (
        df.groupby("product_name", as_index=False)["total_amount"]
        .sum()
        .sort_values(by="total_amount", ascending=False)
    )
    st.dataframe(top_products)

    # ------------------ FULL DATA ------------------
    st.subheader("📋 All Sales Data")
    st.dataframe(df)

