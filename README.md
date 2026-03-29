# 📊 Exploratory Data Analysis and Dashboard Development
### Data Analytics Internship Project

---

## 🗂 Project Structure

```
eda_project/
│
├── data/
│   ├── retail_sales.csv          ← Raw dataset (5,000 orders)
│   └── retail_sales_clean.csv    ← Cleaned dataset with engineered features
│
├── scripts/
│   ├── generate_data.py          ← Synthetic dataset generator
│   └── eda_analysis.py           ← Full EDA pipeline (12 charts)
│
├── notebooks/
│   └── EDA_Notebook.ipynb        ← Interactive Jupyter Notebook
│
├── dashboard/
│   └── app.py                    ← Streamlit dashboard (5 pages)
│
├── outputs/
│   ├── 01_sales_by_category.png
│   ├── 02_monthly_sales_trend.png
│   ├── 03_region_sales_profit.png
│   ├── 04_discount_vs_profit.png
│   ├── 05_correlation_heatmap.png
│   ├── 06_sales_profit_distribution.png
│   ├── 07_top10_cities.png
│   ├── 08_quarterly_segment_sales.png
│   ├── 09_profit_boxplot_category.png
│   ├── 10_payment_mode_pie.png
│   ├── 11_margin_heatmap.png
│   └── 12_yoy_sales_profit.png
│
└── README.md
```

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install pandas numpy matplotlib seaborn plotly streamlit scikit-learn openpyxl
```

### 2. Generate Dataset
```bash
python scripts/generate_data.py
```

### 3. Run EDA Analysis (generates all 12 charts)
```bash
python scripts/eda_analysis.py
```

### 4. Launch Streamlit Dashboard
```bash
streamlit run dashboard/app.py
```

### 5. Open Jupyter Notebook
```bash
jupyter notebook notebooks/EDA_Notebook.ipynb
```

---

## 📋 Dataset Overview

| Field          | Description                          |
|----------------|--------------------------------------|
| Order_ID       | Unique order identifier              |
| Order_Date     | Date of order (2022–2024)            |
| Ship_Mode      | Shipping method                      |
| Customer_ID    | Unique customer identifier           |
| Segment        | Consumer / Corporate / Home Office   |
| City & Region  | Geographic info (5 regions, 25 cities)|
| Category       | Product category (7 types)           |
| Product_Name   | Specific product                     |
| Payment_Mode   | Payment method used                  |
| Unit_Price     | Price per unit (₹)                   |
| Quantity       | Items ordered                        |
| Discount       | Discount applied (0–30%)             |
| Sales          | Revenue generated (₹)               |
| Profit         | Net profit (₹)                       |

---

## 📊 Tools & Libraries

| Tool         | Purpose                            |
|--------------|------------------------------------|
| Python 3.x   | Core language                      |
| Pandas       | Data manipulation & cleaning       |
| NumPy        | Numerical computations             |
| Matplotlib   | Static chart generation            |
| Seaborn      | Statistical visualizations         |
| Plotly       | Interactive charts                 |
| Streamlit    | Interactive web dashboard          |
| Jupyter      | Exploratory analysis notebook      |

---

## 📈 Dashboard Pages

1. **🏠 Overview** — KPI cards, category/region/segment breakdowns
2. **📈 Sales Trends** — Monthly trend, quarterly analysis, correlation matrix
3. **🗺 Geographic** — City rankings, region performance, sales heatmap
4. **📦 Products** — Top products, profit margin boxes, segment analysis
5. **🔍 Raw Data** — Interactive data explorer + CSV download

---

## 🔍 Key Findings

- **Electronics** is the highest-revenue category (₹65M+)
- **Central region** leads in total sales
- **Higher discounts** negatively correlate with profit margins
- **Q4** consistently shows peak sales across all years
- **Credit Card** is the most preferred payment mode (30%)
- **Consumer segment** accounts for ~52% of all orders

---

*Built for Data Analytics Internship · Python · Streamlit · Plotly*
