#!/usr/bin/env python3
"""สร้างตารางคำเฉพาะ (glossary seed) จากไฟล์เกมจริง — ชื่อสถานที่ · ฝ่าย · ไอเทม · ทักษะ · ยศ

ทีมแปลต้องใช้คำเดียวกันทั้งเกม แต่คำเฉพาะของ Ishin! มีหลายพันคำและกระจายอยู่สามชั้น
สคริปต์นี้ดึงออกมาเป็นตารางเดียว พร้อมสองคอลัมน์ช่วยตัดสิน:
  - **JA** ต้นฉบับญี่ปุ่นของคำเดียวกัน (คันจิบอกความหมายที่อังกฤษกลืนไป เช่น
    `Ryotei` = 料亭 ร้านอาหารญี่ปุ่นชั้นสูง ไม่ใช่ชื่อร้าน)
  - **TM** คำที่ภาคพี่น้องเคยใช้ (ถ้าสตริงตรงกันเป๊ะ) — **ร่างเท่านั้น**
    และ **ห้ามใช้กับชื่อตัวละคร** เพราะ Ishin เป็นคนละตัวละครกับซีรีส์หลัก

ผลลัพธ์: translations/glossary_seed.md (ตารางแยกหมวด) + translations/glossary_seed.json

ใช้: python scripts/make_glossary_seed.py
ต้องมีมาก่อน: scripts/build_parallel.py
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")   # console Windows = cp1252 (กติกาข้อ 5)
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                                            # noqa: E402
from make_worklist_ishin import load_tm                 # noqa: E402

# หมวด: (ชื่อหมวด, เงื่อนไข locres namespace, เงื่อนไขตาราง ARMP)
SECTIONS = [
    ("ฝ่าย/สังกัด/องค์กร", r"^correlation_person_diagram_group$", None),
    ("สถานที่ · ถนน · ร้าน", r"^(street_name|shop|walk_)", None),
    ("ชื่อไอเทม", r"^item_name$", r"^(item_|blacksmith_shop_table)"),
    ("ชื่อทักษะ/ท่า", r"^(ability_skill|normal_skill_list|leader_skill_list)$",
     r"^(taishi_(normal|leader)_skill_list|skill_)"),
    ("ชื่อการ์ดไทชิ/ทหาร", r"^card_list$", r"^taishi_card_list$"),
    ("ศัพท์ในสารานุกรม (word_list)", r"^(word_list|dictionary)", r"^dictionary_"),
    ("ชื่อกิจกรรม/ภารกิจ", r"^(activity_list_activity_name|mission_)", None),
]
MAX_LEN = 60          # คำเฉพาะยาวเกินนี้ถือเป็นประโยค ไม่ใช่คำ


def collect():
    loc = json.loads((paths.EXTRACTED / "parallel" / "locres.json")
                     .read_text(encoding="utf-8"))
    db = json.loads((paths.EXTRACTED / "parallel" / "db.json").read_text(encoding="utf-8"))
    out = {}
    for title, ns_pat, tbl_pat in SECTIONS:
        seen = {}
        if ns_pat:
            rx = re.compile(ns_pat)
            for r in loc:
                if rx.match(r["ns"]) and r["en"] and len(r["en"]) <= MAX_LEN:
                    seen.setdefault(r["en"], r["ja"])
        if tbl_pat:
            rx = re.compile(tbl_pat)
            for r in db:
                if rx.match(r["table"]) and r["en"] and len(r["en"]) <= MAX_LEN:
                    seen.setdefault(r["en"], r["ja"])
        out[title] = seen
    return out


def main():
    sections = collect()
    tm = load_tm()

    js = {t: {en: {"ja": ja, "tm": tm.get(en)} for en, ja in d.items()}
          for t, d in sections.items()}
    (paths.TRANSLATIONS / "glossary_seed.json").write_text(
        json.dumps(js, ensure_ascii=False, indent=1), encoding="utf-8")

    md = [
        "# Glossary seed — Like a Dragon: Ishin!", "",
        "สร้างโดย `scripts/make_glossary_seed.py` จากไฟล์เกมจริง — **ยังไม่ล็อกสักคำ**",
        "ใช้เป็นรายการตั้งต้นให้ lead ไล่เคาะ แล้วย้ายคำที่ตัดสินแล้วขึ้น `translations/glossary.md`",
        "",
        "| คอลัมน์ | อ่านยังไง |",
        "|---|---|",
        "| **JA** | ต้นฉบับญี่ปุ่นของคำเดียวกัน — คันจิบอกความหมายที่อังกฤษกลืนไป |",
        "| **TM** | คำที่ภาคพี่น้องเคยใช้กับสตริงเดียวกันเป๊ะ · **ร่างเท่านั้น** |",
        "",
        "⚠ **ห้ามใช้ TM กับชื่อตัวละคร** — Ishin เป็นยุคบาคุมัตสึ ตัวละครคนละคนกับซีรีส์หลัก",
        "ชื่อตัวละครดูที่ `translations/name_proposals.md` แทน",
        "",
    ]
    total = 0
    for title, d in sections.items():
        total += len(d)
        md += ["## %s (%d รายการ)" % (title, len(d)), "",
               "| EN | JA | TM (ร่าง) | ไทยที่ตัดสิน |", "|---|---|---|---|"]
        for en, ja in sorted(d.items()):
            md.append("| %s | %s | %s | |" % (
                en.replace("\n", " ").replace("|", "\\|"),
                (ja or "-").replace("\n", " ").replace("|", "\\|"),
                (tm.get(en) or "").replace("|", "\\|")))
        md.append("")
    p = paths.TRANSLATIONS / "glossary_seed.md"
    p.write_text("\n".join(md), encoding="utf-8")

    for title, d in sections.items():
        hit = sum(1 for en in d if tm.get(en))
        print("%-32s %5d รายการ · มี TM %d" % (title, len(d), hit))
    print("รวม %d รายการ -> %s" % (total, p))


if __name__ == "__main__":
    main()
