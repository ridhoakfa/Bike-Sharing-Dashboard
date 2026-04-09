import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(layout="wide")

# SIDEBAR

analysis_level = st.sidebar.selectbox(
    "Pilih Level Analisis",
    ["Hourly", "Daily"]
)

st.sidebar.markdown("### Filter Data")

workingday = st.sidebar.selectbox(
    "Jenis Hari",
    ["Semua", "Working Day", "Non-Working Day"]
)


# LOAD DATA
hour_df = pd.read_csv("main_data.csv")
day_df = pd.read_csv("day.csv")  

# Pilih dataset
if analysis_level == "Hourly":
    df = hour_df.copy()
else:
    df = day_df.copy()

# Fix Kolom
if "hr" not in df.columns:
    df["hr"] = 0

if "casual" not in df.columns:
    df["casual"] = 0

if "registered" not in df.columns:
    df["registered"] = 0

weather = st.sidebar.multiselect(
    "Kondisi Cuaca:",
    options=df["weather_condition"].unique(),
    default=df["weather_condition"].unique()
)

# Filtering
filtered_df = df.copy()

if workingday == "Working Day":
    filtered_df = filtered_df[filtered_df["workingday"] == 1]
elif workingday == "Non-Working Day":
    filtered_df = filtered_df[filtered_df["workingday"] == 0]

filtered_df = filtered_df[filtered_df["weather_condition"].isin(weather)]


# HEADER
st.title(f"🚲 Bike Sharing Dashboard ({analysis_level} Analysis)")
st.markdown("""
Dashboard ini menyajikan analisis penggunaan sepeda berdasarkan **faktor lingkungan (cuaca)** 
dan **pola waktu penggunaan** untuk membantu memahami perilaku pengguna.
""")

st.info("""
**Dibuat oleh:** Ridho Akbar Fadhilah  
**Dataset:** Bike Sharing Dataset
""")

# Tabs Layout

tab1, tab2, tab3 = st.tabs([
    "Overview",
    "Analisis Cuaca",
    "Pola Waktu"
])

# TAB 1 - OVERVIEW
with tab1:

    col1, col2, col3 = st.columns(3)
    
    col1.metric("Total Penyewaan", f"{int(filtered_df['cnt'].sum()):,}")
    col2.metric("Total Casual", f"{int(filtered_df['casual'].sum()):,}")
    col3.metric("Total Registered", f"{int(filtered_df['registered'].sum()):,}")
    
    st.markdown("### 🔍 Insight Utama")

    if analysis_level == "Hourly":
        st.success("""
        Aktivitas penyewaan paling tinggi terjadi pada jam sibuk, terutama pagi dan sore hari.
        Pada hari kerja, pengguna terdaftar mendominasi karena penggunaan cenderung untuk aktivitas rutin.
        Sementara itu, pada waktu santai dan akhir pekan, pengguna casual terlihat lebih aktif.
        """)
    else:
        st.success("""
        Kondisi cuaca memiliki pengaruh besar terhadap jumlah penyewaan sepeda.
        Cuaca cerah menghasilkan jumlah penyewaan tertinggi, sedangkan hujan menurunkan penggunaan secara signifikan.
        Hal ini menunjukkan bahwa kenyamanan lingkungan menjadi faktor penting bagi pengguna.
        """)


# TAB 2 - ANALISIS CUACA
with tab2:

    st.subheader("📊 Pengaruh Faktor Lingkungan terhadap Penyewaan Sepeda")

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots()
        corr = filtered_df[["cnt", "temp", "hum", "windspeed"]].corr()
        sns.heatmap(corr, annot=True, ax=ax)
        ax.set_title("Korelasi Variabel Cuaca")
        st.pyplot(fig)

    with col2:
        weather_df = filtered_df.groupby("weather_condition")["cnt"].mean().reset_index()

        fig, ax = plt.subplots()
        sns.barplot(data=weather_df, x="weather_condition", y="cnt", ax=ax)
        ax.set_ylabel("Rata-rata Penyewaan")
        ax.set_title("Rata-rata Penyewaan per Kondisi Cuaca")
        st.pyplot(fig)

    st.caption("""
    Suhu memiliki pengaruh paling besar terhadap peningkatan jumlah penyewaan.
    Sebaliknya, angin dan kelembapan cenderung menurunkan minat pengguna.
    Selain itu, kondisi cuaca cerah terbukti menjadi kondisi paling ideal untuk aktivitas bersepeda.
    """)

    # Insight tambahan otomatis
    top_weather = weather_df.sort_values("cnt", ascending=False).iloc[0]["weather_condition"]
    st.info(f"Kondisi dengan penyewaan tertinggi: {top_weather}")


# TAB 3 - POLA WAKTU
with tab3:

    if analysis_level == "Hourly":

        st.subheader("⏰ Clustering Waktu Penggunaan Sepeda (Casual vs Registered)")

        def time_cluster(hour):
            if (7 <= hour <= 9) or (17 <= hour <= 19):
                return "Commute Time"
            elif 10 <= hour <= 16:
                return "Leisure Time"
            else:
                return "Off Time"

        filtered_df["TimeCluster"] = filtered_df["hr"].apply(time_cluster)

        cluster_summary = filtered_df.groupby(["TimeCluster", "workingday"]).agg({
            "casual": "mean",
            "registered": "mean"
        }).reset_index()

        labels = ["Commute Time", "Leisure Time", "Off Time"]
        x = np.arange(len(labels))
        width = 0.35

        wd = cluster_summary[cluster_summary["workingday"] == 1].set_index("TimeCluster").reindex(labels).fillna(0)
        nwd = cluster_summary[cluster_summary["workingday"] == 0].set_index("TimeCluster").reindex(labels).fillna(0)

        colors = {
        "wd_casual": "#A5D8FF",
        "wd_registered": "#1C7ED6",
        "nwd_casual": "#B2F2BB",
        "nwd_registered": "#2B8A3E"
        }

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.bar(x - width/2, wd["casual"], width, color=colors["wd_casual"], label="Casual (Working Day)")
        ax.bar(x - width/2, wd["registered"], width, bottom=wd["casual"], color=colors["wd_registered"], label="Registered (Working Day)")

        ax.bar(x + width/2, nwd["casual"], width, color=colors["nwd_casual"], label="Casual (Non-Working Day)")
        ax.bar(x + width/2, nwd["registered"], width, bottom=nwd["casual"], color=colors["nwd_registered"], label="Registered (Non-Working Day)")

        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylabel("Rata-rata Penyewaan")
        ax.set_title("Pola Penggunaan Berdasarkan Waktu")

        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.5)

        st.pyplot(fig)

        st.caption("""
        Pengguna terdaftar mendominasi total penyewaan pada hari kerja, terutama saat jam sibuk (Commute Time).
        Sebaliknya, pengguna kasual menunjukkan lonjakan proporsi yang signifikan pada hari libur,
        khususnya selama waktu luang (Leisure Time).
        Pola penyewaan menurun drastis saat malam hari (Off Time) di seluruh kategori pengguna.
        """)

    else:
        st.info("Analisis waktu hanya tersedia pada data hourly.")

        st.caption("""
        Data harian tidak memiliki informasi jam, sehingga analisis pola waktu tidak dapat dilakukan.
        Gunakan mode hourly untuk melihat pola penggunaan berdasarkan waktu.
        """)


# FOOTER
st.markdown("---")
st.caption("""
© 2026 Ridho Akbar Fadhilah
""")