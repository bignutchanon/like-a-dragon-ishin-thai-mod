#!/usr/bin/env python3
"""หา "คีย์ที่ใช้ซ้ำหลาย bin" — คีย์สั้นที่โผล่ในหลายตารางของเกม

ทำไมต้องมี: `master_th.json` และไฟล์ `.done.json` เป็น map แบน EN -> TH ตัวเดียว
คีย์เดียวจึงถูกใช้ในทุกที่ที่ข้อความนั้นปรากฏ ถ้าแปลให้เข้ากับบริบทเดียว บริบทอื่นจะพัง
(เคสจริง: ผู้ตรวจ batch_114 เจอ `Medium` ที่เป็นทั้งทรงผมคาบาเรต์และระดับกราฟิกใน option.bin
และ `Up` ที่เป็นทั้งทรงผมและปุ่มทิศทางใน input_action.bin — ถ้าแก้ให้เข้ากับทรงผมจะทำเมนูอื่นพัง)

ใช้:
  python scripts/make_multibin_index.py --write     # เขียน docs/reference/multibin_keys.md
  python scripts/make_multibin_index.py --key "Medium"   # ถามทีละคีย์
"""
import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

UNIQUE = paths.PROJECT / "extracted" / "unique_strings.json"
OUT = paths.PROJECT / "docs" / "reference" / "multibin_keys.md"
MAX_LEN = 40          # คีย์ยาวกว่านี้เป็นประโยค ชนบริบทได้ยาก


def load():
    return json.load(io.open(UNIQUE, encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="เขียนไฟล์รายงาน")
    ap.add_argument("--key", help="ถามคีย์เดียว")
    a = ap.parse_args()
    uniq = load()

    if a.key:
        meta = uniq.get(a.key)
        if not meta:
            print("ไม่พบคีย์นี้ในไฟล์เกม")
            return 1
        bins = sorted(meta["bins"])
        print("%s  ->  %d bin: %s" % (a.key, len(bins), " · ".join(bins)))
        return 0

    rows = []
    for en, meta in uniq.items():
        bins = sorted(set(meta["bins"]))
        if len(bins) >= 2 and len(en) <= MAX_LEN and "\n" not in en:
            rows.append((len(bins), en, bins))
    rows.sort(key=lambda r: (-r[0], r[1].lower()))

    lines = ["# คีย์ที่ใช้ซ้ำหลาย bin — ห้ามแปลให้เข้าบริบทเดียว", "",
             "สร้างด้วย `python scripts/make_multibin_index.py --write` "
             "(ที่มา `extracted/unique_strings.json`) · เกณฑ์: คีย์ยาวไม่เกิน %d ตัวอักษร "
             "และปรากฏใน 2 bin ขึ้นไป" % MAX_LEN, "",
             "**กติกา**: คำแปลของคีย์พวกนี้ต้องใช้ได้กับ *ทุก* บริบทที่มันโผล่ "
             "ถ้าเลี่ยงไม่ได้ให้เลือกคำกลาง ๆ แล้วรายงาน lead — ห้ามแปลให้เข้ากับ bin เดียว "
             "(ไฟล์คำแปลเป็น map แบน EN→TH ตัวเดียวทั้งเกม)", "",
             "รวม %d คีย์" % len(rows), "",
             "| คีย์ EN | จำนวน bin | bin ที่ใช้ |", "|---|---|---|"]
    for n, en, bins in rows:
        show = " · ".join(bins[:6]) + (" · …" if len(bins) > 6 else "")
        lines.append("| `%s` | %d | %s |" % (en.replace("|", r"\|"), n, show))

    if a.write:
        io.open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print("เขียน %s แล้ว (%d คีย์)" % (OUT, len(rows)))
    else:
        print("\n".join(lines[:30]))
        print("... (ใส่ --write เพื่อเขียนไฟล์เต็ม %d คีย์)" % len(rows))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
