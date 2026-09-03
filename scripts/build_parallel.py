#!/usr/bin/env python3
"""สร้างคลังคู่ขนาน อังกฤษ↔ญี่ปุ่น ของทั้งเกม (ทั้งสามชั้นข้อความ)

ทำไมต้องมี: ต้นฉบับอังกฤษของ RGG ตัดข้อมูลที่ภาษาไทยต้องใช้ทิ้งไปเยอะ —
เพศผู้พูด · ระดับความสุภาพ · คำนำหน้าชื่อ · สรรพนามบุรุษที่หนึ่ง
ญี่ปุ่นเก็บไว้ครบ และไฟล์ญี่ปุ่นอยู่ใน pak เดียวกันกับอังกฤษ (ยืนยันแล้ว 1 ก.ย. 2026)

การจับคู่แต่ละชั้น (ทุกชั้นจับคู่แบบชี้ขาด ไม่ใช่การเดา):
  .msg    — ไฟล์ชื่อเดียวกัน · ดัชนีแถวเดียวกัน
            ยืนยันแล้ว: ทั้ง 1,678 ไฟล์มีจำนวนแถวเท่ากันทุกไฟล์ (54,318 แถว)
  ARMP    — ตารางเดียวกัน · sub-table เดียวกัน · ดัชนีแถวเดียวกัน · คอลัมน์เดียวกัน
  locres  — namespace + key เดียวกัน

ผลลัพธ์: extracted/parallel/{msg,db,locres}.json  และ extracted/parallel/summary.json

ใช้: python scripts/build_parallel.py
ต้องมีมาก่อน: extract_msg.py / extract_db.py / extract_locres.py ทั้ง --lang en และ ja
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")   # console Windows = cp1252 (กติกาข้อ 5)
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                            # noqa: E402

OUT = paths.EXTRACTED / "parallel"


def _load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- .msg
def pair_msg():
    en_dir = paths.EXTRACTED / "text_en"
    ja_dir = paths.EXTRACTED / "text_ja"
    rows, mismatched = [], []
    for pe in sorted(en_dir.glob("*.json")):
        pj = ja_dir / pe.name
        if not pj.exists():
            mismatched.append("%s: ไม่มีฝั่ง ja" % pe.name)
            continue
        e, j = _load(pe), _load(pj)
        if len(e) != len(j):
            # ห้ามจับคู่มั่ว — ข้ามทั้งไฟล์แล้วรายงาน (ดีกว่าได้ข้อมูลผิดเงียบ ๆ)
            mismatched.append("%s: en %d แถว · ja %d แถว" % (pe.name, len(e), len(j)))
            continue
        for re_, rj in zip(e, j):
            rows.append({
                "key": re_["key"],
                "file": re_["file"],
                "line": re_["line"],
                "en": re_["en"],
                "ja": rj["en"],          # to_records ใช้ชื่อช่อง "en" เหมือนกันทุกภาษา
                "labels": re_.get("labels") or [],
                # label ของคำสั่ง 0x03 ชนิดย่อย 0x35 = "เล่นเสียงบรรทัดนี้"
                # เป็นหลักฐานผู้พูดรายบรรทัดตัวเดียวที่เชื่อได้ (ดู tools/msg.py)
                "voice": re_.get("voice"),
            })
    return rows, mismatched


# ---------------------------------------------------------------- ARMP
def _armp_cells(path):
    """คืน {(ตาราง, sub, แถว, คอลัมน์): ข้อความ} ของไฟล์ ARMP หนึ่งไฟล์"""
    d = _load(path)
    types = d.get("columnTypes") or {}
    text_cols = {c for c, t in types.items() if t == 13}
    out = {}
    if not text_cols:
        return out
    for k, v in d.items():
        if not k.isdigit() or not isinstance(v, dict):
            continue
        for i, (rk, row) in enumerate(v.items()):
            if not isinstance(row, dict):
                continue
            # reARMP_rowIndex เป็นดัชนีที่คงที่ข้ามภาษา — ใช้เป็นกุญแจ ไม่ใช่ลำดับการวน
            ri = row.get("reARMP_rowIndex", i)
            for col in text_cols:
                s = row.get(col)
                if isinstance(s, str):
                    out[(k, str(ri), col)] = s
    return out


def pair_db():
    en_dir = paths.EXTRACTED / "db_en"
    ja_dir = paths.EXTRACTED / "db_ja"
    rows, missing = [], []
    for pe in sorted(en_dir.glob("*.bin.json")):
        pj = ja_dir / pe.name
        if not pj.exists():
            missing.append(pe.name)
            continue
        ce, cj = _armp_cells(pe), _armp_cells(pj)
        table = pe.name.replace(".bin.json", "")
        for k, en in ce.items():
            rows.append({
                "key": "%s#%s#%s#%s" % (table, k[0], k[1], k[2]),
                "table": table,
                "col": k[2],
                "en": en,
                "ja": cj.get(k),
            })
    return rows, missing


# ---------------------------------------------------------------- locres
def pair_locres():
    de = _load(paths.EXTRACTED / "locres" / "Game.en.json")
    dj = _load(paths.EXTRACTED / "locres" / "Game.ja.json")

    def flat(d):
        S = d["strings"]
        out = {}
        for ns in d["namespaces"]:
            for e in ns["entries"]:
                out[(ns["ns"], e["key"])] = S[e["idx"]]
        return out

    fe, fj = flat(de), flat(dj)
    rows = []
    for (ns, key), en in fe.items():
        rows.append({
            "key": "%s::%s" % (ns, key),
            "ns": ns,
            "en": en,
            "ja": fj.get((ns, key)),
        })
    return rows, [k for k in fe if k not in fj]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {}

    msg, msg_bad = pair_msg()
    (OUT / "msg.json").write_text(json.dumps(msg, ensure_ascii=False), encoding="utf-8")
    summary["msg"] = {"rows": len(msg), "with_ja": sum(1 for r in msg if r["ja"]),
                      "files_skipped": len(msg_bad), "detail": msg_bad[:20]}
    print("msg     : %6d แถว · มีคู่ ja %6d · ไฟล์ที่ข้าม %d"
          % (len(msg), summary["msg"]["with_ja"], len(msg_bad)))

    db, db_bad = pair_db()
    (OUT / "db.json").write_text(json.dumps(db, ensure_ascii=False), encoding="utf-8")
    summary["db"] = {"rows": len(db), "with_ja": sum(1 for r in db if r["ja"]),
                     "tables_missing_ja": db_bad}
    print("db(ARMP): %6d ช่อง · มีคู่ ja %6d · ตารางที่ไม่มีฝั่ง ja %d"
          % (len(db), summary["db"]["with_ja"], len(db_bad)))

    lo, lo_bad = pair_locres()
    (OUT / "locres.json").write_text(json.dumps(lo, ensure_ascii=False), encoding="utf-8")
    summary["locres"] = {"rows": len(lo), "with_ja": sum(1 for r in lo if r["ja"]),
                         "keys_missing_ja": len(lo_bad)}
    print("locres  : %6d แถว · มีคู่ ja %6d · คีย์ที่ไม่มีฝั่ง ja %d"
          % (len(lo), summary["locres"]["with_ja"], len(lo_bad)))

    (OUT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nเขียนแล้ว: %s" % OUT)


if __name__ == "__main__":
    main()
