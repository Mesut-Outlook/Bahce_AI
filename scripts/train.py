"""
Zeytin & Meyve Bahçesi AI — Gelişmiş Model Eğitim Scripti (PyTorch)

Bu script, data/processed/ altındaki verileri kullanarak transfer learning
yöntemiyle zeytin ve meyve yaprağı hastalıklarını teşhis eden bir derin öğrenme
modeli eğitir.

Özellikler:
    - Gelişmiş veri artırımı (Data Augmentation) ile aşırı öğrenmeyi (overfitting) önler.
    - Önceden eğitilmiş MobileNetV2 (telefonda çalışacak şekilde hafif) mimarisini temel alır.
    - Sınıf sayılarını klasör yapısından dinamik tespit eder.
    - Eğitim sonunda doğruluk (accuracy), kayıp (loss) grafiklerini ve detaylı
      sınıflandırma raporunu (precision, recall, F1) çıkarır.

Gereksinimler:
    pip install torch torchvision matplotlib pandas scikit-learn

Kullanım:
    python scripts/train.py --epochs 15 --batch-size 32 --lr 0.0001
"""

import os
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from sklearn.metrics import classification_report, confusion_matrix

def egitimi_baslat(epochs=15, batch_size=32, learning_rate=1e-4):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️  Eğitim cihazı: {device}")

    # Dizinleri tanımla
    proje_koku = Path(__file__).resolve().parents[1]
    data_dir = proje_koku / "data" / "processed"
    models_dir = proje_koku / "models"
    models_dir.mkdir(exist_ok=True)

    train_dir = data_dir / "train"
    val_dir = data_dir / "val"
    test_dir = data_dir / "test"

    if not train_dir.exists() or not val_dir.exists():
        print("❌ HATA: İşlenmiş veri bulunamadı! Lütfen önce scripts/prepare_data.py çalıştırın.")
        return

    # Sınıf isimlerini ve adetlerini dinamik al
    siniflar = sorted([d.name for d in train_dir.iterdir() if d.is_dir()])
    num_classes = len(siniflar)
    print(f"📊 Bulunan Sınıf Sayısı: {num_classes}")
    print(f"🏷️ Sınıflar: {', '.join(siniflar)}")

    # Gelişmiş Veri Artırımı (Augmentation) ve Normalizasyon
    # Modelin farklı ışık, yön ve açılarda genel başarısını (generalization) artırır
    data_transforms = {
        'train': transforms.Compose([
            transforms.RandomResizedCrop(224, scale=(0.8, 1.0)), # Yaprağı rastgele kırp/yakınlaştır
            transforms.RandomHorizontalFlip(),                  # Yatay ayna görüntüsü
            transforms.RandomVerticalFlip(),                    # Dikey ayna görüntüsü
            transforms.RandomRotation(30),                      # ±30 derece döndürme
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1), # Farklı gün ışığı simülasyonu
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]) # ImageNet standartları
        ]),
        'val_test': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    }

    # Datasetleri Yükle
    image_datasets = {
        'train': datasets.ImageFolder(str(train_dir), data_transforms['train']),
        'val': datasets.ImageFolder(str(val_dir), data_transforms['val_test']),
    }
    
    if test_dir.exists():
        image_datasets['test'] = datasets.ImageFolder(str(test_dir), data_transforms['val_test'])

    # DataLoader'ları oluştur
    dataloaders = {
        'train': DataLoader(image_datasets['train'], batch_size=batch_size, shuffle=True, num_workers=2),
        'val': DataLoader(image_datasets['val'], batch_size=batch_size, shuffle=False, num_workers=2),
    }
    if 'test' in image_datasets:
        dataloaders['test'] = DataLoader(image_datasets['test'], batch_size=batch_size, shuffle=False, num_workers=2)

    # 1. Model Mimarisi: Önceden eğitilmiş MobileNetV2 (Hafif ve mobil uyumlu)
    print("📥 Önceden eğitilmiş MobileNetV2 modeli indiriliyor...")
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)

    # Transfer Learning için ilk temel katmanları dondur (ImageNet bilgilerini koru)
    for param in model.parameters():
        param.requires_grad = False

    # Ajanın sınıf sayısına göre sınıflandırıcı başlığı (classifier head) güncelle
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, num_classes)
    )
    
    model = model.to(device)

    # Kayıp fonksiyonu ve Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.classifier.parameters(), lr=learning_rate)

    print("🚀 Model eğitimi başlatılıyor...")
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

    for epoch in range(epochs):
        print(f"\nEpoch {epoch+1}/{epochs}")
        print("-" * 10)

        # Her epoch için eğitim ve doğrulama aşaması
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            # Veri kümesinde gezin
            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                # İleri besleme (forward pass)
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    # Geri besleme ve güncelleme (backward pass + optimize)
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / len(image_datasets[phase])
            epoch_acc = running_corrects.double() / len(image_datasets[phase])

            print(f"{phase.capitalize()} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")
            
            history[f'{phase}_loss'].append(epoch_loss)
            history[f'{phase}_acc'].append(epoch_acc.item())

    print("\n🎉 Eğitim tamamlandı!")

    # Modeli Kaydet
    model_yolu = models_dir / "garden_model_pytorch.pt"
    torch.save(model.state_dict(), model_yolu)
    print(f"💾 Model kaydedildi: {model_yolu}")

    # Grafik oluştur
    egitim_grafigi_olustur(history, epochs, models_dir)

    # Test Seti ile Detaylı Değerlendirme (Varsa)
    if 'test' in dataloaders:
        print("\n🔍 Test seti ile detaylı performans analizi yapılıyor...")
        model.eval()
        true_labels = []
        pred_labels = []

        with torch.no_grad():
            for inputs, labels in dataloaders['test']:
                inputs = inputs.to(device)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                
                true_labels.extend(labels.cpu().numpy())
                pred_labels.extend(preds.cpu().numpy())

        print("\n📋 Sınıflandırma Raporu:")
        print(classification_report(true_labels, pred_labels, target_names=siniflar))


