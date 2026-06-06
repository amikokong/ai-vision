import streamlit as st
import pandas as pd
import io
import traceback
from PIL import Image, ImageDraw, ImageFont
from google import genai
from google.genai import types

# ==========================================
# CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Hijab Color Matching",
    page_icon="🧕",
    layout="centered"
)

st.title("🧕 AI Hijab Color Matching + Visual Palette")
st.markdown("Upload imej → AI cadang warna tudung → jana visual 1:1")

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.header("⚙️ API Setting")
    api_key = st.text_input("Gemini API Key", type="password")
    st.markdown("[Get API Key](https://aistudio.google.com/app/apikey)")

# ==========================================
# PROMPT (COLOR MATCHING)
# ==========================================

prompt = """
Anda adalah pakar color matching fesyen Muslimah.

Tugas:
Analisis pakaian dalam imej dan cadangkan 5 warna tudung yang sesuai.

Wajib output CSV SAHAJA:

Clothing Color,Clothing HEX,Hijab Color,Hijab HEX,Style,Score,Reason

Rules:
- HEX mesti tepat
- Score 0–100
- Fokus pada fashion harmony
- Gunakan neutral & elegant palette
"""

# ==========================================
# UPLOAD IMAGE
# ==========================================

uploaded_file = st.file_uploader(
    "📁 Upload Image",
    type=["jpg", "jpeg", "png"]
)

# ==========================================
# FUNCTION: CREATE PALETTE IMAGE (1:1)
# ==========================================

def create_palette_image(df):
    img = Image.new("RGB", (1080, 1080), "white")
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((40, 30), "Hijab Color Matching Palette", fill="black")

    y = 120
    box_size = 160

    for i, row in df.iterrows():
        color = row["Hijab HEX"]

        # color box
        draw.rectangle(
            [50, y, 50 + box_size, y + box_size],
            fill=color
        )

        # text
        draw.text(
            (230, y + 50),
            f"{row['Hijab Color']} ({row['Score']}%)",
            fill="black"
        )

        draw.text(
            (230, y + 90),
            str(row["Hijab HEX"]),
            fill="gray"
        )

        y += 190

    return img

# ==========================================
# MAIN PROCESS
# ==========================================

if st.button("🚀 Generate Color Matching", use_container_width=True):

    if not api_key:
        st.error("Sila masukkan API Key")
        st.stop()

    if not uploaded_file:
        st.error("Sila upload image")
        st.stop()

    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Input Image", use_container_width=True)

        client = genai.Client(api_key=api_key)

        with st.spinner("AI sedang analisis warna..."):

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, image],
                config=types.GenerateContentConfig(
                    temperature=0.2
                )
            )

            raw = response.text.strip()
            raw = raw.replace("```csv", "").replace("```", "").strip()

            df = pd.read_csv(io.StringIO(raw))

        st.success("Analisis selesai!")

        st.subheader("📊 Result Table")
        st.dataframe(df, use_container_width=True)

        # ==================================
        # VISUAL PALETTE IMAGE
        # ==================================

        palette_img = create_palette_image(df)

        st.subheader("🎨 Visual Palette (1:1)")
        st.image(palette_img, use_container_width=True)

        # SAVE IMAGE
        buf = io.BytesIO()
        palette_img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            "📥 Download Palette Image",
            data=byte_im,
            file_name="hijab_palette.png",
            mime="image/png"
        )

        # SAVE EXCEL
        excel_buf = io.BytesIO()
        df.to_excel(excel_buf, index=False)

        st.download_button(
            "📥 Download Excel",
            data=excel_buf.getvalue(),
            file_name="color_matching.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error("Error berlaku")
        st.code(traceback.format_exc())

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")
st.caption("AI Color Matching System • Streamlit + Gemini + PIL")
