"""Destek talebi ajanı: sınıflandır → araçlarla çöz → riskliyse insana devret."""
import json, os, re
import httpx
from . import tools

OLLAMA = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("CHAT_MODEL", "qwen2.5:3b")
KATEGORILER = ["fatura_kopyasi", "sifre", "ariza", "fatura_itiraz", "iptal", "diger"]

SINIFLA = """Bir telekom şirketinin destek talebini sınıflandır. Sadece JSON döndür:
{"kategori": one of %s, "musteri_no": "M1234 biçiminde ya da null", "aciliyet": "normal" | "yuksek", "ozet": "tek cümle"}
Kategoriler: fatura_kopyasi=fatura/fatura kopyası istiyor; sifre=şifre/giriş sorunu; ariza=internet/hat/santral çalışmıyor;
fatura_itiraz=fazla/hatalı ücret, iade istiyor; iptal=aboneliği kapatmak istiyor; diger=hiçbiri.""" % KATEGORILER

COZ = """Sen Örnek Telekom'un destek ajanısın. Talebi araçları kullanarak çöz.
Kurallar: önce musteri_bul ile müşteriyi doğrula. Arızada önce servis_durumu'na bak; bölgede kesinti varsa kayıt açma, müşteriye bilgi ver.
Para iadesi ve iptal için ilgili aracı çağır ama müşteriye 'talebiniz uzman onayına iletildi' de; kesin söz verme.
Son olarak müşteriye gönderilecek kısa, nazik, Türkçe bir yanıt yaz."""


def _chat(messages, use_tools=False, fmt=None):
    # num_predict: küçük modelin sonsuz/uzun üretime kaçmasını engeller
    body = {"model": MODEL, "stream": False, "messages": messages, "options": {"temperature": 0, "num_predict": 300}}
    if use_tools:
        body["tools"] = tools.SEMA
    if fmt:
        body["format"] = fmt
    for deneme in range(2):
        try:
            r = httpx.post(f"{OLLAMA}/api/chat", json=body, timeout=240)
            r.raise_for_status()
            return r.json()["message"]
        except httpx.TimeoutException:
            if deneme == 1:
                raise


def siniflandir(metin: str):
    m = _chat([{"role": "system", "content": SINIFLA}, {"role": "user", "content": metin}], fmt="json")
    try:
        d = json.loads(m["content"])
    except json.JSONDecodeError:
        d = {}
    no = re.search(r"\bM\d{4}\b", metin)  # model kaçırırsa regex ile güvence
    d["musteri_no"] = d.get("musteri_no") or (no.group(0) if no else None)
    if d.get("kategori") not in KATEGORILER:
        d["kategori"] = "diger"
    d.setdefault("aciliyet", "normal")
    return d


def coz(metin: str, sinif: dict, max_adim: int = 6):
    msgs = [{"role": "system", "content": COZ},
            {"role": "user", "content": f"Talep: {metin}\nSınıflandırma: {json.dumps(sinif, ensure_ascii=False)}"}]
    cagrilar = []
    for _ in range(max_adim):
        m = _chat(msgs, use_tools=True)
        msgs.append(m)
        calls = m.get("tool_calls") or []
        if not calls:
            break
        for c in calls:
            ad, arg = c["function"]["name"], c["function"].get("arguments", {})
            if isinstance(arg, str):
                arg = json.loads(arg or "{}")
            f = tools.ARACLAR.get(ad)
            sonuc = f(**arg) if f else {"hata": "bilinmeyen araç"}
            cagrilar.append({"arac": ad, "girdi": arg, "sonuc": sonuc})
            msgs.append({"role": "tool", "content": json.dumps(sonuc, ensure_ascii=False)})
    yanit = (msgs[-1].get("content") or "").strip()
    return cagrilar, yanit


YAZ = """Sen Örnek Telekom'un destek ajanısın. Aşağıdaki araç sonuçlarına dayanarak müşteriye kısa, nazik, Türkçe bir yanıt yaz.
İade veya iptal 'onay_bekliyor' ise 'talebiniz uzman onayına iletildi' de; kesin söz verme. Bölgede kesinti varsa açıklama ve tahmini bitişi söyle."""


def _cagir(cagrilar, ad, **arg):
    sonuc = tools.ARACLAR[ad](**arg)
    cagrilar.append({"arac": ad, "girdi": arg, "sonuc": sonuc})
    return sonuc


def oyun_kitabi(metin: str, sinif: dict):
    """Bilinen kategorilerde hangi aracın çalışacağına iş kuralı karar verir (küçük modelin yanlış araç seçmesini önler).
    LLM yalnızca sınıflandırır ve müşteri yanıtını yazar. Bilinmeyen durumlarda serbest araç döngüsüne (coz) düşülür."""
    k, no = sinif["kategori"], sinif.get("musteri_no")
    if k == "diger" or not no:
        return None
    c = []
    m = _cagir(c, "musteri_bul", musteri_no=no)
    if "hata" in m:
        return c, "Müşteri numaranızı doğrulayamadık; sizi bir temsilciye aktarıyorum."
    if k == "ariza":
        s = _cagir(c, "servis_durumu", bolge=m["bolge"])
        if not s.get("kesinti"):
            _cagir(c, "teknik_ekip_kaydi", musteri_no=no, ozet=sinif.get("ozet") or metin[:80],
                   oncelik="yuksek" if sinif.get("aciliyet") == "yuksek" else "normal")
    elif k == "fatura_kopyasi":
        _cagir(c, "fatura_kopyasi_gonder", musteri_no=no)
    elif k == "sifre":
        _cagir(c, "sifre_sifirlama_linki", musteri_no=no)
    elif k == "fatura_itiraz":
        _cagir(c, "iade_baslat", musteri_no=no, tutar=m["son_fatura"], gerekce=sinif.get("ozet") or "fatura itirazı")
    elif k == "iptal":
        _cagir(c, "abonelik_iptal", musteri_no=no, gerekce=sinif.get("ozet") or "müşteri talebi")
    ozet = json.dumps([{"arac": x["arac"], "sonuc": x["sonuc"]} for x in c], ensure_ascii=False)
    yanit = _chat([{"role": "system", "content": YAZ},
                   {"role": "user", "content": f"Müşteri mesajı: {metin}\nAraç sonuçları: {ozet}"}]).get("content", "").strip()
    return c, yanit


def isle(talep_id: str, metin: str):
    sinif = siniflandir(metin)
    sonuc = oyun_kitabi(metin, sinif)
    cagrilar, yanit = sonuc if sonuc else coz(metin, sinif)
    riskli = [c for c in cagrilar if c["arac"] in tools.RISKLI]
    if riskli or sinif["kategori"] in ("iptal", "fatura_itiraz"):
        durum = "onay_bekliyor"
    elif sinif["kategori"] == "diger" or not cagrilar:
        durum = "insana_devredildi"
    else:
        durum = "otomatik_cozuldu"
    return {"id": talep_id, "metin": metin, "sinif": sinif, "araclar": cagrilar, "yanit": yanit, "durum": durum}
