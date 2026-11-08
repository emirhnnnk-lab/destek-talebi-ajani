from app import db


def talep(tid, kategori, durum, araclar):
    return {"id": tid, "sinif": {"kategori": kategori}, "durum": durum, "yanit": "ok",
            "araclar": [{"arac": a, "girdi": {}, "sonuc": {}} for a in araclar]}


def kur():
    c = db.baglan(":memory:")
    db.talep_kaydet(c, talep("T1", "sifre", "otomatik_cozuldu", ["musteri_bul", "sifre_sifirlama_linki"]), "şifre", "e-posta")
    db.talep_kaydet(c, talep("T2", "sifre", "insana_devredildi", []), "şifre?", "form")
    db.talep_kaydet(c, talep("T3", "iptal", "onay_bekliyor", ["musteri_bul", "abonelik_iptal"]), "iptal", "e-posta")
    db.talep_kaydet(c, talep("T4", "fatura_kopyasi", "otomatik_cozuldu", ["fatura_kopyasi_gonder"]), "fatura", "e-posta")
    db.onay_kaydet(c, "T3", "reddedildi")
    return c


def test_kategori_otomasyon_orani():
    r = {x["kategori"]: x for x in db.rapor(kur(), "kategori_bazinda_otomasyon")}
    assert r["sifre"]["talep"] == 2 and r["sifre"]["otomasyon_yuzde"] == 50.0
    assert r["iptal"]["otomatik"] == 0


def test_onay_durumu_guncellenir():
    c = kur()
    assert c.execute("SELECT durum FROM talepler WHERE id='T3'").fetchone()[0] == "reddedildi"
    assert db.rapor(c, "onay_sonuclari") == [{"kategori": "iptal", "karar": "reddedildi", "adet": 1}]


def test_dogrulamasiz_islem_yakalanir():
    # T4: müşteri doğrulanmadan fatura gönderilmiş → denetim sorgusu bulmalı
    assert db.rapor(kur(), "dogrulamasiz_islem") == [{"talep_id": "T4", "arac": "fatura_kopyasi_gonder"}]
