"""
Zeytin & Meyve Bahçesi AI — Faz 0 Prototip
OpenAI API (GPT-4o vision) ile fotoğraftan teşhis + öneri.

Veri toplamadan ve model eğitmeden BUGÜN çalışır. Konsept testi içindir.

Kullanım:
    pip install openai python-dotenv
    echo "OPENAI_API_KEY=sk-..." > ../../.env
    python analyze.py /yol/yaprak_fotograf.jpg
"""

import base64
import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
    from dotenv import load_dotenv
except ImportError:
    print("Eksik paket. Kur: pip install openai python-dotenv")
    sys.exit(1)

# Proje kökündeki .env dosyasını yükle
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

# tarim-uzmani mantığını taşıyan sistem promptu (Global Ziraat Mühendisi)
SISTEM_PROMPTU = """Sen dünya genelinde zeytin ve meyve yetiştiriciliği konusunda uzman, deneyimli bir ziraat mühendisisin.
Sana gönderilen ağaç/yaprak/dal/meyve fotoğrafını incele.

Bağlam: Zeytin ve meyve ağaçları Akdeniz iklimi başta olmak üzere farklı coğrafyalarda (Ege, Marmara, Akdeniz, İspanya, İtalya, Kaliforniya vb.) yetişir. 
Yaygın sorunlar: halkalı leke (peacock spot), dal kanseri, antraknoz, verticillium solgunluğu, zeytin sineği, demir eksikliği (kloroz), su stresi ve diğer mantari/bakteriyel hastalıklar.

Cevabını HER ZAMAN şu iki başlıkla, Türkçe ve sade dille ver:

🔍 TEŞHİS
- Ne sorun var (hastalık/zararlı/besin eksikliği/su stresi/sağlıklı)
- Ne kadar eminsin (yüksek/orta/düşük) ve gerekçen
- Emin değilsen hangi açıdan ek fotoğraf gerektiğini söyle

✅ NE YAPMALI (Bölgesel Yaklaşım)
- Çözüm adımlarını sunarken, varsa kullanıcının belirttiği veya görselden anlaşılan bölgeye göre (kurak/nemli iklim, kireçli/asidik toprak vb.) pratik tavsiyeler ver.
- Somut adımlar (sulama/gübre/budama/ilaçlama yaklaşımı) öner.
- İlaç/gübre için kesin doz VERME; "İlaç ve gübre uygulamaları için kesinlikle yerel İl/İlçe Tarım Müdürlüğü'ne veya uzman bir ziraat mühendisine danışın" genel notunu ekle.

Fotoğraf belirsizse dürüst ol, uydurma."""



def fotografi_oku(yol: str):
    """Fotoğrafı base64'e çevir ve medya tipini döndür."""
    p = Path(yol)
    if not p.exists():
        print(f"Dosya bulunamadı: {yol}")
        sys.exit(1)
    uzanti = p.suffix.lower()
    medya = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
             ".png": "image/png", ".webp": "image/webp"}.get(uzanti)
    if not medya:
        print(f"Desteklenmeyen format: {uzanti}. JPG/PNG/WEBP kullan.")
        sys.exit(1)
    veri = base64.standard_b64encode(p.read_bytes()).decode("utf-8")
    return veri, medya


def analiz_et(fotograf_yolu: str):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY bulunamadı. Proje kökünde .env dosyasına ekle.")
        sys.exit(1)

    veri, medya = fotografi_oku(fotograf_yolu)
    client = OpenAI(api_key=api_key)

    print("Analiz ediliyor...\n")
    yanit = client.chat.completions.create(
        model="gpt-5.6",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SISTEM_PROMPTU},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{medya};base64,{veri}"},
                    },
                    {
                        "type": "text",
                        "text": "Bu ağacın/yaprağın neye ihtiyacı var? Teşhis ve öneri ver.",
                    },
                ],
            },
        ],
    )
    print(yanit.choices[0].message.content)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python analyze.py <fotograf_yolu>")
        sys.exit(1)
    analiz_et(sys.argv[1])
