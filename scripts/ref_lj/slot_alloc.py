#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Slot map router ของ Lost Judgment — เลือก donor map ให้ตรงกับฟอนต์ที่วาด bin ปลายทาง

## ทำไมภาคนี้ไม่มี "slot allocator" แบบภาคแรก

Judgment (JETH) ใช้ฟอนต์ bitmap-grid จึงต้องจัดสรรเซลล์เองทั้งหมด (`scripts/ref_judgment/slot_alloc.py`)
Lost Judgment เป็นฟอนต์ **SDF สาย Y8**: กลิฟไทยถูกฉีดทับ *donor slot* ที่มีอยู่แล้วในฟอนต์ด้วย
`inject_thai_sdf.py` การ "จัดสรร" จึงจบไปตั้งแต่ตอนฉีดกลิฟ เหลือแค่หน้าที่เดียวคือ
**เลือก map ให้ตรงฟอนต์ตอน encode ข้อความ** — ไฟล์นี้ทำหน้าที่นั้น และเปิดด่าน X/S ของ `merge_qc.py`

## สอง map (docs/research.md §3.6 — สำรวจ donor จริงจากไฟล์เกม)

| ฟอนต์ | donor | map |
|---|---|---|
| `metaoffcpro-condbook` (เมนู/ไตเติล/UI) | Latin-1 accented ครบ 66/66 | `thai_encode.py` |
| `tbgm_0p`, `tbgm_0p_hires` (ซับคัตซีน EN) | Cyrillic ครบ 66 ตัวพอดี | `thai_encode_cyr.py` |

ตัวอักษรไทย 66 ตัวเป็นชุดเดียวกันทั้งสอง map — คำแปลชุดเดียวใช้ได้ทั้งสองฝั่ง ต่างแค่ตอน encode
ผลคือ **ต้องเลือก map ตาม bin ปลายทาง ไม่ใช่ map เดียวทั้งโปรเจกต์**

## การกำหนดว่า bin ไหนใช้ map ไหน

`SUB_BINS` = bin ที่เป็นบทพูด/ซับซึ่งวาดด้วยฟอนต์ตระกูล `tbgm_0p` (donor Cyrillic)
ที่เหลือถือเป็นเมนู/UI (donor Latin-1) ซึ่งเป็นค่าเริ่มต้น

⚠ รายชื่อนี้ยืนยันบนจอแล้วเฉพาะ `sound_auth.bin` (ซับคัตซีน) กับ `title_root.bin` (เมนูไตเติล)
bin อื่นเป็นการอนุมานจากชนิดข้อความ — ต้องยืนยันด้วยภาพหน้าจอทีละจอ (docs/research.md §4 ข้อ 3)
ถ้าเดาผิด ผลคือข้อความจอนั้นขึ้นเป็นตัวอักษรผิดชุด (ไม่ทำให้เกมพัง) แล้วย้ายชื่อ bin ข้ามฝั่งในตารางนี้

## โหมด direct (ยังไม่ยืนยัน)

`inject_thai_sdf.py --alias-thai` ใส่ alias ของ codepoint ไทยจริง (U+0E01..) ชี้ tile เดียวกับ donor ไว้แล้ว
ถ้าภาพหน้าจอยืนยันว่าเอนจิ้น route ไทยตรง ๆ ได้ → ใช้ `SlotMap.direct()` แล้วเลิกใช้ donor ทั้งโปรเจกต์
(ตอนนี้ยัง **ไม่ใช่ค่าเริ่มต้น** เพราะยังไม่มีหลักฐานบนจอ)

ใช้:
  python scripts/slot_alloc.py                 # รายงาน map + ตรวจ round-trip
  python scripts/slot_alloc.py --write         # เขียน translations/slotmap.json (เปิดด่าน X/S ของ merge_qc)
