import os, uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from . import agent, tools

app = FastAPI(title="Destek Talebi Otomasyon Ajanı")
KUYRUK: dict = {}


class Talep(BaseModel):
    metin: str
    kanal: str = "e-posta"


@app.post("/webhook/talep")
def yeni_talep(t: Talep):
    tid = "T-" + uuid.uuid4().hex[:6].upper()
    KUYRUK[tid] = {**agent.isle(tid, t.metin), "kanal": t.kanal}
    return KUYRUK[tid]


@app.post("/onay/{tid}")
def onayla(tid: str, karar: str = "onayla"):
    if tid not in KUYRUK or KUYRUK[tid]["durum"] != "onay_bekliyor":
        raise HTTPException(404, "onay bekleyen talep yok")
    KUYRUK[tid]["durum"] = "onaylandi" if karar == "onayla" else "reddedildi"
    return KUYRUK[tid]


@app.get("/talepler")
def talepler():
    v = list(KUYRUK.values())
    sayac = {d: sum(1 for x in v if x["durum"] == d) for d in
             ["otomatik_cozuldu", "onay_bekliyor", "insana_devredildi", "onaylandi", "reddedildi"]}
    return {"ozet": sayac, "talepler": v[::-1]}


@app.get("/denetim")
def denetim():
    return tools.LOG[-200:]


@app.get("/", response_class=HTMLResponse)
def panel():
    return open(os.path.join(os.path.dirname(__file__), "panel.html"), encoding="utf-8").read()
