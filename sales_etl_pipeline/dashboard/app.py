"""
dashboard/app.py — Interactive Sales Dashboard (Streamlit)

Usage:
    streamlit run dashboard/app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
        border-radius: 10px; padding: 18px 22px;
        color: white; margin-bottom: 8px;
    }
    .metric-card .label { font-size: 13px; opacity: 0.85; letter-spacing: 0.5px; }
    .metric-card .value { font-size: 26px; font-weight: 700; margin-top: 4px; }
    .metric-card .delta { font-size: 12px; margin-top: 4px; opacity: 0.75; }
    h1 { color: #1e3a5f !important; }
    .stSelectbox label, .stMultiSelect label { font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ── Data loading ──────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.join(os.path.dirname(__file__), "..")
    fact     = pd.read_csv(os.path.join(base, "data/processed/fact_sales.csv"))
    dim_prod = pd.read_csv(os.path.join(base, "data/processed/dim_product.csv"))
    dim_date = pd.read_csv(os.path.join(base, "data/processed/dim_date.csv"))
    dim_cust = pd.read_csv(os.path.join(base, "data/processed/dim_customer.csv"))

    df = fact.merge(dim_prod, on="product_id")
    df = df.merge(dim_date,  on="date_id")
    df = df.merge(dim_cust,  on="customer_id")
    return df


df_all = load_data()

# ── Sidebar filters ───────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bar-chart.png", width=60)
    st.title("🔎 Filters")

    # Status filter
    status_opts = sorted(df_all["status"].unique())
    selected_status = st.multiselect(
        "Order Status", status_opts, default=["Completed"]
    )

    # Region filter
    region_opts = sorted(df_all["region"].unique())
    selected_regions = st.multiselect(
        "Region", region_opts, default=region_opts
    )

    # Category filter
    cat_opts = sorted(df_all["category"].unique())
    selected_cats = st.multiselect(
        "Category", cat_opts, default=cat_opts
    )

    # Month slider
    min_m, max_m = int(df_all["month"].min()), int(df_all["month"].max())
    month_range = st.slider("Month Range", min_m, max_m, (min_m, max_m))

    st.markdown("---")
    st.caption("Sales Data ETL Pipeline · 2023")

# ── Apply filters ─────────────────────────────────────────────
df = df_all[
    df_all["status"].isin(selected_status) &
    df_all["region"].isin(selected_regions) &
    df_all["category"].isin(selected_cats) &
    df_all["month"].between(month_range[0], month_range[1])
].copy()

# ── Header ────────────────────────────────────────────────────
st.title("📊 Sales Analytics Dashboard")
st.markdown(f"Showing **{len(df):,}** orders · Filters applied: "
            f"Status={selected_status}, Regions={len(selected_regions)}, "
            f"Months {month_range[0]}–{month_range[1]}")
st.divider()

# ── KPI row ───────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

total_rev   = df["total_amount"].sum()
total_prof  = df["profit"].sum()
avg_margin  = df["profit_margin_pct"].mean()
total_units = df["quantity"].sum()
total_orders = len(df)

for col, label, value, fmt in zip(
    [k1, k2, k3, k4, k5],
    ["💰 Total Revenue", "📈 Total Profit", "📊 Avg Margin", "📦 Units Sold", "🧾 Orders"],
    [total_rev, total_prof, avg_margin, total_units, total_orders],
    ["${:,.0f}", "${:,.0f}", "{:.1f}%", "{:,.0f}", "{:,}"]
):
    col.markdown(f"""
    <div class="metric-card">
        <div class="label">{label}</div>
        <div class="value">{fmt.format(value)}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Monthly Trend + Region Bar ────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📅 Monthly Revenue & Profit")
    monthly = (
        df.groupby(["month", "month_name"])
        .agg(revenue=("total_amount","sum"), profit=("profit","sum"),
             orders=("order_id","count"))
        .reset_index().sort_values("month")
    )
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=monthly["month_name"].str[:3], y=monthly["revenue"],
        name="Revenue", marker_color="#90CAF9", opacity=0.85
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=monthly["month_name"].str[:3], y=monthly["profit"],
        name="Profit", mode="lines+markers",
        line=dict(color="#F44336", width=2.5),
        marker=dict(size=7, color="white", line=dict(color="#F44336", width=2))
    ), secondary_y=True)
    fig.update_layout(
        height=320, margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    fig.update_yaxes(title_text="Revenue ($)", secondary_y=False,
                     tickprefix="$", showgrid=True)
    fig.update_yaxes(title_text="Profit ($)", secondary_y=True,
                     tickprefix="$", showgrid=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🗺️ Revenue by Region")
    region_df = (
        df.groupby("region")["total_amount"].sum()
        .reset_index().sort_values("total_amount", ascending=True)
    )
    fig2 = px.bar(region_df, x="total_amount", y="region",
                  orientation="h", color="total_amount",
                  color_continuous_scale="Blues",
                  labels={"total_amount": "Revenue ($)", "region": ""})
    fig2.update_layout(
        height=320, margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    fig2.update_xaxes(tickprefix="$")
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Product Treemap + Customer Type Pie ────────────────
col3, col4 = st.columns([2, 3])

with col3:
    st.subheader("👥 Revenue by Customer Type")
    ctype = df.groupby("customer_type")["total_amount"].sum().reset_index()
    fig3 = px.pie(ctype, values="total_amount", names="customer_type",
                  color_discrete_sequence=px.colors.qualitative.Set2,
                  hole=0.45)
    fig3.update_traces(textposition="outside", textinfo="percent+label")
    fig3.update_layout(
        height=320, margin=dict(l=0, r=0, t=10, b=0), showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("📦 Product Revenue Treemap")
    prod_df = df.groupby(["category", "product_name"]).agg(
        revenue=("total_amount","sum"),
        profit=("profit","sum")
    ).reset_index()
    fig4 = px.treemap(
        prod_df, path=["category", "product_name"],
        values="revenue",
        color="profit",
        color_continuous_scale="RdYlGn",
        hover_data={"revenue": ":,.0f", "profit": ":,.0f"},
    )
    fig4.update_layout(
        height=320, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Scatter (margin vs revenue) + Heatmap ─────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("💡 Profit Margin vs Revenue by Product")
    scatter_df = df.groupby(["product_name","category"]).agg(
        revenue=("total_amount","sum"),
        margin=("profit_margin_pct","mean"),
        orders=("order_id","count")
    ).reset_index()
    fig5 = px.scatter(
        scatter_df, x="revenue", y="margin", size="orders",
        color="category", text="product_name",
        color_discrete_sequence=px.colors.qualitative.Set1,
        labels={"revenue":"Revenue ($)", "margin":"Avg Margin (%)", "orders":"Orders"},
        size_max=40
    )
    fig5.update_traces(textposition="top center", textfont_size=9)
    fig5.update_layout(
        height=340, margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    fig5.update_xaxes(tickprefix="$")
    fig5.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.subheader("🔥 Revenue Heatmap: Region × Month")
    pivot = df.pivot_table(
        values="total_amount", index="region", columns="month", aggfunc="sum"
    ).fillna(0)
    fig6 = px.imshow(
        pivot, color_continuous_scale="Blues",
        labels=dict(x="Month", y="Region", color="Revenue ($)"),
        text_auto=".0f", aspect="auto"
    )
    fig6.update_layout(
        height=340, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig6, use_container_width=True)

# ── Row 4: Data Table ─────────────────────────────────────────
st.divider()
st.subheader("📋 Raw Data Explorer")
cols_show = ["order_id", "full_date", "product_name", "category",
             "customer_name", "customer_type", "region", "quantity",
             "unit_price", "total_amount", "profit", "profit_margin_pct", "status"]

search = st.text_input("🔍 Search by product or customer name")
display_df = df[cols_show].copy()
if search:
    mask = (
        display_df["product_name"].str.contains(search, case=False, na=False) |
        display_df["customer_name"].str.contains(search, case=False, na=False)
    )
    display_df = display_df[mask]

st.dataframe(
    display_df.sort_values("order_id").reset_index(drop=True),
    use_container_width=True,
    height=350,
    column_config={
        "total_amount":      st.column_config.NumberColumn("Revenue ($)", format="$%.2f"),
        "profit":            st.column_config.NumberColumn("Profit ($)",  format="$%.2f"),
        "profit_margin_pct": st.column_config.NumberColumn("Margin %",    format="%.1f%%"),
        "unit_price":        st.column_config.NumberColumn("Unit Price",  format="$%.2f"),
    }
)
st.caption(f"Showing {len(display_df):,} of {len(df):,} rows")
