#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ย้าย font_face_en ของสไตล์ที่ใช้ฟอนต์ vector ไปใช้ฟอนต์ SDF ที่ฉีดกลิฟไทยแล้ว

## ปัญหาที่แก้ (docs/ISSUES.md LJ-002)

ฟอนต์ในเกมมีสองชนิด แยกด้วยคอลัมน์ `type` ของ `font2_face.bin`:

- `type=1` = SDF atlas — คู่ไฟล์ `<name>.bin` + `<name>.dds` ใน `font.coyote.par`
  เป็นชนิดเดียวที่ `inject_thai_sdf.py` ฉีดกลิฟไทยเข้าไปได้
- `type=3` = ฟอนต์ vector — ไฟล์ `<name>_s.bin` โครงสร้างคนละแบบ ยังฉีดไทยไม่ได้

`font2_style.bin` มี 300 สไตล์ และ **141 สไตล์ชี้ font_face_en ไปที่ฟอนต์ vector**
ข้อความบนจอเหล่านั้นจึงวาดด้วยกลิฟละตินต้นฉบับเสมอ ไม่ว่าจะฉีด SDF ไปกี่ตัวก็ตาม
(อาการบนจอ: เทลอปสถานที่/วันที่ขึ้นเป็น `ÀûíÑÑîÀ¤ ÀûÀÿêÔÿ ÔõÔ¤äîÍôî` = ตัวละตินอ่านออก ไม่ใช่ tofu)

สคริปต์นี้แก้ที่ตารางแทนที่จะไปแตะไฟล์ฟอนต์: ชี้ `font_face_en` ของสไตล์เหล่านั้น
ไปที่ฟอนต์ SDF ตระกูลเดียวกันที่ฉีดไทยแล้ว แก้เฉพาะช่อง `_en` เท่านั้น
ภาษาอื่น (ja/zh/ko) ยังใช้ฟอนต์เดิมครบ

ใช้:
  python scripts/patch_font_styles.py            # รายงานอย่างเดียว
  python scripts/patch_font_styles.py --write     # เขียน build/text/db.coyote.en/font2_style.bin
"""
import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")           # กติกาเหล็กข้อ 6
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths                                        # noqa: E402

SRC = paths.EXTRACTED / "db_en"
OUT = paths.BUILD / "text" / "db.coyote.en"

# ฟอนต์ vector -> ฟอนต์ SDF ที่ฉีดกลิฟไทยแล้ว (ตระกูลเดียวกันก่อน ไม่มีจึงใช้ metaoffcpro)
REMAP = {
    "tt2025m_s":                  "tt2025m",
    "tt_kafutechno-u_s":          "tt_kafutechno-u",
    "tt_rodincattleya-db_s":      "tt_rodincattleya-db",
    "tt_rodincattleya-m_s":       "tt_rodincattleya-m",
    "tt_modeminblarge-h_latin_s": "tt_modeminblarge-h_latin",
    "metaoffcpro-condbook_s":     "metaoffcpro-condbook",
    # ไม่มี SDF ตระกูลเดียวกันในเกม -> ใช้ตัวที่หน้าตาใกล้สุดที่ฉีดแล้ว
    "tt_modeminb-b_s":            "tt_modeminblarge-h_latin",
    "df-kanteiryu-w11_s":         "metaoffcpro-condbook",
    "tbcgr_0p_s":                 "metaoffcpro-condbook",
    "tbgm_0p_s":                  "metaoffcpro-condbook",
}

# ปล่อยไว้ตามเดิม: staffroll คงอังกฤษตามกติกาเหล็กข้อ 10 · test_ko/test_zh เป็นสไตล์ทดสอบภาษาอื่น
SKIP_FACES = {"tt_modeminb-b_ja_staffroll_s", "koreangd14r_s", "dflihei-md_s"}


def load_faces():
    """คืน (index -> (ชื่อ, type), ชื่อ -> index) จาก font2_face.bin.json"""
    d = json.load(io.open(SRC / "font2_face.bin.json", encoding="utf-8"))
    by_idx, by_name = {}, {}
    for i in range(d["ROW_COUNT"]):
        row = d[str(i)]
        name = list(row)[0]
        by_idx[i] = (name, row[name].get("type"))
        by_name[name] = i
    return by_idx, by_name


def plan():
    """คืนรายการ (row, ชื่อสไตล์, ชื่อ face เดิม, ชื่อ face ใหม่, index ใหม่)"""
    by_idx, by_name = load_faces()
    doc = json.load(io.open(SRC / "font2_style.bin.json", encoding="utf-8"))
    jobs, skipped = [], []
    for i in range(doc["ROW_COUNT"]):
        row = doc[str(i)]
        style = list(row)[0]
        v = row[style]
        eff = v.get("font_face_en") or v.get("font_face") or 0
        face, ftype = by_idx.get(eff, ("", None))
        if ftype != 3:
            continue
        if face in SKIP_FACES:
            skipped.append((i, style, face))
            continue
        dst = REMAP.get(face)
        if dst is None or dst not in by_name:
            skipped.append((i, style, face))
            continue
        jobs.append((i, style, face, dst, by_name[dst]))
    return doc, jobs, skipped


def rebuild(doc):
    """JSON -> .bin ด้วย reARMP (ทำงานบนสำเนาใน temp · path forward-slash ตามกติกาเหล็กข้อ 7)"""
    work = tempfile.mkdtemp(prefix="ljth_style_")
    try:
        jpath = os.path.join(work, "font2_style.bin.json")
        json.dump(doc, io.open(jpath, "w", encoding="utf-8"), ensure_ascii=False)
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        res = subprocess.run([sys.executable, str(paths.REARMP), "font2_style.bin.json"],
                             cwd=work, env=env, stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE, timeout=600)
        out = jpath + ".bin"            # reARMP เขียนผลเป็น <ชื่อ json>.bin
        if res.returncode != 0 or not os.path.exists(out):
            sys.exit("reARMP ล้ม: rc=%d\n%s" % (res.returncode, res.stderr.decode("utf-8", "replace")[-800:]))
        OUT.mkdir(parents=True, exist_ok=True)
        shutil.copy2(out, OUT / "font2_style.bin")
        return OUT / "font2_style.bin"
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="ย้าย font_face_en จากฟอนต์ vector ไปฟอนต์ SDF ที่ฉีดไทยแล้ว")
    ap.add_argument("--write", action="store_true", help="เขียนไฟล์ .bin ลง build/text/db.coyote.en/")
    args = ap.parse_args()

    doc, jobs, skipped = plan()
    per_face = {}
    for _, _, face, dst, _ in jobs:
        per_face.setdefault((face, dst), 0)
        per_face[(face, dst)] += 1
    for (face, dst), n in sorted(per_face.items(), key=lambda x: -x[1]):
        print("  %-30s -> %-26s %3d สไตล์" % (face, dst, n))
    print("จะแก้ %d สไตล์ · ข้าม %d (staffroll/ภาษาอื่น/ไม่มีปลายทาง)" % (len(jobs), len(skipped)))
    for i, style, face in skipped:
        print("    ข้าม %3d %-34s %s" % (i, style, face))

    if not args.write:
        print("(ยังไม่เขียนไฟล์ — ใส่ --write เพื่อบิลด์จริง)")
        return
    for i, style, face, dst, idx in jobs:
        doc[str(i)][style]["font_face_en"] = idx
    path = rebuild(doc)
    print("เขียน %s (%d B)" % (path, path.stat().st_size))


if __name__ == "__main__":
    main()
