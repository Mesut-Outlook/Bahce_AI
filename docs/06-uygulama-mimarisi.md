# 06 — Uygulama Mimarisi

İki aşamalı: önce Claude API ile hızlı prototip, sonra kendi modelinle kalıcı uygulama.

## Aşama 1 — Prototip (Claude & OpenAI API - Tamamlandı ✅)

Veri toplamadan ve model eğitmeden BUGÜN çalışan sürükle-bırak destekli görsel teşhis web ve CLI uygulaması.

```
Kullanıcı fotoğrafı (Web/Mobil)  →  Streamlit (app.py)  →  GPT-4o / Claude 3.5  →  Türkçe Teşhis + Adana Önerisi
```

### Sunulan Altyapı ve Özellikler:
*   **Web Prototipi (`app/prototype/app.py`):** Koyu orman yeşili paletine sahip, modern ve sade tasarımlı premium web arayüzü. OpenAI (GPT-4o) ve Anthropic (Claude 3.5) API'lerinin ikisini de destekler (`.env` dosyasındaki aktif anahtara göre otomatik algılar).
*   **CLI Analiz Aracı (`app/prototype/analyze.py`):** Terminal üzerinden görsel vererek hızlı teşhis yapmayı sağlayan komut satırı aracı.
*   **Canlı Veri Takip Modülü:** Web arayüzünün sol panelinde projenin güncel veri toplama sayılarını (`data/labeled/` altındaki görsel dağılımlarını) canlı gösterir.
*   **Headless Başlatıcı ve Mobil Tünel Sistemi (`scripts/start_app.sh`):**
    *   Streamlit'in ilk açılışta sorduğu e-posta adımını otomatik atlatmak için `.streamlit` yapılandırma entegrasyonu kuruldu.
    *   Uzak bağlantıların ve mobil cihazların tünel üzerinden erişebilmesi için Streamlit'in **CORS** ve **XSRF** korumaları devre dışı bırakılarak başlatıldı.
    *   `localhost.run` üzerinden otomatik SSH ters tüneli kurarak her çalıştırmada cep telefonundan anında girilebilecek **güvenli bir `https://...` internet linki** üretir.
*   **Streamlit Cloud Hazırlığı (`streamlit_app.py`):** Projeyi doğrudan GitHub üzerinden 7/24 internette ücretsiz yayınlamak için kök dizinde yönlendirici script kuruldu.


## Aşama 2 — Kendi modelinle uygulama

Model eğitilince (`models/` altında .tflite) kalıcı araç:

### Seçenek A — Web uygulaması
```
Tarayıcı (fotoğraf yükle)  →  FastAPI/Flask sunucu  →  model tahmini  →  teşhis + öneri
```
- En hızlı geliştirme: **Streamlit** (tek dosyada yükle-analiz arayüzü)
- Sunucuda model çalışır, internet gerekir

### Seçenek B — Mobil uygulama (offline) ✅ nihai hedef
```
Telefon (fotoğraf çek)  →  cihazda TFLite model  →  teşhis + öneri   [internet YOK]
```
- Bahçede internet olmayabilir → offline kritik
- TFLite modeli telefona gömülür, saniyeler içinde sonuç
- Flutter veya React Native + tflite eklentisi

### Seçenek C — Hibrit (en iyisi)
- Önce cihazdaki hızlı model teşhis koyar
- Model emin değilse (düşük güven) → Claude API'ye "ikinci görüş" sorar
- Hem hızlı/offline hem de zor vakalarda zengin açıklama

## Çıktı tasarımı (her seçenekte ortak)

```
┌─────────────────────────────┐
│  📷 [yüklenen fotoğraf]      │
│                             │
│  🔍 TEŞHİS                  │
│  Halkalı leke (orta şiddet) │
│  Güven: %88                 │
│                             │
│  ✅ NE YAPMALI              │
│  • Nemli dönemde koruyucu.. │
│  • Düşen yaprakları temizle │
│  • Ziraat müd. danış        │
└─────────────────────────────┘
```

## Tasarım kuralları

- Tek buton, tek sonuç ekranı — çiftçi dostu sadelik
- Türkçe, sade dil
- Düşük güvende "şu açıdan bir fotoğraf daha çek" yönlendirmesi
- Kullanıcı fotoğrafı izinsiz saklanmaz

## Güvenlik

- API anahtarı `.env`'de, koda gömülmez, `.gitignore`'da
- Offline modda veri telefondan çıkmaz
