import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Retail Sales Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.main { background-color: #f8f9fc; }
.block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
.metric-card { background: white; border-radius: 12px; padding: 18px 22px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 5px solid #1F4E79; margin-bottom: 10px; }
.metric-title { font-size: 13px; color: #666; font-weight: 500; margin-bottom: 4px; }
.metric-value { font-size: 24px; font-weight: 700; color: #1F4E79; }
.section-header { font-size: 17px; font-weight: 700; color: #1F4E79; border-bottom: 2px solid #2874A6; padding-bottom: 6px; margin-bottom: 14px; margin-top: 10px; }
div[data-testid="stSidebar"] { background: #1F4E79; }
div[data-testid="stSidebar"] label { color: #BDD7EE !important; font-size: 13px; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

DATA_PATH = "/home/claude/eda_project/data/retail_sales_clean.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["Order_Date"])
    return df

df_all = load_data()

def kpi(title, value):
    st.markdown(f'<div class="metric-card"><div class="metric-title">{title}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

def sec(title):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 📊 Retail Analytics")
    st.markdown("*Data Analytics Internship*")
    st.markdown("---")
    min_d, max_d = df_all["Order_Date"].min().date(), df_all["Order_Date"].max().date()
    d_range = st.date_input("🗓 Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    sel_cats = st.multiselect("🗂 Category", sorted(df_all["Category"].unique()), default=sorted(df_all["Category"].unique()))
    sel_regs = st.multiselect("🌏 Region",   sorted(df_all["Region"].unique()),   default=sorted(df_all["Region"].unique()))
    sel_segs = st.multiselect("👤 Segment",  sorted(df_all["Segment"].unique()),  default=sorted(df_all["Segment"].unique()))
    st.markdown("---")
    page = st.radio("📄 Page", ["🏠 Overview", "📈 Trends", "🗺 Geographic", "📦 Products", "🔍 Data Explorer"])

# Filter
df = df_all.copy()
if len(d_range) == 2:
    df = df[(df["Order_Date"].dt.date >= d_range[0]) & (df["Order_Date"].dt.date <= d_range[1])]
if sel_cats: df = df[df["Category"].isin(sel_cats)]
if sel_regs: df = df[df["Region"].isin(sel_regs)]
if sel_segs: df = df[df["Segment"].isin(sel_segs)]

BLUES = px.colors.sequential.Blues

# ── OVERVIEW ──────────────────────────────────────────────────────────────────
if page == "🏠 Overview":
    st.title("🏠 Sales Overview Dashboard")
    st.caption(f"{len(df):,} orders · {df['Order_Date'].min().date()} → {df['Order_Date'].max().date()}")

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: kpi("💰 Total Sales",   f"₹{df['Sales'].sum()/1e6:.2f}M")
    with c2: kpi("📈 Total Profit",  f"₹{df['Profit'].sum()/1e6:.2f}M")
    with c3: kpi("📊 Avg Margin",    f"{df['Profit_Margin'].mean():.1f}%")
    with c4: kpi("🛒 Orders",        f"{len(df):,}")
    with c5: kpi("👥 Customers",     f"{df['Customer_ID'].nunique():,}")
    with c6: kpi("🧾 Avg Order",     f"₹{df['Sales'].mean():,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        sec("Sales & Profit by Category")
        cat_df = df.groupby("Category")[["Sales","Profit"]].sum().reset_index().sort_values("Sales", ascending=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(y=cat_df["Category"], x=cat_df["Sales"],  name="Sales",  orientation="h", marker_color="#1F4E79"))
        fig.add_trace(go.Bar(y=cat_df["Category"], x=cat_df["Profit"], name="Profit", orientation="h", marker_color="#85C1E9"))
        fig.update_layout(barmode="group", height=340, margin=dict(l=0,r=10,t=10,b=0),
                          xaxis_tickformat="₹,.0f", plot_bgcolor="white", paper_bgcolor="white",
                          legend=dict(orientation="h",y=1.08))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        sec("Sales Share by Region")
        reg_df = df.groupby("Region")["Sales"].sum().reset_index()
        fig = px.pie(reg_df, names="Region", values="Sales", hole=0.45,
                     color_discrete_sequence=BLUES[2:])
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(height=340, margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        sec("Revenue by Customer Segment")
        seg_df = df.groupby("Segment")[["Sales","Profit"]].sum().reset_index()
        fig = px.bar(seg_df, x="Segment", y=["Sales","Profit"], barmode="group",
                     color_discrete_map={"Sales":"#1F4E79","Profit":"#85C1E9"})
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0), yaxis_tickformat="₹,.0f",
                          plot_bgcolor="white", paper_bgcolor="white", legend=dict(orientation="h",y=1.08))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        sec("Orders by Payment Mode")
        pay_df = df["Payment_Mode"].value_counts().reset_index()
        pay_df.columns = ["Payment_Mode","Count"]
        fig = px.bar(pay_df, x="Count", y="Payment_Mode", orientation="h",
                     color="Count", color_continuous_scale="Blues")
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                          coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

# ── TRENDS ────────────────────────────────────────────────────────────────────
elif page == "📈 Trends":
    st.title("📈 Sales Trends & Analysis")

    sec("Monthly Sales & Profit Trend")
    monthly = df.groupby(df["Order_Date"].dt.to_period("M"))[["Sales","Profit"]].sum().reset_index()
    monthly["Order_Date"] = monthly["Order_Date"].dt.to_timestamp()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=monthly["Order_Date"], y=monthly["Sales"], name="Sales", marker_color="#2874A6", opacity=0.85), secondary_y=False)
    fig.add_trace(go.Scatter(x=monthly["Order_Date"], y=monthly["Profit"], name="Profit", line=dict(color="#F39C12", width=2.5), mode="lines+markers"), secondary_y=True)
    fig.update_layout(height=370, margin=dict(l=0,r=0,t=10,b=0), legend=dict(orientation="h",y=1.08),
                      plot_bgcolor="white", paper_bgcolor="white")
    fig.update_yaxes(tickformat="₹,.0f", secondary_y=False)
    fig.update_yaxes(tickformat="₹,.0f", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        sec("Quarterly Performance by Year")
        qtr = df.groupby(["Year","Quarter"])["Sales"].sum().reset_index()
        qtr["YQ"] = qtr["Year"].astype(str) + " " + qtr["Quarter"]
        fig = px.line(qtr, x="YQ", y="Sales", color="Year", markers=True,
                      color_discrete_sequence=BLUES[2:])
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0), yaxis_tickformat="₹,.0f",
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        sec("Discount vs Profit Margin")
        sample = df.sample(min(800,len(df)), random_state=1)
        fig = px.scatter(sample, x="Discount", y="Profit_Margin", color="Category",
                         size="Sales", opacity=0.65, color_discrete_sequence=BLUES[1:])
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0), xaxis_tickformat=".0%",
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    sec("Correlation Matrix")
    num_cols = ["Unit_Price","Quantity","Discount","Sales","Profit","Profit_Margin"]
    corr = df[num_cols].corr().round(2)
    fig = px.imshow(corr, text_auto=True, color_continuous_scale="Blues", aspect="auto", zmin=-1, zmax=1)
    fig.update_layout(height=380, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

# ── GEOGRAPHIC ────────────────────────────────────────────────────────────────
elif page == "🗺 Geographic":
    st.title("🗺 Geographic Sales Analysis")

    col1, col2 = st.columns([3,2])
    with col1:
        sec("Top 15 Cities by Sales")
        city_df = df.groupby("City")[["Sales","Profit"]].sum().nlargest(15,"Sales").reset_index()
        fig = px.bar(city_df, x="Sales", y="City", orientation="h",
                     color="Profit", color_continuous_scale="Blues", text="Sales")
        fig.update_traces(texttemplate="₹%{x:,.0f}", textposition="outside")
        fig.update_layout(height=500, margin=dict(l=0,r=80,t=10,b=0), xaxis_tickformat="₹,.0f",
                          coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white",
                          yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        sec("Region Summary")
        reg_df = df.groupby("Region").agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
                                           Orders=("Order_ID","count"), Margin=("Profit_Margin","mean")).reset_index().sort_values("Sales",ascending=False)
        fig = go.Figure(data=[go.Table(
            columnwidth=[80,90,70,65,65],
            header=dict(values=["Region","Sales","Profit","Orders","Margin%"],
                        fill_color="#1F4E79", font=dict(color="white",size=12), align="left", height=34),
            cells=dict(values=[reg_df["Region"],
                                reg_df["Sales"].apply(lambda x: f"₹{x/1e6:.2f}M"),
                                reg_df["Profit"].apply(lambda x: f"₹{x/1e6:.2f}M"),
                                reg_df["Orders"], reg_df["Margin"].apply(lambda x: f"{x:.1f}%")],
                       fill_color=[["#D6EAF8" if i%2==0 else "white" for i in range(len(reg_df))]]*5,
                       font=dict(size=11), align="left", height=28))])
        fig.update_layout(height=240, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

        sec("Profit Margin by Region")
        fig = px.bar(reg_df.sort_values("Margin"), x="Margin", y="Region", orientation="h",
                     color="Margin", color_continuous_scale="Blues",
                     text=reg_df.sort_values("Margin")["Margin"].apply(lambda x: f"{x:.1f}%"))
        fig.update_traces(textposition="outside")
        fig.update_layout(height=220, margin=dict(l=0,r=50,t=10,b=0),
                          coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    sec("Sales by Region × Category Heatmap")
    heat_df = df.groupby(["Region","Category"])["Sales"].sum().reset_index()
    heat_pivot = heat_df.pivot(index="Region", columns="Category", values="Sales").fillna(0)
    fig = px.imshow(heat_pivot, text_auto=".2s", color_continuous_scale="Blues", aspect="auto")
    fig.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

# ── PRODUCTS ──────────────────────────────────────────────────────────────────
elif page == "📦 Products":
    st.title("📦 Product & Category Analysis")

    col1, col2 = st.columns(2)
    with col1:
        sec("Top 10 Products by Revenue")
        prod_df = df.groupby("Product_Name")[["Sales","Profit"]].sum().nlargest(10,"Sales").reset_index()
        fig = px.bar(prod_df, x="Sales", y="Product_Name", orientation="h",
                     color="Profit", color_continuous_scale="Blues", text="Sales")
        fig.update_traces(texttemplate="₹%{x:,.0f}", textposition="outside")
        fig.update_layout(height=380, margin=dict(l=0,r=80,t=10,b=0), xaxis_tickformat="₹,.0f",
                          coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white",
                          yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        sec("Profit Margin by Category (Box Plot)")
        fig = px.box(df, x="Category", y="Profit_Margin", color="Category",
                     color_discrete_sequence=BLUES[1:])
        fig.update_layout(height=380, margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
                          yaxis_title="Profit Margin (%)", plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    sec("Category × Segment — Avg Profit Margin (%)")
    pivot = df.groupby(["Category","Segment"])["Profit_Margin"].mean().round(1).reset_index()
    pivot_wide = pivot.pivot(index="Category", columns="Segment", values="Profit_Margin")
    fig = px.imshow(pivot_wide, text_auto=True, color_continuous_scale="Blues", aspect="auto")
    fig.update_layout(height=320, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        sec("Shipping Mode Distribution")
        ship_df = df["Ship_Mode"].value_counts().reset_index(); ship_df.columns=["Ship_Mode","Count"]
        fig = px.pie(ship_df, names="Ship_Mode", values="Count", hole=0.4, color_discrete_sequence=BLUES[2:])
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        sec("Quantity vs Sales by Category")
        sample = df.sample(min(600,len(df)), random_state=42)
        fig = px.scatter(sample, x="Quantity", y="Sales", color="Category", size="Profit",
                         opacity=0.7, color_discrete_sequence=BLUES[1:])
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0), yaxis_tickformat="₹,.0f",
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

# ── DATA EXPLORER ─────────────────────────────────────────────────────────────
elif page == "🔍 Data Explorer":
    st.title("🔍 Raw Data Explorer")

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("Total Rows",    f"{len(df):,}")
    with c2: kpi("Columns",       f"{len(df.columns)}")
    with c3: kpi("Date Span",     f"{df['Order_Date'].min().date()} → {df['Order_Date'].max().date()}")
    with c4: kpi("Unique Orders", f"{df['Order_ID'].nunique():,}")

    st.markdown("<br>", unsafe_allow_html=True)
    sec("Data Preview")
    cols_show = st.multiselect("Columns", df.columns.tolist(), default=df.columns.tolist()[:10])
    n = st.slider("Rows", 10, min(500,len(df)), 50)
    st.dataframe(df[cols_show].head(n), use_container_width=True)

    sec("Descriptive Statistics")
    st.dataframe(df.describe().round(2), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button("⬇️ Download Filtered CSV", df.to_csv(index=False).encode(), "filtered_data.csv", "text/csv")

st.markdown("---")
st.markdown("<p style='text-align:center;color:#999;font-size:12px;'>📊 Retail Sales Analytics · Data Analytics Internship · Python · Streamlit · Plotly</p>", unsafe_allow_html=True)
