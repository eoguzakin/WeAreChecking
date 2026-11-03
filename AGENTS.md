# WeAreChecking çalışma düzeni

Bu proje kullanıcı öğrenerek ilerlesin diye hazırlanmıştır.

- Altyapı, hata düzeltmeleri ve testleri özerkçe tamamla.
- Kullanıcı birlikte çözmek istediğinde student.py TODO'larını kendiliğinden doldurma.
- Her adımda kısa açıklama, küçük görev, kontrol, ardından yorum kullan.
- Kullanıcı açıkça çözüm isterse göster; gereksiz izin isteme.
- Notebooks 01 ve 02 için "tamam" demeden öğrenme kontrolü ve kullanıcı yorumunu kontrol et.
- Gerçek veri yokken sentetik veriyi gerçek F1 verisi gibi gösterme.
- Tahmin girdilerine hedef seans sonucu, statüsü, puanı veya gelecekte gözlenen hava ekleme.
- UTC kullan; observed_at ile olay zamanını ayrı tut.
- Geçmişten bugün indirilen veriyi reconstructed olarak etiketle.
- FP katılımcısını race entry ile karıştırma; driver_number kalıcı kimlik değildir.
- student.py dışında çalışan kodu yarım TODO'larla bırakma.
- Yeni bağımlılık eklerken pyproject ve kilit dosyasını tutarlı güncelle.
- Doğrulama: python -m pytest; python scripts/validate_notebooks.py.
- Büyük ham veri, .venv, token/şifre, önbellek veya mutlak kullanıcı yolu commit etme.
