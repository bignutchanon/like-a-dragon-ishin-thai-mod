"""ตรวจลำดับสระ/วรรณยุกต์ไทยที่ **จอแสดงผลไม่ได้**

ทำไม (3 ก.ย. 2026 · ผู้ตรวจคลื่น MSG_052–054 รายงาน): บรรทัด `ตายซะ อากุริอิิ!!!`
มีสระ ิ **สองตัวบนพยัญชนะเดียว** ซึ่งบนจอจะเป็นกลิฟทับกัน อ่านไม่ออก
แต่ **ผ่านด่านทุกตัวที่มีอยู่** เพราะไม่มีตัวไหนดูลำดับตัวประกอบเลย

ลำดับที่ถูกต้องมีแบบเดียว: พยัญชนะ + (สระบน/ล่างหนึ่งตัว) + (วรรณยุกต์หนึ่งตัว) + (ทัณฑฆาต)
ผิดคือ: สระบนซ้อนสระบน · วรรณยุกต์ซ้อนวรรณยุกต์ · วรรณยุกต์มาก่อนสระ · ตัวประกอบลอยหลังช่องว่าง

ใช้:
  python scripts/check_thai_marks.py              # ทุกไฟล์ใน translations/done/
  python scripts/check_thai_marks.py --only MSG_052
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DONE = ROOT / "translations" / "done"

ABOVE = "ัิีึื็ํ"   # ั ิ ี ึ ื ็ ํ
BELOW = "ฺุู"                            # ุ ู ฺ
TONE = "่้๊๋"                       # ่ ้ ๊ ๋
THANTHAKHAT = "์"                                  # ์
CONS = "ก-ฮ"

BAD = [
    ("สระบนซ้อนสระบน", re.compile("[%s][%s]" % (ABOVE, ABOVE))),
    ("สระล่างซ้อนสระล่าง", re.compile("[%s][%s]" % (BELOW, BELOW))),
    ("วรรณยุกต์ซ้อนวรรณยุกต์", re.compile("[%s][%s]" % (TONE, TONE))),
    ("วรรณยุกต์มาก่อนสระบน/ล่าง", re.compile("[%s][%s%s]" % (TONE, ABOVE, BELOW))),
    # ⚠ ตัวประกอบ "ลอย" = ตามหลังสิ่งที่ไม่ใช่พยัญชนะและไม่ใช่สระบน/ล่าง
    #   (วรรณยุกต์ตามหลังสระบนเป็นรูปที่ถูกต้อง เช่น เชื่อ = ช + ื + ่ — ห้ามนับเป็นผิด)
    ("ตัวประกอบลอย (ไม่มีพยัญชนะนำ)",
     re.compile("(?<![%s%s%s])[%s%s%s%s]" % (CONS, ABOVE, BELOW, ABOVE, BELOW, TONE, THANTHAKHAT))),
]


def batches(only):
    if only:
        return [DONE / ("batch_%s.done.json" % only)]
    return sorted(DONE.glob("batch_*.done.json"))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only")
    ap.add_argument("--max", type=int, default=40)
    a = ap.parse_args()

    hits = 0
    for path in batches(a.only):
        if not path.exists():
            continue
        for k, v in json.load(io.open(path, encoding="utf-8"))["strings"].items():
            if not isinstance(v, str):
                continue
            for name, rx in BAD:
                m = rx.search(v)
                if not m:
                    continue
                hits += 1
                if hits <= a.max:
                    start = max(0, m.start() - 12)
                    print("\n%s  %s" % (path.name, name))
                    print("   EN: %s" % k.replace("\n", " / ")[:80])
                    print("   TH: ...%s..." % v[start:m.end() + 12].replace("\n", " / "))
                break
    print()
    if hits:
        print("พบลำดับที่แสดงผลไม่ได้ %d จุด" % hits)
        return 1
    print("ลำดับสระ/วรรณยุกต์ถูกต้องทุกบรรทัด")
    return 0


if __name__ == "__main__":
    sys.exit(main())
