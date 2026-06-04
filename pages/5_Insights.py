import streamlit as st
import plotly.express as px
from utils import  load_data, sidebar_filters, PLOT_BG, PAPER_BG, TEXT_CLR

st.set_page_config(page_title="Insights", page_icon="💡", layout="wide")

df = load_data()
year_range, selected_countries, selected_indicators, benchmark_country, top_n = sidebar_filters(df)

mask = (
    df["Country"].isin(selected_countries) &
    df["Indicator"].isin(selected_indicators) &
    df["Year"].between(*year_range)
)
filtered = df[mask].copy()

st.markdown("# 💡 Automated Insights")
st.markdown("---")

if filtered.empty:
    st.warning("Adjust filters to generate insights.")
    st.stop()

# ── Insight 1: fastest growing ────────────────────────────────────────────────
growth     = (filtered.groupby(["Country", "Year"])["Value"].sum()
              .reset_index().sort_values(["Country", "Year"]))
growth["pct"] = growth.groupby("Country")["Value"].pct_change() * 100
avg_growth    = growth.groupby("Country")["pct"].mean().dropna()

if not avg_growth.empty:
    fastest     = avg_growth.idxmax()
    fastest_val = avg_growth.max()
    slowest     = avg_growth.idxmin()
    slowest_val = avg_growth.min()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="insight-card">
          <h4>🚀 Fastest Growing Economy</h4>
          <p><strong>{fastest}</strong> leads with an average ICT employment growth of
          <strong>{fastest_val:.1f}%/year</strong> over {year_range[0]}–{year_range[1]}.</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="insight-card">
          <h4>📉 Slowest / Declining Economy</h4>
          <p><strong>{slowest}</strong> has the lowest average growth at
          <strong>{slowest_val:.1f}%/year</strong> — worth investigating for structural shifts.</p>
        </div>""", unsafe_allow_html=True)

# ── Insight 2: dominant sector ────────────────────────────────────────────────
sector_totals = filtered.groupby("Indicator")["Value"].sum().sort_values(ascending=False)
if not sector_totals.empty:
    dom_sector = sector_totals.index[0]
    dom_pct    = sector_totals.iloc[0] / sector_totals.sum() * 100
    least_sec  = sector_totals.index[-1]
    least_pct  = sector_totals.iloc[-1] / sector_totals.sum() * 100
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="insight-card">
          <h4>🏭 Dominant Sector</h4>
          <p><strong>{dom_sector}</strong> accounts for <strong>{dom_pct:.1f}%</strong>
          of total ICT employment — the largest category in this selection.</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="insight-card">
          <h4>🔍 Smallest Sector</h4>
          <p><strong>{least_sec}</strong> is the smallest at just <strong>{least_pct:.1f}%</strong>
          — possibly niche or underreported in several economies.</p>
        </div>""", unsafe_allow_html=True)

# ── Insight 3: benchmark country rank ────────────────────────────────────────
country_totals = filtered.groupby("Country")["Value"].sum().sort_values(ascending=False)
if benchmark_country in country_totals.index:
    rank = list(country_totals.index).index(benchmark_country) + 1
    bval = country_totals[benchmark_country]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="insight-card">
          <h4>📍 {benchmark_country} Ranking</h4>
          <p>Ranks <strong>#{rank}</strong> among selected countries with
          <strong>{bval:,.0f}K</strong> workers.
          {"🥇 It leads the group!" if rank == 1 else f"Leader: {country_totals.index[0]}."}</p>
        </div>""", unsafe_allow_html=True)

    coverage     = filtered.groupby("Country")["Year"].nunique()
    best_covered = coverage.idxmax()
    with c2:
        st.markdown(f"""<div class="insight-card">
          <h4>📅 Best Data Coverage</h4>
          <p><strong>{best_covered}</strong> has the most consistent data with
          <strong>{coverage.max()} years</strong> of records — ideal for time-series analysis.</p>
        </div>""", unsafe_allow_html=True)

# ── Correlation matrix ────────────────────────────────────────────────────────
st.markdown("### 🔗 Indicator Correlation Matrix")
pivot_corr = filtered.pivot_table(index=["Country", "Year"], columns="Indicator", values="Value").dropna()
if pivot_corr.shape[1] > 1:
    corr     = pivot_corr.corr()
    fig_corr = px.imshow(corr, text_auto=".2f",
                         color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
    fig_corr.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                           font=dict(color=TEXT_CLR), height=380,
                           margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_corr, use_container_width=True)
    st.caption("Values near 1.0 = sectors grow together · Near -1.0 = inverse relationship.")
else:
    st.info("Select 2+ indicators to see the correlation matrix.")

# ── Growth chart per country ──────────────────────────────────────────────────
st.markdown("### 📈 Average Annual Growth by Country")
if not avg_growth.empty:
    growth_df = avg_growth.reset_index()
    growth_df.columns = ["Country", "Avg Growth %"]
    growth_df = growth_df.sort_values("Avg Growth %", ascending=False).head(20)
    fig_g = px.bar(growth_df, x="Country", y="Avg Growth %",
                   color="Avg Growth %", color_continuous_scale="RdYlGn",
                   labels={"Avg Growth %": "Avg Annual Growth (%)"})
    fig_g.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor="#0f1117",
                        font=dict(color=TEXT_CLR), height=380,
                        margin=dict(l=10, r=10, t=30, b=60),
                        xaxis=dict(tickangle=-35, tickfont=dict(color=TEXT_CLR)),
                        yaxis=dict(gridcolor="#2d3154", tickfont=dict(color=TEXT_CLR)),
                        coloraxis_showscale=False)
    st.plotly_chart(fig_g, use_container_width=True)
