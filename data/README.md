# Veri

Gerçek veri `snapshots/` altında sürümlenir ve Git'e eklenmez.

- OpenF1: katılımcı, tur, stint, ölçülen hava; kaynak JSON ve normalize Parquet.
- Jolpica: Q/Sprint/R sınıflandırması ve kalıcı sürücü kimliği.
- FastF1: hafta sonu takvimi; F1TV zamanlama API'si kullanılmaz.

Her snapshot kaynak URL'leri, UTC kayıt zamanları, veri kapsamı ve SHA-256 özetlerini içerir. Eski snapshot değişmez; yeni fetch ayrı klasör üretir. Hata alan indirme `failed` kalır. HTTP/takvim önbelleği proje kökündeki `.cache/` altındadır. Önbellekten gelen veri de tarihsel yeniden kurma olarak etiketlenir; yayın anı kanıtı değildir.
