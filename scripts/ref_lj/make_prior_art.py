#!/usr/bin/env python3
"""ดัชนี "ของเดิมที่เคยแปลไปแล้ว" สำหรับ batch ที่เป็นชื่อไอเทม/ชื่อร้าน/ชื่อคน

ทำไมต้องมี (26 ส.ค. 2026 · sprint 15):
batch 119-130 เป็น `item.bin` / `evidence.bin` / `complete.bin` = **ดัชนีของทุกอย่างที่บทพูด
พูดถึงมาแล้ว** วัดกับไฟล์จริงพบว่า **ไม่มีคีย์ไหนซ้ำกับ master_th ตรง ๆ เลย (0/3,000)**
แต่ชื่อพวกนี้โผล่ **อยู่ข้างในประโยค** ที่แปลไปแล้วเต็มไปหมด — เช่น ชื่อร้านในบทพูดของ NPC
ถ้านักแปลไม่เห็นของเดิม ผู้เล่นจะเจอสองคำสำหรับของชิ้นเดียวกันบนจอเดียวกัน

`find_term.py` ตอบทีละคำ (คนถาม) · ไฟล์นี้กวาดทั้ง batch ให้ล่วงหน้า (เครื่องถาม)

ใช้:
  python scripts/make_prior_art.py 119 130          # ช่วง batch
  python scripts/make_prior_art.py 127 127 --max 6  # จำกัดตัวอย่างต่อคีย์
ผลลัพธ์: translations/worklist/batch_NNN.priorart.json
  { "<คีย์ EN ของ batch>": [ {"en": "<ประโยคที่ ship แล้ว>", "th": "<คำแปล>"} , ... ] }
"""
import argparse
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

sys.stdout.reconfigure(encoding="utf-8")

WL = os.path.join(paths.PROJECT, "translations", "worklist")
MASTER = os.path.join(paths.PROJECT, "translations", "master_th.json")

# คีย์ที่สั้นเกินไปจะแมตช์มั่ว ("Bar" อยู่ใน "Barber") — ต้องยาวพอและมีตัวอักษรจริง
MIN_LEN = 5
MAX_LEN = 45
WORD = re.compile(r"[A-Za-z]")


def batch_range(first, last):
    """คืนรายชื่อ id ของ batch ตั้งแต่ first ถึง last

    รองรับสองรูปแบบ: เลขล้วน ("191" -> batch_191) และคิว TALK ("TALK_001" -> batch_TALK_001)
    (เพิ่ม 28 ส.ค. 2026 · sprint 22 — ก่อนหน้านี้รับเฉพาะ int ทำให้ใช้กับคิว TALK ไม่ได้เลย)
    """
    f, l = str(first).upper(), str(last).upper()
    pre = ""
    if f.startswith("TALK_") or l.startswith("TALK_"):
        if not (f.startswith("TALK_") and l.startswith("TALK_")):
            raise SystemExit("first/last ต้องเป็นชนิดเดียวกัน (เลขล้วน หรือ TALK_NNN ทั้งคู่)")
        pre, f, l = "TALK_", f[5:], l[5:]
    return ["%s%03d" % (pre, i) for i in range(int(f), int(l) + 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("first", help="เลข batch หรือ TALK_NNN")
    ap.add_argument("last", help="เลข batch หรือ TALK_NNN")
    ap.add_argument("--max", type=int, default=4, help="ตัวอย่างสูงสุดต่อคีย์")
    a = ap.parse_args()

    with io.open(MASTER, encoding="utf-8") as f:
        master = json.load(f)
    # เรียงประโยคสั้นก่อน — ประโยคสั้นให้บริบทชัดกว่าและอ่านง่ายกว่า
    items = sorted(master.items(), key=lambda kv: len(kv[0]))

    for n in batch_range(a.first, a.last):
        src = os.path.join(WL, "batch_%s.json" % n)
        if not os.path.exists(src):
            continue
        with io.open(src, encoding="utf-8") as f:
            batch = json.load(f)
        out = {}
        for key in batch["strings"]:
            if not (MIN_LEN <= len(key) <= MAX_LEN) or not WORD.search(key):
                continue
            # แมตช์แบบไม่สนตัวพิมพ์ แต่ต้องเป็นคำเต็ม (กัน "Bar" ใน "Barber")
            pat = re.compile(r"(?<![A-Za-z])" + re.escape(key) + r"(?![A-Za-z])", re.I)
            hits = []
            for en, th in items:
                if en == key or len(en) < len(key):
                    continue
                if pat.search(en):
                    hits.append({"en": en, "th": th})
                    if len(hits) >= a.max:
                        break
            if hits:
                out[key] = hits
        dst = os.path.join(WL, "batch_%s.priorart.json" % n)
        with io.open(dst, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print("batch_%s: คีย์ที่เคยโผล่ในของที่ ship แล้ว %d/%d -> %s"
              % (n, len(out), len(batch["strings"]), os.path.basename(dst)))


if __name__ == "__main__":
    main()
