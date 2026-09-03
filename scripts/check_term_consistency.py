"""ตรวจว่า **ชื่อเฉพาะที่มีมาตรฐานอยู่แล้ว** ถูกใช้ตรงกันในทุกก้อน

ต่างจาก `check_cross_batch.py` ที่เทียบคำต่อคำ — ตัวนี้เทียบ **ตระกูลชื่อ**:
ชื่อชุดหนึ่ง (เช่น `Essence of X`) มักถูกแจกให้หลายก้อนพร้อมกัน โดยก้อนหนึ่งได้ชื่อแบบยืนเดี่ยว
(`Essence of Cornering`) ส่วนอีกก้อนได้ชื่อเดียวกันฝังอยู่ในประโยคยาว
("Transition the Essence of Cornering into...") — ทีมสองทีมจึงตั้งคำไทยคนละอย่างได้
ทั้งที่ทั้งคู่ผ่านด่านของตัวเองสะอาด

วิธีตรวจ:
  1. หาคีย์ที่ EN **เท่ากับชื่อนั้นพอดี** → คำแปลของคีย์นั้นคือ "รูปมาตรฐาน" ของชื่อ
  2. ไล่ทุกคีย์ที่ EN **มีชื่อนั้นอยู่ข้างใน** แล้วเช็กว่าคำแปลมีรูปมาตรฐานอยู่จริงไหม
  3. ถ้าชื่อเดียวกันมีรูปยืนเดี่ยวมากกว่าหนึ่งรูป = สองก้อนตั้งชนกันเอง รายงานทันที

ใช้:
    python scripts/check_term_consistency.py                     # ตระกูลที่ตั้งไว้ใน FAMILIES
    python scripts/check_term_consistency.py --pattern "Essence of (.+)"
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DONE = Path(__file__).resolve().parent.parent / "translations" / "done"

# ตระกูลชื่อที่รู้แล้วว่าถูกแจกข้ามก้อน — เพิ่มได้เมื่อเจอตระกูลใหม่
FAMILIES = [
    r"Essence of (?:the )?[A-Z][\w'\-]*(?: [A-Z]?[\w'\-]+)*",
    r"(?:Swordsman|Gunman|Wild Dancer|Brawler) Rank \d+",
    r"Splendid Skill: [\w' \-]+",
    r"Komaki [\w' \-]+",
    r"(?:Heavy Sword|Swordplay): [\w' \-]+",
    # ชื่อท่า "ทริกเกอร์" ที่โผล่ซ้ำในบทบรรยาย Revelation ของก้อนอื่น — หลุดง่ายกว่าชื่อยืนเดี่ยว
    # (ผู้ตรวจ batch_026–029 เจอ 5 จุดใน batch_028 ที่ชื่อเดียวกันเขียนคนละแบบกับ 019/020)
    r"Texas Two-Step", r"Dance of Mourning", r"Phoenix Frenzy",
    r"War Cry Counter", r"Jumping Shots", r"Tiger Drop", r"Finishing Blow", r"Rush Combo",
]


def load():
    out = {}
    for path in sorted(DONE.glob("batch_*.done.json")):
        out[path.name[6:9]] = json.loads(path.read_text(encoding="utf-8"))["strings"]
    return out


def collect(done, patterns):
    """คืน {ชื่อ: {"canon": {ไทย: [ก้อน]}, "used": [(ก้อน, en, th)]}}"""
    terms = collections.defaultdict(lambda: {"canon": collections.defaultdict(list), "used": []})
    for batch, strings in done.items():
        for en, th in strings.items():
            if not isinstance(th, str):
                continue
            for pat in patterns:
                for m in re.finditer(pat, en):
                    name = m.group(0)
                    if en.strip() == name:
                        terms[name]["canon"][th.strip()].append(batch)
                    else:
                        terms[name]["used"].append((batch, en, th))
    return terms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", action="append", help="regex ของตระกูลชื่อ (ใส่ซ้ำได้)")
    args = ap.parse_args()
    patterns = args.pattern or FAMILIES

    done = load()
    if not done:
        print("ไม่พบไฟล์ done")
        return 0
    terms = collect(done, patterns)
    print("เทียบ %d ก้อน · เจอชื่อในตระกูลที่ตรวจ %d ชื่อ" % (len(done), len(terms)))

    clashes = []
    missing = []
    for name, info in sorted(terms.items()):
        canon = info["canon"]
        if len(canon) > 1:
            clashes.append((name, dict(canon)))
            continue
        if not canon:
            continue
        (canon_th,) = canon.keys()
        for batch, en, th in info["used"]:
            if canon_th not in th:
                missing.append((name, canon_th, batch, en, th))

    print("\n[ชั้น 1] ชื่อเดียวกันมีรูปยืนเดี่ยวหลายรูป: %d ชื่อ" % len(clashes))
    for name, canon in clashes:
        print("  %s" % name)
        for th, batches in canon.items():
            print("      %-46s %s" % (th, ",".join(batches)))

    print("\n[ชั้น 2] ประโยคที่เอ่ยชื่อแต่ไม่ได้ใช้รูปมาตรฐาน: %d จุด" % len(missing))
    for name, canon_th, batch, en, th in missing[:40]:
        print("  %s  (มาตรฐาน: %s)" % (name, canon_th))
        print("      %s  %s" % (batch, th[:90]))
    if len(missing) > 40:
        print("  ... อีก %d จุด" % (len(missing) - 40))

    print("\n⚠ ชั้น 2 เป็นตัวเตือน — ประโยคที่เรียบเรียงใหม่จนไม่เอ่ยชื่อตรง ๆ ก็ติดได้")
    return 1 if (clashes or missing) else 0


if __name__ == "__main__":
    raise SystemExit(main())
