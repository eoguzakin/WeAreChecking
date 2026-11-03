# Adımlar ve bitiş ölçütleri

## Şimdi: ilk iki hedef

1. **Gerçek hafta sonu:** seans takvimi, tur/stint/hava/katılımcı tabloları, kaynak ve kalite kontrolleri. Öğrenci görevi: sürücü başına benzersiz tur sayısını çıkarma.
2. **İlk tahmin:** Q sırasını yarış sırası için benchmark olarak kullanma, tahmini sonuçtan önce dosyaya yazma, MAE ve sıra korelasyonu, decision note.

Her iki hedefin altyapısı hazırlanır; öğrenme görevleri interaktif yapılır.

## Sonraki gelişim

3. **Çok yarışlı deney:** geçmiş sezonları kronolojik train/validation/test ayırma; son test yarışlarına bakmadan model seçimi. Q benchmark, takım/sürücü geçmişi benchmark, belirsizlik.
4. **İlk eğitilen model:** yarış/driver satırları, geçmişten rolling özellikler, takım ve pist etkisi. Önce açıklanabilir model; sonra ranking modeli. Hedef seans özellikleri yasak.
5. **Pist ve tempo:** pist uzunluğu/tip/viraj profili; FP long-run tempo, lastik yaşı, pist gelişimi, trafik ve kırmızı/sarı bayrak temizleme. Yakıt bilinmiyorsa kesin yakıt düzeltmesi iddia etme.
6. **Seanslara ayrılma:** FP tur zamanı sırası ile yarış sırasını ayrı hedefle; Q, SQ, Sprint, GP için ayrı değerlendirme. Sprint formatını takvimden belirle; seans sayısı/sırasını sabitleme.
7. **Haber ve entry sistemi:** FIA/ekip duyuruları kaynaklı olay defteri. Yaralanma iddiasından tıbbi çıkarım yapma; yalnız doğrulanmış yarışa katılım etkisi. Ceza/DSQ/DNS/substitution, yayın zamanı, geçerlilik zamanı, kaynak, revizyon. Rookie FP katılımı yarış katılımı değildir.
8. **Art arda güncelleme:** seans sonunda yeni snapshot → yalnız kalan seans tahminleri → eski tahmini koru → değişimin kaynağını açıkla. Ertelenen/iptal seans ve yeni sürücü için senaryo.
9. **Gerçek replay:** o anda kaydedilmiş verinin available_at/observed_at zamanları; haberin ilk yayın sürümü ve hava tahmininin issued_at zamanı. Tarihsel düzeltilmiş veriden ayrı rapor.
10. **Sunum:** kalibre edilmiş sıra dağılımı, podyum/ilk 10/yarışı bitirme olasılığı, veri tazeliği, model kartı ve demo.

## Başarı standardı

Tek yarış tahmini yeterli kanıt değildir. Çok sayıda ilerleyen zaman penceresinde güçlü basit benchmark'ı geçme, hata çubukları, rejim değişimi ve yeni sürücü denemeleri gerekir. DNF/DNS/DSQ ayrı hedef/durum olmalı. Yakalanamayan haber varsa "işlendi" denmez.

## Mimarinin bugünkü sınırı

Mevcut kod yalnız ilk iki hedefin öğrenme altyapısıdır. Haber botu, canlı scheduler, sürekli öğrenme, ücretli veri hesabı veya sunucu kurulmuş değildir.
