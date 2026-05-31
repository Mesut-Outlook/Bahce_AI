# CLAUDE.md — Zeytin & Meyve Bahçesi AI Projesi

Bu dosya Claude Code tarafından her oturumda otomatik okunur. Projenin "anayasası"dır.

## Projenin amacı

Adana'daki aile bahçesinde bulunan **zeytin ve meyve ağaçlarının** fotoğraflarından
sağlık durumunu tespit eden bir yapay zeka aracı geliştirmek. Araç şunları ayırt etmeli:

- **Hastalık** (mantar, bakteri, virüs)
- **Zararlı** (böcek, akar)
- **Besin eksikliği** (demir, azot, çinko, vb.)
- **Çevresel stres** (su stresi, don, sıcak)
- **Sağlıklı** (sorun yok)

Çıktı her zaman iki parçalı olmalı: (1) teşhis, (2) "ne yapmalı" önerisi.

## Bahçe bağlamı (önemli)

- **Konum:** Adana, Akdeniz iklimi (sıcak-kurak yaz, ılık-yağışlı kış)
- **Yıllık yağış hedefi (zeytin):** 650–800 mm; yazın sulama gerekir
- **Yaygın ağaçlar:** zeytin, nar, incir, narenciye, şeftali, kayısı, erik
- **Akdeniz'de en sık zeytin sorunları:** halkalı leke (peacock spot), dal kanseri,
  antraknoz, verticillium solgunluğu, zeytin sineği

Bu iklim bağlamı modelin ve önerilerin merkezindedir. Genel/dünya geneli tavsiye değil,
**Adana koşullarına** uygun öneri üret.

## Çalışma prensipleri

1. **Önce küçük başla.** Tüm hastalıkları aynı anda hedefleme. İlk model 4–5 sınıf:
   sağlıklı zeytin yaprağı + halkalı leke + zeytin sineği + demir eksikliği + su stresi.
2. **Transfer learning kullan.** PlantVillage gibi hazır modeli temel al, bahçe
   fotoğraflarıyla ince ayar (fine-tune) yap. Sıfırdan eğitme.
3. **Her sınıf için "sağlıklı" karşılığı şart.** Model neyin sorunlu olduğunu anlamak
   için neyin normal olduğunu görmeli.
4. **Veri kalitesi > veri miktarı.** Bulanık, kötü ışıklı fotoğraflar veri setine girmez.
5. **Türkçe çıktı.** Kullanıcıya dönük tüm metinler, etiketler ve öneriler Türkçe.

## Klasör yapısı

```
zeytin-bahce-ai/
├── CLAUDE.md            # bu dosya
├── docs/               # tüm dokümantasyon (proje planı, rehberler, katalog)
├── data/
│   ├── raw/            # çekilmiş ham fotoğraflar (işlenmemiş)
│   ├── labeled/        # etiketlenmiş fotoğraflar (sınıf klasörleri halinde)
│   └── processed/      # boyutlandırılmış/temizlenmiş eğitime hazır veri
├── models/             # eğitilmiş model dosyaları (.pt, .h5, .tflite)
├── app/
│   └── prototype/      # Claude/OpenAI API ile hızlı analiz web ve CLI prototipi
├── scripts/            # Veri hazırlama, API'den indirme ve sunucu başlatıcı scriptler
│   ├── download_inaturalist.py  # iNaturalist API ile veri toplayıcı
│   ├── start_app.sh             # Sunucu ve tünel başlatıcı
│   ├── check_dataset.py         # Veri kontrol ve dengelilik analiz aracı
│   └── prepare_data.py          # Görsel ön işlem ve train/val split aracı
└── notebooks/          # deney/eğitim Jupyter notebook'ları

```

## Sub-agent'lar (uzmanlar)

Bu projede 5 uzman sub-agent tanımlı (`.claude/agents/`). Doğru işi doğru uzmana ver:

- **tarim-uzmani** → hastalık/zararlı/eksiklik teşhisi, hangi sınıfları toplamalı,
  Adana'ya özgü tarımsal sorular
- **veri-toplama** → fotoğraf çekim planı, kaç fotoğraf, nasıl çekilmeli
- **etiketleme** → etiketleme standardı, klasör yapısı, kalite kontrol
- **model-egitim** → model mimarisi seçimi, transfer learning, eğitim script'leri
- **uygulama-gelistirici** → prototip ve son uygulama (web/mobil) geliştirme

## Slash komutları (workflow'lar)

`.claude/commands/` altında hazır workflow'lar var:

- `/proje-durumu` → projenin genel durumunu raporla
- `/veri-kontrol` → veri setini analiz et (kaç fotoğraf, hangi sınıf eksik)
- `/yeni-sinif` → yeni bir hastalık/durum sınıfı ekle
- `/egitim-baslat` → model eğitim sürecini başlat

## Kod standartları

- Python 3.10+, PyTorch veya TensorFlow (model-egitim agent'ı karar verir)
- Görüntü standardı: **512×512 px**, RGB, JPEG/PNG
- Sınıf klasörü adlandırma: `agac-turu_durum` örn: `zeytin_halkali-leke`, `zeytin_saglikli`
- Tüm yorumlar ve değişken açıklamaları Türkçe olabilir; kod İngilizce
- Gizli anahtarlar (API key) asla repoya girmez → `.env` kullan, `.gitignore`'da

## Önemli hatırlatma

Kullanıcı (Mesut) tarımsal AI alanında yeni. Açıklamalar net, adım adım ve uygulanabilir
olmalı. Teknik jargonu Türkçe karşılığıyla ver. Bir sonraki somut adımı her zaman belirt.
