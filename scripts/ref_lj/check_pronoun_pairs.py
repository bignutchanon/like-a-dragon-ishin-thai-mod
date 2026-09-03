#!/usr/bin/env python3
"""ตรวจว่าคำแปลไทยใช้สรรพนาม "จับคู่" ถูกระดับตาม PRONOUN_MATRIX §0

ระบบที่ผู้ใช้สั่งไว้ (20 ส.ค. 2026):
  T1 สุภาพ : ผม / ดิฉัน  <->  คุณ            (คำลงท้าย ครับ/ค่ะ)
  T2 กันเอง: ฉัน         <->  แก             (ว่ะ/นะ/เหรอ/สิ)
  T3 หยาบ  : กู          <->  มึง            (โว้ย/เว้ย/ว่ะ)

ผิดคือ "ผสมข้ามระดับในประโยคเดียว" เช่น «ผม...มึง» หรือ «กู...คุณ» — ตัวตรวจนี้จับให้อัตโนมัติ
เพราะพอแปลจริงหลายหมื่นบรรทัดโดยหลายคน การผสมข้ามระดับจะหลุดแน่ถ้าไม่มีตัวจับ

ใช้:
  python scripts/check_pronoun_pairs.py                       # ตรวจ translations/master_th.json (ถ้ามี)
  python scripts/check_pronoun_pairs.py --files translations/characters_main.json translations/PRONOUN_MATRIX.md
  python scripts/check_pronoun_pairs.py --max 50              # จำกัดจำนวนที่พิมพ์
"""
import argparse
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

# คำแทนตัวเอง / คำเรียกคู่สนทนา แยกตามระดับ
# คำเดียวอาจอยู่ได้หลายระดับ — "ฉัน" เป็นได้ทั้ง T1 (หญิง โทนกลาง ๆ ตาม §0 แถวแรก) และ T2
# ดังนั้นเก็บเป็น "ชุดระดับที่เป็นไปได้" แล้วตัดสินว่าผิดก็ต่อเมื่อ **ไม่มีระดับไหนใช้ร่วมกันได้เลย**
# (ก่อน 21 ส.ค. 2026 เคยล็อก ฉัน = T2 อย่างเดียว ทำให้ "ฉัน...คุณ" ของตัวละครหญิงตก QC เท็จ
#  ผู้ตรวจ batch_050/051 ต้องไปดัด "ดิฉัน" หรือตัด "คุณ" ทิ้งเพื่อให้ผ่าน — บิดคำแปลเพราะเครื่องมือผิด)
SELF = {"ผม": {"T1"}, "ดิฉัน": {"T1"}, "ฉัน": {"T1", "T2"}, "กู": {"T3"}}
OTHER = {"คุณ": {"T1"}, "นาย": {"T1", "T2"}, "แก": {"T2"}, "มึง": {"T3"}}
# คำที่ไม่นับในกฎ "คำเรียกอีกฝ่ายหลายคำในบรรทัดเดียว" — ใช้ตรวจเฉพาะการผสมข้ามระดับ
# "นาย" อยู่ได้ทั้ง T1 และ T2 (ยากามิใช้ "คุณ/นาย" สลับกันได้ในบทเดียว) และคำอย่าง
# "คุณนักสืบ" เป็นฉายาที่ล็อกไว้ ไม่ใช่สรรพนาม — ถ้านับรวมจะเตือนเท็จ 5 จาก 7 จุด
MULTI_EXEMPT = {"นาย"}
ENDINGS = {"T1": ["ครับ", "ค่ะ", "คะ"], "T3": ["โว้ย", "เว้ย"]}

