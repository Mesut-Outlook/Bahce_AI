import base64
import os
import re
from pathlib import Path
from PIL import Image
import io

try:
    import streamlit as st
    from dotenv import load_dotenv
except ImportError:
    import sys
    print("Eksik paketler: pip install streamlit python-dotenv pillow")
    sys.exit(1)

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

try:
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
        if key in st.secrets and not os.environ.get(key):
            os.environ[key] = st.secrets[key]
except Exception:
    pass

st.set_page_config(
    page_title="Bahçe AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    /* Global Typography */
    html, body, [class*="css"], .stApp, p, span, label, input, button, select {
        font-family: 'Outfit', sans-serif !important;
    }
    /* Material ikon fontunu koru — aksi halde ikonlar "upload" gibi ham metin olarak görünür */
    [data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded' !important;
    }

    /* Main App Background — açık & ferah yeşil-krem */
    .stApp {
        background: linear-gradient(160deg, #f5faf2 0%, #e9f3e4 100%) !important;
        color: #1f3d2b !important;
    }

    /* Glassmorphic Cards — yumuşak beyaz */
    .glass-card {
        background: rgba(255, 255, 255, 0.72) !important;
        border: 1px solid rgba(16, 185, 129, 0.15) !important;
        border-radius: 22px !important;
        padding: 24px !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 8px 30px rgba(31, 61, 43, 0.06) !important;
        margin-bottom: 20px !important;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.7) !important;
        border: 1px solid rgba(16, 185, 129, 0.15) !important;
        border-radius: 18px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
        backdrop-filter: blur(8px);
        box-shadow: 0 6px 20px rgba(31, 61, 43, 0.05);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: rgba(16, 185, 129, 0.4) !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 26px rgba(31, 61, 43, 0.08);
    }

    /* Styled Sidebar — açık krem */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.85) !important;
        border-right: 1px solid rgba(16, 185, 129, 0.15) !important;
        backdrop-filter: blur(12px);
    }

    /* Headers */
    h1, h2, h3 {
        color: #1f3d2b !important;
        font-weight: 600 !important;
    }

    /* Premium Action Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #047857 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        box-shadow: 0 6px 18px rgba(16, 185, 129, 0.22) !important;
        width: 100% !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 24px rgba(16, 185, 129, 0.32) !important;
        background: linear-gradient(135deg, #34d399 0%, #059669 100%) !important;
    }
    div.stButton > button:active {
        transform: translateY(1px) !important;
    }

    /* Styled Text Inputs */
    .stTextInput label {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: #1f3d2b !important;
        margin-bottom: 10px !important;
        display: inline-block !important;
    }
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(16, 185, 129, 0.25) !important;
        color: #1f3d2b !important;
        border-radius: 14px !important;
        padding: 12px 16px !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput input::placeholder {
        color: #9bb3a3 !important;
    }
    .stTextInput input:focus {
        border-color: #10b981 !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15) !important;
        background-color: #ffffff !important;
    }

    /* File Uploader styling */
    section[data-testid="stFileUploader"] {
        border: 2px dashed rgba(16, 185, 129, 0.4) !important;
        border-radius: 20px !important;
        background-color: rgba(255, 255, 255, 0.6) !important;
        padding: 20px !important;
        transition: all 0.3s ease;
    }
    section[data-testid="stFileUploader"]:hover {
        border-color: #10b981 !important;
        background-color: rgba(16, 185, 129, 0.06) !important;
    }

    /* Diagnostic Results Card */
    .diagnosis-card {
        background: rgba(255, 255, 255, 0.78) !important;
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
        border-radius: 22px !important;
        padding: 24px !important;
        box-shadow: 0 8px 30px rgba(31, 61, 43, 0.07) !important;
        backdrop-filter: blur(10px);
        margin-top: 15px;
    }
    .diagnosis-header {
        font-size: 1.35rem;
        font-weight: 700;
        color: #059669 !important;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-left: 4px solid #10b981;
        padding-left: 10px;
    }
    .rec-header {
        font-size: 1.35rem;
        font-weight: 700;
        color: #047857 !important;
        margin-top: 25px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-left: 4px solid #34d399;
        padding-left: 10px;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 15px;
    }
    .badge-healthy {
        background-color: rgba(16, 185, 129, 0.12);
        color: #059669;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .badge-danger {
        background-color: rgba(239, 68, 68, 0.12);
        color: #dc2626;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .badge-warning {
        background-color: rgba(245, 158, 11, 0.14);
        color: #d97706;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    .badge-info {
        background-color: rgba(59, 130, 246, 0.12);
        color: #2563eb;
        border: 1px solid rgba(59, 130, 246, 0.4);
    }

    /* Confidence bar */
    .confidence-container {
        margin-bottom: 22px;
        background: rgba(16, 185, 129, 0.06);
        padding: 12px;
        border-radius: 14px;
        border: 1px solid rgba(16, 185, 129, 0.12);
    }
    .confidence-label {
        font-size: 0.85rem;
        color: #5f7a68;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
    }
    .confidence-bar-bg {
        width: 100%;
        height: 8px;
        background-color: rgba(16, 185, 129, 0.12);
        border-radius: 10px;
        overflow: hidden;
    }
    .confidence-bar-fill {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #10b981, #34d399);
        transition: width 1s ease-out;
    }

    /* Styled Tabs */
    button[data-baseweb="tab"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #5f7a68 !important;
        border-bottom: 2px solid transparent !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        background: transparent !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #1f3d2b !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #059669 !important;
        border-bottom: 2px solid #10b981 !important;
    }
    div[data-testid="stTabContent"] {
        padding-top: 20px;
    }

    /* Native Streamlit chrome'u da açık temada sabitle (sistem koyu modunda bile) */
    header[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"] {
        background: rgba(245, 250, 242, 0.85) !important;
    }
    [data-baseweb="popover"], [data-baseweb="menu"], ul[data-baseweb="menu"],
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1f3d2b !important;
    }
    div[data-testid="stAppViewContainer"] { color: #1f3d2b !important; }

    /* App gibi görünsün: büyük, yuvarlatılmış, gölgeli görseller */
    [data-testid="stImage"] img {
        border-radius: 18px !important;
        box-shadow: 0 8px 24px rgba(31, 61, 43, 0.14) !important;
        border: 1px solid rgba(16, 185, 129, 0.18) !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    }
    [data-testid="stImage"] img:hover {
        transform: translateY(-3px) scale(1.01) !important;
        box-shadow: 0 12px 30px rgba(31, 61, 43, 0.2) !important;
    }

    /* Büyük simgeler — app hissi için */
    .app-icon-xl { font-size: 2.6rem !important; line-height: 1 !important; }
    .app-icon-lg { font-size: 1.7rem !important; line-height: 1 !important; }
    .status-badge { font-size: 1rem !important; padding: 8px 18px !important; }
    .diagnosis-header, .rec-header { font-size: 1.5rem !important; }
    button[data-baseweb="tab"] { font-size: 1.2rem !important; }
    div.stButton > button { font-size: 1.1rem !important; }

    /* ── Mobil duyarlılık (telefon) ─────────────────────────── */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1.2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .glass-card, .diagnosis-card {
            padding: 16px !important;
            border-radius: 18px !important;
        }
        h1 {
            font-size: 1.7rem !important;
        }
        h2 {
            font-size: 1.3rem !important;
        }
        h3 {
            font-size: 1.1rem !important;
        }
        .stTextInput label {
            font-size: 1.05rem !important;
        }
        .diagnosis-header, .rec-header {
            font-size: 1.15rem !important;
        }
        .app-icon-xl { font-size: 2rem !important; }
        .app-icon-lg { font-size: 1.4rem !important; }
        /* Sekme şeridi taşmasın — yatay kaydırılabilir, kompakt */
        div[data-baseweb="tab-list"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
        }
        button[data-baseweb="tab"] {
            font-size: 0.92rem !important;
            padding: 10px 12px !important;
            white-space: nowrap !important;
        }
        div.stButton > button {
            padding: 14px 20px !important;
            font-size: 1.05rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ── Yardımcı Fonksiyonlar ───────────────────────────────────────────────────
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


def parse_llm_response(text: str):
    """
    Yapay zeka teşhis çıktısını yapılandırılmış alanlara böler:
    - diagnosis
    - recommendations
    - status
    - confidence
    """
    if not text:
        return None
        
    diagnosis_part = ""
    rec_part = ""
    status = "info"
    confidence = None
    
    # Başlıkları yakalamak için split
    parts = re.split(r'(🔍\s*TEŞHİS|🔄\s*GÜNCELLENMİŞ\s*TEŞHİS|✅\s*NE\s*YAPMALI|✅\s*GÜNCELLENMİŞ\s*ÖNERİLER)', text, flags=re.IGNORECASE)
    
    current_header = ""
    for part in parts:
        part_strip = part.strip()
        if not part_strip:
            continue
            
        if re.search(r'TEŞHİS', part_strip, re.IGNORECASE):
            current_header = "TEŞHİS"
        elif re.search(r'(NE YAPMALI|ÖNERİLER)', part_strip, re.IGNORECASE):
            current_header = "ÖNERİLER"
        else:
            if current_header == "TEŞHİS":
                diagnosis_part += part
            elif current_header == "ÖNERİLER":
                rec_part += part
            else:
                diagnosis_part += part

    diagnosis_part = diagnosis_part.strip()
    rec_part = rec_part.strip()
    
    # Güven yüzdesini ayıkla (örn %85 veya 85%)
    pct_match = re.search(r'(?:%\s*(\d{2,3}))|(\d{2,3})\s*%', text)
    if pct_match:
        val = pct_match.group(1) or pct_match.group(2)
        try:
            val_int = int(val)
            if 0 <= val_int <= 100:
                confidence = val_int
        except ValueError:
            pass
            
    if not confidence:
        if "yüksek" in text.lower() or "güvenli" in text.lower():
            confidence = 85
        elif "orta" in text.lower():
            confidence = 60
        elif "düşük" in text.lower():
            confidence = 35
            
    # Durum tespiti
    text_lower = text.lower()
    if "sağlıklı" in text_lower and not any(w in text_lower for w in ["hastalık", "zararlı", "eksikliği", "stres", "leke", "böcek", "akar", "sorun"]):
        status = "healthy"
    elif any(w in text_lower for w in ["hastalık", "mantar", "bakteri", "virüs", "kanser", "solgunluk"]):
        status = "danger"
    elif any(w in text_lower for w in ["zararlı", "böcek", "sineği", "akar"]):
        status = "danger"
    elif any(w in text_lower for w in ["eksikliği", "kloroz", "demir", "azot", "çinko"]):
        status = "warning"
    elif any(w in text_lower for w in ["stres", "su stresi", "don", "sıcak"]):
        status = "warning"
    else:
        status = "info"
        
    return {
        "diagnosis": diagnosis_part,
        "recommendations": rec_part,
        "status": status,
        "confidence": confidence
    }


def gorsel_rapor_olustur(result_text: str):
    """Yapay zeka teşhis çıktısını şık HTML kartlar halinde ekrana basar."""
    if not result_text:
        st.info("Fotoğraf yükleyip 'Teşhis Et' butonuna basın.")
        return
        
    parsed = parse_llm_response(result_text)
    if not parsed:
        st.markdown(f"<div class='diagnosis-card'>{result_text}</div>", unsafe_allow_html=True)
        return
        
    status = parsed["status"]
    confidence = parsed["confidence"]
    diag = parsed["diagnosis"]
    recs = parsed["recommendations"]
    
    # Rozet ayarla
    badge_html = ""
    if status == "healthy":
        badge_html = '<span class="status-badge badge-healthy">🟢 Sorun Yok (Sağlıklı)</span>'
    elif status == "danger":
        badge_html = '<span class="status-badge badge-danger">🔴 Hastalık / Zararlı Tespit Edildi</span>'
    elif status == "warning":
        badge_html = '<span class="status-badge badge-warning">🟡 Besin Eksikliği / Çevresel Stres</span>'
    else:
        badge_html = '<span class="status-badge badge-info">🔵 Durum Analiz Edildi</span>'
        
    # Güven barı ayarla
    conf_html = ""
    if confidence:
        bar_color = "linear-gradient(90deg, #ef4444, #f59e0b)" # kırmızı-turuncu
        if confidence >= 75:
            bar_color = "linear-gradient(90deg, #10b981, #34d399)" # yeşil
        elif confidence >= 50:
            bar_color = "linear-gradient(90deg, #f59e0b, #fbbf24)" # sarı-turuncu
            
        conf_html = f"""
        <div class="confidence-container">
            <div class="confidence-label">
                <span>🔍 Teşhis Güven Oranı</span>
                <strong>%{confidence}</strong>
            </div>
            <div class="confidence-bar-bg">
                <div class="confidence-bar-fill" style="width: {confidence}%; background: {bar_color};"></div>
            </div>
        </div>
        """
        
    st.markdown(f"""
    <div class="diagnosis-card">
        {badge_html}
        {conf_html}
        <div class="diagnosis-header">🔍 Teşhis Raporu</div>
    """, unsafe_allow_html=True)
    
    st.markdown(diag if diag else result_text)
    
    if recs:
        st.markdown(f"""
        <hr style="border-color: rgba(46, 117, 89, 0.2); margin: 20px 0;">
        <div class="rec-header">✅ Uygulanacak Çözüm Önerileri</div>
        """, unsafe_allow_html=True)
        st.markdown(recs)
        
    st.markdown("</div>", unsafe_allow_html=True)

# ── Sistem promptları ────────────────────────────────────────────────────────

TESHIS_PROMPTU = """Sen dünya genelinde zeytin ve meyve yetiştiriciliği konusunda uzman, deneyimli bir ziraat mühendisisin.
Sana bitki/ağaç/yaprak/dal/meyve fotoğrafları gönderilecek (bir veya birden fazla). Tüm fotoğrafları birlikte değerlendirerek tek bir bütünleşik teşhis yap — aynı bitkinin farklı açılardan çekilmiş görüntüleri olarak ele al.

Bağlam: Zeytin ve meyve ağaçları Akdeniz iklimi başta olmak üzere farklı coğrafyalarda (Ege, Marmara, Akdeniz, İspanya, İtalya, Kaliforniya vb.) yetişir. 
Yaygın sorunlar: halkalı leke (peacock spot), dal kanseri, antraknoz, verticillium solgunluğu, zeytin sineği, demir eksikliği (kloroz), su stresi ve diğer mantari/bakteriyel hastalıklar.
Konum verilmişse o bölgenin iklimine göre uyarla. Verilmemişse genel öneriler ver.{ek_baglam}

Cevabını HER ZAMAN şu iki başlıkla Türkçe ver:

🔍 TEŞHİS
- Tespit ettiğin bitki/ağaç türü
- Sorun: hastalık/zararlı/eksiklik/stres/sağlıklı
- Fotoğraftaki belirtilere dayanarak teşhisin doğruluk güven oranını (%) ve gerekçesini açıkla.
- Emin değilsen hangi açılardan yeni fotoğraflar çekilmesi gerektiğini belirt.

✅ NE YAPMALI (Bölgesel Yaklaşım)
- Çözüm adımlarını sunarken, varsa kullanıcının belirttiği veya görselden anlaşılan bölgeye göre (kurak/nemli iklim, kireçli/asidik toprak vb.) pratik tavsiyeler ver.
- Somut adımlar (sulama/gübre/budama/ilaçlama) öner.
- Kesin kimyasal ilaç veya gübre dozajları VERME; "İlaç ve gübreleme uygulamaları için kesinlikle yerel İl/İlçe Tarım Müdürlüğü'ne veya uzman bir ziraat mühendisine danışın" genel notunu ekle.

Fotoğraf belirsizse dürüst ol, uydurma."""

TANITIM_PROMPTU = """Sen deneyimli bir ziraat mühendisisin. Kullanıcı {bitki} hakkında genel bilgi istiyor.{konum_bilgisi}

Şu başlıklarla Türkçe, sade ve uygulanabilir bilgi ver:



🌳 BİTKİ TANITIMI
- Kısa tanım ve özellikleri
- İdeal iklim ve toprak koşulları
- {konum_iklim}

💧 BAKIM TAKVİMİ
- Sulama (ne zaman, ne kadar)
- Gübreleme dönemi
- Budama zamanı

🍂 HASAT & MEVSİM
- Hasat dönemi
- Olgunluk belirtileri

⚠️ EN SIK SORUNLAR
- Bu bitkide en çok görülen 3-4 hastalık/zararlı
- Kısa belirtileri"""

EK_FOTOGRAF_PROMPTU = """Sen deneyimli bir ziraat mühendisisin.
Daha önce şu teşhisi yapmıştın:
---
{onceki_teshis}
---
Kullanıcı şimdi aynı ağaçtan {adet} ek fotoğraf gönderdi.
Bu yeni fotoğraflarla birlikte önceki teşhisini gözden geçir ve güncelle.
Eğer yeni fotoğraflar teşhisi değiştiriyorsa veya netleştiriyorsa belirt.{ek_baglam}

Cevabını şu başlıklarla Türkçe ver:

🔄 GÜNCELLENMİŞ TEŞHİS
- Önceki teşhisten fark var mı?
- Yeni fotoğrafların katkısı
- Nihai teşhis ve güven düzeyi

✅ GÜNCELLENMİŞ ÖNERİLER
- Somut adımlar; kesin doz verme."""


def ek_baglam_olustur(konum: str, bitki: str) -> str:
    ek = []
    if konum.strip():
        ek.append(f"Konum: {konum.strip()}")
    if bitki.strip():
        ek.append(f"Bitki türü: {bitki.strip()}")
    return ("\n\nEk bağlam:\n" + "\n".join(ek)) if ek else ""


def gorsel_icerik_olustur(dosyalar: list) -> list:
    """Birden fazla yüklenen dosyayı API mesaj içeriğine dönüştür."""
    icerik = []
    for dosya in dosyalar:
        veri = base64.b64encode(dosya).decode("utf-8")
        icerik.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{veri}"},
        })
    icerik.append({
        "type": "text",
        "text": "Bu fotoğrafları birlikte değerlendir. Teşhis ve öneri ver.",
    })
    return icerik


