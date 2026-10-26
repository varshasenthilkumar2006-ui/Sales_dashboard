import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Sales & Revenue Dashboard",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    .main-title {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 17px;
        margin-bottom: 25px;
    }

    [data-testid="stMetric"] {
        border: 1px solid #dddddd;
        padding: 15px;
        border-radius: 10px;
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">📊 Sales & Revenue Analysis Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Interactive dashboard for analyzing sales performance and business revenue</div>',
    unsafe_allow_html=True
)

# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv("sales_data.csv")

    # Convert Date column
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Remove invalid dates
    df = df.dropna(subset=["Date"])

    # Calculate Profit
    df["Profit"] = df["Sales_Amount"] - df["Cost"]

    # Calculate Profit Margin
    df["Profit_Margin"] = (
        df["Profit"] / df["Sales_Amount"] * 100
    ).fillna(0)

    # Create Month column
    df["Month"] = df["Date"].dt.strftime("%Y-%m")

    return df


# Load dataset
try:
    df = load_data()

except Exception as e:

    st.error("❌ Unable to load sales_data.csv")

    st.write("Please check that sales_data.csv is present in the same folder as app.py.")

    st.exception(e)

    st.stop()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.title("🔍 Dashboard Filters")

st.sidebar.markdown("Use the filters below to analyze the data.")

# ------------------------------------------------------------
# Date Filter
# ------------------------------------------------------------

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "📅 Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Make sure two dates are selected
if isinstance(date_range, tuple) and len(date_range) == 2:

    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

else:

    start_date = pd.to_datetime(min_date)
    end_date = pd.to_datetime(max_date)


# ------------------------------------------------------------
# Region Filter
# ------------------------------------------------------------

regions = sorted(df["Region"].dropna().unique())

selected_regions = st.sidebar.multiselect(
    "🌍 Select Region",
    options=regions,
    default=regions
)


# ------------------------------------------------------------
# Category Filter
# ------------------------------------------------------------

categories = sorted(df["Category"].dropna().unique())

selected_categories = st.sidebar.multiselect(
    "📦 Select Category",
    options=categories,
    default=categories
)


# ------------------------------------------------------------
# Product Filter
# ------------------------------------------------------------

products = sorted(df["Product"].dropna().unique())

selected_products = st.sidebar.multiselect(
    "🏷️ Select Product",
    options=products,
    default=products
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    (df["Date"] >= start_date)
    & (df["Date"] <= end_date)
    & (df["Region"].isin(selected_regions))
    & (df["Category"].isin(selected_categories))
    & (df["Product"].isin(selected_products))
].copy()


# ============================================================
# CHECK FILTERED DATA
# ============================================================

if filtered_df.empty:

    st.warning("⚠️ No data available for the selected filters.")

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_sales = filtered_df["Sales_Amount"].sum()

total_revenue = filtered_df["Sales_Amount"].sum()

total_profit = filtered_df["Profit"].sum()

total_quantity = filtered_df["Quantity"].sum()

average_order_value = filtered_df["Sales_Amount"].mean()

profit_margin = (
    total_profit / total_sales * 100
    if total_sales > 0
    else 0
)


# ============================================================
# KPI SECTION
# ============================================================

st.subheader("📈 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "💰 Total Sales",
        f"₹{total_sales:,.0f}"
    )

with col2:
    st.metric(
        "💵 Total Revenue",
        f"₹{total_revenue:,.0f}"
    )

with col3:
    st.metric(
        "📈 Total Profit",
        f"₹{total_profit:,.0f}"
    )

with col4:
    st.metric(
        "📦 Quantity Sold",
        f"{total_quantity:,}"
    )

with col5:
    st.metric(
        "📊 Profit Margin",
        f"{profit_margin:.2f}%"
    )


st.markdown("---")


# ============================================================
# REVENUE TREND
# ============================================================

st.subheader("📈 Revenue Trend")

monthly_revenue = (
    filtered_df
    .groupby("Month")["Sales_Amount"]
    .sum()
    .reset_index()
)

fig_revenue = px.line(
    monthly_revenue,
    x="Month",
    y="Sales_Amount",
    markers=True,
    title="Monthly Revenue Trend"
)

fig_revenue.update_layout(
    xaxis_title="Month",
    yaxis_title="Revenue (₹)",
    hovermode="x unified"
)

st.plotly_chart(
    fig_revenue,
    use_container_width=True
)


# ============================================================
# TOP PRODUCTS + CATEGORY
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# TOP 10 PRODUCTS
# ------------------------------------------------------------

with col1:

    st.subheader("🏆 Top 10 Products")

    top_products = (
        filtered_df
        .groupby("Product")["Sales_Amount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig_products = px.bar(
        top_products,
        x="Sales_Amount",
        y="Product",
        orientation="h",
        title="Top 10 Products by Sales",
        text_auto=".2s"
    )

    fig_products.update_layout(
        xaxis_title="Sales (₹)",
        yaxis_title="Product"
    )

    st.plotly_chart(
        fig_products,
        use_container_width=True
    )


# ------------------------------------------------------------
# SALES BY CATEGORY
# ------------------------------------------------------------

with col2:

    st.subheader("📊 Sales by Category")

    category_sales = (
        filtered_df
        .groupby("Category")["Sales_Amount"]
        .sum()
        .reset_index()
    )

    fig_category = px.pie(
        category_sales,
        values="Sales_Amount",
        names="Category",
        title="Sales Distribution by Category",
        hole=0.4
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


# ============================================================
# SALES BY REGION
# ============================================================

st.subheader("🌍 Sales by Region")

region_sales = (
    filtered_df
    .groupby("Region")["Sales_Amount"]
    .sum()
    .reset_index()
    .sort_values("Sales_Amount", ascending=False)
)

fig_region = px.bar(
    region_sales,
    x="Region",
    y="Sales_Amount",
    title="Regional Sales Performance",
    text_auto=".2s"
)

fig_region.update_layout(
    xaxis_title="Region",
    yaxis_title="Sales (₹)"
)

st.plotly_chart(
    fig_region,
    use_container_width=True
)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

best_product = (
    filtered_df
    .groupby("Product")["Sales_Amount"]
    .sum()
    .idxmax()
)

best_category = (
    filtered_df
    .groupby("Category")["Sales_Amount"]
    .sum()
    .idxmax()
)

best_region = (
    filtered_df
    .groupby("Region")["Sales_Amount"]
    .sum()
    .idxmax()
)

insight1, insight2, insight3 = st.columns(3)

with insight1:

    st.info(
        f"🏆 **Top Product**\n\n"
        f"{best_product}"
    )

with insight2:

    st.info(
        f"📦 **Best Category**\n\n"
        f"{best_category}"
    )

with insight3:

    st.info(
        f"🌍 **Best Region**\n\n"
        f"{best_region}"
    )


# ============================================================
# DETAILED DATA TABLE
# ============================================================

st.subheader("📋 Detailed Sales Data")

display_columns = [
    "Date",
    "Product",
    "Category",
    "Region",
    "Quantity",
    "Unit_Price",
    "Sales_Amount",
    "Cost",
    "Profit",
    "Profit_Margin"
]

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DOWNLOAD FILTERED DATA
# ============================================================

st.subheader("⬇️ Download Data")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv_data,
    file_name="filtered_sales_data.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "📊 Sales & Revenue Analysis Dashboard | "
    "Built with Python, Pandas, Plotly and Streamlit"
)