import io
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# =========================================================
# KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(
    page_title="Naive Bayes Peminatan PT",
    page_icon="🎓",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 34px;
        font-weight: 800;
        color: #14532d;
        margin-bottom: 0px;
    }
    .subtitle {
        font-size: 16px;
        color: #475569;
        margin-top: 0px;
        margin-bottom: 22px;
    }
    .metric-card {
        padding: 18px;
        border-radius: 18px;
        background: linear-gradient(135deg, #ecfdf5, #f8fafc);
        border: 1px solid #bbf7d0;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }
    .metric-label {
        color: #475569;
        font-size: 14px;
        margin-bottom: 6px;
    }
    .metric-value {
        color: #14532d;
        font-size: 28px;
        font-weight: 800;
    }
    .note-box {
        padding: 14px 18px;
        border-radius: 14px;
        background-color: #fffbeb;
        border: 1px solid #fde68a;
        color: #713f12;
    }
    .success-box {
        padding: 18px;
        border-radius: 16px;
        background-color: #dcfce7;
        border: 1px solid #86efac;
        color: #14532d;
        font-size: 20px;
        font-weight: 800;
        text-align: center;
    }
    .danger-box {
        padding: 18px;
        border-radius: 16px;
        background-color: #fee2e2;
        border: 1px solid #fca5a5;
        color: #7f1d1d;
        font-size: 20px;
        font-weight: 800;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# HALAMAN LOGIN
# =========================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""


def get_login_credentials() -> tuple[str, str]:
    """Mengambil kredensial dari Streamlit Secrets dengan fallback lokal."""
    try:
        username = st.secrets["login"]["username"]
        password = st.secrets["login"]["password"]
        return str(username), str(password)
    except (KeyError, FileNotFoundError):
        return "admin", "admin123"


if not st.session_state.authenticated:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stHeader"] {background: transparent;}
        .block-container {max-width: 920px; padding-top: 3rem; padding-bottom: 3rem;}
        .login-card {
            padding: 42px 46px 28px 46px;
            border-radius: 28px;
            text-align: center;
            background: linear-gradient(145deg, #ecfdf5 0%, #ffffff 52%, #eff6ff 100%);
            border: 1px solid #bbf7d0;
            box-shadow: 0 22px 55px rgba(15, 23, 42, 0.13);
        }
        .login-icon {font-size: 64px; margin-bottom: 4px;}
        .login-title {font-size: 42px; font-weight: 900; color: #14532d; margin-bottom: 8px;}
        .login-subtitle {font-size: 21px; font-weight: 750; color: #0f172a; line-height: 1.4;}
        .login-description {color: #64748b; margin: 14px auto 8px auto; max-width: 680px;}
        .login-footer {text-align: center; color: #64748b; font-size: 13px; margin-top: 22px;}
        div.stButton > button {
            min-height: 50px; border-radius: 14px; border: 0; font-size: 17px;
            font-weight: 800; background: linear-gradient(90deg, #15803d, #0f766e);
            color: white; box-shadow: 0 10px 24px rgba(21, 128, 61, 0.22);
        }
        div.stButton > button:hover {color: white; border: 0; transform: translateY(-1px);}
        </style>
        <div class="login-card">
            <div class="login-icon">🎓</div>
            <div class="login-title">LOGIN SISTEM</div>
            <div class="login-subtitle">
                Sistem Klasifikasi Minat Pendidikan Tinggi<br>
                Siswa SMK Al-Ikhlas Losari
            </div>
            <div class="login-description">
                Masukkan username dan password untuk mengakses dashboard klasifikasi Naive Bayes.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    left, center, right = st.columns([1.15, 1.7, 1.15])
    with center:
        with st.form("login_form", clear_on_submit=False):
            username_input = st.text_input("Username", placeholder="Masukkan username")
            password_input = st.text_input("Password", type="password", placeholder="Masukkan password")
            login_button = st.form_submit_button("🔐 LOGIN", use_container_width=True)

        if login_button:
            valid_username, valid_password = get_login_credentials()
            if username_input == valid_username and password_input == valid_password:
                st.session_state.authenticated = True
                st.session_state.username = username_input
                st.success("Login berhasil. Mengarahkan ke dashboard...")
                st.rerun()
            else:
                st.error("Username atau password salah.")

        with st.expander("Informasi akun demo"):
            st.caption("Username: admin | Password: admin123")

    st.markdown(
        '<div class="login-footer">© 2026 SMK Al-Ikhlas Losari — Sistem Klasifikasi Minat Pendidikan Tinggi</div>',
        unsafe_allow_html=True,
    )
    st.stop()

DEFAULT_DATA_FILE = Path(__file__).with_name("data_peminatan_naive_bayes.xlsx")
FEATURES = ["Jurusan", "Rombel", "Jenis Kelamin"]
TARGET = "Label Aktual/Latih (editable)"
CLASS_MINAT = "Minat"
CLASS_TIDAK = "Tidak minat"
CLASSES = [CLASS_MINAT, CLASS_TIDAK]


# =========================================================
# FUNGSI DATA
# =========================================================
@st.cache_data(show_spinner=False)
def read_excel_file(file_bytes: bytes | None, default_path: str) -> pd.DataFrame:
    """Membaca file Excel dari upload atau file default."""
    if file_bytes is not None:
        xls = pd.ExcelFile(io.BytesIO(file_bytes))
    else:
        xls = pd.ExcelFile(default_path)

    if "Data_Siswa" in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name="Data_Siswa")
    elif "Data Gabungan" in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name="Data Gabungan")
    else:
        df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])

    # Hilangkan kolom kosong karena ekspor Excel kadang membawa kolom Unnamed.
    df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed", regex=True)]

    # Pastikan kolom utama tersedia.
    missing = [col for col in FEATURES if col not in df.columns]
    if missing:
        raise ValueError(f"Kolom wajib tidak ditemukan: {', '.join(missing)}")

    # Jika label belum ada, buat label contoh agar Naive Bayes dapat dilatih.
    if TARGET not in df.columns:
        df[TARGET] = np.where(
            df["Jurusan"].astype(str).str.upper().str.startswith("MP"),
            CLASS_MINAT,
            CLASS_TIDAK,
        )

    # Normalisasi data teks.
    for col in FEATURES + [TARGET]:
        df[col] = df[col].astype(str).str.strip()

    # Ambil baris yang valid saja.
    df = df[df[TARGET].isin(CLASSES)].copy()
    df = df.dropna(subset=FEATURES)
    df = df.reset_index(drop=True)

    return df


def train_naive_bayes(df: pd.DataFrame, features: list[str], target: str) -> dict:
    """Melatih Naive Bayes kategorikal secara manual dengan Laplace Smoothing."""
    total_data = len(df)
    class_count = {kelas: int((df[target] == kelas).sum()) for kelas in CLASSES}
    priors = {
        kelas: (class_count[kelas] / total_data if total_data else 0)
        for kelas in CLASSES
    }

    categories = {
        feature: sorted(df[feature].dropna().astype(str).unique().tolist())
        for feature in features
    }

    likelihood_tables: dict[str, pd.DataFrame] = {}
    for feature in features:
        rows = []
        k = len(categories[feature])
        for kategori in categories[feature]:
            item = {"Kategori": kategori}
            for kelas in CLASSES:
                count_x_c = int(((df[feature] == kategori) & (df[target] == kelas)).sum())
                denominator = class_count[kelas] + k
                prob = (count_x_c + 1) / denominator if denominator else 0
                item[f"Count {kelas}"] = count_x_c
                item[f"P(X|{kelas})"] = prob
            rows.append(item)
        likelihood_tables[feature] = pd.DataFrame(rows)

    return {
        "class_count": class_count,
        "priors": priors,
        "categories": categories,
        "likelihood_tables": likelihood_tables,
        "features": features,
        "target": target,
    }


def predict_single(input_data: dict, model: dict) -> dict:
    """Menghitung skor, probabilitas, dan keputusan satu data."""
    scores = {}
    detail = []

    for kelas in CLASSES:
        score = model["priors"].get(kelas, 0)
        row_detail = {
            "Kelas": kelas,
            "Prior": score,
        }
        for feature in model["features"]:
            value = str(input_data[feature])
            table = model["likelihood_tables"][feature]
            col_prob = f"P(X|{kelas})"

            if value in table["Kategori"].values:
                prob = float(table.loc[table["Kategori"] == value, col_prob].iloc[0])
            else:
                # Jika kategori baru tidak ada di data latih, pakai Laplace smoothing minimum.
                k = len(model["categories"][feature]) + 1
                prob = 1 / (model["class_count"][kelas] + k)

            score *= prob
            row_detail[f"P({feature}|{kelas})"] = prob

        scores[kelas] = score
        row_detail["Skor Akhir"] = score
        detail.append(row_detail)

    total_score = sum(scores.values())
    if total_score == 0:
        probability = {kelas: 0 for kelas in CLASSES}
    else:
        probability = {kelas: scores[kelas] / total_score for kelas in CLASSES}

    keputusan = CLASS_MINAT if probability[CLASS_MINAT] >= probability[CLASS_TIDAK] else CLASS_TIDAK

    return {
        "scores": scores,
        "probability": probability,
        "keputusan": keputusan,
        "detail": pd.DataFrame(detail),
    }


def add_predictions(df: pd.DataFrame, model: dict) -> pd.DataFrame:
    """Menambahkan kolom hasil prediksi ke seluruh data siswa."""
    result = df.copy()
    skor_minat = []
    skor_tidak = []
    prob_minat = []
    prob_tidak = []
    keputusan = []

    for _, row in result.iterrows():
        pred = predict_single({feature: row[feature] for feature in FEATURES}, model)
        skor_minat.append(pred["scores"][CLASS_MINAT])
        skor_tidak.append(pred["scores"][CLASS_TIDAK])
        prob_minat.append(pred["probability"][CLASS_MINAT])
        prob_tidak.append(pred["probability"][CLASS_TIDAK])
        keputusan.append(pred["keputusan"])

    result["Skor NB Minat"] = skor_minat
    result["Skor NB Tidak minat"] = skor_tidak
    result["Probabilitas Minat"] = prob_minat
    result["Probabilitas Tidak minat"] = prob_tidak
    result["Keputusan NB"] = keputusan
    result["Keterangan"] = np.where(
        result["Keputusan NB"] == result[TARGET],
        "Sesuai label latih",
        "Berbeda dari label latih",
    )
    return result


def make_excel_download(df_pred: pd.DataFrame, model: dict) -> bytes:
    """Membuat file Excel hasil prediksi untuk diunduh."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_pred.to_excel(writer, index=False, sheet_name="Hasil_Prediksi")

        prior_df = pd.DataFrame(
            {
                "Kelas": CLASSES,
                "Jumlah": [model["class_count"][kelas] for kelas in CLASSES],
                "Prior": [model["priors"][kelas] for kelas in CLASSES],
            }
        )
        prior_df.to_excel(writer, index=False, sheet_name="Prior_Kelas")

        for feature, table in model["likelihood_tables"].items():
            sheet_name = feature.replace(" ", "_")[:31]
            table.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()


def metric_card(label: str, value: str):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("🎓 Naive Bayes")
st.sidebar.caption("Klasifikasi Minat Pendidikan Tinggi")

st.sidebar.success(f"Login sebagai: {st.session_state.username}")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.rerun()


uploaded_file = st.sidebar.file_uploader(
    "Upload Excel data siswa",
    type=["xlsx", "xls"],
    help="Gunakan file default atau upload file Excel yang memiliki kolom Jurusan, Rombel, dan Jenis Kelamin.",
)

menu = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Prediksi Manual", "Data Siswa", "Probabilitas", "Rumus"],
)

# =========================================================
# LOAD DATA
# =========================================================
try:
    file_bytes = uploaded_file.getvalue() if uploaded_file is not None else None
    df = read_excel_file(file_bytes, str(DEFAULT_DATA_FILE))
    model = train_naive_bayes(df, FEATURES, TARGET)
    df_pred = add_predictions(df, model)
except Exception as exc:
    st.error(f"Data tidak dapat dibaca: {exc}")
    st.stop()

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="main-title">Website Klasifikasi Minat Pendidikan Tinggi</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Analisis data siswa kelas XII tahun 2026 menggunakan metode Naive Bayes dengan dua keputusan: <b>Minat</b> dan <b>Tidak minat</b>.</div>',
    unsafe_allow_html=True,
)

if TARGET not in pd.read_excel(DEFAULT_DATA_FILE, sheet_name="Data_Siswa", nrows=1).columns and uploaded_file is None:
    st.warning("File default belum memiliki label asli. Aplikasi memakai label simulasi dan harus diganti dengan hasil kuesioner untuk penelitian final.")

# =========================================================
# MENU DASHBOARD
# =========================================================
if menu == "Dashboard":
    total_siswa = len(df_pred)
    total_minat = int((df_pred["Keputusan NB"] == CLASS_MINAT).sum())
    total_tidak = int((df_pred["Keputusan NB"] == CLASS_TIDAK).sum())
    akurasi = float((df_pred["Keputusan NB"] == df_pred[TARGET]).mean()) if total_siswa else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total siswa", f"{total_siswa}")
    with c2:
        metric_card("Keputusan Minat", f"{total_minat}")
    with c3:
        metric_card("Keputusan Tidak minat", f"{total_tidak}")
    with c4:
        metric_card("Akurasi model", f"{akurasi:.2%}")

    st.markdown("---")

    left, right = st.columns([1, 1])

    with left:
        rekap = df_pred["Keputusan NB"].value_counts().reset_index()
        rekap.columns = ["Keputusan", "Jumlah"]
        fig_pie = px.pie(
            rekap,
            names="Keputusan",
            values="Jumlah",
            title="Persentase Keputusan Peminatan",
            hole=0.45,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)

    with right:
        jurusan_chart = (
            df_pred.groupby(["Jurusan", "Keputusan NB"])
            .size()
            .reset_index(name="Jumlah")
        )
        fig_bar = px.bar(
            jurusan_chart,
            x="Jurusan",
            y="Jumlah",
            color="Keputusan NB",
            barmode="group",
            title="Hasil Keputusan Berdasarkan Jurusan",
            text="Jumlah",
        )
        fig_bar.update_layout(xaxis_title="Jurusan", yaxis_title="Jumlah siswa")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Grafik Keputusan Berdasarkan Rombel")
    rombel_chart = (
        df_pred.groupby(["Rombel", "Keputusan NB"])
        .size()
        .reset_index(name="Jumlah")
        .sort_values("Rombel")
    )
    fig_rombel = px.bar(
        rombel_chart,
        x="Rombel",
        y="Jumlah",
        color="Keputusan NB",
        barmode="group",
        title="Jumlah Minat dan Tidak Minat per Rombel",
        text="Jumlah",
    )
    st.plotly_chart(fig_rombel, use_container_width=True)

    st.markdown(
        """
        <div class="note-box">
        <b>Catatan metodologis:</b> Data siswa telah diperbarui menggunakan data kelas XII tahun 2026 sebanyak 116 siswa.
        Karena berkas sumber belum memuat jawaban kuesioner minat pendidikan tinggi, label bawaan pada file contoh
        bersifat simulasi untuk pengujian aplikasi. Nilai akurasi yang tampil dihitung otomatis dari perbandingan
        hasil prediksi dan label pada file. Untuk hasil penelitian final, ganti kolom label dengan hasil kuesioner
        atau wawancara siswa yang sebenarnya.
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# MENU PREDIKSI MANUAL
# =========================================================
elif menu == "Prediksi Manual":
    st.subheader("Form Prediksi Satu Siswa")
    st.write("Pilih atribut siswa, kemudian sistem akan menghitung probabilitas Naive Bayes dan memberikan keputusan.")

    col_a, col_b = st.columns([1, 1])
    with col_a:
        input_jurusan = st.selectbox("Jurusan", model["categories"]["Jurusan"])
        input_rombel = st.selectbox("Rombel", model["categories"]["Rombel"])
        input_jk = st.selectbox("Jenis Kelamin", model["categories"]["Jenis Kelamin"])

        input_data = {
            "Jurusan": input_jurusan,
            "Rombel": input_rombel,
            "Jenis Kelamin": input_jk,
        }
        pred = predict_single(input_data, model)

        if pred["keputusan"] == CLASS_MINAT:
            st.markdown(
                '<div class="success-box">Keputusan: MINAT melanjutkan ke perguruan tinggi</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="danger-box">Keputusan: TIDAK MINAT melanjutkan ke perguruan tinggi</div>',
                unsafe_allow_html=True,
            )

    with col_b:
        prob_df = pd.DataFrame(
            {
                "Kelas": CLASSES,
                "Probabilitas": [
                    pred["probability"][CLASS_MINAT],
                    pred["probability"][CLASS_TIDAK],
                ],
            }
        )
        fig_prob = px.bar(
            prob_df,
            x="Kelas",
            y="Probabilitas",
            text=prob_df["Probabilitas"].map(lambda x: f"{x:.2%}"),
            title="Perbandingan Probabilitas Keputusan",
        )
        fig_prob.update_layout(yaxis_tickformat=".0%", yaxis_title="Probabilitas")
        st.plotly_chart(fig_prob, use_container_width=True)

    st.subheader("Detail Perhitungan")
    st.dataframe(
        pred["detail"].style.format(precision=8),
        use_container_width=True,
    )

    st.info(
        "Keputusan diambil dari probabilitas terbesar antara kelas Minat dan Tidak minat."
    )

# =========================================================
# MENU DATA SISWA
# =========================================================
elif menu == "Data Siswa":
    st.subheader("Data Siswa dan Hasil Keputusan Naive Bayes")

    filter_keputusan = st.multiselect(
        "Filter keputusan",
        options=CLASSES,
        default=CLASSES,
    )
    show_df = df_pred[df_pred["Keputusan NB"].isin(filter_keputusan)].copy()

    st.dataframe(
        show_df.style.format(
            {
                "Skor NB Minat": "{:.8f}",
                "Skor NB Tidak minat": "{:.8f}",
                "Probabilitas Minat": "{:.2%}",
                "Probabilitas Tidak minat": "{:.2%}",
            }
        ),
        use_container_width=True,
        height=520,
    )

    excel_bytes = make_excel_download(df_pred, model)
    st.download_button(
        label="⬇️ Download hasil prediksi Excel",
        data=excel_bytes,
        file_name="hasil_prediksi_naive_bayes_peminatan.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# =========================================================
# MENU PROBABILITAS
# =========================================================
elif menu == "Probabilitas":
    st.subheader("Tabel Probabilitas Naive Bayes")

    prior_df = pd.DataFrame(
        {
            "Kelas": CLASSES,
            "Jumlah Data": [model["class_count"][kelas] for kelas in CLASSES],
            "Prior P(C)": [model["priors"][kelas] for kelas in CLASSES],
        }
    )
    st.markdown("### Prior Kelas")
    st.dataframe(prior_df.style.format({"Prior P(C)": "{:.4f}"}), use_container_width=True)

    tab_jurusan, tab_rombel, tab_jk = st.tabs(["Jurusan", "Rombel", "Jenis Kelamin"])
    with tab_jurusan:
        st.dataframe(model["likelihood_tables"]["Jurusan"].style.format(precision=6), use_container_width=True)
    with tab_rombel:
        st.dataframe(model["likelihood_tables"]["Rombel"].style.format(precision=6), use_container_width=True)
    with tab_jk:
        st.dataframe(model["likelihood_tables"]["Jenis Kelamin"].style.format(precision=6), use_container_width=True)

    st.markdown(
        """
        <div class="note-box">
        Rumus probabilitas fitur menggunakan Laplace Smoothing:<br>
        <b>P(X|C) = (jumlah X pada kelas C + 1) / (jumlah kelas C + jumlah kategori fitur)</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# MENU RUMUS
# =========================================================
elif menu == "Rumus":
    st.subheader("Rumus Manual Metode Naive Bayes")

    st.markdown(
        r"""
        Metode Naive Bayes menghitung peluang sebuah data masuk ke kelas tertentu berdasarkan atribut-atribut yang dimiliki.

        **1. Prior kelas**

        $$P(C)=\frac{Jumlah\ data\ pada\ kelas\ C}{Total\ data\ latih}$$

        **2. Likelihood fitur dengan Laplace Smoothing**

        $$P(X|C)=\frac{Jumlah\ fitur\ X\ pada\ kelas\ C + 1}{Jumlah\ data\ kelas\ C + Jumlah\ kategori\ fitur}$$

        **3. Skor Naive Bayes**

        $$Skor(C)=P(C) \times P(Jurusan|C) \times P(Rombel|C) \times P(Jenis\ Kelamin|C)$$

        **4. Normalisasi probabilitas**

        $$P(C|X)=\frac{Skor(C)}{Skor(Minat)+Skor(Tidak\ minat)}$$

        **5. Keputusan**

        Sistem memilih kelas dengan probabilitas terbesar.
        """
    )

    st.success("Jika Probabilitas Minat lebih besar, maka keputusan = Minat. Jika sebaliknya, keputusan = Tidak minat.")
