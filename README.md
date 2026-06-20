# Website Streamlit Naive Bayes Peminatan Perguruan Tinggi

Website ini digunakan untuk melakukan klasifikasi peminatan perguruan tinggi dengan dua kelas:

- Minat
- Tidak minat

## Cara menjalankan di laptop

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cara deploy ke Streamlit Cloud

1. Upload semua file ke GitHub:
   - `app.py`
   - `requirements.txt`
   - `data_peminatan_naive_bayes.xlsx`
2. Buka https://streamlit.io/cloud
3. Pilih repository GitHub
4. Main file path isi dengan: `app.py`
5. Klik Deploy

## Catatan data

Apabila file Excel belum memiliki label aktual `Minat/Tidak minat`, aplikasi akan membuat label contoh otomatis berdasarkan jurusan. Untuk penelitian sebenarnya, sebaiknya label diganti dengan hasil kuesioner atau wawancara siswa.
