import base64
import os
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

try:
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]:
        if key in st.secrets and not os.environ.get(key):
            os.environ[key] = st.secrets[key]
except Exception:
    pass

st.set_page_config(
    page_title="Bahçe AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background-color: #0c120c; color: #e8ece9; }
    section[data-testid="stSidebar"] {
        background-color: #121b12 !important;
        border-right: 1px solid #233623;
    }
    h1, h2, h3 { color: #e2f0d9 !important; }
    div.stButton > button {
        background: linear-gradient(135deg, #2e7559 0%, #1c4d39 100%) !important;
        color: white !important; border: none !important;
        border-radius: 8px !important; font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(46,117,89,0.3) !important; width: 100%;
    }
    div.stButton > button:hover {
        box-shadow: 0 6px 16px rgba(46,117,89,0.5) !important;
    }
    section[data-testid="stFileUploader"] {
        border: 2px dashed #2e7559 !important;
        border-radius: 12px; background-color: #121b12;
    }
    .sonuc-kutu {
        background-color: #121b12; padding: 20px; border-radius: 10px;
        border: 1px solid #233623; margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ── Sistem promptları ────────────────────────────────────────────────────────

TESHIS_PROMPTU = """Sen deneyimli bir ziraat mühendisisin. Sana bitki/ağaç/yaprak/dal/meyve
fotoğrafları gönderilecek (bir veya birden fazla). Tüm fotoğrafları birlikte değerlendirerek
tek bir bütünleşik teşhis yap — aynı bitkinin farklı açılardan çekilmiş görüntüleri olarak ele al.

Teşhiste değerlendir: hastalık (mantar/bakteri/virüs), zararlı (böcek/akar),
besin eksikliği (demir/azot/çinko), çevresel stres (su/don/sıcak), sağlıklı.

Konum verilmişse o bölgenin iklimine göre uyarla. Verilmemişse genel öneriler ver.{ek_baglam}

Cevabını HER ZAMAN şu iki başlıkla Türkçe ver:

🔍 TEŞHİS
- Tespit ettiğin bitki/ağaç türü
- Sorun: hastalık/zararlı/eksiklik/stres/sağlıklı
- Güven düzeyi (yüksek/orta/düşük) ve nedeni
- Emin değilsen hangi açıdan ek fotoğraf gerektiğini belirt

✅ NE YAPMALI
- Somut adımlar (sulama/gübre/budama/ilaçlama)
- Kesin doz VERME; yerel tarım otoritesine danışılmasını öner

Fotoğraf belirsizse dürüst ol, uydurma."""

TANITIM_PROMPTU = """Sen deneyimli bir ziraat mühendisisin. Kullanıcı {bitki} hakkında
genel bilgi istiyor.{konum_bilgisi}

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
        model="gpt-4o",
        max_tokens=1200,
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


def analiz_yap(prompt: str, dosya_verileri: list, provider: str,
               openai_key: str, anthropic_key: str):
    icerik = gorsel_icerik_olustur(dosya_verileri)
    if "OpenAI" in provider and openai_key:
        return openai_cagir(prompt, icerik, openai_key)
    elif "Anthropic" in provider and anthropic_key:
        return anthropic_cagir(prompt, icerik, anthropic_key)
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
    st.markdown("<h2 style='text-align:center'>🌿 Bahçe AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#a0b0a0'>Bitki & Ağaç Sağlığı Teşhis</p>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("🤖 Yapay Zeka")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")

    provider_options = []
    if openai_key:
        provider_options.append("OpenAI (GPT-4o)")
    if anthropic_key:
        provider_options.append("Anthropic (Claude Sonnet)")

    if not provider_options:
        st.warning("⚠️ API anahtarı bulunamadı!")
        secim = st.selectbox("Sağlayıcı", ["OpenAI", "Anthropic"])
        custom_key = st.text_input("API Key", type="password")
        if secim == "OpenAI":
            openai_key = custom_key
            provider_options = ["OpenAI (GPT-4o)"]
        else:
            anthropic_key = custom_key
            provider_options = ["Anthropic (Claude Sonnet)"]
    provider = st.selectbox("Model", provider_options) if provider_options else ""

    st.markdown("---")
    st.caption("Bahçe AI — Faz 0 Prototipi\nHer konum ve bitki türü desteklenir.")

# ── Ana Sayfa ─────────────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center;margin-bottom:4px'>🌿 Bahçe AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#a0b0a0;margin-bottom:24px'>Fotoğraf yükle, konum ve bitki türünü gir — yapay zeka teşhis ve öneri versin.</p>", unsafe_allow_html=True)

# Konum + bitki türü — ANA SAYFADA
c1, c2 = st.columns(2)
with c1:
    konum = st.text_input("📍 Konum", placeholder="örn: Adana, Amsterdam, Mersin...",
                           help="Girersen iklime özel öneri alırsın.")
with c2:
    bitki = st.text_input("🌱 Bitki / Ağaç Türü", placeholder="örn: zeytin, elma, nar, incir...",
                           help="Boş bırakırsan fotoğraftan anlamaya çalışır.")

st.markdown("---")

# Fotoğraf yükleme
sol, sag = st.columns([1, 1])

with sol:
    st.subheader("📸 Fotoğraf Yükle")
    yuklu_dosyalar = st.file_uploader(
        "Yaprak, dal, meyve veya gövde fotoğrafı (birden fazla yüklenebilir):",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
    )

    dosya_verileri = []
    if yuklu_dosyalar:
        for dosya in yuklu_dosyalar:
            veri = dosya.read()
            dosya_verileri.append(veri)
            img = Image.open(io.BytesIO(veri))
            st.image(img, caption=dosya.name, use_container_width=True)

with sag:
    st.subheader("🔍 Teşhis Sonucu")

    if dosya_verileri:
        if st.button(f"Teşhis Et 🚀  ({len(dosya_verileri)} fotoğraf)"):
            prompt = TESHIS_PROMPTU.format(ek_baglam=ek_baglam_olustur(konum, bitki))
            with st.spinner("Analiz ediliyor..."):
                try:
                    sonuc = analiz_yap(prompt, dosya_verileri, provider, openai_key, anthropic_key)
                    if sonuc:
                        st.session_state.teshis_sonucu = sonuc
                        st.session_state.konum_teshis = konum
                        st.session_state.bitki_turu_teshis = bitki
                        st.session_state.tanitim_goster = False
                        st.session_state.tanitim_metni = None
                        st.session_state.ek_mod = False
                except Exception as e:
                    st.error(f"Hata: {e}")

    # Teşhis sonucunu göster
    if st.session_state.teshis_sonucu:
        st.markdown(f"<div class='sonuc-kutu'>{st.session_state.teshis_sonucu}</div>",
                    unsafe_allow_html=True)

        st.markdown("---")

        # Aksiyon butonları
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🌳 Bu Ağaç Hakkında Bilgi Al"):
                st.session_state.tanitim_goster = True
                st.session_state.ek_mod = False
        with b2:
            if st.button("📸 Ek Fotoğraf Ekle"):
                st.session_state.ek_mod = True
                st.session_state.tanitim_goster = False

    else:
        st.info("Fotoğraf yükleyip 'Teşhis Et' butonuna basın.")

# ── Ek Fotoğraf Modu ─────────────────────────────────────────────────────────
if st.session_state.ek_mod:
    st.markdown("---")
    st.subheader("📸 Ek Fotoğraf ile Yeniden Değerlendirme")
    st.caption("Aynı ağaçtan farklı açılardan çekilmiş ek fotoğraflar yükleyin.")

    ek_dosyalar = st.file_uploader(
        "Ek fotoğraflar:",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        key="ek_yukleyici",
    )

    ek_verileri = []
    if ek_dosyalar:
        cols = st.columns(min(len(ek_dosyalar), 3))
        for i, dosya in enumerate(ek_dosyalar):
            veri = dosya.read()
            ek_verileri.append(veri)
            with cols[i % 3]:
                st.image(Image.open(io.BytesIO(veri)), caption=dosya.name, use_container_width=True)

    if ek_verileri and st.button("Teşhisi Güncelle 🔄"):
        prompt = EK_FOTOGRAF_PROMPTU.format(
            onceki_teshis=st.session_state.teshis_sonucu,
            adet=len(ek_verileri),
            ek_baglam=ek_baglam_olustur(
                st.session_state.konum_teshis,
                st.session_state.bitki_turu_teshis,
            ),
        )
        with st.spinner("Ek fotoğraflarla değerlendiriliyor..."):
            try:
                yeni_sonuc = analiz_yap(prompt, ek_verileri, provider, openai_key, anthropic_key)
                if yeni_sonuc:
                    st.session_state.teshis_sonucu = yeni_sonuc
                    st.session_state.ek_mod = False
                    st.rerun()
            except Exception as e:
                st.error(f"Hata: {e}")

# ── Ağaç Tanıtımı ─────────────────────────────────────────────────────────────
if st.session_state.tanitim_goster:
    st.markdown("---")
    bitki_adi = st.session_state.bitki_turu_teshis or "bu bitki"
    kon = st.session_state.konum_teshis

    konum_bilgisi = f" Konum: {kon}." if kon else ""
    konum_iklim = f"{kon} iklimine uygun bakım takvimi" if kon else "Genel bakım takvimi"

    if not st.session_state.tanitim_metni:
        prompt = TANITIM_PROMPTU.format(
            bitki=bitki_adi,
            konum_bilgisi=konum_bilgisi,
            konum_iklim=konum_iklim,
        )
        with st.spinner(f"{bitki_adi} hakkında bilgi toplanıyor..."):
            try:
                icerik = [{"type": "text", "text": f"{bitki_adi} hakkında detaylı bilgi ver."}]
                if "OpenAI" in provider and openai_key:
                    st.session_state.tanitim_metni = openai_cagir(prompt, icerik, openai_key)
                elif "Anthropic" in provider and anthropic_key:
                    st.session_state.tanitim_metni = anthropic_cagir(prompt, icerik, anthropic_key)
            except Exception as e:
                st.error(f"Hata: {e}")

    if st.session_state.tanitim_metni:
        st.subheader(f"🌳 {bitki_adi.capitalize()} Tanıtımı")
        st.markdown(f"<div class='sonuc-kutu'>{st.session_state.tanitim_metni}</div>",
                    unsafe_allow_html=True)

# ── Alt bilgi ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<p style='text-align:center;color:#607060;font-size:0.8rem'>Bahçe AI — Faz 0 Prototipi · Her konum ve bitki türü desteklenir</p>", unsafe_allow_html=True)
