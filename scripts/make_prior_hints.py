"""สร้างไฟล์ 'คำที่เคยเคาะแล้ว' ต่อ batch จาก translations/master_th.json

เหตุผล: ปัญหาหลักของคลื่น 018-029 คือชื่อเดียวกันถูกแจกข้ามก้อน แล้วแต่ละก้อน
ตั้งคำไทยกันเอง (ผู้ตรวจเจอ 28 + 47 จุด) — คำพวกนั้นเคยถูกเคาะไปแล้วใน batch ก่อน
แต่ไม่เคยถูกเขียนลง glossary นักแปลจึงมองไม่เห็น

วิธี: ดึงคีย์สั้น (ป้ายเมนู/ชื่อเฉพาะ) จาก master แล้วหาว่าคีย์ไหนโผล่เป็นคำย่อย
ในสตริงของ batch ที่กำลังจะแจก -> เขียนเป็น <batch>.prior.json ให้นักแปลอ่านคู่กับ worklist

ใช้: python scripts/make_prior_hints.py 030 031 ...   (ไม่ใส่เลข = ทุก batch ที่ยังไม่ส่ง)
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
WORKLIST = ROOT / "translations" / "worklist"
MASTER = ROOT / "translations" / "master_th.json"

# คีย์ที่ใช้เป็น "คำ" ได้: สั้น ไม่มีขึ้นบรรทัดใหม่ ไม่ใช่ประโยคเต็ม
MAX_WORDS = 5
MIN_CHARS = 3


PLACE_LOCKS = ROOT / "translations" / "place_locks.json"
NAME_LOCKS = ROOT / "translations" / "name_locks.json"


def load_locks() -> dict:
    """คำล็อกที่ lead เคาะไว้แล้ว (ชื่อคน + ชื่อสถานที่) — บังคับใช้ ไม่ใช่แค่ร่าง"""
    lex = {}
    if NAME_LOCKS.exists():
        d = json.loads(NAME_LOCKS.read_text(encoding="utf-8"))
        for group in ("full", "short"):
            for en, th in (d.get(group) or {}).items():
                if th and not th.startswith("⚠"):
                    lex[en] = th
    if PLACE_LOCKS.exists():
        d = json.loads(PLACE_LOCKS.read_text(encoding="utf-8"))
        for group in ("places", "context_only"):
            lex.update({k: v for k, v in (d.get(group) or {}).items() if v})
    return lex


def load_lexicon() -> dict:
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    lex = {}
    for en, th in master.items():
        if not isinstance(th, str) or not th.strip():
            continue
        if "\n" in en or len(en) < MIN_CHARS:
            continue
        if len(en.split()) > MAX_WORDS:
            continue
        if en.endswith((".", "!", "?")):
            continue
        lex[en] = th
    return lex


# ชื่อเฉพาะที่ **ไม่เคยเป็นคีย์สั้นเดี่ยว ๆ** ใน master จะไม่เข้า lexicon เลย
# (เช่น Higashihara โผล่ 6 คีย์ แต่ทุกคีย์เป็นประโยคเต็ม — `Higashihara...` ก็ตกเพราะลงท้ายด้วยจุด)
# อาการนี้บันทึกมาแล้วสองครั้ง (HANDOFF sprint 9 §4 · ก้อน MSG_056 ของ sprint 15)
# วิธีขุด: เอาทุกคู่ใน master ที่ EN มีชื่อนั้น แล้วหาสตริงไทยที่ยาวที่สุดซึ่งปรากฏใน **ทุก** ค่า
# ต้องมีอย่างน้อยสองคู่ ไม่งั้นแยกชื่อออกจากประโยคไม่ได้
MIN_NAME_PAIRS = 2
MIN_NAME_CHARS = 3
# สัดส่วนขั้นต่ำ: คู่ที่มีชื่อนี้ ต่อ คู่ทั้งหมดในคลังที่มีสตริงไทยนั้น
NAME_PRECISION = 0.8
# ความยาวไทยต่อความยาวโรมาจิ — ทับศัพท์ปกติไม่เกินราวสองเท่าครึ่ง
MAX_NAME_RATIO = 2.5
THAI_RUN = re.compile(r"[ก-๙]+")
# คำอังกฤษที่ขึ้นต้นประโยคด้วยตัวใหญ่เป็นปกติ — กันไม่ให้ถูกนับเป็นชื่อเฉพาะ
NOT_A_NAME = {
    "The", "This", "That", "There", "These", "Those", "They", "Then", "Thanks",
    "What", "When", "Where", "Which", "While", "Who", "Why", "With", "Well",
    "You", "Your", "Yeah", "Yes", "But", "And", "For", "Not", "Now", "Just",
    "Have", "How", "Here", "His", "Her", "Him", "She", "Let", "Look", "Listen",
    "Come", "Can", "Did", "Does", "Don", "Doing", "Been", "Because", "Before",
    "After", "Again", "All", "Any", "Are", "Was", "Were", "Will", "Would",
    "Should", "Could", "Maybe", "Sorry", "Please", "Right", "Really", "Sure",
    "Even", "Ever", "Every", "Something", "Someone", "Nothing",
}


# ตัวประกอบไทยที่ห้ามอยู่ต้นคำ — ถ้าโผล่ที่ตำแหน่ง 1 แปลว่าตัดกลางพยางค์
# (`อาร์เนสต์` -> `ร์เนสต์` · ผู้แปลก้อน MSG_082 รายงาน 3 ก.ย. 2026)
BAD_SECOND = "์"


def longest_common_thai(values: list, min_len: int = MIN_NAME_CHARS) -> list:
    """สตริงไทยที่ยาวที่สุดซึ่งปรากฏในทุกค่าของ values — คืน **ทุกตัวที่ยาวเท่ากัน**

    คืนหลายตัวเมื่อกำกวม (เช่น `William Bradley` โผล่คู่กันทุกคู่ ทำให้ทั้ง
    `วิลเลียม` และ `แบรดลีย์` ยาวเท่ากัน) — ผู้เรียกต้องทิ้งกรณีกำกวมไป
    """
    base = min(values, key=len)
    best_len = 0
    found = []
    for run in THAI_RUN.findall(base):
        for i in range(len(run)):
            for j in range(len(run), i + min_len - 1, -1):
                sub = run[i:j]
                if len(sub) < best_len:
                    break
                if not all(sub in v for v in values):
                    continue
                if len(sub) > best_len:
                    best_len, found = len(sub), [sub]
                elif sub not in found:
                    found.append(sub)
                break
    return found


def mine_names(strings: list, master: dict, known: dict) -> dict:
    """ชื่อเฉพาะในก้อนนี้ที่ master เคยเคาะรูปไทยไว้แล้ว แต่ lexicon มองไม่เห็น"""
    blob = "\n".join(strings)
    # ต้องเคยโผล่กลางประโยคอย่างน้อยหนึ่งครั้ง (ไม่ใช่ตัวใหญ่เพราะขึ้นต้นประโยคเฉย ๆ)
    mid = set(re.findall(r"(?<=[a-z,] )([A-Z][a-z]{3,})(?![A-Za-z])", blob))
    out = {}
    for name in sorted(mid - NOT_A_NAME):
        if name in known:
            continue
        pat = re.compile(r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])")
        values = [th for en, th in master.items() if th and pat.search(en)]
        if len(values) < MIN_NAME_PAIRS:
            continue
        cands = [
            t for t in longest_common_thai(values)
            # ต้องไม่ตัดกลางพยางค์ และต้องไม่ยาวเกินสัดส่วนทับศัพท์ปกติ
            # (`Tatsu` -> `ยูเมโนทัตสึคุดากิ` = ชื่อดาบทั้งชื่อ ไม่ใช่ชื่อคน)
            if len(t) >= MIN_NAME_CHARS
            and t[1:2] != BAD_SECOND
            and len(t) <= MAX_NAME_RATIO * len(name)
        ]
        # กำกวม (สองชื่อโผล่คู่กันเสมอ) = แยกไม่ออกว่าอันไหนคือชื่อนี้ -> ทิ้ง
        if len(cands) != 1:
            continue
        th = cands[0]
        # ⚠ ด่านกรองความแม่น — สตริงไทยร่วมอาจเป็น "คำสามัญ" ที่บังเอิญอยู่ในทุกคู่
        # (เช่น Oharu -> "น้องสาว" · Land -> "กที่") ไม่ใช่รูปทับศัพท์ของชื่อ
        # เกณฑ์: ถ้าคำนั้นโผล่ในคู่ที่ EN **ไม่มี** ชื่อนี้เกินหนึ่งในห้า = เป็นคำสามัญ ทิ้ง
        total = sum(1 for v in master.values() if isinstance(v, str) and th in v)
        if total == 0 or len(values) / total < NAME_PRECISION:
            continue
        out[name] = th
    return out


def hints_for(batch: str, lex: dict) -> dict:
    path = WORKLIST / f"batch_{batch}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    strings = list(data["strings"])
    blob = "\n".join(strings)
    out = {}
    for en, th in lex.items():
        # คำเดี่ยวต้องตรงขอบคำ ป้องกัน "Gold" ไปแมตช์ใน "Golden"
        pat = r"(?<![A-Za-z])" + re.escape(en) + r"(?![A-Za-z])"
        if re.search(pat, blob):
            out[en] = th
    return out


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("ต้องระบุเลข batch เช่น: python scripts/make_prior_hints.py 030 031")
        return 1
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    lex = load_lexicon()
    locks = load_locks()
    print(f"lexicon จาก master: {len(lex):,} คำ/ป้าย · คำล็อกชื่อคน/สถานที่: {len(locks):,}")
    for batch in args:
        batch = batch.zfill(3)
        hints = hints_for(batch, lex)
        lock_hits = hints_for(batch, locks)
        hints = {k: v for k, v in hints.items() if k not in lock_hits}
        strings = list(json.loads(
            (WORKLIST / f"batch_{batch}.json").read_text(encoding="utf-8"))["strings"])
        mined = mine_names(strings, master, {**lex, **locks})
        dest = WORKLIST / f"batch_{batch}.prior.json"
        locked = {k: v for k, v in hints.items() if len(k.split()) > 1}
        context = {k: v for k, v in hints.items() if len(k.split()) == 1}
        payload = {
            "batch": batch,
            "readme": (
                "คำที่ 'เคาะไปแล้ว' ในก้อนก่อนหน้า และโผล่อยู่ในสตริงของก้อนนี้ "
                "ดึงจาก master_th.json อัตโนมัติ"
            ),
            "how_to_use": {
                "locked_names_places": "คำล็อกจาก name_locks.json / place_locks.json — "
                                       "**บังคับ** ต้องสะกดตามนี้เป๊ะ",
                "terms": "ชื่อเฉพาะ/วลี — ใช้รูปนี้เท่านั้น ห้ามตั้งใหม่ "
                         "ถ้าเห็นว่ารูปเดิมผิดจริง ให้รายงาน lead อย่าเปลี่ยนเอง",
                "names_from_master": "ชื่อเฉพาะที่ master เคยเคาะรูปไทยไว้แล้ว แต่ไม่เคยเป็นคีย์สั้น "
                                     "จึงไม่เข้า lexicon — ขุดด้วยการหาสตริงไทยร่วมของทุกคู่ที่ EN มีชื่อนั้น "
                                     "**ใช้รูปนี้ ห้ามตั้งใหม่**",
                "single_words": "คำเดี่ยว — เป็นคำแปลของ **บริบทอื่น** อาจไม่ตรงบริบทก้อนนี้ "
                                "(เช่น Result = 'ผลการซื้อขาย' มาจากหน้าร้านค้า) "
                                "ให้ใช้เมื่อบริบทตรงกันเท่านั้น",
            },
            "locked_names_places": dict(sorted(lock_hits.items(), key=lambda kv: -len(kv[0]))),
            "names_from_master": dict(sorted(mined.items())),
            "terms": dict(sorted(locked.items(), key=lambda kv: -len(kv[0]))),
            "single_words": dict(sorted(context.items())),
        }
        dest.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"batch_{batch}: ล็อก {len(lock_hits):,} + จาก master {len(hints):,} "
              f"+ ชื่อที่ขุดได้ {len(mined):,} -> {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
