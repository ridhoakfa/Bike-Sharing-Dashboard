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

season_options = df['season_name'].unique().tolist()
season = st.sidebar.multiselect(
    "Musim:",
    options=season_options,
    default=season_options
)

# FILTERING
filtered_df = df.copy()

if workingday == "Working Day":
    filtered_df = filtered_df[filtered_df["workingday"] == 1]
elif workingday == "Non-Working Day":
    filtered_df = filtered_df[filtered_df["workingday"] == 0]

filtered_df = filtered_df[filtered_df["weather_condition"].isin(weather)]

filtered_df = filtered_df[filtered_df["season_name"].isin(season)]

# Pastikan datetime
filtered_df["dteday"] = pd.to_datetime(filtered_df["dteday"])

# Ambil batas dari data
min_date = filtered_df["dteday"].min().date()
max_date = filtered_df["dteday"].max().date()

st.sidebar.markdown("### Filter Tanggal")

# Input manual
start_date = st.sidebar.date_input(
    "Tanggal Mulai",
    value=min_date,
    min_value=min_date,
    max_value=max_date
)

end_date = st.sidebar.date_input(
    "Tanggal Akhir",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)

# Validasi jika user kebalik pilih
if start_date > end_date:
    st.sidebar.warning("Tanggal mulai lebih besar dari tanggal akhir. Otomatis disesuaikan.")
    start_date, end_date = end_date, start_date

# Filter
filtered_df = filtered_df[
    (filtered_df["dteday"].dt.date >= start_date) &
    (filtered_df["dteday"].dt.date <= end_date)
]

st.sidebar.caption(f"Rentang data: {min_date} sampai {max_date}")

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
    g1 = sns.jointplot(data=agg_df, x='temp', y='cnt', kind='reg', 
                       scatter_kws={'alpha':0.4, 'color':'steelblue'}, 
                       line_kws={'color':'darkred', 'linewidth':2},
                       marginal_kws={'bins':25, 'fill':True, 'color':'steelblue'})
    g1.fig.suptitle("Suhu vs Penyewaan", y=1.02)
    st.pyplot(g1.figure)

col3, col4 = st.columns(2)

with col3:
    g2 = sns.jointplot(data=agg_df, x='hum', y='cnt', kind='reg',
                       scatter_kws={'alpha':0.4, 'color':'seagreen'},
                       line_kws={'color':'darkred', 'linewidth':2},
                       marginal_kws={'bins':25, 'fill':True, 'color':'seagreen'})
    g2.fig.suptitle("Kelembapan vs Penyewaan", y=1.02)
    st.pyplot(g2.figure)

with col4:
    g3 = sns.jointplot(data=agg_df, x='windspeed', y='cnt', kind='reg',
                       scatter_kws={'alpha':0.4, 'color':'indianred'},
                       line_kws={'color':'darkred', 'linewidth':2},
                       marginal_kws={'bins':25, 'fill':True, 'color':'indianred'})
    g3.fig.suptitle("Kecepatan Angin vs Penyewaan", y=1.02)
    st.pyplot(g3.figure)

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
st.markdown("## 🌤️ Analisis Kondisi Cuaca dan Musim")

# 1. Barplot Rata-rata per Musim & Cuaca
season_avg = filtered_df.groupby('season_name')['cnt'].mean().reindex(['Spring', 'Summer', 'Fall', 'Winter'])
weather_avg = filtered_df.groupby('weather_condition')['cnt'].mean().reindex(['Cerah', 'Berawan', 'Hujan Ringan'])

col1, col2 = st.columns(2)

with col1:
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    sns.barplot(x=season_avg.index, y=season_avg.values, ax=ax1, palette='Set3', edgecolor='black')
    ax1.set_title('Rata-rata Penyewaan per Musim')
    ax1.set_ylabel('Rata-rata Jumlah Penyewaan')
    for i, v in enumerate(season_avg.values):
        if pd.notna(v):
            ax1.text(i, v + 100, f'{v:.0f}', ha='center', fontweight='bold')
    st.pyplot(fig1)

with col2:
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.barplot(x=weather_avg.index, y=weather_avg.values, ax=ax2, palette='Set2', edgecolor='black')
    ax2.set_title('Rata-rata Penyewaan per Kondisi Cuaca')
    ax2.set_ylabel('Rata-rata Jumlah Penyewaan')
    for i, v in enumerate(weather_avg.values):
        if pd.notna(v):
            ax2.text(i, v + 100, f'{v:.0f}', ha='center', fontweight='bold')
    st.pyplot(fig2)

