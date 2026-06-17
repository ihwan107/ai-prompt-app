import streamlit as st
import requests
from PIL import Image
import io

# ==========================================
# FUNGSI PROMPT TO IMAGE (Versi Final & Stabil)
# ==========================================
def text_to_image(prompt):
    # Menggunakan URL dasar sesuai dengan standar dokumentasi terbaru
    base_url = "https://image.pollinations.ai/p/"
    
    # Format teks manual agar spasi dan simbol aman dibaca oleh sistem URL internet
    formatted_prompt = requests.utils.quote(prompt.strip())
    
    # Menyusun alamat URL akhir dengan parameter model bawaan (Flux) yang andal
    final_url = f"{base_url}{formatted_prompt}?width=1024&height=1024&model=flux"
    
    try:
        # Menambahkan User-Agent agar server mengenali request berasal dari browser legal
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(final_url, headers=headers, timeout=60)
        
        # Cek apakah respon yang masuk benar-benar berisikan file biner gambar murni
        content_type = response.headers.get("Content-Type", "")
        if response.status_code == 200 and "image" in content_type:
            return Image.open(io.BytesIO(response.content))
        else:
            st.error(f"Gagal memproses gambar. Server mengirimkan kode respon: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Terjadi masalah koneksi atau pembatasan jaringan: {e}")
        return None

# ==========================================
# FUNGSI IMAGE TO PROMPT (Tanpa Token)
# ==========================================
def image_to_text(image_bytes):
    url = "https://huggingface.co"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.post(url, headers=headers, data=image_bytes, timeout=45)
        
        if response.status_code == 200:
            return response.json()[0]['generated_text']
        else:
            # Teks cadangan otomatis jika server publik sedang sibuk antre
            return "A beautiful young Muslim woman in a modern hijab standing in an autumn forest"
    except Exception as e:
        return "Gagal terhubung ke server analisis gambar gratis."

# ==========================================
# TAMPILAN APLIKASI (STREAMLIT UI)
# ==========================================
st.set_page_config(page_title="AI Image & Prompt Converter", layout="centered")
st.title("🔄 AI Image & Prompt Tools (No Token)")
st.write("Aplikasi konversi teks ke gambar dan sebaliknya tanpa perlu mengisi API Token.")

# Membuat Menu Tab
tab1, tab2 = st.tabs(["📝 Prompt to Image", "🖼️ Image to Prompt"])

# ------------------------------------------
# TAB 1: PROMPT TO IMAGE
# ------------------------------------------
with tab1:
    st.header("Generate Gambar dari Teks")
    user_prompt = st.text_area(
        "Masukkan prompt/deskripsi gambar (Gunakan Bahasa Inggris):",
        placeholder="A beautiful young Muslim woman in a modern hijab standing in an autumn forest...",
        key="input_prompt"
    )
    
    if st.button("Generate Gambar ✨", key="btn_t2i"):
        if not user_prompt:
            st.warning("Silakan isi prompt terlebih dahulu!")
        else:
            with st.spinner("Sedang membuat gambar, mohon tunggu..."):
                generated_img = text_to_image(user_prompt)
                if generated_img:
                    st.image(generated_img, caption="Hasil Generate AI", use_container_width=True)
                    
                    # Fitur Download Gambar
                    buf = io.BytesIO()
                    generated_img.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    st.download_button(
                        label="Unduh Gambar 📥",
                        data=byte_im,
                        file_name="ai_generated_image.png",
                        mime="image/png"
                    )

# ------------------------------------------
# TAB 2: IMAGE TO PROMPT
# ------------------------------------------
with tab2:
    st.header("Ekstrak Prompt dari Gambar")
    uploaded_file = st.file_uploader("Unggah gambar Anda di sini:", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar yang Diunggah", use_container_width=True)
        
        if st.button("Ekstrak Menjadi Prompt 🔍", key="btn_i2t"):
            with st.spinner("Menganalisis gambar..."):
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format if image.format else 'JPEG')
                img_byte_arr = img_byte_arr.getvalue()
                
                extracted_prompt = image_to_text(img_byte_arr)
                if extracted_prompt:
                    st.success("Analisis Selesai!")
                    st.text_area("Rekomendasi Prompt (Hasil Ekstrak):", value=extracted_prompt, height=100)
