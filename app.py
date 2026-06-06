import streamlit as st
import pandas as pd
import io
from PIL import Image
import traceback

from google import genai
from google.genai import types

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================

st.set_page_config(
    page_title="Penganalisis Warna Tudung AI",
    page_icon="🧕",
    layout="centered"
)

# ==========================================
# HEADER
# ==========================================

st.title("🧕 AI Vision: Analisis Warna Tudung")
st.caption("Sistem Cadangan & Pengekstrakan Warna Berstruktur")

st.markdown("""
Muat naik imej model atau tudung.

AI Gemini akan mengenal pasti **3 warna utama yang paling dominan atau sesuai**, lengkap dengan:

- Nama warna
- Kod Hex
- Skor keyakinan

Keputusan boleh dimuat turun dalam format Excel.
""")

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.header("⚙️ Tetapan Sistem")

    api_key = st.text_input(
        "Gemini API Key",
        type="password"
    )

    st.markdown(
        "[🔑 Dapatkan API Key](https://aistudio.google.com/app/apikey)"
    )

# ==========================================
# PROMPT
# ==========================================

default_prompt = """
[CONTEXT]
Anda adalah sistem analisis visi fesyen AI yang canggih.

[ROLE]
Bertindak sebagai Penganalisis Warna Fesyen Profesional.

[ACTION]
Analisis imej yang dimuat naik dan kenal pasti 3 warna tudung Muslimah yang paling sesuai.

[FORMAT]
Output MESTILAH dalam format CSV sahaja.

Kedudukan,Nama Warna,Kod Hex,Skor Keyakinan (%)

[TASK]
Susun daripada skor tertinggi ke skor terendah.
"""

with st.expander("📝 Penyesuaian Prompt"):
    prompt = st.text_area(
        "Prompt Analisis",
        value=default_prompt,
        height=250
    )

# ==========================================
# UPLOAD FILE
# ==========================================

uploaded_file = st.file_uploader(
    "📁 Muat Naik Imej",
    type=["jpg", "jpeg", "png"]
)

# ==========================================
# PROSES ANALISIS
# ==========================================

if st.button(
    "🚀 Analisis Warna (Jana Excel)",
    type="primary",
    use_container_width=True
):

    if not api_key:
        st.error("Sila masukkan Gemini API Key.")
        st.stop()

    if uploaded_file is None:
        st.error("Sila muat naik imej.")
        st.stop()

    try:

        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="Imej Sumber",
            use_container_width=True
        )

        client = genai.Client(api_key=api_key)

        with st.spinner("🧠 AI sedang menganalisis warna..."):

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, image],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    thinking_config=types.ThinkingConfig(
                        thinking_budget=0
                    )
                )
            )

            raw_text = response.text.strip()

            # Bersihkan markdown
            raw_text = raw_text.replace("```csv", "")
            raw_text = raw_text.replace("```", "")
            raw_text = raw_text.strip()

            st.subheader("📄 Respons Mentah AI")
            st.code(raw_text)

            # Convert CSV kepada DataFrame
            df = pd.read_csv(io.StringIO(raw_text))

            # Pastikan ada data
            if df.empty:
                st.error("Tiada data ditemui.")
                st.stop()

            st.success("✅ Analisis Berjaya")

            st.subheader("📊 Keputusan Analisis")
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            # ==================================
            # JANA EXCEL
            # ==================================

            output = io.BytesIO()

            with pd.ExcelWriter(
                output,
                engine="openpyxl"
            ) as writer:

                df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Analisis Warna"
                )

            excel_data = output.getvalue()

            st.download_button(
                label="📥 Muat Turun Excel",
                data=excel_data,
                file_name="Analisis_Warna_Tudung.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    except pd.errors.ParserError:

        st.error(
            "AI tidak mengembalikan CSV yang sah."
        )

        st.code(raw_text)

    except Exception as e:

        st.error(f"Ralat: {e}")

        st.code(traceback.format_exc())

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.caption(
    "AI Vision • Analisis Warna Tudung Muslimah • Streamlit + Gemini"
)
