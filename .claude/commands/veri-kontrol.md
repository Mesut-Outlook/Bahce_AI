---
description: Veri setini analiz eder — sınıf dağılımı, dengesizlik, kalite uyarıları, eksik sınıflar.
argument-hint: "(opsiyonel) belirli bir sınıf adı"
---

Veri setini analiz et. Eğer `$ARGUMENTS` verilmişse sadece o sınıfa odaklan, yoksa tümü.

1. `scripts/check_dataset.py` varsa çalıştır; yoksa `data/labeled/` altındaki klasörleri
   tarayıp her sınıftaki fotoğraf sayısını say.
2. Sınıf dağılımını bir tablo halinde göster (sınıf adı → fotoğraf sayısı).
3. Dengesizliği tespit et: en kalabalık ve en az dolu sınıfı karşılaştır. Oran 3:1'i
   geçiyorsa uyar.
4. Hedefe göre eksiği hesapla: transfer learning için sınıf başına min 100–150 fotoğraf.
   Hangi sınıflar hedefin altında, kaç fotoğraf daha lazım?
5. `veri-toplama` agent'ına devredilecek somut çekim listesi öner (örn: "zeytin_dal-kanseri
   için 80 fotoğraf daha, tercihen farklı ağaçlardan").

Sonucu net bir tablo + eylem listesiyle bitir.
