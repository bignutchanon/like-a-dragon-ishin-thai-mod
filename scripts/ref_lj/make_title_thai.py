#!/usr/bin/env python3
"""สร้าง PoC ภาษาไทยหน้าไตเติลของ Lost Judgment

ทำสองไฟล์ลง `build/text/db.coyote.en/`:
  1. `title_root.bin`  — เมนูหน้าไตเติลเป็นไทย (encode เป็น donor slot ตาม `thai_encode.py`)
  2. `font2_face.bin`  — อัปเดต `texture_height` ของ `metaoffcpro-condbook` ให้ตรงกับ atlas
     ที่ `inject_thai_sdf.py --grow` ขยายไว้ (1024 -> 1184) เพราะ LJ เก็บขนาด atlas ไว้ใน db ด้วย
     (ต่างจาก Y8 ที่อ่านจาก DDS header + aux อย่างเดียว)

ข้อความที่เป็น license/เครดิต คงอังกฤษไว้ตามกติกาเหล็กข้อ 10

ใช้:  python scripts/make_title_thai.py
อ่าน  extracted/db_en/{title_root,font2_face}.bin.json (ต้นฉบับ — ไม่แตะ)
เขียน build/text/db.coyote.en/*.bin + build/text/TITLE_POC.md
"""
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                                  # noqa: E402
from thai_encode import encode, coverage      # noqa: E402

STAGE = paths.BUILD / "text" / "db.coyote.en"
WORK = paths.BUILD / "text" / "_work"
REPORT = paths.BUILD / "text" / "TITLE_POC.md"

# ชื่อ face ที่ฉีดกลิฟไทยไว้ -> ความสูง atlas ใหม่ (ต้องตรงกับ build/font/<face>.dds)
ATLAS_HEIGHT = {"metaoffcpro-condbook": 1184}

# (row_key, column, ข้อความไทย)
EDITS = [
    ("new_game", "name", "เริ่มเกมใหม่"),
    ("new_game", "explanation", "เริ่มเล่นตั้งแต่ต้นเรื่อง"),
    ("new_game_after_clear", "name", "เริ่มเกมใหม่"),
    ("new_game_after_clear", "explanation", "เริ่มเล่นตั้งแต่ต้นเรื่อง"),
    ("continue", "name", "เล่นต่อ"),
    ("continue", "explanation", "เล่นต่อจากไฟล์เซฟ"),
    ("continue_after_clear", "name", "เล่นต่อ"),
    ("continue_after_clear", "explanation", "เล่นต่อจากไฟล์เซฟ"),
    ("option", "name", "ตั้งค่าเกม"),
    ("option", "explanation", "ปรับตั้งค่าที่มีผลต่อการเล่น"),
    ("audio_option", "name", "ตั้งค่าเสียง"),
    ("audio_option", "explanation", "ปรับตั้งค่าเสียงในเกม"),
    ("movie", "name", "ดูฉากย้อนหลัง"),
    ("movie", "explanation", "ดูฉากเนื้อเรื่องหลักที่เคยผ่านมาแล้ว"),
    ("coyote_premium_adventure", "name", "พรีเมียมแอดเวนเจอร์"),
    ("coyote_premium_adventure", "explanation", "ตะลุยเมืองได้อิสระโดยไม่ต้องเดินตามเนื้อเรื่องหลัก"),
    ("coyote_photo_gallery", "name", "คลังภาพถ่าย"),
    ("coyote_photo_gallery", "explanation", "ดูภาพที่ถ่ายด้วยมือถือในเกม"),
    ("kaito_story_root", "name", "แฟ้มคดีไคโตะ"),
    ("kaito_story_root", "explanation", "เริ่มเนื้อหาเสริมที่มีมาซาฮารุ ไคโตะเป็นตัวเอก"),
    ("profile_change", "name", "เปลี่ยนโปรไฟล์"),
    ("profile_change", "explanation", "สลับผู้ใช้ที่กำลังเล่นอยู่"),
    ("quit_game", "name", "ออกจากเกม"),
    ("quit_game", "explanation", "จบเกมแล้วกลับสู่เดสก์ท็อป"),
    ("gauntlet", "name", "เดอะ กอนต์เล็ต"),
    ("difficulty_easy", "name", "ง่าย"),
    ("difficulty_normal", "name", "ปกติ"),
    ("difficulty_hard", "name", "ยาก"),
    ("difficulty_legend", "name", "ตำนาน"),
    ("difficulty_ex_easy", "name", "ง่ายมาก"),
]


