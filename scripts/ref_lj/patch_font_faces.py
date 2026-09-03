#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""อัปเดต texture_width / texture_height ใน font2_face.bin ให้ตรงกับ atlas จริงใน build/font/

## ทำไมต้องมี

`inject_thai_sdf.py --grow` ขยาย atlas ลงล่างเพื่อหาที่ว่างวางกลิฟไทย ทำให้ไฟล์ `.dds`
สูงขึ้นกว่าต้นฉบับ แต่เอนจิ้นอ่านขนาด atlas จากตาราง `font2_face.bin` ในฐานข้อมูล ไม่ใช่จากหัวไฟล์ DDS
ถ้าไม่อัปเดตตาราง เอนจิ้นจะยังคิดว่า atlas สูงเท่าเดิม แล้วคำนวณพิกัด UV ผิด → กลิฟเพี้ยนทั้งฟอนต์

เดิมค่านี้ถูกฮาร์ดโค้ดเป็นตาราง `ATLAS_HEIGHT` ใน `make_spoil.py` ซึ่งมีชื่อเดียว
พอ 29 ส.ค. 2026 ฉีดฟอนต์เพิ่มอีกเจ็ดตัว ตารางนั้นก็ตกยุคทันทีโดยไม่มีอะไรเตือน
สคริปต์นี้จึงอ่านขนาดจริงจากหัวไฟล์ DDS ทุกครั้ง ไม่ต้องมีตารางให้ลืมอัปเดต

⚠ **ห้ามรัน `make_spoil.py` เพื่อจุดประสงค์นี้** — สคริปต์นั้นเขียนทับ `sound_auth.bin`
ด้วยชุดข้อความสปอยยุค proof-of-concept ซึ่งจะทำให้คำแปลทั้งเกมหายไป

ใช้:
  python scripts/patch_font_faces.py             # รายงานอย่างเดียว
  python scripts/patch_font_faces.py --write      # เขียน build/text/db.coyote.en/font2_face.bin
"""
import argparse
import io
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")           # กติกาเหล็กข้อ 6
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths                                        # noqa: E402

SRC_JSON = paths.DB_EN / "font2_face.bin.json"
BUILD_FONT = paths.BUILD / "font"
OUT_DIR = paths.BUILD / "text" / "db.coyote.en"


def dds_size(path):
    """คืน (กว้าง, สูง) จากหัวไฟล์ DDS — offset 12 = height, 16 = width"""
    with open(path, "rb") as f:
        head = f.read(32)
    if head[:4] != b"DDS ":
        raise ValueError("ไม่ใช่ไฟล์ DDS: %s" % path)
    height, width = struct.unpack_from("<II", head, 12)
    return width, height


def plan():
    doc = json.load(io.open(SRC_JSON, encoding="utf-8"))
    jobs = []
    for i in range(doc["ROW_COUNT"]):
        row = doc[str(i)]
        name = list(row)[0]
        fields = row[name]
        dds = BUILD_FONT / ("%s.dds" % name)
        if not dds.exists():
            continue                                # ฟอนต์ที่ไม่ได้ฉีด = ไม่แตะ
        w, h = dds_size(dds)
        old_w = fields.get("texture_width")
        old_h = fields.get("texture_height")
        if (old_w, old_h) != (w, h):
            jobs.append((i, name, (old_w, old_h), (w, h)))
    return doc, jobs


def rebuild(doc):
    work = tempfile.mkdtemp(prefix="ljth_face_")
    try:
        jpath = os.path.join(work, "font2_face.bin.json")
        json.dump(doc, io.open(jpath, "w", encoding="utf-8"), ensure_ascii=False)
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        res = subprocess.run([sys.executable, str(paths.REARMP), "font2_face.bin.json"],
                             cwd=work, env=env, stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE, timeout=600)
        out = jpath + ".bin"                        # reARMP เขียนผลเป็น <ชื่อ json>.bin
        if res.returncode != 0 or not os.path.exists(out):
            sys.exit("reARMP ล้ม: rc=%d\n%s"
                     % (res.returncode, res.stderr.decode("utf-8", "replace")[-800:]))
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(out, OUT_DIR / "font2_face.bin")
        return OUT_DIR / "font2_face.bin"
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="ซิงก์ขนาด atlas ใน font2_face.bin กับไฟล์ DDS จริง")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    doc, jobs = plan()
    if not jobs:
        print("ขนาด atlas ในตารางตรงกับไฟล์ DDS ทุกตัวแล้ว ไม่ต้องแก้")
        return
    for i, name, old, new in jobs:
        print("  %-30s %sx%s -> %sx%s" % (name, old[0], old[1], new[0], new[1]))
    print("ต้องแก้ %d face" % len(jobs))
    if not a.write:
        print("(ยังไม่เขียนไฟล์ — ใส่ --write เพื่อบิลด์จริง)")
        return
    for i, name, old, new in jobs:
        doc[str(i)][name]["texture_width"] = new[0]
        doc[str(i)][name]["texture_height"] = new[1]
    path = rebuild(doc)
    print("เขียน %s (%s B)" % (path, "{:,}".format(path.stat().st_size)))


if __name__ == "__main__":
    main()
