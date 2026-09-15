#!/usr/bin/env python3
"""เก็บงานค้างหลังคลื่นเกลาบทพูด §0.61 ที่ lead แก้เองใน done (15 ก.ย. 2026)

1. "No good!" (แชทมินิเกมไพ่/มาจง/โชกิ ダメだ、こりゃ！ ทั้ง 4 ที่) — คำแปลเดิม "ไม่ไหวแล้วสิ่งนี้!" ยก こりゃ มาตรงตัว
   จน "สิ่งนี้" ลอย · ข้อเสนอคลื่นเกลา "หมดสภาพแล้ว!" ความหมายเพี้ยน (หมดสภาพ = ชำรุด/อ่อนล้า) lead ตัดทิ้งใน
   lead_drop.json แล้วแก้เองเป็น "แบบนี้ไม่ไหวแล้ว!" (こりゃ = แบบนี้)
2. ชื่อเกมไพ่ตามคำล็อก glossary §1.9.6 — บทบ่อนพนันเก่ายังเขียน โคอิโคอิ / โออิโจคาบุ (ไม่มีขีด · จ แทน ช)
3. ปุ่ม こいこいする / こいこいしない แปล "เรียกโคอิโคอิ" แต่ทิปส์วิธีเล่นเรียกปุ่มเดียวกันว่า "เรียกโคอิ"
   -> ใช้ "เรียกโคอิ-โคอิ" ทั้งปุ่มและทิปส์ (ตาม JA และคำล็อกชื่อเกม)
   ต้องไม่ตรงชื่อคน — "เรียกโคอิจิ" (Koichi) จึงห้ามมีอักษรไทยหรือขีดตามหลัง
4. ข้อความได้รับไอเทม: รูปข้างมาก (143 สตริง) เว้นวรรคก่อนแท็กสีและก่อน "แล้ว" ท้ายชื่อไอเทม
   "ได้รับ<Color:8>ของ" / "ของ<Color:Default>แล้ว" ที่ไม่เว้นวรรค -> เติมช่องว่าง
   ("แล้ว" แตะเฉพาะสตริงที่ขึ้นต้นด้วย ได้รับ — ประโยคอื่นที่ต่อ แล้วก็ หลังแท็กไม่เกี่ยว)

ใช้: python scripts/fix_polish_leftovers.py [--write]   แล้วต่อด้วย python scripts/merge_qc.py
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

# EN -> (คำแปลที่คาดว่ายังอยู่, คำแปลใหม่) — ถ้าคำแปลปัจจุบันไม่ใช่ของเดิม ไม่แตะ (กันทับงานที่ลงทีหลัง)
EXACT = {
    "No good!": ("ไม่ไหวแล้วสิ่งนี้!", "แบบนี้ไม่ไหวแล้ว!"),
}
SUBS = [
    (re.compile("โคอิโคอิ"), "โคอิ-โคอิ"),
    (re.compile("โออิโจคาบุ"), "โออิโช-คาบุ"),
    (re.compile("เรียกโคอิ(?![-฀-๿])"), "เรียกโคอิ-โคอิ"),
    (re.compile(r"ได้รับ(<Color:\d+>)"), r"ได้รับ \1"),
]
OBTAINED_END = re.compile(r"(<Color:Default>)แล้ว")


def fix(en, th):
    if en in EXACT:
        old, new = EXACT[en]
        if th == old:
            th = new
        elif th != new:
            print("!! %r คำแปลปัจจุบันไม่ตรงของเดิม — ข้าม: %s" % (en, th))
    for rx, rep in SUBS:
        th = rx.sub(rep, th)
    if th.startswith("ได้รับ"):
        th = OBTAINED_END.sub(r"\1 แล้ว", th)
    return th


def one(s):
    return s.replace("\r\n", " / ").replace("\n", " / ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    n_files = n_keys = 0
    for p in sorted((paths.TRANSLATIONS / "done").glob("batch_*.done.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        strings = data.get("strings") or {}
        hit = 0
        for en, th in list(strings.items()):
            if not isinstance(th, str):
                continue
            new = fix(en, th)
            if new == th:
                continue
            print("%s | %s\n  เดิม: %s\n  ใหม่: %s" % (p.name, one(en)[:90], one(th), one(new)))
            strings[en] = new
            hit += 1
        if hit:
            n_files += 1
            n_keys += hit
            if args.write:
                p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print("%d ไฟล์ · %d คีย์%s" % (n_files, n_keys, "" if args.write else " (ยังไม่เขียน — ใส่ --write)"))


if __name__ == "__main__":
    main()
