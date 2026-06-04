import streamlit as st
import pandas as pd

PLOT_BG  = "#0f1117"
PAPER_BG = "#1a1d2e"
GRID_CLR = "#2d3154"
TEXT_CLR = "#c5c9e8"
PALETTE  = ["#6c71d6", "#48b0f1", "#f9a03f", "#5ec97e", "#f06292", "#ab7df8"]



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
