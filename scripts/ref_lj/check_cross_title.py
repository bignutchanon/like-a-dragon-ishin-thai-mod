#!/usr/bin/env python3
"""ด่านคำล็อกข้ามภาค — จับคำที่ **โปรเจกต์พี่น้องล็อกไว้แล้ว แต่ LJ แปลเป็นอย่างอื่น**

ทำไมต้องมี (สร้าง 26 ส.ค. 2026 · sprint 11):
`check_glossary_locks.py` เฝ้าเฉพาะคำที่อยู่ใน `glossary.md` ของ LJ เอง จึงมองไม่เห็นคำที่
ภาคอื่น ship ไปแล้วแต่ LJ ยังไม่ได้ล็อก — sprint 10 เจอแบบนี้ 5 คำ
(`Shintani` · `Queen Rouge` · `mahjong` · `Earth Angel` · `Ijin Three`)
ทุกคำถูกจับด้วย "สายตาผู้ตรวจ" ล้วน ๆ ซึ่งแปลว่าที่ไม่มีใครทันสังเกตก็ยังหลุดอยู่

`find_term.py` ตอบคำถาม "คำนี้เคยแปลว่าอะไร" ทีละคำ (คนถาม)
ไฟล์นี้ตอบ "มีคำไหนบ้างที่เราแปลไม่ตรงกับภาคอื่น" ทั้งกอง (เครื่องถาม)

⚠ **เป็นตัวเตือน ไม่ใช่ด่านตัดสิน** — LJ ชนะเสมอถ้าตั้งใจใช้คำต่าง สิ่งที่ต้องดูคือ
"เราตั้งใจต่าง หรือไม่มีใครรู้ว่าภาคอื่นมีคำอยู่แล้ว"

ใช้:
  python scripts/check_cross_title.py                 # ทั้ง master_th
  python scripts/check_cross_title.py --only 083      # เจาะ batch เดียว (ไฟล์ done)
  python scripts/check_cross_title.py --done          # ทุกไฟล์ใน translations/done/
  python scripts/check_cross_title.py --min 2         # แสดงเฉพาะคำที่ขัดตั้งแต่ N จุดขึ้นไป
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

# ⚠ รายชื่อโฟลเดอร์ภาคพี่น้องอยู่ที่ `paths.SIBLINGS` ที่เดียว (รวมมา 26 ส.ค. 2026 · sprint 16)
# (ชื่อที่แสดง, path ของ glossary) — เรียงตามลำดับความสำคัญ
SIBLINGS = [(n, g) for n, _m, g in paths.sibling_paths()]
# \u0e04\u0e33\u0e17\u0e35\u0e48 **\u0e40\u0e04\u0e32\u0e30\u0e41\u0e25\u0e49\u0e27\u0e27\u0e48\u0e32\u0e43\u0e2b\u0e49\u0e43\u0e0a\u0e49\u0e23\u0e39\u0e1b\u0e02\u0e2d\u0e07 LJ** \u0e17\u0e31\u0e49\u0e07\u0e17\u0e35\u0e48\u0e15\u0e48\u0e32\u0e07\u0e08\u0e32\u0e01\u0e20\u0e32\u0e04\u0e2d\u0e37\u0e48\u0e19 \u2014 \u0e44\u0e21\u0e48\u0e15\u0e49\u0e2d\u0e07\u0e40\u0e15\u0e37\u0e2d\u0e19\u0e0b\u0e49\u0e33\u0e17\u0e38\u0e01\u0e23\u0e2d\u0e1a
# (\u0e40\u0e2b\u0e15\u0e38\u0e1c\u0e25\u0e40\u0e15\u0e47\u0e21\u0e2d\u0e22\u0e39\u0e48\u0e43\u0e19 `translations/glossary.md` \u00a77.3 \u00b7 \u0e40\u0e02\u0e35\u0e22\u0e19\u0e44\u0e27\u0e49\u0e17\u0e35\u0e48\u0e19\u0e35\u0e48\u0e14\u0e49\u0e27\u0e22\u0e40\u0e1e\u0e37\u0e48\u0e2d\u0e43\u0e2b\u0e49\u0e04\u0e19\u0e2d\u0e48\u0e32\u0e19\u0e2a\u0e04\u0e23\u0e34\u0e1b\u0e15\u0e4c\u0e40\u0e2b\u0e47\u0e19\u0e40\u0e25\u0e22)
DECIDED = {
    "Hiro":  "\u0e04\u0e19\u0e25\u0e30\u0e15\u0e31\u0e27\u0e25\u0e30\u0e04\u0e23\u0e01\u0e31\u0e1a Hiro \u0e02\u0e2d\u0e07 Y7 \u00b7 LJ \u0e43\u0e0a\u0e49 '\u0e2e\u0e34\u0e42\u0e23\u0e30' \u0e04\u0e23\u0e1a 54 \u0e08\u0e38\u0e14",
    "Shiro": "\u0e04\u0e19\u0e25\u0e30\u0e15\u0e31\u0e27\u0e25\u0e30\u0e04\u0e23\u0e01\u0e31\u0e1a Shiro \u0e02\u0e2d\u0e07 Gaiden \u00b7 LJ \u0e43\u0e0a\u0e49 '\u0e0a\u0e34\u0e42\u0e23\u0e30'",
    "Renji": "\u0e04\u0e19\u0e25\u0e30\u0e15\u0e31\u0e27\u0e25\u0e30\u0e04\u0e23\u0e01\u0e31\u0e1a Renji \u0e02\u0e2d\u0e07 Gaiden \u00b7 LJ \u0e43\u0e0a\u0e49 '\u0e40\u0e23\u0e19\u0e08\u0e34'",
    "White Masks": "Y8 \u0e40\u0e2d\u0e07\u0e43\u0e0a\u0e49\u0e2a\u0e2d\u0e07\u0e23\u0e39\u0e1b\u0e1b\u0e19\u0e01\u0e31\u0e19 \u00b7 LJ \u0e43\u0e0a\u0e49 '\u0e2b\u0e19\u0e49\u0e32\u0e01\u0e32\u0e01\u0e02\u0e32\u0e27' \u0e04\u0e23\u0e1a 9/9 \u0e41\u0e25\u0e30\u0e1a\u0e17\u0e2d\u0e18\u0e34\u0e1a\u0e32\u0e22\u0e04\u0e33\u0e19\u0e35\u0e49\u0e40\u0e2d\u0e07\u0e27\u0e48\u0e32\u0e40\u0e1b\u0e47\u0e19\u0e04\u0e33\u0e40\u0e23\u0e35\u0e22\u0e01",
    "Keihin Gang": "\u0e02\u0e2d\u0e07 LJ \u0e04\u0e37\u0e2d 'Neo Keihin Gang' = \u0e41\u0e01\u0e4a\u0e07\u0e19\u0e35\u0e42\u0e2d\u0e40\u0e04\u0e2e\u0e34\u0e19 \u2014 \u0e04\u0e19\u0e25\u0e30\u0e04\u0e33\u0e01\u0e31\u0e1a '\u0e41\u0e01\u0e4a\u0e07\u0e40\u0e04\u0e2e\u0e34\u0e19' \u0e02\u0e2d\u0e07\u0e20\u0e32\u0e04\u0e41\u0e23\u0e01",
}

THAI = re.compile(r"[\u0e00-\u0e7f]")
LATIN = re.compile(r"[A-Za-z]")
BOLD = re.compile(r"\*\*|`|~~")
PAREN = re.compile(r"\([^)]*\)|\[[^\]]*\]|（[^）]*）")

# คำที่ห้ามเอามาเป็นกฎ (เป็นหัวตาราง/ศัพท์ทั่วไป/คำที่ LJ ใช้ต่างโดยตั้งใจ)
BAN_EN = {
    "en", "th", "ไทย", "note", "ที่มา", "หมายเหตุ", "คำ", "ศัพท์", "ชื่อ",
    "yakuza", "kiwami", "sega", "boss", "clan", "family", "street", "city",
    "east", "west", "north", "south", "police", "detective", "lawyer",
    # ผลบวกเท็จรอบแรก (26 ส.ค. 2026) — ฝั่งภาคอื่นล็อกไว้เป็น **ศัพท์เมนู UI หรือค่าพลังในเกม**
    # ไม่ใช่คำเดียวกับที่ LJ ใช้ในบทสนทนา (Back->ย้อนกลับ · Quit->ออก · Defense->พลังป้องกัน)
    "quit", "call", "back", "next", "defense", "charmed", "ballsy", "hotshot",
    "help", "stand", "check", "trial", "justice", "guard", "attack", "speed",
}


def clean(s):
    s = BOLD.sub("", s)
    s = PAREN.sub("", s)
    return s.strip(" *`|")


def harvest(path):
    """ดึงคู่ EN -> ไทย จาก glossary.md ทั้งสองรูปแบบ (ตาราง markdown และ `EN→ไทย` ในบรรทัดเดียว)"""
    out = {}
    try:
        text = io.open(path, encoding="utf-8").read()
    except Exception:
        return out
    for ln in text.splitlines():
        # รูปแบบ 1: แถวตาราง | EN | ไทย | ... |
        if ln.lstrip().startswith("|") and "---" not in ln:
            cols = [clean(c) for c in ln.strip().strip("|").split("|")]
            if len(cols) >= 2:
                en, th = cols[0], cols[1]
                if en and th and LATIN.search(en) and THAI.search(th) and not THAI.search(en):
                    out.setdefault(en, th)
        # รูปแบบ 2: `EN→ไทย` คั่นด้วย | ในบรรทัดร้อยแก้ว
        for m in re.finditer(r"([A-Za-z][A-Za-z0-9'&.\- ]{2,40}?)\s*(?:→|->)\s*([\u0e00-\u0e7f][^|·\n]{0,40})", ln):
            en, th = clean(m.group(1)), clean(m.group(2))
            if en and th and not THAI.search(en):
                out.setdefault(en, th.split("(")[0].strip())
    keep = {}
    for k, v in out.items():
        # ตัดคำอธิบายที่ห้อยท้ายค่าไทย (`ชิโร่, Izumi->อิซึมิ` · `เก็นดะ ใช้ตามรูปที่ล็อก...`)
        v = re.split(r"[,·;]| / |\s+ใช้|\s+ตาม|\s+—|\s+-\s", v)[0].strip()
        if k.lower() in BAN_EN or len(k) < 4 or len(v) < 3:
            continue
        if not THAI.search(v) or LATIN.search(v):
            continue
        # **ต้องเป็นวิสามานยนาม** — ขึ้นต้นตัวใหญ่ในต้นฉบับ glossary
        # (ไม่งั้นจะได้ศัพท์เมนู UI อย่าง Back->ย้อนกลับ / Next->ถัดไป มาเป็นกฎ แล้วจับคำว่า
        #  "back off" ทั้งเกมเป็นของผิด — วัดจริงแล้วได้ผลบวกปลอม 435 จุดจากคำเดียว)
        if not k[:1].isupper():
            continue
        keep[k] = v
    return keep


def lj_locked():
    """คำที่ LJ ล็อกเองแล้ว — ของเราชนะ ไม่ต้องเตือน"""
    return {k.lower() for k in harvest(str(paths.TRANSLATIONS / "glossary.md"))}


def build_rules():
    """คืน {en_lower: (thai, ชื่อภาคที่เป็นเจ้าของ)} โดยภาคที่อยู่บนสุดในลำดับชนะ"""
    mine = lj_locked()
    rules = {}
    for label, path in SIBLINGS:
        for en, th in harvest(path).items():
            if en.lower() in mine or en in rules:
                continue
            rules[en] = (th, label)
    return rules, mine


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="เจาะ batch เดียว")
    ap.add_argument("--done", action="store_true", help="ตรวจทุกไฟล์ใน translations/done/")
    ap.add_argument("--min", type=int, default=1, help="แสดงเฉพาะคำที่ขัดตั้งแต่ N จุด")
    ap.add_argument("--max", type=int, default=40, help="แสดงกี่คำ")
    ap.add_argument("--all", action="store_true",
                    help="แสดงคำที่เคาะแล้ว (DECIDED) เป็นปัญหาด้วย — ใช้ตอนทบทวนคำตัดสินเก่า")
    a = ap.parse_args()

    rules, mine = build_rules()

    pairs = []
    if a.only or a.done:
        pat = "batch_%s.done.json" % a.only if a.only else "*.done.json"
        for p in sorted((paths.TRANSLATIONS / "done").glob(pat)):
            d = json.load(io.open(p, encoding="utf-8"))
            pairs += [(k, v, p.stem) for k, v in d["strings"].items()]
    else:
        d = json.load(io.open(paths.MASTER_TH, encoding="utf-8"))
        pairs = [(k, v, "master") for k, v in d.items()]

    hits = collections.Counter()
    where = collections.defaultdict(list)
    owner = {}
    compiled = {t: re.compile(r"(?<![A-Za-z])" + re.escape(t) + r"(?![A-Za-z])")
                for t in rules}
    # ต้นประโยค = ตัวใหญ่เพราะไวยากรณ์ ไม่ใช่เพราะเป็นชื่อเฉพาะ -> ไม่นับ (เว้นชื่อหลายคำ)
    STOP = set(".!?:\"'(—-")

    def sent_start(prefix):
        """ตัวใหญ่ต้นประโยคเกิดจากไวยากรณ์ ไม่ใช่เพราะเป็นชื่อเฉพาะ"""
        p = prefix.rstrip(" \t")
        return (not p) or p[-1] in STOP

    for en_key, th_val, src in pairs:
        for term, (th_term, label) in rules.items():
            if term not in en_key:
                continue
            m = compiled[term].search(en_key)
            if not m:
                continue
            if " " not in term and sent_start(en_key[:m.start()]):
                continue
            if th_term in th_val:
                continue
            hits[term] += 1
            owner[term] = (th_term, label)
            if len(where[term]) < 2:
                where[term].append((src, en_key[:80], th_val[:80]))

    print("กฎจากภาคพี่น้อง %d คำ (LJ ล็อกเอง %d คำ — ของเราชนะ ไม่นับ)" % (len(rules), len(mine)))
    print("ตรวจ %s คู่ · คำที่ไทยไม่ตรงกับภาคพี่น้อง %d แบบ (เกณฑ์ >= %d จุด)"
          % (format(len(pairs), ","), sum(1 for t in hits if hits[t] >= a.min), a.min))
    print("")
    decided = [t for t in hits if t in DECIDED]
    if decided and not a.all:
        print("เคาะแล้วให้ใช้รูปของ LJ (ไม่นับเป็นปัญหา · ดู glossary.md §7.3):")
        for t in decided:
            print("  %-16s x%-4d %s" % (t, hits[t], DECIDED[t]))
        print("")

    shown = 0
    for term, n in hits.most_common():
        if n < a.min or (term in DECIDED and not a.all):
            continue
        th_term, label = owner[term]
        print("  %-28s x%-4d  %s ล็อกว่า \"%s\"" % (term, n, label, th_term))
        for src, k, v in where[term]:
            print("      [%s] EN: %s" % (src, k))
            print("             TH: %s" % v)
        shown += 1
        if shown >= a.max:
            print("  ... ตัดที่ %d คำ (ใช้ --max เพิ่มได้)" % a.max)
            break
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
