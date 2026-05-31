# 02 — Veri Toplama Rehberi

Bahçeden makine öğrenmesi için kaliteli fotoğraf toplama rehberi. Sahada telefonla
uygulanabilir şekilde yazıldı.

## Ne kadar fotoğraf?

| Senaryo | Sınıf başına hedef |
|---------|--------------------|
| İdeal (ikili) | 1.000–2.000 |
| Çok sınıflı | 500–1.000 |
| **Transfer learning (başlangıç)** | **100–200** ✅ buradan başla |

Veri artırma (augmentation) ile eğitimde etkili sayı 2–5 kat artar. Yani 150 gerçek
fotoğraf, eğitimde ~500–750 etkisi yapar.

**İlk hedef:** 5 sınıf × 150 fotoğraf ≈ 750 fotoğraf.

## Her ağaçtan 4 tip kare

1. **Yaprak yakın plan** — lekeli/renk değişimli yaprak, hem üst hem alt yüz
2. **Genel ağaç görünümü** — tüm taç, seyreklik/solgunluk var mı
3. **Dal ve gövde** — kanser yarası, ur, reçine akışı, kabuk rengi
4. **Meyve** (varsa) — çürüme, leke, şekil bozukluğu, erken dökülme

## Çekim kalite kuralları ✅

- Net görüntü — bulanık olan veri setine GİRMEZ
- Doğal gün ışığı — öğlen keskin gölgelerinden ve parlamadan kaçın
- Sabit/sade arka plan tercih et (gökyüzü, toprak), karmaşık arka planı azalt
- Sorunlu bölge kareye net girsin, çok uzaktan çekme
- Farklı şiddet seviyeleri çek: hafif / orta / ağır
- Aynı sorunu farklı ağaçlardan çek (tek ağaca bağlı kalma)

## Çekme ❌

- Bulanık, karanlık, aşırı parlak fotoğraflar
- İki sorunu aynı anda gösteren karışık kareler (model şaşırır)
- Tekrarlayan neredeyse aynı kareler (çeşitlilik önemli)

## Mevsimsel takvim (Adana)

| Dönem | Öncelikli çekim |
|-------|-----------------|
| İlkbahar (Mart–Mayıs) | Halkalı leke belirginleşir, yeni sürgün, çiçeklenme |
| Yaz (Haziran–Ağustos) | Zeytin sineği, su stresi, sıcak stresi, besin eksikliği |
| Sonbahar (Eylül–Kasım) | Meyve sorunları, antraknoz, hasat dönemi |
| Kış (Aralık–Şubat) | Don zararı, dal kanseri, budama sonrası yaralar |

## Pratik saha checklist

- [ ] Telefonu temizle, lens lekesiz olsun
- [ ] Her ağaca bir numara ver (not al — hangi ağaç hangi durum)
- [ ] Sorunlu yaprağı kopararak sade zemine koyup da çekebilirsin
- [ ] Her çekimde "bu hangi sınıf" diye not düş (sonra etiketlemeyi kolaylaştırır)
- [ ] Sağlıklı örnekleri de unutma — her sorun için sağlıklı karşılığı şart
- [ ] Fotoğrafları `data/raw/` içine, tarih klasörü açarak aktar (örn: `2026-05-31/`)

## Çekim sonrası

Ham fotoğraflar `data/raw/` içine. Etiketleme `data/labeled/`'da yapılır
(bkz. `03-etiketleme-standardi.md`). Ham klasörü asla silme — yeniden etiketleme
gerekirse lazım olur.
