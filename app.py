
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# 1. KONFIGURASI
# =========================================================

st.set_page_config(
    page_title="Dashboard TPT Indonesia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Warna dashboard
NAVY = "#173B5E"
BLUE = "#2878A8"
LIGHT_BLUE = "#EAF2F8"
ORANGE = "#E98243"
GREEN = "#16856D"
RED = "#D95D59"
GREY = "#8998A8"
DARK = "#24364B"
BG = "#F3F6FA"

# Benchmark nasional dari notebook
NAS_FEB = 4.68
NAS_MEI = 4.65
NAS_DELTA = -0.03

# Lokasi dataset default
DEFAULT_FILE = Path(__file__).resolve().parent / "hasil_analisis_tpt.csv"

# =========================================================
# 2. CSS
# =========================================================

st.markdown("""
<style>
    .stApp {
        background-color: #F3F6FA;
        color: #24364B;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .hero {
        background: linear-gradient(115deg, #102F4D, #245579);
        color: white;
        padding: 28px 32px;
        border-radius: 16px;
        margin-bottom: 15px;
        box-shadow: 0 5px 18px rgba(20, 48, 75, 0.15);
    }

    .hero-small {
        color: #BDD3E4;
        font-size: 11px;
        letter-spacing: 2px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .hero h1 {
        color: white;
        font-size: 29px;
        line-height: 1.2;
        margin: 0;
        font-weight: 750;
    }

    .hero p {
        color: #D9E7F1;
        font-size: 13px;
        margin-top: 10px;
        margin-bottom: 0;
        line-height: 1.6;
    }

    .section-card {
        background: white;
        border: 1px solid #E5EAF0;
        border-radius: 13px;
        padding: 17px 18px;
        margin-bottom: 13px;
        box-shadow: 0 2px 8px rgba(20, 48, 75, 0.035);
    }

    .section-title {
        font-size: 17px;
        font-weight: 750;
        color: #173B5E;
        margin-bottom: 3px;
    }

    .section-subtitle {
        font-size: 11px;
        color: #718096;
        margin-bottom: 12px;
    }

    .number-circle {
        display: inline-flex;
        width: 27px;
        height: 27px;
        border-radius: 50%;
        align-items: center;
        justify-content: center;
        background: #173B5E;
        color: white;
        font-size: 13px;
        font-weight: 700;
        margin-right: 7px;
    }

    .metric-card {
        background: white;
        border: 1px solid #E6EBF1;
        border-radius: 12px;
        padding: 15px 17px;
        min-height: 112px;
        box-shadow: 0 2px 8px rgba(20, 48, 75, 0.035);
    }

    .metric-label {
        color: #718096;
        font-size: 11px;
        font-weight: 600;
        margin-bottom: 7px;
    }

    .metric-value {
        color: #173B5E;
        font-size: 28px;
        font-weight: 800;
        line-height: 1.1;
    }

    .metric-note {
        color: #8998A8;
        font-size: 10px;
        margin-top: 6px;
    }

    .insight-box {
        background: #EAF2F8;
        border-left: 4px solid #2878A8;
        padding: 12px 14px;
        border-radius: 7px;
        margin-top: 8px;
        color: #29445E;
        font-size: 12px;
        line-height: 1.6;
    }

    .footer {
        color: #8290A0;
        font-size: 10px;
        border-top: 1px solid #DFE5EC;
        padding-top: 12px;
        margin-top: 20px;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 8px;
    }

    h2 {
        color: #173B5E !important;
        font-size: 21px !important;
    }

    h3 {
        color: #173B5E !important;
        font-size: 16px !important;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. MEMBACA DATA
# =========================================================

st.sidebar.title("Pengaturan Dashboard")

uploaded_file = st.sidebar.file_uploader(
    "Upload dataset CSV",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
elif DEFAULT_FILE.exists():
    df = pd.read_csv(DEFAULT_FILE)
else:
    st.error(
        "Dataset belum ditemukan. Silakan upload "
        "hasil_analisis_tpt.csv melalui sidebar."
    )
    st.stop()

# Membersihkan nama kolom
df.columns = df.columns.str.strip()

required_columns = [
    "provinsi", "tpt_feb", "tpt_mei", "delta"
]

missing = [c for c in required_columns if c not in df.columns]

if missing:
    st.error(f"Kolom berikut belum tersedia: {missing}")
    st.stop()

# Konversi numerik
numeric_columns = [
    "tpt_feb", "tpt_mei", "delta",
    "selisih_nasional", "rank_feb",
    "rank_mei", "delta_rank",
    "prediksi", "residual"
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["provinsi", "tpt_feb", "tpt_mei"]).copy()

# Menghitung delta jika belum tersedia
if "delta" not in df.columns:
    df["delta"] = df["tpt_mei"] - df["tpt_feb"]

# Menghapus baris nasional jika ada
df = df[
    ~df["provinsi"].astype(str).str.upper().isin(
        ["INDONESIA", "NASIONAL"]
    )
].copy()

# Membuat arah perubahan jika belum tersedia
if "arah" not in df.columns:
    df["arah"] = np.select(
        [
            df["delta"] > 0,
            df["delta"] < 0
        ],
        [
            "Naik",
            "Turun"
        ],
        default="Tetap"
    )

# Warna arah perubahan
direction_colors = {
    "Naik": ORANGE,
    "Turun": BLUE,
    "Tetap": GREY
}

# Filter provinsi
all_provinces = sorted(df["provinsi"].unique())

selected_provinces = st.sidebar.multiselect(
    "Pilih provinsi",
    all_provinces,
    default=all_provinces
)

data = df[df["provinsi"].isin(selected_provinces)].copy()

if data.empty:
    st.warning("Pilih minimal satu provinsi.")
    st.stop()

# =========================================================
# 4. FUNGSI BANTU
# =========================================================

def format_num(value, decimals=2):
    return f"{value:.{decimals}f}".replace(".", ",")


def section_title(number, title, subtitle):
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;margin-bottom:4px;">
            <span class="number-circle">{number}</span>
            <span class="section-title">{title}</span>
        </div>
        <div class="section-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True
    )


def make_card(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def chart_layout(fig, height=300):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial",
            color=DARK,
            size=10
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#EDF1F5",
        zerolinecolor="#B8C4D0"
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#EDF1F5",
        zerolinecolor="#B8C4D0"
    )

    return fig


# =========================================================
# 5. HEADER DASHBOARD
# =========================================================

st.markdown("""
<div class="hero">
    <div class="hero-small">KETENAGAKERJAAN INDONESIA</div>
    <h1>TPT Nasional Menurun Tipis,<br>
    dengan Perubahan Antarprovinsi yang Beragam</h1>
    <p>
        Tingkat Pengangguran Terbuka (TPT) nasional turun 0,03 poin
        persentase pada Mei 2026. Di tingkat provinsi, perubahan
        menunjukkan pola yang beragam.
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 6. KPI NASIONAL
# =========================================================

k1, k2, k3, k4 = st.columns([1, 1, 1.1, 1.3])

with k1:
    make_card(
        "TPT Nasional Februari 2026",
        "4,68%",
        "Benchmark nasional"
    )

with k2:
    make_card(
        "TPT Nasional Mei 2026",
        "4,65%",
        "Benchmark nasional"
    )

with k3:
    make_card(
        "Perubahan Nasional",
        "−0,03",
        "Poin persentase"
    )

with k4:
    make_card(
        "Jumlah Provinsi",
        str(len(data)),
        "Provinsi dalam analisis"
    )

# Grafik mini tren nasional
st.markdown('<div class="section-card">', unsafe_allow_html=True)

mini = go.Figure()

mini.add_trace(go.Scatter(
    x=["Februari 2026", "Mei 2026"],
    y=[NAS_FEB, NAS_MEI],
    mode="lines+markers+text",
    line=dict(color=BLUE, width=3),
    marker=dict(size=9, color=NAVY),
    text=["4,68%", "4,65%"],
    textposition="top center",
    showlegend=False
))

mini.update_layout(
    height=150,
    margin=dict(l=20, r=20, t=35, b=5),
    paper_bgcolor="white",
    plot_bgcolor="white",
    yaxis=dict(
        range=[4.55, 4.80],
        visible=False
    ),
    xaxis=dict(
        showgrid=False,
        zeroline=False
    )
)

st.plotly_chart(mini, use_container_width=True)

st.markdown(
    """
    <div class="insight-box">
    <b>Catatan:</b> Angka nasional merupakan benchmark resmi dari
    notebook dan tidak dihitung dari rata-rata 38 provinsi.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 7. PERUBAHAN TPT TERBESAR
# =========================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)

section_title(
    1,
    "Provinsi dengan Perubahan TPT Terbesar",
    "Perbandingan provinsi yang mengalami penurunan dan kenaikan TPT."
)

col_down, col_up = st.columns(2)

top_down = data.nsmallest(5, "delta").sort_values("delta")
top_up = data.nlargest(5, "delta").sort_values("delta", ascending=False)

with col_down:
    st.markdown("#### 🔵 Penurunan TPT terbesar")

    fig_down = px.bar(
        top_down,
        x="delta",
        y="provinsi",
        orientation="h",
        text=top_down["delta"].map(
            lambda x: format_num(x, 2)
        ),
        color_discrete_sequence=[BLUE]
    )

    fig_down.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    fig_down.update_layout(
        xaxis_title="Perubahan (poin persentase)",
        yaxis_title="",
        xaxis=dict(autorange="reversed")
    )

    fig_down = chart_layout(fig_down, 290)
    st.plotly_chart(fig_down, use_container_width=True)

with col_up:
    st.markdown("#### 🟠 Kenaikan TPT terbesar")

    fig_up = px.bar(
        top_up,
        x="delta",
        y="provinsi",
        orientation="h",
        text=top_up["delta"].map(
            lambda x: "+" + format_num(x, 2)
        ),
        color_discrete_sequence=[ORANGE]
    )

    fig_up.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    fig_up.update_layout(
        xaxis_title="Perubahan (poin persentase)",
        yaxis_title=""
    )

    fig_up = chart_layout(fig_up, 290)
    st.plotly_chart(fig_up, use_container_width=True)

st.markdown(
    """
    <div class="insight-box">
    <b>Insight:</b> Kepulauan Riau mengalami penurunan terbesar,
    sedangkan Sulawesi Tenggara mengalami kenaikan terbesar.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 8. ARAH PERUBAHAN TPT
# =========================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)

section_title(
    2,
    "Arah Perubahan TPT di Tingkat Provinsi",
    "Distribusi provinsi berdasarkan perubahan TPT Februari–Mei 2026."
)

counts = data["arah"].value_counts()

naik = int(counts.get("Naik", 0))
turun = int(counts.get("Turun", 0))
tetap = int(counts.get("Tetap", 0))
total = len(data)

fig_direction = go.Figure()

fig_direction.add_trace(go.Bar(
    x=[turun],
    y=["Arah perubahan"],
    orientation="h",
    marker_color=BLUE,
    name="Turun",
    text=[f"{turun}"],
    textposition="inside"
))

fig_direction.add_trace(go.Bar(
    x=[tetap],
    y=["Arah perubahan"],
    orientation="h",
    marker_color=GREY,
    name="Tetap",
    text=[f"{tetap}"],
    textposition="inside"
))

fig_direction.add_trace(go.Bar(
    x=[naik],
    y=["Arah perubahan"],
    orientation="h",
    marker_color=ORANGE,
    name="Naik",
    text=[f"{naik}"],
    textposition="inside"
))

fig_direction.update_layout(
    barmode="stack",
    height=95,
    margin=dict(l=10, r=10, t=5, b=5),
    paper_bgcolor="white",
    plot_bgcolor="white",
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    legend=dict(
        orientation="h",
        y=-0.35,
        x=0.25
    )
)

st.plotly_chart(fig_direction, use_container_width=True)

a, b, c = st.columns(3)

with a:
    make_card(
        "TPT Turun",
        str(turun),
        f"{turun / total * 100:.1f}% provinsi"
    )

with b:
    make_card(
        "Tidak Berubah",
        str(tetap),
        f"{tetap / total * 100:.1f}% provinsi"
    )

with c:
    make_card(
        "TPT Naik",
        str(naik),
        f"{naik / total * 100:.1f}% provinsi"
    )

# Sensitivitas threshold
st.markdown("#### Sensitivitas batas perubahan")

threshold_data = pd.DataFrame({
    "Batas perubahan": ["0,00", "0,05", "0,10"],
    "Naik": [20, 12, 5],
    "Tetap": [2, 18, 27],
    "Turun": [16, 8, 6]
})

fig_threshold = go.Figure()

for label, color in [
    ("Turun", BLUE),
    ("Tetap", GREY),
    ("Naik", ORANGE)
]:
    fig_threshold.add_trace(go.Bar(
        x=threshold_data["Batas perubahan"],
        y=threshold_data[label],
        name=label,
        marker_color=color
    ))

fig_threshold.update_layout(
    barmode="stack",
    xaxis_title="Toleransi perubahan (poin persentase)",
    yaxis_title="Jumlah provinsi"
)

fig_threshold = chart_layout(fig_threshold, 240)
st.plotly_chart(fig_threshold, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 9. DESKRIPTIF DAN DISTRIBUSI
# =========================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)

section_title(
    3,
    "Gambaran Distribusi TPT",
    "Perbandingan sebaran TPT antarprovinsi pada Februari dan Mei 2026."
)

col1, col2 = st.columns(2)

with col1:
    dist = data.melt(
        id_vars="provinsi",
        value_vars=["tpt_feb", "tpt_mei"],
        var_name="Periode",
        value_name="TPT"
    )

    dist["Periode"] = dist["Periode"].map({
        "tpt_feb": "Februari",
        "tpt_mei": "Mei"
    })

    fig_box = px.box(
        dist,
        x="Periode",
        y="TPT",
        color="Periode",
        color_discrete_map={
            "Februari": BLUE,
            "Mei": ORANGE
        },
        points="all"
    )

    fig_box.update_layout(
        xaxis_title="",
        yaxis_title="TPT (%)",
        showlegend=False
    )

    fig_box = chart_layout(fig_box, 300)
    st.plotly_chart(fig_box, use_container_width=True)

with col2:
    fig_hist = go.Figure()

    fig_hist.add_trace(go.Histogram(
        x=data["tpt_feb"],
        name="Februari",
        opacity=0.7,
        marker_color=BLUE
    ))

    fig_hist.add_trace(go.Histogram(
        x=data["tpt_mei"],
        name="Mei",
        opacity=0.7,
        marker_color=ORANGE
    ))

    fig_hist.update_layout(
        barmode="overlay",
        xaxis_title="TPT (%)",
        yaxis_title="Jumlah provinsi"
    )

    fig_hist = chart_layout(fig_hist, 300)
    st.plotly_chart(fig_hist, use_container_width=True)

# Statistik deskriptif
stats = data[["tpt_feb", "tpt_mei"]].describe().T
stats.index = ["Februari", "Mei"]
stats.columns = [
    "Jumlah", "Rata-rata", "Standar deviasi",
    "Minimum", "Q1", "Median", "Q3", "Maksimum"
]

st.markdown("#### Statistik deskriptif")
st.dataframe(
    stats.round(2),
    use_container_width=True
)

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 10. HIERARCHICAL CLUSTERING
# =========================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)

section_title(
    4,
    "Hierarchical Clustering",
    "Pengelompokan provinsi berdasarkan TPT Mei dan perubahan TPT."
)

hc_scores = pd.DataFrame({
    "Jumlah klaster": [2, 3, 4, 5, 6],
    "Silhouette": [0.423, 0.452, 0.420, 0.354, 0.369]
})

col1, col2 = st.columns([1, 1.5])

with col1:
    fig_sil = px.bar(
        hc_scores,
        x="Jumlah klaster",
        y="Silhouette",
        text="Silhouette",
        color="Silhouette",
        color_continuous_scale=["#BFD8E8", BLUE]
    )

    fig_sil.update_traces(texttemplate="%{text:.3f}")
    fig_sil.update_layout(
        coloraxis_showscale=False,
        yaxis_range=[0, 0.55]
    )

    fig_sil = chart_layout(fig_sil, 290)
    st.plotly_chart(fig_sil, use_container_width=True)

with col2:
    if "klaster" in data.columns:
        fig_cluster = px.scatter(
            data,
            x="tpt_mei",
            y="delta",
            color="klaster",
            hover_name="provinsi",
            color_discrete_sequence=[
                "#2878A8", "#E98243", "#16856D"
            ],
            labels={
                "tpt_mei": "TPT Mei (%)",
                "delta": "Perubahan TPT (pp)",
                "klaster": "Klaster"
            }
        )

        fig_cluster.add_hline(
            y=0,
            line_dash="dash",
            line_color=GREY
        )

        fig_cluster = chart_layout(fig_cluster, 290)
        st.plotly_chart(fig_cluster, use_container_width=True)
    else:
        st.info("Kolom klaster belum tersedia pada dataset.")

st.markdown("#### Profil Hierarchical Clustering")

hc_profile = pd.DataFrame({
    "Klaster": [
        "Cluster 1",
        "Cluster 2",
        "Cluster 3"
    ],
    "Jumlah provinsi": [11, 3, 24],
    "Rata-rata TPT Mei": [5.92, 5.63, 3.52],
    "Rata-rata perubahan": [0.00, -0.32, 0.03],
    "Karakteristik": [
        "TPT tinggi, relatif stabil",
        "TPT tinggi, turun tajam",
        "TPT rendah, relatif stabil"
    ]
})

st.dataframe(
    hc_profile,
    hide_index=True,
    use_container_width=True
)

st.markdown(
    """
    <div class="insight-box">
    <b>Insight:</b> Tiga klaster dipilih karena menghasilkan
    Silhouette Score tertinggi, yaitu 0,452. Cluster 2 memiliki
    karakteristik khusus berupa TPT tinggi dengan penurunan tajam.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 11. K-MEANS
# =========================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)

section_title(
    5,
    "K-Means Clustering",
    "Evaluasi jumlah klaster menggunakan Inertia dan Silhouette Score."
)

kmeans_eval = pd.DataFrame({
    "k": [2, 3, 4, 5, 6],
    "Inertia": [40.40, 25.61, 17.26, 13.87, 11.81],
    "Silhouette": [0.413, 0.436, 0.409, 0.362, 0.380]
})

col1, col2 = st.columns(2)

with col1:
    fig_elbow = px.line(
        kmeans_eval,
        x="k",
        y="Inertia",
        markers=True,
        text="Inertia"
    )

    fig_elbow.update_traces(
        line_color=BLUE,
        line_width=3
    )

    fig_elbow = chart_layout(fig_elbow, 260)
    st.plotly_chart(fig_elbow, use_container_width=True)

with col2:
    fig_ksil = px.line(
        kmeans_eval,
        x="k",
        y="Silhouette",
        markers=True,
        text="Silhouette"
    )

    fig_ksil.update_traces(
        line_color=ORANGE,
        line_width=3
    )

    fig_ksil = chart_layout(fig_ksil, 260)
    st.plotly_chart(fig_ksil, use_container_width=True)

st.markdown("#### Profil K-Means")

km_profile = pd.DataFrame({
    "Klaster": ["Cluster 1", "Cluster 2", "Cluster 3"],
    "Jumlah provinsi": [13, 3, 22],
    "Centroid TPT Mei": [5.69, 5.63, 3.44],
    "Centroid perubahan": [-0.01, -0.32, 0.04],
    "Karakteristik": [
        "TPT tinggi, stabil",
        "TPT tinggi, turun tajam",
        "TPT rendah, stabil"
    ]
})

st.dataframe(
    km_profile,
    hide_index=True,
    use_container_width=True
)

if "kmeans" in data.columns:
    fig_km = px.scatter(
        data,
        x="tpt_mei",
        y="delta",
        color="kmeans",
        hover_name="provinsi",
        color_discrete_sequence=[
            "#2878A8", "#E98243", "#16856D"
        ],
        labels={
            "tpt_mei": "TPT Mei (%)",
            "delta": "Perubahan TPT (pp)",
            "kmeans": "Klaster K-Means"
        }
    )

    fig_km.add_hline(
        y=0,
        line_dash="dash",
        line_color=GREY
    )

    fig_km = chart_layout(fig_km, 300)
    st.plotly_chart(fig_km, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 12. PERBANDINGAN METODE CLUSTERING
# =========================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)

section_title(
    6,
    "Perbandingan Hasil Clustering",
    "Melihat kesesuaian hasil Hierarchical Clustering dan K-Means."
)

c1, c2 = st.columns(2)

with c1:
    make_card(
        "Adjusted Rand Index",
        "0,811",
        "Kesamaan hasil dua metode"
    )

with c2:
    make_card(
        "Silhouette Score",
        "0,452 vs 0,436",
        "Hierarchical vs K-Means"
    )

# Crosstab dari hasil notebook
comparison = pd.DataFrame(
    [
        [11, 0, 0],
        [0, 3, 0],
        [2, 0, 22]
    ],
    index=[
        "Hierarchical 1",
        "Hierarchical 2",
        "Hierarchical 3"
    ],
    columns=[
        "K-Means 1",
        "K-Means 2",
        "K-Means 3"
    ]
)

fig_heat = px.imshow(
    comparison,
    text_auto=True,
    color_continuous_scale="Blues",
    aspect="auto"
)

fig_heat.update_layout(
    xaxis_title="K-Means",
    yaxis_title="Hierarchical"
)

fig_heat = chart_layout(fig_heat, 280)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown(
    """
    <div class="insight-box">
    <b>Insight:</b> Kedua metode menunjukkan pola pengelompokan
    yang relatif konsisten. Dua provinsi, yaitu Kalimantan Barat
    dan Maluku Utara, berpindah kelompok dari Hierarchical
    Cluster 3 ke K-Means Cluster 1.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 13. ANALISIS KUADRAN
# =========================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)

section_title(
    7,
    "Posisi Provinsi terhadap TPT Nasional",
    "Membandingkan selisih TPT Februari terhadap benchmark nasional dan TPT Mei."
)

if "selisih_nasional" in data.columns:

    if "kuadran" in data.columns:
        color_col = "kuadran"
    else:
        color_col = "arah"

    fig_quad = px.scatter(
        data,
        x="selisih_nasional",
        y="tpt_mei",
        color=color_col,
        hover_name="provinsi",
        color_discrete_sequence=[
            BLUE, ORANGE, GREEN, GREY, RED
        ],
        labels={
            "selisih_nasional": "Selisih TPT Februari terhadap nasional (pp)",
            "tpt_mei": "TPT Mei (%)",
            color_col: "Kategori"
        }
    )

    fig_quad.add_vline(
        x=0,
        line_dash="dash",
        line_color=RED,
        annotation_text="Benchmark nasional"
    )

    fig_quad = chart_layout(fig_quad, 370)
    st.plotly_chart(fig_quad, use_container_width=True)

else:
    st.warning(
        "Kolom selisih_nasional belum tersedia pada dataset."
    )

quad_counts = pd.DataFrame({
    "Kategori": [
        "Di bawah nasional, naik",
        "Di bawah nasional, turun",
        "Di atas nasional, turun",
        "Di atas nasional, naik",
        "Di bawah nasional, tetap"
    ],
    "Jumlah": [14, 8, 8, 6, 2]
})

st.dataframe(
    quad_counts,
    hide_index=True,
    use_container_width=True
)

st.markdown(
    """
    <div class="insight-box">
    <b>Insight:</b> Provinsi di bawah benchmark nasional
    berada pada kelompok TPT rendah, sedangkan provinsi di atas
    benchmark nasional berada pada kelompok TPT tinggi.
    Analisis kuadran juga memperlihatkan arah perubahan masing-masing wilayah.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 14. SPEARMAN
# =========================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)

section_title(
    8,
    "Konsistensi Peringkat TPT Antarperiode",
    "Hubungan peringkat TPT Februari dan Mei berdasarkan korelasi Spearman."
)

col1, col2 = st.columns([1, 2])

with col1:
    make_card(
        "Korelasi Spearman",
        "0,996",
        "p-value = 2,8 × 10⁻⁴⁰"
    )

    st.markdown(
        """
        <div class="insight-box">
        Hubungan peringkat sangat kuat dan positif.
        Provinsi dengan peringkat TPT tinggi pada Februari
        cenderung tetap memiliki peringkat tinggi pada Mei.
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    if "rank_feb" in data.columns and "rank_mei" in data.columns:

        fig_rank = px.scatter(
            data,
            x="rank_feb",
            y="rank_mei",
            hover_name="provinsi",
            color_discrete_sequence=[BLUE]
        )

        fig_rank.add_shape(
            type="line",
            x0=1,
            y0=1,
            x1=38,
            y1=38,
            line=dict(
                color=ORANGE,
                dash="dash",
                width=2
            )
        )

        fig_rank.update_layout(
            xaxis_title="Peringkat Februari",
            yaxis_title="Peringkat Mei"
        )

        fig_rank = chart_layout(fig_rank, 290)
        st.plotly_chart(fig_rank, use_container_width=True)

st.markdown("#### Perubahan peringkat terbesar")

if "delta_rank" in data.columns:
    rank_change = data.assign(
        abs_change=data["delta_rank"].abs()
    ).nlargest(5, "abs_change")

    st.dataframe(
        rank_change[
            ["provinsi", "rank_feb", "rank_mei", "delta_rank"]
        ],
        hide_index=True,
        use_container_width=True
    )

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 15. UJI STATISTIK
# =========================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)

section_title(
    9,
    "Pengujian Perubahan TPT",
    "Pengujian statistik untuk melihat apakah terdapat perbedaan TPT antara Februari dan Mei."
)

test_result = pd.DataFrame({
    "Metode": [
        "Shapiro-Wilk",
        "Sign Test",
        "Wilcoxon",
        "Paired T-Test"
    ],
    "Statistik": [
        "W = 0,909",
        "20 kenaikan dari 36 perubahan",
        "315",
        "t = -0,224"
    ],
    "P-value": [
        "0,0047",
        "0,618",
        "0,777",
        "0,824"
    ],
    "Keterangan": [
        "Tidak normal",
        "Tidak signifikan",
        "Tidak signifikan",
        "Tidak signifikan"
    ]
})

st.dataframe(
    test_result,
    hide_index=True,
    use_container_width=True
)

c1, c2, c3 = st.columns(3)

with c1:
    make_card(
        "Rata-rata Perubahan",
        "−0,0045",
        "Poin persentase"
    )

with c2:
    make_card(
        "Batas Bawah CI 95%",
        "−0,0445",
        "Bootstrap"
    )

with c3:
    make_card(
        "Batas Atas CI 95%",
        "+0,0337",
        "Bootstrap"
    )

st.markdown(
    """
    <div class="insight-box">
    <b>Kesimpulan statistik:</b> Tidak ditemukan perbedaan
    TPT keseluruhan yang signifikan secara statistik antara
    Februari dan Mei 2026. Seluruh p-value pengujian utama
    berada di atas 0,05. Hal ini tidak berarti seluruh provinsi
    mengalami perubahan yang sama.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 16. REGRESI
# =========================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)

section_title(
    10,
    "Analisis Regresi Perubahan TPT",
    "Hubungan TPT Februari dengan perubahan TPT menuju Mei 2026."
)

col1, col2 = st.columns([1, 2])

with col1:
    make_card(
        "Koefisien Korelasi",
        "−0,422",
        "Hubungan negatif"
    )

    make_card(
        "R-Squared",
        "0,178",
        "Variasi yang dijelaskan model"
    )

    make_card(
        "P-value Slope",
        "0,0083",
        "Hubungan signifikan"
    )

with col2:
    if "prediksi" in data.columns:
        fig_reg = go.Figure()

        fig_reg.add_trace(go.Scatter(
            x=data["tpt_feb"],
            y=data["delta"],
            mode="markers",
            name="Data aktual",
            text=data["provinsi"],
            marker=dict(
                color=BLUE,
                size=9
            )
        ))

        reg_line = data.dropna(
            subset=["prediksi", "tpt_feb"]
        ).sort_values("tpt_feb")

        fig_reg.add_trace(go.Scatter(
            x=reg_line["tpt_feb"],
            y=reg_line["prediksi"],
            mode="lines",
            name="Garis regresi",
            line=dict(
                color=ORANGE,
                width=3
            )
        ))

        fig_reg.update_layout(
            xaxis_title="TPT Februari (%)",
            yaxis_title="Perubahan TPT (pp)"
        )

        fig_reg = chart_layout(fig_reg, 330)
        st.plotly_chart(fig_reg, use_container_width=True)

    else:
        st.info("Kolom prediksi belum tersedia pada dataset.")

st.markdown(
    """
    <div class="insight-box">
    <b>Persamaan regresi:</b><br>
    Perubahan TPT = 0,159 − 0,037 × TPT Februari.<br><br>
    Hubungan ini bersifat eksploratif dan tidak dapat
    diartikan sebagai hubungan sebab-akibat atau digunakan
    sebagai dasar prediksi jangka panjang.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 17. INSIGHT UTAMA
# =========================================================

st.markdown("""
<div class="section-card">
    <div class="section-title">🎯 Insight Utama</div>
    <div class="section-subtitle">
        Ringkasan temuan dari seluruh tahapan analisis.
    </div>
</div>
""", unsafe_allow_html=True)

ins1, ins2 = st.columns(2)

with ins1:
    st.markdown("""
    <div class="section-card">
        <b style="color:#2878A8;">01 — Perubahan Nasional</b>
        <p style="font-size:12px;">
        TPT nasional turun tipis sebesar 0,03 poin persentase,
        dari 4,68% menjadi 4,65%.
        </p>
        <b style="color:#2878A8;">02 — Perbedaan Antarprovinsi</b>
        <p style="font-size:12px;">
        Perubahan TPT tidak seragam. Terdapat provinsi yang
        mengalami penurunan cukup besar dan ada pula yang meningkat.
        </p>
    </div>
    """, unsafe_allow_html=True)

with ins2:
    st.markdown("""
    <div class="section-card">
        <b style="color:#2878A8;">03 — Konsistensi Peringkat</b>
        <p style="font-size:12px;">
        Korelasi Spearman sebesar 0,996 menunjukkan bahwa
        posisi relatif provinsi cenderung konsisten.
        </p>
        <b style="color:#2878A8;">04 — Karakteristik Wilayah</b>
        <p style="font-size:12px;">
        Clustering membedakan provinsi berdasarkan tingkat TPT
        dan arah perubahannya, termasuk kelompok TPT tinggi
        yang mengalami penurunan tajam.
        </p>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# 18. DATA DAN DOWNLOAD
# =========================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)

st.markdown("### Data Provinsi")

with st.expander("Lihat seluruh data hasil analisis"):
    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True
    )

csv_data = data.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="⬇ Download Data CSV",
    data=csv_data,
    file_name="hasil_analisis_tpt.csv",
    mime="text/csv"
)

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 19. FOOTER
# =========================================================

st.markdown("""
<div class="footer">
    <b>Sumber:</b> Badan Pusat Statistik (BPS),
    Tingkat Pengangguran Terbuka menurut Provinsi (Triwulanan), 2026.
    <br>
    <b>Catatan:</b> TPT = Tingkat Pengangguran Terbuka.
    Perubahan dihitung dalam poin persentase.
    Analisis bersifat deskriptif dan eksploratif.
</div>
""", unsafe_allow_html=True)
