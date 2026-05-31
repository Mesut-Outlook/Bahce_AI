import base64
import os
import sys
from pathlib import Path
from PIL import Image
import io

try:
    import streamlit as st
    from dotenv import load_dotenv
except ImportError:
    print("Eksik paketler var. Lütfen kurun: pip install streamlit python-dotenv pillow")
    sys.exit(1)

# Yerel .env yükle (Streamlit Cloud'da bu dosya olmaz, secrets kullanılır)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# Streamlit Cloud secrets desteği
try:
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]:
        if key in st.secrets and not os.environ.get(key):
            os.environ[key] = st.secrets[key]
except Exception:
    pass

# Sayfa Yapılandırması (Premium Görünüm)
st.set_page_config(
    page_title="Zeytin & Meyve Bahçesi AI",
    page_icon="🫒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Özel Premium Tasarım (CSS)
st.markdown("""
<style>
    /* Ana Tema ve Renkler */
    .stApp {
        background-color: #0c120c;
        color: #e8ece9;
    }
    
    /* Yan Panel Stili */
    section[data-testid="stSidebar"] {
        background-color: #121b12 !important;
        border-right: 1px solid #233623;
    }
    
    /* Kart Yapısı ve Gölgelendirmeler */
    .metric-card {
        background: rgba(25, 40, 25, 0.45);
        border: 1px solid #325232;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .status-success {
        background-color: rgba(46, 117, 89, 0.2);
        color: #4ade80;
        border: 1px solid #2e7559;
    }
    
    .status-warning {
        background-color: rgba(234, 179, 8, 0.2);
        color: #facc15;
        border: 1px solid #cab014;
    }
    
    /* Başlıklar */
    h1, h2, h3 {
        color: #e2f0d9 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Buton Tasarımı */
    div.stButton > button {
        background: linear-gradient(135deg, #2e7559 0%, #1c4d39 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(46, 117, 89, 0.3) !important;
        width: 100%;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(46, 117, 89, 0.5) !important;
    }
    
    /* Yükleyici Box Stili */
    section[data-testid="stFileUploader"] {
        border: 2px dashed #2e7559 !important;
        border-radius: 12px;
        background-color: #121b12;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)


# Sistem Promptu (Ziraat Mühendisi Rolü)
SISTEM_PROMPTU_SABLONU = """Sen deneyimli bir ziraat mühendisisin. Sana bir bitki/ağaç/yaprak/dal/meyve
fotoğrafı gönderilecek. Kullanıcı ayrıca bulunduğu konumu ve bitki türünü belirtebilir —
belirtmemişse fotoğraftan çıkarmaya çalış.

Teşhiste şunları değerlendir:
- Hastalık (mantar, bakteri, virüs)
- Zararlı (böcek, akar, vb.)
- Besin eksikliği (demir, azot, çinko, vb.)
- Çevresel stres (su stresi, don, sıcak, tuzluluk)
- Sağlıklı (sorun yok)

Konum verilmişse önerilerini o bölgenin iklimine ve koşullarına göre uyarla.
Konum verilmemişse genel geçer öneriler ver.{ek_baglam}

Cevabını HER ZAMAN şu iki ana başlıkla, Türkçe ve sade dille ver:

🔍 TEŞHİS
- Tespit ettiğin bitki/ağaç türü (fotoğraftan anlaşılıyorsa)
- Sorunun ne olduğunu net şekilde belirt (hastalık/zararlı/besin eksikliği/stres/sağlıklı)
- Teşhisin güven düzeyi (yüksek/orta/düşük) ve nedeni
- Emin değilsen hangi açılardan ek fotoğraf gerektiğini belirt

✅ NE YAPMALI
- Somut ve uygulanabilir çözüm adımları (sulama/gübre/budama/ilaçlama yaklaşımı)
- Konum verilmişse o bölgenin tarım otoritesine danışılmasını öner
- Kesin ilaç veya kimyasal gübre dozajları VERME

Fotoğraf belirsiz veya bitki tanınamıyorsa dürüstçe söyle, uydurma."""


def sistem_promptu_olustur(konum: str, bitki_turu: str) -> str:
    ek = []
    if konum.strip():
        ek.append(f"Kullanıcının konumu: {konum.strip()}")
    if bitki_turu.strip():
        ek.append(f"Kullanıcının belirttiği bitki/ağaç türü: {bitki_turu.strip()}")
    ek_baglam = ("\n\nEk bağlam:\n" + "\n".join(ek)) if ek else ""
    return SISTEM_PROMPTU_SABLONU.format(ek_baglam=ek_baglam)

def get_base64_image(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")

def count_labeled_images():
    """labeled klasöründeki toplam görsel sayısını hesaplar."""
    proje_koku = Path(__file__).resolve().parents[2]
    labeled_path = proje_koku / "data" / "labeled"
    if not labeled_path.exists():
        return 0, {}
    
    siniflar = {}
    uzantilar = {".jpg", ".jpeg", ".png", ".webp"}
    for klasor in labeled_path.iterdir():
        if klasor.is_dir() and klasor.name != "belirsiz":
            adet = sum(1 for f in klasor.iterdir() if f.suffix.lower() in uzantilar)
            siniflar[klasor.name] = adet
    return sum(siniflar.values()), siniflar

# --- YAN PANEL (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🌿 Bahçe AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a0b0a0;'>Bitki & Ağaç Sağlığı Teşhis Sistemi</p>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("📍 Konum & Bitki")
    konum = st.text_input("Konum (isteğe bağlı)", placeholder="örn: Adana, Amsterdam, Mersin...")
    bitki_turu = st.text_input("Bitki / Ağaç Türü (isteğe bağlı)", placeholder="örn: zeytin, elma, nar, incir...")
    st.caption("Konum girilirse iklime özel öneri alırsın. Boş bırakırsan fotoğraftan anlar.")
    st.markdown("---")
    
    # Model/API Sağlayıcı Seçimi
    st.subheader("🤖 Yapay Zeka Sağlayıcısı")
    
    # API Anahtarlarını Kontrol Et
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    provider_options = []
    if openai_key:
        provider_options.append("OpenAI (GPT-4o)")
    if anthropic_key:
        provider_options.append("Anthropic (Claude 3.5 Sonnet)")
        
    if not provider_options:
        st.warning("⚠️ .env dosyasında API anahtarı bulunamadı!")
        provider = st.selectbox("API Sağlayıcı Seçin", ["OpenAI", "Anthropic"])
        custom_key = st.text_input("API Key Girin", type="password")
        if provider == "OpenAI":
            openai_key = custom_key
        else:
            anthropic_key = custom_key
    else:
        provider = st.selectbox("Aktif Yapay Zeka Modeli", provider_options)

    st.markdown("---")
    
    # Bahçe Veri Seti Özeti (check_dataset entegrasyonu!)
    st.subheader("📸 Mevcut Eğitim Verisi Özeti")
    toplam_gorsel, sinif_detaylari = count_labeled_images()
    
    st.markdown(f"""
    <div class='metric-card'>
        <div style='font-size: 0.9rem; color: #a0b0a0;'>Toplanan Toplam Görsel</div>
        <div style='font-size: 1.8rem; font-weight: bold; color: #4ade80;'>{toplam_gorsel} / 750</div>
        <div style='font-size: 0.8rem; color: #708070; margin-top: 5px;'>Transfer learning hedefi: sınıf başına min 100-150 adet</div>
    </div>
    """, unsafe_allow_html=True)
    
    if sinif_detaylari:
        with st.expander("Sınıf Dağılımları"):
            for s_ad, s_adet in sinif_detaylari.items():
                durum_icon = "🟢" if s_adet >= 100 else "🟡"
                st.write(f"{durum_icon} **{s_ad}**: {s_adet} adet")
    else:
        st.info("Henüz etiketlenmiş görsel yok. Çekilen fotoğrafları `data/labeled/` klasörüne yerleştirin.")

# --- ANA SAYFA ---
st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>🌿 Yaprak & Ağaç Teşhis Prototipi</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a0b0a0; font-size: 1.1rem; margin-bottom: 30px;'>Fotoğraf yükleyin, konumunuzu girin — yapay zeka anında teşhis ve öneri çıkarsın.</p>", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1])

uploaded_file = None
image_to_analyze = None

with col_left:
    st.subheader("📸 Fotoğraf Yükleme")
    uploaded_file = st.file_uploader(
        "Ağacın sorunlu yaprak, meyve veya gövdesinin net bir fotoğrafını yükleyin:",
        type=["jpg", "jpeg", "png", "webp"]
    )
    
    if uploaded_file is not None:
        image_to_analyze = uploaded_file.read()
        # Görseli göster
        image = Image.open(io.BytesIO(image_to_analyze))
        st.image(image, caption="Yüklenen Fotoğraf", use_container_width=True)
    else:
        st.info("👉 Devam etmek için bir fotoğraf yükleyin (JPG, PNG veya WEBP).")

with col_right:
    st.subheader("🔍 Yapay Zeka Analiz Sonucu")
    
    if image_to_analyze is not None:
        if st.button("Teşhis Et ve Önerileri Getir 🚀"):
            with st.spinner("Yapay zeka ziraat mühendisi fotoğrafı inceliyor..."):
                
                analysis_success = False
                result_text = ""
                
                # --- OPENAI API ANALİZ ---
                aktif_prompt = sistem_promptu_olustur(konum, bitki_turu)

                if "OpenAI" in provider and openai_key:
                    try:
                        from openai import OpenAI
                        client = OpenAI(api_key=openai_key)

                        base64_image = get_base64_image(image_to_analyze)

                        response = client.chat.completions.create(
                            model="gpt-4o",
                            max_tokens=1024,
                            messages=[
                                {"role": "system", "content": aktif_prompt},
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "image_url",
                                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                                        },
                                        {
                                            "type": "text",
                                            "text": "Bu bitkinin/ağacın durumunu değerlendir. Teşhis ve öneri ver.",
                                        },
                                    ],
                                },
                            ],
                        )
                        result_text = response.choices[0].message.content
                        analysis_success = True
                    except Exception as e:
                        st.error(f"OpenAI API Hatası: {e}")

                # --- ANTHROPIC CLAUDE API ANALİZ ---
                elif "Anthropic" in provider and anthropic_key:
                    try:
                        from anthropic import Anthropic
                        client = Anthropic(api_key=anthropic_key)

                        base64_image = get_base64_image(image_to_analyze)

                        response = client.messages.create(
                            model="claude-sonnet-4-6",
                            max_tokens=1024,
                            system=aktif_prompt,
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "image",
                                            "source": {
                                                "type": "base64",
                                                "media_type": "image/jpeg",
                                                "data": base64_image,
                                            },
                                        },
                                        {
                                            "type": "text",
                                            "text": "Bu bitkinin/ağacın durumunu değerlendir. Teşhis ve öneri ver."
                                        }
                                    ],
                                }
                            ],
                        )
                        result_text = response.content[0].text
                        analysis_success = True
                    except Exception as e:
                        st.error(f"Anthropic API Hatası: {e}")
                
                # --- SONUÇLARI GÖSTER ---
                if analysis_success:
                    st.success("Analiz tamamlandı!")
                    
                    # Teşhis ve Önerileri ayrı kutularda veya temiz markdown ile göster
                    st.markdown("""
                    <div style='background-color: #121b12; padding: 20px; border-radius: 10px; border: 1px solid #233623;'>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(result_text)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.write("Analiz sonuçları yüklediğiniz fotoğraf işlendikten sonra burada görünecektir.")

# Sayfa Altı Bilgisi
st.markdown("---")
st.markdown("<p style='text-align: center; color: #607060; font-size: 0.85rem;'>Bahçe AI — Faz 0 Web Prototipi. Her konum ve bitki türü için çalışır.</p>", unsafe_allow_html=True)
