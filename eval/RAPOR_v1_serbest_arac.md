# Değerlendirme raporu

- Talep sayısı: **16**
- Sınıflandırma doğruluğu: **16/16**
- Doğru yönlendirme (otomatik / onay / insan): **14/16**
- Model: `qwen2.5:3b` (lokal, Ollama) · Süre: 105 sn

| Talep | Kategori (beklenen → ajan) | Yönlendirme | Araç zinciri |
|---|---|---|---|
| M1001 internetim sabahtan beri çalışmıyor, acil bakar mısını | ariza → ariza ✅ | otomatik_cozuldu → otomatik_cozuldu ✅ | servis_durumu → musteri_bul |
| Merhaba, M1002 numaralı hattımda internet çok yavaş ve kopuy | ariza → ariza ✅ | otomatik_cozuldu → otomatik_cozuldu ✅ | musteri_bul → servis_durumu |
| IP santralimiz arama almıyor, müşteri no M1003. Ofis çalışam | ariza → ariza ✅ | otomatik_cozuldu → otomatik_cozuldu ✅ | musteri_bul → servis_durumu |
| Son faturamın kopyasını mail atabilir misiniz? M1003 | fatura_kopyasi → fatura_kopyasi ✅ | otomatik_cozuldu → otomatik_cozuldu ✅ | fatura_kopyasi_gonder |
| Muhasebe için ekim faturası lazım. Abone no: M1005 | fatura_kopyasi → fatura_kopyasi ✅ | otomatik_cozuldu → otomatik_cozuldu ✅ | fatura_kopyasi_gonder |
| Fatura kopyası rica ediyorum, M1001 | fatura_kopyasi → fatura_kopyasi ✅ | otomatik_cozuldu → otomatik_cozuldu ✅ | fatura_kopyasi_gonder |
| Şifremi unuttum, giriş yapamıyorum. M1005 | sifre → sifre ✅ | otomatik_cozuldu → insana_devredildi ❌ | - |
| Online işlemler hesabıma giremiyorum, şifre hatalı diyor. M1 | sifre → sifre ✅ | otomatik_cozuldu → insana_devredildi ❌ | - |
| Bu ay faturam normalin iki katı, fazlasını iade edin. M1002 | fatura_itiraz → fatura_itiraz ✅ | onay_bekliyor → onay_bekliyor ✅ | teknik_ekip_kaydi → musteri_bul |
| SMS paketimden kullanmadığım ücret kesilmiş, geri istiyorum. | fatura_itiraz → fatura_itiraz ✅ | onay_bekliyor → onay_bekliyor ✅ | teknik_ekip_kaydi |
| Yanlış tarife uygulanmış, iadeyi ne zaman yaparsınız? M1001 | fatura_itiraz → fatura_itiraz ✅ | onay_bekliyor → onay_bekliyor ✅ | - |
| Taşınıyorum, M1004 aboneliğimi iptal etmek istiyorum. | iptal → iptal ✅ | onay_bekliyor → onay_bekliyor ✅ | abonelik_iptal |
| Hizmetten memnun değilim, M1002 hattımı kapatın. | iptal → iptal ✅ | onay_bekliyor → onay_bekliyor ✅ | teknik_ekip_kaydi |
| Ofisiniz nerede, ziyarete gelmek istiyorum. | diger → diger ✅ | insana_devredildi → insana_devredildi ✅ | musteri_bul |
| Şirketinizde iş ilanı var mı? | diger → diger ✅ | insana_devredildi → insana_devredildi ✅ | - |
| Kampanyalarınız hakkında bilgi alabilir miyim? | diger → diger ✅ | insana_devredildi → insana_devredildi ✅ | - |
