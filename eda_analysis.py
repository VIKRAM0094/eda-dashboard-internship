"""
eda_analysis.py
───────────────
Full Exploratory Data Analysis pipeline for the Retail Sales dataset.
Produces cleaned data + 12 publication-quality charts saved to outputs/.

Run:  python scripts/eda_analysis.py
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import warnings, os

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA   = os.path.join(BASE, "data", "retail_sales.csv")
OUT    = os.path.join(BASE, "outputs")
CLEAN  = os.path.join(BASE, "data", "retail_sales_clean.csv")
os.makedirs(OUT, exist_ok=True)

# ── Palette ───────────────────────────────────────────────────────────────────
PALETTE   = ["#1F4E79","#2874A6","#2E86C1","#5DADE2","#85C1E9","#AED6F1","#D6EAF8"]
HEAT_CMAP = "Blues"
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams.update({"figure.dpi": 130, "font.family": "DejaVu Sans"})

def savefig(name):
    path = os.path.join(OUT, name)
    plt.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  ✅  Saved: {name}")

# ══════════════════════════════════════════════════════════════════════════════
# 1.  LOAD & INSPECT
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  STEP 1 — Loading Data")
print("═"*60)

df = pd.read_csv(DATA, parse_dates=["Order_Date"])
print(f"\nShape : {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"\nDtypes:\n{df.dtypes}")
print(f"\nFirst 3 rows:\n{df.head(3).to_string()}")

# ══════════════════════════════════════════════════════════════════════════════
# 2.  DATA QUALITY REPORT
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  STEP 2 — Data Quality Report")
print("═"*60)

null_report = pd.DataFrame({
    "Missing Count": df.isnull().sum(),
    "Missing %":     (df.isnull().mean() * 100).round(2),
    "Dtype":         df.dtypes
}).query("`Missing Count` > 0")

print(f"\nColumns with nulls:\n{null_report}")
print(f"\nDuplicate rows: {df.duplicated().sum()}")
print(f"\nNumerical summary:\n{df.describe().round(2)}")

# ══════════════════════════════════════════════════════════════════════════════
# 3.  DATA CLEANING
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  STEP 3 — Data Cleaning")
print("═"*60)

df_clean = df.copy()

# Fill numeric nulls with median
for col in ["Discount", "Profit"]:
    med = df_clean[col].median()
    n   = df_clean[col].isnull().sum()
    df_clean[col].fillna(med, inplace=True)
    print(f"  Filled {n} nulls in '{col}' with median ({med:.2f})")

# Fill categorical nulls with mode
for col in ["Ship_Mode"]:
    mode = df_clean[col].mode()[0]
    n    = df_clean[col].isnull().sum()
    df_clean[col].fillna(mode, inplace=True)
    print(f"  Filled {n} nulls in '{col}' with mode ('{mode}')")

# Feature engineering
df_clean["Year"]          = df_clean["Order_Date"].dt.year
df_clean["Month"]         = df_clean["Order_Date"].dt.month
df_clean["Month_Name"]    = df_clean["Order_Date"].dt.strftime("%b")
df_clean["Quarter"]       = df_clean["Order_Date"].dt.quarter.map({1:"Q1",2:"Q2",3:"Q3",4:"Q4"})
df_clean["Profit_Margin"] = (df_clean["Profit"] / df_clean["Sales"] * 100).round(2)

df_clean.to_csv(CLEAN, index=False)
print(f"\n  Clean dataset saved → {CLEAN}")
print(f"  Final shape: {df_clean.shape}")

# ══════════════════════════════════════════════════════════════════════════════
# 4.  VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  STEP 4 — Generating Visualizations")
print("═"*60)

# ── FIG 1: Sales by Category (Horizontal Bar) ─────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
cat_sales = df_clean.groupby("Category")["Sales"].sum().sort_values()
bars = ax.barh(cat_sales.index, cat_sales.values, color=PALETTE[::-1], edgecolor="white", height=0.65)
ax.bar_label(bars, labels=[f"₹{v/1e6:.1f}M" for v in cat_sales.values], padding=5, fontsize=10)
ax.set_title("Total Sales by Category", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Total Sales (₹)", fontsize=11)
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x/1e6:.0f}M"))
ax.spines[["top","right"]].set_visible(False)
plt.tight_layout()
savefig("01_sales_by_category.png")

# ── FIG 2: Monthly Sales Trend (Line) ────────────────────────────────────────
monthly = df_clean.groupby(["Year","Month"])["Sales"].sum().reset_index()
monthly["Period"] = pd.to_datetime(monthly[["Year","Month"]].assign(day=1))

fig, ax = plt.subplots(figsize=(12, 5))
for yr, grp in monthly.groupby("Year"):
    ax.plot(grp["Period"], grp["Sales"], marker="o", linewidth=2.2,
            markersize=5, label=str(yr))
ax.set_title("Monthly Sales Trend (2022–2024)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Month", fontsize=11)
ax.set_ylabel("Total Sales (₹)", fontsize=11)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
ax.legend(title="Year", fontsize=10)
ax.spines[["top","right"]].set_visible(False)
plt.tight_layout()
savefig("02_monthly_sales_trend.png")

# ── FIG 3: Region-wise Sales & Profit (Grouped Bar) ───────────────────────────
reg = df_clean.groupby("Region")[["Sales","Profit"]].sum().reset_index().sort_values("Sales", ascending=False)
x   = np.arange(len(reg))
w   = 0.38

fig, ax = plt.subplots(figsize=(9, 5))
b1 = ax.bar(x - w/2, reg["Sales"],   w, label="Sales",  color=PALETTE[1], edgecolor="white")
b2 = ax.bar(x + w/2, reg["Profit"],  w, label="Profit", color=PALETTE[4], edgecolor="white")
ax.set_xticks(x); ax.set_xticklabels(reg["Region"], fontsize=11)
ax.set_title("Sales & Profit by Region", fontsize=14, fontweight="bold", pad=12)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
ax.legend(fontsize=10); ax.spines[["top","right"]].set_visible(False)
plt.tight_layout()
savefig("03_region_sales_profit.png")

# ── FIG 4: Discount vs Profit Scatter ────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
sc = ax.scatter(df_clean["Discount"], df_clean["Profit"],
                c=df_clean["Sales"], cmap="Blues", alpha=0.5, s=18, edgecolors="none")
plt.colorbar(sc, ax=ax, label="Sales (₹)")
ax.set_title("Discount vs Profit (colored by Sales)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Discount Rate", fontsize=11)
ax.set_ylabel("Profit (₹)", fontsize=11)
ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
ax.spines[["top","right"]].set_visible(False)
plt.tight_layout()
savefig("04_discount_vs_profit.png")

# ── FIG 5: Correlation Heatmap ────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
num_cols = ["Unit_Price","Quantity","Discount","Sales","Profit","Profit_Margin"]
corr = df_clean[num_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap=HEAT_CMAP,
            linewidths=0.5, ax=ax, cbar_kws={"shrink":0.8})
ax.set_title("Correlation Matrix — Numerical Features", fontsize=13, fontweight="bold", pad=12)
plt.tight_layout()
savefig("05_correlation_heatmap.png")

# ── FIG 6: Sales Distribution (Histogram + KDE) ───────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, col, label in zip(axes, ["Sales","Profit"], ["Sales (₹)","Profit (₹)"]):
    data = df_clean[col].clip(upper=df_clean[col].quantile(0.99))
    ax.hist(data, bins=50, color=PALETTE[2], edgecolor="white", alpha=0.85, density=True)
    data.plot.kde(ax=ax, color=PALETTE[0], linewidth=2)
    ax.set_title(f"Distribution of {label}", fontsize=12, fontweight="bold")
    ax.set_xlabel(label, fontsize=10); ax.set_ylabel("Density", fontsize=10)
    ax.spines[["top","right"]].set_visible(False)
fig.suptitle("Sales & Profit Distributions", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
savefig("06_sales_profit_distribution.png")

# ── FIG 7: Top 10 Cities by Sales ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
top10 = df_clean.groupby("City")["Sales"].sum().nlargest(10).sort_values()
colors = [PALETTE[0] if i >= 7 else PALETTE[3] for i in range(len(top10))]
bars = ax.barh(top10.index, top10.values, color=colors, edgecolor="white", height=0.65)
ax.bar_label(bars, labels=[f"₹{v/1e6:.2f}M" for v in top10.values], padding=5, fontsize=9)
ax.set_title("Top 10 Cities by Total Sales", fontsize=14, fontweight="bold", pad=12)
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
ax.spines[["top","right"]].set_visible(False)
plt.tight_layout()
savefig("07_top10_cities.png")

# ── FIG 8: Segment-wise Quarterly Sales (Stacked Bar) ─────────────────────────
seg_q = df_clean.groupby(["Quarter","Segment"])["Sales"].sum().unstack()
fig, ax = plt.subplots(figsize=(9, 5))
seg_q.plot(kind="bar", stacked=True, ax=ax,
           color=[PALETTE[0], PALETTE[2], PALETTE[4]],
           edgecolor="white", width=0.6)
ax.set_title("Quarterly Sales by Customer Segment", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Quarter", fontsize=11); ax.set_ylabel("Total Sales (₹)", fontsize=11)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
ax.legend(title="Segment", fontsize=10); ax.tick_params(axis="x", rotation=0)
ax.spines[["top","right"]].set_visible(False)
plt.tight_layout()
savefig("08_quarterly_segment_sales.png")

# ── FIG 9: Box Plot — Profit by Category ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
order = df_clean.groupby("Category")["Profit"].median().sort_values(ascending=False).index
df_plot = df_clean[df_clean["Profit"] < df_clean["Profit"].quantile(0.98)]
sns.boxplot(data=df_plot, x="Category", y="Profit", order=order,
            palette=PALETTE[:len(order)], width=0.55, linewidth=1.2, ax=ax)
ax.set_title("Profit Distribution by Category", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel(""); ax.set_ylabel("Profit (₹)", fontsize=11)
ax.tick_params(axis="x", labelsize=10)
ax.spines[["top","right"]].set_visible(False)
plt.tight_layout()
savefig("09_profit_boxplot_category.png")

# ── FIG 10: Payment Mode Pie Chart ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 6))
pay = df_clean["Payment_Mode"].value_counts()
wedge_props = dict(width=0.55, edgecolor="white", linewidth=2)
ax.pie(pay.values, labels=pay.index, autopct="%1.1f%%",
       colors=PALETTE[:len(pay)], startangle=140,
       wedgeprops=wedge_props, pctdistance=0.75, textprops={"fontsize":10})
ax.set_title("Orders by Payment Mode", fontsize=14, fontweight="bold", pad=12)
plt.tight_layout()
savefig("10_payment_mode_pie.png")

# ── FIG 11: Profit Margin by Category & Segment (Heatmap) ────────────────────
pivot = df_clean.groupby(["Category","Segment"])["Profit_Margin"].mean().unstack()
fig, ax = plt.subplots(figsize=(8, 5))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="Blues",
            linewidths=0.5, ax=ax, cbar_kws={"label":"Avg Profit Margin (%)"})
ax.set_title("Avg Profit Margin (%) — Category × Segment", fontsize=13, fontweight="bold", pad=12)
ax.set_xlabel(""); ax.set_ylabel("")
plt.tight_layout()
savefig("11_margin_heatmap.png")

# ── FIG 12: Year-over-Year Growth ─────────────────────────────────────────────
yoy = df_clean.groupby("Year")[["Sales","Profit"]].sum()
yoy["Sales_Growth"]  = yoy["Sales"].pct_change()  * 100
yoy["Profit_Growth"] = yoy["Profit"].pct_change() * 100

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, col, label, color in zip(axes,
        ["Sales","Profit"], ["Sales (₹)","Profit (₹)"], [PALETTE[1], PALETTE[4]]):
    bars = ax.bar(yoy.index.astype(str), yoy[col], color=color, edgecolor="white", width=0.5)
    ax.bar_label(bars, labels=[f"₹{v/1e6:.1f}M" for v in yoy[col]], padding=5, fontsize=10)
    ax.set_title(f"Year-over-Year {label}", fontsize=12, fontweight="bold")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x/1e6:.0f}M"))
    ax.spines[["top","right"]].set_visible(False)
fig.suptitle("Annual Sales & Profit Comparison", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
savefig("12_yoy_sales_profit.png")

# ══════════════════════════════════════════════════════════════════════════════
# 5.  SUMMARY STATISTICS EXPORT
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  STEP 5 — Summary Statistics")
print("═"*60)

total_sales  = df_clean["Sales"].sum()
total_profit = df_clean["Profit"].sum()
avg_margin   = df_clean["Profit_Margin"].mean()
top_cat      = df_clean.groupby("Category")["Sales"].sum().idxmax()
top_region   = df_clean.groupby("Region")["Sales"].sum().idxmax()

print(f"\n  Total Sales     : ₹{total_sales:,.0f}")
print(f"  Total Profit    : ₹{total_profit:,.0f}")
print(f"  Avg Profit Margin: {avg_margin:.2f}%")
print(f"  Top Category    : {top_cat}")
print(f"  Top Region      : {top_region}")
print(f"\n  12 charts saved to: {OUT}")
print("\n" + "═"*60)
print("  EDA COMPLETE ✅")
print("═"*60 + "\n")