def openai_cagir(prompt: str, icerik: list, api_key: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    yanit = client.chat.completions.create(
        model="gpt-5.6",
        max_completion_tokens=1200,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": icerik},
        ],
    )
    return yanit.choices[0].message.content


def anthropic_cagir(prompt: str, icerik: list, api_key: str) -> str:
    from anthropic import Anthropic
    ant_icerik = []
    for item in icerik:
        if item["type"] == "image_url":
            b64 = item["image_url"]["url"].split(",")[1]
            ant_icerik.append({
                "type": "image",
                "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
            })
        else:
            ant_icerik.append({"type": "text", "text": item["text"]})
    client = Anthropic(api_key=api_key)
    yanit = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        system=prompt,
        messages=[{"role": "user", "content": ant_icerik}],
    )
    return yanit.content[0].text


def gemini_cagir(prompt: str, dosya_verileri: list, api_key: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    # PIL image listesi oluşturalım
    contents = []
    for veri in dosya_verileri:
        img = Image.open(io.BytesIO(veri))
        contents.append(img)
    
    # Kullanıcı promptu
    contents.append("Bu fotoğrafları birlikte değerlendir. Teşhis ve öneri ver.")
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=prompt
    )
    
    yanit = model.generate_content(contents)
    return yanit.text


def analiz_yap(prompt: str, dosya_verileri: list, provider: str,
               openai_key: str, anthropic_key: str, gemini_key: str = None):
    icerik = gorsel_icerik_olustur(dosya_verileri)
    if "OpenAI" in provider and openai_key:
        return openai_cagir(prompt, icerik, openai_key)
    elif "Anthropic" in provider and anthropic_key:
        return anthropic_cagir(prompt, icerik, anthropic_key)
    elif "Google" in provider and gemini_key:
        return gemini_cagir(prompt, dosya_verileri, gemini_key)
    return None


