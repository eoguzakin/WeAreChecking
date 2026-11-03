# WeAreChecking 🏁

Formula 1 hafta sonlarını adım adım tahmin etmeyi öğrenmek için Python projesi.

**Başlangıç:** [BASLA.md](BASLA.md) → [01 · Hafta sonu verisi](notebooks/01_weekend_data.ipynb) → [02 · İlk tahmin](notebooks/02_first_prediction.ipynb).

## Şu anki kapsam

- İzole Python ortamı, veri indirme komutu, önbellek ve sürümlü snapshot.
- OpenF1: seans katılımcıları, turlar, lastik stintleri, gözlenen hava.
- Jolpica: Q / Sprint / yarış sınıflandırması ve kalıcı sürücü kimlikleri.
- FastF1: yalnız takvim; zamanlama indirmesi kullanılmıyor.
- Model girdisi / gerçek sonuç ayrımı, UTC kesim zamanı, tahmin kaydı ve değerlendirme.
- İki açıklamalı defter, iki öğrenci alıştırması ve çevrimdışı altyapı testleri.

**Henüz tamamlanmadı:** öğrenci alıştırmaları, eğitilmiş ML modeli, tüm seanslar için tahmin, pist performans özellikleri, haber/sakatlık/ceza/yer değiştirme işleme, canlı güncelleme ve arayüz. Bunlar [yol haritasında](docs/ROADMAP.md).

İlk benchmark, Q sırasından yarış sırası üretir. Hızlı öğrenmek ve sonraki modelleri karşılaştırmak için başlangıçtır; projenin son hedefi değildir.

## Kurulum ve kontrol

Python 3.12–3.14; bu makinede 3.13 kullanılır. PowerShell, proje kökü:

```powershell
py -3.13 bootstrap.py
.\.venv\Scripts\python.exe -m wearechecking doctor
.\.venv\Scripts\python.exe -m pytest
```

VS Code'da **bu klasörü** aç. Notebook kernelini **WeAreChecking (.venv)** veya bu klasördeki `.venv\Scripts\python.exe` seç. Ortam aktivasyonu gerekmez.

```powershell
.\.venv\Scripts\python.exe -m wearechecking fetch --year 2024 --round 1
.\.venv\Scripts\python.exe -m wearechecking inspect --year 2024 --round 1
```

Varsayılan örnek: 2024 Bahreyn. Komut takvimdeki bütün seansları indirir. İlk indirme internet ister; notebook mevcut snapshot'ı okur. Yeniden indirme ayrı snapshot oluşturur. Ayrıntılı telemetri indirilmez.

## Öğrenme düzeni

Birlikte önce **tahmin et → küçük kod yaz → kontrolü çalıştır → sonucu açıkla** döngüsünü kullanacağız. `src/wearechecking/student.py` senin çalışma alanın. Fonksiyonlar başlangıçta `None` döndürür; defter bunu **BEKLİYOR** diye gösterir. Bu bir kurulum hatası değildir. Altyapı testlerinin geçmesi alıştırmaların tamamlandığı anlamına gelmez.

## Dürüst değerlendirme

Geçmiş veriler bugün indirilir. Sonradan yapılan sınıflandırma düzeltmeleri bulunabilir. Bu nedenle ilk çalışma açıkça **reconstructed** olarak etiketlidir. Gerçek bir tarihsel point-in-time backtest değildir.

Q katılımcıları ilk alıştırmada geçici yarış katılımcıları kabul edilir. Grid cezası, DNS veya sürücü değişimi henüz modellenmez; değerlendirmede katılımcı uyuşmazlığı varsa işlem durur. Tek yarışın hatası genel başarı kanıtı değildir. DNF olan sınıflandırılmış sürücünün resmi sırası korunur; DNS/DSQ için geliştirilecek ayrı durum modeli ertelenmiştir.

## Kaynaklar

Erişim koşulları 3 Kasım 2026'da kontrol edildi:

- [OpenF1 docs](https://openf1.org/docs/) — 2023 sonrası tarihsel veri, ücretsiz ve kimlik doğrulamasız.
- [Jolpica docs](https://github.com/jolpica/jolpica-f1/blob/main/docs/README.md) — sonuçlar, sürücü ve pist kayıtları.
- [FastF1 authentication](https://github.com/theOehrly/Fast-F1/blob/main/docs/api_reference/accounts_auth.rst) — zamanlama erişimi artık F1TV gerektirir; bu başlangıçta yalnız takvim kullanılır.

Kod ile kaynak verinin lisansları ayrıdır. İndirilen gerçek veri ve önbellek Git'e eklenmez. Kaynak şartları korunmalı; çalışma kişisel öğrenme/portföy içindir.
