"""Ajanın kullanabildiği araçlar. Riskli aksiyonlar doğrudan çalışmaz, insan onayı kuyruğuna düşer."""
import json, os, datetime

D = os.path.join(os.path.dirname(__file__), "..", "data")
MUSTERI = json.load(open(os.path.join(D, "musteriler.json"), encoding="utf-8"))
SERVIS = json.load(open(os.path.join(D, "servis_durumu.json"), encoding="utf-8"))
RISKLI = {"iade_baslat", "abonelik_iptal"}
LOG = []  # her araç çağrısı denetim kaydına yazılır


def _log(name, args, result):
    LOG.append({"zaman": datetime.datetime.now().isoformat(timespec="seconds"), "arac": name, "girdi": args, "sonuc": result})
    return result


def musteri_bul(musteri_no: str):
    return _log("musteri_bul", {"musteri_no": musteri_no}, MUSTERI.get(musteri_no, {"hata": "müşteri bulunamadı"}))


def servis_durumu(bolge: str):
    return _log("servis_durumu", {"bolge": bolge}, SERVIS.get(bolge, {"kesinti": False}))


def fatura_kopyasi_gonder(musteri_no: str):
    m = MUSTERI.get(musteri_no)
    if not m:
        return _log("fatura_kopyasi_gonder", {"musteri_no": musteri_no}, {"hata": "müşteri yok"})
    return _log("fatura_kopyasi_gonder", {"musteri_no": musteri_no}, {"gonderildi": True, "tutar": m["son_fatura"]})


def sifre_sifirlama_linki(musteri_no: str):
    return _log("sifre_sifirlama_linki", {"musteri_no": musteri_no}, {"gonderildi": musteri_no in MUSTERI})


def teknik_ekip_kaydi(musteri_no: str, ozet: str, oncelik: str = "normal"):
    return _log("teknik_ekip_kaydi", {"musteri_no": musteri_no, "ozet": ozet, "oncelik": oncelik},
                {"kayit_no": f"TK-{len(LOG) + 1000}"})


def iade_baslat(musteri_no: str, tutar: float, gerekce: str):
    return _log("iade_baslat", {"musteri_no": musteri_no, "tutar": tutar, "gerekce": gerekce}, {"onay_bekliyor": True})


def abonelik_iptal(musteri_no: str, gerekce: str):
    return _log("abonelik_iptal", {"musteri_no": musteri_no, "gerekce": gerekce}, {"onay_bekliyor": True})


ARACLAR = {f.__name__: f for f in [musteri_bul, servis_durumu, fatura_kopyasi_gonder, sifre_sifirlama_linki,
                                    teknik_ekip_kaydi, iade_baslat, abonelik_iptal]}

SEMA = [
 {"type": "function", "function": {"name": "musteri_bul", "description": "Müşteri no ile paket, bölge, fatura bilgisi getirir",
   "parameters": {"type": "object", "properties": {"musteri_no": {"type": "string"}}, "required": ["musteri_no"]}}},
 {"type": "function", "function": {"name": "servis_durumu", "description": "Bölgede bilinen kesinti var mı",
   "parameters": {"type": "object", "properties": {"bolge": {"type": "string"}}, "required": ["bolge"]}}},
 {"type": "function", "function": {"name": "fatura_kopyasi_gonder", "description": "Son faturanın kopyasını e-postayla gönderir",
   "parameters": {"type": "object", "properties": {"musteri_no": {"type": "string"}}, "required": ["musteri_no"]}}},
 {"type": "function", "function": {"name": "sifre_sifirlama_linki", "description": "Online işlemler şifre sıfırlama linki gönderir",
   "parameters": {"type": "object", "properties": {"musteri_no": {"type": "string"}}, "required": ["musteri_no"]}}},
 {"type": "function", "function": {"name": "teknik_ekip_kaydi", "description": "Arıza için teknik ekip kaydı açar",
   "parameters": {"type": "object", "properties": {"musteri_no": {"type": "string"}, "ozet": {"type": "string"},
   "oncelik": {"type": "string", "enum": ["normal", "yuksek"]}}, "required": ["musteri_no", "ozet"]}}},
 {"type": "function", "function": {"name": "iade_baslat", "description": "Para iadesi başlatır (İNSAN ONAYI GEREKİR)",
   "parameters": {"type": "object", "properties": {"musteri_no": {"type": "string"}, "tutar": {"type": "number"}, "gerekce": {"type": "string"}},
   "required": ["musteri_no", "tutar", "gerekce"]}}},
 {"type": "function", "function": {"name": "abonelik_iptal", "description": "Abonelik iptali talebi (İNSAN ONAYI GEREKİR)",
   "parameters": {"type": "object", "properties": {"musteri_no": {"type": "string"}, "gerekce": {"type": "string"}}, "required": ["musteri_no", "gerekce"]}}},
]
