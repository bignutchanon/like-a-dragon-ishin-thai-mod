#!/usr/bin/env python3
"""จับ "คำทับศัพท์ที่สะกดเพี้ยนกันเอง" ในคลังคำแปล — เช่น ชิเออิกัน กับ ชิเออิกัง

ทำไมต้องมี (2 ก.ย. 2026): ภาคนี้เต็มไปด้วยชื่อญี่ปุ่นที่ต้องทับศัพท์ (คน · สำนัก · ย่าน · สายวิชา)
คำเดียวกันจึงสะกดคนละแบบได้ง่ายมากเมื่อมีหลายคนแปล และ `check_glossary_locks.py` จับได้เฉพาะคำ
ที่ถูกล็อกไว้แล้ว **แต่คำที่ยังไม่ได้ล็อกจะเพี้ยนเงียบ ๆ** — รอบ batch_003 เจอ "ชิเออิกัน/ชิเออิกัง"
อยู่ในไฟล์เดียวกันโดยไม่มีด่านไหนเห็น (lead จับได้เพราะบังเอิญ)

วิธีตรวจ: หาคำไทยที่ **ต่างกันแค่ตัวอักษรเดียว** (แทรก/ลบ/แทนที่) แล้วรายงานคู่ที่ความถี่
ต่างกันมาก — รูปที่พบน้อยกว่ามากมักเป็นตัวที่พิมพ์เพี้ยน

⚠ เป็น **ตัวเตือน ไม่ใช่ตัวตัดสิน** — ภาษาไทยมีคู่คำที่ต่างกันตัวเดียวโดยชอบธรรมเยอะ
(กัน/กับ · ท่าน/ท่า) ตัวกรองความยาวและอัตราส่วนความถี่ช่วยได้ระดับหนึ่งเท่านั้น

ใช้:
  python scripts/check_translit_drift.py                 # ตรวจ master_th + ไฟล์ done ทั้งหมด
  python scripts/check_translit_drift.py --only 003      # เฉพาะ batch เดียว
  python scripts/check_translit_drift.py --min-len 6 --ratio 5
"""
import argparse
import collections
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

sys.stdout.reconfigure(encoding="utf-8")

THAI_WORD = re.compile(r"[ก-ฮะ-๎]{3,}")
# คำไทยธรรมดาที่ยาวพอจะหลุดตัวกรอง และมีคู่ต่างตัวเดียวโดยชอบธรรม — ข้ามไปเลย
COMMON = {
    "เหมือนกัน", "เหมือนกับ", "ด้วยกัน", "ด้วยกับ", "อย่างไร", "อย่างนั้น", "อย่างนี้",
    "ตัวเอง", "ตัวเอย", "เท่านั้น", "เท่านี้", "ทั้งหมด", "ทั้งหลาย", "ครั้งนี้", "ครั้งนั้น",
    "เรื่องนี้", "เรื่องนั้น", "คนนี้", "คนนั้น", "ที่นี่", "ที่นั่น", "แบบนี้", "แบบนั้น",
}


def levenshtein_le1(a, b):
    """คืน True ถ้าระยะแก้ไข <= 1 (เขียนเองเพื่อไม่ต้องพึ่งไลบรารีนอก)"""
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        diff = sum(1 for x, y in zip(a, b) if x != y)
        return diff <= 1
    if la > lb:
        a, b, la, lb = b, a, lb, la
    i = j = 0
    skipped = False
    while i < la and j < lb:
        if a[i] == b[j]:
            i += 1
            j += 1
            continue
        if skipped:
            return False
        skipped = True
        j += 1
    return True


def collect(only=None):
    """คืน Counter ของคำไทย พร้อม {คำ: ตัวอย่างบรรทัด}"""
    words = collections.Counter()
    sample = {}

    def eat(text, where):
        for w in THAI_WORD.findall(text):
            words[w] += 1
            sample.setdefault(w, where)

    files = []
    done_dir = paths.TRANSLATIONS / "done"
    if done_dir.exists():
        files = sorted(done_dir.glob("batch_*.done.json"))
        if only:
            files = [f for f in files if only in f.name]
    for f in files:
        st = json.load(io.open(f, encoding="utf-8"))["strings"]
        for v in st.values():
            if isinstance(v, str):
                eat(v, f.name)
    if not only and paths.MASTER_TH.exists():
        master = json.load(io.open(paths.MASTER_TH, encoding="utf-8"))
        for v in master.values():
            if isinstance(v, str):
                eat(v, "master_th.json")
    return words, sample


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="เลข batch เช่น 003")
    ap.add_argument("--min-len", type=int, default=5,
                    help="ความยาวคำขั้นต่ำที่จะตรวจ (สั้นกว่านี้ชนคำไทยปกติเยอะ)")
    ap.add_argument("--ratio", type=float, default=3.0,
                    help="รายงานเมื่อความถี่ต่างกันตั้งแต่กี่เท่า (รูปที่น้อยกว่ามัก = พิมพ์เพี้ยน)")
    ap.add_argument("--max", type=int, default=40)
    a = ap.parse_args()

    words, sample = collect(a.only)
    cand = [w for w, n in words.items()
            if len(w) >= a.min_len and w not in COMMON]
    # จัดกลุ่มด้วยความยาวใกล้กัน + อักษรตัวแรก เพื่อไม่ต้องเทียบทุกคู่
    buckets = collections.defaultdict(list)
    for w in cand:
        buckets[(w[0], len(w))].append(w)
        buckets[(w[0], len(w) + 1)].append(w)

    seen, pairs = set(), []
    for group in buckets.values():
        for i, x in enumerate(group):
            for y in group[i + 1:]:
                if x == y or (x, y) in seen or (y, x) in seen:
                    continue
                seen.add((x, y))
                if not levenshtein_le1(x, y):
                    continue
                nx, ny = words[x], words[y]
                hi, lo = (x, y) if nx >= ny else (y, x)
                nhi, nlo = max(nx, ny), min(nx, ny)
                if nhi < a.ratio * nlo:
                    continue
                pairs.append((nhi, nlo, hi, lo))

    pairs.sort(key=lambda p: (-p[0], p[3]))
    if not pairs:
        print("ไม่พบคำที่น่าจะสะกดเพี้ยนกันเอง (ตรวจคำไทยไม่ซ้ำ %d คำ)" % len(cand))
        return 0
    print("คู่คำที่น่าสงสัยว่าสะกดเพี้ยน %d คู่ (ตรวจคำไทยไม่ซ้ำ %d คำ)" % (len(pairs), len(cand)))
    for nhi, nlo, hi, lo in pairs[:a.max]:
        print("  %-22s %4d ครั้ง   <->   %-22s %4d ครั้ง   (%s)"
              % (hi, nhi, lo, nlo, sample.get(lo, "-")))
    print("\n⚠ ตัวเตือน ไม่ใช่คำตัดสิน — คู่คำไทยปกติที่ต่างกันตัวเดียวก็ติดมาได้")
    return 1


if __name__ == "__main__":
    sys.exit(main())
