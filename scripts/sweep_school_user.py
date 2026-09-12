#!/usr/bin/env python3
r"""แก้ "ผู้ใช้สำนักX" เป็น "ผู้ใช้วิชาสำนักX" (ผู้ใช้รายงาน 12 ก.ย. 2026)

"สำนัก" ในบริบทนี้คือสายวิชา/สำนักดาบ คนไม่ได้ "ใช้สำนัก" แต่ใช้ **วิชา** ของสำนักนั้น
EN `a Tennen Rishin user` · `used the Tennen Rishin style` → ไทยต้องมีคำว่า "วิชา" คั่น
ในคลังมีรูปที่ถูกอยู่แล้วคือ "ผู้ใช้ดาบสำนักเท็นเน็นริชิน" และ "ฝีมือดาบสำนักเท็นเน็นริชิน"

จับ "ใช้" + (ช่องว่างขอบคำที่ fix_thai_wrap แทรกได้) + "สำนัก" แล้วเติม "วิชา"
ไม่แตะ "ผู้ใช้ดาบสำนัก…" (มีคำนามคั่นอยู่แล้ว) เพราะ pattern บังคับให้ "สำนัก" ตามหลัง "ใช้" ทันที

ใช้:
  python scripts/sweep_school_user.py --check
  python scripts/sweep_school_user.py
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
PAT = re.compile(r"ใช้\s?สำนัก")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    total = 0
    for path in sorted(DONE.glob("*.done.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        strings = data["strings"] if isinstance(data, dict) and "strings" in data else data
        n = 0
        for key, val in strings.items():
            if not isinstance(val, str) or not PAT.search(val):
                continue
            new = PAT.sub("ใช้วิชาสำนัก", val)
            if new != val:
                strings[key] = new
                n += 1
                if total + n <= 6:
                    print("  เดิม:", val[:80])
                    print("  ใหม่:", new[:80])
        if n:
            total += n
            if not args.check:
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print("%-28s %3d คีย์" % (path.name, n))
    print("รวม %d คีย์%s" % (total, "  (ตรวจอย่างเดียว)" if args.check else "  (เขียนแล้ว)"))


if __name__ == "__main__":
    main()
