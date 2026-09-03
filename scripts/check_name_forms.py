"""หา **ชื่อเฉพาะอังกฤษหนึ่งคำที่ถูกทับศัพท์เป็นไทยหลายรูป** ข้ามก้อน

ทำไม (3 ก.ย. 2026): `check_cross_batch.py` ชั้น 2 บอกได้แค่ "คำไทยสองรูปคล้ายกัน"
แต่แยกไม่ออกว่าเป็น **ชื่อเดียวกันสะกดต่างกัน** (ต้องกวาด) หรือ **คนละชื่อจริง ๆ**
(นากาจิมะ 中島 ≠ นางาชิมะ 長島 — ตัวตรวจเดิมเตือนคู่นี้ทุกครั้งทั้งที่ถูกทั้งคู่)

ตัวนี้ทำงานจากฝั่งอังกฤษแทน: ไล่ทุกคีย์ในไฟล์ done หา token ที่ขึ้นต้นด้วยตัวใหญ่
แล้วดูว่า token เดียวกันไปอยู่กับคำไทยรูปไหนบ้าง — ถ้ามีหลายรูป **นั่นคือ drift จริง**

ใช้: python scripts/check_name_forms.py [--min 2]
"""
import argparse
import collections
import io
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DONE = ROOT / "translations" / "done"
# token อังกฤษที่ขึ้นต้นตัวใหญ่ ยาว >= 4 (สั้นกว่านี้ชนคำสามัญ)
EN_NAME = re.compile(r"(?<![A-Za-z])([A-Z][a-z]{3,})(?![A-Za-z])")
# คำไทยติดกันหนึ่งช่วง
TH_WORD = re.compile(r"[ก-๙]+")
# คำสามัญอังกฤษที่ขึ้นต้นตัวใหญ่เพราะอยู่ต้นประโยค — ไม่ใช่ชื่อ
STOP = {
    "That", "This", "What", "When", "Where", "Which", "There", "Then", "They", "Their",
    "Your", "You", "Well", "With", "Will", "Were", "Have", "Just", "Look", "Like",
    "Come", "Dont", "Cant", "Here", "Hell", "Damn", "Even", "Only", "Some", "Sure",
    "Take", "Tell", "Them", "Time", "Very", "Want", "Wait", "Well", "Were", "Wont",
    "Good", "Give", "Know", "Make", "Much", "Need", "Nice", "Okay", "Once", "Over",
    "Right", "Really", "Should", "Would", "Could", "About", "After", "Again", "Alright",
    "Because", "Before", "Being", "Better", "Everything", "First", "From", "Great",
    "Guess", "Hmph", "Huh", "Maybe", "More", "Never", "Nothing", "Please", "Something",
    "Sorry", "Still", "Thank", "Thanks", "Thats", "Think", "Those", "Though", "Understand",
    "Well", "Whats", "While", "Whoa", "Yeah", "Domain", "Division", "Captain", "Chief",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min", type=int, default=2,
                    help="รายงานเมื่อชื่อเดียวมีคำไทยกี่รูปขึ้นไป")
    a = ap.parse_args()

    # ชื่อ EN -> {คำไทยที่สะกดใกล้กัน: [ก้อน...]}
    seen = collections.defaultdict(lambda: collections.defaultdict(set))
    for path in sorted(DONE.glob("batch_*.done.json")):
        batch = path.name[len("batch_"):-len(".done.json")]
        for en, th in json.load(io.open(path, encoding="utf-8"))["strings"].items():
            if not isinstance(th, str):
                continue
            names = {m.group(1) for m in EN_NAME.finditer(en)} - STOP
            if not names or len(names) > 3:      # หลายชื่อในบรรทัดเดียว จับคู่ไม่ได้
                continue
            words = TH_WORD.findall(th)
            for n in names:
                for w in words:
                    if len(w) >= 4:
                        seen[n][w].add(batch)

    hits = 0
    for name in sorted(seen):
        forms = seen[name]
        # เก็บเฉพาะคำไทยที่ "เกือบเหมือนกัน" (ต่างกันไม่เกิน 2 ตัวอักษร และยาวใกล้กัน)
        cands = [w for w in forms if len(forms[w]) >= 1]
        groups = []
        for w in sorted(cands, key=lambda x: -len(forms[x])):
            for g in groups:
                if near(w, g[0]):
                    g.append(w)
                    break
            else:
                groups.append([w])
        for g in groups:
            if len(g) < a.min:
                continue
            hits += 1
            print("%-14s %s" % (name, " · ".join(
                "%s (%s)" % (w, ",".join(sorted(forms[w]))) for w in g)))
    print("\nรวม %d ชื่อที่มีคำไทยหลายรูป" % hits)
    print("⚠ ตัวเตือน ไม่ใช่คำตัดสิน — ชื่อพ้องรูปในอังกฤษ (Kawakami สองคน) ก็ติดได้")
    return 1 if hits else 0


# คู่อักษรที่ "สลับกันได้" ในการทับศัพท์ญี่ปุ่น — drift จริงจะต่างกันแค่ในกลุ่มนี้เท่านั้น
# (ก↔ค จาก k กลางคำ/ต้นคำ · ต↔ท จาก t · ด↔ต · ซ↔ส จาก s/su · สระสั้น-ยาว · ะ/็ หายไป)
SWAP = [set("กค"), set("ตท"), set("ดต"), set("ซส"), set("จช"), set("บพ"),
        set("ุู"), set("ิี"), set("เแ"), set("โ"), set("ะา")]
OPTIONAL = set("ะ็์ ")


def _swappable(x, y):
    return any(x in g and y in g for g in SWAP)


def near(a, b):
    """คำไทยสองรูปที่เป็น **การทับศัพท์ชื่อเดียวกัน** ไม่ใช่คนละคำ

    ต่างกันได้เฉพาะอักษรที่สลับกันได้ในการทับศัพท์ (ก↔ค · ต↔ท · ซ↔ส · สระสั้น-ยาว)
    หรือมี ะ/็ เกินมาหนึ่งตัว — ถ้าต่างกันด้วยอักษรอื่น = คนละคำ ไม่ใช่ drift
    (กันเสียงรบกวนอย่าง "หมู่สอง/หมู่สาม" · "ฝ่ายรับ/ฝ่ายรุก" ที่ถูกทั้งคู่)
    """
    if abs(len(a) - len(b)) > 1 or a == b:
        return False
    if len(a) < 4 or len(b) < 4:
        return False
    if a[0] != b[0]:
        return False
    # ระยะแฮมมิงอย่างหยาบบนคำที่ยาวเท่ากัน · คำที่ยาวต่างกัน 1 ใช้การตัดหัว/ท้าย
    if len(a) == len(b):
        diff = [(x, y) for x, y in zip(a, b) if x != y]
        return 0 < len(diff) <= 2 and all(_swappable(x, y) for x, y in diff)
    long, short = (a, b) if len(a) > len(b) else (b, a)
    # ยาวกว่าหนึ่งตัว = มี ะ/็ เกินมา และที่เหลือต้องตรงกันหรือสลับกันได้
    for i in range(len(long)):
        if long[i] in OPTIONAL and long[:i] + long[i + 1:] == short:
            return True
    return False


if __name__ == "__main__":
    sys.exit(main())