def rearmp(json_path):
    """JSON -> .bin (ทำงานใน WORK) — คืน path ของ .bin"""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, str(paths.REARMP), json_path.name],
                       cwd=str(WORK), env=env, capture_output=True, timeout=1800)
    out = WORK / (json_path.name + ".bin")
    if r.returncode != 0 or not out.exists() or out.stat().st_size == 0:
        err = r.stderr.decode("utf-8", "replace").strip().splitlines()
        sys.exit("reARMP ล้ม (%s): %s" % (json_path.name, err[-1] if err else "?"))
    return out


def rows(doc):
    """คืน (index, row_key, fields) ของทุกแถว"""
    for i in range(doc["ROW_COUNT"]):
        for key, fields in doc[str(i)].items():
            yield i, key, fields


def build_title():
    src = paths.EXTRACTED / "db_en" / "title_root.bin.json"
    doc = json.load(io.open(src, encoding="utf-8"))
    index = {key: fields for _, key, fields in rows(doc)}

    log = []
    for key, col, th in EDITS:
        fields = index.get(key)
        if fields is None:
            sys.exit("ไม่พบแถว %r ใน title_root.bin" % key)
        miss = coverage(th)
        if miss:
            sys.exit("ตัวอักษรไทยไม่มีใน slot map: %s (%r)" % (miss, th))
        en = fields.get(col, "")
        fields[col] = encode(th)
        log.append((key, col, en, th, fields[col]))
    return doc, log


def build_font2_face():
    src = paths.EXTRACTED / "db_en" / "font2_face.bin.json"
    doc = json.load(io.open(src, encoding="utf-8"))
    changed = []
    for _, key, fields in rows(doc):
        if key in ATLAS_HEIGHT and "texture_height" in fields:
            old = fields["texture_height"]
            new = ATLAS_HEIGHT[key]
            if old != new:
                fields["texture_height"] = new
                changed.append((key, old, new))
    if not changed:
        print("  font2_face: ไม่มีอะไรต้องแก้ (ความสูง atlas ตรงอยู่แล้ว)")
    return doc, changed


def write_report(log, atlas_changes):
    L = ["# PoC ไตเติลภาษาไทย — Lost Judgment", "",
         "> สร้างด้วย `python scripts/make_title_thai.py` — ห้ามแก้ด้วยมือ", "",
         "ฟอนต์ที่ต้องคู่กัน: `build/font/metaoffcpro-condbook.{bin,dds}` "
         "(สร้างด้วย `python scripts/inject_thai_sdf.py metaoffcpro-condbook --grow`)", ""]
    if atlas_changes:
        L += ["## `font2_face.bin`", "",
              "| face | texture_height เดิม | ใหม่ |", "|---|---|---|"]
        L += ["| %s | %d | %d |" % c for c in atlas_changes]
        L.append("")
    L += ["## `title_root.bin`", "",
          "| แถว | คอลัมน์ | อังกฤษ | ไทย | donor ที่ encode ออกมา |", "|---|---|---|---|---|"]
    for key, col, en, th, enc in log:
        L.append("| `%s` | %s | %s | %s | `%s` |"
                 % (key, col, en.replace("\n", " / ")[:60], th, enc))
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    io.open(REPORT, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")


def main():
    STAGE.mkdir(parents=True, exist_ok=True)
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    title_doc, log = build_title()
    face_doc, atlas_changes = build_font2_face()

    for name, doc in (("title_root", title_doc), ("font2_face", face_doc)):
        if name == "font2_face" and not atlas_changes:
            continue
        jp = WORK / ("%s.bin.json" % name)
        io.open(jp, "w", encoding="utf-8", newline="\n").write(
            json.dumps(doc, ensure_ascii=False, indent=1))
        out = rearmp(jp)
        dst = STAGE / ("%s.bin" % name)
        shutil.copy2(out, dst)
        print("เขียน %s (%s B)" % (dst, "{:,}".format(dst.stat().st_size)))

    write_report(log, atlas_changes)
    print("แก้ %d ช่อง · รายงาน: %s" % (len(log), REPORT))


if __name__ == "__main__":
    main()
