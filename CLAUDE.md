# CLAUDE.md — Bahçe AI Projesi

Bu dosya Claude Code tarafından her oturumda otomatik okunur. Projenin "anayasası"dır.

## Projenin amacı

Bitki ve ağaçların fotoğraflarından sağlık durumunu tespit eden bir yapay zeka aracı.
Kullanıcı konum ve bitki türü girer (isteğe bağlı), araç şunları ayırt eder:

- **Hastalık** (mantar, bakteri, virüs)
- **Zararlı** (böcek, akar)
- **Besin eksikliği** (demir, azot, çinko, vb.)
- **Çevresel stres** (su stresi, don, sıcak)
- **Sağlıklı** (sorun yok)

Çıktı her zaman iki parçalı: (1) teşhis, (2) "ne yapmalı" önerisi.
Konum verilirse o bölgenin iklimine göre uyarlanır.

## Kapsam

Adana'ya veya zeytin'e özel değil — her konum ve bitki türü desteklenir.
Mesut uygulamayı **Adana, Mersin ve Amsterdam'da** kullanıyor.

## Erişim

- **Streamlit Cloud:** https://bahceai.streamlit.app (her yerden, her cihazdan)
- **Yerel:** `bash scripts/start_app.sh` → `http://<yerel-ip>:8501`
- **GitHub:** https://github.com/Mesut-Outlook/Bahce_AI.git

## Uygulama özellikleri

- Konum + bitki türü → ana sayfada, isteğe bağlı
- Birden fazla fotoğraf yükleme (hepsi seçili modele gönderilir)
- Teşhis sonrası **ek fotoğraf** ekleyerek aynı konudan devam
- Teşhis sonrası **ağaç tanıtımı** (sulama takvimi, hasat, yaygın hastalıklar)
- Teşhis sonrası **"Yeni Arama Başlat"** butonu → fotoğrafları, konum/bitki alanlarını
  ve raporu tek tıkla sıfırlar
- Sağlayıcı seçimi: OpenAI (ChatGPT), Anthropic Claude Sonnet veya Google Gemini
  (sidebar'dan seçim). OpenAI seçilince hesapta kullanıma açık **tüm ChatGPT
  modelleri** `/models` uç noktasından dinamik çekilip listelenir (görsel üretim/ses/
  arama/kod modelleri filtrelenir); varsayılan `gpt-5.6-terra`.
- Açık tema `.streamlit/config.toml` (kök ve `app/prototype/`) ile sabitlenmiştir —
  ziyaretçinin sistem/tarayıcı koyu mod tercihine bakılmaksızın açık yeşil-krem
  palet kullanılır. Bu dosya `.gitignore`'da istisna tutulur (`secrets.toml` ve
  `credentials.toml` hâlâ hariç tutulur, asla commit edilmez).

## Klasör yapısı

```
Bahce_AI/
├── CLAUDE.md
├── streamlit_app.py        # Streamlit Cloud giriş noktası
├── requirements.txt
├── .env.example
├── .gitignore
├── .streamlit/config.toml  # Açık tema (Streamlit Cloud bunu okur)
├── app/
│   └── prototype/
│       ├── app.py          # Ana Streamlit uygulaması
│       ├── analyze.py      # CLI versiyonu
│       ├── web.py          # Flask versiyonu (port 5000)
│       └── .streamlit/config.toml  # Açık tema (yerel çalıştırma için)
├── scripts/
│   ├── start_app.sh        # Tek komutla başlatıcı
│   ├── check_dataset.py
│   ├── prepare_data.py
│   ├── download_inaturalist.py
│   └── train.py            # PyTorch/MobileNetV2 eğitim script'i (Faz 3)
├── data/
│   ├── raw/
│   ├── labeled/            # Sınıf klasörleri: agac-turu_durum
│   └── processed/
├── models/
├── notebooks/
└── docs/
```

## Çalıştırma prensipleri

1. **Önce küçük başla.** Transfer learning, PlantVillage bazlı. Sıfırdan eğitim yok.
2. **Veri kalitesi > veri miktarı.** Bulanık fotoğraf veri setine girmez.
3. **Her sınıf için "sağlıklı" karşılığı şart.**
4. **Türkçe çıktı.** Kullanıcıya dönük tüm metinler Türkçe; kod İngilizce.
5. **Konum/bitki asla sabit kodlanmaz.** Kullanıcıdan alınır.

## Fazlar

- **Faz 0 ✓:** ChatGPT (GPT-5.6) vision ile web prototipi (aktif, Streamlit Cloud'da yayında)
- **Faz 1:** Fotoğraf toplama (sınıf başına 100–200)
- **Faz 2:** Etiketleme
- **Faz 3:** Transfer learning (PyTorch/MobileNetV2, `scripts/train.py` hazır), %85+ doğruluk hedefi
- **Faz 4:** Offline telefon/web uygulaması

## Kod standartları

- Python 3.10+, sanal ortam: `venv/`
- Görüntü standardı: 512×512 px, RGB, JPEG/PNG
- Sınıf klasörü: `agac-turu_durum` (ör: `zeytin_halkali-leke`, `zeytin_saglikli`)
- API key: `.env` (yerel) veya Streamlit Cloud Secrets — asla repoya girmez

## Sub-agent'lar (`.claude/agents/`)

- **tarim-uzmani** → hastalık/zararlı/eksiklik teşhisi, bölgeye özgü sorular
- **veri-toplama** → fotoğraf çekim planı, kaç ve nasıl
- **etiketleme** → etiketleme standardı, kalite kontrol
- **model-egitim** → model mimarisi, transfer learning, eğitim script'leri
- **uygulama-gelistirici** → prototip ve son uygulama geliştirme

## Slash komutları

- `/proje-durumu` → genel durum raporu
- `/veri-kontrol` → veri seti analizi
- `/yeni-sinif` → yeni hastalık/durum sınıfı ekle
- `/egitim-baslat` → model eğitim süreci

## Önemli

Kullanıcı (Mesut) tarımsal AI'da yeni. Açıklamalar net, adım adım, Türkçe olmalı.
Teknik terimleri Türkçe karşılığıyla ver. Her zaman bir sonraki somut adımı belirt.
