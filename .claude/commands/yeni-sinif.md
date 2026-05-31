---
description: Projeye yeni bir hastalık/zararlı/eksiklik sınıfı ekler — katalog, klasör ve etiketleme standardını günceller.
argument-hint: "sınıf adı, örn: zeytin antraknoz"
---

Projeye yeni bir tespit sınıfı ekle: **$ARGUMENTS**

Sırayla şunları yap:

1. **Tarımsal doğrulama:** `tarim-uzmani` agent'ını çağır. Bu sınıfın belirtilerini,
   görsel görünümünü, hangi mevsimde/parçada görüldüğünü ve diğer sınıflarla karışma
   riskini tarif ettir. Adana koşullarına uygun "ne yapmalı" önerisini al.

2. **Katalog güncelle:** `docs/05-hastalik-katalogu.md`'ye yeni sınıfı standart formatta
   ekle (ad, belirtiler, fotoğrafta görünüm, öneri, karışabileceği sınıflar).

3. **Klasör oluştur:** `data/labeled/` altında standart adla klasör aç
   (`agac-turu_durum` formatı, Türkçe karakter yok, boşluk yerine tire).

4. **Veri planı:** `veri-toplama` agent'ından bu yeni sınıf için çekim planı al
   (kaç fotoğraf, hangi açı, hangi mevsim).

5. **Etiketleme notu:** `docs/03-etiketleme-standardi.md`'ye yeni sınıfı ekle ve
   varsa `etiketler.csv` şablonunu güncelle.

Bittiğinde yeni sınıfın eklendiğini ve sıradaki adımın (fotoğraf toplama) ne olduğunu
özetle.
