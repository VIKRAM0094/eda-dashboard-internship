"""
dashboard/app.py
────────────────
Interactive Retail Sales Analytics Dashboard — built with Streamlit & Plotly.

Run:  streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, warnings

warnings.filterwarnings("ignore")

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fc; }
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 5px solid #1F4E79;
        margin-bottom: 10px;
    }
    .metric-title { font-size: 13px; color: #666; font-weight: 500; margin-bottom: 4px; }
    .metric-value { font-size: 26px; font-weight: 700; color: #1F4E79; }
    .metric-delta { font-size: 12px; color: #27ae60; margin-top: 2px; }
    .section-header {
        font-size: 17px; font-weight: 700; color: #1F4E79;
        border-bottom: 2px solid #2874A6;
        padding-bottom: 6px; margin-bottom: 14px; margin-top: 10px;
    }
    div[data-testid="stSidebar"] { background: #1F4E79; }
    div[data-testid="stSidebar"] * { color: white !important; }
    div[data-testid="stSidebar"] .stSelectbox label,
    div[data-testid="stSidebar"] .stMultiSelect label { color: #BDD7EE !important; font-size: 13px; }
    .sidebar-title { font-size: 20px; font-weight: 800; color: white; margin-bottom: 4px; }
    .sidebar-sub   { font-size: 12px; color: #AED6F1; margin-bottom: 20px; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
BASE        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH  = os.path.join(BASE, "data", "retail_sales_clean.csv")
RAW_PATH    = os.path.join(BASE, "data", "retail_sales.csv")

@st.cache_data
def load_data():
    path = CLEAN_PATH if os.path.exists(CLEAN_PATH) else RAW_PATH
    df = pd.read_csv(path, parse_dates=["Order_Date"])
    if "Year" not in df.columns:
        df["Year"]         = df["Order_Date"].dt.year
        df["Month"]        = df["Order_Date"].dt.month
        df["Month_Name"]   = df["Order_Date"].dt.strftime("%b")
        df["Quarter"]      = df["Order_Date"].dt.quarter.map({1:"Q1",2:"Q2",3:"Q3",4:"Q4"})
    if "Profit_Margin" not in df.columns:
        df["Profit_Margin"] = (df["Profit"] / df["Sales"] * 100).round(2)
    return df

df_all = load_data()

COLORS = px.colors.sequential.Blues[3:]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">📊 Retail Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Data Analytics Internship Project</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**🗓 Date Range**")
    min_date = df_all["Order_Date"].min().date()
    max_date = df_all["Order_Date"].max().date()
    date_from, date_to = st.date_input(
        "Select Range",
        value=(min_date, max_date),
        min_value=min_date, max_value=max_date,
        label_visibility="collapsed"
    )

    st.markdown("**🗂 Category**")
    all_cats = sorted(df_all["Category"].unique())
    sel_cats = st.multiselect("Category", all_cats, default=all_cats, label_visibility="collapsed")

    st.markdown("**🌏 Region**")
    all_regions = sorted(df_all["Region"].unique())
    sel_regions = st.multiselect("Region", all_regions, default=all_regions, label_visibility="collapsed")

    st.markdown("**👤 Segment**")
    all_segs = sorted(df_all["Segment"].unique())
    sel_segs = st.multiselect("Segment", all_segs, default=all_segs, label_visibility="collapsed")

    st.markdown("---")
    page = st.radio("📄 **Navigation**",
                    ["🏠 Overview", "📈 Sales Trends", "🗺 Geographic", "📦 Products", "🔍 Raw Data"],
                    label_visibility="collapsed")

# ── Filter Data ───────────────────────────────────────────────────────────────
df = df_all.copy()
df = df[
    (df["Order_Date"].dt.date >= date_from) &
    (df["Order_Date"].dt.date <= date_to) &
    (df["Category"].isin(sel_cats)) &
    (df["Region"].isin(sel_regions)) &
    (df["Segment"].isin(sel_segs))
]

# ── KPI Helper ────────────────────────────────────────────────────────────────
def kpi_card(title, value, delta=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-delta">{delta}</div>
    </div>""", unsafe_allow_html=True)

