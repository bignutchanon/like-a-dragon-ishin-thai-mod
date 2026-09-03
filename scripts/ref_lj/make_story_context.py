#!/usr/bin/env python3
"""ดึง "บริบทเนื้อเรื่อง" ที่ทีมแปลต้องใช้ ออกจากไฟล์เกมโดยตรง

ทำไมต้องมี: นักแปลเห็นบทเป็นบรรทัดลอย ๆ ไม่รู้ว่าฉากไหน ใครเป็นใคร คดีอะไร
ข้อมูลพวกนี้ **มีอยู่ในเกมอยู่แล้ว** ในสองที่ที่ไม่มีใครแตะ:

  mission_title.bin  ->  `msg_story` = **เรื่องย่อของแต่ละบท** (เขียนโดยทีมสร้างเกม)
  evidence.bin       ->  ตาราง `coyote_evidence_*` คอลัมน์ 7 = ชื่อคน/หลักฐาน · 8 = คำอธิบาย
                         (= แฟ้มคดีในเกม บอกความสัมพันธ์/บทบาทของตัวละครแทบทุกคนในคดี)

ดีกว่าวิกิตรงที่ตรงกับสคริปต์ที่เราต้องแปลจริง ๆ และไม่มีข้อมูลผิด

ผลลัพธ์:
  extracted/facts/story_chapters.json   [{id, title, summary, loading}]
  extracted/facts/evidence.json         {ชื่อคดี: [{name, desc}]}
  docs/reference/story_context_lj.md    เอกสารอ่านคน (⚠ สปอยล์ทั้งไฟล์)

ใช้:  python scripts/make_story_context.py [--write]
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

MISSION_TITLE = paths.DB_EN / "mission_title.bin.json"
EVIDENCE = paths.DB_EN / "evidence.bin.json"
CHAPTERS = paths.EXTRACTED / "facts" / "chapters.json"
OUT_CH = paths.EXTRACTED / "facts" / "story_chapters.json"
OUT_EV = paths.EXTRACTED / "facts" / "evidence.json"
OUT_MD = paths.DOCS / "reference" / "story_context_lj.md"

CASE_TITLE = {
    "main_case": "คดีหลัก (เนื้อเรื่อง)",
    "side_case": "คดีเสริม",
    "school": "เนื้อเรื่องโรงเรียน (School Stories)",
    "dlc": "The Kaito Files (DLC)",
}


def load(p):
    return json.load(io.open(p, encoding="utf-8"))


def chapter_stories():
    """[{id, title, summary, loading}] จาก mission_title.bin"""
    data = load(MISSION_TITLE)
    titles = {c["id"]: c["name"] for c in load(CHAPTERS)} if CHAPTERS.exists() else {}
    out = []
    for row_key, row in data.items():
        if not isinstance(row, dict):
            continue
        for name, cols in row.items():
            if not isinstance(cols, dict) or not name:
                continue
            story = cols.get("msg_story") or ""
            if not isinstance(story, str) or len(story) < 20:
                continue
            m = re.search(r"c(\d+)$", name)
            cid = "chapter%d" % int(m.group(1)) if m else name
            out.append({
                "row": row_key, "id": name,
                "chapter_title": titles.get(cid, ""),
                "summary": story,
                "loading": cols.get("msg_loading_story") or "",
            })
    out.sort(key=lambda r: r["id"])
    return out


def evidence_files():
    """{ชื่อตารางคดี: [{name, desc}]} จาก evidence.bin (คอลัมน์ 7 = ชื่อ · 8 = คำอธิบาย)"""
    data = load(EVIDENCE)
    out = collections.OrderedDict()

    def walk(node):
        if not isinstance(node, dict):
            return
        for key, val in node.items():
            if isinstance(key, str) and key.startswith("coyote_evidence") and isinstance(val, dict):
                table = val.get("table")
                rows = []
                if isinstance(table, dict):
                    for rk, rv in table.items():
                        if not rk.isdigit() or not isinstance(rv, dict):
                            continue
                        cell = rv.get("", {})
                        if not isinstance(cell, dict):
                            continue
                        nm, desc = cell.get("7"), cell.get("8")
                        if isinstance(nm, str) and nm.strip():
                            rows.append({"name": nm.strip(),
                                         "desc": (desc or "").strip() if isinstance(desc, str) else ""})
                if rows:
                    out[key] = rows
            walk(val)

    walk(data)
    return out


def group_of(case_key):
    if "main_case" in case_key:
        return "main_case"
    if "dlc" in case_key:
        return "dlc"
    if "school" in case_key or "sc_" in case_key:
        return "school"
    return "side_case"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    chapters = chapter_stories()
    evidence = evidence_files()
    people = sum(len(v) for v in evidence.values())
    print("เรื่องย่อรายบท %d · แฟ้มคดี %d ชุด · รายการในแฟ้มรวม %d"
          % (len(chapters), len(evidence), people))
    for c in chapters[:3]:
        print("   %-16s %s" % (c["id"], (c["chapter_title"] or c["summary"])[:70]))

    if not a.write:
        print("(ใส่ --write เพื่อเขียนไฟล์)")
        return 0

    OUT_CH.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT_CH, "w", encoding="utf-8", newline="\n").write(
        json.dumps(chapters, ensure_ascii=False, indent=1) + "\n")
    io.open(OUT_EV, "w", encoding="utf-8", newline="\n").write(
        json.dumps(evidence, ensure_ascii=False, indent=1) + "\n")

    L = ["# บริบทเนื้อเรื่อง — Lost Judgment (ดึงจากไฟล์เกม)", "",
         "> สร้างด้วย `python scripts/make_story_context.py --write` ·",
         "> ข้อมูลดิบ: `extracted/facts/story_chapters.json` + `evidence.json`", "",
         "## ⚠ ไฟล์นี้สปอยล์ทั้งฉบับ",
         "ข้อความทั้งหมดคัดมาจากไฟล์เกมตรง ๆ (`mission_title.bin` = เรื่องย่อรายบทที่ทีมสร้างเกมเขียนเอง ·",
         "`evidence.bin` = แฟ้มคดีในเกม) — ใช้ตอนแปลเพื่อรู้ว่า **ฉากนี้เกิดอะไร ใครเป็นใคร**",
         "ห้ามเอาไปเขียนคำแปลที่เฉลยล่วงหน้ามากกว่าต้นฉบับ", "",
         "## วิธีใช้",
         "1. ไม่รู้ว่าบรรทัดที่แปลอยู่ในฉากไหน → ดูช่อง `chapter` ใน `batch_NNN.context.json` แล้วมาอ่านบทนั้น",
         "2. ไม่รู้ว่าตัวละครนี้เป็นใคร/เกี่ยวอะไรกับคดี → ค้นชื่อในหัวข้อ \"แฟ้มคดี\" ด้านล่าง",
         "3. คำเรียกตำแหน่ง/ความสัมพันธ์ในแฟ้มคดี = คำที่ควรใช้ให้ตรงกันทั้งเกม (ยืนยันกับ glossary ก่อน)", "",
         "---", "", "## เรื่องย่อรายบท (จาก `mission_title.bin` · คอลัมน์ `msg_story`)", ""]
    for c in chapters:
        head = c["chapter_title"] or c["id"]
        L += ["### %s  <sub>`%s`</sub>" % (head, c["id"]), "", "```", c["summary"], "```", ""]
        if c["loading"] and c["loading"] != c["summary"]:
            L += ["ข้อความตอนโหลด (สำนวนที่สอง — **ต้องแปลด้วย**):", "", "```", c["loading"], "```", ""]

    L += ["---", "", "## แฟ้มคดี (จาก `evidence.bin`) — ใครเป็นใคร", ""]
    by_group = collections.OrderedDict()
    for case, rows in evidence.items():
        by_group.setdefault(group_of(case), []).append((case, rows))
    for g, items in by_group.items():
        L += ["### %s" % CASE_TITLE.get(g, g), ""]
        for case, rows in items:
            L += ["#### `%s` (%d รายการ)" % (case, len(rows)), "",
                  "| ชื่อ/หลักฐาน | คำอธิบายในเกม |", "|---|---|"]
            for r in rows:
                desc = r["desc"].replace("\n", " ").replace("|", "\\|")
                L.append("| **%s** | %s |" % (r["name"].replace("|", "\\|"), desc))
            L.append("")
    io.open(OUT_MD, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("เขียน %s\nเขียน %s\nเขียน %s" % (OUT_CH, OUT_EV, OUT_MD))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