# ภาษาไทยไม่เว้นวรรคระหว่างคำ จึงเช็ค "ขอบเขตคำ" ด้วย regex เฉพาะคำ (กันคำที่มีสรรพนามเป็นส่วนหนึ่ง
# เช่น คุณภาพ · ฉันทะ · แกง/แก้/แกล้ง · กูเกิล · เส้นผม) — จับพลาดฝั่งปล่อยผ่านดีกว่าจับผิดคนแปล
# ตารางนี้ดึง pattern จาก `thai_pronouns.py` แหล่งเดียว (แยกออกมา 26 ส.ค. 2026)
# ห้ามแก้รูปตรงนี้ — ต้องไปแก้ที่โมดูลกลาง ไม่งั้นตัวตรวจอีกสองตัวจะไม่ได้รับการแก้ด้วย
import thai_pronouns as _tp        # noqa: E402
WORD_RE = {
    "ผม":   _tp.RE_PHOM.pattern,
    "ดิฉัน": _tp.RE_DICHAN.pattern,
    "ฉัน":  _tp.RE_CHAN.pattern,
    "กู":   _tp.RE_KU.pattern,
    "นาย":  _tp.RE_NAI.pattern,
    "คุณ":  _tp.RE_KHUN.pattern,
    "แก":   _tp.RE_KAE.pattern,
    "มึง":  _tp.RE_MUENG.pattern,
}


def find_word(text, word):
    """หาคำสรรพนามแบบมีขอบเขต — คืนตำแหน่งที่พบจริง"""
    pat = WORD_RE.get(word, re.escape(word))
    return [m.start() for m in re.finditer(pat, text)]


def tiers_in(text):
    """คืน (คำแทนตัวที่พบ, คำเรียกอีกฝ่ายที่พบ, ระดับที่พบจากคำลงท้าย)"""
    self_w = [w for w in SELF if find_word(text, w)]
    other_w = [w for w in OTHER if find_word(text, w)]
    end_t = {t for t, ws in ENDINGS.items() if any(w in text for w in ws)}
    return self_w, other_w, end_t


def possible_tiers(words, table):
    """ระดับที่ยัง "เป็นไปได้พร้อมกัน" ของคำที่พบ — ว่างเปล่า = ขัดกันเอง"""
    out = None
    for w in words:
        out = set(table[w]) if out is None else out & table[w]
    return out if out is not None else set()


# ข้อความ "อธิบายกฎ" ในไฟล์เอกสาร/ไฟล์ตัวละคร จงใจเอ่ยหลายระดับพร้อมกัน (เช่น "แก้จาก 'ผม / ฉัน' เดิม")
# เวลาสแกนไฟล์พวกนั้นให้ข้ามด้วย --docs · บทแปลจริงใน master_th.json ไม่มีเครื่องหมายพวกนี้
NOTE_MARKERS = ["T1", "T2", "T3", "⏳", "§", "แก้จาก", "PRONOUN", "จับคู่", "ระดับ", "ตาม EN",
                "ยืนยันกับ EN", "คู่กับ", "แล้วแต่บริบท", "ตามความเป็นทางการ", "ห้ามผสม",
                "ห้ามข้าม", "ห้ามขยับ", "สลับตามบริบท", "เหตุผล:"]


def is_note(text):
    return any(m in text for m in NOTE_MARKERS)


def check_text(text):
    """คืนรายการปัญหาของข้อความหนึ่งชิ้น"""
    problems = []
    self_w, other_w, end_t = tiers_in(text)
    self_t, other_t = possible_tiers(self_w, SELF), possible_tiers(other_w, OTHER)
    if self_w and other_w and not (self_t & other_t):
        problems.append("ผสมข้ามระดับ: แทนตัว %s + เรียกอีกฝ่าย %s"
                        % ("/".join(self_w), "/".join(other_w)))
    all_t = possible_tiers(self_w + other_w, dict(SELF, **OTHER))
    if all_t == {"T3"} and "T1" in end_t:
        problems.append("T3 (กู/มึง) คู่กับคำลงท้ายสุภาพ ครับ/ค่ะ")
    if len(self_w) > 1:
        problems.append("คำแทนตัวหลายคำในบรรทัดเดียว: %s" % "/".join(self_w))
    # "นาย" ไม่นับในกฎนี้ — ดู MULTI_EXEMPT
    multi = [w for w in other_w if w not in MULTI_EXEMPT]
    if len(multi) > 1:
        problems.append("คำเรียกอีกฝ่ายหลายคำในบรรทัดเดียว: %s" % "/".join(multi))
    return problems