def section(title):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("🏠 Sales Overview Dashboard")
    st.caption(f"Filtered: {len(df):,} orders  |  {date_from} → {date_to}")

    # KPIs
    total_sales   = df["Sales"].sum()
    total_profit  = df["Profit"].sum()
    avg_margin    = df["Profit_Margin"].mean()
    total_orders  = len(df)
    unique_custs  = df["Customer_ID"].nunique()
    avg_order_val = df["Sales"].mean()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: kpi_card("💰 Total Sales",   f"₹{total_sales/1e6:.2f}M")
    with c2: kpi_card("📈 Total Profit",  f"₹{total_profit/1e6:.2f}M")
    with c3: kpi_card("📊 Avg Margin",    f"{avg_margin:.1f}%")
    with c4: kpi_card("🛒 Total Orders",  f"{total_orders:,}")
    with c5: kpi_card("👥 Customers",     f"{unique_custs:,}")
    with c6: kpi_card("🧾 Avg Order Val", f"₹{avg_order_val:,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1: Category + Region
    col1, col2 = st.columns(2)
    with col1:
        section("Sales by Category")
        cat_df = df.groupby("Category")[["Sales","Profit"]].sum().reset_index().sort_values("Sales", ascending=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(y=cat_df["Category"], x=cat_df["Sales"],  name="Sales",  orientation="h",
                             marker_color="#2874A6"))
        fig.add_trace(go.Bar(y=cat_df["Category"], x=cat_df["Profit"], name="Profit", orientation="h",
                             marker_color="#85C1E9"))
        fig.update_layout(barmode="group", height=340, margin=dict(l=0,r=10,t=10,b=0),
                          legend=dict(orientation="h", y=1.05),
                          xaxis_tickformat="₹,.0f", plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Sales Share by Region")
        reg_df = df.groupby("Region")["Sales"].sum().reset_index()
        fig = px.pie(reg_df, names="Region", values="Sales",
                     color_discrete_sequence=px.colors.sequential.Blues[2:],
                     hole=0.45)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(height=340, margin=dict(l=0,r=0,t=10,b=0),
                          showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    # Row 2: Segment + Payment
    col3, col4 = st.columns(2)
    with col3:
        section("Revenue by Customer Segment")
        seg_df = df.groupby("Segment")[["Sales","Profit"]].sum().reset_index()
        fig = px.bar(seg_df, x="Segment", y=["Sales","Profit"],
                     barmode="group",
                     color_discrete_map={"Sales":"#1F4E79","Profit":"#85C1E9"})
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                          yaxis_tickformat="₹,.0f", plot_bgcolor="white", paper_bgcolor="white",
                          legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        section("Orders by Payment Mode")
        pay_df = df["Payment_Mode"].value_counts().reset_index()
        pay_df.columns = ["Payment_Mode","Count"]
        fig = px.bar(pay_df, x="Count", y="Payment_Mode", orientation="h",
                     color="Count", color_continuous_scale="Blues")
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                          showlegend=False, coloraxis_showscale=False,
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SALES TRENDS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Sales Trends":
    st.title("📈 Sales Trends & Analysis")

    # Monthly trend
    section("Monthly Sales & Profit Trend")
    monthly = df.groupby(df["Order_Date"].dt.to_period("M"))[["Sales","Profit"]].sum().reset_index()
    monthly["Order_Date"] = monthly["Order_Date"].dt.to_timestamp()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=monthly["Order_Date"], y=monthly["Sales"],
                         name="Sales", marker_color="#2874A6", opacity=0.85), secondary_y=False)
    fig.add_trace(go.Scatter(x=monthly["Order_Date"], y=monthly["Profit"],
                             name="Profit", line=dict(color="#F39C12", width=2.5),
                             mode="lines+markers"), secondary_y=True)
    fig.update_layout(height=370, margin=dict(l=0,r=0,t=10,b=0),
                      legend=dict(orientation="h", y=1.08),
                      plot_bgcolor="white", paper_bgcolor="white")
    fig.update_yaxes(tickformat="₹,.0f", secondary_y=False)
    fig.update_yaxes(tickformat="₹,.0f", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        section("Quarterly Performance")
        qtr = df.groupby(["Year","Quarter"])[["Sales","Profit"]].sum().reset_index()
        qtr["YQ"] = qtr["Year"].astype(str) + " " + qtr["Quarter"]
        fig = px.line(qtr, x="YQ", y="Sales", color="Year",
                      markers=True, color_discrete_sequence=px.colors.sequential.Blues[2:])
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                          yaxis_tickformat="₹,.0f",
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Discount vs Profit Margin")
        sample = df.sample(min(800, len(df)), random_state=1)
        fig = px.scatter(sample, x="Discount", y="Profit_Margin", color="Category",
                         size="Sales", opacity=0.65,
                         color_discrete_sequence=px.colors.sequential.Blues[1:])
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                          xaxis_tickformat=".0%",
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    section("Correlation Matrix")
    num_cols = ["Unit_Price","Quantity","Discount","Sales","Profit","Profit_Margin"]
    corr = df[num_cols].corr().round(2)
    fig = px.imshow(corr, text_auto=True, color_continuous_scale="Blues",
                    aspect="auto", zmin=-1, zmax=1)
    fig.update_layout(height=380, margin=dict(l=0,r=0,t=10,b=0),
                      plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: GEOGRAPHIC
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗺 Geographic":
    st.title("🗺 Geographic Sales Analysis")

    col1, col2 = st.columns([3, 2])
    with col1:
        section("Top 15 Cities by Sales")
        city_df = df.groupby("City")[["Sales","Profit"]].sum().nlargest(15,"Sales").reset_index()
        fig = px.bar(city_df, x="Sales", y="City", orientation="h",
                     color="Profit", color_continuous_scale="Blues", text="Sales")
        fig.update_traces(texttemplate="₹%{x:,.0f}", textposition="outside")
        fig.update_layout(height=480, margin=dict(l=0,r=60,t=10,b=0),
                          xaxis_tickformat="₹,.0f",
                          coloraxis_showscale=False,
                          plot_bgcolor="white", paper_bgcolor="white",
                          yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Region Performance")
        reg_df = df.groupby("Region").agg(
            Sales=("Sales","sum"), Profit=("Profit","sum"),
            Orders=("Order_ID","count"), Margin=("Profit_Margin","mean")
        ).reset_index().sort_values("Sales", ascending=False)
        reg_df["Sales_M"]  = reg_df["Sales"].apply(lambda x: f"₹{x/1e6:.2f}M")
        reg_df["Profit_M"] = reg_df["Profit"].apply(lambda x: f"₹{x/1e6:.2f}M")
        reg_df["Margin%"]  = reg_df["Margin"].apply(lambda x: f"{x:.1f}%")

        fig = go.Figure(data=[go.Table(
            columnwidth=[90, 90, 70, 80, 75],
            header=dict(values=["Region","Sales","Profit","Orders","Margin"],
                        fill_color="#1F4E79", font=dict(color="white", size=12),
                        align="left", height=36),
            cells=dict(values=[reg_df["Region"], reg_df["Sales_M"], reg_df["Profit_M"],
                                reg_df["Orders"], reg_df["Margin%"]],
                       fill_color=[["#D6EAF8" if i%2==0 else "white" for i in range(len(reg_df))]]*5,
                       font=dict(size=11), align="left", height=30)
        )])
        fig.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

        section("Profit Margin by Region")
        fig = px.bar(reg_df.sort_values("Margin"), x="Margin", y="Region",
                     orientation="h", color="Margin", color_continuous_scale="Blues",
                     text="Margin%")
        fig.update_traces(textposition="outside")
        fig.update_layout(height=220, margin=dict(l=0,r=50,t=10,b=0),
                          coloraxis_showscale=False, xaxis_tickformat=".1f",
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    section("Sales by Region and Category (Heatmap)")
    heat_df = df.groupby(["Region","Category"])["Sales"].sum().reset_index()
    heat_pivot = heat_df.pivot(index="Region", columns="Category", values="Sales").fillna(0)
    fig = px.imshow(heat_pivot, text_auto=".2s", color_continuous_scale="Blues", aspect="auto")
    fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📦 Products":
    st.title("📦 Product & Category Analysis")

    col1, col2 = st.columns(2)
    with col1:
        section("Top 10 Products by Revenue")
        prod_df = df.groupby("Product_Name")[["Sales","Profit"]].sum().nlargest(10,"Sales").reset_index()
        fig = px.bar(prod_df, x="Sales", y="Product_Name", orientation="h",
                     color="Profit", color_continuous_scale="Blues", text="Sales")
        fig.update_traces(texttemplate="₹%{x:,.0f}", textposition="outside")
        fig.update_layout(height=360, margin=dict(l=0,r=80,t=10,b=0),
                          xaxis_tickformat="₹,.0f", coloraxis_showscale=False,
                          plot_bgcolor="white", paper_bgcolor="white",
                          yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Profit Margin Distribution by Category")
        fig = px.box(df, x="Category", y="Profit_Margin",
                     color="Category", color_discrete_sequence=px.colors.sequential.Blues[1:])
        fig.update_layout(height=360, margin=dict(l=0,r=0,t=10,b=0),
                          showlegend=False, yaxis_title="Profit Margin (%)",
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    section("Category × Segment — Avg Profit Margin (%)")
    pivot = df.groupby(["Category","Segment"])["Profit_Margin"].mean().round(1).reset_index()
    pivot_wide = pivot.pivot(index="Category", columns="Segment", values="Profit_Margin")
    fig = px.imshow(pivot_wide, text_auto=True, color_continuous_scale="Blues", aspect="auto")
    fig.update_layout(height=320, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        section("Ship Mode Distribution")
        ship_df = df["Ship_Mode"].value_counts().reset_index()
        ship_df.columns = ["Ship_Mode","Count"]
        fig = px.pie(ship_df, names="Ship_Mode", values="Count", hole=0.4,
                     color_discrete_sequence=px.colors.sequential.Blues[2:])
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        section("Quantity vs Sales by Category")
        sample = df.sample(min(600, len(df)), random_state=42)
        fig = px.scatter(sample, x="Quantity", y="Sales", color="Category",
                         size="Profit", opacity=0.7,
                         color_discrete_sequence=px.colors.sequential.Blues[1:])
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                          yaxis_tickformat="₹,.0f",
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: RAW DATA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Raw Data":
    st.title("🔍 Raw Data Explorer")

    col1, col2, col3, col4 = st.columns(4)
    with col1: kpi_card("Total Rows",    f"{len(df):,}")
    with col2: kpi_card("Columns",       f"{len(df.columns)}")
    with col3: kpi_card("Date Range",    f"{df['Order_Date'].min().date()} → {df['Order_Date'].max().date()}")
    with col4: kpi_card("Unique Orders", f"{df['Order_ID'].nunique():,}")

    st.markdown("<br>", unsafe_allow_html=True)
    section("Data Preview")

    # Column selector
    cols_to_show = st.multiselect("Select Columns", df.columns.tolist(), default=df.columns.tolist()[:10])
    n_rows = st.slider("Rows to display", 10, min(500, len(df)), 50)
    st.dataframe(df[cols_to_show].head(n_rows), use_container_width=True)

    section("Descriptive Statistics")
    st.dataframe(df.describe().round(2), use_container_width=True)

    section("Missing Values")
    null_df = pd.DataFrame({
        "Column": df.columns,
        "Missing": df.isnull().sum().values,
        "Missing %": (df.isnull().mean() * 100).round(2).values,
        "Dtype": df.dtypes.values.astype(str)
    })
    st.dataframe(null_df, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Download Filtered Dataset as CSV",
        data=csv_data,
        file_name="retail_sales_filtered.csv",
        mime="text/csv"
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#999; font-size:12px;'>"
    "📊 Retail Sales Analytics Dashboard &nbsp;|&nbsp; "
    "Data Analytics Internship Project &nbsp;|&nbsp; "
    "Built with Python · Streamlit · Plotly</p>",
    unsafe_allow_html=True
)
