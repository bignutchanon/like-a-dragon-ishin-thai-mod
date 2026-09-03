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
#  ตัวตรวจมองข้ามเพราะยาว 3 ตัวอักษร — ใช้ check_translit_drift.py จับแทน)
# ชนคำอื่นไม่ได้อยู่แล้วเพราะ pattern ครอบด้วยขอบคำ (?<![A-Za-z]) / (?![A-Za-z])
MIN_LEN_PROPER = 3
THAI_RE = re.compile(r"[ก-๙]")


def strip_md(cell):
    s = re.sub(r"`([^`]*)`", r"\1", cell)
    s = s.replace("**", "").replace("*", "").strip()
    s = re.sub(r"\([^)]*\)", " ", s)          # ตัดวงเล็บอธิบาย
    s = re.sub(r"[“”\"]", "", s)
    return s.strip(" .·")


# คำล็อกที่ EN เป็นคำสามัญคำเดียว — **บังคับไม่ได้** เพราะคำเดียวกันโผล่ในบริบทอื่นทั้งเกม
# (Gold = ขุนพลทอง เฉพาะกระดานโชกิ แต่ "gold" ในคำอธิบายไอเทมคือทองคำ)
# ยังคงอยู่ใน glossary เพื่อให้นักแปลอ่าน แต่ตัวตรวจข้ามไป ไม่งั้นเตือนเท็จทุกก้อน
# (เพิ่ม 2 ก.ย. 2026 หลังใส่ §1.9.8 แล้วเตือนเท็จโผล่ทันที 4 คำในก้อนเดียว)
CONTEXT_ONLY = {
    "king", "gold", "silver", "knight", "lance", "rook", "bishop", "pawn",
    "single", "racer", "check", "draw", "level", "rank",
    "voice", "music", "font", "standard", "custom", "season", "variety", "junk",
    # คำล็อกพ้องรูปใน §1.7 — สองความหมายอยู่คนละคอลัมน์ บังคับคอลัมน์เดียวไม่ได้
    "clear data",
    # เพิ่ม 2 ก.ย. 2026 (sprint 10 · ก้อน MSG_004): คำล็อกผูกกับ UI ช่องเดียว
    # แต่คำเดียวกันเป็นคำสามัญในบทพูด — "tags" = ป้ายไม้เดิมพันที่ซื้อจากหน้าร้าน
    # (คนละอย่างกับช่องแต้ม 点) · "heat" = ความร้อนรุ่มในร่างกาย ไม่ใช่เกจฮีท
    "tags", "heat",
}


def load_locks():
    """คืน [(คำอังกฤษ, [คำไทยที่ยอมรับได้...])]"""
    if not GLOSSARY.exists():
        return []
    out, seen = [], set()
    # อ่านเฉพาะหัวข้อ "§1 คำล็อก (LOCKED)" — ที่เหลือใน glossary.md เป็นข้อเสนอที่ lead
    # ยังไม่เคาะ (§2 คำที่ต้องเคาะก่อนเปิด batch) ถ้าอ่านมาด้วยจะกลายเป็นบังคับใช้คำที่ยังไม่ล็อก
    in_locked = False
    for line in io.open(GLOSSARY, encoding="utf-8"):
        # เช็คเฉพาะหัวข้อระดับ `## ` — หัวข้อย่อย `### ` ข้างในยังอยู่ในหมวดเดิม
        if line.startswith("## ") and not line.startswith("###"):
            in_locked = "LOCKED" in line
            continue
        if not in_locked or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        # ช่องซ้ายที่เขียนเป็นโค้ดล้วน (`NAME` · `GET_COMMENT`) คือ **ชื่อคอลัมน์ของตารางในเกม**
        # ไม่ใช่คำอังกฤษบนจอ — ตารางกติกาแบบนี้ (§1.9.13) จะกลายเป็นคำล็อกปลอมถ้าอ่านมาด้วย
        if re.fullmatch(r"`[^`]+`", cells[0].strip()):
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
    out += load_name_locks(seen)
    out += load_place_locks(seen)
    return [(en, forms) for en, forms in out if en.lower() not in CONTEXT_ONLY]