# ── Session state başlat ─────────────────────────────────────────────────────
for key, default in [
    ("teshis_sonucu", None),
    ("bitki_turu_teshis", ""),
    ("konum_teshis", ""),
    ("tanitim_goster", False),
    ("tanitim_metni", None),
    ("ek_mod", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='text-align:center; margin-bottom: 0;'><span class='app-icon-lg'>🌿</span> Bahçe AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#5f7a68; font-size:0.85rem;'>Zeytin & Meyve Bahçesi Sağlık Asistanı</p>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("🤖 Yapay Zeka Modeli")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    gemini_key = os.environ.get("GEMINI_API_KEY", "")

    provider_options = []
    if openai_key:
        provider_options.append("OpenAI (GPT-5.6)")
    if anthropic_key:
        provider_options.append("Anthropic (Claude Sonnet)")
    if gemini_key:
        provider_options.append("Google (Gemini 1.5 Flash)")

    if not provider_options:
        st.warning("⚠️ API anahtarı bulunamadı!")
        secim = st.selectbox("Sağlayıcı", ["OpenAI", "Anthropic", "Google Gemini"])
        custom_key = st.text_input("API Key", type="password")
        if secim == "OpenAI":
            openai_key = custom_key
            provider_options = ["OpenAI (GPT-5.6)"]
        elif secim == "Anthropic":
            anthropic_key = custom_key
            provider_options = ["Anthropic (Claude Sonnet)"]
        else:
            gemini_key = custom_key
            provider_options = ["Google (Gemini 1.5 Flash)"]
            
    provider = st.selectbox("Model Seçimi", provider_options) if provider_options else ""

    # Bahçe Veri Seti Özeti (Görsel İlerleme Çubuklu)
    st.markdown("---")
    st.subheader("📊 Veri Seti Özeti")
    toplam_gorsel, sinif_detaylari = count_labeled_images()
    
    hedef_toplam = 750
    yuzde_toplam = min(int((toplam_gorsel / hedef_toplam) * 100), 100)
    
    st.markdown(f"""
    <div class='metric-card'>
        <div style='font-size: 0.85rem; color: #5f7a68; margin-bottom: 4px;'>Toplam Toplanan Görsel</div>
        <div style='font-size: 1.8rem; font-weight: 700; color: #059669; line-height: 1.2;'>{toplam_gorsel} <span style='font-size: 0.95rem; color: #8aa090;'>/ {hedef_toplam}</span></div>
        <div class="confidence-bar-bg" style="margin-top: 8px; height: 6px;">
            <div class="confidence-bar-fill" style="width: {yuzde_toplam}%; background: linear-gradient(90deg, #10b981, #34d399);"></div>
        </div>
        <div style='font-size: 0.75rem; color: #8aa090; margin-top: 6px;'>Hedef: Sınıf başına min 100-150 görsel.</div>
    </div>
    """, unsafe_allow_html=True)
    
    if sinif_detaylari:
        with st.expander("📁 Sınıf Dağılımları", expanded=False):
            for s_ad, s_adet in sinif_detaylari.items():
                s_yuzde = min(int((s_adet / 150) * 100), 100)
                durum_renk = "#fbbf24" if s_adet < 100 else "#10b981"
                st.markdown(f"""
                <div style="margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #1f3d2b;">
                        <span>{s_ad}</span>
                        <strong>{s_adet} adet</strong>
                    </div>
                    <div class="confidence-bar-bg" style="height: 4px; margin-top: 4px;">
                        <div class="confidence-bar-fill" style="width: {s_yuzde}%; background: {durum_renk};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.caption("Henüz etiketlenmiş görsel bulunmuyor. Fotoğrafları `data/labeled/` altına ekleyin.")

    st.markdown("---")
    st.caption("Bahçe AI — Faz 0 Prototip\nHer konum ve bitki türü desteklenir.")

# ── Ana Sayfa ─────────────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center; margin-bottom: 0px;'><span class='app-icon-xl'>🌿</span> Bahçe AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#5f7a68; margin-bottom:28px; font-size:1.05rem;'>Bitki fotoğraflarını yükleyin — Yapay Zeka anında teşhis ve çözüm sunsun.</p>", unsafe_allow_html=True)

# Konum + bitki türü kartı (Glassmorphic)
st.markdown("<div class='glass-card' style='padding: 20px !important; margin-bottom: 25px !important;'>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    konum = st.text_input("📍 Konum (İsteğe Bağlı)", placeholder="örn: Adana, Amsterdam, Mersin...",
                           help="Bölgesel iklim ve toprak koşullarına özel öneriler almak için girin.")
with c2:
    bitki = st.text_input("🌱 Bitki / Ağaç Türü (İsteğe Bağlı)", placeholder="örn: zeytin, elma, nar, incir...",
                           help="Boş bırakırsanız yapay zeka fotoğraftan bitkiyi tespit etmeye çalışacaktır.")
st.markdown("</div>", unsafe_allow_html=True)

# Sekmeli Bölüm Yapısı (TABS)
tab1, tab2, tab3 = st.tabs(["🔍 Teşhis & Tedavi", "🌳 Bitki Kılavuzu", "📸 Ek Fotoğraf Ekle"])

with tab1:
    sol, sag = st.columns([1, 1])
    
    dosya_verileri = []
    
    with sol:
        st.markdown("<h3 style='margin-top:0;'><span class='app-icon-lg'>📸</span> Fotoğraf Yükle</h3>", unsafe_allow_html=True)
        yuklu_dosyalar = st.file_uploader(
            "Yaprak, dal, meyve veya gövde fotoğrafları:",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
        )
        
        if yuklu_dosyalar:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            # Yatay Grid Düzeni
            n_images = len(yuklu_dosyalar)
            cols = st.columns(min(n_images, 3))
            for i, dosya in enumerate(yuklu_dosyalar):
                veri = dosya.read()
                dosya_verileri.append(veri)
                img = Image.open(io.BytesIO(veri))
                with cols[i % 3]:
                    st.image(img, caption=dosya.name, use_container_width=True)
        else:
            st.info("👉 Analize başlamak için zeytin veya meyve ağacınızın sorunlu kısımlarını gösteren net fotoğraflar yükleyin.")

    with sag:
        st.markdown("<h3 style='margin-top:0;'><span class='app-icon-lg'>🔍</span> Teşhis Sonucu</h3>", unsafe_allow_html=True)
        
        if dosya_verileri:
            st.markdown("<div style='margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)
            if st.button(f"Teşhis Et 🚀 ({len(dosya_verileri)} Fotoğraf)"):
                prompt = TESHIS_PROMPTU.format(ek_baglam=ek_baglam_olustur(konum, bitki))
                with st.spinner("Analiz ediliyor..."):
                    try:
                        sonuc = analiz_yap(prompt, dosya_verileri, provider, openai_key, anthropic_key, gemini_key)
                        if sonuc:
                            st.session_state.teshis_sonucu = sonuc
                            st.session_state.konum_teshis = konum
                            st.session_state.bitki_turu_teshis = bitki
                            st.session_state.tanitim_metni = None # Sıfırla
                    except Exception as e:
                        st.error(f"Analiz sırasında hata oluştu: {e}")
            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.teshis_sonucu:
            # Teşhisi şık arayüzde göster
            gorsel_rapor_olustur(st.session_state.teshis_sonucu)
        else:
            st.info("Fotoğrafları yükleyip 'Teşhis Et' butonuna bastıktan sonra raporunuz burada görünecektir.")

with tab2:
    bitki_adi = st.session_state.bitki_turu_teshis or bitki
    kon = st.session_state.konum_teshis or konum
    
    if bitki_adi:
        st.markdown(f"<h3 style='margin-top:0;'><span class='app-icon-lg'>🌳</span> {bitki_adi.capitalize()} Bakım Kılavuzu</h3>", unsafe_allow_html=True)
        st.caption(f"{bitki_adi.capitalize()} ağacının genel özellikleri, bakım takvimi ve sık görülen sorunları.")
        
        konum_bilgisi = f" Konum: {kon}." if kon else ""
        konum_iklim = f"{kon} iklimine uygun bakım takvimi" if kon else "Genel bakım takvimi"
        
        if not st.session_state.tanitim_metni:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            if st.button(f"🌳 {bitki_adi.capitalize()} Kılavuzunu Oluştur"):
                prompt = TANITIM_PROMPTU.format(
                    bitki=bitki_adi,
                    konum_bilgisi=konum_bilgisi,
                    konum_iklim=konum_iklim,
                )
                with st.spinner(f"{bitki_adi.capitalize()} hakkında bilgiler toplanıyor..."):
                    try:
                        icerik = [{"type": "text", "text": f"{bitki_adi} hakkında detaylı bilgi ver."}]
                        if "OpenAI" in provider and openai_key:
                            st.session_state.tanitim_metni = openai_cagir(prompt, icerik, openai_key)
                        elif "Anthropic" in provider and anthropic_key:
                            st.session_state.tanitim_metni = anthropic_cagir(prompt, icerik, anthropic_key)
                        elif "Google" in provider and gemini_key:
                            st.session_state.tanitim_metni = gemini_cagir(prompt, [], gemini_key)
                    except Exception as e:
                        st.error(f"Kılavuz oluşturulurken hata: {e}")
        
        if st.session_state.tanitim_metni:
            st.markdown(f"<div class='diagnosis-card'>", unsafe_allow_html=True)
            st.markdown(st.session_state.tanitim_metni)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("🌳 Bitki bakım kılavuzunu görüntülemek için önce bir teşhis yapın veya üstteki 'Bitki / Ağaç Türü' alanına bir isim girin.")

with tab3:
    if st.session_state.teshis_sonucu:
        st.markdown("<h3 style='margin-top:0;'><span class='app-icon-lg'>📸</span> Ek Fotoğraf ile Analizi Güncelle</h3>", unsafe_allow_html=True)
        st.caption("Aynı ağaçtan veya yapraktan farklı açılarda çekilmiş ek fotoğraflar ekleyerek teşhisi netleştirin.")
        
        ek_dosyalar = st.file_uploader(
            "Ek fotoğraflar yükleyin:",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key="ek_yukleyici",
        )
        
        ek_verileri = []
        if ek_dosyalar:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            cols = st.columns(min(len(ek_dosyalar), 3))
            for i, dosya in enumerate(ek_dosyalar):
                veri = dosya.read()
                ek_verileri.append(veri)
                with cols[i % 3]:
                    st.image(Image.open(io.BytesIO(veri)), caption=dosya.name, use_container_width=True)
                    
        if ek_verileri:
            st.markdown("<div style='margin-top: 15px;'>", unsafe_allow_html=True)
            if st.button("Teşhisi Güncelle 🔄"):
                prompt = EK_FOTOGRAF_PROMPTU.format(
                    onceki_teshis=st.session_state.teshis_sonucu,
                    adet=len(ek_verileri),
                    ek_baglam=ek_baglam_olustur(
                        st.session_state.konum_teshis,
                        st.session_state.bitki_turu_teshis,
                    ),
                )
                with st.spinner("Ek fotoğraflarla yeniden değerlendiriliyor..."):
                    try:
                        yeni_sonuc = analiz_yap(prompt, ek_verileri, provider, openai_key, anthropic_key, gemini_key)
                        if yeni_sonuc:
                            st.session_state.teshis_sonucu = yeni_sonuc
                            st.session_state.tanitim_metni = None # Sıfırla
                            st.rerun()
                    except Exception as e:
                        st.error(f"Güncelleme sırasında hata: {e}")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("📸 Ek fotoğraflarla analizi güncellemek için önce ana fotoğraflarla teşhis yapmalısınız.")

# ── Alt bilgi ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<p style='text-align:center;color:#8aa090;font-size:0.8rem'>Bahçe AI — Faz 0 Prototipi · Her konum ve bitki türü desteklenir</p>", unsafe_allow_html=True)
