"""Script that generates the EDA Jupyter notebook programmatically."""
import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

cells = []

# ── Cell helpers ──────────────────────────────────────────────
def md(src):   return nbf.v4.new_markdown_cell(src)
def code(src): return nbf.v4.new_code_cell(src)

# ─────────────────────────────────────────────────────────────
cells.append(md("""# 📊 Sales Data — Exploratory Data Analysis (EDA)

This notebook explores the processed sales data warehouse tables.
It covers:
- Dataset overview & shape
- Missing value and duplicate checks
- Sales distribution analysis
- Revenue & profit trends
- Regional and product breakdowns
- Customer behaviour insights
- Correlation analysis

**Run the ETL pipeline first:** `python main.py`
"""))

# ── 1. Setup ─────────────────────────────────────────────────
cells.append(md("## 1. Setup & Data Loading"))
cells.append(code("""\
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 110, "font.size": 11})

# Load processed tables
fact     = pd.read_csv("../data/processed/fact_sales.csv")
dim_prod = pd.read_csv("../data/processed/dim_product.csv")
dim_date = pd.read_csv("../data/processed/dim_date.csv")
dim_cust = pd.read_csv("../data/processed/dim_customer.csv")

# Build enriched flat table
df = fact.merge(dim_prod, on="product_id")
df = df.merge(dim_date,  on="date_id")
df = df.merge(dim_cust,  on="customer_id")

print(f"Total rows : {len(df):,}")
print(f"Columns    : {df.columns.tolist()}")
df.head()
"""))

# ── 2. Overview ───────────────────────────────────────────────
cells.append(md("## 2. Dataset Overview"))
cells.append(code("""\
print("── Shape ──────────────────────────────")
print(f"Rows: {df.shape[0]:,}   Columns: {df.shape[1]}")

print("\\n── Data Types ─────────────────────────")
print(df.dtypes)

print("\\n── Null Values ────────────────────────")
print(df.isnull().sum())

print("\\n── Duplicate order_ids ────────────────")
print(f"{df['order_id'].duplicated().sum()} duplicates found")
"""))

cells.append(code("""\
# Summary statistics for numeric columns
df[["quantity", "unit_price", "total_amount", "profit", "profit_margin_pct"]].describe().round(2)
"""))

# ── 3. Order Status ───────────────────────────────────────────
cells.append(md("## 3. Order Status Distribution"))
cells.append(code("""\
status_counts = df["status"].value_counts()

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Bar chart
axes[0].bar(status_counts.index, status_counts.values,
            color=sns.color_palette("Set2", 3))
axes[0].set_title("Orders by Status")
axes[0].set_ylabel("Count")
for i, v in enumerate(status_counts.values):
    axes[0].text(i, v + 5, str(v), ha="center", fontweight="bold")

# Pie chart
axes[1].pie(status_counts.values, labels=status_counts.index,
            autopct="%1.1f%%", colors=sns.color_palette("Set2", 3),
            startangle=90)
axes[1].set_title("Order Status Share")

plt.suptitle("Order Status Distribution", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.show()

print(status_counts.to_frame("count").assign(pct=lambda x: (x["count"]/x["count"].sum()*100).round(1)))
"""))

# ── 4. Revenue Overview ───────────────────────────────────────
cells.append(md("## 4. Revenue & Profit Overview"))
cells.append(code("""\
completed = df[df["status"] == "Completed"]

metrics = {
    "Total Orders":       len(completed),
    "Total Revenue ($)":  completed["total_amount"].sum(),
    "Total Profit ($)":   completed["profit"].sum(),
    "Avg Order Value ($)":completed["total_amount"].mean(),
    "Avg Profit Margin %":completed["profit_margin_pct"].mean(),
    "Avg Qty per Order":  completed["quantity"].mean(),
}
for k, v in metrics.items():
    if "$" in k:
        print(f"  {k:<25} ${v:>10,.2f}")
    elif "%" in k:
        print(f"  {k:<25} {v:>10.1f}%")
    else:
        print(f"  {k:<25} {v:>10.1f}")
"""))

cells.append(code("""\
fig, axes = plt.subplots(1, 3, figsize=(14, 4))

for ax, col, title, color in zip(
    axes,
    ["total_amount", "profit", "profit_margin_pct"],
    ["Order Revenue ($)", "Order Profit ($)", "Profit Margin (%)"],
    ["#2196F3", "#4CAF50", "#FF9800"]
):
    ax.hist(completed[col], bins=30, color=color, edgecolor="white", alpha=0.85)
    ax.axvline(completed[col].mean(), color="red", linestyle="--", label=f"Mean: {completed[col].mean():.1f}")
    ax.set_title(title)
    ax.set_xlabel(col)
    ax.set_ylabel("Frequency")
    ax.legend(fontsize=9)

plt.suptitle("Distribution of Key Metrics (Completed Orders)", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.show()
"""))

# ── 5. Monthly Trend ──────────────────────────────────────────
cells.append(md("## 5. Monthly Sales Trend"))
cells.append(code("""\
monthly = (
    completed.groupby(["year", "month", "month_name"])
    .agg(revenue=("total_amount","sum"), profit=("profit","sum"), orders=("order_id","count"))
    .reset_index()
    .sort_values(["year","month"])
)
monthly["label"] = monthly["month_name"].str[:3]

fig, ax1 = plt.subplots(figsize=(13, 5))
ax2 = ax1.twinx()

ax1.bar(monthly["label"], monthly["revenue"], color="#90CAF9", alpha=0.8, label="Revenue")
ax2.plot(monthly["label"], monthly["profit"], color="#F44336", marker="o",
         linewidth=2.5, label="Profit", markerfacecolor="white", markeredgewidth=2)

ax1.set_ylabel("Revenue ($)", color="#1565C0")
ax2.set_ylabel("Profit ($)", color="#C62828")
ax1.set_title("Monthly Revenue vs Profit (2023)", fontsize=14, fontweight="bold")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.tight_layout()
plt.show()
monthly[["label","revenue","profit","orders"]].set_index("label")
"""))

