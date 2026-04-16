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

# Cek apakah data tersedia setelah filtering
if filtered_df.empty:
    st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih. Silakan sesuaikan filter.")
    st.stop()

# HEADER
st.title(f"🚲 Bike Sharing Dashboard ({analysis_level} Analysis)")
st.markdown("""
Dashboard ini menyajikan analisis lengkap untuk menjawab:
1. Pengaruh faktor lingkungan terhadap penyewaan
2. Dampak kondisi cuaca dan musim
3. Pola perilaku pengguna berdasarkan waktu
""")

st.caption("📅 **Periode Data:** 1 Januari 2011 – 31 Desember 2012")

st.info("""
**Dibuat oleh:** Ridho Akbar Fadhilah  
**Dataset:** Bike Sharing Dataset
""")


# OVERVIEW
st.markdown("## 📊 Overview")
st.caption(f"📅 Data ditampilkan: **{start_date.strftime('%d %b %Y')}** – **{end_date.strftime('%d %b %Y')}**")

col1, col2, col3 = st.columns(3)

col1.metric("Total Penyewaan", f"{int(filtered_df['cnt'].sum()):,}")
col2.metric("Total Casual", f"{int(filtered_df['casual'].sum()):,}")
col3.metric("Total Registered", f"{int(filtered_df['registered'].sum()):,}")

st.markdown("---")
    
st.markdown("### 🔍 Insight Utama")

total = filtered_df["cnt"].sum()

if total > 0:
    casual_ratio = filtered_df["casual"].sum() / total
    registered_ratio = filtered_df["registered"].sum() / total
else:
    casual_ratio = 0
    registered_ratio = 0

dominant_user = "registered" if registered_ratio > casual_ratio else "casual"
dominant_ratio = max(casual_ratio, registered_ratio)

usage_type = "kebutuhan rutin (commuting)" if registered_ratio > 0.6 else "rekreasional"

