#!/usr/bin/env python3
"""ตั้งชื่อดาบใหม่ให้ได้กลิ่นวิถีซามูไร (ผู้ใช้สั่ง 15 ก.ย. 2026) + รวมชื่อ Arms Dealer เป็น "พ่อค้าอาวุธ"

คำเคาะของผู้ใช้ (ถามด้วยตัวอย่างสามแบบ): **ผสม** —
  ดาบที่มีตัวตนจริงในประวัติศาสตร์ญี่ปุ่น = ทับศัพท์ชื่อญี่ปุ่น (แบบเดียวกับ โอนิมารุ · โดจิกิริ · เนเนกิริมารุ ที่ล็อกไว้แล้ว)
  ดาบที่เกมตั้งขึ้นเอง = ไทยขลังตามความหมายของชื่อญี่ปุ่น ขึ้นต้นด้วย "ดาบ"
ชื่อญี่ปุ่นและคำอ่านมาจากไฟล์เกม: locres ns `item_name` (ja) + คีย์ไอเทม (`item/name/hotarumaru`)
รูปสะกดทับศัพท์ยึดคำล็อกเดิม: kiri = กิริ (โดจิกิริ · เนเนกิริมารุ) · -ne/-ge = เนะ/เงะ (โอคาเนะฮิระ · อุจิชิเงะ) ·
tsu = สึ (โคการาสึมารุ) · ichimonji = อิจิโมนจิ (คิคุ อิจิโมนจิ)

การแทนที่: ทุกสตริงใน master ที่ **EN มีชื่อไอเทมตรงตัว (ตัวพิมพ์ตรง ขอบคำ)** และคำแปลมีชื่อไทยเดิม -> แทนด้วยชื่อใหม่
คำไทยเดิมบางคำเป็นคำทั่วไป (หิ่งห้อย · หยดน้ำ · แสงสวรรค์) จึงห้ามแทนที่ด้วยการค้นคำไทยอย่างเดียว
`SKIP` = สตริงที่ lead อ่านแล้วว่าไม่ได้หมายถึงดาบ

ใช้:
  python scripts/rename_swords.py            # พิมพ์ทุกสตริงที่จะเปลี่ยน ไม่เขียน
  python scripts/rename_swords.py --write    # ลง done แล้วต่อด้วย python scripts/merge_qc.py
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                      # noqa: E402
import merge_revise_wave as RW    # noqa: E402

# EN ชื่อไอเทม: (ชื่อไทยใหม่, ชื่อญี่ปุ่น, เหตุผล)
RENAME = {
    # --- ดาบจริงในประวัติศาสตร์ -> ทับศัพท์ ---
    "Firefly": ("โฮตารุมารุ", "蛍丸", "ดาบจริง (Hotarumaru)"),
    "Stonecarver": ("อิชิกิริมารุ", "石切丸", "ดาบจริง (Ishikirimaru)"),
    "Vulpecula": ("โคกิตสึเนะมารุ", "小狐丸", "ดาบจริง (Kogitsunemaru)"),
    "Close Shave": ("ฮิเงะกิริ", "髭切", "ดาบจริง (Higekiri)"),
    "Bonechewer": ("โฮเนะบามิ", "骨喰", "ดาบจริง (Honebami)"),
    "King of Beasts": ("ชิชิโอ", "獅子王", "ดาบจริง (Shishiō)"),
    "Poet Immortal": ("คาเซ็น", "歌仙", "ดาบจริง (Kasen Kanesada)"),
    "Blade of the Shogun": ("โซฮายะโนะสึรุกิ", "ソハヤノツルギ", "ดาบจริง (Sohaya-no-Tsurugi)"),
    "Dragon's Clutch": ("โคริว", "小竜", "ดาบจริง (Koryū Kagemitsu)"),
    "Suijin's Demise": ("ซุยจินกิริ", "水神切", "ดาบจริง (Suijingiri)"),
    "Eternal Gold": ("จิโยกาเนะมารุ", "千代金丸", "ดาบจริง (Chiyoganemaru)"),
    "Crane Princess": ("ฮิเมะสึรุ อิจิโมนจิ", "姫鶴一文字", "ดาบจริง (Himetsuru Ichimonji)"),
    "Thunderstop": ("ไรกิริ", "雷切", "ดาบจริง (Raikiri)"),
    # --- ดาบที่เกมตั้งเอง -> ไทยขลังตามความหมายญี่ปุ่น ---
    "Waterdrop": ("ดาบฝนพรำ", "五月雨", "ฝนต้นฤดูร้อน"),
    "Legion Slayer": ("ดาบพิฆาตพันคน", "千人切", "ฟันพันคน"),
    "Dragon Slayer": ("ดาบมังกรฟ้า", "天龍神馬", "มังกรฟ้าอาชาเทพ"),
    "Bloody Sheen": ("ดาบโลหิตพราย", "艶薄紅", "แดงระเรื่อวาววับ + คำอธิบายเลือดหยดตลอด"),
    "Blossoming Bud": ("ดาบบุปผาบาน", "花盛", "ดอกไม้บานสะพรั่ง"),
    "Last of the Dragons": ("ดาบทลายมังกร", "夢龍砕", "บดขยี้มังกรในฝัน"),
    "Light of Heaven": ("ดาบแสงสวรรค์", "天光丸", "แสงสวรรค์"),
    "Handy Blade": ("ดาบสายลมสน", "松風", "ลมพัดผ่านสน"),
    "Exorcism Greatsword": ("โอดาจิยางิว", "柳生大太刀", "โอดาจิสำนักยางิว"),
    "Centered Odachi": ("ดาบโอดาจินากามากิ", "中巻野太刀", "นากามากิโนดาจิ (ด้ามพันกลางใบ)"),
    "Snowcap": ("ดาบหิมะโปรยปราย", "細雪", "หิมะละเอียด"),
    "Radiant Drunkard": ("ดาบสุราเรืองรอง", "輝上文字", "ล้อ 一文字 · คำอธิบายพลังตอนเมา"),
    "Celestial Steed": ("ดาบแสงตะวัน", "陽光", "แสงอาทิตย์ (คำแปลเดิม อาชาสวรรค์ ไม่ตรงชื่อญี่ปุ่น)"),
    "Elegance": ("ดาบสง่างาม", "雅丸", "ความสง่า"),
    "Ivory Sword": ("ดาบประกายขาว", "白刃丸", "ใบดาบขาว (คำแปลเดิม งาช้าง ไม่ตรงชื่อญี่ปุ่น)"),
    "Ebony Sword": ("ดาบเหล็กดำ", "黒鉄丸", "เหล็กดำ"),
    "Tideturner": ("ดาบพลิกฟ้า", "回天丸", "回天 = พลิกฟ้าเปลี่ยนยุค"),
    "Morning Gale": ("ดาบพายุรุ่งอรุณ", "朝嵐", "พายุยามเช้า"),
    "Sakura Storm": ("ดาบพายุซากุระ", "桜吹雪", "ซากุระปลิวว่อน"),
}

# EN: เหตุผลที่ไม่แตะ (เติมหลังอ่านผล dry-run)
SKIP = {}

# สตริงรูปแปรที่คำแปลเดิมไม่ได้ใช้ชื่อไทยเดียวกับชื่อไอเทม (dry-run 15 ก.ย. 2026) — EN: คำแปลใหม่ทั้งสตริง
EXTRA = {
    "Bonechewer Katana": "คาตานะโฮเนะบามิ",
    "Snowcap Katana": "คาตานะหิมะโปรยปราย",
    # ชุดไอเทม DLC เรียก Bloody Sheen ว่า "เงาเลือด" ไม่ตรงชื่อไอเทม
    "This kit contains the Black Ship Cannon as well as two katanas, the Kijin-maru Kunishige and Bloody Sheen.":
        "ชุดนี้บรรจุปืนใหญ่เรือดำ พร้อมดาบคาตานะสองเล่ม คือคิจินมารุ คุนิชิเงะ และดาบโลหิตพราย",
}


def swap_name(th, old, new):
    """แทนชื่อเดิม — ถ้าหน้าชื่อมีคำเรียกชนิดอาวุธอยู่แล้ว (คาตานะ) ไม่ต้องมี "ดาบ" ซ้อน
    เจอจริง: "Waterdrop Katana" = "คาตานะหยดน้ำ" -> ต้องเป็น "คาตานะฝนพรำ" ไม่ใช่ "คาตานะดาบฝนพรำ" """
    bare = new[len("ดาบ"):] if new.startswith("ดาบ") and len(new) > len("ดาบ") + 1 else new
    th = th.replace("คาตานะ" + old, "คาตานะ" + bare)
    return th.replace(old, new)

ARMS = {"Arms Dealer": "พ่อค้าอาวุธ"}
ARMS_SWAP = ("เจ้าของร้านอาวุธ", "พ่อค้าอาวุธ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    master = json.loads(paths.MASTER_TH.read_text(encoding="utf-8"))
    changes = {}
    missing = []
    for en_name, (new, ja, why) in RENAME.items():
        old = master.get(en_name)
        if not old:
            missing.append(en_name)
            continue
        pat = re.compile(r"(?<![A-Za-z])%s(?![A-Za-z])" % re.escape(en_name))
        hits = 0
        for en, th in master.items():
            if en in SKIP or not pat.search(en):
                continue
            cur = changes.get(en, th)
            if old in cur:
                changes[en] = swap_name(cur, old, new)
                hits += 1
            elif en != en_name:
                print("   ? %s: EN มีชื่อแต่คำแปลไม่มี '%s' — %s => %s" % (en_name, old, en[:70], cur[:70]))
        print("%-22s %s  %s -> %s  (%d สตริง)" % (en_name, ja, old, new, hits))
    for en, th in master.items():
        if "Arms Dealer" in en and ARMS_SWAP[0] in th:
            changes[en] = changes.get(en, th).replace(*ARMS_SWAP)
    for en, new in list(ARMS.items()) + list(EXTRA.items()):
        if en not in master:
            missing.append(en)
        elif master.get(en) != new:
            changes[en] = new

    print("\n=== สตริงที่จะเปลี่ยน %d ===" % len(changes))
    for en, new in changes.items():
        print("- EN: %s\n  เดิม: %s\n  ใหม่: %s" % (en.replace("\n", " / ")[:120],
                                                  master[en].replace("\n", " / ")[:160],
                                                  new.replace("\n", " / ")[:160]))
    if missing:
        print("!! ไม่พบใน master: %s" % missing)
    if args.write:
        nf, nk = RW.apply_to_done(changes)
        print("ลง done %d ไฟล์ · %d คีย์ -> ต่อด้วย python scripts/merge_qc.py" % (nf, nk))


if __name__ == "__main__":
    main()
