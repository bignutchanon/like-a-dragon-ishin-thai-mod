"""make_todo.py — สร้าง batch_NNN.todo.json = คิวแปลที่ตัดคีย์ DNT ออกแล้ว

นักแปลควรได้รับเฉพาะคีย์ที่ต้องแปลจริง ส่วนคีย์ DNT (ชื่อ id · path รูป · ไฟล์ .msg
ที่ RGG ไม่เคยแปลเป็นอังกฤษ) ประกอบกลับทีหลังด้วย scripts/assemble_done.py

ใช้: python scripts/make_todo.py MSG_001 MSG_002 ...   (ไม่ใส่ = ทุกก้อนที่มีไฟล์ .dnt.json)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import paths
import thai_pronouns as tp

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

NOTE = ("คีย์ชนิดข้อมูล/ไฟล์ที่ไม่เคยแปลเป็นอังกฤษถูกตัดออกแล้ว — "
        "แปลเฉพาะคีย์ในไฟล์นี้ · ลำดับคีย์คือลำดับใน worklist")


def build(name):
    wl_path = paths.WORKLIST / ("batch_%s.json" % name)
    if not wl_path.exists():
        print("ไม่พบ", wl_path.name)
        return
    wl = json.loads(wl_path.read_text(encoding="utf-8"))
    dnt_path = paths.WORKLIST / ("batch_%s.dnt.json" % name)
    dnt = json.loads(dnt_path.read_text(encoding="utf-8")) if dnt_path.exists() else {}

    keys = [k for k in wl["strings"] if k not in dnt]
    out = {
        "batch": wl_path.name,
        "priority": wl.get("priority"),
        "sources": wl.get("sources", []),
        "note": NOTE,
        "strings": {k: "" for k in keys},
    }
    era = wl.get("priority") in (1, 4, 9)
    dropped_tm = 0
    for extra in ("ref_ja", "ref_tm"):
        if extra not in wl:
            continue
        sub = {k: v for k, v in wl[extra].items() if k in out["strings"]}
        if extra == "ref_tm" and era:
            # TM มาจากภาคปัจจุบัน (ครับ/ค่ะ/ผม/คุณ) ซึ่งผิดกติกาของภาคนี้ — วัดแล้ว 21% ของทั้งชั้น .msg
            # ถ้าปล่อยไว้ นักแปลจะลอกไปแล้วโดนด่าน M ตีกลับทีหลัง เสียรอบเปล่า
            keep = {k: v for k, v in sub.items()
                    if not (isinstance(v, str) and tp.MODERN_SPEECH.search(v))}
            dropped_tm = len(sub) - len(keep)
            sub = keep
        out[extra] = sub
    dest = paths.WORKLIST / ("batch_%s.todo.json" % name)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("batch_%s: ต้องแปล %d/%d (ตัด DNT %d%s)"
          % (name, len(keys), len(wl["strings"]), len(dnt),
             " · ตัด ref_tm ที่ผิดกติกา %d" % dropped_tm if dropped_tm else ""))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        args = [p.stem[len("batch_"):-len(".dnt")] for p in sorted(paths.WORKLIST.glob("batch_*.dnt.json"))]
    for a in args:
        build(a if not a.isdigit() else a.zfill(3))


if __name__ == "__main__":
    main()
