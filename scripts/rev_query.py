"""ผู้ตรวจ: query ก้อน MSG_055/056/057 — อ่านอย่างเดียว"""
import sys, json, os, re, glob

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

W = "translations/worklist"
D = "translations/done"


def load(batch):
    wl = json.load(open(f"{W}/batch_{batch}.json", encoding="utf-8"))
    dn = json.load(open(f"{D}/batch_{batch}.done.json", encoding="utf-8"))
    ctx = json.load(open(f"{W}/batch_{batch}.context.json", encoding="utf-8"))
    return wl, dn, ctx


def rows(batch):
    wl, dn, ctx = load(batch)
    ja = wl.get("ref_ja", {})
    tm = wl.get("ref_tm", {})
    lines = ctx.get("lines", ctx)
    out = []
    for i, en in enumerate(wl["strings"]):
        c = lines.get(en, {}) if isinstance(lines, dict) else {}
        out.append(
            dict(i=i, batch=batch, en=en, th=dn["strings"].get(en, ""),
                 ja=ja.get(en, ""), tm=tm.get(en, ""), ctx=c)
        )
    return out


def dump(r, ctxfields=("speakers", "gender", "neutral", "voice", "file", "key")):
    print(f"[{r['batch']}#{r['i']:03d}]")
    print("  EN:", r["en"].replace("\n", "\\n"))
    print("  JA:", (r["ja"] or "").replace("\n", "\\n"))
    print("  TH:", (r["th"] or "").replace("\n", "\\n"))
    if r["tm"]:
        print("  TM:", str(r["tm"]).replace("\n", "\\n")[:200])
    c = r["ctx"] or {}
    bits = {k: c.get(k) for k in ctxfields if c.get(k) is not None}
    if bits:
        print("  CTX:", json.dumps(bits, ensure_ascii=False)[:400])
