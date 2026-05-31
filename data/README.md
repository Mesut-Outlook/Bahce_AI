# data/

- **raw/** — Bahçeden çekilen ham fotoğraflar. Tarih klasörü aç (örn: `2026-05-31/`). ASLA silme.
- **labeled/** — Sınıf klasörlerine ayrılmış etiketli fotoğraflar (`agacturu_durum`). Bkz: `docs/03-etiketleme-standardi.md`
- **processed/** — `scripts/prepare_data.py` çıktısı; 512x512, train/val/test bölünmüş, eğitime hazır.

Büyük dosyalar `.gitignore` ile git'e girmez; sadece klasör yapısı korunur.
