#!/usr/bin/env python3
"""PoC: แปลเมนูจอไตเติลเป็นไทย + ใส่ฟอนต์ไทย แล้วแพ็กเป็น pak ม็อดหนึ่งไฟล์

จุดประสงค์ — ตอบ 4 คำถามพร้อมกันด้วยการทดสอบครั้งเดียว:
  1. เกมโหลด pak เสริม (pakchunk99) ไหม
  2. ฟอนต์ไทยที่ยัดผ่าน .ufont ติดไหม
  3. สระบน/ล่างและวรรณยุกต์วางถูกตำแหน่งไหม (UE เปิด text shaping หรือเปล่า)
  4. สตริงที่ยาวกว่าเดิมเกมรับไหม

ทำอะไรบ้าง:
  - อ่าน extracted/locres/Game.en.json แล้ว **เพิ่มสตริงไทยเข้าไปท้ายตาราง** พร้อมชี้ idx ใหม่
    (ไม่ทับสตริงเดิมในตำแหน่งเดิม เพราะ locres ใช้ index ร่วมกันหลายคีย์ — แก้ที่เดียวจะไปโผล่ที่อื่น)
  - ประกอบ Game.locres ใหม่ด้วย tools/locres.py (roundtrip identity ผ่านแล้ว byte-exact)
  - เอา font/Sarabun-Regular.ttf ไปเป็น .ufont ทับ FontFace ที่จอ EN ใช้
  - แพ็กสองไฟล์นั้นเป็น build/pakchunk99-WindowsNoEditor.pak

ใช้:
  python scripts/make_title_poc.py              # บิลด์อย่างเดียว
  python scripts/make_title_poc.py --install    # คัดลอกเข้าโฟลเดอร์ Paks ของเกมด้วย
  python scripts/make_title_poc.py --uninstall  # ลบ pak ม็อดออกจากเกม
  python scripts/make_title_poc.py --loose      # วางไฟล์ loose ใน Content/ (ไม่แพ็ก pak)
  python scripts/make_title_poc.py --loose-uninstall

โหมด --loose คืออะไร: เกม UE หลายตัวอ่านไฟล์ที่วางเปล่า ๆ ใน Content/ ทับไฟล์ใน pak
โดยไม่ต้องแพ็กเป็น pak เลย ใช้ตัดตัวแปรเรื่องฟอร์แมต pak ออกทั้งหมด
ปลอดภัย: โฟลเดอร์ Content/ ของเกมเดิมมีแต่ Paks/ → ไฟล์ที่วางไม่ทับของเดิมสักไฟล์
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                   # noqa: E402
import locres                                  # noqa: E402
from pakwrite import write_pak                 # noqa: E402

LOCRES_GAME_PATH = "LikeaDragonIshin/Content/Localization/Game/en/Game.locres"
# FontFace ที่ Font_System ใช้เป็น DefaultTypeface ของภาษาชุด EFIGS (ยืนยันจาก Font_System.uasset)
FONT_GAME_PATH = ("LikeaDragonIshin/Content/Projects/Devil2/UI/Font/FontFace/"
                  "EFIGS/Kuro-Medium.ufont")
MOD_PAK = paths.MOD_PAK      # ต้องลงท้าย _P และวางใน Paks/~mods/ (ดูเหตุผลใน paths.py)

# ชื่อเก่าที่เคยลองแล้วไม่ได้ผล — เก็บไว้ให้ --uninstall เก็บกวาดได้ครบ
LEGACY_NAMES = ["pakchunk99-WindowsNoEditor.pak", "pakchunk99-WindowsNoEditor_P.pak"]

# คำแปลชุดทดสอบ — เลือกให้ครอบทั้งคำสั้น คำยาว คำที่มีสระบน-ล่าง-วรรณยุกต์ซ้อน และคำที่ปนอังกฤษ
# ⚠ ชุดนี้เป็นแค่ PoC ยังไม่ผ่าน glossary/QC — ห้ามยกไปใช้เป็นคำแปลจริง
TRANSLATIONS = {
    "surfboard": {
        "TitleMenu/Label/01": "ระดับความยาก",
        "TitleMenu/Menu/01": "เริ่มเกมใหม่",
        "TitleMenu/Menu/02": "เล่นต่อ",
        "TitleMenu/Menu/03": "อัปโหลด / ดาวน์โหลด",
        "TitleMenu/Menu/04": "ดูฉากย้อนหลัง",
        "TitleMenu/Menu/05": "มินิเกมการพนัน",
        "TitleMenu/Menu/06": "ข้อมูลเครือข่าย",
        "TitleMenu/Menu/07": "ตั้งค่า",
        "TitleMenu/Menu/08": "บาคุมัตสึพรีเมียมแอดเวนเจอร์",
        "TitleMenu/Menu/09": "เรื่องย่อ",
        "TitleMenu/Menu/10": "บททดสอบขั้นสูงสุด",
        "TitleMenu/Menu/11": "เริ่มเกมใหม่ / ย้ายข้อมูล",
        "TitleMenu/Menu/12": "ของแถม",
        "TitleMenu/Menu/13": "ตั้งค่า / การช่วยเหลือการเข้าถึง",
        "TitleMenu/Menu/15": "เนื้อหาดาวน์โหลดเพิ่มเติม",
        "TitleMenu/Menu/16": "ออกจากเกม",
        "TitleMenu/Menu/17": "เดโมช่วงกลางวัน",
        "TitleMenu/Menu/18": "เดโมช่วงกลางคืน",
        "TitleMenu/Menu/20": "ใช้ข้อมูลเซฟจาก PlayStation®4",
    },
    "title": {
        "title/s_sz_difficulty/0000": "ง่าย",
        "title/s_sz_difficulty/0001": "ปกติ",
        "title/s_sz_difficulty/0002": "ยาก",
        "title/s_sz_difficulty/0003": "ตำนาน",
        "title/s_sz_difficulty_title/0000": "ระดับความยาก",
        "title/s_sz_difficulty_msg/0000": "เหมาะกับผู้เล่นที่เพิ่งเริ่มเล่นเกมแอ็กชัน",
        "title/s_sz_difficulty_msg/0001": "ระดับความยากมาตรฐาน",
        "title/s_sz_difficulty_msg/0002": "เหมาะกับผู้เล่นที่ชำนาญเกมแอ็กชัน",
        "title/s_sz_difficulty_msg/0003": "สำหรับผู้เล่นที่มองหาความท้าทาย",
    },
    "syo_title": {
        "syo_title/1": "บทที่ 1: หนีจากบ้านเกิด",
        "syo_title/2": "บทที่ 2: ชายที่ชื่อไซโต ฮาจิเมะ",
    },
}
# หมายเหตุ: TitleMenu/Menu/14 = "All Rights Reserved" และชื่อเกม คงอังกฤษตามกติกาข้อ 9


def build(out_dir):
    src_json = paths.EXTRACTED / "locres" / "Game.en.json"
    if not src_json.exists():
        print("ยังไม่มี %s — รัน scripts/extract_locres.py ก่อน" % src_json)
        return None
    doc = json.loads(src_json.read_text(encoding="utf-8"))
    strings = doc["strings"]
    raw_lengths = doc.get("raw_lengths") or []

    by_ns = {n["ns"]: n for n in doc["namespaces"]}
    n_changed = n_missing = 0
    for ns, mapping in TRANSLATIONS.items():
        node = by_ns.get(ns)
        if node is None:
            print("!! ไม่พบ namespace %s" % ns)
            n_missing += len(mapping)
            continue
        for entry in node["entries"]:
            th = mapping.get(entry["key"])
            if th is None:
                continue
            # เพิ่มสตริงใหม่ท้ายตารางแล้วชี้ idx มาที่ตัวใหม่ — ไม่แตะสตริงเดิมที่คีย์อื่นใช้ร่วม
            strings.append(th)
            if raw_lengths:
                raw_lengths.append(None)
            entry["idx"] = len(strings) - 1
            n_changed += 1
        for key in mapping:
            if not any(e["key"] == key for e in node["entries"]):
                print("!! ไม่พบคีย์ %s/%s" % (ns, key))
                n_missing += 1

    if raw_lengths:
        doc["raw_lengths"] = raw_lengths

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    patched_json = out_dir / "Game.th.json"
    patched_json.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    patched_locres = out_dir / "Game.th.locres"
    locres.build_full(str(patched_json), str(patched_locres))

    if not paths.SARABUN_TTF.exists():
        print("!! ไม่พบฟอนต์ %s" % paths.SARABUN_TTF)
        return None

    files = {
        LOCRES_GAME_PATH: patched_locres.read_bytes(),
        FONT_GAME_PATH: paths.SARABUN_TTF.read_bytes(),
    }
    pak = write_pak(out_dir / MOD_PAK, files)
    print("แก้แล้ว %d คีย์ · ไม่พบ %d คีย์" % (n_changed, n_missing))
    print("locres ใหม่ %d ไบต์ · ฟอนต์ %d ไบต์" % (len(files[LOCRES_GAME_PATH]),
                                                    len(files[FONT_GAME_PATH])))
    print("pak: %s (%d ไบต์)" % (pak, pak.stat().st_size))
    return pak


def install(pak):
    paths.MODS_DIR.mkdir(parents=True, exist_ok=True)
    dst = paths.MODS_DIR / MOD_PAK
    shutil.copy2(pak, dst)
    print("ติดตั้งแล้ว: %s" % dst)
    print("ถอนออกด้วย: python scripts/make_title_poc.py --uninstall")


# ไฟล์ loose ที่จะวาง: {path ในเกม (นับจาก Content/): ชื่อไฟล์ต้นทางใน build/ หรือ font/}
LOOSE_MAP = {
    "Localization/Game/en/Game.locres": "build/Game.th.locres",
    "Projects/Devil2/UI/Font/FontFace/EFIGS/Kuro-Medium.ufont": "font/Sarabun-Regular.ttf",
}


def _content_dir():
    return paths.PAKS.parent          # <GAME>/LikeaDragonIshin/Content


def loose_install():
    content = _content_dir()
    for rel, src in LOOSE_MAP.items():
        dst = content / rel
        if dst.exists():
            print("!! มีไฟล์เดิมอยู่แล้ว ข้าม (ห้ามทับของเกม): %s" % dst)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(paths.PROJECT / src, dst)
        print("วางแล้ว: %s (%d ไบต์)" % (dst, dst.stat().st_size))
    print("ถอนด้วย: python scripts/make_title_poc.py --loose-uninstall")


def loose_uninstall():
    content = _content_dir()
    for rel in LOOSE_MAP:
        dst = content / rel
        if dst.exists():
            dst.unlink()
            print("ลบแล้ว: %s" % dst)
    # เก็บโฟลเดอร์ว่างที่เราสร้างขึ้นมาเอง (ไม่แตะ Paks)
    for top in ("Localization", "Projects"):
        base = content / top
        if not base.exists():
            continue
        for d in sorted(base.rglob("*"), key=lambda x: -len(x.parts)):
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
        if base.is_dir() and not any(base.iterdir()):
            base.rmdir()
            print("ลบโฟลเดอร์ว่าง: %s" % base)


def uninstall():
    targets = [paths.MODS_DIR / MOD_PAK] + [paths.PAKS / n for n in LEGACY_NAMES]
    targets += [paths.MODS_DIR / n for n in LEGACY_NAMES]
    n = 0
    for dst in targets:
        if not dst.exists():
            continue
        try:
            dst.unlink()
            print("ลบแล้ว: %s" % dst)
            n += 1
        except PermissionError:
            print("!! ลบไม่ได้ (เกมเปิดอยู่?): %s" % dst)
    if not n:
        print("ไม่มีไฟล์ม็อดให้ลบ")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--loose", action="store_true")
    ap.add_argument("--loose-uninstall", action="store_true")
    a = ap.parse_args()
    if a.uninstall:
        uninstall()
        return
    if a.loose_uninstall:
        loose_uninstall()
        return
    pak = build(paths.BUILD)
    if not pak:
        return
    if a.install:
        install(pak)
    if a.loose:
        loose_install()


if __name__ == "__main__":
    main()