st.success(f"""
- Pada periode yang dipilih, total jumlah penyewaan tercatat sebesar **{total:,.0f}**, 
  dengan dominasi pengguna **{dominant_user} ({dominant_ratio:.1%})**.

- Komposisi ini menunjukkan bahwa pola penggunaan sepeda cenderung bersifat **{usage_type}**, 
  yang mencerminkan adanya segmentasi antara pengguna rutin dan pengguna kasual.

- Perbedaan proporsi ini menjadi indikasi bahwa perilaku pengguna berpotensi dipengaruhi oleh 
  **kondisi eksternal seperti waktu, cuaca, dan musim**, yang akan dianalisis lebih lanjut pada bagian berikutnya.

- Oleh karena itu, memahami faktor lingkungan serta pola waktu penggunaan menjadi kunci 
  untuk menjawab bagaimana permintaan bike sharing dapat berubah dalam berbagai kondisi.
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
    if analysis_level == "Hourly":
        st.caption("ℹ️ Data diagregasi ke level harian untuk analisis korelasi.")

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

corr_values = agg_df[["temp", "hum", "windspeed"]].corrwith(agg_df["cnt"])

top_factor = corr_values.abs().idxmax()
top_value = corr_values[top_factor]

st.success(f"""
Insight:

- Berdasarkan hasil korelasi, variabel yang memiliki hubungan paling kuat dengan jumlah penyewaan adalah **{top_factor} ({top_value:.2f})**.

- Variabel suhu (temp) menunjukkan hubungan **{'positif' if corr_values['temp'] > 0 else 'negatif'} ({corr_values['temp']:.2f})**, 
  yang mengindikasikan bahwa perubahan suhu {'meningkatkan' if corr_values['temp'] > 0 else 'menurunkan'} jumlah penyewaan.

- Kelembapan (hum) memiliki hubungan **{'positif' if corr_values['hum'] > 0 else 'negatif'} ({corr_values['hum']:.2f})**, 
  namun pengaruhnya relatif {'lemah' if abs(corr_values['hum']) < 0.3 else 'cukup terlihat'}.

- Kecepatan angin (windspeed) menunjukkan hubungan **{'positif' if corr_values['windspeed'] > 0 else 'negatif'} ({corr_values['windspeed']:.2f})**, 
  yang mencerminkan bahwa kondisi angin dapat memengaruhi kenyamanan pengguna.

- Secara keseluruhan, faktor lingkungan memang berpengaruh terhadap jumlah penyewaan, 
  namun kekuatan pengaruhnya bergantung pada kondisi data yang dipilih melalui filter.
""")

# PERTANYAAN 2
st.markdown("## 🌤️ Analisis Kondisi Cuaca dan Musim")

# Deteksi dinamis agar "Hujan Lebat" tidak terpotong jika ada di data
order_cuaca = ['Cerah', 'Berawan', 'Hujan Ringan', 'Hujan Lebat']
cuaca_tersedia = [c for c in order_cuaca if c in filtered_df['weather_condition'].unique()]

order_musim = ['Spring', 'Summer', 'Fall', 'Winter']
musim_tersedia = [m for m in order_musim if m in filtered_df['season_name'].unique()]

# 1. Barplot Rata-rata per Musim & Cuaca
season_avg = filtered_df.groupby('season_name')['cnt'].mean().reindex(musim_tersedia)
weather_avg = filtered_df.groupby('weather_condition')['cnt'].mean().reindex(cuaca_tersedia)

col1, col2 = st.columns(2)

with col1:
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    sns.barplot(x=season_avg.index, y=season_avg.values, ax=ax1, palette='Set3', edgecolor='black', legend=False)
    ax1.set_title('Rata-rata Penyewaan per Musim')
    ax1.set_ylabel('Rata-rata Jumlah Penyewaan')
    
    # Perbaikan: Offset dinamis (5% dari nilai max) agar angka tidak melayang
    offset = season_avg.max() * 0.05
    for i, v in enumerate(season_avg.values):
        if pd.notna(v):
            ax1.text(i, v + offset, f'{v:.0f}', ha='center', fontweight='bold')
    
    # Tambah margin atas grafik agar angka tidak terpotong
    ax1.set_ylim(0, season_avg.max() + (season_avg.max() * 0.15))
    st.pyplot(fig1)

with col2:
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.barplot(x=weather_avg.index, y=weather_avg.values, ax=ax2, palette='Set2', edgecolor='black', legend=False)
    ax2.set_title('Rata-rata Penyewaan per Kondisi Cuaca')
    ax2.set_ylabel('Rata-rata Jumlah Penyewaan')
    
    # Perbaikan: Offset dinamis
    offset = weather_avg.max() * 0.05
    for i, v in enumerate(weather_avg.values):
        if pd.notna(v):
            ax2.text(i, v + offset, f'{v:.0f}', ha='center', fontweight='bold')
            
    ax2.set_ylim(0, weather_avg.max() + (weather_avg.max() * 0.15))
    st.pyplot(fig2)
    if analysis_level == "Hourly":
        st.caption("ℹ️ Dalam mode Hourly, nilai rata-rata adalah **penyewaan per jam**, sehingga angkanya lebih kecil dibandingkan mode Daily (penyewaan per hari).")

# 2. Boxplot Interaksi Musim dan Cuaca
st.markdown("### 📦 Distribusi Penyewaan: Interaksi Musim dan Cuaca")
fig3, ax3 = plt.subplots(figsize=(14, 6))

if analysis_level == "Hourly":
    box_df = filtered_df.groupby(["dteday", "season_name", "weather_condition"])["cnt"].sum().reset_index()
else:
    box_df = filtered_df.copy()

sns.boxplot(data=box_df, x='season_name', y='cnt', hue='weather_condition',
            order=musim_tersedia,
            hue_order=cuaca_tersedia,
            palette='viridis', width=0.7, ax=ax3)

ax3.set_title('Distribusi Penyewaan Sepeda: Interaksi Musim dan Kondisi Cuaca (2011-2012)')
ax3.set_ylabel('Jumlah Penyewaan (cnt)')
ax3.legend(title='Kondisi Cuaca', bbox_to_anchor=(1.02, 1), loc='upper left')
st.pyplot(fig3)

if analysis_level == "Hourly":
    st.caption("ℹ️ Pada mode Hourly, data diagregasi menjadi total harian agar boxplot representatif dan tidak terlihat 'gepeng' karena jam malam yang sepi.")

# 3. Lineplot Tren Bulanan per Musim
st.markdown("### 📈 Tren Rata-rata Penyewaan Bulanan per Musim")
if "year" in filtered_df.columns and "month" in filtered_df.columns:
    monthly_season = filtered_df.groupby(['year', 'month', 'season_name'])['cnt'].mean().reset_index()
    monthly_season['date'] = pd.to_datetime(monthly_season[['year', 'month']].assign(day=1))

    if not monthly_season.empty:
        fig4, ax4 = plt.subplots(figsize=(14, 5))
        sns.lineplot(data=monthly_season, x='date', y='cnt', hue='season_name',
                     hue_order=musim_tersedia,
                     palette='Set1', marker='o', linewidth=2.5, markersize=8, ax=ax4)
        ax4.set_title('Tren Rata-rata Penyewaan Bulanan per Musim')
        ax4.set_ylabel('Rata-rata Penyewaan')
        ax4.legend(title='Musim', bbox_to_anchor=(1.02, 1), loc='upper left')
        plt.xticks(rotation=45)
        st.pyplot(fig4)
    else:
        st.warning("Data bulanan tidak tersedia untuk filter yang dipilih.")

top_season = season_avg.idxmax()
top_season_val = season_avg.max()

top_weather = weather_avg.idxmax()
top_weather_val = weather_avg.max()

interaction = box_df.groupby(["season_name", "weather_condition"])["cnt"].median().idxmax()

st.success(f"""
Insight:

- Musim dengan rata-rata jumlah penyewaan tertinggi adalah **{top_season} ({top_season_val:.0f})**,
  menunjukkan bahwa periode ini paling optimal untuk aktivitas bike sharing pada data yang ditampilkan.

- Kondisi cuaca dengan rata-rata penyewaan tertinggi adalah **{top_weather} ({top_weather_val:.0f})**,
  yang mengindikasikan bahwa kondisi cuaca berperan penting dalam menentukan tingkat penggunaan.

- Distribusi pada boxplot menunjukkan adanya variasi jumlah penyewaan di setiap kombinasi musim dan cuaca,
  yang menandakan bahwa **interaksi antara kedua faktor ini memengaruhi permintaan secara bersamaan**.

- Kombinasi dengan median penyewaan tertinggi terjadi pada **{interaction[0]} + {interaction[1]}**.  

- Pada kondisi cuaca yang kurang mendukung (seperti hujan), jumlah penyewaan cenderung lebih rendah
  dibandingkan kondisi cuaca yang lebih baik.

- Tren bulanan memperlihatkan adanya periode tertentu dengan peningkatan penyewaan,
  yang mencerminkan pola musiman dalam penggunaan layanan bike sharing.
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

# Ambil dominasi per kondisi
wd_peak = wd.sum(axis=1).idxmax()
nwd_peak = nwd.sum(axis=1).idxmax()

wd_dominant = "registered" if wd["registered"].sum() > wd["casual"].sum() else "casual"
nwd_dominant = "registered" if nwd["registered"].sum() > nwd["casual"].sum() else "casual"

st.info(f"""
Insight:

- Pada **Working Day**, periode dengan aktivitas tertinggi terjadi pada **{wd_peak}**, 
  dengan dominasi pengguna **{wd_dominant}**, yang mencerminkan pola penggunaan untuk aktivitas rutin.

- Pada **Non-Working Day**, aktivitas tertinggi terjadi pada **{nwd_peak}**, 
  dengan kecenderungan dominasi pengguna **{nwd_dominant}**, yang menunjukkan pola penggunaan yang lebih fleksibel.

- Perbandingan ini menunjukkan adanya **perbedaan pola penggunaan berdasarkan jenis hari**, 
  di mana waktu penggunaan dan tipe pengguna dapat berubah mengikuti konteks aktivitas.

- Secara umum, aktivitas penyewaan cenderung lebih rendah pada periode **Off Time**, 
  yang mengindikasikan adanya pengaruh faktor waktu terhadap intensitas penggunaan.

- Temuan ini menegaskan bahwa **waktu dan jenis hari merupakan faktor penting**
  dalam memahami segmentasi pengguna dan dinamika permintaan bike sharing.
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
