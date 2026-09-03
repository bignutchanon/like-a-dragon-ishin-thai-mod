#!/usr/bin/env python3
"""ดึง "ข้อเท็จจริงจากไฟล์เกม" ที่นักแปล/ทีมวิจัยต้องใช้ ออกมาเป็นไฟล์อ่านง่าย

ทำไมต้องมี: ทีมวิจัยเนื้อหา (story / ตัวละคร / side content / glossary) ต้องอ้างอิง **ข้อมูลจริง
จากเกม** ไม่ใช่ wiki อย่างเดียว — บทเรียนจาก K3 คือ wiki ผิดบ่อย (ชื่อบท สังกัด บทบาท) และ
ชื่อผู้พูดที่โผล่ในเกมจริงมีเยอะกว่าที่ wiki ลงไว้มาก

อ่านจาก JSON ที่ `extract_all_en.py` แปลงไว้แล้ว (ไม่แตะไฟล์เกม) แล้วเขียน:
  extracted/facts/<ชื่อ>.json      — ข้อมูลดิบต่อหมวด (ให้ agent/สคริปต์อ่าน)
  docs/reference/lj_extract_facts.md — สรุปอ่านคน + รายชื่อผู้พูดครบทุกชื่อ

ใช้:  python scripts/make_translator_facts.py
"""
import io
import json
import os
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

BINS = paths.DB_EN
FACTS = paths.EXTRACTED / "facts"
OUT_MD = paths.DOCS / "reference" / "lj_extract_facts.md"

META_KEYS = {"VERSION", "REVISION", "ROW_COUNT", "COLUMN_COUNT", "TEXT_COUNT", "ROW_VALIDATOR",
             "COLUMN_VALIDATOR", "HAS_ROW_NAMES", "HAS_COLUMN_NAMES", "HAS_ROW_VALIDITY",
             "HAS_COLUMN_VALIDITY", "HAS_UNKNOWN_BITMASK", "HAS_ROW_INDICES", "TABLE_ID",
             "STORAGE_MODE", "columnTypes", "columnValidity"}
SKIP_FIELDS = {"reARMP_isValid", "reARMP_rowIndex"}


def load(bin_name):
    p = BINS / (bin_name + ".json")
    if not p.exists():
        return None
    return json.load(io.open(p, encoding="utf-8"))


def rows(data):
    """คืน [(row_name, {คอลัมน์: ค่า})] ตามลำดับแถวจริงในตาราง"""
    out = []
    for k, v in data.items():
        if k in META_KEYS or not isinstance(v, dict):
            continue
        for row_name, cols in v.items():
            if isinstance(cols, dict):
                out.append((row_name, cols))
    return out


def text_fields(cols, prefix=""):
    """คอลัมน์ที่เป็นข้อความจริง — เดินลง sub-table ด้วย (บางตารางเก็บข้อความลึกหนึ่งชั้น
    เช่น `evidence_item_to_update.bin` ที่ประวัติบุคคลอยู่ใน column `table`)"""
    out = OrderedDict()
    for k, v in cols.items():
        if k in SKIP_FIELDS or k in META_KEYS:
            continue
        key = (prefix + "." + str(k)) if prefix else str(k)
        if isinstance(v, str) and v.strip():
            out[key] = v
        elif isinstance(v, dict):
            out.update(text_fields(v, key))
    return out


def collect(bin_name, want=None, require=None):
    """ดึงแถวที่มีข้อความ -> [{"id":.., "idx":.., ...ฟิลด์ข้อความ}]"""
    data = load(bin_name)
    if data is None:
        return []
    out = []
    for i, (row_name, cols) in enumerate(rows(data)):
        tf = text_fields(cols)
        if want:
            tf = OrderedDict((k, v) for k, v in tf.items() if k in want)
        if not tf:
            continue
        if require and not all(k in tf for k in require):
            continue
        ent = OrderedDict(id=row_name, idx=i)
        ent.update(tf)
        out.append(ent)
    return out


