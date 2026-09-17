#!/usr/bin/env python3
"""เปลี่ยน "ไอ้หนู<ชื่อ>" ที่แปลจาก -chan กลับเป็น "<ชื่อ>จัง" (คำเคาะผู้ใช้ 17 ก.ย. 2026)

ผู้ใช้เคาะ: โอกิตะเรียกไซโตว่า 一ちゃん / Hajime-chan ให้แปลตรงเป็น "ฮาจิเมะจัง"
รอบสอง: ชื่ออื่นที่เป็น -chan ทั้งหมด (เรียวมะ/โทชิ/อิซามิ/โกโร/ชินปะ) ก็เป็น "จัง" ด้วย
→ ยกเลิกข้อยกเว้น "ไอ้หนู" นำหน้าชื่อ (เคาะ 2 ก.ย. 2026) ทั้งข้อ
"ไอ้หนู" ที่แปลจาก kid/boy (ไม่มีชื่อ) ไม่แตะ

แก้ใน `translations/done/*.done.json` แบบแทนข้อความดิบ (คงรูปแบบไฟล์เดิม)
แล้วต้องรัน `merge_qc.py` เพื่อลง master_th.json

ใช้:
  python scripts/revert_hajime_chan.py          # พิมพ์จำนวน ไม่เขียน
  python scripts/revert_hajime_chan.py --write
"""
import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DONE = Path(__file__).resolve().parent.parent / "translations" / "done"

# ลำดับสำคัญ: รูปพิเศษก่อนรูปทั่วไป
SWAPS = [
    ("ไ-ไอ้หนูฮาจิเมะ", "ฮ-ฮาจิเมะจัง"),     # "Ha—Hajime-chan?" (ติดอ่าง)
    ("ไอ้หนู... ฮาจิเมะ", "ฮาจิเมะ... จัง"),  # "Hajime... chan?"
    ("ไอ้หนูฮาจิเมะ", "ฮาจิเมะจัง"),
    # รอบสอง (เคาะ 17 ก.ย. 2026): ชื่ออื่นที่ต้นฉบับเป็น -chan ก็กลับเป็น "จัง" ด้วย
    # (คนโดหัวหน้าใหญ่โดนเรียก "ไอ้หนู" อ่านแล้วผิดที่) · "ไอ้หนู" จาก kid/boy ไม่แตะ
    ("ไอ้หนูซากาโมโตะ เรียวมะ", "ซากาโมโตะ เรียวมะจัง"),
    ("ไอ้หนูเรียวมะ", "เรียวมะจัง"),
    ("ไอ้หนูโทชิ", "โทชิจัง"),
    ("ไอ้หนูชินปา", "ชินปะจัง"),   # รูปเดียวกับ "ชินปะจัง" ที่มีอยู่แล้ว (glossary)
    ("ไอ้หนูอิซามิ", "อิซามิจัง"),
    ("ไอ้หนูโกโร", "โกโรจัง"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    total = 0
    for f in sorted(DONE.glob("*.done.json")):
        text = f.read_bytes().decode("utf-8")
        new = text
        n = 0
        for old, rep in SWAPS:
            n += new.count(old)
            new = new.replace(old, rep)
        if n:
            total += n
            print(f"{f.name}: {n}")
            if args.write:
                f.write_bytes(new.encode("utf-8"))
    print(f"รวม {total} จุด" + ("" if args.write else " (ยังไม่เขียน — ใส่ --write)"))


if __name__ == "__main__":
    main()
