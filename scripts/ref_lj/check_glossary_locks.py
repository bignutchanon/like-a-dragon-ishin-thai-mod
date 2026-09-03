#!/usr/bin/env python3
"""ตรวจว่า "คำล็อก" ใน `translations/glossary.md` ถูกใช้จริงในคำแปล

ทำไมต้องมี (26 ส.ค. 2026): คำล็อกหลุดซ้ำสอง sprint ติดกันโดยไม่มีด่านไหนจับได้เลย —
`alibi` ต้องเป็น "พยานที่อยู่" แต่ batch_046 แปลเป็น "ข้ออ้าง" และ batch_050 แปลเป็น
"หลักฐานยืนยันตัวจริง"/"ข้ออ้าง" อีก 4 จุด ทั้งสองครั้งกว่าจะเจอก็ต้องรอผู้ตรวจไล่อ่านด้วยตา
ตัวตรวจนี้ทำงานตรงข้ามกับ `check_latin_leftovers.py`:
  - ตัวนั้นถาม "มีอังกฤษตกค้างในคำแปลไหม"
  - ตัวนี้ถาม "**ต้นฉบับมีคำที่ล็อกไว้ แต่คำแปลไม่มีคำไทยที่ล็อกคู่กัน**ไหม"

วิธีอ่านตาราง glossary: เอาเฉพาะแถวที่ช่องซ้ายเป็นอังกฤษล้วน (ตัดวงเล็บอธิบายทิ้ง)
และช่องขวามีคำไทย · คำไทยที่คั่นด้วย "/" ถือว่าใช้ได้ทุกตัว (เช่น "สำนักงานกฎหมายเก็นดะ / สำนักงานเก็นดะ")

⚠ ตัวนี้เป็น **ตัวเตือน ไม่ใช่ด่านตัดสิน** — ภาษาไทยเรียบเรียงใหม่ได้ บางบรรทัดจงใจไม่เอ่ยคำนั้น
ให้คนอ่านผลแล้วตัดสิน ไม่ใช่ไล่แก้ตามเครื่องทุกจุด

ใช้:
  python scripts/check_glossary_locks.py --only 050
  python scripts/check_glossary_locks.py --done          # ทุกไฟล์ใน translations/done/
  python scripts/check_glossary_locks.py --done --terms alibi,handyman
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

GLOSSARY = paths.TRANSLATIONS / "glossary.md"

# คำที่ไม่ต้องตรวจ: สั้นเกินจนชนคำอื่น หรือเป็นคำที่ตั้งใจให้คงอังกฤษ (มี check_latin_leftovers ดูแลอยู่แล้ว)
SKIP_EN = {"rk", "mrc", "cg", "cgi", "ai", "atm", "usb", "chatter", "steam", "playstation",
           "buzzy searcher", "buzz researcher", "siren", "survive",
           # เพิ่ม 26 ส.ค. 2026: "pops" เป็นคำล็อก (= "ตาแก่" คำที่ไคโตะใช้เรียกชายสูงวัย)
           # แต่ก็เป็นคำกริยาอังกฤษธรรมดา ("pops up" · "pops out") ที่โผล่ทุก batch
           # ทำให้เตือนเท็จซ้ำ ๆ (นักแปล b070 รายงาน) — คำล็อกยังอยู่ใน glossary ให้คนอ่านตามปกติ
           "pops"}
MIN_LEN = 4          # คำอังกฤษสั้นกว่านี้ชนคำอื่นง่าย (a, an, gym ฯลฯ)
# ...ยกเว้น **ชื่อเฉพาะ** ที่ขึ้นต้นด้วยตัวใหญ่ — สั้นแค่ไหนก็ต้องตรวจ
# (26 ส.ค. 2026: `Tak` = ชื่อเล่นยากามิที่ไคโตะเรียก ล็อกเป็น "ทาคุ" แต่ batch_054 เขียน "แทค" 6 จุด
#  ตัวตรวจมองข้ามเพราะยาว 3 ตัวอักษร — เจอด้วย normalize_terms.py แทน)
# ชนคำอื่นไม่ได้อยู่แล้วเพราะ pattern ครอบด้วยขอบคำ (?<![A-Za-z]) / (?![A-Za-z])
MIN_LEN_PROPER = 3
THAI_RE = re.compile(r"[ก-๙]")


def strip_md(cell):
    s = re.sub(r"`([^`]*)`", r"\1", cell)
    s = s.replace("**", "").replace("*", "").strip()
    s = re.sub(r"\([^)]*\)", " ", s)          # ตัดวงเล็บอธิบาย
    s = re.sub(r"[“”\"]", "", s)
    return s.strip(" .·")


def load_locks():
    """คืน [(คำอังกฤษ, [คำไทยที่ยอมรับได้...])]"""
    if not GLOSSARY.exists():
        return []
    out, seen = [], set()
    for line in io.open(GLOSSARY, encoding="utf-8"):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        en = strip_md(cells[0])
        if not en or THAI_RE.search(en):
            continue
        # ตาราง glossary มีสองทรง: (EN | ไทย | ที่มา) และ (EN | ที่พบในเกม | ไทย | ที่มา)
        # ช่อง "ที่พบในเกม" มีคีย์ของไฟล์เกมแบบ snake_case (`y_building_seiryo`) — ต้องข้าม
        # ไม่งั้นจะหยิบช่องผิดแล้วเตือนผิดทุกบรรทัด (เจอจริงตอนสร้างตัวตรวจนี้)
        th = ""
        for c in cells[1:]:
            cand = strip_md(c)
            if not THAI_RE.search(cand):
                continue
            if re.search(r"[a-z0-9]+_[a-z0-9_]+", cand):
                continue
            th = cand
            break
        if not th:
            continue
        if not re.fullmatch(r"[A-Za-z0-9 '\-\.]+", en):
            continue
        key = en.lower()
        floor = MIN_LEN_PROPER if en[:1].isupper() else MIN_LEN
        if key in SKIP_EN or len(key) < floor or key in seen:
            continue
        # ช่องขวาอาจมีหลายรูปที่ยอมรับได้ คั่นด้วย / — และตัดคำอธิบายท้ายที่ขึ้นต้นด้วย —
        th = th.split("—")[0]
        forms = [t.strip() for t in th.split("/") if THAI_RE.search(t)]
        # ชื่อเต็มมักถูกเรียกด้วยชื่อเดียวในบทพูด ("มาซาฮารุ ไคโตะ" -> "ไคโตะ")
        # จึงรับคำย่อยที่ยาวพอเป็นรูปที่ยอมรับได้ด้วย ไม่งั้นจะเตือนผิดทุกบรรทัดที่เรียกชื่อสั้น
        for t in list(forms):
            forms += [w for w in t.split() if len(w) >= 3]
        forms = [t for t in dict.fromkeys(forms) if len(t) >= 2]
        if not forms:
            continue
        seen.add(key)
        out.append((en, forms))
    return out


def batches(a):
    if a.only:
        return [a.only]
    return [p.name[len("batch_"):-len(".done.json")]
            for p in sorted((paths.TRANSLATIONS / "done").glob("batch_*.done.json"))]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", help="เลข batch เช่น 050")
    ap.add_argument("--done", action="store_true", help="ทุกไฟล์ใน translations/done/")
    ap.add_argument("--terms", help="ตรวจเฉพาะคำเหล่านี้ (คั่นด้วย ,)")
    ap.add_argument("--max", type=int, default=60)
    a = ap.parse_args()

    locks = load_locks()
    if a.terms:
        want = {t.strip().lower() for t in a.terms.split(",")}
        locks = [(en, th) for en, th in locks if en.lower() in want]
    if not locks:
        print("ไม่พบคำล็อกที่ตรวจได้ใน glossary.md")
        return 2
    print("คำล็อกที่ตรวจได้ %d คำ" % len(locks))

    pats = [(en, th, re.compile(r"(?<![A-Za-z])%s(?![A-Za-z])" % re.escape(en), re.I))
            for en, th in locks]

    hits = collections.Counter()
    shown = 0
    for b in batches(a):
        done_p = paths.TRANSLATIONS / "done" / ("batch_%s.done.json" % b)
        if not done_p.exists():
            continue
        done = json.load(io.open(done_p, encoding="utf-8"))["strings"]
        for k, v in done.items():
            for en, forms, rx in pats:
                if not rx.search(k):
                    continue
                if any(f in v for f in forms):
                    continue
                hits[en] += 1
                if shown < a.max:
                    shown += 1
                    print("\nbatch_%s  ต้นฉบับมี \"%s\" แต่คำแปลไม่มี %s"
                          % (b, en, " / ".join(forms)))
                    print("   EN: %s" % k.replace("\n", " / ")[:110])
                    print("   TH: %s" % v.replace("\n", " / ")[:110])
    print()
    if not hits:
        print("ไม่พบคำล็อกที่หายไป")
        return 0
    print("สรุปคำที่ควรตรวจ (จำนวนบรรทัด):")
    for en, n in hits.most_common():
        print("   %-28s %d" % (en, n))
    print("\n⚠ เป็นตัวเตือน ไม่ใช่คำตัดสิน — บางบรรทัดเรียบเรียงใหม่โดยไม่เอ่ยคำนั้นก็ถูกต้องได้")
    return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
