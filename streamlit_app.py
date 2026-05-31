import sys
from pathlib import Path

# Proje kök dizinini ve prototip klasörünü sistem yoluna ekle
proje_koku = Path(__file__).resolve().parent
sys.path.append(str(proje_koku / "app" / "prototype"))

# app/prototype/app.py uygulamasını çalıştır
import app
