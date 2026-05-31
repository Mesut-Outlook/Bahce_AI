# 06 — Uygulama Mimarisi

İki aşamalı: önce Claude API ile hızlı prototip, sonra kendi modelinle kalıcı uygulama.

## Aşama 1 — Prototip (Claude API Vision)

Veri toplamadan ve model eğitmeden BUGÜN çalışır. Konsept ve kullanıcı deneyimi testi için.

```
Kullanıcı fotoğrafı  →  Claude API (vision + tarım sistem promptu)  →  Türkçe teşhis + öneri
```

- Dosya: `app/prototype/analyze.py`
- Sistem promptu `tarim-uzmani` mantığını taşır: Adana iklimi, zeytin sorunları, iki
  parçalı çıktı (teşhis + ne yapmalı)
- Artı: hemen çalışır, sınıf sınırı yok, dil zengin
- Eksi: internet gerekir, API maliyeti, model "bizim bahçeye" özel değil

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
