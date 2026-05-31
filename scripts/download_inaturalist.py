"""
Zeytin & Meyve Bahçesi AI — iNaturalist Veri İndirme Aracı

iNaturalist API'sini kullanarak araştırma kalitesinde (research grade), 
açık lisanslı (Creative Commons) bitki, hastalık ve zararlı fotoğraflarını 
otomatik olarak indirir.

Gereksinimler:
    pip install requests

Kullanım:
    # 50 adet zeytin ağacı (Taxon ID: 55909) fotoğrafı indir:
    python scripts/download_inaturalist.py --taxon 55909 --limit 50 --out zeytin_saglikli

    # "halkalı leke" araması yaparak 30 fotoğraf indir:
    python scripts/download_inaturalist.py --query "Spilocaea oleagina" --limit 30 --out zeytin_halkali-leke
"""

import os
import sys
import argparse
from pathlib import Path

try:
    import requests
except ImportError:
    print("Eksik paket. Lütfen kurun: pip install requests")
    sys.exit(1)

# Sabit iNaturalist API URL'si
INAT_API_URL = "https://api.inaturalist.org/v1/observations"

def gorselleri_indir(taxon_id=None, query=None, limit=50, out_name=None):
    """iNaturalist API'sinden gözlemleri filtreleyip fotoğraflarını indirir."""
    
    # Çıktı klasörünü belirle
    proje_koku = Path(__file__).resolve().parents[1]
    
    if out_name:
        cikti_dizin = proje_koku / "data" / "raw" / out_name
    else:
        ad = f"inat_{taxon_id}" if taxon_id else f"query_{query.replace(' ', '_')}"
        cikti_dizin = proje_koku / "data" / "raw" / ad
        
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    
    print(f"🔍 iNaturalist sorgulanıyor...")
    
    # API Parametreleri
    params = {
        "quality_grade": "research", # Sadece uzmanlarca onaylanmış gözlemler
        "photos": "true",           # Sadece fotoğraflı gözlemler
        "per_page": min(limit, 200),# Sayfa başına çekilecek miktar
        "license": "cc-by,cc-by-nc,cc-by-sa", # Güvenli açık lisanslar
    }
    
    if taxon_id:
        params["taxon_id"] = taxon_id
    if query:
        params["q"] = query

    try:
        response = requests.get(INAT_API_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ API Hatası oluştu: {e}")
        return

    sonuclar = data.get("results", [])
    if not sonuclar:
        print("❌ Eşleşen gözlem bulunamadı. Lütfen parametreleri kontrol edin.")
        return

    print(f"✓ {len(sonuclar)} adet gözlem bulundu. Fotoğraflar indiriliyor...")
    
    indirilen_adet = 0
    
    for obs in sonuclar:
        if indirilen_adet >= limit:
            break
            
        obs_id = obs.get("id")
        photos = obs.get("observation_photos", [])
        
        for idx, obs_photo in enumerate(photos):
            if indirilen_adet >= limit:
                break
                
            photo_url = obs_photo.get("photo", {}).get("url")
            if not photo_url:
                continue
                
            # iNaturalist varsayılan olarak 'square' (küçük kare) sürümü verir. 
            # Eğitim için 'medium' veya 'large' sürümünü çekmek üzere URL'i değiştiriyoruz.
            photo_url = photo_url.replace("square", "medium")
            
            try:
                img_resp = requests.get(photo_url, timeout=10)
                img_resp.raise_for_status()
                
                # Dosya adını oluştur (obs_id + fotoğraf sırası)
                dosya_adi = f"inat_{obs_id}_{idx}.jpg"
                dosya_yolu = cikti_dizin / dosya_adi
                
                dosya_yolu.write_bytes(img_resp.content)
                indirilen_adet += 1
                
                print(f" [{indirilen_adet}/{limit}] İndirildi: {dosya_adi}")
            except Exception as e:
                print(f" ⚠️ Fotoğraf indirilemedi ({photo_url}): {e}")
                
    print(f"\n✅ Tamamlandı! {indirilen_adet} adet fotoğraf şuraya kaydedildi:\n👉 {cikti_dizin}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="iNaturalist Fotoğraf İndirici")
    parser.add_argument("--taxon", type=int, help="iNaturalist Taxon ID (örn: Zeytin için 55909)")
    parser.add_argument("--query", type=str, help="Arama sorgusu (örn: 'Spilocaea oleagina')")
    parser.add_argument("--limit", type=int, default=50, help="İndirilecek maksimum fotoğraf sayısı")
    parser.add_argument("--out", type=str, help="Çıktı klasör adı (data/raw/ altındaki)")
    
    args = parser.parse_args()
    
    if not args.taxon and not args.query:
        print("❌ HATA: --taxon veya --query parametrelerinden en az birini belirtmelisiniz.")
        parser.print_help()
        sys.exit(1)
        
    gorselleri_indir(taxon_id=args.taxon, query=args.query, limit=args.limit, out_name=args.out)
