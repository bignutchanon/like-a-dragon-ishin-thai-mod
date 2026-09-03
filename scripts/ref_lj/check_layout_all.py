#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ตรวจ layout ของทุก bin ที่บิลด์แล้ว เทียบกับต้นฉบับใน `extracted/db_en/`

ด่านนี้จับบั๊กคนละชนิดกับ `check_bin_roundtrip.py`:

- `check_bin_roundtrip.py` decode ไฟล์ที่บิลด์ด้วย reARMP ตัวเดิม แล้วเทียบ **ค่า** กับ JSON ต้นฉบับ
  ถ้าตัว encode กับ decode ผิดสมมาตรกัน (เขียนผิดที่ แล้วอ่านกลับจากที่ผิดเดียวกัน) มันจะบอกว่า "ผ่าน"
- ตัวนี้เทียบ **ไบต์ในแถวจริง** กับ vanilla โดยข้ามเฉพาะช่อง index ข้อความ (type 13) กับ table
  pointer (type 9) ที่เราตั้งใจให้ต่าง → จับ layout เลื่อนได้ตรง ๆ

เหตุที่ต้องมี: reARMP writer โหมด storage-1 เคยจัด layout แถวใหม่เอง (ไม่มี alignment · ถือ
vf128 type 27 ขนาด 0) ทำให้ `talk_elevator.play_pos` (เวกเตอร์พิกัดวาร์ป shift 32) เลื่อนไป 37
ทับคอลัมน์อื่น → พิกัดขยะ → ผู้เล่นวาร์ปทะลุพื้นแมพ (Y7 เจอ 16 ส.ค. 2026 · LJ เจอ 29 ส.ค. 2026)
ดู docs/ISSUES.md LJ-011

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

# คอลัมน์ที่เรา **ตั้งใจแก้ค่า** หลังบิลด์ จึงไม่นับเป็น layout เพี้ยน
#   * font2_style.font_face_en  — LJ-002 ย้าย 126 สไตล์จากฟอนต์ vector ไปฟอนต์ SDF ที่มีกลิฟไทย
#   * font2_face.texture_*      — อัปเดตขนาด atlas ให้ตรงไฟล์ DDS ที่ขยายแล้ว
# ที่เหลือทุกไบต์ต้องตรง vanilla เป๊ะ
INTENDED = {
    "font2_style.bin": ["font_face_en"],
    "font2_face.bin": ["texture_width", "texture_height"],
}
AUX_SIZE = {1: 8, 2: 4, 3: 2, 4: 1, 5: 8, 6: 4, 7: 2, 8: 1, 9: 8, 10: 4, 12: 8, 13: 8, 27: 16}

STAGE = paths.BUILD / "text" / "db.coyote.en"
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
        sys.exit("!! ยังไม่ได้บิลด์ — รัน scripts/build_text.py ก่อน")
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
