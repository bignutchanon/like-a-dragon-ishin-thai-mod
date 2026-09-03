#!/usr/bin/env python3
r"""แพ็กไฟล์แจก — ตัวติดตั้งอัตโนมัติที่ใช้วิธีเดียวกับที่ทดสอบผ่านแล้วในเครื่องเรา

**ไม่ใช้วิธีของ MOD2SUB** (วางฟอนต์ไว้ในโฟลเดอร์ mods แล้วหวังว่า Parless จะโหลดให้)
เพราะวิธีนั้นเรายังไม่เคยพิสูจน์เอง และกติกาเหล็กข้อ 5 ของโปรเจกต์ระบุว่าเกมโหลดฟอนต์
ตั้งแต่ก่อน Parless จะ hook ทัน สิ่งที่เรายืนยันบนจอจริงแล้วคือ **ฟอนต์เขียนทับไฟล์เกมตรง ๆ**
(สำรองเป็น .orig ก่อนเสมอ) ส่วนข้อความไปทางโฟลเดอร์ mods

โครงที่แพ็ก:

    LostJudgmentThai-th-vX/
      install.bat / install.ps1        ติดตั้ง (หาโฟลเดอร์เกมจาก Steam ให้เอง)
      uninstall.bat / uninstall.ps1    ถอน — คืนฟอนต์จาก .orig + ลบโฟลเดอร์ม็อด
      README.txt
      patch.md                         บันทึกการเปลี่ยนแปลงของเวอร์ชัน
      files/
        font/font.coyote.par           -> data/font.coyote.par (สำรอง .orig ก่อนทับ)
        LostJudgmentThai/db.coyote.en/...   -> mods/LostJudgmentThai/
        loader/                        -> runtime/media/ (ใส่ให้เฉพาะที่ยังไม่มี)

⚠ ภาคนี้ฟอนต์ไม่ได้แยกเป็น .dds รายไฟล์แบบภาคแรก — กลิฟไทยถูกฉีดลงใน atlas SDF
ภายใน `font.coyote.par` จึงต้องแจกทั้ง par (~207 MB) ไฟล์ที่แจกคือ `build/font.coyote.par`
ซึ่ง `deploy_title_poc.font_repack()` สร้างไว้และเป็นไฟล์เดียวกับที่ทดสอบผ่านในเกมแล้ว

ใช้:  python scripts/package_release.py [--version 1.0] [--no-loader]
"""
import argparse
import io
import json
import os
import re
import shutil
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

RELEASE = paths.PROJECT / "release"
PACKAGING = paths.PROJECT / "packaging"
MOD_NAME = "LostJudgmentThai"
LOADER = ["ShinRyuModManager.exe", "version.dll", "YakuzaParless.asi"]
FONT_PAR = "font.coyote.par"          # แจกทั้ง par — ดู docstring
SCRIPTS = ["install.bat", "install.ps1", "uninstall.bat", "uninstall.ps1"]

META = """Name: LostJudgmentThai
Author: LJTH
Version: {ver}
Description: "Lost Judgment ภาษาไทย — แปลจากภาษาอังกฤษของเกม (ข้อความ {n_bin} ไฟล์ + ฟอนต์ไทย)"
"""

README = r"""Lost Judgment — ม็อดแปลไทย (LJTH) v{ver}
=====================================

แปลข้อความในเกมเป็นไทย {n_str} ประโยค พร้อมฟอนต์ไทยที่ฉีดกลิฟลงในฟอนต์ของเกมเอง
รองรับเฉพาะ Lost Judgment เวอร์ชัน Steam (PC) เท่านั้น

สิ่งที่คงเป็นภาษาอังกฤษโดยตั้งใจ: license / EULA / เครดิต / กล่องข้อความของ Windows
(เช่นตอนกด Alt+F4 — ตัวนั้น Windows เป็นคนวาด ไม่ใช่เกม)


ติดตั้ง
--------
ดับเบิลคลิก  install.bat  — ตัวติดตั้งจะหาโฟลเดอร์เกมจาก Steam ให้เอง
(ถ้าหาไม่เจอ จะให้วางพาธของโฟลเดอร์ที่มีไฟล์ LostJudgment.exe เอง)

จากนั้นเข้าเกมแล้วตั้งภาษาข้อความเป็น English — ม็อดแทนที่ข้อความชุดอังกฤษ

ตัวติดตั้งทำ 3 อย่าง:
 1. สำรอง data\font.coyote.par เดิมเป็น font.coyote.par.orig (ครั้งแรกครั้งเดียว)
    แล้วเขียนทับด้วยฟอนต์ไทย — ไฟล์นี้ราว 207 MB ตอนติดตั้งจะใช้เวลาสักครู่
    และต้องมีพื้นที่ว่างเพิ่มอีกราว 207 MB สำหรับไฟล์สำรอง
 2. ก๊อปข้อความไทยไปที่ mods\{mod}\
 3. ใส่ตัวโหลดม็อด (Shin Ryu Mod Manager / Parless) ให้ถ้ายังไม่มี แล้วสร้างไฟล์ MLO


ถอนการติดตั้ง
--------------
ดับเบิลคลิก  uninstall.bat  — คืนฟอนต์เดิมจากไฟล์ .orig และลบโฟลเดอร์ม็อดออก
ไฟล์ตัวโหลดม็อดไม่ถูกลบ เพราะม็อดตัวอื่นอาจใช้อยู่


ข้อควรทราบ
-----------
* ฟอนต์เขียนทับไฟล์ในเกมจริง เพราะเกมโหลดฟอนต์ตั้งแต่ก่อนตัวโหลดม็อดจะทำงานทัน
  วางไว้ในโฟลเดอร์ mods แล้วไม่ติด — ตัวติดตั้งจึงสำรอง .orig ไว้ให้เสมอ
* ถ้าสั่ง "ตรวจสอบความสมบูรณ์ของไฟล์เกม" ใน Steam ฟอนต์จะถูกเขียนกลับเป็นของเดิม
  ให้รัน install.bat ซ้ำอีกครั้ง
* เกมอัปเดตแล้วให้รัน install.bat ซ้ำ เพื่อสร้างไฟล์ MLO ใหม่
* ยังไม่ผ่านการเล่นจบเกม — เจอข้อความเพี้ยนหรือเกมค้าง ช่วยแจ้งพร้อมภาพหน้าจอ
* รายละเอียดสิ่งที่แก้ในเวอร์ชันนี้อยู่ในไฟล์ patch.md


เครดิต
-------
* ตัวโหลดม็อด: Shin Ryu Mod Manager + YakuzaParless (SutandoTsukai181 และผู้ร่วมพัฒนา)
* ฟอนต์ไทย: Sarabun (SIL Open Font License)
"""


