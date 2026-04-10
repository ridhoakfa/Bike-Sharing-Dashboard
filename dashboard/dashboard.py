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
import os

BASE_DIR = os.path.dirname(__file__)

hour_df = pd.read_csv(os.path.join(BASE_DIR, "main_data.csv"))
day_df = pd.read_csv(os.path.join(BASE_DIR, "day.csv"))

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

st.sidebar.markdown("### Filter Tambahan")

# Range tanggal
if "dteday" in df.columns:
    df["dteday"] = pd.to_datetime(df["dteday"])
    date_range = st.sidebar.date_input(
        "Pilih Rentang Tanggal",
        [df["dteday"].min(), df["dteday"].max()]
    )

    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df["dteday"] >= pd.to_datetime(date_range[0])) &
            (filtered_df["dteday"] <= pd.to_datetime(date_range[1]))
        ]

# HEADER
st.title(f"🚲 Bike Sharing Dashboard ({analysis_level} Analysis)")
st.markdown("""
Dashboard ini menyajikan analisis lengkap untuk menjawab:
1. Pengaruh faktor lingkungan terhadap penyewaan
2. Dampak kondisi cuaca
3. Pola perilaku pengguna berdasarkan waktu
""")

st.info("""
**Dibuat oleh:** Ridho Akbar Fadhilah  
**Dataset:** Bike Sharing Dataset
""")


# OVERVIEW
st.markdown("## 📊 Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Penyewaan", f"{int(filtered_df['cnt'].sum()):,}")
col2.metric("Total Casual", f"{int(filtered_df['casual'].sum()):,}")
col3.metric("Total Registered", f"{int(filtered_df['registered'].sum()):,}")

st.markdown("---")
    
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

# PERTANYAAN 1

st.markdown("## 🌡️ Pengaruh Faktor Lingkungan terhadap Penyewaan")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots()
    corr = filtered_df[["cnt", "temp", "hum", "windspeed"]].corr()
    sns.heatmap(corr, annot=True, ax=ax)
    ax.set_title("Korelasi Variabel")
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots()
    sns.regplot(x="temp", y="cnt", data=filtered_df, ax=ax)
    ax.set_title("Suhu vs Penyewaan")
    st.pyplot(fig)

col3, col4 = st.columns(2)

with col3:
    fig, ax = plt.subplots()
    sns.regplot(x="hum", y="cnt", data=filtered_df, ax=ax)
    ax.set_title("Kelembapan vs Penyewaan")
    st.pyplot(fig)

with col4:
    fig, ax = plt.subplots()
    sns.regplot(x="windspeed", y="cnt", data=filtered_df, ax=ax)
    ax.set_title("Windspeed vs Penyewaan")
    st.pyplot(fig)

st.info("""
Insight:
- Suhu memiliki pengaruh paling kuat (positif)
- Windspeed berdampak negatif
- Kelembapan pengaruhnya lemah
""")

# PERTANYAAN 2
st.markdown("## 🌤️ Analisis Kondisi Cuaca")

weather_stats = filtered_df.groupby("weather_condition")["cnt"].agg(["mean", "sum"]).reset_index()

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots()
    sns.barplot(data=weather_stats, x="weather_condition", y="sum", ax=ax)
    ax.set_title("Total Penyewaan per Cuaca")
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots()
    sns.barplot(data=weather_stats, x="weather_condition", y="mean", ax=ax)
    ax.set_title("Rata-rata Penyewaan per Cuaca")
    st.pyplot(fig)

# Tren waktu (khusus daily)
if "dteday" in filtered_df.columns:
    fig, ax = plt.subplots()
    sns.lineplot(data=filtered_df, x="dteday", y="cnt", hue="weather_condition", ax=ax)
    plt.xticks(rotation=30)
    ax.set_title("Tren Penyewaan berdasarkan Cuaca")
    st.pyplot(fig)

top_weather = weather_stats.sort_values("sum", ascending=False).iloc[0]["weather_condition"]

st.success(f"Kondisi terbaik untuk penyewaan: {top_weather}")


# POLA WAKTU
    
if analysis_level == "Hourly":

    st.markdown("⏰ Clustering Waktu Penggunaan Sepeda (Casual vs Registered)")

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
