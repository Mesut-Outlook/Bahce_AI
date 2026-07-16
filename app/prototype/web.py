"""
Bahçe AI — Web Arayüzü
Telefon tarayıcısından fotoğraf yükleyip teşhis alınabilir.

Çalıştır:
    .venv/bin/python3 app/prototype/web.py
Sonra telefonda aç:
    http://192.168.68.130:5000
"""

import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template_string, request
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

SISTEM_PROMPTU = """Sen deneyimli bir ziraat mühendisisin. Sana bir bitki/ağaç/yaprak/dal/meyve
fotoğrafı gönderilecek. Kullanıcı ayrıca bulunduğu konumu ve ağaç türünü belirtebilir —
belirtmemişse fotoğraftan çıkarmaya çalış.

Teşhiste şunları değerlendir:
- Hastalık (mantar, bakteri, virüs)
- Zararlı (böcek, akar, vb.)
- Besin eksikliği (demir, azot, çinko, vb.)
- Çevresel stres (su stresi, don, sıcak, tuzluluk)
- Sağlıklı (sorun yok)

Konum verilmişse önerilerini o bölgenin iklimine ve koşullarına göre uyarla.
Konum verilmemişse genel geçer öneriler ver.

Cevabını HER ZAMAN şu iki başlıkla, Türkçe ve sade dille ver:

🔍 TEŞHİS
- Tespit ettiğin bitki/ağaç türü (fotoğraftan anlaşılıyorsa)
- Ne sorun var (hastalık/zararlı/besin eksikliği/stres/sağlıklı)
- Güven düzeyin (yüksek/orta/düşük) ve nedeni
- Emin değilsen hangi açıdan ek fotoğraf gerektiğini söyle

✅ NE YAPMALI
- Somut adımlar (sulama/gübre/budama/ilaçlama yaklaşımı)
- Konum verilmişse o bölgenin tarım otoritesine danışılmasını öner
- İlaç/gübre için kesin doz verme

Fotoğraf belirsizse veya bitki tanınamıyorsa dürüst ol, uydurma."""


def sistem_promptu_olustur(konum: str, agac_turu: str) -> str:
    ek = []
    if konum.strip():
        ek.append(f"Kullanıcının konumu: {konum.strip()}")
    if agac_turu.strip():
        ek.append(f"Kullanıcının belirttiği ağaç/bitki türü: {agac_turu.strip()}")
    if ek:
        return SISTEM_PROMPTU + "\n\nEk bağlam:\n" + "\n".join(ek)
    return SISTEM_PROMPTU


