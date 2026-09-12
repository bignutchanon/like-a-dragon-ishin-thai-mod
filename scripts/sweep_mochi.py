#!/usr/bin/env python3
r"""แก้ทับศัพท์ 餅 (mochi) จาก "มอจิ" เป็น "โมจิ" ทั้งคลัง

ที่มา (ผู้ใช้สั่ง 12 ก.ย. 2026): คำที่ใช้อยู่ปนกันสองรูป — นับทั้งคลังแล้วได้
**"โมจิ" 31 คีย์ : "มอจิ" 6 คีย์** รูปข้างมากตรงกับการถอดเสียง も = โม ที่โปรเจกต์ใช้อยู่แล้ว
(โมโมกาวะ · โมริ) จึงกวาดรูปข้างน้อยให้ตรงกัน

⚠ ไม่ใช้กติกา "ก้อนเลขน้อยกว่าเป็นเจ้าของรูป" — นับทั้งคลังก่อนกวาดเสมอ (HANDOFF §4)

ระหว่างคำอาจมีช่องว่างที่ `fix_thai_wrap.py` แทรกไว้ตอนขอบคำ (§0.52) จึงจับด้วย `\s*`
แล้วเขียนคืนแบบติดกัน

ใช้:
  python scripts/sweep_mochi.py --check    # ดูว่าจะแก้อะไรบ้าง ไม่เขียนไฟล์
  python scripts/sweep_mochi.py            # เขียนลง translations/done/*.done.json
แล้วต่อด้วย: python scripts/merge_qc.py
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DONE = Path("translations/done")
WRONG = re.compile(r"มอ\s*จิ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="ไม่เขียนไฟล์ แสดงรายการที่จะแก้")
    args = ap.parse_args()

    n_files = n_keys = 0
    for p in sorted(DONE.glob("*.done.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        strings = data.get("strings") or {}
        hit = 0
        for en, th in list(strings.items()):
            if not isinstance(th, str) or not WRONG.search(th):
                continue
            new = WRONG.sub("โมจิ", th)
            hit += 1
            print("%s\n  เดิม: %s\n  แก้ : %s" % (p.name, th.replace("\n", " / "), new.replace("\n", " / ")))
            if not args.check:
                strings[en] = new
        if hit:
            n_files += 1
            n_keys += hit
            if not args.check:
                p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print("-" * 50)
    print("%s %d ไฟล์ · %d คีย์" % ("จะแก้" if args.check else "แก้แล้ว", n_files, n_keys))
    if not args.check and n_keys:
        print("ต่อด้วย: python scripts/merge_qc.py")


if __name__ == "__main__":
    main()
