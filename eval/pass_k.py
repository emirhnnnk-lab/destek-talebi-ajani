"""Tekrarlanabilirlik: her talep k kez çalıştırılır.
pass@1 = tek denemede ortalama başarı; pass^k = k denemenin HEPSİNDE başarılı olan talep oranı (τ-bench).
Başarı = doğru kategori VE doğru yönlendirme (oyun kitabı kategoriye göre araç zincirini belirler).
Kullanım: DESTEK_TEMP=0.7 python eval/pass_k.py 5
"""
import json, math, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import agent

K = int(sys.argv[1]) if len(sys.argv) > 1 else 5
D = os.path.dirname(__file__)
veri = json.load(open(os.path.join(D, "talepler.json"), encoding="utf-8"))
sonuc = []  # her talep için k adet 0/1
t0 = time.time()
for i, v in enumerate(veri):
    s = []
    for j in range(K):
        r = agent.isle(f"P{i}-{j}", v["metin"])
        s.append(int(r["sinif"]["kategori"] == v["kategori"] and r["durum"] == v["durum"]))
    sonuc.append(s)
    print(f"[talep] {i+1}/{len(veri)} basari={sum(s)}/{K}", flush=True)

n = len(veri)
p1 = sum(sum(s) for s in sonuc) / (n * K)
pk = sum(all(s) for s in sonuc) / n


def wilson(x, n, z=1.96):
    if n == 0:
        return (0, 0)
    p = x / n
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    return round(max(0, c - m), 3), round(min(1, c + m), 3)


ozet = {"model": agent.MODEL, "sicaklik": float(os.getenv("DESTEK_TEMP", "0")), "k": K, "talep": n,
        "pass@1": round(p1, 3), "pass^k": round(pk, 3),
        "pass^k_guven_araligi_95": wilson(sum(all(s) for s in sonuc), n),
        "talep_bazinda": sonuc, "sure_sn": round(time.time() - t0)}
json.dump(ozet, open(os.path.join(D, f"pass_k_sonuc_t{ozet['sicaklik']}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in ozet.items() if k != "talep_bazinda"}, ensure_ascii=False))
