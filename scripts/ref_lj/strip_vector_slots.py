#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ถอด donor slot ออกจาก cp table ของฟอนต์ vector (`*_s.bin`) เพื่อบังคับให้เอนจิ้น fallback
ไปฟอนต์ SDF ที่ฉีดกลิฟไทยไว้แล้ว

## ปัญหาที่แก้ (docs/ISSUES.md LJ-015)

ฟอนต์ในเกมมีสามชนิด (คอลัมน์ `type` ของ `font2_face.bin`): 1 = SDF atlas · 3 = vector (`<name>_s.bin`)
· 4 = ฟอนต์สไปรต์ของ UI (ตารางอยู่ใน `ui.coyote.en.par/font/*.bin`) เราฉีดกลิฟไทยได้เฉพาะชนิดที่ 1

จอที่เอนจิ้นเลือกฟอนต์ vector เองจึงวาดไบต์ donor ของเราเป็น "ตัวละตินอ่านออก" เสมอ
LJ-002 แก้ปัญหานี้ด้วยการย้าย `font2_style.font_face_en` ไปฟอนต์ SDF ซึ่งใช้ได้เฉพาะจอที่เลือกฟอนต์
ผ่านตาราง `font2_style` เท่านั้น — จอของมินิเกม (ชมรมเต้น · โดรน ฯลฯ) เลือกฟอนต์จากตาราง scene
ใน `ui.coyote.*.par` เอง ไม่ผ่าน `font2_style` การแก้ที่ตารางสไตล์จึงไปไม่ถึง

วิธีของ Y8 (`scripts/strip_svg_slots.py` ในโปรเจกต์ `y8-infinite-wealth` · พิสูจน์ในเกมแล้ว):
**ทำให้ lookup ของ codepoint donor พลาดเสียเลย** โดยเขียนทับค่าใน cp table ด้วย PUA (U+E000+i)
ซึ่งไม่มีข้อความไหนเรียกใช้ เอนจิ้นหา glyph ไม่เจอจึงถอยไปใช้ฟอนต์สำรอง = ฟอนต์ SDF ที่มีไทยแล้ว
ไม่แตะ payload ของ vector แม้แต่ไบต์เดียว (แกะ payload ไม่ได้ — บทเรียน K2R)

## เรื่อง cp table ที่เรียงอยู่แล้ว

Y8 ยกเลิกการ strip เมื่อ cp table เรียงลำดับ เพราะกลัวเอนจิ้นใช้ binary search
ของ LJ ตรวจแล้วว่า **เอนจิ้นใช้ binary search ไม่ได้**: ฟอนต์รีเทลเองมี cp table ที่ไม่เรียง
อยู่หลายไฟล์และเป็นไฟล์ใหญ่ด้วย (`dflihei-md_s` 13,600 · `koreangd14r_s` 11,942 ·
`morisawaudshingo-sc-m_s` 7,358 · `tbcgr_0p_s` / `tbgm_0p_s` 7,082) ถ้าเอนจิ้นค้นแบบ binary
ฟอนต์เหล่านี้ในเกมรีเทลจะพังไปแล้ว จึงถอด donor ในไฟล์ที่เรียงอยู่ได้เช่นกัน

ใช้:
  python scripts/strip_vector_slots.py                # ทุกไฟล์ *_s.bin ที่มี donor
  python scripts/strip_vector_slots.py tt_kafutechno-u_s
อ่าน  extracted/font/<name>.bin (ต้นฉบับเกม — ไม่แตะ) · เขียน build/font/<name>.bin
"""
import glob
import os
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8")           # กติกาเหล็กข้อ 6
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths                                        # noqa: E402
from thai_encode import DECODE                      # noqa: E402

PUA_BASE = 0xE000


def cp_pack_ch(ch):
    """codepoint ในตารางเก็บเป็นไบต์ UTF-8 อ่านแบบ big-endian (เหมือน font_tool.cp_pack)"""
    return int.from_bytes(ch.encode("utf-8"), "big")


DONORS = {cp_pack_ch(chr(c)) for c in DECODE}


def read_cps(data):
    """คืน (offset ของ cp table, จำนวน, รายการค่า) จากหัวไฟล์ฟอนต์"""
    aux, = struct.unpack_from("<Q", data, 0x18)
    cp_off, = struct.unpack_from("<Q", data, 0x20)
    n = (aux - cp_off) // 4
    return cp_off, aux, n, list(struct.unpack_from("<%dI" % n, data, cp_off))


def strip(name):
    src = paths.EXTRACTED / "font" / (name + ".bin")
    out_dir = paths.BUILD / "font"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / (name + ".bin")

    data = bytearray(open(src, "rb").read())
    assert data[:4] == b"font", "ไม่ใช่ไฟล์ฟอนต์: %s" % src
    cp_off, aux, n, cps = read_cps(data)
    hit = [i for i, v in enumerate(cps) if v in DONORS]
    if not hit:
        print("%-34s ไม่มี donor — ข้าม" % name)
        return False

    for k, i in enumerate(hit):
        struct.pack_into("<I", data, cp_off + 4 * i,
                         int.from_bytes(chr(PUA_BASE + k).encode("utf-8"), "big"))
    open(out, "wb").write(bytes(data))

    # ตรวจกลับ: ต้องต่างจากต้นฉบับเฉพาะไบต์ในโซน cp table เท่านั้น
    a, b = open(src, "rb").read(), open(out, "rb").read()
    assert len(a) == len(b)
    diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    assert all(cp_off <= i < aux for i in diff), "มีไบต์นอก cp table เปลี่ยน: %s" % name
    assert not (set(read_cps(bytearray(b))[3]) & DONORS), "ยังเหลือ donor: %s" % name
    print("%-34s cps=%-6d ถอด %d donor (เปลี่ยน %d ไบต์ ในโซน %#x..%#x)"
          % (name, n, len(hit), len(diff), cp_off, aux))
    return True


def main():
    names = sys.argv[1:]
    if not names:
        names = sorted(os.path.basename(p)[:-4]
                       for p in glob.glob(str(paths.EXTRACTED / "font" / "*_s.bin")))
    done = sum(1 for nm in names if strip(nm))
    print("ถอดแล้ว %d ไฟล์ (เขียนที่ %s)" % (done, paths.BUILD / "font"))


if __name__ == "__main__":
    main()
