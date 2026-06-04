import streamlit as st
from utils import load_data, sidebar_filters

st.set_page_config(page_title="ILO ICT Dashboard", page_icon="📡", layout="wide")


df = load_data()
year_range, selected_countries, selected_indicators, benchmark_country, top_n = sidebar_filters(df)

mask = (
    df["Country"].isin(selected_countries) &
    df["Indicator"].isin(selected_indicators) &
    df["Year"].between(*year_range)
)
filtered = df[mask]

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,#1a1f4e 0%,#0d1b3e 50%,#1a2a4e 100%);
     border:1px solid #3d4a7a;border-radius:16px;padding:36px 40px;
     margin-bottom:28px;box-shadow:0 8px 32px rgba(0,0,0,0.4);">
  <div style="font-size:2.2rem;font-weight:800;color:#e8eaf6;">📡 ILO ICT Employment Analytics</div>
  <div style="font-size:1rem;color:#8b92c4;margin-top:8px;">
      Global ICT sector employment trends across 151 economies · 1993–2024
  </div>
  <div style="margin-top:16px;">
    <span class="badge">📅 {year_range[0]}–{year_range[1]}</span>
    <span class="badge">🌍 {len(selected_countries)} Countries</span>
    <span class="badge">📊 {len(selected_indicators)} Indicators</span>
    <span class="badge">🔢 {len(filtered):,} Data Points</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
total_emp   = filtered["Value"].sum()
avg_emp     = filtered["Value"].mean()
top_country = filtered.groupby("Country")["Value"].sum().idxmax() if not filtered.empty else "—"
top_sector  = filtered.groupby("Indicator")["Value"].sum().idxmax() if not filtered.empty else "—"
prev_mask   = (df["Country"].isin(selected_countries) & df["Indicator"].isin(selected_indicators) &
               df["Year"].between(year_range[0]-1, year_range[1]-1))
prev_emp    = df[prev_mask]["Value"].sum()
delta_pct   = ((total_emp - prev_emp) / prev_emp * 100) if prev_emp > 0 else 0

k1.metric("Total Employment (000s)", f"{total_emp/1000:,.1f}K", f"{delta_pct:+.1f}% vs prev period")
k2.metric("Avg per Country/Year", f"{avg_emp:,.1f}")
k3.metric("Top Country", top_country)
k4.metric("Dominant Sector", top_sector)

st.markdown("<br>", unsafe_allow_html=True)

# ── About cards ───────────────────────────────────────────────────────────────
st.markdown("### 📖 About This Dashboard")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""<div class="insight-card">
      <h4>📊 Dataset</h4>
      <p>Employment by Economic Activity from the International Labour Organization (ILO),
      covering 5 ICT sectors across 151 economies from 1993 to 2024.</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="insight-card">
      <h4>🗂️ Pages</h4>
      <p>Use the sidebar to navigate: Trends, Country Deep Dive, Rankings,
      Sector Analysis, and auto-generated Insights.</p>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="insight-card">
      <h4>🎛️ Filters</h4>
      <p>All filters in the sidebar apply across every page — set your countries,
      years, and indicators once and explore freely.</p>
    </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<center style='color:#4a5270;font-size:0.8rem;'>ILO ICT Employment Dashboard · Data: ILO via World Bank · Built with Streamlit & Plotly</center>",
            unsafe_allow_html=True)
