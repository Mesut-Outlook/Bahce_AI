#!/bin/bash

# Klasör dizinini ayarla
cd "$(dirname "$0")/.."

echo "=============================================="
echo "🫒 Zeytin & Meyve Bahçesi AI Başlatıcı"
echo "=============================================="
echo ""

# Python Sanal Ortamı (venv) kontrolü ve kurulumu
if [ ! -d "venv" ]; then
    echo "📦 Sanal ortam (venv) oluşturuluyor..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Hata: python3-venv yüklü olmayabilir. Sistem paketlerinizi kontrol edin."
        exit 1
    fi
fi

# Sanal ortamı aktif et
source venv/bin/activate

# Paketleri yükle/güncelle
echo "📥 Gerekli paketler yükleniyor/güncelleniyor (Pillow, Streamlit, OpenAI, Anthropic vb.)..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Hata: Kütüphaneler yüklenemedi."
    exit 1
fi

# Streamlit uygulamasını arka planda çalıştır
echo "🖥️ Streamlit sunucusu başlatılıyor..."
cd app/prototype
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.enableCORS false --server.enableXsrfProtection false > ../../streamlit.log 2>&1 &
STREAMLIT_PID=$!


# Sunucunun ayağa kalkması için kısa bir süre bekle
sleep 3

# Bilgisayarın yerel ağ IP adresini bul
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "=============================================="
echo "📶 YEREL AĞ BAĞLANTISI (Aynı Wi-Fi üzerindeki cihazlar için):"
echo "👉 http://${LOCAL_IP}:8501"
echo "=============================================="
echo ""

# Telefonundan her yerden (bahçeden) girmek için SSH Tüneli oluştur (localhost.run servisi ile)
echo "🌐 Telefonla internet üzerinden (her yerden) erişim için güvenli tünel kuruluyor..."
ssh -o StrictHostKeyChecking=no -R 80:localhost:8501 nokey@localhost.run > ../../tunnel.log 2>&1 &
TUNNEL_PID=$!

# Tünel linkinin üretilmesi için bekle ve loglardan linki oku
sleep 5
TUNNEL_URL=$(grep -o -E "https://[a-zA-Z0-9.-]+\.lhr\.life" ../../tunnel.log | head -n 1)

if [ -z "$TUNNEL_URL" ]; then
    # Alternatif domain kontrolü
    TUNNEL_URL=$(grep -o -E "https://[a-zA-Z0-9.-]+\.lhrtunnel\.link" ../../tunnel.log | head -n 1)
fi

echo ""
if [ -n "$TUNNEL_URL" ]; then
    echo "=============================================="
    echo "📱 TELEFON / İNTERNET ERİŞİM LİNKİ (Bahçeden girmek için):"
    echo "👉 $TUNNEL_URL"
    echo "=============================================="
else
    echo "⚠️ Güvenli internet linki henüz üretilemedi. (Loglar kontrol ediliyor...)"
    echo "Yerel tünel logu çıktısı:"
    cat ../../tunnel.log
    echo ""
    echo "İpucu: Birkaç saniye sonra sayfayı yenileyebilir veya tekrar başlatabilirsiniz."
fi
echo ""
echo "💡 Kapatmak için terminalde Ctrl+C tuşlarına basın..."

# Ctrl+C basıldığında çalışan arka plan işlemlerini güvenle kapat
cleanup() {
    echo ""
    echo "🛑 Sunucular kapatılıyor..."
    kill $STREAMLIT_PID 2>/dev/null
    kill $TUNNEL_PID 2>/dev/null
    echo "✓ Sunucular başarıyla durduruldu."
    exit 0
}

trap cleanup INT

# Tünel açık kaldığı sürece scripti beklet
wait
