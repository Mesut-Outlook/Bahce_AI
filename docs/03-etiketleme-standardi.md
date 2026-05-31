# 03 — Etiketleme Standardı

Fotoğrafların tutarlı ve eğitime hazır şekilde etiketlenmesi için kurallar.

## Klasör (sınıf) yapısı

Sınıflandırma için en basit ve hızlı yöntem **klasör bazlı etiketleme**. Her sınıf
bir klasör, fotoğraflar ilgili klasöre kopyalanır:

```
data/labeled/
├── zeytin_saglikli/
├── zeytin_halkali-leke/
├── zeytin_zeytin-sinegi/
├── zeytin_demir-eksikligi/
├── zeytin_su-stresi/
├── nar_saglikli/
└── belirsiz/            # şüpheli/karışık — eğitime GİRMEZ
```

## Adlandırma kuralı

Format: **`agacturu_durum`**

- Hepsi küçük harf
- Türkçe karakter YOK (ç→c, ş→s, ı→i, ğ→g, ö→o, ü→u)
- Boşluk yerine tire (`-`)
- Örnekler: `zeytin_halkali-leke`, `zeytin_dal-kanseri`, `incir_yaprak-leke`

## etiketler.csv (opsiyonel ama önerilir)

Klasör yapısına ek olarak metadata tutmak modelin ve analizin kalitesini artırır:

```csv
dosya_adi,agac_turu,durum,siddet,cekim_tarihi,not
IMG_001.jpg,zeytin,halkali-leke,orta,2026-05-31,3 numarali agac
IMG_002.jpg,zeytin,saglikli,,2026-05-31,5 numarali agac
```

- `siddet`: hafif / orta / agir (sağlıklıda boş)
- Bu dosya `scripts/check_dataset.py` ile birlikte kullanılır

## Etiketleme kalite kuralları

1. **Bir fotoğraf = bir net sınıf.** Emin değilsen `belirsiz/`'e koy, zorlamaya çalışma.
2. **Şüpheli teşhisi doğrulat.** Hastalık ayrımından emin değilsen `tarim-uzmani`
   agent'ına fotoğrafı tarif et veya göster.
3. **Dengeyi koru.** Bir sınıf çok kalabalık, diğeri çok az olmasın. `/veri-kontrol`
   komutu dengesizliği raporlar.
4. **Sağlıklı sınıfı ihmal etme.** Her ağaç türü için bol "sağlıklı" örnek şart.

## Sınıflandırma mı, nesne tespiti mi?

- **Sınıflandırma (classification):** "Bu fotoğrafta halkalı leke var." → klasör bazlı
  yeterli. **Başlangıç için bunu seç.**
- **Nesne tespiti (detection):** "Yaprağın şu bölgesinde leke var." → LabelImg/Roboflow
  ile bounding box gerekir. Daha çok emek; sadece konum önemliyse.

## Araçlar

| Araç | Ne için | Not |
|------|---------|-----|
| Klasör bazlı | Sınıflandırma | En hızlı, ekstra araç gerekmez |
| LabelImg | Bounding box | Ücretsiz, masaüstü |
| Roboflow | Box + augmentation + export | Web tabanlı, ekip dostu |

## Akış

1. `data/raw/` → fotoğrafı incele
2. Doğru sınıf klasörüne `data/labeled/<sinif>/` kopyala
3. (Opsiyonel) `etiketler.csv`'ye satır ekle
4. Periyodik olarak `/veri-kontrol` çalıştır, eksik sınıfı gör
