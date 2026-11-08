"""Kalıcı kayıt: talepler, araç çağrıları (denetim) ve onay kararları SQLite'ta.
Sunucu yeniden başlasa da denetim izi kaybolmaz; raporlar düz SQL ile çıkar."""
import json
import os
import sqlite3
import datetime

YOL = os.environ.get("DESTEK_DB", os.path.join(os.path.dirname(__file__), "..", "data", "destek.db"))

SEMA = """
CREATE TABLE IF NOT EXISTS talepler (
  id TEXT PRIMARY KEY, zaman TEXT NOT NULL, kanal TEXT, metin TEXT NOT NULL,
  kategori TEXT, durum TEXT NOT NULL, yanit TEXT
);
CREATE TABLE IF NOT EXISTS arac_cagrilari (
  id INTEGER PRIMARY KEY AUTOINCREMENT, talep_id TEXT, zaman TEXT NOT NULL,
  arac TEXT NOT NULL, girdi TEXT, sonuc TEXT,
  FOREIGN KEY (talep_id) REFERENCES talepler(id)
);
CREATE TABLE IF NOT EXISTS onaylar (
  id INTEGER PRIMARY KEY AUTOINCREMENT, talep_id TEXT NOT NULL, zaman TEXT NOT NULL,
  karar TEXT NOT NULL CHECK (karar IN ('onaylandi', 'reddedildi')),
  FOREIGN KEY (talep_id) REFERENCES talepler(id)
);
CREATE INDEX IF NOT EXISTS ix_cagri_talep ON arac_cagrilari(talep_id);
"""


def baglan(yol: str | None = None) -> sqlite3.Connection:
    c = sqlite3.connect(yol or YOL, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.executescript(SEMA)
    return c


def _simdi():
    return datetime.datetime.now().isoformat(timespec="seconds")


def talep_kaydet(c, t: dict, metin: str, kanal: str):
    c.execute("INSERT OR REPLACE INTO talepler (id, zaman, kanal, metin, kategori, durum, yanit) VALUES (?,?,?,?,?,?,?)",
              (t["id"], _simdi(), kanal, metin, (t.get("sinif") or {}).get("kategori"), t["durum"], t.get("yanit")))
    for k in t.get("araclar", []):
        c.execute("INSERT INTO arac_cagrilari (talep_id, zaman, arac, girdi, sonuc) VALUES (?,?,?,?,?)",
                  (t["id"], k.get("zaman", _simdi()), k["arac"], json.dumps(k.get("girdi"), ensure_ascii=False),
                   json.dumps(k.get("sonuc"), ensure_ascii=False)))
    c.commit()


def onay_kaydet(c, talep_id: str, karar: str):
    c.execute("INSERT INTO onaylar (talep_id, zaman, karar) VALUES (?,?,?)", (talep_id, _simdi(), karar))
    c.execute("UPDATE talepler SET durum = ? WHERE id = ?", (karar, talep_id))
    c.commit()


# Panelin ve yöneticinin sorduğu sorular — her biri tek SQL sorgusu.
RAPORLAR = {
    "kategori_bazinda_otomasyon": """
        SELECT kategori,
               COUNT(*) AS talep,
               SUM(durum = 'otomatik_cozuldu') AS otomatik,
               ROUND(100.0 * SUM(durum = 'otomatik_cozuldu') / COUNT(*), 1) AS otomasyon_yuzde
        FROM talepler GROUP BY kategori ORDER BY talep DESC""",
    "en_cok_kullanilan_araclar": """
        SELECT arac, COUNT(*) AS cagri, COUNT(DISTINCT talep_id) AS talep
        FROM arac_cagrilari GROUP BY arac ORDER BY cagri DESC""",
    "onay_sonuclari": """
        SELECT t.kategori, o.karar, COUNT(*) AS adet
        FROM onaylar o JOIN talepler t ON t.id = o.talep_id
        GROUP BY t.kategori, o.karar""",
    "dogrulamasiz_islem": """
        -- güvenlik denetimi: müşteri doğrulanmadan işlem aracı çağrılan talepler (v1'deki hata tipi)
        SELECT DISTINCT a.talep_id, a.arac
        FROM arac_cagrilari a
        WHERE a.arac <> 'musteri_bul' AND a.arac <> 'servis_durumu'
          AND NOT EXISTS (SELECT 1 FROM arac_cagrilari m
                          WHERE m.talep_id = a.talep_id AND m.arac = 'musteri_bul' AND m.id < a.id)""",
}


def rapor(c, ad: str):
    return [dict(r) for r in c.execute(RAPORLAR[ad])]
