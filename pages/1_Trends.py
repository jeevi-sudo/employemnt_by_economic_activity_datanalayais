import streamlit as st
import plotly.express as px
from utils import apply_css, load_data, sidebar_filters, plotly_layout, PALETTE

st.set_page_config(page_title="Trends", page_icon="📈", layout="wide")
apply_css()

df = load_data()
year_range, selected_countries, selected_indicators, benchmark_country, top_n = sidebar_filters(df)

mask = (
    df["Country"].isin(selected_countries) &
    df["Indicator"].isin(selected_indicators) &
    df["Year"].between(*year_range)
)
filtered = df[mask].copy()

st.markdown("# 📈 Employment Trends Over Time")
st.markdown("---")

if filtered.empty:
    st.warning("No data for selected filters. Adjust sidebar.")
    st.stop()

# ── Chart 1 + 2 ───────────────────────────────────────────────────────────────
c1, c2 = st.columns([2, 1])

with c1:
    trend = filtered.groupby(["Year", "Country", "Indicator"])["Value"].sum().reset_index()
    trend["Series"] = trend["Country"] + " · " + trend["Indicator"]
    fig = px.line(trend, x="Year", y="Value", color="Series",
                  color_discrete_sequence=PALETTE * 5,
                  labels={"Value": "Employment (000s)"})
    fig.update_traces(line=dict(width=2.5), mode="lines+markers", marker=dict(size=4))
    plotly_layout(fig, "Employment by Country & Sector", height=440)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    area_data = filtered.groupby(["Year", "Indicator"])["Value"].sum().reset_index()
    fig2 = px.area(area_data, x="Year", y="Value", color="Indicator",
                   color_discrete_sequence=PALETTE, labels={"Value": "Employment (000s)"})
    fig2.update_traces(line=dict(width=1.5))
    plotly_layout(fig2, "Total by Sector (Stacked)", height=440)
    st.plotly_chart(fig2, use_container_width=True)

# ── Chart 3: YoY Growth ───────────────────────────────────────────────────────
st.markdown("### 📉 Year-over-Year Growth Rate (%)")
yoy = (filtered.groupby(["Year", "Country"])["Value"].sum()
       .reset_index().sort_values(["Country", "Year"]))
yoy["Growth %"] = yoy.groupby("Country")["Value"].pct_change() * 100
yoy.dropna(subset=["Growth %"], inplace=True)

fig3 = px.bar(yoy, x="Year", y="Growth %", color="Country",
              barmode="group", color_discrete_sequence=PALETTE)
plotly_layout(fig3, "", height=360)
st.plotly_chart(fig3, use_container_width=True)
