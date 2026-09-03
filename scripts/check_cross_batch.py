"""เทียบคำแปลข้ามหลาย batch — จับคำที่ทีมซึ่งทำงานขนานกันตั้งชนกันเอง

ด่านรายก้อน (`merge_qc.py` · `check_translit_drift.py`) ตรวจ **ภายใน**ไฟล์เดียว จึงมองไม่เห็น
กรณีที่ batch_012 เขียน "โจรทอง" ขณะที่ batch_013 เขียน "โจรทองคำ" — ทั้งสองก้อนผ่านด่านของตัวเองสะอาด

ตรวจสองชั้น:
  ชั้น 1  คีย์ EN เดียวกันในหลายก้อน แต่คำแปลไทยไม่ตรงกัน
  ชั้น 2  คำไทยที่ต่างกันเพียงเล็กน้อยหลัง normalize (วรรณยุกต์ · จ/ช · ซ/ส · ึ/ุ · ต/ท · ค/ก · บ/ป · ะ ท้าย)
          — ชั้นนี้คือชั้นที่จับคำทับศัพท์สะกดคนละแบบได้ (เอ็จจูโด/เอ็คชูโด/เอ็ตชูโด)

ใช้:
    python scripts/check_cross_batch.py                  # ทุกไฟล์ใน translations/done/
    python scripts/check_cross_batch.py --only 012 013   # เฉพาะก้อนที่ระบุ
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DONE = Path(__file__).resolve().parent.parent / "translations" / "done"

# คู่อักษรที่คนทับศัพท์ญี่ปุ่นมักสลับกันเอง
FOLD = [("จ", "ช"), ("ซ", "ส"), ("ึ", "ุ"), ("ต", "ท"), ("ค", "ก"), ("บ", "ป")]
TONE = re.compile(r"[่้๊๋์]")
THAI_WORD = re.compile(r"[ก-๙]{4,}")


def normalize(word):
    """ยุบรูปที่ต่างกันแค่วรรณยุกต์ · คู่อักษรใกล้เคียง · ะ ท้าย"""
    word = TONE.sub("", word)
    for a, b in FOLD:
        word = word.replace(a, b)
    return word.rstrip("ะ")


def load(batches):
    out = {}
    for path in sorted(DONE.glob("batch_*.done.json")):
        # ⚠ เดิมตัด [6:9] ซึ่งใช้ได้เฉพาะชื่อก้อนตัวเลข — `batch_MSG_043.done.json`
        #   กลายเป็น "MSG" เหมือนกันหมด **ก้อน MSG ทั้งซีรีส์จึงยุบเป็นถังเดียว**
        #   คีย์ของก้อนหลังทับก้อนก่อน และเทียบข้ามก้อน MSG ด้วยกันไม่ได้เลย
        #   (ผู้ตรวจคลื่น MSG_043–045 รายงาน 3 ก.ย. 2026)
        batch = path.name[len("batch_"):-len(".done.json")]
        if batches and batch not in batches:
            continue
        out[batch] = json.loads(path.read_text(encoding="utf-8"))["strings"]
    return out


def same_key_clashes(done):
    by_key = collections.defaultdict(dict)
    for batch, strings in done.items():
        for en, th in strings.items():
            by_key[en][batch] = th
    rows = []
    for en, per_batch in by_key.items():
        if len(per_batch) > 1 and len(set(per_batch.values())) > 1:
            rows.append((en, per_batch))
    return rows


def near_miss_words(done):
    where = collections.defaultdict(set)
    for batch, strings in done.items():
        for th in strings.values():
            for word in THAI_WORD.findall(th):
                where[word].add(batch)
    groups = collections.defaultdict(list)
    for word in where:
        groups[normalize(word)].append(word)
    rows = []
    for variants in groups.values():
        if len(variants) > 1:
            rows.append(sorted((w, sorted(where[w])) for w in variants))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=None, help="เลขก้อน เช่น 012 013")
    args = ap.parse_args()

    done = load(set(args.only) if args.only else None)
    if not done:
        print("ไม่พบไฟล์ done ที่ตรงเงื่อนไข")
        return 0
    print(f"เทียบ {len(done)} ก้อน: {' '.join(sorted(done))}")

    clashes = same_key_clashes(done)
    print(f"\n[ชั้น 1] คีย์ EN เดียวกันแต่คำแปลต่างกัน: {len(clashes)} คีย์")
    for en, per_batch in clashes:
        print(f"  {en[:60]!r}")
        for batch, th in sorted(per_batch.items()):
            print(f"      {batch}  {th[:70]}")

    near = near_miss_words(done)
    print(f"\n[ชั้น 2] คำไทยที่ต่างกันเล็กน้อย: {len(near)} กลุ่ม")
    for variants in near:
        print("  " + " · ".join(f"{w} ({','.join(bs)})" for w, bs in variants))

    print("\n⚠ เป็นตัวเตือน ไม่ใช่คำตัดสิน — คำที่ต่างกันจริงก็ติดได้")
    print("   คู่ที่ตรวจแล้วว่าถูกทั้งคู่ (ไม่ต้องแก้):")
    print("     ราคุไน / ราคุไก     คนละย่าน (洛内 / 洛外)")
    print("     โกชิ / โจชิ         คนละชนชั้น (郷士 / 上士)")
    print("     เอ่อ / เอ้อ         คนละคำอุทาน (ลังเล / รับรู้)")
    print("     เฮอะ / เฮ้อ         คนละคำอุทาน (เย้ยหยัน / ถอนหายใจ)")
    print("     อะไรว— / อะไรวะ     รูปแรกเป็นบทที่ถูกขัดกลางคำโดยตั้งใจ")
    print("     กลอง / กล้อง        เครื่องดนตรี / camera")
    print("     ก่อน / ค้อน          คำบอกเวลา / hammer")
    print("     ตาที่สาม / ท่าที่สาม  Third Eye / ท่าลำดับที่สาม")
    print("   คู่ชื่อคนที่เขียนใกล้กันแต่เป็นคนละคนจริง (ห้ามไล่แก้ให้เหมือนกัน):")
    print("     Nakai/Nagai · Nakao/Nagao · Ogawa/Okawa · Ichikawa/Ishikawa")
    print("     Nakajima/Nagashima · Kawakami(025)/Kawakami(026) · Tsutsui/Suzui")
    print("     Shiba/Chiba · Joshi(上士)/Shoji · Kondo/Gondo")
    return 1 if (clashes or near) else 0


if __name__ == "__main__":
    raise SystemExit(main())
