# Veri sözleşmesi v1

- **Weekend:** yıl + resmi round; pist/location ve kaynak meeting_key.
- **Session:** kaynağın session_key'si, tür, UTC takvim ve olay bitiş sınırı.
- **Entry:** seansa ait DriverNumber + kaynak adı; Q/R/S için Jolpica DriverId. FP kimliğini yarış kadrosundan otomatik doldurma.
- **Lap:** bir sürücünün bir turu; eksik, tekrar veya pit-out kayıtlar olabilir. LapTime boşluğu sıfır değildir.
- **Weather:** ölçülmüş hava; yarış öncesi forecast değildir.
- **Snapshot:** schema_version, observed_at, kaynak URL'leri, raw JSON, normalize Parquet, SHA-256; indirme başarısızsa status=failed.
- **Forecast:** kaynak snapshot kimliği, target_session, cutoff_utc, mode, model sürümü, sıralama CSV özeti.
- **Label:** R/results; yalnız kaydedilmiş tahmin değerlendirilirken okunur.

## Zamanın anlamı

`cutoff_utc` tahmini yaptığımızı varsaydığımız zamandır.
`observed_at` veriyi bugün gerçekten indirdiğimiz zamandır.
`event_end_bound_utc` kaynak seans bitişi ve son ölçülen tur bitişinin büyüğüdür; veri yayın zamanı değildir.

İlk deneyde yalnız reconstructed modu desteklenir. Kesim Q bitişinden sonra, yarış başlangıcından önce olmalıdır. Sonradan düzeltilen Q sınıflandırması sızıntısını bu kaynaklarla tam ortadan kaldıramayız. Canlı/as-of doğruluğu iddiası yoktur.

## Snapshot kapsamı

`status=complete`, istenen seansların indiği anlamına gelir. `requested_sessions` kapsamı gösterir; yalnız Q indirdiysen tüm hafta sonu inmiş sayılmaz. 01 defteri bütün seansların varlığını ayrıca kontrol eder.

## Tahmin v0

İlk girdi allowlist'i: driver_id, driver, team, qualifying_position.
Q katılımcıları geçici R katılımcılarıdır. Katılımcı farkı veya eksik sınıflandırma varsa değerlendirme hata verir; otomatik olarak sonuncu yapmaz.