def walk_json(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_json(v, "%s/%s" % (path, k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_json(v, "%s[%d]" % (path, i))
    elif isinstance(obj, str):
        yield path, obj


def units(p):
    """แตกไฟล์เป็นชิ้นข้อความที่ควรตรวจทีละชิ้น"""
    if p.suffix == ".json":
        data = json.load(io.open(p, encoding="utf-8"))
        yield from walk_json(data)
    else:
        for i, line in enumerate(io.open(p, encoding="utf-8"), 1):
            yield "บรรทัด %d" % i, line.rstrip("\n")


def excepted_texts():
    """คำแปลที่ได้รับการยกเว้นไว้แล้วใน translations/pronoun_exceptions.json

    ไฟล์นั้นคีย์ด้วย **ต้นฉบับ EN** (เพราะ merge_qc.py ทำงานกับคีย์ EN) แต่ตัวตรวจนี้เห็นเฉพาะ
    ข้อความไทย จึงต้องแปลงเป็นชุดข้อความไทยก่อนด้วยการเปิด master_th.json
    เคสจริงที่ต้องยกเว้น: ตัวละคร T1 **ยกคำพูดของอันธพาลมาเล่า** ในเครื่องหมายคำพูด
    ทำให้ "กู" กับ "ค่ะ" อยู่บรรทัดเดียวกันโดยเป็นคนละผู้พูด (ดู batch_034)
    """
    ex = paths.TRANSLATIONS / "pronoun_exceptions.json"
    if not (ex.exists() and paths.MASTER_TH.exists()):
        return set()
    try:
        keys = json.load(io.open(ex, encoding="utf-8"))
        master = json.load(io.open(paths.MASTER_TH, encoding="utf-8"))
    except Exception:
        return set()
    master = master if isinstance(master, dict) else master.get("strings", {})
    return {master[k] for k in keys if isinstance(master.get(k), str)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--files", nargs="*", help="ไฟล์ที่จะตรวจ (ว่าง = translations/master_th.json)")
    ap.add_argument("--max", type=int, default=100)
    ap.add_argument("--docs", action="store_true",
                    help="โหมดสแกนไฟล์เอกสาร/ไฟล์ตัวละคร — ข้ามข้อความที่เป็นคำอธิบายกฎ")
    a = ap.parse_args()

    files = [paths.PROJECT / f for f in (a.files or [])] or [paths.MASTER_TH]
    files = [f for f in files if f.exists()]
    if not files:
        print("ไม่พบไฟล์ที่จะตรวจ (ยังไม่มี translations/master_th.json — ปกติสำหรับตอนนี้)")
        return 0

    skip = excepted_texts()
    total = shown = 0
    for p in files:
        for where, text in units(p):
            if a.docs and is_note(text):
                continue
            if text in skip:               # ยกเว้นไว้แล้วใน pronoun_exceptions.json
                continue
            probs = check_text(text)
            if not probs:
                continue
            total += 1
            if shown < a.max:
                shown += 1
                try:                       # ไฟล์นอกโปรเจกต์ (เช่นไฟล์ทดสอบใน temp) ก็ต้องตรวจได้
                    label = p.relative_to(paths.PROJECT)
                except ValueError:
                    label = p
                print("%s  %s" % (label, where))
                for pr in probs:
                    print("    - " + pr)
                print("    " + text.strip()[:160])
    print()
    print("พบปัญหา %d จุด%s" % (total, "" if total <= a.max else " (แสดง %d จุดแรก)" % a.max))
    return 1 if total else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
