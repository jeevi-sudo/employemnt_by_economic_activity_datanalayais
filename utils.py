import streamlit as st
import pandas as pd

PLOT_BG  = "#0f1117"
PAPER_BG = "#1a1d2e"
GRID_CLR = "#2d3154"
TEXT_CLR = "#c5c9e8"
PALETTE  = ["#6c71d6", "#48b0f1", "#f9a03f", "#5ec97e", "#f06292", "#ab7df8"]

CSS = """
<style>
    .stApp { background-color: #0f1117; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d2e 0%, #0f1117 100%);
        border-right: 1px solid #2d3154;
    }
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2140 0%, #252847 100%);
        border: 1px solid #3d4270; border-radius: 12px;
        padding: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    [data-testid="metric-container"] label { color: #8b92c4 !important; font-size: 0.8rem !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e8eaf6 !important; font-size: 1.8rem !important; }
    .section-header {
        font-size: 1.1rem; font-weight: 700; color: #7c83d6;
        letter-spacing: 0.08em; text-transform: uppercase;
        margin-bottom: 4px; padding-bottom: 6px; border-bottom: 2px solid #2d3154;
    }
    .insight-card {
        background: linear-gradient(135deg, #1e2140 0%, #252847 100%);
        border: 1px solid #3d4270; border-radius: 12px;
        padding: 18px 20px; margin-bottom: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    }
    .insight-card h4 { color: #7c83d6; margin: 0 0 8px 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.06em; }
    .insight-card p  { color: #c5c9e8; margin: 0; font-size: 0.95rem; line-height: 1.5; }
    .badge {
        display: inline-block; background: rgba(100,110,220,0.2);
        border: 1px solid #4a52a0; border-radius: 20px;
        padding: 4px 14px; font-size: 0.78rem; color: #a0a8e8; margin-right: 8px;
    }
    h1,h2,h3 { color: #e8eaf6 !important; }
    p, li { color: #c5c9e8; }
    div[data-testid="stPlotlyChart"] {
        border-radius: 12px; overflow: hidden; border: 1px solid #2d3154;
    }
</style>
"""

def apply_css():
    st.markdown(CSS, unsafe_allow_html=True)

def plotly_layout(fig, title="", height=420):
    fig.update_layout(
        title=dict(text=title, font=dict(color=TEXT_CLR, size=15, family="Inter, sans-serif")),
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        font=dict(color=TEXT_CLR, family="Inter, sans-serif"),
        xaxis=dict(gridcolor=GRID_CLR, linecolor=GRID_CLR, tickfont=dict(color=TEXT_CLR)),
        yaxis=dict(gridcolor=GRID_CLR, linecolor=GRID_CLR, tickfont=dict(color=TEXT_CLR)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_CLR)),
        height=height, margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig

@st.cache_data
def load_data():
    df = pd.read_csv("ILO_EMP.csv")
    df = df[["REF_AREA_LABEL", "INDICATOR_LABEL", "TIME_PERIOD", "OBS_VALUE"]].copy()
    df.columns = ["Country", "Indicator", "Year", "Value"]
    df["Year"]  = pd.to_numeric(df["Year"],  errors="coerce")
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df.dropna(subset=["Year", "Value"], inplace=True)
    df["Year"] = df["Year"].astype(int)
    short = {
        "Employment: ICT manufacturing": "ICT Manufacturing",
        "Employment: ICT services": "ICT Services",
        "Employment: IT services": "IT Services",
        "Employment: Publishing, broadcasting, and audiovisual services": "Publishing & Broadcasting",
        "Employment: Telecommunication services": "Telecom Services",
    }
    df["Indicator"] = df["Indicator"].map(short).fillna(df["Indicator"])
    return df

def sidebar_filters(df):
    ALL_COUNTRIES  = sorted(df["Country"].unique())
    ALL_INDICATORS = sorted(df["Indicator"].unique())
    YEAR_MIN = int(df["Year"].min())
    YEAR_MAX = int(df["Year"].max())

    with st.sidebar:
        st.markdown("## 🎛️ Filters")
        st.markdown("---")
        st.markdown('<p class="section-header">📅 Time Range</p>', unsafe_allow_html=True)
        year_range = st.slider("Select Years", YEAR_MIN, YEAR_MAX, (2000, YEAR_MAX), step=1)

        st.markdown('<p class="section-header">🌍 Countries</p>', unsafe_allow_html=True)
        default_countries = ["India", "China", "United States"] if all(
            c in ALL_COUNTRIES for c in ["India", "China", "United States"]
        ) else ALL_COUNTRIES[:3]
        selected_countries = st.multiselect("Choose Countries", ALL_COUNTRIES, default=default_countries)

        st.markdown('<p class="section-header">📊 Indicators</p>', unsafe_allow_html=True)
        selected_indicators = st.multiselect("Choose Indicators", ALL_INDICATORS, default=ALL_INDICATORS)

        st.markdown("---")
        st.markdown('<p class="section-header">🔬 Deep Analysis</p>', unsafe_allow_html=True)
        benchmark_country = st.selectbox("Benchmark Country", ALL_COUNTRIES,
                                         index=ALL_COUNTRIES.index("India") if "India" in ALL_COUNTRIES else 0)
        top_n = st.slider("Top N Countries (Rankings)", 5, 20, 10)
        st.markdown("---")
        st.caption("Data: ILO via World Bank · 1993–2024 · 151 Economies")

    if not selected_countries:
        selected_countries = ALL_COUNTRIES[:3]
    if not selected_indicators:
        selected_indicators = ALL_INDICATORS

    return year_range, selected_countries, selected_indicators, benchmark_country, top_n
