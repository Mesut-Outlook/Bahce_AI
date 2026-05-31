# 04 — Model Mimarisi

> Bu doküman `model-egitim` agent'ı tarafından eğitim sırasında güncellenir.
> Aşağıdaki öneriler başlangıç noktasıdır.

## Yaklaşım: Transfer Learning

Sıfırdan model eğitmek binlerce fotoğraf ve büyük hesaplama gücü ister. Bunun yerine
**ImageNet veya PlantVillage ile önceden eğitilmiş** bir modeli temel alıp son katmanları
bahçe sınıflarımıza göre yeniden eğitiriz. Az veriyle yüksek doğruluk verir.

## Önerilen modeller

| Model | Avantaj | Ne zaman |
|-------|---------|----------|
| **MobileNetV2** | Hafif, telefonda hızlı çalışır | Offline mobil uygulama hedefi varsa ✅ |
| **EfficientNet-B0** | Hafif + yüksek doğruluk dengesi | Genel başlangıç önerisi ✅ |
| EfficientNetV2-S | Daha yüksek doğruluk | Veri çoğaldıkça, sunucu tarafı |

Literatürde zeytin yaprağı hastalıklarında MobileNetV2 ve EfficientNet tabanlı
modeller %96–99 doğruluğa ulaşmıştır (kontrollü veri setlerinde).

## Veri hattı (pipeline)

```
data/labeled/  →  512×512 boyutlandır  →  augmentation  →  train/val/test (70/20/10)
```

Augmentation teknikleri (eğitim setine):
- Yatay/dikey çevirme
- Hafif döndürme (±20°)
- Parlaklık/kontrast oynama
- Hafif yakınlaştırma/kırpma

> Not: Augmentation sadece eğitim setine uygulanır; doğrulama/test setine uygulanmaz.

## Eğitim ayarları (başlangıç)

- Batch size: 16–32
- Optimizer: Adam
- Learning rate: küçük (1e-4 civarı, fine-tuning olduğu için)
- Early stopping: doğrulama kaybı düşmeyi durdurunca dur (overfitting önler)
- Dropout: 0.2–0.5 (son katmanlarda)
- Az fotoğraflı sınıf varsa: class weighting

## Değerlendirme metrikleri

- **Accuracy** (doğruluk) — genel başarı
- **Precision / Recall / F1** — özellikle az örnekli sınıflar için
- **Confusion matrix** — HANGİ sınıflar birbirine karışıyor? En kritik çıktı.

Karışan sınıflar → `tarim-uzmani`'ya "bu ikisi görsel olarak nasıl ayrılır" sor +
`veri-toplama`'ya "şu sınıftan daha ayırt edici fotoğraf çek" geri bildirimi.

## Hedef

İlk model: doğrulama setinde **%85+**. Yetersizse:
1. Önce veri kalitesi/dengesi (en sık sebep)
2. Daha çok fotoğraf
3. Augmentation çeşitliliği
4. En son: daha büyük model

## Dışa aktarma

- **TensorFlow Lite (.tflite)** → telefonda offline çalışma (öncelik)
- **ONNX** → platform bağımsız
- Çıktı `models/` altına versiyonlu kaydedilir (örn: `model_v1_85acc.tflite`)

## Donanım

GPU yoksa **Google Colab** (ücretsiz GPU) kullan. Eğitim notebook'u `notebooks/` altında.
