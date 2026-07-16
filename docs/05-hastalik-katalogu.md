# 05 — Hastalık & Durum Kataloğu

> Bu katalog `tarim-uzmani` agent'ı tarafından doğrulanır ve genişletilir.
> Her sınıf için: belirtiler, fotoğrafta görünüm, öneri, karışabileceği sınıflar.
> `/yeni-sinif` komutu yeni girdileri buraya ekler.

⚠️ **Uyarı:** Buradaki öneriler genel bilgilendirmedir. Kesin teşhis, ilaç/gübre dozu ve yerel mevzuat için bağlı bulunduğunuz bölgedeki İl/İlçe Tarım ve Orman Müdürlüğü'ne veya uzman bir ziraat mühendisine danışın.

---

## ZEYTİN

### zeytin_saglikli
- **Görünüm:** Koyu yeşil, parlak, lekesiz yapraklar; düzgün sürgün gelişimi.
- **Not:** Her sorun için karşılaştırma temeli. Bol örnek toplanmalı.

### zeytin_halkali-leke (Peacock spot / Spilocaea oleagina)
- **Belirti:** İlkbaharda yaprak üst yüzeyinde siyahımsı-gri yuvarlak lekeler; lekenin
  çevresinde açık renkli halka ("tavus kuşu gözü" görünümü). Erken yaprak dökümü.
- **Fotoğrafta:** Yaprağın ÜST yüzeyi, yuvarlak halkalı lekeler. İlkbahar/nemli dönem.
- **Öneri (Bölgesel):** Yağışlı/nemli dönemler öncesinde bakırlı preparatlarla koruyucu uygulama; havalandırma için doğru budama; yere düşen enfekteli yaprakların bahçeden uzaklaştırılması. → Yerel tarım müdürlüğüne danış.
- **Karışabilir:** Antraknoz, besin eksikliği lekeleri.

### zeytin_dal-kanseri (Pseudomonas savastanoi)
- **Belirti:** Gövde, dal ve sürgünlerde ur/siğil şeklinde şişkinlikler; budama
  yaraları, dolu/sırık vuruğu sonrası açılan yerlerde gelişir.
- **Fotoğrafta:** Dal ve gövde yakın plan; ur/siğil dokusu.
- **Öneri (Bölgesel):** Enfekteli dalların sterilize edilmiş aletlerle budanıp uzaklaştırılması; budama yaralarının aşı macunu ile kapatılması; budama işleminin yağışsız/kuru havada yapılması.
- **Karışabilir:** Don çatlağı urları, mekanik yara.

### zeytin_antraknoz (Colletotrichum)
- **Belirti:** Meyvelerde çürüme ve mumyalaşma, yaprak lekeleri; nemli/yağışlı dönemde.
- **Fotoğrafta:** Meyve yakın plan (çürük/mumyalaşmış) ve lekeli yaprak.
- **Öneri (Bölgesel):** Hava sirkülasyonunu engelleyen sık dikimden kaçınma, havalandırma budaması; mumyalaşmış ve yere düşmüş meyvelerin imha edilmesi; yağışlı dönem öncesi koruyucu fungisid uygulaması. → Yerel tarım müdürlüğüne danış.
- **Karışabilir:** Halkalı leke, diğer meyve çürüklükleri.

### zeytin_zeytin-sinegi (Bactrocera oleae)
- **Belirti:** Meyvede iğne deliği şeklinde giriş izi, içte larva galerisi, erken
  meyve dökümü; yazın aktif.
- **Fotoğrafta:** Meyve yakın plan; delik ve çürüme.
- **Öneri (Bölgesel):** Kitlesel tuzaklar (feromon/besin) ile popülasyon takibi; eşik aşımında ruhsatlı preparatlarla zamanında ilaçlama; hasat sonrası yere düşen kurtlu meyvelerin temizlenmesi.
- **Karışabilir:** Antraknoz meyve çürümesi.

### zeytin_demir-eksikligi (Demir klorozu)
- **Belirti:** Genç yapraklarda damar aralarının sararması, damarların yeşil kalması
  (intervenal kloroz). Kireçli/yüksek pH topraklarda yaygın.
- **Fotoğrafta:** Genç yaprak; yeşil damar + sarı doku kontrastı.
- **Öneri (Bölgesel):** Detaylı toprak ve yaprak analizi; yüksek pH ve kireç oranına sahip topraklarda damla sulama veya yapraktan demir şelat (Fe-EDDHA) takviyesi; aşırı/düzensiz sulamadan kaçınma.
- **Karışabilir:** Azot eksikliği (o yaşlı yaprakta), su stresi sarısı.

### zeytin_su-stresi
- **Belirti:** Yaprakta solgunluk, kıvrılma, donuklaşma, uç kurumaları; yaz sıcağında
  ve yetersiz sulamada. Zeytin yıllık 650–800 mm su ister, yazın sulama gerekir.
- **Fotoğrafta:** Solgun/kıvrık yapraklar, genel taç görünümü.
- **Öneri (Bölgesel):** Bölgesel buharlaşma oranlarına göre derin ve düzenli sulama; toprak nemini korumak için malçlama; kök boğulmasını engellemek için aşırı ve drenajsız sulamadan kaçınma.
- **Karışabilir:** Besin eksikliği sarısı, verticillium solgunluğu.

---

## MEYVE AĞAÇLARI (genişletilecek)

Adana'da yaygın: nar, incir, narenciye, şeftali, kayısı, erik. Her tür için
`/yeni-sinif` ile sağlıklı + yaygın hastalıkları eklenecek. Örnek başlıklar:

- `nar_saglikli`, `nar_yaprak-leke`
- `incir_saglikli`, `incir_yaprak-pas`
- `narenciye_saglikli`, `narenciye_demir-eksikligi`
- Genel: külleme, ateş yanıklığı, pas, kök çürüklüğü, demir kloroz

---

## Katalog girdi şablonu (yeni sınıf eklerken)

```
### agacturu_durum
- **Belirti:** ...
- **Fotoğrafta:** (hangi parça, hangi yüz, hangi mevsim) ...
- **Öneri (Adana):** ... → Ziraat müdürlüğüne danış.
- **Karışabilir:** ...
```
