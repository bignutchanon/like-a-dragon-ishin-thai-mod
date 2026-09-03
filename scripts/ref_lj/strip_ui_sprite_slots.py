#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ล้างช่อง donor ออกจากตารางฟอนต์สไปรต์ของ UI (`ui.coyote.en.par/font/*.bin`)
เพื่อบังคับให้เอนจิ้น fallback ไปฟอนต์ที่มีกลิฟไทย

## ปัญหาที่แก้ (docs/ISSUES.md LJ-015)

ฟอนต์ `type=4` ใน `font2_face.bin` ไม่ใช่ atlas SDF และไม่ใช่ vector — เป็น **ฟอนต์สไปรต์ของ UI**
ตารางค้นหาอยู่ที่ `ui.coyote.en.par/font/<ชื่อ>.bin` (ARMP · 256 แถว × 4 คอลัมน์)
โดย **เลขแถว = codepoint** และค่าในแถวคือ (texture id, กลุ่ม, ลำดับกลิฟในสไปรต์ชีต)
แถวที่เป็นศูนย์ทั้งแถว = ฟอนต์นี้ไม่มีตัวอักษรนั้น เอนจิ้นจะถอยไปใช้ฟอนต์อื่นแทน
(โครงสร้างเดียวกับที่โปรเจกต์ Y8 ถอดไว้ใน `translations/worklist/font_audit3/A_ui_font_prop.md`)

จอโดรน (`drone_font`) มีช่อง donor ของเราอยู่จริง **28 จาก 66 ตัว** ผลบนจอจึงออกมาปนกัน:
ตัวที่สไปรต์ชีตมี → วาดเป็นตัวละตินตัวใหญ่ · ตัวที่ไม่มี → fallback ไปฟอนต์ปกติ = ไทยตัวเล็ก
(ตรงกับภาพหน้าจอที่ผู้ใช้ส่งมา 1 ก.ย. 2026)

สคริปต์นี้เขียนศูนย์ทับทั้งแถวของ codepoint donor ทุกตัว → ทั้งข้อความ fallback ไปฟอนต์เดียวกันหมด
= อ่านเป็นไทยได้ทั้งบรรทัด (แลกกับการเสียหน้าตาฟอนต์สไปรต์เฉพาะจอนั้น)

**แก้ระดับไบต์ ไม่ผ่าน reARMP** เพราะ reARMP เข้ารหัสตารางกลุ่มนี้กลับมาไม่ตรงต้นฉบับ
(5,456 → 5,504 ไบต์ · ต่างกัน 884 ไบต์) — บทเรียน LJ-011 บอกว่า layout ที่เลื่อนเงียบ ๆ อันตราย
แถวเก็บแบบ row-major ตายตัว: เริ่มที่ `0x80` แถวละ 16 ไบต์ = int32 LE สี่ช่อง เรียง (texture id, กลุ่ม, ลำดับกลิฟ, ว่าง)
สคริปต์ตรวจสอบ layout นี้กับค่าที่ decode ด้วย reARMP ทุกไฟล์ก่อนเขียนเสมอ ถ้าไม่ตรงจะหยุด

ใช้:
  python scripts/strip_ui_sprite_slots.py             # รายงานอย่างเดียว
  python scripts/strip_ui_sprite_slots.py --write     # เขียน build/ui/ui.coyote.en/font/*.bin
