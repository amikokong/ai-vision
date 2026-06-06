# ==========================================
# CELL 2: BUILD THE AI VISION APP (app.py)
# FUNGSI: Pengekstrakan Warna Tudung Muslimah & Eksport Excel
# ==========================================

%%writefile app.py
import streamlit as st
import pandas as pd
import io
from google import genai
from google.genai import types
from PIL import Image
import traceback

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Penganalisis Warna Tudung AI",
    page_icon="🧕",
    layout="centered"
)

# --- PENGENALAN SISTEM ---
st.title("🧕 AI Vision: Analisis Warna Tudung")
st.caption("Sistem Cadangan & Pengekstrakan Warna Berstruktur")
st.markdown("---")
st.markdown(
    "Muat naik imej model atau tudung. Sistem AI Gemini akan mengekstrak **3 warna utama** "
    "yang paling dominan atau sesuai, memaparkan kod warna, dan membenarkan muat turun laporan dalam format Excel."
)

# --- PANEL SISI: KUNCI API ---
with st.sidebar:
    st.header("⚙️ Tetapan Sistem")
    api_key = st.text_input(
        "Masukkan Gemini API Key:",
        type="password",
        help="Diperlukan untuk menghubungkan aplikasi dengan model Gemini AI."
    )
    st.markdown("🔑 [Dapatkan API Key di Google AI Studio](https://aistudio.google.com/app/apikey)")

# --- PROMPT BERASASKAN FORMULA CRAFT ---
default_prompt = """[CONTEXT] Anda adalah sistem analisis visi fesyen AI yang canggih, mengkhususkan dalam fesyen dan penggayaan tudung Muslimah.
[ROLE] Bertindak sebagai Penganalisis Warna Fesyen Profesional.
[ACTION] Analisis imej yang dimuat naik, kenal pasti dan cadangkan 3 warna tudung Muslimah yang paling menonjol atau paling sesuai berserta skor keyakinannya.
[FORMAT] Output MESTILAH secara eksklusif dalam format raw CSV (Comma Separated Values) dengan penamaan lajur yang tepat. Tiada teks pengenalan, tiada penutup, dan jangan gunakan pemformatan blok kod (seperti ```csv). 
Format lajur mestilah: Kedudukan,Nama Warna,Kod Hex,Skor Keyakinan (%)
[TASK] Susun 3 warna tersebut secara menurun bermula dengan skor tertinggi. Pastikan Nama Warna adalah nama komersial yang elegan (contoh: Dusty Rose, Emerald Green) dan Kod Hex adalah tepat (contoh: #DCAE96)."""

with st.expander("📝 Penyesuaian Arahan AI (CRAFT Prompt)"):
    prompt = st.text_area(
        "Ubah suai arahan pengekstrakan di sini jika perlu:",
        value=default_prompt,
        height=250
    )

# --- PEMPROSESAN MUAT NAIK IMEJ ---
uploaded_file = st.file_uploader(
    "📁 Muat naik imej tudung (Format: JPG, PNG):",
    type=["jpg", "png", "jpeg"],
    help="Saiz maksimum: 10MB."
)

if st.button("🚀 Analisis Warna (Jana Excel)", type="primary", use_container_width=True):
    
    # Pengesahan pra-syarat
    if not api_key:
        st.error("❌ Sila masukkan Gemini API Key pada panel sisi terlebih dahulu.")
        st.stop()
        
    if not uploaded_file:
        st.error("❌ Sila muat naik imej sebelum memulakan analisis.")
        st.stop()

    try:
        # Membaca imej yang dimuat naik
        image = Image.open(uploaded_file)
        st.markdown("### 📷 Imej Sumber")
        st.image(image, use_container_width=True)

        client = genai.Client(api_key=api_key)

        with st.spinner("🧠 Al sedang menjalankan pengekstrakan fotometrik dan analisis warna..."):
            # Menjana respons menggunakan model vision[cite: 1]
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, image],
                config=types.GenerateContentConfig(
                    temperature=0.2, # Suhu rendah untuk ketepatan analitikal
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                )
            )

            # Pembersihan rentetan teks (sanitize string)
            raw_text = response.text.strip()
            raw_text = raw_text.replace("
```csv", "").replace("```", "").strip()

            # Penguraian data (Parsing) kepada Jadual Mendatar (Pandas DataFrame)
            df = pd.read_csv(io.StringIO(raw_text))

            st.success("✅ Analisis berjaya disempurnakan!")
            
            # Paparan Jadual Mendatar
            st.markdown("### 📊 Jadual Keputusan Analisis Warna")
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Generasi Fail Excel dalam Memori
            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Analisis Warna')
            excel_data = output_excel.getvalue()

            # Butang Muat Turun Eksklusif
            st.markdown("### 💾 Eksport Data")
            st.download_button(
                label="📥 Muat Turun Laporan (Format .xlsx)",
                data=excel_data,
                file_name="Analisis_Warna_Tudung_Muslimah.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    except pd.errors.ParserError:
        st.error("❌ Ralat Pemprosesan Data: Model AI gagal mengembalikan format CSV yang sah. Sila cuba analisis semula.")
        st.code(raw_text)
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ Ralat Kesisteman Kritis: {error_msg}")
        st.code(traceback.format_exc())

# --- PENUTUP ---
st.markdown("---")
st.caption("Pembangunan Aplikasi Automasi Berstruktur • Dikuasakan oleh algoritma analisis visual pemampatan tinggi.")
