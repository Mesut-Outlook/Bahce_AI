"""
Veri seti kontrol script'i.
data/labeled/ altındaki sınıf klasörlerini sayar, dengesizliği raporlar.

Kullanım:
    python scripts/check_dataset.py
"""

from pathlib import Path

HEDEF_MIN = 100   # transfer learning için sınıf başına minimum hedef
DENGESIZLIK_ORANI = 3.0  # en kalabalık / en az; bunu aşarsa uyar
GORUNTU_UZANTI = {".jpg", ".jpeg", ".png", ".webp"}


def say():
    kok = Path(__file__).resolve().parents[1]
    labeled = kok / "data" / "labeled"
    if not labeled.exists():
        print("data/labeled/ bulunamadı.")
        return

    siniflar = {}
    for klasor in sorted(labeled.iterdir()):
        if not klasor.is_dir() or klasor.name == "belirsiz":
            continue
        adet = sum(1 for f in klasor.iterdir()
                   if f.suffix.lower() in GORUNTU_UZANTI)
        siniflar[klasor.name] = adet

    if not siniflar:
        print("Henüz etiketlenmiş sınıf yok. data/labeled/ altında klasör aç.")
        return

    print("\n=== SINIF DAĞILIMI ===")
    print(f"{'Sınıf':<32} {'Adet':>6}  Durum")
    print("-" * 52)
    for ad, adet in siniflar.items():
        durum = "✓" if adet >= HEDEF_MIN else f"eksik ({HEDEF_MIN - adet} gerek)"
        print(f"{ad:<32} {adet:>6}  {durum}")

    toplam = sum(siniflar.values())
    en_az = min(siniflar.values())
    en_cok = max(siniflar.values())
    print("-" * 52)
    print(f"{'TOPLAM':<32} {toplam:>6}")
    print(f"Sınıf sayısı: {len(siniflar)}")

    if en_az > 0 and en_cok / en_az > DENGESIZLIK_ORANI:
        print(f"\n⚠️  DENGESİZLİK: en kalabalık {en_cok}, en az {en_az} "
              f"(oran {en_cok/en_az:.1f}:1). Az olan sınıflardan daha çok fotoğraf topla.")

    eksikler = {a: HEDEF_MIN - n for a, n in siniflar.items() if n < HEDEF_MIN}
    if eksikler:
        print("\n📸 TOPLANACAK:")
        for ad, eksik in eksikler.items():
            print(f"   - {ad}: {eksik} fotoğraf daha")
    else:
        print("\n✅ Tüm sınıflar minimum hedefte. Eğitime hazır olabilirsin.")


if __name__ == "__main__":
    say()