อ่าน  extracted/ui_en/font/*.bin (แตกจาก par ของเกม — ไม่แตะ)
"""
import argparse
import glob
import io
import json
import os
import struct
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")           # กติกาเหล็กข้อ 6
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths                                        # noqa: E402
from thai_encode import DECODE                      # noqa: E402

SRC = paths.EXTRACTED / "ui_en" / "font"
OUT = paths.BUILD / "ui" / "ui.coyote.en" / "font"

ROW_BASE = 0x80          # ไบต์แรกของแถว 0
ROW_STRIDE = 16          # 4 คอลัมน์ × int32
N_ROWS = 256             # เลขแถว = codepoint 0..255
DONORS = sorted(cp for cp in DECODE if cp < N_ROWS)


def decode(path):
    """decode ด้วย reARMP ในโฟลเดอร์ชั่วคราว แล้วคืนตารางย่อย (อ่านอย่างเดียว)"""
    work = tempfile.mkdtemp(prefix="ljth_uifont_")
    dst = os.path.join(work, os.path.basename(path))
    io.open(dst, "wb").write(io.open(path, "rb").read())
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, str(paths.REARMP), os.path.basename(dst)],
                       cwd=work, env=env, stdout=subprocess.DEVNULL,
                       stderr=subprocess.PIPE, timeout=300)
    jpath = dst + ".json"
    if r.returncode != 0 or not os.path.exists(jpath):
        return None
    doc = json.load(io.open(jpath, encoding="utf-8"))
    try:
        return doc["0"][""]["1"]                    # ตารางย่อย 256 แถว
    except Exception:
        return None


def row_values(data, r):
    return struct.unpack_from("<4I", data, ROW_BASE + r * ROW_STRIDE)


def plan(name):
    """คืน (ไบต์ต้นฉบับ, แถว donor ที่มีข้อมูล) หรือ None ถ้าไฟล์นี้ไม่เข้าโครง"""
    src = SRC / (name + ".bin")
    data = bytearray(io.open(src, "rb").read())
    sub = decode(str(src))
    if not sub or sub.get("ROW_COUNT") != N_ROWS or sub.get("COLUMN_COUNT") != 4:
        return None
    if len(data) < ROW_BASE + N_ROWS * ROW_STRIDE:
        return None

    # ตรวจว่า layout ที่เราจะแก้ตรงกับค่าที่ decode ได้ทุกแถวจริง ๆ
    live = []
    for r in range(N_ROWS):
        raw = row_values(data, r)
        row = sub.get(str(r))
        got = list(row.values())[0] if row else {}
        want = (int(got.get("1") or 0), int(got.get("2") or 0), int(got.get("3") or 0), 0)
        if raw != want:
            sys.exit("!! layout ไม่ตรงกับ reARMP ที่แถว %d ของ %s: raw=%s json=%s"
                     % (r, name, raw, want))
        if any(raw):
            live.append(r)
    return data, [r for r in live if r in DONORS]


def main():
    ap = argparse.ArgumentParser(description="ล้างช่อง donor ในฟอนต์สไปรต์ของ UI")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    names = sorted(os.path.basename(p)[:-4] for p in glob.glob(str(SRC / "*.bin")))
    hits = 0
    for name in names:
        got = plan(name)
        if not got:
            continue
        data, rows = got
        if not rows:
            continue
        hits += 1
        print("%-30s donor ที่ต้องล้าง %2d ช่อง: %s"
              % (name, len(rows), " ".join("%02X" % r for r in rows)))
        if not a.write:
            continue
        for r in rows:
            struct.pack_into("<4I", data, ROW_BASE + r * ROW_STRIDE, 0, 0, 0, 0)
        OUT.mkdir(parents=True, exist_ok=True)
        io.open(OUT / (name + ".bin"), "wb").write(bytes(data))

        # ตรวจกลับ: ต้องต่างจากต้นฉบับเฉพาะไบต์ในแถว donor เท่านั้น
        orig = io.open(SRC / (name + ".bin"), "rb").read()
        new = io.open(OUT / (name + ".bin"), "rb").read()
        assert len(orig) == len(new)
        allowed = {ROW_BASE + r * ROW_STRIDE + k for r in rows for k in range(ROW_STRIDE)}
        diff = {i for i, (x, y) in enumerate(zip(orig, new)) if x != y}
        assert diff <= allowed, "มีไบต์นอกแถว donor เปลี่ยนใน %s" % name
        assert all(not any(row_values(bytearray(new), r)) for r in rows)
        print("   เขียน %s (เปลี่ยน %d ไบต์)" % (OUT / (name + ".bin"), len(diff)))

    print("ไฟล์ที่มี donor: %d จาก %d" % (hits, len(names)))
    if not a.write:
        print("(ยังไม่เขียนไฟล์ — ใส่ --write เพื่อเขียนจริง)")


if __name__ == "__main__":
    main()