HTML = """<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bahçe AI</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: sans-serif; background: #f4f7f0; color: #222; }
    .kapsam { max-width: 600px; margin: 0 auto; padding: 20px; }
    h1 { color: #3a6b1a; font-size: 1.4rem; margin-bottom: 4px; }
    .altyazi { color: #666; font-size: 0.9rem; margin-bottom: 20px; }
    .form-alan { background: white; border-radius: 12px; padding: 20px;
                  box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px; }
    label { display: block; font-weight: bold; margin-bottom: 6px; color: #3a6b1a; }
    .alan-grubu { margin-bottom: 16px; }
    input[type=text] { width: 100%; padding: 10px 12px; border: 1px solid #ccc;
                        border-radius: 8px; font-size: 0.95rem; }
    input[type=text]:focus { outline: none; border-color: #3a6b1a; }
    .ipucu { font-size: 0.8rem; color: #888; margin-top: 4px; }
    input[type=file] { width: 100%; padding: 10px; border: 2px dashed #bcd89a;
                        border-radius: 8px; background: #f9fdf5; cursor: pointer; }
    .onizleme { width: 100%; max-height: 280px; object-fit: contain;
                 border-radius: 8px; margin-top: 12px; display: none; }
    button { width: 100%; padding: 14px; background: #3a6b1a; color: white;
              border: none; border-radius: 8px; font-size: 1.1rem;
              cursor: pointer; margin-top: 14px; }
    button:hover { background: #2e5514; }
    button:disabled { background: #999; cursor: not-allowed; }
    .sonuc { background: white; border-radius: 12px; padding: 20px;
              box-shadow: 0 2px 8px rgba(0,0,0,0.08); white-space: pre-wrap;
              line-height: 1.7; font-size: 0.95rem; }
    .hata { color: #c0392b; }
    .yukluyor { text-align: center; color: #3a6b1a; padding: 20px;
                 display: none; font-size: 1rem; }
  </style>
</head>
<body>
<div class="kapsam">
  <h1>🌿 Bahçe AI</h1>
  <p class="altyazi">Yaprak veya dal fotoğrafı çek, teşhis al.</p>

  <div class="form-alan">
    <form id="form" method="POST" enctype="multipart/form-data">

      <div class="alan-grubu">
        <label for="konum">Konum <span style="font-weight:normal;color:#888">(isteğe bağlı)</span></label>
        <input type="text" id="konum" name="konum"
               placeholder="örn: Adana, Amsterdam, Mersin..."
               value="{{ konum or '' }}">
        <p class="ipucu">Konuma göre iklim bazlı öneri alırsın.</p>
      </div>

      <div class="alan-grubu">
        <label for="agac_turu">Ağaç / Bitki Türü <span style="font-weight:normal;color:#888">(isteğe bağlı)</span></label>
        <input type="text" id="agac_turu" name="agac_turu"
               placeholder="örn: zeytin, nar, incir, elma..."
               value="{{ agac_turu or '' }}">
        <p class="ipucu">Boş bırakırsan fotoğraftan anlamaya çalışır.</p>
      </div>

      <div class="alan-grubu">
        <label for="fotograf">Fotoğraf</label>
        <input type="file" id="fotograf" name="fotograf"
               accept="image/*" capture="environment" required>
        <img id="onizleme" class="onizleme" alt="Önizleme">
      </div>

      <button type="submit" id="btn">Analiz Et</button>
    </form>
  </div>

  <div class="yukluyor" id="yukluyor">⏳ Analiz ediliyor, lütfen bekleyin...</div>

  {% if sonuc %}
  <div class="sonuc {% if hata %}hata{% endif %}">{{ sonuc }}</div>
  {% endif %}
</div>

<script>
  document.getElementById('fotograf').addEventListener('change', function() {
    const dosya = this.files[0];
    if (!dosya) return;
    const okuyucu = new FileReader();
    okuyucu.onload = e => {
      const img = document.getElementById('onizleme');
      img.src = e.target.result;
      img.style.display = 'block';
    };
    okuyucu.readAsDataURL(dosya);
  });

  document.getElementById('form').addEventListener('submit', function() {
    document.getElementById('btn').disabled = true;
    document.getElementById('btn').textContent = 'Analiz ediliyor...';
    document.getElementById('yukluyor').style.display = 'block';
  });
</script>
</body>
</html>"""


@app.route("/", methods=["GET", "POST"])
def ana_sayfa():
    sonuc = None
    hata = False
    konum = ""
    agac_turu = ""

    if request.method == "POST":
        konum = request.form.get("konum", "")
        agac_turu = request.form.get("agac_turu", "")
        dosya = request.files.get("fotograf")

        if not dosya or dosya.filename == "":
            sonuc = "Lütfen bir fotoğraf seçin."
            hata = True
        else:
            uzanti = Path(dosya.filename).suffix.lower()
            medya = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                     ".png": "image/png", ".webp": "image/webp"}.get(uzanti, "image/jpeg")
            gorsel_verisi = base64.standard_b64encode(dosya.read()).decode("utf-8")

            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                sonuc = "API anahtarı bulunamadı. .env dosyasını kontrol edin."
                hata = True
            else:
                try:
                    client = OpenAI(api_key=api_key)
                    yanit = client.chat.completions.create(
                        model="gpt-5.6",
                        max_completion_tokens=1024,
                        messages=[
                            {"role": "system", "content": sistem_promptu_olustur(konum, agac_turu)},
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:{medya};base64,{gorsel_verisi}"
                                        },
                                    },
                                    {
                                        "type": "text",
                                        "text": "Bu bitkinin/ağacın durumunu değerlendir. Teşhis ve öneri ver.",
                                    },
                                ],
                            },
                        ],
                    )
                    sonuc = yanit.choices[0].message.content
                except Exception as e:
                    sonuc = f"Hata oluştu: {e}"
                    hata = True

    return render_template_string(HTML, sonuc=sonuc, hata=hata, konum=konum, agac_turu=agac_turu)


if __name__ == "__main__":
    print("Telefonda şu adresi aç: http://192.168.68.130:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
