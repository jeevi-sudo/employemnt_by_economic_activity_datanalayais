import streamlit as st
import plotly.express as px
from utils import apply_css, load_data, sidebar_filters, PALETTE, PLOT_BG, PAPER_BG, GRID_CLR, TEXT_CLR

st.set_page_config(page_title="Rankings", page_icon="🏆", layout="wide")
apply_css()

df = load_data()
year_range, selected_countries, selected_indicators, benchmark_country, top_n = sidebar_filters(df)

st.markdown("# 🏆 Country Rankings by Sector")
st.markdown("---")

latest_year  = df[df["Year"].between(*year_range)]["Year"].max()
latest_data  = df[
    (df["Year"] == latest_year) & (df["Indicator"].isin(selected_indicators))
].groupby(["Country", "Indicator"])["Value"].sum().reset_index()

st.markdown(f"#### Showing Top **{top_n}** countries per sector · Latest year: **{latest_year}**")
st.markdown("<br>", unsafe_allow_html=True)

if latest_data.empty:
    st.warning("No data available. Adjust year range or indicators.")
    st.stop()

cols = st.columns(2)
for i, ind in enumerate(selected_indicators):
    ind_data = (latest_data[latest_data["Indicator"] == ind]
                .nlargest(top_n, "Value")
                .sort_values("Value"))
    if ind_data.empty:
        continue
    fig_rank = px.bar(ind_data, x="Value", y="Country", orientation="h",
                      color="Value", color_continuous_scale="Blues",
                      labels={"Value": "Employment (000s)"})
    fig_rank.update_layout(
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, font=dict(color=TEXT_CLR),
        coloraxis_showscale=False, height=380,
        margin=dict(l=10, r=10, t=45, b=10),
        title=dict(text=f"🏆 {ind} ({latest_year})", font=dict(color=TEXT_CLR, size=13)),
        yaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=TEXT_CLR)),
        xaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=TEXT_CLR)),
    )
    cols[i % 2].plotly_chart(fig_rank, use_container_width=True)

# ── Overall ranking table ─────────────────────────────────────────────────────
st.markdown("### 📋 Overall Rankings Table")
overall = (df[df["Year"].between(*year_range) & df["Indicator"].isin(selected_indicators)]
           .groupby("Country")["Value"].sum()
           .reset_index()
           .sort_values("Value", ascending=False)
           .reset_index(drop=True))
overall.index += 1
overall.columns = ["Country", "Total Employment (000s)"]
overall["Total Employment (000s)"] = overall["Total Employment (000s)"].round(1)
st.dataframe(overall.head(30), use_container_width=True)
