# 🫒 Prototip — Web & CLI Fotoğraf Analizi

Veri toplamadan ve model eğitmeden BUGÜN çalışan teşhis araçları. Hem **CLI** (Komut satırı) hem de **Streamlit** (Web arayüzü) desteği bulunmaktadır.

## ⚙️ Kurulum

Gereksinimleri yükleyin:
```bash
pip install -r ../../requirements.txt
```

`.env` dosyanıza API anahtarınızı ekleyin (Örn: `OPENAI_API_KEY` veya `ANTHROPIC_API_KEY`).

---

## 💻 Seçenek A: Streamlit Web Uygulaması (Önerilen)

Kullanıcı dostu, modern bir web arayüzü üzerinden fotoğraflarınızı sürükleyip bırakarak teşhis koymak ve bahçe eğitim verilerinizin durumunu izlemek için:

```bash
streamlit run app.py
```

---

## 🖥️ Seçenek B: CLI (Komut Satırı) Aracı

Terminal üzerinden hızlıca analiz yapmak için:

```bash
python analyze.py /yol/yaprak_fotograf.jpg
```

---

## 🔍 Çıktı Standardı
Her iki araç da size Türkçe olarak iki parçalı rapor sunar:
1. **TEŞHİS:** Sorun (hastalık, zararlı, besin eksikliği vb.) ve doğruluk güven yüzdesi.
2. **NE YAPMALI:** Adana iklimine özel somut çözüm adımları.

