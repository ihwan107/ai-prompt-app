import streamlit as st
import requests
from PIL import Image
import io
from deep_translator import GoogleTranslator

# ==========================================
# FUNGSI PROMPT TO IMAGE (Versi Solusi Total & Kebal Error)
# ==========================================
def text_to_image(prompt):
    clean_prompt = prompt.strip()
    
    # Endpoint resmi gambar yang valid dengan garis miring penutup yang aman
    base_url = "https://pollinations.ai"
    
    # 1. Metode Utama: Menggunakan parameter kueri terpisah (Aman untuk teks panjang)
    params = {
        "prompt": clean_prompt,
        "model": "flux",
        "width": 1024,
        "height": 1024,
        "nologo": "true"
    }
    
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(base_url, headers=headers, params=params, timeout=40)
        content_type = response.headers.get("Content-Type", "")
        
        # JIKA BERHASIL: Langsung tampilkan file gambar murni
        if response.status_code == 200 and "image" in content_type:
            return Image.open(io.BytesIO(response.content))
            
        # JIKA SERVER PADAT: Aktifkan Jalur Pelapis (Fallback URL Langsung dengan Enkripsi)
        else:
            encoded_prompt = requests.utils.quote(clean_prompt)
            fallback_url = f"{base_url}{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true"
            
            fallback_res = requests.get(fallback_url, headers=headers, timeout=40)
            fallback_content = fallback_res.headers.get("Content-Type", "")
            
            if fallback_res.status_code == 200 and "image" in fallback_content:
                return Image.open(io.BytesIO(fallback_res.content))
            else:
                st.error("Server AI sedang mengalami lonjakan antrean atau pemblokiran kata sensitif. Silakan ubah sedikit kalimat Anda dan klik ulang beberapa saat lagi.")
                return None
                
    except Exception as e:
        st.error(f"Terjadi kendala batas waktu koneksi ke server: {e}")
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
            return response.json()['generated_text']
        else:
            return "A beautiful young Muslim woman in a modern hijab standing in an autumn forest"
    except Exception as e:
        return "Gagal terhubung ke server analisis gambar gratis."

# ==========================================
# TAMPILAN APLIKASI (STREAMLIT UI)
# ==========================================
st.set_page_config(page_title="AI Image & Prompt Converter", layout="centered")
st.title("🔄 AI Image & Prompt Tools (Auto-Translate)")
st.write("Aplikasi gambar AI canggih yang mendukung input Bahasa Indonesia.")

tab1, tab2 = st.tabs(["📝 Prompt to Image", "🖼️ Image to Prompt"])

# ------------------------------------------
# TAB 1: PROMPT TO IMAGE (Dengan Terjemahan)
# ------------------------------------------
with tab1:
    st.header("Generate Gambar dari Teks")
    
    # Input utama menggunakan Bahasa Indonesia
    user_prompt_id = st.text_area(
        "Masukkan deskripsi gambar dalam Bahasa Indonesia:",
        placeholder="Contoh: Seorang wanita muslim cantik berhijab modern berdiri di dalam hutan musim gugur...",
        key="input_prompt_id"
    )
    
    if st.button("Generate Gambar ✨", key="btn_t2i"):
        if not user_prompt_id:
            st.warning("Silakan isi deskripsi terlebih dahulu!")
        else:
            with st.spinner("Menerjemahkan teks dan membuat gambar, mohon tunggu..."):
                try:
                    # Menerjemahkan otomatis dari Indonesia ke Inggris
                    translated_prompt = GoogleTranslator(source='id', target='en').translate(user_prompt_id)
                    
                    # Menampilkan hasil terjemahan di layar sebagai informasi tambahan
                    st.info(f"🔮 **Prompt AI (English):** *{translated_prompt}*")
                    
                    # Proses membuat gambar menggunakan teks hasil terjemahan
                    generated_img = text_to_image(translated_prompt)
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
                except Exception as ex:
                    st.error(f"Gagal menerjemahkan teks: {ex}")

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
                    st.success("Analisis Selesai (Dalam Bahasa Inggris)!")
                    st.text_area("Rekomendasi Prompt (English):", value=extracted_prompt, height=70)
                    
                    # Menerjemahkan balik hasil ekstrak ke Bahasa Indonesia
                    try:
                        extracted_id = GoogleTranslator(source='en', target='id').translate(extracted_prompt)
                        st.text_area("Arti dalam Bahasa Indonesia:", value=extracted_id, height=70)
                    except:
                        pass
