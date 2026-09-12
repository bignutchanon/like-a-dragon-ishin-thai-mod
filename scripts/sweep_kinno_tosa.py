#!/usr/bin/env python3
r"""เปลี่ยนชื่อพรรค 土佐勤王党 เป็น "พรรคกินโนโทซะ" และทับศัพท์ 土佐 เป็น "โทซะ" ทั้งคลัง

ที่มา (ผู้ใช้รายงาน 11 ก.ย. 2026): "พรรคจงรักภักดีโทสะ" อ่านแล้วสะดุด เพราะคำว่า "โทสะ"
ซึ่งเป็นทับศัพท์ของแคว้น 土佐 ไปต่อท้าย "ภักดี" พอดี กลายเป็น "ภักดี + โทสะ (ความโกรธ)"
ชื่อพรรคเดิมยังยาวด้วย (18 ตัวอักษร) ทำให้ป้ายผู้พูดและบรรทัดที่อ้างถึงพรรคยาวเกินจำเป็น

สองอย่างที่เปลี่ยน (ผู้ใช้เคาะ 11 ก.ย. 2026):
  1. ทับศัพท์ 土佐 = "โทซะ" (さ = ซะ ตามหลักถอดเสียงญี่ปุ่น) แทน "โทสะ" ที่ชนคำไทยแปลว่าความโกรธ
  2. ชื่อพรรคใช้ทับศัพท์ 勤王 = "กินโน" (Kinnō) แทนการแปลความว่า "จงรักภักดี"
     เข้าชุดกับ ชิชิ · โกชิ · โจชิ ที่ทับศัพท์อยู่แล้ว และสั้นกว่าเดิม 5 ตัวอักษร
     คำอธิบายศัพท์ในเกม (สารานุกรม) ยังบอกความหมาย "จงรักภักดีต่อองค์จักรพรรดิ" ไว้ครบ

คำว่า "จงรักภักดี" ที่เป็น**คำสามัญ** (ความจงรักภักดี · จงรักภักดีต่อโชกุน/แผ่นดิน ·
สาบานตนจงรักภักดี) ไม่แตะ — เปลี่ยนเฉพาะที่เป็น**ชื่อกลุ่ม** (พรรค/ฝ่าย/พวก/กลุ่ม/ชิชิ + จงรักภักดี)

ข้อยกเว้นที่ตรวจแล้วไม่แก้: บรรทัด "white-hot temper" ใช้คำว่า "โทสะ" ในความหมายความโกรธจริง ๆ
(กวาดทั้งคลังแล้วมีบรรทัดเดียว — คีย์อยู่ใน KEEP_ANGER)

ระหว่างคำอาจมีช่องว่างที่ `fix_thai_wrap.py` แทรกไว้ตอนขอบคำ จึงจับด้วย `\s*` แล้วเขียนคืนแบบติดกัน
(สั้นลงอยู่แล้ว ถ้าจุดตัดบรรทัดยังไม่พอให้รัน `fix_thai_wrap.py` ตามหลัง)

ใช้:
  python scripts/sweep_kinno_tosa.py --check    # ดูว่าจะแก้อะไรบ้าง ไม่เขียนไฟล์
  python scripts/sweep_kinno_tosa.py            # เขียนลง translations/done/*.done.json
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

# บรรทัดที่ "โทสะ" = ความโกรธ ไม่ใช่ชื่อแคว้น (กวาดทั้งคลังแล้วมีเท่านี้)
KEEP_ANGER = {
    "I'm afraid so. I told you, he's strict, with a white-hot temper to boot... "
    "Such is why no one makes him food anymore. Everyone is much too terrified.",
}

# ชื่อกลุ่ม -> ทับศัพท์ (เรียงยาวไปสั้น · \s* รองรับช่องว่างขอบคำที่ fix_thai_wrap แทรกไว้)
GROUP_RULES = [
    (re.compile(r"พรรค\s*จงรักภักดี\s*โทสะ"), "พรรคกินโนโทซะ"),
    (re.compile(r"พรรค\s*จงรักภักดี"), "พรรคกินโน"),
    (re.compile(r"ฝ่าย\s*จงรักภักดี"), "ฝ่ายกินโน"),
    (re.compile(r"ชิชิ\s*ผู้\s*จงรักภักดี"), "ชิชิฝ่ายกินโน"),
    (re.compile(r"ชิชิ\s*จงรักภักดี"), "ชิชิฝ่ายกินโน"),
    (re.compile(r"พวก\s*จงรักภักดี"), "พวกกินโน"),
    (re.compile(r"กลุ่ม\s*จงรักภักดี"), "กลุ่มกินโน"),
    (re.compile(r"แคว้น\s*จงรักภักดี"), "แคว้นฝ่ายกินโน"),
    (re.compile(r'"จงรักภักดี"\s*คือ'), '"กินโน" คือ'),
]

# ป้ายศัพท์เดี่ยวในสารานุกรม — คีย์ EN -> คำแปลใหม่ทั้งช่อง
TERM_KEYS = {
    "Loyalist": "กินโน",
    "Loyalist Shishi": "ชิชิฝ่ายกินโน",
}

TOSA = re.compile(r"โทสะ")


def convert(key, text):
    out = text
    if key in TERM_KEYS:
        return TERM_KEYS[key]
    for pat, rep in GROUP_RULES:
        out = pat.sub(rep, out)
    if key not in KEEP_ANGER:
        out = TOSA.sub("โทซะ", out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="ไม่เขียนไฟล์ แสดงผลอย่างเดียว")
    args = ap.parse_args()

    total_keys = 0
    total_files = 0
    samples = []
    for path in sorted(DONE.glob("*.done.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        strings = data["strings"] if isinstance(data, dict) and "strings" in data else data
        n = 0
        for key, val in strings.items():
            if not isinstance(val, str):
                continue
            new = convert(key, val)
            if new != val:
                strings[key] = new
                n += 1
                if len(samples) < 12:
                    samples.append((path.name, val, new))
        if n:
            total_keys += n
            total_files += 1
            if not args.check:
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
            print(f"{path.name:28s} {n:4d} คีย์")

    print(f"\nรวม {total_keys} คีย์ · {total_files} ไฟล์" + ("  (ตรวจอย่างเดียว)" if args.check else "  (เขียนแล้ว)"))
    print("\nตัวอย่าง:")
    for name, old, new in samples:
        print(f"  [{name}]")
        print(f"    เดิม: {old[:90]}")
        print(f"    ใหม่: {new[:90]}")


if __name__ == "__main__":
    main()
