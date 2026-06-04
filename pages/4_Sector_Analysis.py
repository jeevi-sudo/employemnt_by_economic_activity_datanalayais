import streamlit as st
import plotly.express as px
from utils import apply_css, load_data, sidebar_filters, plotly_layout, PALETTE, PAPER_BG, TEXT_CLR

st.set_page_config(page_title="Sector Analysis", page_icon="🔥", layout="wide")
apply_css()

df = load_data()
year_range, selected_countries, selected_indicators, benchmark_country, top_n = sidebar_filters(df)

st.markdown("# 🔥 Sector Analysis")
st.markdown("---")

base = df[df["Year"].between(*year_range) & df["Indicator"].isin(selected_indicators)]

if base.empty:
    st.warning("No data for selected filters.")
    st.stop()

# ── Treemap + Bubble ──────────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    tree_data = base.groupby(["Indicator", "Country"])["Value"].sum().reset_index()
    fig_tree  = px.treemap(tree_data,
                           path=[px.Constant("ICT Employment"), "Indicator", "Country"],
                           values="Value", color="Value", color_continuous_scale="Blues")
    fig_tree.update_layout(paper_bgcolor=PAPER_BG, font=dict(color=TEXT_CLR), height=440,
                           margin=dict(l=10, r=10, t=40, b=10),
                           title=dict(text="Treemap: Sector → Country", font=dict(color=TEXT_CLR, size=14)))
    st.plotly_chart(fig_tree, use_container_width=True)

with c2:
    bubble = (base.groupby(["Country", "Indicator"])["Value"]
              .agg(["mean", "std"]).reset_index())
    bubble.columns = ["Country", "Indicator", "Mean", "Volatility"]
    bubble.dropna(inplace=True)
    fig_bub = px.scatter(bubble, x="Mean", y="Volatility", color="Indicator",
                         size="Mean", hover_name="Country",
                         color_discrete_sequence=PALETTE,
                         labels={"Mean": "Avg Employment", "Volatility": "Std Dev"})
    plotly_layout(fig_bub, "Avg Employment vs Volatility", height=440)
    st.plotly_chart(fig_bub, use_container_width=True)

# ── Global share evolution ────────────────────────────────────────────────────
st.markdown("### 📊 Global Sector Share Evolution")
share       = base.groupby(["Year", "Indicator"])["Value"].sum().reset_index()
share_pivot = share.pivot(index="Year", columns="Indicator", values="Value").fillna(0)
share_pct   = share_pivot.div(share_pivot.sum(axis=1), axis=0) * 100
share_pct   = share_pct.reset_index().melt(id_vars="Year", var_name="Indicator", value_name="Share %")

fig_share = px.area(share_pct, x="Year", y="Share %", color="Indicator",
                    color_discrete_sequence=PALETTE, labels={"Share %": "Global Share (%)"})
fig_share.update_traces(line=dict(width=1))
plotly_layout(fig_share, "", height=360)
st.plotly_chart(fig_share, use_container_width=True)

# ── Sector summary table ──────────────────────────────────────────────────────
st.markdown("### 📋 Sector Summary")
summary = (base.groupby("Indicator")["Value"]
           .agg(Total="sum", Mean="mean", Max="max", Min="min")
           .round(1).reset_index())
st.dataframe(summary, use_container_width=True)
