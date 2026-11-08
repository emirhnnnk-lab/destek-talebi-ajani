# Destek Talebi Ajanı

> **EN summary:** A support-ticket agent running on a local LLM: it classifies incoming tickets, resolves routine ones through tool chains (invoice copy, password reset, outage check, technical ticket) and routes risky actions (refunds, cancellations) to human approval. Every tool call is audit-logged in SQLite. The README documents the debugging story: v1 looked fine on routing (14/16) but the exact tool chain was right in only 3/16 cases; v2 fixed it to 16/16. Full English version: [README.en.md](README.en.md).

**Canlı demo:** [huggingface.co/spaces/emrhnnnnnn/ai-uygulamalar-demo](https://huggingface.co/spaces/emrhnnnnnn/ai-uygulamalar-demo), sekme: 🎧 Destek Talebi Ajanı. Demo OpenAI gpt-5.4-mini ile çalışıyor; iş mantığı bu repodakiyle aynı.

Bir şirketin destek ekibine gelen taleplerin çoğu birbirinin aynısı: "faturamın kopyasını gönderin", "şifremi unuttum", "internetim yok". Bunları bir insanın tek tek açıp aynı işlemi yapması hem yorucu hem yavaş. Bu ajan talebi okuyor, ne olduğunu anlıyor, tekrar eden işleri araçlarla kendisi çözüyor. **Para ya da iptal içeren** işlemlerde ise durup insan onayı bekliyor. Böylece ekip sadece gerçekten gereken yerde devreye giriyor. Model kendi bilgisayarımda çalışıyor (yerel LLM), yani müşteri verisi dışarı çıkmıyor.

## Nasıl çalışıyor
```
Talep (e-posta / form / WhatsApp) → model talebi sınıflar → oyun kitabı doğru araçları sırayla çalıştırır
   → otomatik çözüldü | onay bekliyor (iade, iptal) | insana devredildi (tanınmayan)
   → model müşteriye cevabı yazar · her araç çağrısı denetim kaydına düşer
```
| Talep türü | Sırayla çalışan araçlar | Sonuç |
|---|---|---|
| Arıza | müşteriyi bul → bölgede kesinti var mı bak → (yoksa) teknik kayıt aç | Otomatik |
| Fatura kopyası | müşteriyi bul → faturayı gönder | Otomatik |
| Şifre | müşteriyi bul → sıfırlama linki gönder | Otomatik |
| Fatura itirazı / iade | müşteriyi bul → iadeyi başlat | **İnsan onayı** |
| İptal | müşteriyi bul → iptal talebi aç | **İnsan onayı** |
| Diğer | — | İnsana devret |

Panelde canlı sayaçlar var: kaç talep otomatik çözüldü, kaçı onay bekliyor, kaçı insana gitti ve otomasyon oranı. Onay bekleyenleri tek tuşla onaylayıp reddedebiliyorsunuz, her talepte hangi araçların çalıştığı görünüyor.

## Sonuçlar (16 etiketli talep)
| Sürüm | Talebi doğru sınıflama | Doğru yere yönlendirme |
|---|---|---|
| v1: model araçları kendisi seçiyor | 16/16 | 14/16 |
| **v2: model sadece sınıflıyor, araçları oyun kitabı seçiyor** | **16/16** | **16/16** |

Ama bu tablo hikâyenin yarısı. Asıl ders aşağıda.

## Neler patladı, nasıl düzelttim

**1. İlk sürüm iyi görünüyordu.** Modele araçları verip "talebi çöz" dedim; hangi aracı hangi sırayla çağıracağına kendisi karar veriyordu. Yönlendirme puanı 14/16 çıktı. İlk bakışta fena değil.

**2. Araç zincirine bakınca tablo değişti.** Rapora her talepte hangi araçların çalıştığını da yazdırdım ([v1 raporu](eval/RAPOR_v1_serbest_arac.md)). O güzel puan asıl sorunu saklıyormuş:
- **Yanlış araç:** "Faturam iki katı, iade edin" talebinde iade yerine **teknik arıza kaydı** açıldı. "Hattımı kapatın" talebinde de iptal yerine yine teknik kayıt açıldı. Sonuç doğru kutuya (onay bekliyor) düştüğü için puan bunu görmedi.
- **Hiç araç yok:** İki şifre talebinde model hiçbir araç çağırmadı, talep boşuna insana gitti.
- **Kimlik doğrulama atlandı:** Talimatta "önce müşteriyi bul" yazmasına rağmen 5 talepte müşteri hiç doğrulanmadan işlem yapıldı, 1 talepte de doğrulama sonradan yapıldı.
- **Eksik adım:** İki arıza talebinde kesinti yokken teknik kayıt açılmadı.

Beklenen araç zinciriyle birebir eşleşen talep sadece **3/16** idi.

**3. Kararı modelden aldım.** Model artık sadece talebi sınıflıyor, ki bunu zaten 16/16 yapıyordu. Hangi aracın hangi sırayla çalışacağını talep türüne göre sabit bir **oyun kitabı** belirliyor. Para ve iptal içeren işlemler her zaman insan onayına gidiyor. Tanınmayan durumlar için modelin serbest araç seçmesi sadece yedek olarak kaldı.

| | v1: model aracı seçiyor | v2: oyun kitabı |
|---|---|---|
| Doğru yönlendirme | 14/16 | **16/16** |
| Beklenen araç zinciri | 3/16 | **16/16** |
| Yanlış araçla işlem | 3 | **0** |
| Müşteri doğrulanmadan işlem | 5 | **0** |

**4. Sonradan fark ettiğim bir hata.** Demo cevaplarını okurken modelin isimden cinsiyet tahmin edip "Hanım/Bey" diye hitap ettiğini gördüm. Yanlış tahmin müşteriyi rahatsız eder. Cevap talimatına "unvan kullanma, isimden cinsiyet tahmin etme" kuralını ekledim.

**Ders:** Sadece sonuç kutusuna bakan bir ölçüm, yanlış yoldan doğru kutuya varan hataları gizliyor. Ajanlarda araç zincirini de ölçmek gerekiyor. Bir de modeli, kuralı yazılabilen kararlar için değil, kuralın yazılamadığı yerlerde (talebi anlamak, müşteriye cevap yazmak) kullanmak daha güvenli.

## Kalıcı kayıt ve SQL raporları
Talepler, her araç çağrısı ve onay kararları bir veritabanına (SQLite) yazılıyor: `app/db.py`, tablolar `talepler`, `arac_cagrilari`, `onaylar`. Sunucu yeniden başlasa da denetim izi kaybolmuyor. Raporlar düz SQL ile çıkıyor: `GET /rapor/<ad>`.

| Rapor | Cevapladığı soru |
|---|---|
| `kategori_bazinda_otomasyon` | Hangi talep türünde işlerin yüzde kaçı insansız çözülüyor? |
| `en_cok_kullanilan_araclar` | Ajan en çok hangi aracı, kaç farklı talepte çağırıyor? |
| `onay_sonuclari` | İnsan onayına düşen işler türüne göre kaç kez onaylandı ya da reddedildi? |
| `dogrulamasiz_islem` | **Güvenlik denetimi:** müşteri doğrulanmadan işlem yapılan talep var mı? |

Sonuncusunu, yukarıdaki v1 hatası (müşteriyi doğrulamadan işlem yapmak) bir daha sessizce geçmesin diye yazdım. Ajanın yaptığı her çağrıyı sonradan tek bir sorguyla denetleyebiliyorum. Testleri: `tests/test_db.py`.

## Çalıştırma
```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
uvicorn app.main:app --reload     # http://localhost:8000
python eval/degerlendir.py
pytest
```
API: `POST /webhook/talep {"metin": "..."}` · `POST /onay/{id}?karar=onayla|reddet` · `GET /talepler` · `GET /denetim` · `GET /rapor/<ad>`

## Teknoloji
Python · FastAPI · Ollama (qwen2.5:3b, araç çağırma + JSON çıktı) · SQLite · httpx · pytest

> Müşteri ve servis verileri uydurma (Örnek Telekom).

---
Geliştiren: **Emirhan Karaca**
