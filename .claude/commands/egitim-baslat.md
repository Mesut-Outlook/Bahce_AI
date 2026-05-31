---
description: Model eğitim sürecini başlatır — önce veri hazır mı kontrol eder, sonra eğitimi kurar ve çalıştırır.
---

Model eğitimini başlat. Acele etme; önce hazırlık kontrolü yap.

1. **Ön kontrol:** `/veri-kontrol` mantığıyla veri setini denetle. Eğer herhangi bir
   sınıf 100 fotoğrafın altındaysa DUR ve uyar — eğitime girmeden önce veri toplanmalı.
   (Transfer learning ile yine de denenebilir ama kullanıcıya riski söyle.)

2. **Veri hazırlama:** `scripts/prepare_data.py` ile fotoğrafları 512×512'ye boyutlandır,
   augmentation uygula, train/val/test (70/20/10) böl. Çıktı `data/processed/`'a gitsin.

3. **Mimari kararı:** `model-egitim` agent'ını çağır. Veri miktarına göre uygun modeli
   (MobileNetV2 / EfficientNet-B0) ve transfer learning ayarlarını belirlet.

4. **Eğitim:** `scripts/train.py`'yi çalıştır (yoksa model-egitim agent'ına yazdır).
   GPU yoksa Google Colab notebook'u öner ve `notebooks/` altına hazırla.

5. **Değerlendirme:** Eğitim bitince doğruluk, F1 ve karışıklık matrisini raporla.
   Hangi sınıflar karışıyor? Bunu veri toplama önerisine çevir.

6. **Dışa aktar:** Model %85+ doğruluğa ulaştıysa TFLite/ONNX'e çevirip `models/`'a koy
   ve `uygulama-gelistirici` agent'ına "Aşama 2 hazır" sinyali ver.

Her adımda ne yaptığını ve sonucu özetle. Başarısızsa modeli büyütmeden önce veri
kalitesini sorgula.
