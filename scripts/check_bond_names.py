"""check_bond_names.py — ชื่อ NPC สายสัมพันธ์ต้องตรงกันทั้งสามป้าย

เกมเรียก NPC สายสัมพันธ์ตัวเดียวกันในสามที่ ซึ่งอยู่คนละ batch กันบ่อย ๆ:
  1. `Bond with X`                          (ป้ายในเมนู)
  2. `Deepen your bond with the X.`          (คำอธิบายภารกิจ)
  3. `You have formed a bond with the X. …`  (ข้อความระบบตอนเกิดสายสัมพันธ์)

ถ้าสามป้ายใช้ชื่อไทยคนละรูป ผู้เล่นจะนึกว่าเป็นคนละคน — ตรวจครั้งแรก 3 ก.ย. 2026 เจอ **8 ตัวจาก 74**
(บุรุษไปรษณีย์/คนเดินสาร · ตาเฒ่าคนตัดฟืน/คนตัดฟืน · อุตะมารุยะ/อุตามารุยะ …)

ใช้: python scripts/check_bond_names.py        # อ่านจาก translations/master_th.json
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import paths

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

PATTERNS = (
    (re.compile(r"^Bond with (?:the )?(.+)$"), "label",
     ("สายสัมพันธ์กับ", "สานสัมพันธ์กับ")),
    (re.compile(r"^Deepen your bond with (?:the )?([^.]+)\."), "deepen",
     ("สานสัมพันธ์กับ", "สายสัมพันธ์กับ")),
    (re.compile(r"^You have formed a bond with (?:the )?([^.]+)\."), "formed",
     ("เจ้าได้ก่อร่างสายสัมพันธ์กับ",)),
)
# ตัดหางประโยคออกให้เหลือแต่ชื่อ NPC
TAIL_RE = re.compile(r"(แล้ว|ให้แน่นแฟ้น|ให้ลึกซึ้ง).*$")


def core(text, prefixes):
    for p in prefixes:
        if text.startswith(p):
            return TAIL_RE.sub("", text[len(p):]).strip()
    return None


def main():
    master = json.loads((paths.TRANSLATIONS / "master_th.json").read_text(encoding="utf-8"))
    master = master.get("strings", master)

    found = {}
    for en, th in master.items():
        for rx, slot, prefixes in PATTERNS:
            m = rx.match(en)
            if m:
                found.setdefault(m.group(1), {})[slot] = (th, prefixes)

    bad = 0
    for npc, slots in sorted(found.items()):
        names = {core(th, pref) for th, pref in slots.values()}
        names = {n for n in names if n}
        if len(names) > 1:
            bad += 1
            print("%-34s %s" % (npc, " / ".join(sorted(names))))
    print("\nNPC สายสัมพันธ์ %d ตัว · ชื่อไม่ตรงกันข้ามป้าย **%d ตัว**" % (len(found), bad))
    if bad:
        print("แก้ที่ไฟล์ translations/done/*.done.json แล้ว merge ใหม่ (ห้ามแก้ master ตรง ๆ)")


if __name__ == "__main__":
    main()
