# Buradan başla

## 1. Klasörü aç

VS Code → File → Open Folder → **WeAreChecking**.

İçinde README.md, bootstrap.py, notebooks ve src klasörlerini görmelisin.
Önceki Olist projesinin sanal ortamını kullanma.

## 2. Ortamı doğrula

Terminal → New Terminal; PowerShell kullan:

```powershell
.\.venv\Scripts\python.exe -m wearechecking doctor
```

Bu makinede ortam hazırlandıysa yeniden kurulum gerekmez. Başka makinede veya ZIP'ten yeni açtıysan:

```powershell
py -3.13 bootstrap.py
```

`py` bulunmazsa kurulu Python 3.12–3.14 yorumlayıcısıyla `bootstrap.py` çalıştır. Başarısız komutun çıktısını paylaş; eksik kurulumu başarılı sayma.

## 3. İlk iki hedef

| Hedef | Nerede? | Sen ne yapacaksın? | Ne zaman tamam? |
|---|---|---|---|
| 1 · Gerçek hafta sonu verisini anlamak | notebooks/01_weekend_data.ipynb | Seans/tur/sürücü ayrımını açıkla; lap_counts fonksiyonunu yaz | Veri kontrolleri + alıştırma kontrolü geçer; bir tur kaydını anlatabilirsin |
| 2 · İlk sıralama tahmini | notebooks/02_first_prediction.ipynb | qualifying_baseline fonksiyonunu yaz; tahmini kaydet; değerlendirmeyi yorumla | Tahmin 1..N olur; sonuç sızıntısı yoktur; decision note doldurulur |

İlk olarak yalnız **01 defterinin 1–3. adımlarını** çalıştır.
Üst sağdaki **Select Kernel → Python Environments → .venv** seç.

Beklediğimiz: Bahreyn hafta sonu tablosu, indirme kaynağı ve tur tablosunun ilk satırları.
Veri yoksa defterin gösterdiği fetch komutunu terminalde çalıştır, hücreyi tekrar çalıştır.
Defter kendi kendine indirme yapmaz.

## 4. Birlikte çalışırken

- Her seferinde tek küçük parça yazacağız.
- Önce ne beklediğini söyle; sonra çalıştır.
- Hata olursa son hücreyi ve hata metnini paylaş.
- `student.py` değişiklikleri her alıştırma hücresinde yeniden yüklenir.
- Kernel karışırsa **Restart Kernel → Run All**.
- **BEKLİYOR**, henüz yazmadığımız alıştırmadır; traceback değildir.

İlk konuşma sorusu: **`laps` tablosunda bir satır sürücüyü mü, turu mu temsil ediyor?**
Yanıtını, gördüğün DriverNumber ve LapNumber değerleriyle açıkla.

## Sık sorunlar

- `ModuleNotFoundError`: doğru .venv kernelini seç; gerekirse bootstrap çalıştır.
- `KeyError`: doğrudan `df.columns.tolist()` bak. Bu projedeki kontroller hangi kolonun eksik olduğunu söyler.
- İndirme yarıda kalırsa: fetch'i tekrar çalıştır; başarısız snapshot silinmez ve notebook tarafından seçilmez.
- GitHub girişi: yalnız repo yayınlama için gerekir. Yerel defterler için gerekmez.
- `pytest` geçse bile alıştırmalar tamamlanmış sayılmaz.
