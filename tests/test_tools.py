from app import tools, agent


def test_riskli_araclar_onaya_duser():
    assert tools.iade_baslat("M1002", 100, "fazla ücret")["onay_bekliyor"] is True
    assert tools.abonelik_iptal("M1004", "taşınma")["onay_bekliyor"] is True
    assert {"iade_baslat", "abonelik_iptal"} == tools.RISKLI


def test_kesinti_bilgisi_ve_denetim_kaydi():
    n = len(tools.LOG)
    assert tools.servis_durumu("Kadıköy")["kesinti"] is True
    assert tools.musteri_bul("M9999") == {"hata": "müşteri bulunamadı"}
    assert len(tools.LOG) == n + 2


def test_isle_yonlendirme_kurallari(monkeypatch):
    monkeypatch.setattr(agent, "oyun_kitabi", lambda m, s: None)
    monkeypatch.setattr(agent, "siniflandir", lambda m: {"kategori": "iptal", "musteri_no": "M1004", "aciliyet": "normal"})
    monkeypatch.setattr(agent, "coz", lambda m, s: ([{"arac": "abonelik_iptal", "girdi": {}, "sonuc": {}}], "Talebiniz iletildi."))
    assert agent.isle("X", "iptal")["durum"] == "onay_bekliyor"
    monkeypatch.setattr(agent, "siniflandir", lambda m: {"kategori": "sifre", "musteri_no": "M1005", "aciliyet": "normal"})
    monkeypatch.setattr(agent, "coz", lambda m, s: ([{"arac": "sifre_sifirlama_linki", "girdi": {}, "sonuc": {}}], "Link gönderildi."))
    assert agent.isle("Y", "şifre")["durum"] == "otomatik_cozuldu"
    monkeypatch.setattr(agent, "siniflandir", lambda m: {"kategori": "diger", "musteri_no": None, "aciliyet": "normal"})
    monkeypatch.setattr(agent, "coz", lambda m, s: ([], "Sizi bir temsilciye aktarıyorum."))
    assert agent.isle("Z", "adres")["durum"] == "insana_devredildi"


def test_oyun_kitabi_dogru_araci_secer(monkeypatch):
    monkeypatch.setattr(agent, "_chat", lambda *a, **k: {"content": "yanıt"})
    c, _ = agent.oyun_kitabi("iade", {"kategori": "fatura_itiraz", "musteri_no": "M1002", "ozet": "fazla ücret"})
    assert [x["arac"] for x in c] == ["musteri_bul", "iade_baslat"]
    c, _ = agent.oyun_kitabi("internet yok", {"kategori": "ariza", "musteri_no": "M1001", "aciliyet": "yuksek"})
    assert [x["arac"] for x in c] == ["musteri_bul", "servis_durumu"]  # Kadıköy'de kesinti var: kayıt açılmaz
    c, _ = agent.oyun_kitabi("internet yok", {"kategori": "ariza", "musteri_no": "M1002"})
    assert [x["arac"] for x in c][-1] == "teknik_ekip_kaydi"