def load_place_locks(seen):
    """คำล็อกชื่อสถานที่/ร้านค้าจาก `translations/place_locks.json`

    ป้ายสถานที่เดียวกันกระจายข้ามหลายก้อน (คลื่น 030-041 มีอยู่ 5 ก้อน) และจะโผล่ซ้ำ
    ในบทพูด NPC ของคลื่นถัดไป — เก็บไว้ไฟล์เดียวแบบเดียวกับ name_locks.json
    """
    p = paths.TRANSLATIONS / "place_locks.json"
    if not p.exists():
        return []
    d = json.load(io.open(p, encoding="utf-8"))
    out = []
    for en, th in (d.get("places") or {}).items():
        key = en.lower()
        if key in seen or THAI_RE.search(en) or not th.strip():
            continue
        # ช่องขวาเป็นวลี (ร้านน้ำชาโอตาเกะ) — รับคำย่อยที่ยาวพอด้วย เหมือนกฎของชื่อคน
        forms = [th] + [w for w in th.split() if len(w) >= 3]
        forms = [t for t in dict.fromkeys(forms) if len(t) >= 2]
        seen.add(key)
        out.append((en, forms))
    return out


def load_name_locks(seen):
    """คำล็อกชื่อตัวละครจาก `translations/name_locks.json`

    ชื่อ 35 ชื่ออยู่ในไฟล์ JSON ไม่ใช่ตารางใน glossary.md (แก้ที่เดียวแล้วเอกสารสร้างตาม)
    ตัวตรวจจึงต้องอ่านทั้งสองที่ ไม่งั้นบังคับใช้ได้แค่ 6 ชื่อที่ยกมาโชว์ใน glossary §1.5
    """
    p = paths.TRANSLATIONS / "name_locks.json"
    if not p.exists():
        return []
    d = json.load(io.open(p, encoding="utf-8"))
    out = []
    for group in ("full", "short"):
        for en, th in (d.get(group) or {}).items():
            key = en.lower()
            if key in seen or THAI_RE.search(en) or not th.strip():
                continue
            if th.startswith("⚠"):          # ยังไม่ได้ล็อกจริง
                continue
            forms = [th] + [w for w in th.split() if len(w) >= 3]
            forms = [t for t in dict.fromkeys(forms) if len(t) >= 2]
            seen.add(key)
            out.append((en, forms))
    return out


# คำล็อก "To X" คือ **ป้ายจุดหมาย**บนแผนที่ (ไปมุคุโรไก · ไปกิอง) ไม่ใช่รูปที่บังคับในร้อยแก้ว
# ถ้าจับแบบซับสตริง ประโยคปกติ ("I should hurry to Mukurogai.") จะโดนเตือนทุกบรรทัด
# ทั้งที่คำแปลใช้รูปที่ master ใช้อยู่แล้ว ("ไปย่านมุคุโรไก" — ย่าน<ชื่อ> มีใน master 7 จุด)
# → ล็อกกลุ่มนี้ตรวจเฉพาะตอนที่ทั้งสตริงคือป้ายนั้นจริง (เพิ่ม 3 ก.ย. 2026 · คลื่น MSG_043–048)
SIGN_PREFIX = ("to ",)


def sign_pattern(en):
    """คืน regex ของคำล็อกหนึ่งคำ — ป้ายจุดหมายจับทั้งสตริง ที่เหลือจับด้วยขอบคำ"""
    if en.lower().startswith(SIGN_PREFIX):
        return r"\A\s*%s\s*\Z" % re.escape(en)
    return r"(?<![A-Za-z])%s(?![A-Za-z])" % re.escape(en)


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

    # เรียงจากวลียาวไปสั้น เพื่อให้ "คำล็อกที่เป็นวลี" ชนะ "คำล็อกคำเดี่ยวที่อยู่ข้างใน"
    # เคสจริง (batch_001 · 2 ก.ย. 2026): `Tosa Loyalist Party` ล็อกเป็น "พรรคจงรักภักดีโทสะ"
    # แต่ `Loyalist` คำเดี่ยวล็อกเป็น "ชิชิ" — ถ้าไม่จัดลำดับ ตัวตรวจจะเตือนเท็จทุกบรรทัดที่เอ่ยชื่อพรรค
    locks = sorted(locks, key=lambda x: -len(x[0]))
    pats = [(en, th, re.compile(sign_pattern(en), re.I)) for en, th in locks]

    hits = collections.Counter()
    shown = 0
    for b in batches(a):
        done_p = paths.TRANSLATIONS / "done" / ("batch_%s.done.json" % b)
        if not done_p.exists():
            continue
        done = json.load(io.open(done_p, encoding="utf-8"))["strings"]
        for k, v in done.items():
            covered = []          # ช่วงตัวอักษรที่คำล็อกวลียาวกว่าจับไปแล้ว
            for en, forms, rx in pats:
                ms = [m for m in rx.finditer(k)
                      if not any(m.start() < e and s < m.end() for s, e in covered)]
                if not ms:
                    continue
                covered += [(m.start(), m.end()) for m in ms]
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
