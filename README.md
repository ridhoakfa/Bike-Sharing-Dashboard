# 🚲 Bike Sharing Data Analysis Dashboard

## 📌 Deskripsi Proyek

Proyek ini menganalisis pola penggunaan layanan **bike sharing** selama periode **2011–2012** berdasarkan faktor lingkungan (suhu, kelembapan, kecepatan angin), kondisi cuaca, musim, dan waktu. Analisis dilakukan menggunakan **Python** (Pandas, Seaborn, Matplotlib, Scipy) dan divisualisasikan dalam **dashboard interaktif** menggunakan **Streamlit**.

Dashboard dirancang agar pengguna dapat mengeksplorasi data secara dinamis melalui filter level analisis (harian/jam), rentang tanggal, musim, cuaca, dan jenis hari.

---

## 👤 Informasi Pembuat

**Ridho Akbar Fadhilah**  

---

## 🎯 Pertanyaan Bisnis

1. Bagaimana hubungan antara faktor lingkungan seperti **suhu (temp)**, **kelembapan (hum)**, dan **kecepatan angin (windspeed)** terhadap jumlah penyewaan sepeda (**cnt**) selama periode **2011–2012**?

2. Bagaimana variasi **kondisi cuaca (weather_condition)** dan **musim (season_name)** memengaruhi pola penggunaan layanan penyewaan sepeda selama periode **2011–2012**, khususnya dalam perbandingan antar kategori?

---

## 🔍 Analisis Lanjutan (Clustering Waktu)

Untuk memperdalam pemahaman terhadap pola penggunaan sepeda, dilakukan analisis tambahan pada data per jam (*hourly*):

- **Commute Time** (07.00–09.00 & 17.00–19.00)
- **Leisure Time** (10.00–16.00)
- **Off Time** (di luar jam tersebut)

Tujuan analisis:

* Mengidentifikasi pola penggunaan berdasarkan waktu
* Membandingkan perilaku pengguna **casual vs registered**
* Menganalisis perbedaan pola antara hari kerja dan hari libur

---

## 📊 Insight Utama

### 1. Faktor Lingkungan

* Faktor lingkungan memiliki pengaruh terhadap jumlah penyewaan, dengan **suhu sebagai faktor yang paling dominan** pada sebagian besar kondisi.
* Kondisi yang lebih nyaman (suhu optimal, angin rendah) cenderung meningkatkan penggunaan layanan.

### 2. Cuaca & Musim

* Kondisi cuaca yang baik (cerah/berawan) menghasilkan tingkat penyewaan yang lebih tinggi.
* Kombinasi antara **musim dan cuaca** memengaruhi permintaan secara simultan.
* Terdapat periode tertentu yang secara konsisten menunjukkan permintaan lebih tinggi (pola musiman).

### 3. Pola Waktu Penggunaan

* Pada hari kerja, penggunaan didominasi oleh **registered users** pada jam sibuk (*commute time*).
* Pada hari libur, penggunaan lebih banyak terjadi pada waktu santai (*leisure time*) dengan peningkatan pengguna casual.
* Hal ini menunjukkan adanya perbedaan antara pola penggunaan **utility-driven** dan **leisure-driven**.

---

## ⚙️ Fitur Utama Dashboard

Dashboard ini memiliki beberapa fitur utama:

* 🔄 **Dual Analysis Mode**

  * *Hourly Analysis*: analisis detail per jam
  * *Daily Analysis*: analisis agregasi harian

* 🎛️ **Filter Interaktif**

  * Rentang tanggal
  * Jenis hari (working / non-working)
  * Kondisi cuaca
  * Musim

* 📊 **Visualisasi Interaktif**

  * Heatmap korelasi faktor lingkungan
  * Scatter + regression (jointplot)
  * Barplot per musim & cuaca
  * Boxplot interaksi musim & cuaca
  * Tren bulanan
  * Clustering waktu penggunaan

* 💡 **Insight Dinamis**

  * Insight otomatis menyesuaikan filter yang dipilih
  * Tidak menggunakan hardcoded insight
    
---

## 🗂️ Struktur Direktori

```

submission
├── dashboard
│   ├── main_data.csv      # Data hasil cleaning (hourly)
│   ├── day.csv            # Data harian (daily)
│   └── dashboard.py       # Dashboard Streamlit
├── data
│   ├── data_1.csv         # Dataset mentah (hour.csv)
│   └── data_2.csv         # Dataset mentah (day.csv)
├── notebook.ipynb         # Proses analisis data
├── README.md
├── requirements.txt
└── url.txt

```
---


## ⚙️ Cara Menjalankan Dashboard

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Masuk ke Folder Dashboard

```bash
cd dashboard
```

### 3. Jalankan Streamlit

```bash
streamlit run dashboard.py
```

---

## 🧰 Library yang Digunakan

* pandas
* numpy
* matplotlib
* seaborn
* kagglehub (hanya untuk notebook)
* os
* streamlit

---

## 📌 Catatan Tambahan

- Dataset: [Bike Sharing Dataset](https://www.kaggle.com/datasets/lakshmi25npathi/bike-sharing-dataset)
- Data telah melalui proses **Data Wrangling** (gathering, assessing, cleaning) serta **Exploratory Data Analysis (EDA)** lengkap (Univariate, Multivariate, Numerical, Categorical).
- Dashboard mendukung dua **mode analisis**:
  - **Hourly** – menampilkan data per jam (termasuk clustering waktu).
  - **Daily** – ringkasan harian (fokus pada pertanyaan bisnis utama).
- Filter interaktif: rentang tanggal, musim, kondisi cuaca, jenis hari.

---

## 🌐 Deployment 

[ `Bike Sharing Dashboard`](https://bike-sharing-dashboard-ridho-akfa.streamlit.app/)

---

## © Copyright

© 2026 Ridho Akbar Fadhilah

---