"""
import argparse
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")           # กติกาเหล็กข้อ 6 — console Windows = cp1252
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths                                        # noqa: E402
import thai_encode as MAP_LATIN1                    # noqa: E402
import thai_encode_cyr as MAP_CYR                   # noqa: E402

SLOTMAP = paths.TRANSLATIONS / "slotmap.json"

# bin ที่วาดด้วยฟอนต์ตระกูล tbgm_0p (donor = Cyrillic)
#
# ⚠ 29 ส.ค. 2026 — ล้างรายชื่อนี้ให้ว่างหลังทดสอบในเกมจริง (docs/ISSUES.md LJ-001)
# หลักฐานบนจอ: ข้อความที่ route ไป Latin-1 (ชื่อผู้พูด · ตัวติดตามเควส · ปุ่มบริบท) ขึ้นไทยถูกต้อง
# แต่ข้อความที่ route ไป Cyrillic (บทพูดในกล่อง · ซับคัตซีน · แถบโหลด) ขึ้น tofu ทึบทั้งแถว
# tofu = ตัวอักษร Cyrillic ไม่มีในฟอนต์ที่วาดจอนั้นเลย จึงสรุปได้ว่าบทพูดไม่ได้วาดด้วย
# tbgm_0p/tbgm_0p_hires อย่างที่เคยอนุมานจาก font2_style.font_face_en แต่วาดด้วยฟอนต์ตระกูล
# Latin ชุดเดียวกับ UI ซึ่งไม่มีช่วง Cyrillic (metaoffcpro-condbook มี donor Cyrillic 0/66)
#
# ตัดสมมติฐาน "ฟอนต์ไม่ได้ฉีด" ออกไปแล้วด้วยการตรวจไฟล์จริง:
#   - font.coyote.par ในเกม md5 ตรงกับ build/font.coyote.par เป๊ะ
#   - build/font/tbgm_0p_hires.bin มี donor Cyrillic 66/66 ชี้ tile ไทยแล้ว + alias ไทยจริงอีก 66
#   - atlas 8192x5120 มีพิกเซลกลิฟไทยจริงในโซนที่ UV ชี้ (ของเดิมโซนนั้นว่างเปล่า)
# ฟอนต์ฝั่ง tbgm จึงพร้อมใช้ แต่ไม่มี bin ไหนที่ยืนยันได้ว่าถูกวาดด้วยมันจริง
#
# ถ้าเจอจอที่ยืนยันได้ว่าใช้ tbgm จริง ให้ใส่ชื่อ bin กลับเข้ามาในเซ็ตนี้ทีละไฟล์
SUB_BINS = set()

MAPS = {"latin1": MAP_LATIN1, "cyr": MAP_CYR}


class SlotMap(object):
    """หน้ากากบาง ๆ ครอบ donor map หนึ่งชุด — API เท่าที่ build_text.py / merge_qc.py ต้องใช้

    `dec` = {donor codepoint: ตัวอักษรไทย} ใช้โดยด่าน S ของ merge_qc เพื่อกันไม่ให้คำแปล
    มีตัวอักษร donor ปนมาเอง (จะกลายเป็นตัวไทยมั่วบนจอ)
    """

    def __init__(self, name, mod, dec=None):
        self.name = name
        self.mod = mod
        self.dec = dict(dec if dec is not None else getattr(mod, "DECODE", {}))

    # -------------------------------------------------------------- factory
    @classmethod
    def load(cls, path=None):
        """map เริ่มต้นสำหรับงานที่ไม่ผูกกับ bin (เช่น QC) — donor รวมทั้งสองชุด

        encode ใช้ Latin-1 (ชุดที่ครอบคลุมเมนู/UI ซึ่งเป็น bin ส่วนใหญ่) แต่ `dec` รวม donor
        ของทั้งสอง map เพื่อให้ด่าน S จับตัวอักษร donor ได้ครบทั้ง Latin-1 และ Cyrillic
        """
        dec = dict(MAP_LATIN1.DECODE)
        dec.update(MAP_CYR.DECODE)
        return cls("latin1+cyr", MAP_LATIN1, dec)

    @classmethod
    def for_bin(cls, bin_name):
        """เลือก map ตาม bin ปลายทาง (ดูตาราง SUB_BINS ด้านบน)"""
        key = "cyr" if bin_name in SUB_BINS else "latin1"
        return cls(key, MAPS[key])

    @classmethod
    def named(cls, key):
        return cls(key, MAPS[key])

    @classmethod
    def direct(cls):
        """โหมดเขียน codepoint ไทยจริง (ใช้ได้ต่อเมื่อยืนยันบนจอแล้วว่าเอนจิ้น route ไทยได้)"""
        return cls("direct", _DirectMap)

    # --------------------------------------------------------------- encode
    def encode(self, text):
        """ไทย -> สตริง donor · ตัวอักษรไทยที่ไม่มีใน map = ขึ้น tofu บนจอ จึงถือเป็นความผิดพลาด"""
        miss = self.mod.coverage(text)
        if miss:
            raise SystemExit("ตัวอักษรไทยไม่มีใน map %s: %s" % (self.name, " ".join(miss)))
        return self.mod.encode(text)

    def coverage(self, text):
        return self.mod.coverage(text)

    def __repr__(self):
        return "<SlotMap %s donor=%d>" % (self.name, len(self.dec))


class _DirectMap(object):
    """map ที่ไม่แปลงอะไรเลย — ปล่อย codepoint ไทยจริงผ่านไปตรง ๆ"""
    DECODE = {}

    @staticmethod
    def encode(s):
        return s

    @staticmethod
    def coverage(text):
        return []


def selftest():
    """ตรวจว่า encode/decode ของทั้งสอง map กลับมาเป็นข้อความเดิมได้ (กันตารางเพี้ยน)"""
    samples = ["เริ่มเกมใหม่", "ยากามิ", "ไคโตะ", "สำนักงานนักสืบยากามิ",
               "กระทำอนาจาร", "หลิวหมังโยโกฮาม่า", "ผู้รับจ้างสารพัด"]
    bad = []
    for key, mod in MAPS.items():
        for s in samples:
            enc = mod.encode(s)
            back = "".join(mod.DECODE.get(ord(c), c) for c in enc)
            # decode คืนมาเป็นลำดับ "มาร์กก่อนฐาน" ตามที่ encode จัด — เทียบแบบไม่สนลำดับภายในคลัสเตอร์
            if sorted(back) != sorted(s):
                bad.append((key, s, back))
    return bad


def main():
    ap = argparse.ArgumentParser(description="รายงาน/เขียน slot map ของ LJ")
    ap.add_argument("--write", action="store_true", help="เขียน translations/slotmap.json")
    args = ap.parse_args()

    bad = selftest()
    for key, mod in MAPS.items():
        print("map %-7s donor %3d slot · ครอบคลุมไทย %d ตัว"
              % (key, len(mod.DECODE), len(set(mod.DECODE.values()))))
    print("bin ที่ใช้ donor Cyrillic: %s" % ", ".join(sorted(SUB_BINS)))
    if bad:
        for key, s, back in bad:
            print("!! round-trip ไม่ตรง (%s): %r -> %r" % (key, s, back))
        sys.exit("map เพี้ยน — ห้ามใช้บิลด์")
    print("round-trip ผ่านทั้งสอง map")

    if args.write:
        doc = {
            "note": "สร้างจาก scripts/slot_alloc.py — ห้ามแก้ด้วยมือ",
            "maps": {
                key: {"donor_codepoints": {"%04X" % cp: th for cp, th in sorted(mod.DECODE.items())},
                      "thai_count": len(set(mod.DECODE.values()))}
                for key, mod in MAPS.items()
            },
            "sub_bins": sorted(SUB_BINS),
        }
        SLOTMAP.parent.mkdir(parents=True, exist_ok=True)
        with io.open(SLOTMAP, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print("เขียน %s แล้ว (merge_qc จะเปิดด่าน X/S ให้อัตโนมัติ)" % SLOTMAP)


if __name__ == "__main__":
    main()