# 2. Boxplot Interaksi Musim dan Cuaca
st.markdown("### 📦 Distribusi Penyewaan: Interaksi Musim dan Cuaca")
fig3, ax3 = plt.subplots(figsize=(14, 6))
sns.boxplot(data=filtered_df, x='season_name', y='cnt', hue='weather_condition',
            order=['Spring', 'Summer', 'Fall', 'Winter'],
            hue_order=['Cerah', 'Berawan', 'Hujan Ringan'],
            palette='viridis', width=0.7, ax=ax3)
ax3.set_title('Interaksi Musim dan Kondisi Cuaca (2011-2012)')
ax3.set_ylabel('Jumlah Penyewaan (cnt)')
ax3.legend(title='Kondisi Cuaca', bbox_to_anchor=(1.02, 1), loc='upper left')
st.pyplot(fig3)

# 3. Lineplot Tren Bulanan per Musim
st.markdown("### 📈 Tren Rata-rata Penyewaan Bulanan per Musim")
if "year" in filtered_df.columns and "month" in filtered_df.columns:
    monthly_season = filtered_df.groupby(['year', 'month', 'season_name'])['cnt'].mean().reset_index()
    monthly_season['date'] = pd.to_datetime(monthly_season[['year', 'month']].assign(day=1))

    fig4, ax4 = plt.subplots(figsize=(14, 5))
    sns.lineplot(data=monthly_season, x='date', y='cnt', hue='season_name',
                 palette='Set1', marker='o', linewidth=2.5, markersize=8, ax=ax4)
    ax4.set_title('Tren Rata-rata Penyewaan Bulanan per Musim')
    ax4.set_ylabel('Rata-rata Penyewaan Harian')
    ax4.legend(title='Musim', bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.xticks(rotation=45)
    st.pyplot(fig4)

st.success("""
Insight:
- **Musim Gugur (Fall)** merupakan periode dengan rata-rata penyewaan tertinggi, mengungguli Musim Panas.
- Kondisi dengan penyewaan tertinggi adalah **Cuaca Cerah**, yang secara konsisten paling optimal bagi pengguna.
- Interaksi menunjukkan bahwa kombinasi **Musim Gugur + Cuaca Cerah** memberikan median penyewaan tertinggi (>7.000).
- Namun, ketika terjadi **hujan ringan**, jumlah penyewaan turun drastis di semua musim, menjadikan kombinasi **Musim Semi + Hujan Ringan** sebagai titik terendah.
- Pola tren bulanan memperlihatkan puncak permintaan yang selalu terpusat di bulan September-Oktober (awal musim gugur).
""")


# ANALISIS LANJUTAN
st.markdown("## 🔍 Analisis Lanjutan")
st.markdown("---")   
if analysis_level == "Hourly":

    st.markdown("### ⏰ Clustering Waktu Penggunaan Sepeda (Casual vs Registered)")

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

    st.info("""
    Insight:

    - Pada **Working Day**, penyewaan didominasi oleh **pengguna registered**, terutama pada **Commute Time**.
  Hal ini menunjukkan bahwa sepeda banyak digunakan untuk **aktivitas rutin seperti berangkat dan pulang kerja**.

    - Sebaliknya, pada **Non-Working Day**, terjadi peningkatan signifikan pada **pengguna casual**,
  khususnya pada **Leisure Time**, yang mengindikasikan penggunaan lebih bersifat **rekreasional**.

    - Perbandingan ini menegaskan adanya **perbedaan perilaku pengguna berdasarkan jenis hari**:
      - Hari kerja → dominan **utility-driven (transportasi)**
      - Hari libur → dominan **leisure-driven (rekreasi)**

    - Pada **Off Time (malam hari)**, jumlah penyewaan menurun drastis di semua kategori,
      menunjukkan bahwa faktor waktu (gelap/malam) menjadi **batas alami aktivitas penggunaan sepeda**.

    - Secara keseluruhan, pola ini memperlihatkan bahwa **waktu dan jenis hari adalah faktor kunci**
      dalam menentukan segmentasi pengguna dan intensitas penyewaan.
    """)

else:
    st.info("""
    Analisis waktu tidak tersedia pada level data harian (daily), karena tidak terdapat variabel jam (hour).

    Untuk memahami pola penggunaan berdasarkan waktu secara lebih detail,
    silakan gunakan mode **Hourly Analysis**.
    """)


# FOOTER
st.markdown("---")
st.caption("""
© 2026 Ridho Akbar Fadhilah
""")
