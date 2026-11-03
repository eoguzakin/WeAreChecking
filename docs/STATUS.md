# Durum — 3 Kasım 2026

## Hazır

- Yerel Python 3.13 sanal ortamı ve repo içinde Jupyter kerneli.
- Windows/Python 3.13 bağımlılık kilidi; diğer desteklenen ortamlar için pyproject aralıkları.
- Gerçek 2024 Bahreyn verisi: FP1, FP2, FP3, Q, R. Her seans için katılımcı/tur/stint/hava.
- Q ve R sınıflandırması; kaynaklar arası numara/kısaltma kontrolü.
- 2024 Avusturya sprint takvimi API ile doğrulandı; tam sprint verisi bu kurulumda indirilmedi.
- 21 çevrimdışı altyapı testi geçti; pip check bağımlılık hatası bulmadı.
- 01 ve 02 defterleri baştan sona çalıştırıldı. Çalıştırılmış kopyalar ve HTML önizlemeler `reports/executed/` altında. Git'teki defterler çıktısızdır.
- İki HTML görünümü tarayıcıda kontrol edildi.
- GitHub için CI dosyası hazır; uzak depoda henüz çalışmadı.

## Birlikte tamamlayacağız

- [ ] Hedef 1: tabloyu yorumla, student.lap_counts yaz, kontrolü geçir.
- [ ] Hedef 2: student.qualifying_baseline yaz, tahmini kaydet, gerçek sonuçla karşılaştır.
- [ ] Decision note'u kendi sonuçlarınla doldur.

Defterlerin hatasız çalışması bu kutuların tamamlandığı anlamına gelmez. Henüz kullanıcı tahmini veya model başarı skoru üretilmedi.

## GitHub

Yerel Git deposu hazır. Hedef: eoguzakin/WeAreChecking, başlangıçta private.
Tarayıcıdaki GitHub oturumuna giriş bekleniyor; uzak depo henüz oluşturulmadı.
Giriş tamamlandıktan sonra mevcut commit gönderilecek; yeniden kurulum gerekmeyecek.