def main():
    ap = argparse.ArgumentParser(description="แพ็กไฟล์แจก")
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--no-loader", action="store_true",
                    help="ไม่ใส่ไฟล์ตัวโหลดม็อดไปด้วย (ผู้ใช้ต้องติดตั้งเอง)")
    a = ap.parse_args()

    stage_text = paths.BUILD / "text" / "db.coyote.en"
    font_par = paths.BUILD / FONT_PAR
    assert stage_text.exists(), "ยังไม่ได้บิลด์ข้อความ — รัน scripts/build_text.py"
    assert font_par.exists(), ("ยังไม่ได้ repack ฟอนต์ — รัน "
                              "deploy_title_poc.font_repack() (ได้ build/%s)" % FONT_PAR)
    # ฟอนต์ที่แจกต้องเป็นไฟล์เดียวกับที่ติดตั้งอยู่ในเกมและผ่านการทดสอบบนจอแล้ว
    live = paths.FONT_PAR
    if live.exists():
        import hashlib

        def md5(fp):
            h = hashlib.md5()
            with io.open(fp, "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 22), b""):
                    h.update(chunk)
            return h.hexdigest()

        h_build, h_live = md5(font_par), md5(live)   # อย่าใช้ชื่อ a/b — ทับตัวแปร argparse
        assert h_build == h_live, ("ฟอนต์ใน build/ ไม่ตรงกับที่ติดตั้งในเกม (%s vs %s) — "
                                   "แจกไฟล์ที่ยังไม่ได้ทดสอบไม่ได้"
                                   % (h_build[:8], h_live[:8]))
        print("ฟอนต์ตรงกับที่ทดสอบในเกมแล้ว (md5 %s)" % h_build[:12])

    out = RELEASE / ("%s-th-v%s" % (MOD_NAME, a.version))
    if out.exists():
        shutil.rmtree(out)
    files = out / "files"
    mod = files / MOD_NAME
    (files / "font").mkdir(parents=True)
    (files / "loader").mkdir()
    shutil.copytree(stage_text, mod / "db.coyote.en")
    # ตารางฟอนต์สไปรต์ของ UI (LJ-015) — loose file ทับ ui.coyote.en.par ผ่าน Parless
    stage_ui = paths.BUILD / "ui"
    for src in sorted(stage_ui.glob("*")) if stage_ui.exists() else []:
        if src.is_dir():
            shutil.copytree(src, mod / src.name)
            print("รวม %s (%d ไฟล์)" % (src.name, sum(1 for _ in src.rglob("*"))))
    print("คัดลอกฟอนต์ %.0f MB ..." % (font_par.stat().st_size / 1e6))
    shutil.copy2(font_par, files / "font" / FONT_PAR)
    if not a.no_loader:
        for f in LOADER:
            shutil.copy2(paths.TOOLS / "SRMM-4.8.4" / f, files / "loader" / f)
    for f in SCRIPTS:
        shutil.copy2(PACKAGING / f, out / f)
    # บันทึกการเปลี่ยนแปลง — แจกไปพร้อมชุดติดตั้งเสมอ
    patch = paths.PROJECT / "patch.md"
    if patch.exists():
        shutil.copy2(patch, out / "patch.md")
    else:
        print("!! ไม่พบ patch.md — ชุดที่แจกจะไม่มีบันทึกการเปลี่ยนแปลง")

    n_bin = sum(1 for _ in (mod / "db.coyote.en").rglob("*.bin"))
    # นับเฉพาะประโยคที่เป็นไทยจริง — ที่เหลือคง EN โดยตั้งใจ (license/EULA/เครดิต/ชื่อบท ฯลฯ)
    _m = json.load(io.open(paths.MASTER_TH, encoding="utf-8"))
    _thai = re.compile(r"[฀-๿]")
    n_str = sum(1 for v in _m.values() if isinstance(v, str) and _thai.search(v))
    n_en = len(_m) - n_str
    io.open(mod / "mod-meta.yaml", "w", encoding="utf-8", newline="\n").write(
        META.format(ver=a.version, n_bin=n_bin))
    io.open(out / "README.txt", "w", encoding="utf-8-sig", newline="\r\n").write(
        README.format(ver=a.version, n_str="{:,}".format(n_str), mod=MOD_NAME))

    total = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print("แพ็ก %s · %d bin · %.1f MB" % (out, n_bin, total / 1e6))

    if not a.no_zip:
        zpath = RELEASE / ("%s-th-v%s.zip" % (MOD_NAME, a.version))
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for f in sorted(out.rglob("*")):
                if f.is_file():
                    z.write(f, str(f.relative_to(out)).replace("\\", "/"))
        print("เขียน %s (%.1f MB)" % (zpath, zpath.stat().st_size / 1e6))


if __name__ == "__main__":
    main()
