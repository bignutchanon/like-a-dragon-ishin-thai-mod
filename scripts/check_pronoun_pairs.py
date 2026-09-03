#!/usr/bin/env python3
"""ตรวจว่าคำแปลไทยใช้สรรพนาม "จับคู่" ถูกระดับตาม PRONOUN_MATRIX §0

ระบบของภาคนี้ (ยุคบาคุมัตสึ — PRONOUN_MATRIX §0 · เคาะ 1 ก.ย. 2026):
  T1 สุภาพ : ข้า / กระผม  <->  ท่าน          (คำลงท้าย ขอรับ/เจ้าค่ะ)
  T2 กันเอง: ข้า          <->  เจ้า / นาย    (นะ/สิ/เหรอ)
  T3 หยาบ  : กู           <->  มึง           (โว้ย/เว้ย/ว่ะ)

ระบบของภาคปัจจุบัน (ผม/คุณ/ครับ/ค่ะ · ฉัน/แก) ยังอยู่ในตารางด้วยในชื่อระดับ M1/M2 เพราะ
**ข้อความเมนู/ระบบของภาคนี้ยังใช้ภาษาไทยปัจจุบัน** (PRONOUN_MATRIX §4 ข้อ 3) — แต่ระดับ M
กับระดับ T ใช้ร่วมบรรทัดเดียวกันไม่ได้ ตัวตรวจจึงจับ "ข้า…คุณ" หรือ "ผม…เจ้า" เป็นการผสมข้ามยุค

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
# คำเดียวอาจอยู่ได้หลายระดับ — "ข้า" เป็นได้ทั้ง T1 และ T2 (ต่างกันที่คำเรียกคู่สนทนา)
# จึงเก็บเป็น "ชุดระดับที่เป็นไปได้" แล้วตัดสินว่าผิดก็ต่อเมื่อ **ไม่มีระดับไหนใช้ร่วมกันได้เลย**
# (บทเรียน LJ sprint ต้น ๆ: เคยล็อกคำเดียว = ระดับเดียว แล้วตีคำแปลที่ถูกต้องตกเป็นสิบบรรทัด)
#
# M1/M2 = ระบบของภาคปัจจุบัน ซึ่งภาคนี้ใช้ได้เฉพาะข้อความเมนู/ระบบ ไม่ใช่บทพูดของตัวละครในยุค
# (การใช้ M ในบทพูดเป็นหน้าที่ของด่าน M ใน merge_qc.py ที่รู้ priority ของ batch — ไม่ใช่ที่นี่)
SELF = {"ข้า": {"T1", "T2"}, "กระผม": {"T1"}, "กู": {"T3"},
        "ผม": {"M1"}, "ดิฉัน": {"M1"}, "ฉัน": {"M1", "M2"}}
OTHER = {"ท่าน": {"T1"}, "เจ้า": {"T2"}, "นาย": {"T2", "M1", "M2"}, "มึง": {"T3"},
         "คุณ": {"M1"}, "แก": {"M2"}}
# คำที่ไม่นับในกฎ "คำเรียกอีกฝ่ายหลายคำในบรรทัดเดียว"
# "นาย" อยู่ได้หลายระดับ · "ท่าน" ในยุคนี้ใช้เป็นคำนำหน้าบุคคลที่สามด้วย ("ท่านฮิจิกาตะสั่งมา")
# จึงอยู่ร่วมบรรทัดกับคำเรียกคู่สนทนาตัวจริงได้โดยไม่ผิด
MULTI_EXEMPT = {"นาย", "ท่าน"}
# คำลงท้าย — ตรวจด้วย regex ไม่ใช่ substring
# ⚠ ห้ามใช้ `"ค่ะ" in text`: "เจ้าค่ะ" ซึ่งเป็นคำลงท้ายที่ถูกต้องของภาคนี้มี "ค่ะ" อยู่ข้างใน
import thai_pronouns as _tp        # noqa: E402
ENDINGS = {"T1": _tp.POLITE_OLD,
           "T3": re.compile(r"โว้ย|เว้ย"),
           "M1": re.compile(_tp.RE_KHRAP.pattern + r"|" + _tp.RE_KHA_MODERN.pattern)}

# ภาษาไทยไม่เว้นวรรคระหว่างคำ จึงเช็ค "ขอบเขตคำ" ด้วย regex เฉพาะคำ (กันคำที่มีสรรพนามเป็นส่วนหนึ่ง
# เช่น ข้าม/ข้าว/เข้า · ท่านั่ง · เจ้าของ · คุณภาพ · กูเกิล) — ตารางนี้ดึง pattern จาก
# `thai_pronouns.py` แหล่งเดียว · ห้ามเขียนรูปใหม่ที่นี่ ไม่งั้นตัวตรวจตัวอื่นจะไม่ได้รับการแก้ด้วย
WORD_RE = {
    "ข้า":   _tp.RE_KHA_SELF.pattern,
    "กระผม": _tp.RE_KRAPHOM.pattern,
    "กู":    _tp.RE_KU.pattern,
    "ผม":    _tp.RE_PHOM.pattern,
    "ดิฉัน":  _tp.RE_DICHAN.pattern,
    "ฉัน":   _tp.RE_CHAN.pattern,
    "ท่าน":  _tp.RE_THAN.pattern,
    "เจ้า":   _tp.RE_CHAO.pattern,
    "นาย":   _tp.RE_NAI.pattern,
    "คุณ":   _tp.RE_KHUN.pattern,
    "แก":    _tp.RE_KAE.pattern,
    "มึง":   _tp.RE_MUENG.pattern,
}

# ชื่อตัวละครที่ล็อกไว้ — ใช้กัน "ท่าน + ชื่อ" (คำนำหน้าบุคคลที่สาม) ไม่ให้ถูกนับเป็นคำเรียกคู่สนทนา
# ตัวอย่างจริงที่ต้องไม่ตก: "ท่านฮิจิกาตะสั่งมา เจ้าไปเถอะ" — ท่าน = คนที่สาม · เจ้า = คู่สนทนา
_NAME_TOKENS = None


def name_tokens():
    global _NAME_TOKENS
    if _NAME_TOKENS is None:
        toks = set()
        f = paths.TRANSLATIONS / "name_locks.json"
        if f.exists():
            data = json.load(io.open(f, encoding="utf-8"))
            for k, v in data.items():
                if k.startswith("_") or not isinstance(v, dict):
                    continue
                for th in v.values():
                    if isinstance(th, str):
                        toks.update(t for t in th.split() if len(t) >= 2)
        _NAME_TOKENS = toks
    return _NAME_TOKENS


def find_word(text, word):
    """หาคำสรรพนามแบบมีขอบเขต — คืนตำแหน่งที่พบจริง

    "ท่าน" ที่ตามด้วยชื่อตัวละครที่ล็อกไว้ = คำนำหน้าบุคคลที่สาม ไม่ใช่คำเรียกคู่สนทนา จึงไม่นับ
    """
    pat = WORD_RE.get(word, re.escape(word))
    hits = []
    for m in re.finditer(pat, text):
        if word == "ท่าน":
            rest = text[m.end():]
            if any(rest.startswith(t) for t in name_tokens()):
                continue
        hits.append(m.start())
    return hits


def tiers_in(text):
    """คืน (คำแทนตัวที่พบ, คำเรียกอีกฝ่ายที่พบ, ระดับที่พบจากคำลงท้าย)"""
    self_w = [w for w in SELF if find_word(text, w)]
    other_w = [w for w in OTHER if find_word(text, w)]
    end_t = {t for t, rx in ENDINGS.items() if rx.search(text)}
    return self_w, other_w, end_t


def possible_tiers(words, table):
    """ระดับที่ยัง "เป็นไปได้พร้อมกัน" ของคำที่พบ — ว่างเปล่า = ขัดกันเอง"""
    out = None
    for w in words:
        out = set(table[w]) if out is None else out & table[w]
    return out if out is not None else set()


# ข้อความ "อธิบายกฎ" ในไฟล์เอกสาร/ไฟล์ตัวละคร จงใจเอ่ยหลายระดับพร้อมกัน (เช่น "แก้จาก 'ผม / ฉัน' เดิม")
# เวลาสแกนไฟล์พวกนั้นให้ข้ามด้วย --docs · บทแปลจริงใน master_th.json ไม่มีเครื่องหมายพวกนี้
NOTE_MARKERS = ["T1", "T2", "T3", "M1", "M2", "⏳", "§", "แก้จาก", "PRONOUN", "จับคู่", "ระดับ", "ตาม EN",
                "ยืนยันกับ EN", "คู่กับ", "แล้วแต่บริบท", "ตามความเป็นทางการ", "ห้ามผสม",
                "ห้ามข้าม", "ห้ามขยับ", "สลับตามบริบท", "เหตุผล:"]


def is_note(text):
    return any(m in text for m in NOTE_MARKERS)


# ชื่อเฉพาะที่ใส่เครื่องหมายคำพูดไว้ (ชื่อท่า · ชื่อไอเทม · ชื่อฉายา) ไม่ใช่บทพูด
# 2 ก.ย. 2026 (คลื่น 042–054): ชื่อคันเบ็ด "เบ็ดเจ้าสายน้ำ" มีคำว่า "เจ้า" อยู่ในชื่อ
# ทำให้ด่าน P นับเป็นคำเรียกคู่สนทนา แล้วตีกลับคำอธิบายเมนูที่ถูกต้องอยู่แล้ว
_QUOTE_CHARS = "\"“”「」‘’'"
QUOTED = re.compile("[%s][^%s\\n]{1,40}[%s]"
                    % (_QUOTE_CHARS, _QUOTE_CHARS, _QUOTE_CHARS))


def strip_quoted_names(text):
    """ตัดชื่อเฉพาะในเครื่องหมายคำพูดออกก่อนตรวจสรรพนาม"""
    return QUOTED.sub(" ", text)


def is_document(text):
    """เอกสารยาว (ตำราประวัติศาสตร์ · จดหมาย · บันทึกใน `book_book`) ไม่ใช่ "บทพูดหนึ่งบรรทัด"

    มีหลายย่อหน้าและหลายน้ำเสียงในสตริงเดียว จึงมีทั้งคำนำหน้าบุคคลที่สามและสรรพนามผู้เขียนปนกันได้
    `merge_qc.py` ด่าน P ยกเว้นเคสนี้เป็นคำเตือนมาตั้งแต่คลื่น 042–054 — ตัวตรวจนี้ต้องรายงานตรงกัน
    ไม่งั้นผู้ตรวจเห็น "พบปัญหา N จุด" ทุกครั้งทั้งที่ merge ผ่าน (รายงานจากคลื่น MSG_034–036)
    """
    return len(text) > 400 or text.count(chr(10) + chr(10)) >= 2


def check_text(text):
    """คืนรายการปัญหาของข้อความหนึ่งชิ้น"""
    text = strip_quoted_names(text)
    problems = []
    self_w, other_w, end_t = tiers_in(text)
    self_t, other_t = possible_tiers(self_w, SELF), possible_tiers(other_w, OTHER)
    if self_w and other_w and not (self_t & other_t):
        problems.append("ผสมข้ามระดับ: แทนตัว %s + เรียกอีกฝ่าย %s"
                        % ("/".join(self_w), "/".join(other_w)))
    all_t = possible_tiers(self_w + other_w, dict(SELF, **OTHER))
    if all_t == {"T3"} and (end_t & {"T1", "M1"}):
        problems.append("T3 (กู/มึง) คู่กับคำลงท้ายสุภาพ (ขอรับ/เจ้าค่ะ/ครับ/ค่ะ)")
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
        # ไฟล์ done มีช่อง `notes` ที่ผู้ตรวจ/นักแปลเขียนอธิบายกฎ ซึ่งมักยกตัวอย่างสรรพนามหลายระดับ
        # ในประโยคเดียว — ถ้าสแกนทั้งไฟล์จะถูกจับเป็นคำแปลที่ผสมข้ามระดับ (เกิดจริงกับ batch_002)
        if isinstance(data, dict) and isinstance(data.get("strings"), dict):
            data = data["strings"]
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
    total = shown = docs = 0
    for p in files:
        for where, text in units(p):
            if a.docs and is_note(text):
                continue
            if text in skip:               # ยกเว้นไว้แล้วใน pronoun_exceptions.json
                continue
            probs = check_text(text)
            if not probs:
                continue
            if is_document(text):          # เตือนอย่างเดียว เหมือนด่าน P ของ merge_qc
                docs += 1
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
    if docs:
        print("(ข้าม %d จุดที่เป็นเอกสารยาว — ด่าน P ของ merge_qc ก็ยกเว้นเหมือนกัน)" % docs)
    return 1 if total else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
