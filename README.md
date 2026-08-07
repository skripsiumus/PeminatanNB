# Streamlit Naive Bayes — SMK Al-Ikhlas Losari

Aplikasi klasifikasi minat pendidikan tinggi siswa kelas XII menggunakan algoritma Naive Bayes dengan data gabungan tahun ajaran 2024–2025 dan 2025–2026 sebanyak 596 siswa.

## Login demo lokal

- Username: `admin`
- Password: `admin123`

Untuk deployment, gunakan Streamlit Secrets agar password tidak ditulis langsung di source code.

## Menjalankan di komputer

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy ke Streamlit Community Cloud

1. Buat repository GitHub baru.
2. Unggah `app.py`, `requirements.txt`, dan `Data_Siswa_Kelas_XII_Gabungan.xlsx`.
3. Masuk ke Streamlit Community Cloud dan pilih **Create app**.
4. Pilih repository, branch `main`, dan main file `app.py`.
5. Buka **Advanced settings > Secrets**, lalu isi:

```toml
[login]
username = "admin"
password = "password_kuat_anda"
```

6. Klik **Deploy**.

Jangan unggah file `.streamlit/secrets.toml` yang berisi password asli ke GitHub.
