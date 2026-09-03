#!/usr/bin/env python3
"""ดึง "เพศของผู้พูด" จากไฟล์เกมโดยตรง — `sound_voicer.bin` มีคอลัมน์ `sex` (1=ชาย · 2=หญิง)

ที่มา: ผู้ตรวจ batch_043 ค้นเจอว่า `sound_voicer.bin` เก็บ **เพศของ voicer ทุกตัว** ไว้ตรง ๆ
(ตรวจสอบแล้วตรงกับตัวละครที่เรายืนยันเพศไว้ก่อนหน้าทุกตัว: yagami/hoshino/kuroiwa/kido/izumida/saori)
นี่คือหลักฐานที่ดีที่สุดที่เรามี — ดีกว่าการไล่หา he/she ในบทพูด เพราะครอบคลุมทุกคนที่มีเสียงพากย์

สคริปต์นี้แปลงตารางนั้นเป็น `extracted/facts/voicer_gender.json` แล้ว **ผสมเข้า**
`extracted/facts/gender_evidence.json` (ทับเฉพาะรายการที่ยังเป็น unknown หรือยังไม่มี)

ใช้:  python scripts/make_gender_table.py [--write]
"""
import argparse
import collections
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

SRC = paths.DB_EN / "sound_voicer.bin.json"
OUT = paths.EXTRACTED / "facts" / "voicer_gender.json"
EVIDENCE = paths.EXTRACTED / "facts" / "gender_evidence.json"
SEX = {1: "male", 2: "female"}


def load_voicers():
    data = json.load(io.open(SRC, encoding="utf-8"))
    out = collections.OrderedDict()
    for k, v in data.items():
        if not isinstance(v, dict) or k in ("columnTypes", "columnValidity"):
            continue
        for name, cols in v.items():
            if isinstance(cols, dict) and "sex" in cols and name:
                g = SEX.get(cols["sex"])
                if g:
                    out[name] = g
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="เขียนไฟล์ + ผสมเข้า gender_evidence.json")
    a = ap.parse_args()

    voicers = load_voicers()
    males = sum(1 for g in voicers.values() if g == "male")
    print("voicer ที่มีเพศระบุ: %d (ชาย %d · หญิง %d)" % (len(voicers), males, len(voicers) - males))

    if not a.write:
        for n, g in list(voicers.items())[:10]:
            print("   %-24s %s" % (n, g))
        print("(ใส่ --write เพื่อเขียนไฟล์)")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(
        json.dumps(voicers, ensure_ascii=False, indent=1) + "\n")

    ev = json.load(io.open(EVIDENCE, encoding="utf-8"),
                   object_pairs_hook=collections.OrderedDict) if EVIDENCE.exists() else collections.OrderedDict()
    filled = added = 0
    for name, g in voicers.items():
        cur = ev.get(name)
        entry = collections.OrderedDict([
            ("name_en", name),
            ("gender", g),
            ("confidence", "high"),
            ("evidence", [{"source": "sound_voicer.bin (คอลัมน์ sex)",
                           "quote": "sex=%d" % (1 if g == "male" else 2),
                           "type": "game_data"}]),
            ("notes", "ดึงอัตโนมัติด้วย scripts/make_gender_table.py — ตารางเพศของ voicer ในไฟล์เกม"),
        ])
        if cur is None:
            ev[name] = entry
            added += 1
        elif cur.get("gender") in (None, "unknown"):
            ev[name] = entry
            filled += 1
    io.open(EVIDENCE, "w", encoding="utf-8", newline="\n").write(
        json.dumps(ev, ensure_ascii=False, indent=1) + "\n")

    still_unknown = [k for k, v in ev.items()
                     if isinstance(v, dict) and v.get("gender") == "unknown"]
    print("เขียน %s" % OUT)
    print("ผสมเข้า gender_evidence.json: เพิ่มใหม่ %d · เติมที่เคย unknown %d" % (added, filled))
    print("ยังเหลือ unknown %d: %s" % (len(still_unknown), " ".join(still_unknown[:15]) or "-"))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
