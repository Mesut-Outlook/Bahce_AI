"""
Veri hazırlama script'i (iskelet).
data/labeled/ → 512x512 boyutlandır → train/val/test böl → data/processed/

Bu bir başlangıç iskeletidir; model-egitim agent'ı seçilen framework'e
(TensorFlow veya PyTorch) göre genişletir.

Kullanım:
    pip install pillow scikit-learn
    python scripts/prepare_data.py
"""

import shutil
from pathlib import Path

try:
    from PIL import Image
    from sklearn.model_selection import train_test_split
except ImportError:
    raise SystemExit("Eksik paket. Kur: pip install pillow scikit-learn")

HEDEF_BOYUT = (512, 512)
GORUNTU_UZANTI = {".jpg", ".jpeg", ".png", ".webp"}
# train / val / test oranları
ORAN_VAL = 0.20
ORAN_TEST = 0.10


def hazirla():
    kok = Path(__file__).resolve().parents[1]
    kaynak = kok / "data" / "labeled"
    hedef = kok / "data" / "processed"

    if not kaynak.exists():
        raise SystemExit("data/labeled/ bulunamadı.")

    for klasor in sorted(kaynak.iterdir()):
        if not klasor.is_dir() or klasor.name == "belirsiz":
            continue
        sinif = klasor.name
        dosyalar = [f for f in klasor.iterdir()
                    if f.suffix.lower() in GORUNTU_UZANTI]
        if len(dosyalar) < 5:
            print(f"  atlandı (az fotoğraf): {sinif} ({len(dosyalar)})")
            continue

        # train / (val+test) böl, sonra val / test böl
        train, gecici = train_test_split(
            dosyalar, test_size=ORAN_VAL + ORAN_TEST, random_state=42)
        val, test = train_test_split(
            gecici, test_size=ORAN_TEST / (ORAN_VAL + ORAN_TEST), random_state=42)

        for bolum, liste in [("train", train), ("val", val), ("test", test)]:
            cikti_dizin = hedef / bolum / sinif
            cikti_dizin.mkdir(parents=True, exist_ok=True)
            for f in liste:
                try:
                    img = Image.open(f).convert("RGB").resize(HEDEF_BOYUT)
                    img.save(cikti_dizin / f"{f.stem}.jpg", "JPEG", quality=90)
                except Exception as e:
                    print(f"  hata ({f.name}): {e}")

        print(f"  {sinif}: train={len(train)} val={len(val)} test={len(test)}")

    print(f"\n✅ Hazır veri: {hedef}")
    print("Sonraki adım: model-egitim agent'ı ile scripts/train.py oluştur.")


if __name__ == "__main__":
    hazirla()
