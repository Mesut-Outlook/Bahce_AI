# 01 — Proje Planı

## Vizyon

Adana'daki aile bahçesinde zeytin ve meyve ağaçlarının fotoğrafından sağlık durumunu
tespit eden, "ağacın neye ihtiyacı var" sorusuna cevap veren bir yapay zeka aracı.

## Çıktı tanımı

Kullanıcı bir yaprak/dal/meyve fotoğrafı yükler. Araç iki parçalı cevap döner:

1. **Teşhis:** Ne sorun var? (hastalık / zararlı / besin eksikliği / su stresi / sağlıklı)
2. **Öneri:** Adana koşullarında ne yapmalı? (sulama, gübre, ilaçlama, budama vb.)

## Fazlar

### Faz 0 — Prototip (Tamamlandı ✅)
Streamlit web uygulaması (sürükle-bırak destekli, premium yeşil arayüz) ve CLI araçları tamamlandı. OpenAI (GPT-4o) ve Anthropic (Claude 3.5) API desteği ve telefonla her yerden erişim için tünel sistemi kuruldu. → `app/prototype/app.py`


### Faz 1 — Veri toplama (sezon boyu)
Bahçeden sistematik fotoğraf çekimi. Sınıf başına 100–200 fotoğraf hedefi.
→ `docs/02-veri-toplama-rehberi.md`, `veri-toplama` agent'ı

### Faz 2 — Etiketleme
Fotoğrafları sınıf klasörlerine ayırma, kalite kontrol.
→ `docs/03-etiketleme-standardi.md`, `etiketleme` agent'ı

### Faz 3 — Model eğitimi
Transfer learning ile kendi modelini eğit, değerlendir, optimize et.
→ `docs/04-model-mimarisi.md`, `model-egitim` agent'ı

### Faz 4 — Uygulama
Eğitilmiş modeli telefon/web aracına dönüştür (offline çalışabilen).
→ `docs/06-uygulama-mimarisi.md`, `uygulama-gelistirici` agent'ı

## İlk hedef sınıflar (gerçekçi başlangıç)

Tüm hastalıkları aynı anda hedefleme. İlk model 5–6 sınıf:

| Sınıf | Klasör adı |
|-------|-----------|
| Sağlıklı zeytin yaprağı | `zeytin_saglikli` |
| Halkalı leke | `zeytin_halkali-leke` |
| Zeytin sineği zararı | `zeytin_zeytin-sinegi` |
| Demir eksikliği (kloroz) | `zeytin_demir-eksikligi` |
| Su stresi | `zeytin_su-stresi` |

Bu çalıştıktan sonra meyve ağaçları ve diğer hastalıklar eklenir (`/yeni-sinif`).

## Başarı ölçütü

- Faz 0: prototip 5 fotoğraftan en az 4'ünü doğru yorumlasın (göz kontrolü)
- Faz 3: doğrulama setinde %85+ doğruluk
- Faz 4: telefonda internetsiz çalışan, 2 saniyede sonuç veren araç

## Riskler ve önlemler

- **Az veri → overfitting:** transfer learning + augmentation + early stopping
- **Sınıf karışması:** `tarim-uzmani` ile görsel ayırt edici belirtileri netleştir
- **Dengesiz veri:** her sınıfta benzer fotoğraf sayısı, gerekirse class weighting
- **Mevsim kısıtı:** bazı hastalıklar sadece belirli mevsimde → yıllık çekim takvimi
