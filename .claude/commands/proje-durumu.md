---
description: Projenin genel durumunu raporlar — hangi fazdayız, veri durumu, sıradaki adım.
---

Projenin mevcut durumunu analiz et ve özetle:

1. `data/raw/` ve `data/labeled/` altındaki fotoğrafları say (sınıf başına).
2. `models/` altında eğitilmiş model var mı kontrol et.
3. `app/prototype/` çalışır durumda mı bak.
4. `docs/` altındaki dokümanların hangileri doldurulmuş kontrol et.

Sonra şu formatta raporla:

- **Mevcut faz:** (Faz 0 Prototip / Faz 1 Veri / Faz 2 Etiketleme / Faz 3 Eğitim / Faz 4 Uygulama)
- **Veri durumu:** toplam fotoğraf, sınıf sayısı, en eksik sınıf
- **Tamamlananlar:** ✓ listesi
- **Sıradaki somut adım:** tek ve net bir sonraki iş
- **Öneri:** o adım için hangi agent'ı veya komutu kullanmalı

Kısa ve uygulanabilir tut. Mesut'a "şimdi şunu yap" diyecek netlikte bitir.
