#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ตรวจ layout ของทุก `.bin` ที่บิลด์แล้ว เทียบ **ไบต์ในแถว** กับต้นฉบับใน `extracted/db_en/`

ทำไมต้องมีด่านนี้ (พอร์ตจาก Lost Judgment 2 ก.ย. 2026):
`reARMP` ประกอบ `.bin` กลับ **ไม่ได้ไบต์เท่าเดิมทั้งไฟล์** (padding ต่าง) การเทียบทั้งไฟล์จึงใช้ไม่ได้
และการ decode ไฟล์ที่บิลด์ด้วย reARMP ตัวเดิมแล้วเทียบค่าก็เชื่อไม่ได้ — ถ้าตัวเขียนกับตัวอ่าน
ผิดสมมาตรกัน (เขียนผิดที่ แล้วอ่านกลับจากที่ผิดเดียวกัน) มันจะรายงานว่า "ผ่าน" ทั้งที่ไฟล์พัง
(กติกาเหล็กข้อ 6 · บทเรียน LJ-011)

ด่านนี้จึงเทียบ **ไบต์ในแถวจริง** กับ vanilla โดยข้ามเฉพาะช่องที่ต้องต่างอยู่แล้ว:
ดัชนีข้อความ (คอลัมน์ type 13) และ table pointer (type 9)
เคสที่ด่านนี้เคยจับได้ในภาคพี่น้อง: reARMP จัดแถวใหม่จนคอลัมน์เวกเตอร์เลื่อนไปทับคอลัมน์อื่น
→ ค่าพิกัดกลายเป็นขยะ → ผู้เล่นวาร์ปทะลุพื้นแมพ (Y7 16 ส.ค. 2026 · LJ 29 ส.ค. 2026)

ใช้:
  python scripts/check_layout_all.py
"""
import io
import json
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                                            # noqa: E402
from armp_layout_check import layout_mismatch           # noqa: E402

# คอลัมน์ที่เรา "ตั้งใจแก้ค่า" หลังบิลด์ จึงไม่นับว่า layout เพี้ยน
# ภาคนี้ยังไม่มีเลย — ระบบฟอนต์เป็น UE Slate + FreeType จึงไม่ต้องแตะตารางฟอนต์แบบ Dragon Engine
# (ถ้าวันหนึ่งต้องแก้คอลัมน์ไหนจริง ให้ใส่ที่นี่พร้อมเหตุผล ไม่ใช่ไปผ่อนเกณฑ์ในตัวตรวจ)
INTENDED = {}
AUX_SIZE = {1: 8, 2: 4, 3: 2, 4: 1, 5: 8, 6: 4, 7: 2, 8: 1, 9: 8, 10: 4, 12: 8, 13: 8, 27: 16}

STAGE = paths.BUILD / "text" / "db.macan.en"
VANILLA = paths.EXTRACTED / "db_en"
REPORT = paths.BUILD / "layout_report.md"


def intended_ranges(bin_name):
    """แปลงชื่อคอลัมน์ใน INTENDED เป็นช่วง (shift, size) โดยอ่าน COLUMN_LAYOUT ของ JSON ต้นฉบับ"""
    cols = INTENDED.get(bin_name)
    if not cols:
        return ()
    j = VANILLA / (bin_name + ".json")
    if not j.exists():
        return ()
    d = json.loads(io.open(j, encoding="utf-8").read())
    layout = d.get("COLUMN_LAYOUT")
    if not layout:
        return ()
    names = list(d["columnTypes"])
    out = []
    for c in cols:
        if c not in names:
            continue
        aux_type, shift = layout[names.index(c)][0], layout[names.index(c)][1]
        if shift >= 0:
            out.append((shift, AUX_SIZE.get(aux_type, 4)))
    return tuple(out)


def main():
    built = sorted(STAGE.glob("*.bin"))
    if not built:
        sys.exit("!! ยังไม่ได้บิลด์ชั้น ARMP — รัน scripts/build_text.py ก่อน")
    bad, skipped = {}, []
    for p in built:
        v = VANILLA / p.name
        if not v.exists():
            skipped.append(p.name)
            continue
        try:
            d = layout_mismatch(v, p, extra_skip=intended_ranges(p.name))
        except Exception as e:                          # noqa: BLE001
            d = ["ตรวจไม่ได้: %s: %s" % (type(e).__name__, e)]
        if d:
            bad[p.name] = d
    print("bin ที่ตรวจ %d · layout ตรง vanilla %d · ต่าง %d · ข้าม %d"
          % (len(built), len(built) - len(bad) - len(skipped), len(bad), len(skipped)))
    for name, d in sorted(bad.items()):
        print("  !! %s" % name)
        for x in d[:4]:
            print("       %s" % x)
    L = ["# Layout check — เทียบไบต์ในแถวกับ vanilla", "",
         "> `python scripts/check_layout_all.py` — ห้ามแก้ด้วยมือ", "",
         "| ตัวชี้วัด | ค่า |", "|---|---|",
         "| bin ที่ตรวจ | %d |" % len(built),
         "| layout ตรง vanilla | %d |" % (len(built) - len(bad) - len(skipped)),
         "| layout ต่าง | %d |" % len(bad),
         "| ข้าม (ไม่มีต้นฉบับ) | %d |" % len(skipped), ""]
    if bad:
        L += ["## bin ที่ layout ต่าง", ""]
        for name, d in sorted(bad.items()):
            L.append("- **%s** — %s" % (name, " · ".join(d[:4])))
    else:
        L += ["## ผลตรวจ", "", "ผ่านครบทุกไฟล์"]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    io.open(REPORT, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("เขียน %s" % REPORT)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
