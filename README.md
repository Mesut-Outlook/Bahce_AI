# 🫒 Zeytin & Meyve Bahçesi AI

Adana'daki bahçede bulunan zeytin ve meyve ağaçlarının fotoğraflarından **hastalık,
zararlı, besin eksikliği ve su stresini** tespit eden yapay zeka aracı.

> Fotoğraf çek → AI analiz etsin → "Ağacın neye ihtiyacı var" cevabını al.

---

## 🚀 Hızlı başlangıç (Claude Code ile)

Bu klasör bir **Claude Code projesi** olarak yapılandırıldı. Terminalde proje klasörüne
girip Claude Code'u başlat:

```bash
cd ~/Documents/PROJELER/zeytin-bahce-ai
claude
```

Claude Code `CLAUDE.md` dosyasını otomatik okuyacak ve projenin tüm bağlamını bilecek.
Sonra şunları deneyebilirsin:

```
/proje-durumu                    # nerede olduğumuzu görelim
"Bahçe fotoğraf çekim planı yap" # veri-toplama agent'ı devreye girer
/veri-kontrol                    # veri setini analiz et
/egitim-baslat                   # model eğitimini başlat
```

## 📁 Ne nerede?

| Klasör | İçerik |
|--------|--------|
| `docs/` | Proje planı, veri toplama rehberi, hastalık kataloğu, model mimarisi |
| `data/raw/` | Çektiğin ham fotoğraflar buraya |
| `data/labeled/` | Etiketlenmiş fotoğraflar (sınıf klasörleri) |
| `models/` | Eğitilmiş modeller |
| `app/prototype/` | Bugün çalışan hızlı analiz prototipi (Claude API) |
| `scripts/` | Veri hazırlama araçları |
| `.claude/agents/` | 5 uzman sub-agent |
| `.claude/commands/` | Hazır workflow'lar (slash komutları) |

## 🗺️ Yol haritası

1. **Faz 0 — Prototip (1 gün):** `app/prototype/` ile Claude API kullanarak hemen
   çalışan bir analiz aracı. Veri toplamadan önce konsepti test et.
2. **Faz 1 — Veri toplama (sezon boyu):** `docs/02-veri-toplama-rehberi.md`'ye göre
   bahçeden sistematik fotoğraf çek.
3. **Faz 2 — Etiketleme:** `docs/03-etiketleme-standardi.md`'ye göre etiketle.
4. **Faz 3 — Model eğitimi:** Transfer learning ile kendi modelini eğit.
5. **Faz 4 — Uygulama:** Telefon/web aracı haline getir.

## 📚 Önce bunları oku

- [`docs/01-proje-plani.md`](docs/01-proje-plani.md) — tam plan
- [`docs/02-veri-toplama-rehberi.md`](docs/02-veri-toplama-rehberi.md) — fotoğraf nasıl çekilir
- [`docs/05-hastalik-katalogu.md`](docs/05-hastalik-katalogu.md) — hangi durumlar tespit edilecek

## ⚙️ Kurulum

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Claude API prototipi için anahtarını `.env` dosyasına koy:

```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```