def egitim_grafigi_olustur(history, epochs, output_dir):
    """Eğitim kaybı ve doğruluk grafiklerini çizip kaydeder."""
    epochs_range = range(1, epochs + 1)
    
    plt.figure(figsize=(12, 4))
    
    # 1. Doğruluk (Accuracy) Grafiği
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, history['train_acc'], label='Eğitim Başarısı')
    plt.plot(epochs_range, history['val_acc'], label='Doğrulama Başarısı')
    plt.xlabel('Epoch')
    plt.ylabel('Doğruluk')
    plt.title('Eğitim ve Doğrulama Başarısı')
    plt.legend()
    
    # 2. Kayıp (Loss) Grafiği
    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, history['train_loss'], label='Eğitim Kaybı')
    plt.plot(epochs_range, history['val_loss'], label='Doğrulama Kaybı')
    plt.xlabel('Epoch')
    plt.ylabel('Kayıp (Loss)')
    plt.title('Eğitim ve Doğrulama Kaybı')
    plt.legend()
    
    plt.tight_layout()
    grafik_yolu = output_dir / "egitim_grafikleri.png"
    plt.savefig(grafik_yolu)
    print(f"📊 Eğitim grafikleri kaydedildi: {grafik_yolu}")
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zeytin & Meyve Bahçesi AI Model Eğitim Scripti")
    parser.add_argument("--epochs", type=int, default=15, help="Eğitim devir sayısı")
    parser.add_argument("--batch-size", type=int, default=32, help="Paket boyutu")
    parser.add_argument("--lr", type=float, default=1e-4, help="Öğrenme oranı (learning rate)")
    
    args = parser.parse_args()
    egitimi_baslat(epochs=args.epochs, batch_size=args.batch_size, learning_rate=args.lr)
