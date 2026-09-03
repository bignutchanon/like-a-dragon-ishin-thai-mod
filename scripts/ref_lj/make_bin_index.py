#!/usr/bin/env python3
"""ทำสารบัญ bin ทั้ง 1,358 ไฟล์ของ `db.coyote.en.par` -> extracted/bin_index.json + docs/bin_index.md

อ่านจาก JSON ที่ `extract_all_en.py` แปลงไว้แล้ว (ไม่แตะไฟล์เกม) เก็บต่อไฟล์:
  ROW_COUNT · จำนวนคอลัมน์ · มี sub-table ไหม · จำนวน string ที่เข้าเกณฑ์แปล
  · ขนาดไฟล์ · กลุ่ม (prefix ก่อน `_` ตัวแรก)

ใช้ตอนวางแผน worklist และตอนตัดสิน DENY_BINS (ตารางที่ engine อ่านเป็นพารามิเตอร์ ไม่ใช่ข้อความ)
"""
import io
import json
import os
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

BINS = paths.DB_EN
OUT_JSON = paths.EXTRACTED / "bin_index.json"
OUT_MD = paths.DOCS / "bin_index.md"
TOP_N = 60


def scan_one(name, strings_by_bin):
    p = BINS / name
    jp = BINS / (name + ".json")
    ent = {"bin": name, "size": p.stat().st_size, "group": name.split("_")[0].replace(".bin", ""),
           "strings": len(strings_by_bin.get(name, [])), "rows": None, "cols": None,
           "subtables": 0, "ok": jp.exists()}
    if not jp.exists():
        return ent
    try:
        d = json.load(io.open(jp, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — ไฟล์พังนับเป็น not ok ไม่ให้ล้มทั้งงาน
        ent["ok"] = False
        ent["error"] = "%s: %s" % (type(e).__name__, e)
        return ent
    ent["rows"] = d.get("ROW_COUNT")
    rows = [k for k in d if k not in ("VERSION", "REVISION", "ROW_COUNT")]
    ent["cols"] = len(d[rows[0]]) if rows and isinstance(d[rows[0]], dict) else 0
    ent["subtables"] = sum(1 for k in rows if isinstance(d.get(k), dict)
                           and any(isinstance(v, dict) for v in d[k].values()))
    return ent


def main():
    strings_by_bin = {}
    p = paths.EXTRACTED / "strings_by_bin.json"
    if p.exists():
        strings_by_bin = json.load(io.open(p, encoding="utf-8"))
    names = sorted(f for f in os.listdir(BINS) if f.endswith(".bin"))
    index = [scan_one(n, strings_by_bin) for n in names]
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT_JSON, "w", encoding="utf-8", newline="\n").write(
        json.dumps(index, ensure_ascii=False, indent=1) + "\n")

    ok = [e for e in index if e["ok"]]
    bad = [e for e in index if not e["ok"]]
    with_text = sorted((e for e in ok if e["strings"]), key=lambda e: -e["strings"])
    groups = Counter()
    for e in ok:
        groups[e["group"]] += e["strings"]

    L = ["# สารบัญ bin — `db.coyote.en.par` (1,358 ไฟล์)", "",
         "> สร้างด้วย `python scripts/make_bin_index.py` · ข้อมูลเต็มอยู่ที่ `extracted/bin_index.json`", "",
         "| ตัวชี้วัด | ค่า |", "|---|---|",
         "| bin ทั้งหมด | %d |" % len(index),
         "| แปลง JSON ได้ | %d |" % len(ok),
         "| แปลงไม่ได้ | %d |" % len(bad),
         "| bin ที่มีข้อความแปลได้ | %d |" % len(with_text),
         "| แถวรวมทุก bin | {:,} |".format(sum(e["rows"] or 0 for e in ok)),
         "| ขนาดรวม | %.1f MB |" % (sum(e["size"] for e in index) / 1048576.0), "",
         "## Top-%d bin ตามจำนวน string" % TOP_N, "",
         "| # | bin | strings | rows | cols | ขนาด (KB) |", "|---|---|---|---|---|---|"]
    for i, e in enumerate(with_text[:TOP_N], 1):
        L.append("| %d | %s | %d | %s | %s | %.0f |" % (
            i, e["bin"], e["strings"], e["rows"], e["cols"], e["size"] / 1024.0))
    L += ["", "## กลุ่มไฟล์ (prefix) ที่มีข้อความมากสุด", "",
          "| กลุ่ม | strings |", "|---|---|"]
    for g, n in groups.most_common(20):
        L.append("| %s | %d |" % (g, n))
    L += ["", "## bin ที่ reARMP แปลงไม่ผ่าน (%d)" % len(bad), "",
          "| bin | ขนาด | หมายเหตุ |", "|---|---|---|"]
    for e in bad:
        L.append("| %s | %d B | %s |" % (e["bin"], e["size"], e.get("error", "reARMP KeyError")))
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT_MD, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("เขียน", OUT_JSON)
    print("เขียน", OUT_MD)
    print("bin %d · แปลงได้ %d · มีข้อความ %d · แถวรวม %d"
          % (len(index), len(ok), len(with_text), sum(e["rows"] or 0 for e in ok)))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
