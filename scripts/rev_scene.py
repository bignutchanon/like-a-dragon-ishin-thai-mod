"""ผู้ตรวจ: หาไฟล์ฉากของสตริง EN แล้ว dump ทั้งฉากพร้อม label/ja/เครื่องหมายเพศ"""
import sys, json, os, glob

sys.path.insert(0, "scripts")
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
import merge_qc as M

TE = "extracted/text_en"
TJ = "extracted/text_ja"

_index = None


def index():
    global _index
    if _index is None:
        _index = {}
        for p in glob.glob(TE + "/*.json"):
            for r in json.load(open(p, encoding="utf-8")):
                _index.setdefault(r["en"], []).append((r["file"], r["line"]))
    return _index


def ja_of(fid):
    p = f"{TJ}/{fid}.json"
    if not os.path.exists(p):
        return {}
    return {r["line"]: r.get("ja") or r.get("en") for r in json.load(open(p, encoding="utf-8"))}


def dump_scene(fid, mark_lines=(), lo=None, hi=None, th=None):
    rows = json.load(open(f"{TE}/{fid}.json", encoding="utf-8"))
    jam = ja_of(fid)
    print(f"### scene {fid} ({len(rows)} lines)")
    for r in rows:
        n = r["line"]
        if lo is not None and not (lo <= n <= hi):
            continue
        ja = jam.get(n, "")
        g = M.ja_gender(ja)
        star = " <<<" if n in mark_lines else ""
        lab = ",".join(r.get("labels") or [])
        v = r.get("voice") or ""
        print(f"[{n:03d}] lab={lab} voice={v} ja_gender={g}{star}")
        print("   EN:", (r["en"] or "").replace("\n", "\\n")[:200])
        print("   JA:", (ja or "").replace("\r", "").replace("\n", "\\n")[:200])
        if th and r["en"] in th:
            print("   TH:", th[r["en"]].replace("\n", "\\n")[:200])


if __name__ == "__main__":
    q = sys.argv[1]
    if os.path.exists(f"{TE}/{q}.json"):
        lo = int(sys.argv[2]) if len(sys.argv) > 2 else None
        hi = int(sys.argv[3]) if len(sys.argv) > 3 else None
        dump_scene(q, lo=lo, hi=hi)
