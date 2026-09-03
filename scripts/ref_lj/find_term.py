#!/usr/bin/env python3
"""ค้นคำ EN ว่าเคยถูกแปลเป็นไทยว่าอย่างไรมาก่อน — ในโปรเจกต์นี้ **และในโปรเจกต์พี่น้อง**

ทำไมต้องมี (เคาะ 26 ส.ค. 2026 · sprint 10):
กติกาเดิมบอกให้ "นับ master_th ของ LJ ก่อนเสนอคำใหม่" ซึ่งจับ lead ผิดได้ 5 ครั้งใน session เดียว
แต่มันมองไม่เห็นคำที่ **ภาคอื่น ship ไปแล้วและ LJ ยังไม่เคยเจอ** — ผู้ตรวจ batch_074 เสนอทับศัพท์
`Ijin Three` เพราะนับใน LJ ได้ 0 จุด ทั้งที่ Y8 ล็อกคำไทยไว้แล้ว เขาทำถูกตามกติกาที่มี
กติกาต่างหากที่แคบไป · sprint นี้เจอคำล็อกข้ามภาคแบบนี้รวม 5 คำ
(`Shintani` · `Queen Rouge` · `mahjong` · `Earth Angel` · `Ijin Three`)

ลำดับความสำคัญของคำตอบ (บนสุดชนะ):
  1. `master_th.json` ของ LJ  — คำที่ ship ไปแล้วในภาคนี้ ชนะทุกอย่าง
  2. `glossary.md` ของ LJ     — คำที่ lead เคาะไว้แล้ว
  3. Judgment (ภาคแรก)        — ซีรีส์เดียวกัน ตัวละคร/ร้านค้าใช้ต่อกันตรง ๆ
  4. K3 > Gaiden > Y8 > Y7 > Pirate > K2R  (ใหม่กว่าชนะ ตาม CLAUDE.md)

ใช้:
  python scripts/find_term.py "Ijin Three"
  python scripts/find_term.py "mahjong" --max 5      # จำกัดตัวอย่างต่อโปรเจกต์
  python scripts/find_term.py "Queen Rouge" --lj-only
"""
import argparse
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

# ⚠ รายชื่อโฟลเดอร์ภาคพี่น้องอยู่ที่ `paths.SIBLINGS` ที่เดียว (รวมมา 26 ส.ค. 2026 · sprint 16)
# ⚠⚠ **ลำดับที่สคริปต์นี้พิมพ์ออกมา (Judgment ก่อน) ไม่ใช่ลำดับเดียวของโปรเจกต์**
#    26 ส.ค. 2026 (sprint 16) เคาะกฎ **I10** ว่าลำดับอำนาจมีสองสาย:
#      · ของซีรีส์ Judgment โดยเฉพาะ (ตัวละคร องค์กร ระบบเฉพาะภาค คู่มือที่ข้อความซ้ำกันทั้งดุ้น) -> Judgment ก่อน
#      · ของโลก RGG ที่ใช้ร่วมกัน (ชื่อถนน/ย่าน ร้านเชน อาหาร ไอเทมทั่วไป) -> K3 > Gaiden > Y8 > Y7 > Pirate > K2R
#      · คำที่เป็นการทับศัพท์ล้วน -> การอ่าน romaji ที่ถูกต้องชนะทุกภาค
#    รายละเอียดและตัวอย่างที่เคาะไปแล้ว: `translations/review/sprint16_locks.md` §5.19
# (ชื่อที่แสดง, master_th, glossary) — เรียงตามลำดับความสำคัญ · เตือนดัง ๆ ถ้าโฟลเดอร์ไหนหาย
SIBLINGS = paths.sibling_paths()
_cache = {}


def load_json(path):
    if path not in _cache:
        try:
            with io.open(path, encoding="utf-8") as f:
                _cache[path] = json.load(f)
        except Exception:
            _cache[path] = {}
    return _cache[path]


def load_text(path):
    if path not in _cache:
        try:
            with io.open(path, encoding="utf-8") as f:
                _cache[path] = f.read()
        except Exception:
            _cache[path] = ""
    return _cache[path]


def scan_master(data, rx, cap):
    """คืน (จำนวนคีย์ที่ตรง, ตัวอย่าง [(en, th)])"""
    hits, ex = 0, []
    for k, v in data.items():
        if rx.search(k):
            hits += 1
            if len(ex) < cap:
                ex.append((k, v))
    return hits, ex


def scan_glossary(text, rx, cap):
    return [ln.strip() for ln in text.splitlines() if rx.search(ln)][:cap]


def report(label, master_path, gloss_path, rx, cap):
    n, ex = scan_master(load_json(master_path), rx, cap)
    g = scan_glossary(load_text(gloss_path), rx, cap)
    if not n and not g:
        return False
    print("")
    print("== %s ==" % label)
    if g:
        print("  glossary:")
        for ln in g:
            print("    %s" % ln[:160])
    if n:
        print("  master_th: %d คีย์" % n)
        for k, v in ex:
            print("    EN: %s" % k[:110])
            print("    TH: %s" % v[:110])
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("term", help="คำ EN ที่จะค้น (ไม่สนตัวพิมพ์ใหญ่-เล็ก)")
    ap.add_argument("--max", type=int, default=3, help="ตัวอย่างสูงสุดต่อโปรเจกต์ (ค่าตั้งต้น 3)")
    ap.add_argument("--lj-only", action="store_true", help="ค้นเฉพาะ Lost Judgment")
    a = ap.parse_args()

    rx = re.compile(re.escape(a.term), re.I)
    print('ค้น "%s"' % a.term)

    found_lj = report("Lost Judgment (ภาคนี้ — ชนะทุกอย่าง)",
                      str(paths.MASTER_TH), str(paths.TRANSLATIONS / "glossary.md"), rx, a.max)
    # tm_judgment คือ TM ของภาคแรกที่ import เข้ามาแล้ว — อยู่ใน repo นี้แต่เป็นของภาคแรก
    n, ex = scan_master(load_json(str(paths.TRANSLATIONS / "tm_judgment.json")), rx, a.max)
    if n:
        print("")
        print("== tm_judgment.json (TM ภาคแรกที่ import มา) ==")
        print("  %d คีย์" % n)
        for k, v in ex:
            print("    EN: %s" % k[:110])
            print("    TH: %s" % v[:110])

    found_sib = False
    if not a.lj_only:
        for label, m, g in SIBLINGS:
            found_sib |= report(label, m, g, rx, a.max)

    print("")
    if not found_lj and not n and not found_sib:
        print("ไม่พบที่ไหนเลย → เป็นคำใหม่จริง เสนอคำไทยมาให้ lead เคาะได้")
    elif not found_lj:
        print("⚠ LJ ยังไม่เคยใช้คำนี้ แต่ **ภาคอื่นใช้ไปแล้ว** — ต้องใช้ตาม ห้ามตั้งคำใหม่ทับ")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
