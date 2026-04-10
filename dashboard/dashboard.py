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

hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
day_df["dteday"] = pd.to_datetime(day_df["dteday"])

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

# Pastikan kolom datetime
filtered_df["dteday"] = pd.to_datetime(filtered_df["dteday"])

# Ambil tanggal unik yang tersedia
available_dates = sorted(filtered_df["dteday"].dt.date.unique())

# Cegah error jika data kosong setelah filter lain
if len(available_dates) > 0:

    min_date = min(available_dates)
    max_date = max(available_dates)

    date_range = st.sidebar.date_input(
        "Filter Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Validasi jika user pilih 1 tanggal saja
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    # Filter data
    filtered_df = filtered_df[
        (filtered_df["dteday"].dt.date >= start_date) &
        (filtered_df["dteday"].dt.date <= end_date)
    ]

else:
    st.warning("Tidak ada data tersedia untuk filter yang dipilih.")


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

total = filtered_df["cnt"].sum()
casual_ratio = filtered_df["casual"].sum() / total
registered_ratio = filtered_df["registered"].sum() / total

st.success(f"""
Insight Utama:

- Total penyewaan mencapai **{total:,.0f}**, dengan dominasi pengguna **registered ({registered_ratio:.1%})**,
  menunjukkan bahwa layanan ini lebih banyak digunakan untuk **kebutuhan rutin (commuting)** dibanding rekreasi.
- Pola ini konsisten di seluruh filter, di mana pengguna registered tetap menjadi kontributor utama.
- Selain itu, faktor lingkungan seperti **suhu dan kondisi cuaca** terbukti memiliki pengaruh signifikan
  terhadap fluktuasi jumlah penyewaan.
- Dengan demikian, sistem bike sharing ini dapat dikategorikan sebagai layanan yang **utility-driven**,
  bukan sekadar leisure.
""")

st.markdown("---")
# PERTANYAAN 1

st.markdown("## 🌡️ Pengaruh Faktor Lingkungan terhadap Penyewaan")

col1, col2 = st.columns(2)

with col1:
# AGREGASI
    agg_df = filtered_df.copy()

    if analysis_level == "Hourly":
        agg_df = agg_df.groupby("dteday").agg({
            "cnt": "sum",
            "temp": "mean",
            "hum": "mean",
            "windspeed": "mean"
        }).reset_index()

    fig, ax = plt.subplots()
    corr = agg_df[["cnt", "temp", "hum", "windspeed"]].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", ax=ax)
    ax.set_title("Korelasi Variabel")
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots()
    sns.regplot(x="temp", y="cnt", data=agg_df, scatter_kws={"alpha":0.5}, ax=ax)
    ax.set_xlabel("Suhu")
    ax.set_ylabel("Jumlah Penyewaan")
    st.pyplot(fig)

col3, col4 = st.columns(2)

with col3:
    fig, ax = plt.subplots()
    sns.regplot(x="hum", y="cnt", data=agg_df, scatter_kws={"alpha":0.5}, ax=ax)
    ax.set_xlabel("Kelembaban")
    ax.set_ylabel("Jumlah Penyewaan")
    st.pyplot(fig)

with col4:
    fig, ax = plt.subplots()
    sns.regplot(x="windspeed", y="cnt", data=agg_df, scatter_kws={"alpha":0.5}, ax=ax)
    ax.set_xlabel("Kecepatan Angin")
    ax.set_ylabel("Jumlah Penyewaan")
    st.pyplot(fig)

st.info("""
Insight:

- **Suhu (temp)** menunjukkan hubungan positif yang paling kuat dengan jumlah penyewaan,
  yang berarti semakin hangat kondisi cuaca, semakin tinggi minat pengguna.
- **Kelembapan (hum)** memiliki hubungan negatif yang lemah, sehingga bukan faktor utama
  dalam menentukan keputusan pengguna.
- **Kecepatan angin (windspeed)** menunjukkan pengaruh negatif, di mana kondisi berangin
  cenderung menurunkan kenyamanan dan jumlah penyewaan.
- Secara keseluruhan, faktor lingkungan berpengaruh, namun **suhu adalah driver utama**.
""")
st.markdown("---")
# PERTANYAAN 2
st.markdown("## 🌤️ Analisis Kondisi Cuaca")

weather_stats = filtered_df.groupby("weather_condition")["cnt"].agg(["mean", "sum"]).reset_index()

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots()
    sns.barplot(data=weather_stats, x="weather_condition", y="sum", ax=ax)

    for i, v in enumerate(weather_stats["sum"]):
        ax.text(i, v, f"{v:,.0f}", ha="center", va="bottom")

    ax.set_title("Total Penyewaan per Kondisi Cuaca")
    ax.set_xlabel("Kondisi Cuaca")
    ax.set_ylabel("Total Penyewaan")
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots()
    sns.barplot(data=weather_stats, x="weather_condition", y="mean", ax=ax)
    ax.set_title("Rata-rata Penyewaan per Cuaca")
    ax.set_xlabel("Kondisi Cuaca")
    ax.set_ylabel("Rata-rata Penyewaan")
    st.pyplot(fig)

# Tren waktu
if "dteday" in filtered_df.columns:
    filtered_df["dteday"] = pd.to_datetime(filtered_df["dteday"])
    fig, ax = plt.subplots()
    trend_df = filtered_df.copy()

    if analysis_level == "Hourly":
        trend_df = trend_df.groupby(["dteday", "weather_condition"])["cnt"].sum().reset_index()

        # smoothing (rolling average)
        trend_df["cnt_smooth"] = trend_df.groupby("weather_condition")["cnt"]\
            .transform(lambda x: x.rolling(window=7, min_periods=1).mean())

    fig, ax = plt.subplots()
    sns.lineplot(data=trend_df, x="dteday", y="cnt_smooth", hue="weather_condition", ax=ax)

    ax.set_title("Tren Penyewaan Berdasarkan Cuaca")
    ax.set_xlabel("Tanggal")
    ax.set_ylabel("Jumlah Penyewaan")
    plt.xticks(rotation=45)

    st.pyplot(fig)

    top_weather = weather_stats.sort_values("sum", ascending=False).iloc[0]["weather_condition"]

st.success(f"""
Insight:

- Kondisi dengan penyewaan tertinggi adalah **{top_weather}**, yang menunjukkan bahwa kondisi ini paling optimal
  bagi pengguna untuk beraktivitas menggunakan sepeda.
- Terlihat bahwa **cuaca cerah secara konsisten menghasilkan jumlah penyewaan tertinggi**, karena memberikan kenyamanan maksimal.
- **Cuaca berawan masih cukup toleran**, dengan penurunan yang tidak terlalu drastis.
- Namun, ketika memasuki kondisi **hujan (ringan maupun lebat)**, terjadi penurunan signifikan,
  yang menunjukkan bahwa faktor cuaca buruk menjadi hambatan utama.
- Pola ini mengindikasikan bahwa keputusan pengguna sangat sensitif terhadap **kenyamanan lingkungan**, terutama kondisi hujan.
""")

# ANALISIS LANJUTAN
st.markdown("---")    
if analysis_level == "Hourly":

    st.markdown("## ⏰ Clustering Waktu Penggunaan Sepeda (Casual vs Registered)")

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
