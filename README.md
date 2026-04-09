# 🚲 Bike Sharing Data Analysis Dashboard

## 📌 Deskripsi Proyek

Proyek ini bertujuan untuk menganalisis pola penggunaan layanan **bike sharing** berdasarkan faktor lingkungan (cuaca) dan waktu. Analisis dilakukan menggunakan Python (Pandas, Seaborn, Matplotlib) dan divisualisasikan dalam bentuk dashboard interaktif menggunakan Streamlit.

Dashboard ini dirancang agar dapat membantu pengguna memahami perilaku penyewaan sepeda secara intuitif, bahkan bagi pengguna non-teknis.

---

## 👤 Informasi Pembuat

- **Nama:** Ridho Akbar Fadhilah  

---

## 🎯 Business Questions

1. Sejauh mana hubungan antara faktor lingkungan seperti suhu, kelembapan, dan kecepatan angin terhadap jumlah penyewaan sepeda?
2. Bagaimana variasi kondisi cuaca memengaruhi pola penggunaan layanan penyewaan sepeda?

---

## 🔍 Analisis Lanjutan (Opsional)

Untuk memperdalam pemahaman terhadap pola penggunaan sepeda, dilakukan analisis tambahan berupa:

### Clustering Waktu Penggunaan
Data hourly dikelompokkan ke dalam tiga kategori waktu:
- **Commute Time** (07.00–09.00 & 17.00–19.00)
- **Leisure Time** (10.00–16.00)
- **Off Time** (di luar jam tersebut)

Analisis ini bertujuan untuk:
- Mengidentifikasi pola penggunaan berdasarkan waktu
- Membandingkan perilaku pengguna casual dan registered
- Melihat perbedaan pola antara hari kerja dan hari libur

---

## 📊 Insight Utama

### 1. Pengaruh Faktor Lingkungan
- Suhu memiliki korelasi positif yang cukup kuat terhadap jumlah penyewaan sepeda
- Kelembapan dan kecepatan angin cenderung berdampak negatif
- Semakin nyaman kondisi lingkungan, semakin tinggi jumlah penyewaan

### 2. Pengaruh Kondisi Cuaca
- Cuaca cerah menghasilkan jumlah penyewaan tertinggi
- Cuaca berawan masih cukup mendukung aktivitas
- Hujan menyebabkan penurunan signifikan dalam penggunaan sepeda

### 3. Pola Waktu (Hourly)
- Aktivitas tertinggi terjadi pada jam sibuk (commute time)
- Pengguna registered mendominasi pada hari kerja
- Pengguna casual meningkat saat waktu santai dan akhir pekan

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
└── url.txt (opsional)

---
```

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
* kagglehub
* streamlit

---

## 📌 Catatan Tambahan

* Dataset yang digunakan berasal dari Bike Sharing Dataset
* Data telah melalui proses cleaning, feature engineering, dan transformasi
* Dashboard mendukung dua mode analisis:

  * **Hourly (detail per jam)**
  * **Daily (ringkasan per hari)**

---

## 🌐 Deployment (Opsional)

Jika dashboard di-deploy menggunakan Streamlit Cloud, link dapat ditambahkan pada file `url.txt`.

---

## © Copyright

© 2026 Ridho Akbar Fadhilah

```

---

