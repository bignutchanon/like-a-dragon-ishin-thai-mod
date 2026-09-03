#!/usr/bin/env python3
"""สร้าง "ทะเบียนชื่อท่า/ชื่อตระกูล" (glossary §1.9.7) จาก `master_th.json` แล้วเขียนทับหมวดนั้น

ทำไมต้องมี: ชื่อท่าและชื่อตระกูลไอเทม (ตรา · คัมภีร์ · ดาบในตำนาน) ถูกเคาะไปแล้วในก้อนก่อน
แต่ไม่เคยถูกเขียนลง glossary — มีแต่ปรากฏใน `.done.json` นักแปลก้อนถัดไปจึงมองไม่เห็น
แล้วตั้งชื่อใหม่ชนกัน (คลื่น 018-029 เจอ 28 + 47 จุด · คลื่น 030-041 เจออีก 1 จุดในตระกูลตรา)
HANDOFF สั่งให้ lead อัปเดตหมวดนี้ด้วยมือหลัง merge ทุกครั้ง — สคริปต์นี้ทำแทน

ใช้:
  python scripts/make_skill_registry.py            # เขียนทับ §1.9.7 ใน glossary.md
  python scripts/make_skill_registry.py --print    # แค่พิมพ์ดู ไม่แตะไฟล์
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

# แพตเทิร์นของ "ชื่อที่ต้องสะกดเหมือนกันทั้งเกม" — คีย์ที่ EN ยืนเดี่ยว (ไม่ใช่ประโยค)
PATTERNS = [
    re.compile(r"^Essence of .+$"),
    re.compile(r"^(Swordsman|Gunman|Wild Dancer|Brawler) Rank \d+$"),
    re.compile(r"^Splendid Skill: .+$"),
    re.compile(r"^Komaki .+$"),
    re.compile(r"^(Exclusive|Sword|Square|Sphere|Gun) Seal: .+$"),
    re.compile(r"^Book of Revelations: .+$"),
    re.compile(r"^Phoenix (Clash|Battle|War)$"),
]

HEADING = "### 1.9.7 ทะเบียนชื่อท่า"
NEXT_HEADING = re.compile(r"^### (?!1\.9\.7)", re.M)


def collect():
    master = json.loads(paths.MASTER_TH.read_text(encoding="utf-8"))
    rows = {}
    for en, th in master.items():
        if "\n" in en or not isinstance(th, str) or not th.strip():
            continue
        if any(p.match(en) for p in PATTERNS):
            rows[en] = th.strip()
    return dict(sorted(rows.items()))


def render(rows):
    out = [
        HEADING + " · ชื่อตระกูลไอเทม (สร้างจาก `master_th.json` — **ตัวตรวจคำล็อกอ่านหมวดนี้**)",
        "",
        "> สร้างอัตโนมัติด้วย `python scripts/make_skill_registry.py` — **ห้ามแก้ด้วยมือ**",
        "> แก้ที่คำแปลในก้อนต้นทางแล้ว merge ใหม่ จากนั้นรันสคริปต์นี้ซ้ำ",
        "",
        "รูปที่ใช้คือรูปของคีย์ที่ EN เป็น **ชื่อยืนเดี่ยว** = ชื่อที่โชว์ในเมนูจริง",
        f"ปัจจุบันมี **{len(rows)} ชื่อ**",
        "",
        "| EN | ไทย |",
        "|---|---|",
    ]
    out += [f"| {en} | {th} |" for en, th in rows.items()]
    out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print", action="store_true", dest="only_print")
    a = ap.parse_args()
    rows = collect()
    block = render(rows)
    if a.only_print:
        print(block)
        return 0
    p = paths.TRANSLATIONS / "glossary.md"
    text = p.read_text(encoding="utf-8")
    i = text.find(HEADING)
    if i < 0:
        print(f"ไม่พบหัวข้อ {HEADING} ใน glossary.md")
        return 1
    m = NEXT_HEADING.search(text, i + len(HEADING))
    j = m.start() if m else len(text)
    p.write_text(text[:i] + block + "\n" + text[j:], encoding="utf-8")
    print(f"เขียน §1.9.7 ใหม่: {len(rows)} ชื่อ -> {p.relative_to(paths.PROJECT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