# ── 6. Regional Analysis ──────────────────────────────────────
cells.append(md("## 6. Regional Sales Analysis"))
cells.append(code("""\
region = completed.groupby("region").agg(
    orders=("order_id","count"),
    revenue=("total_amount","sum"),
    profit=("profit","sum"),
    avg_margin=("profit_margin_pct","mean")
).reset_index().sort_values("revenue", ascending=False)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Revenue by region
bars = axes[0].bar(region["region"], region["revenue"],
                   color=sns.color_palette("muted", len(region)))
axes[0].bar_label(bars, fmt="$%.0f", padding=5, fontsize=9)
axes[0].set_title("Revenue by Region")
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

# Avg margin by region
bars2 = axes[1].bar(region["region"], region["avg_margin"],
                    color=sns.color_palette("Set2", len(region)))
axes[1].bar_label(bars2, fmt="%.1f%%", padding=5, fontsize=9)
axes[1].set_title("Avg Profit Margin % by Region")
axes[1].set_ylabel("%")

plt.suptitle("Regional Performance", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.show()

region.set_index("region").round(2)
"""))

# ── 7. Product Analysis ───────────────────────────────────────
cells.append(md("## 7. Product Performance"))
cells.append(code("""\
product = completed.groupby(["product_name","category"]).agg(
    units=("quantity","sum"),
    revenue=("total_amount","sum"),
    profit=("profit","sum"),
    margin=("profit_margin_pct","mean")
).reset_index().sort_values("revenue", ascending=False)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Revenue ranking
product_sorted = product.sort_values("revenue")
axes[0].barh(product_sorted["product_name"], product_sorted["revenue"],
             color=sns.color_palette("muted", len(product)))
axes[0].set_title("Revenue by Product")
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

# Margin vs Revenue scatter
colors = {"Electronics": "#2196F3", "Furniture": "#FF9800", "Stationery": "#4CAF50"}
for _, row in product.iterrows():
    axes[1].scatter(row["revenue"], row["margin"],
                    color=colors.get(row["category"], "gray"), s=120, zorder=5)
    axes[1].annotate(row["product_name"], (row["revenue"], row["margin"]),
                     textcoords="offset points", xytext=(6, 3), fontsize=8)
axes[1].set_xlabel("Revenue ($)")
axes[1].set_ylabel("Profit Margin (%)")
axes[1].set_title("Revenue vs Margin by Product")

from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=c, label=cat) for cat, c in colors.items()]
axes[1].legend(handles=legend_elements, fontsize=9)

plt.suptitle("Product Performance Analysis", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.show()

product.set_index("product_name").round(2)
"""))

# ── 8. Customer Analysis ──────────────────────────────────────
cells.append(md("## 8. Customer Behaviour"))
cells.append(code("""\
customer = completed.groupby(["customer_name","customer_type"]).agg(
    orders=("order_id","count"),
    total_spent=("total_amount","sum"),
    avg_order=("total_amount","mean"),
    profit=("profit","sum")
).reset_index().sort_values("total_spent", ascending=False)

# Customer type segments
by_type = completed.groupby("customer_type").agg(
    orders=("order_id","count"),
    revenue=("total_amount","sum"),
).reset_index()

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Top customers bar
top10 = customer.head(8)
axes[0].barh(top10["customer_name"], top10["total_spent"],
             color=sns.color_palette("muted", len(top10)))
axes[0].set_title("Top Customers by Revenue")
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

# Revenue by customer type
axes[1].pie(by_type["revenue"], labels=by_type["customer_type"],
            autopct="%1.1f%%", colors=sns.color_palette("Set2", 3), startangle=90)
axes[1].set_title("Revenue Share by Customer Type")

plt.suptitle("Customer Analysis", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.show()

customer.head(10).set_index("customer_name").round(2)
"""))

# ── 9. Correlation Heatmap ────────────────────────────────────
cells.append(md("## 9. Correlation Analysis"))
cells.append(code("""\
numeric_cols = ["quantity", "unit_price", "unit_cost",
                "total_amount", "total_cost", "profit", "profit_margin_pct"]
corr = completed[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(9, 7))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
            mask=mask, ax=ax, linewidths=0.5, square=True)
ax.set_title("Correlation Heatmap — Numeric Features", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.show()
"""))

# ── 10. Key Insights ─────────────────────────────────────────
cells.append(md("""\
## 10. Key Insights Summary

After exploring the data, here are the main takeaways:

| Area | Finding |
|------|---------|
| **Revenue** | ~77% of orders are Completed; ~13% Returned |
| **Top Product** | Laptop Pro drives the most revenue by far |
| **Best Margin** | Stationery has the highest profit margin % |
| **Top Region** | Revenue is spread fairly evenly across regions |
| **Customer Segments** | Enterprise customers have the highest average order value |
| **Seasonality** | Review monthly trend chart for peak months |

> 💡 **Next steps**: Connect to MySQL, run `sql/analytics_queries.sql` for deeper SQL-based analysis.
"""))

# ── Assemble & save ───────────────────────────────────────────
nb.cells = cells
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    },
    "language_info": {"name": "python", "version": "3.12.0"}
}

os.makedirs("notebooks", exist_ok=True)
path = "notebooks/sales_eda.ipynb"
with open(path, "w") as f:
    nbf.write(nb, f)

print(f"✅ Notebook saved → {path}")
print(f"   Cells: {len(nb.cells)}")
