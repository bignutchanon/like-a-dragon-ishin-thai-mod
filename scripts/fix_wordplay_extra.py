#!/usr/bin/env python3
"""ส่วนเติมของคลื่นมุกทายคำ (15 ก.ย. 2026) — บรรทัดที่ผู้ตรวจไม่ได้ยื่นแต่ต้องแก้ให้ทั้งรอบสอดคล้อง

1. รอบ "Religiously, that?" (ぎっちりしゆうがかえ) ในจดหมายโทซะ uid000c1432
   ผู้ตรวจเสนอคำสะพาน "เคร่ง" แทน "ทำเป็นกิจวัตร" (lead รับ #222 #230 #236 #239 ผ่าน merge_proposals)
   เพราะตัวเลือกสามข้อคือ มั่นคง (เคร่งครัด) · ทุกวัน (เคร่ง = ทำสม่ำเสมอ) · เคร่งศาสนา — "กิจวัตร" รองรับข้อศาสนาไม่ได้
   แต่ยังเหลือ 4 บรรทัดที่อ้างคำเดิม → แก้ตามนี้ ไม่งั้นจดหมายกับคำถามใช้คนละคำ
2. ควิซซากิโกะ uid000c12ed: ปุ่มตัวเลือก "A dog." = "สุนัขที่เลี้ยงไว้" แต่บทพูดตามปุ่ม (#073) = "หมาใช่ไหม?"
   ตัวเลือกอื่นปุ่มกับบทพูดใช้คำเดียวกัน (รูปปั้นจิโซ · หุ่นไล่กา) → แก้ที่ปุ่ม (ทั้งสองสตริงมีแค่ไฟล์นี้)

ใช้: python scripts/fix_wordplay_extra.py [--write]  แล้วต่อด้วย python scripts/merge_qc.py
"""
import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                      # noqa: E402
import merge_revise_wave as RW    # noqa: E402

# คีย์บรรทัด (หรือ "EN:<สตริง>") -> (ข้อความเดิมในคำแปล, ข้อความใหม่)
FIXES = {
    "uid000c1432#044": ('"ทำเป็นกิจวัตรงั้นหรือ"', '"เคร่งขนาดนั้นเชียวหรือ"'),
    "uid000c1432#224": ("ทำเป็นกิจวัตรหรือไฉน", "เคร่งขนาดนั้นเชียวหรือ"),
    "uid000c1432#226": ('คำว่า"ทำเป็นกิจวัตร"', 'คำว่า "เคร่ง"'),
    "uid000c1432#227": ('"ทำเป็นกิจวัตรหรือไฉน"', '"เคร่งขนาดนั้นเชียวหรือ"'),
    "EN:A dog.": ("สุนัขที่เลี้ยงไว้", "หมา"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    par = json.loads((paths.EXTRACTED / "parallel" / "msg.json").read_text(encoding="utf-8"))
    en_of = {r["key"]: r.get("en") or "" for r in par}
    master = json.loads(paths.MASTER_TH.read_text(encoding="utf-8"))
    take, bad = {}, 0
    for key, (old, new) in FIXES.items():
        en = key[3:] if key.startswith("EN:") else en_of.get(key, "")
        th = master.get(en)
        if not th or th.count(old) != 1:
            print("!! %s: หา %r ในคำแปลไม่เจอหรือเจอหลายที่ — %r" % (key, old, th))
            bad += 1
            continue
        take[en] = th.replace(old, new)
        print("%s\n  เดิม: %s\n  ใหม่: %s" % (key, RW.flat(th), RW.flat(take[en])))
    if args.write and not bad:
        nf, nk = RW.apply_to_done(take)
        print("ลง done %d ไฟล์ · %d คีย์ -> ต่อด้วย python scripts/merge_qc.py" % (nf, nk))
    elif bad:
        print("มีรายการใช้ไม่ได้ %d — ไม่เขียน" % bad)


if __name__ == "__main__":
    main()
