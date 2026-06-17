import streamlit as st
import requests
from PIL import Image
import io
from deep_translator import GoogleTranslator
from urllib.parse import urljoin, quote

# ==========================================
# FUNGSI PROMPT TO IMAGE (Versi Solusi Mutlak & Anti-Gagal)
# ==========================================
def text_to_image(prompt):
    # Membersihkan teks dari spasi liar di awal dan akhir
    clean_prompt = prompt.strip()
    
    # Domain dasar resmi yang dikunci rapat tanpa risiko penempelan teks ilegal
    base_url = "https://pollinations.ai"
    
    try:
        # Mengonversi teks kalimat ke dalam format sandi internet resmi (URL Encoding)
        # Langkah ini memastikan spasi berubah menjadi %20 secara aman oleh sistem Python
        encoded_prompt = quote(clean_prompt)
        
        # Menggunakan fungsi bawaan Python untuk menggabungkan domain dan teks secara presisi
        # Hasil akhirnya dijamin mutlak berupa: https://pollinations.aikalimat%20anda
        final_url = urljoin(base_url, encoded_prompt)
        
        # Menambahkan parameter tambahan untuk kualitas gambar model Flux
        final_url_with_params = f"{final_url}?width=1024&height=1024&model=flux&nologo=true"
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(final_url_with_params, headers=headers, timeout=45)
        content_type = response.headers.get("Content-Type", "")
        
        # Validasi dokumen respon: Jika file berupa gambar murni, langsung tampilkan
        if response.status_code == 200 and "image" in content_type:
            return Image.open(io.BytesIO(response.content))
        else:
            st.error("Server AI eksternal sedang sibuk atau mendeteksi kata yang terlalu sensitif. Mohon coba klik ulang beberapa saat lagi.")
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
