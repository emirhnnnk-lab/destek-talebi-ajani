"""Ajan değerlendirmesi: sınıflandırma doğruluğu ve doğru yönlendirme (otomatik / onay / insan)."""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import agent

veri = json.load(open(os.path.join(os.path.dirname(__file__), "talepler.json"), encoding="utf-8"))
rows, kat, yon, t0 = [], 0, 0, time.time()
for i, v in enumerate(veri):
    r = agent.isle(f"E{i}", v["metin"])
    k = r["sinif"]["kategori"] == v["kategori"]
    y = r["durum"] == v["durum"]
    kat += k
    yon += y
    zincir = " → ".join(a["arac"] for a in r["araclar"]) or "-"
    rows.append(f"| {v['metin'][:60]} | {v['kategori']} → {r['sinif']['kategori']} {'✅' if k else '❌'} | {v['durum']} → {r['durum']} {'✅' if y else '❌'} | {zincir} |")
n = len(veri)
rep = ["# Değerlendirme raporu", "", f"- Talep sayısı: **{n}**", f"- Sınıflandırma doğruluğu: **{kat}/{n}**",
       f"- Doğru yönlendirme (otomatik / onay / insan): **{yon}/{n}**",
       f"- Model: `{agent.MODEL}` (lokal, Ollama) · Süre: {time.time()-t0:.0f} sn", "",
       "| Talep | Kategori (beklenen → ajan) | Yönlendirme | Araç zinciri |", "|---|---|---|---|"] + rows
open(os.path.join(os.path.dirname(__file__), "RAPOR.md"), "w", encoding="utf-8").write("\n".join(rep) + "\n")
print(f"kategori {kat}/{n}  yonlendirme {yon}/{n}")
