"""
visualize.py — Sales Data Visualizations
Reads the processed CSVs and generates charts.

Usage:
    python src/visualize/visualize.py
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 130, "font.size": 11})

OUTPUT_DIR = "docs/charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data():
    fact     = pd.read_csv("data/processed/fact_sales.csv")
    dim_prod = pd.read_csv("data/processed/dim_product.csv")
    dim_date = pd.read_csv("data/processed/dim_date.csv")
    dim_cust = pd.read_csv("data/processed/dim_customer.csv")

    # Join for richer analysis
    df = fact.merge(dim_prod, on="product_id")
    df = df.merge(dim_date,  on="date_id")
    df = df.merge(dim_cust,  on="customer_id")
    df = df[df["status"] == "Completed"]   # completed orders only
    return df


# ── Chart 1: Monthly Revenue Trend ───────────────────────────
def plot_monthly_trend(df):
    monthly = (
        df.groupby(["year", "month", "month_name"])["total_amount"]
        .sum()
        .reset_index()
        .sort_values(["year", "month"])
    )
    monthly["label"] = monthly["month_name"].str[:3]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(monthly["label"], monthly["total_amount"], marker="o",
            linewidth=2.5, color="#2196F3", markerfacecolor="white",
            markeredgewidth=2, markersize=7)
    ax.fill_between(monthly["label"], monthly["total_amount"],
                    alpha=0.12, color="#2196F3")
    ax.set_title("Monthly Revenue Trend (2023)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue ($)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "1_monthly_revenue_trend.png")
    plt.savefig(path)
    plt.close()
    print(f"✅ Saved: {path}")


# ── Chart 2: Revenue by Region ───────────────────────────────
def plot_sales_by_region(df):
    region = df.groupby("region")["total_amount"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(region.index, region.values, color=sns.color_palette("muted", len(region)))
    ax.bar_label(bars, fmt="$%.0f", padding=5, fontsize=9)
    ax.set_title("Total Revenue by Region", fontsize=14, fontweight="bold")
    ax.set_xlabel("Region")
    ax.set_ylabel("Revenue ($)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "2_revenue_by_region.png")
    plt.savefig(path)
    plt.close()
    print(f"✅ Saved: {path}")


# ── Chart 3: Top 5 Products by Revenue ───────────────────────
def plot_top_products(df):
    top = (
        df.groupby("product_name")["total_amount"]
        .sum()
        .sort_values(ascending=True)
        .tail(5)
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(top.index, top.values, color=sns.color_palette("muted", 5))
    ax.bar_label(bars, fmt="$%.0f", padding=5, fontsize=9)
    ax.set_title("Top 5 Products by Revenue", fontsize=14, fontweight="bold")
    ax.set_xlabel("Revenue ($)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "3_top_products.png")
    plt.savefig(path)
    plt.close()
    print(f"✅ Saved: {path}")


# ── Chart 4: Profit Margin by Category ───────────────────────
def plot_profit_margin_by_category(df):
    cat = df.groupby("category").agg(
        revenue=("total_amount", "sum"),
        profit=("profit", "sum")
    ).reset_index()
    cat["margin_pct"] = (cat["profit"] / cat["revenue"] * 100).round(1)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(cat["category"], cat["margin_pct"],
                  color=sns.color_palette("Set2", len(cat)))
    ax.bar_label(bars, fmt="%.1f%%", padding=5, fontsize=10)
    ax.set_title("Profit Margin % by Product Category", fontsize=14, fontweight="bold")
    ax.set_xlabel("Category")
    ax.set_ylabel("Profit Margin (%)")
    ax.set_ylim(0, cat["margin_pct"].max() * 1.25)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "4_profit_margin_by_category.png")
    plt.savefig(path)
    plt.close()
    print(f"✅ Saved: {path}")


# ── Chart 5: Sales Heatmap — Region × Month ──────────────────
def plot_heatmap_region_month(df):
    pivot = df.pivot_table(
        values="total_amount", index="region",
        columns="month", aggfunc="sum"
    ).fillna(0)
    pivot.columns = [f"M{c:02d}" for c in pivot.columns]

    fig, ax = plt.subplots(figsize=(13, 4))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu",
                linewidths=0.5, ax=ax, cbar_kws={"label": "Revenue ($)"})
    ax.set_title("Revenue Heatmap: Region × Month", fontsize=14, fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Region")
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "5_heatmap_region_month.png")
    plt.savefig(path)
    plt.close()
    print(f"✅ Saved: {path}")


if __name__ == "__main__":
    print("Loading data...")
    df = load_data()
    print(f"Plotting charts for {len(df)} completed orders...\n")
    plot_monthly_trend(df)
    plot_sales_by_region(df)
    plot_top_products(df)
    plot_profit_margin_by_category(df)
    plot_heatmap_region_month(df)
    print(f"\n🎉 All charts saved to: {OUTPUT_DIR}/")
