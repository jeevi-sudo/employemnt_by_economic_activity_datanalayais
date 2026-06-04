import streamlit as st
import plotly.express as px
from utils import apply_css, load_data, sidebar_filters, plotly_layout, PALETTE, PLOT_BG, PAPER_BG, GRID_CLR, TEXT_CLR

st.set_page_config(page_title="Country Deep Dive", page_icon="🌍", layout="wide")
apply_css()

df = load_data()
year_range, selected_countries, selected_indicators, benchmark_country, top_n = sidebar_filters(df)

st.markdown(f"# 🌍 Country Deep Dive: {benchmark_country}")
st.markdown("---")

bench = df[
    (df["Country"] == benchmark_country) &
    (df["Year"].between(*year_range)) &
    (df["Indicator"].isin(selected_indicators))
].copy()

if bench.empty:
    st.warning(f"No data for **{benchmark_country}** in the selected range. Try changing the Benchmark Country or year range.")
    st.stop()

# ── Pie + Line ────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    pie_data = bench.groupby("Indicator")["Value"].sum().reset_index()
    fig_pie  = px.pie(pie_data, values="Value", names="Indicator",
                      color_discrete_sequence=PALETTE, hole=0.45)
    fig_pie.update_traces(textfont_color="white", textinfo="percent+label")
    plotly_layout(fig_pie, f"{benchmark_country} — Sector Mix", height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    bench_trend = bench.groupby(["Year", "Indicator"])["Value"].sum().reset_index()
    fig_b = px.line(bench_trend, x="Year", y="Value", color="Indicator",
                    color_discrete_sequence=PALETTE, markers=True,
                    labels={"Value": "Employment (000s)"})
    fig_b.update_traces(line=dict(width=2.5), marker=dict(size=5))
    plotly_layout(fig_b, f"{benchmark_country} — Sector Trends", height=400)
    st.plotly_chart(fig_b, use_container_width=True)

# ── Heatmap ───────────────────────────────────────────────────────────────────
st.markdown("### 🔥 Heatmap — Year × Sector")
pivot    = bench.pivot_table(index="Indicator", columns="Year", values="Value", aggfunc="sum")
fig_heat = px.imshow(pivot, color_continuous_scale="Blues",
                     labels=dict(color="Employment"), aspect="auto")
fig_heat.update_layout(plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
                       font=dict(color=TEXT_CLR), height=300,
                       margin=dict(l=10, r=10, t=30, b=10))
st.plotly_chart(fig_heat, use_container_width=True)

# ── Compare with selected countries ───────────────────────────────────────────
st.markdown("### 📊 Compare with Selected Countries")
compare = df[
    (df["Country"].isin(selected_countries + [benchmark_country])) &
    (df["Year"].between(*year_range)) &
    (df["Indicator"].isin(selected_indicators))
].groupby(["Year", "Country"])["Value"].sum().reset_index()

fig_cmp = px.line(compare, x="Year", y="Value", color="Country",
                  color_discrete_sequence=PALETTE, markers=True,
                  labels={"Value": "Total Employment (000s)"})
fig_cmp.update_traces(line=dict(width=2.5), marker=dict(size=4))
plotly_layout(fig_cmp, "Total ICT Employment — Country Comparison", height=400)
st.plotly_chart(fig_cmp, use_container_width=True)
