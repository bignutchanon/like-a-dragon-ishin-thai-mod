#!/usr/bin/env python3
"""แก้ชื่อดาบ "-丸" สามเล่มที่แปลตรงตัวจนไม่เหมือนดาบ (ผู้ใช้รายงาน 15 ก.ย. 2026)

ภาพผู้ใช้: ตัวเลือก "เอาจิ้งเหลนให้ดู / เอาไชเท้าให้ดู" ในฉากชายขอชมดาบ อ่านแล้วไม่รู้ว่าเป็นดาบ
และหาในช่องอุปกรณ์ไม่เจอ

หลักฐานจาก locres (`extracted/parallel/locres.json` ns `item_name`):
  item/name/daikonnmaru  The Radish     大根丸   -> เดิม "ไชเท้า" ชนกับผัก `farm_daikon` Daikon 大根 ที่เป็น "ไชเท้า" เหมือนกัน
  item/name/tokagemaru   Skink Lizard   蜥蜴丸   -> เดิม "จิ้งเหลน" · บทบาคุมัตสึบ็อบยังเรียก "ดาบมนตร์โทคาเงะมารุ" อีกแบบ
  item/name/yashamaru    Yaksha Blade   夜叉丸   -> "ดาบยักษา" ถูกอยู่แล้ว
ใช้รูปเดียวกับ `konnnyakumaru` Jelly Blade 蒟蒻丸 = "ดาบบุก" (นำหน้าด้วย ดาบ)

แก้ใน done ทุกไฟล์ที่มีสตริงนี้ แล้วรัน `python scripts/merge_qc.py` ต่อ (กติกาเหล็กข้อ 4)
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import merge_revise_wave as RW    # noqa: E402

BOB = ("It's Bakumatsu Bob—we're on first name terms by now, I think. Anyway, sixth heavenly gift coming "
       "your way. It's the Skink Lizard & Practical Enhancing Materials Pack. Teradaya's kitchen sound good?")

FIX = {
    "The Radish": "ดาบไชเท้า",
    "Skink Lizard": "ดาบจิ้งเหลน",
    "Show him The Radish": "เอาดาบไชเท้าให้ดู",
    "Show him the Skink Lizard": "เอาดาบจิ้งเหลนให้ดู",
    "You got the <Color:8>Skink Lizard<Color:Default>.": "ได้รับ <Color:8>ดาบจิ้งเหลน<Color:Default>",
    # "ดาบ...เรอะ... ดาบดีนี่" ซ้ำคำ -> "ของดีนี่" ทั้งสามเล่มให้เข้าชุดกัน
    "The Radish, huh... a nice sword.": "ดาบไชเท้าเรอะ... ของดีนี่",
    "The Skink Lizard, huh... a nice sword.": "ดาบจิ้งเหลนเรอะ... ของดีนี่",
    "The Yaksha Blade, huh... a nice sword.": "ดาบยักษาเรอะ... ของดีนี่",
    BOB: ("ข้าอุตสึโนมิยะ ป่านนี้คงสนิทกันจนเรียกชื่อจริงได้แล้วมั้ง เอาล่ะ ของขวัญจากสวรรค์ชุดที่หกกำลังมาหาเจ้า "
          "เป็นดาบจิ้งเหลนกับชุดวัตถุดิบเสริมพลังใช้งานจริง ที่ครัวเทราดายะดีไหมล่ะ"),
}

if __name__ == "__main__":
    nf, nk = RW.apply_to_done(FIX)
    print("ลง done %d ไฟล์ · %d คีย์ (%d สตริง)" % (nf, nk, len(FIX)))
    print("ต่อด้วย: python scripts/merge_qc.py")