# แต่ละหมวด: (ชื่อผลลัพธ์, bin, คำอธิบาย, คอลัมน์ที่เอา (None = ทุกคอลัมน์ข้อความ), คอลัมน์บังคับ)
SECTIONS = [
    ("speakers", "talk_talker.bin", "ชื่อผู้พูดทั้งหมด (key = ชื่อญี่ปุ่นในไฟล์ · `talk_talker` = ชื่อที่โชว์บนจอ EN)",
     None, None),
    ("chapters", "title_movie_chapter.bin", "ชื่อบท (main story + Majima Saga)", None, None),
    ("missions", "mission_mission_kind.bin", "ภารกิจ/คดี — ทั้ง Main Case, Side Case และงานย่อย",
     None, None),
    ("friends", "character_friend_list.bin", "ระบบเพื่อน (Friends) — ชื่อ + คำอธิบายของแต่ละคน",
     None, None),
    ("skills", "player_skill.bin", "สกิลของยางามิ (ชื่อ + คำอธิบาย + เงื่อนไขปลดล็อก)", None, None),
    ("items", "item.bin", "ไอเทม/แฟ้มคดี/ของสะสม (ชื่อ + คำอธิบาย)", None, None),
    ("evidence", "evidence_item_to_update.bin", "ประวัติบุคคล/หลักฐานที่อัปเดตตามเนื้อเรื่อง",
     None, None),
    ("complete", "complete.bin", "รายการ completion (ชี้ว่ามี side content อะไรบ้าง)", None, None),
    ("complete_checklist", "complete_checklist.bin", "หมวดของ completion list", None, None),
    ("popup_names", "character_npc_popup_text.bin", "ป้ายชื่อ NPC ที่เด้งขึ้นบนจอ", None, None),
    ("npc_names", "character_npc_soldier_name_group.bin", "ชื่อกลุ่ม NPC ทั่วเมือง", None, None),
    ("scenario_summary", "scene_scenario_explanation.bin", "สรุปเนื้อเรื่องย่อของแต่ละตอน (ในเกม)",
     None, None),
    ("help", "help.bin", "หัวข้อ help — ชี้ระบบทั้งหมดที่เกมมี", None, None),
    ("manual", "manual.bin", "คู่มือในเกม (กติกามินิเกมทั้งหมด)", None, None),
    ("ui_text", "ui_text.bin", "ข้อความ UI รวม", None, None),
    ("talk_select", "talk_select_select.bin", "ตัวเลือกบทสนทนา", None, None),
    ("trophy", "trophy.bin", "ถ้วยรางวัล (สปอยล์โครงเรื่องระดับหยาบ)", None, None),
    ("places", "map_place.bin", "สถานที่ในเมือง (ชื่อ + คำบรรยาย)", None, None),
    ("complete_group", "complete_group.bin", "หมวดของ completion list", None, None),
    ("shops", "shop.bin", "ร้านค้าในเมือง", None, None),
]


def main():
    FACTS.mkdir(parents=True, exist_ok=True)
    summary = []
    speakers = []
    for name, bin_name, desc, want, req in SECTIONS:
        data = collect(bin_name, want, req)
        if not data:
            summary.append((name, bin_name, desc, 0, None))
            continue
        p = FACTS / (name + ".json")
        io.open(p, "w", encoding="utf-8", newline="\n").write(
            json.dumps(data, ensure_ascii=False, indent=1) + "\n")
        summary.append((name, bin_name, desc, len(data), p))
        if name == "speakers":
            speakers = data

    L = ["# ข้อเท็จจริงจากไฟล์เกม Lost Judgment — สำหรับทีมวิจัย/นักแปล", "",
         "> สร้างด้วย `python scripts/make_translator_facts.py` จาก JSON ที่แตกไว้แล้ว",
         "> (`extracted/db_en/*.bin.json`) · ข้อมูลดิบรายหมวดอยู่ที่ `extracted/facts/*.json`",
         "",
         "**กติกาการใช้**: ข้อมูลในไฟล์นี้คือ *ของจริงจากเกม* — ถ้าขัดกับ wiki ให้เชื่อไฟล์นี้",
         "และจดความขัดแย้งไว้ในรายงาน (บทเรียน K3: wiki ผิดเรื่องชื่อบท/สังกัด/บทบาทบ่อย)", "",
         "## หมวดข้อมูลที่ดึงมาแล้ว", "",
         "| หมวด | ไฟล์ต้นทาง | รายการ | คำอธิบาย |", "|---|---|---|---|"]
    for name, bin_name, desc, n, p in summary:
        L.append("| `%s` | `%s` | %s | %s |" % (name, bin_name, n if n else "— (ไม่มีไฟล์)", desc))

    # ---- รายชื่อผู้พูดครบ (ตัวสำคัญที่สุดสำหรับทีมตัวละคร) ----
    named = [s for s in speakers if s.get("talk_talker")]
    L += ["", "## รายชื่อผู้พูดที่มีชื่อแสดงผลภาษาอังกฤษ (%d จาก %d แถว)" % (len(named), len(speakers)),
          "", "ครบทุกชื่อ — ทีมตัวละครต้องครอบคลุมให้หมด (หลักเดียวกับ K3: main + side ต้องรวมกันได้เท่านี้)",
          "", "| # | ชื่อในไฟล์ (JA) | ชื่อที่โชว์บนจอ (EN) |", "|---|---|---|"]
    for i, s in enumerate(named, 1):
        L.append("| %d | %s | %s |" % (i, s["id"] or "—", s["talk_talker"]))

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT_MD, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("เขียน", OUT_MD)
    for name, bin_name, desc, n, p in summary:
        print("  %-20s %6s  %s" % (name, n if n else "-", bin_name))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
