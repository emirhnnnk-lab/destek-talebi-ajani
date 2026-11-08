# Destek Talebi Otomasyon Ajanı

**🔴 Canlı demo:** [huggingface.co/spaces/emrhnnnnnn/ai-uygulamalar-demo](https://huggingface.co/spaces/emrhnnnnnn/ai-uygulamalar-demo) — sekme: 🎧 Destek Talebi Ajanı (demo OpenAI gpt-5.4-mini ile çalışır; iş mantığı bu repodakiyle aynı)

Müşteri destek taleplerini **lokal LLM** ile sınıflandıran, araçlarla çözen ve riskli işlemleri **insan onayına** bırakan ajan. Tekrar eden destek işini (fatura kopyası, şifre sıfırlama, arıza kaydı) otomatiğe bağlar, ekibi sadece gerçekten gereken yerde devreye sokar.

## Nasıl çalışır
```
Webhook (e-posta / form / WhatsApp) → sınıflandır (LLM, JSON) → oyun kitabı: doğru araç zinciri
   → otomatik çözüldü | onay bekliyor (iade, iptal) | insana devredildi (bilinmeyen)
   → LLM müşteri yanıtını yazar · her araç çağrısı denetim kaydına düşer
```
| Kategori | Araç zinciri | Sonuç |
|---|---|---|
| Arıza | müşteri → bölge kesinti kontrolü → (kesinti yoksa) teknik kayıt | Otomatik |
| Fatura kopyası | müşteri → fatura gönder | Otomatik |
| Şifre | müşteri → sıfırlama linki | Otomatik |
| Fatura itirazı / iade | müşteri → iade başlat | **İnsan onayı** |
| İptal | müşteri → iptal talebi | **İnsan onayı** |
| Diğer | — | İnsana devret |

Panelde canlı sayaçlar (otomatik / onay bekleyen / devredilen, otomasyon oranı), onayla/reddet butonları ve araç zinciri görünür.

## Sonuçlar (16 etiketli talep)
| Sürüm | Sınıflandırma | Doğru yönlendirme |
|---|---|---|
| v1: LLM araçları serbest seçiyor | 16/16 | 14/16 |
| **v2: LLM sınıflar, oyun kitabı aracı seçer** | **16/16** | **16/16** |

v1'de 3B model bazen yanlış aracı seçiyordu (iade talebinde teknik kayıt açmak gibi): [rapor](eval/RAPOR_v1_serbest_arac.md). v2'de karar mantığı deterministik, LLM sınıflandırma ve doğal dil yanıtında kullanılıyor. Bilinmeyen durumlar serbest araç döngüsüne düşüyor. Ayrıntı: [eval/RAPOR.md](eval/RAPOR.md)

## Hata → düzeltme süreci

**1. Ne bozuktu?** İlk sürümde LLM'e araçları verip "talebi çöz" dedim; hangi aracı ne sırayla çağıracağına kendisi karar veriyordu. Yönlendirme puanı 14/16 çıktı, ilk bakışta fena değildi.

**2. Nasıl fark ettim?** Rapora araç zincirini de yazdırınca ([v1 raporu](eval/RAPOR_v1_serbest_arac.md)) tablo değişti. Yönlendirme puanı asıl sorunu saklıyordu:
- **Yanlış araç:** "Faturam iki katı, iade edin" talebinde iade yerine **teknik arıza kaydı** açıldı. "Hattımı kapatın" talebinde de iptal yerine yine teknik kayıt açıldı. Sonuç doğru kutuya (onay bekliyor) düştüğü için puan bunu görmedi.
- **Hiç araç yok:** İki şifre talebinde model hiçbir araç çağırmadı, talep boşuna insana gitti.
- **Kimlik doğrulama atlandı:** "Önce müşteriyi bul" kuralı talimatta yazmasına rağmen 16 talebin 9'unda müşteri doğrulanmadan işlem yapıldı.
- **Eksik adım:** İki arıza talebinde kesinti yokken teknik kayıt açılmadı.

Beklenen zincirle birebir eşleşen talep sadece **3/16** idi.

**3. Ne değiştirdim?** Karar vermeyi LLM'den aldım. LLM artık sadece talebi sınıflandırıyor (bunu zaten 16/16 yapıyordu). Hangi aracın hangi sırayla çağrılacağını kategoriye göre sabit bir **oyun kitabı** belirliyor. Para ve iptal içeren işlemler her zaman insan onayına gidiyor. Tanınmayan durumlar için serbest araç döngüsü sadece yedek olarak kaldı.

**4. Sonuç**

| | v1: LLM aracı seçiyor | v2: oyun kitabı |
|---|---|---|
| Doğru yönlendirme | 14/16 | **16/16** |
| Beklenen araç zinciri | 3/16 | **16/16** |
| Yanlış araçla işlem | 3 | **0** |
| Müşteri doğrulanmadan işlem | 9 | **0** |

**Sonradan bulunan hata:** Demo cevaplarını okurken modelin isimden cinsiyet tahmin edip "Hanım/Bey" diye hitap ettiğini gördüm. Yanlış tahmin müşteriyi rahatsız eder. Yanıt talimatına "unvan kullanma, isimden cinsiyet tahmin etme" kuralını ekledim.

**Ders:** Sadece sonuç kutusuna bakan bir metrik, yanlış yoldan doğru kutuya varan hataları gizliyor. Ajanlarda araç zincirini de ölçmek gerekiyor. Ve LLM'i, kural yazılabilecek kararlar için değil, kuralın yazılamadığı yerlerde (sınıflandırma, doğal dil yanıtı) kullanmak daha güvenli.

## Çalıştırma
```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
uvicorn app.main:app --reload     # http://localhost:8000
python eval/degerlendir.py
pytest
```
API: `POST /webhook/talep {"metin": "..."}` · `POST /onay/{id}?karar=onayla|reddet` · `GET /talepler` · `GET /denetim`

## Teknoloji
Python · FastAPI · Ollama (qwen2.5:3b, tool-calling + JSON çıktı) · httpx · pytest

> Müşteri ve servis verileri uydurmadır (Örnek Telekom).

---
Geliştiren: **Emirhan Karaca**
