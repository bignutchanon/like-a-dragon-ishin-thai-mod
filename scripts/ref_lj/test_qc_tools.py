#!/usr/bin/env python3
"""เทสต์ตัวตรวจ QC สองตัวที่เพิ่มในสปรินต์สี่

`check_speaker_gender.py` (คำลงท้ายขัดเพศผู้พูด) และ `check_pair_shuffle.py` (คำแปลติดคีย์ผิด)
เคสหลอกในนี้คือเคสที่เคยทำให้ตัวตรวจรุ่นก่อนแจ้งผิดจริง — แก้ regex เมื่อไรต้องรันไฟล์นี้ให้ผ่านก่อน
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check_pair_shuffle as shuf  # noqa: E402
import check_speaker_gender as gen  # noqa: E402

CASES = []


def case(name, got, want):
    CASES.append((name, got == want, got, want))


# --- check_speaker_gender: ต้องจับได้ ---
case("ครับ = คำชาย", gen.male_markers("เปล่า ไม่คุ้นเลยครับ"), True)
case("ผม (สรรพนาม) = คำชาย", gen.male_markers("ขอผมคิดดูก่อนนะ"), True)
case("ค่ะ = คำหญิง", gen.female_markers("แน่นอนค่ะ!"), True)
case("ดิฉัน = คำหญิง", gen.female_markers("ดิฉันไม่ทราบ"), True)

# --- check_speaker_gender: ห้ามจับผิด ---
case("เส้นผม ไม่ใช่สรรพนาม", gen.male_markers("สีผมโทนเรียบ ๆ"), False)
case("ทรงผม ไม่ใช่สรรพนาม", gen.male_markers("ไม่ชอบทรงผมเดิมของฉัน"), False)
case("คะแนน ไม่ใช่คำลงท้าย", gen.female_markers("นึกว่าจะทำคะแนนได้มากกว่านี้"), False)
case("โยคะ ไม่ใช่คำลงท้าย", gen.female_markers("ครูสอนโยคะ?"), False)
case("ยกคำพูดผู้ชายมาเล่า", gen.male_markers('เขาบอก "ผมมองคุณเป็นมากกว่านั้นครับ" แล้วก็เดินจากไป'), False)

# --- check_pair_shuffle ---
case("EN คำถาม แต่ไทยไม่มีคำถาม = น่าสงสัย",
     "Q" in shuf.signals("Because you already know my answer, don't you?", "แค่หน้าตาดีก็ผ่านแล้ว"), True)
case("ไทยละ ? แต่มีคำถามไทย = ไม่จับ",
     "Q" in shuf.signals("Have you played darts before?", "เคยเล่นดาร์ทมาก่อนไหมครับ"), False)
case("ตัวเลขไม่ตรง = น่าสงสัย",
     "D" in shuf.signals("I want 10 minutes of footage.", "ขอดูภาพ 15 นาที"), True)
case("ความยาวผิดสัดส่วนมาก = น่าสงสัย",
     "L" in shuf.signals("Yeah. As long as you're not expecting perfection, there's a lot to respect.",
                         "อืม ก็ดีนะ"), True)
case("คู่ปกติ = ไม่จับอะไรเลย",
     shuf.signals("I'll be waiting at the office.", "ผมจะรออยู่ที่สำนักงานนะครับ"), [])

fail = 0
for name, ok, got, want in CASES:
    print("%-4s %-42s ได้ %r" % ("PASS" if ok else "FAIL", name, got))
    fail += 0 if ok else 1
print()
print("ผ่าน %d / %d" % (len(CASES) - fail, len(CASES)))
sys.exit(1 if fail else 0)
