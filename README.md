# Destek Talebi Otomasyon Ajanı

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
