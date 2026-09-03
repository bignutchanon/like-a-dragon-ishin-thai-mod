#!/usr/bin/env python3
"""ค่าคงที่ path กลางของโปรเจกต์ ISHTH — Like a Dragon: Ishin! (แปลไทย)
ทุกสคริปต์ import จากที่นี่ — แก้ path ที่เดียว ได้ผลทุกตัว

override ได้ด้วย environment variable:
  ISHIN_GAME = โฟลเดอร์เกม (ค่า default คือที่ติดตั้งจริงบนเครื่องนี้)

⚠ ภาคนี้ไม่ใช่ Dragon Engine
  Ishin! (รีเมค 2023) วางบน Unreal Engine 4.27 — ไม่มี .par/ARMP/SRMM/Parless
  แต่ **ข้อมูลข้อความข้างในยังเป็นฟอร์แมตของ RGG เอง** (.msg/.gmd/.bin แบบ Old Engine)
  ซึ่งถูกยัดไว้ในไฟล์ pak ของ UE อีกที → ต้องแตกสองชั้น (pak → msg)
  รายละเอียด + หลักฐาน: docs/research.md

กติกา:
  - ห้ามแก้/ลบ/ทับไฟล์ใน Content/Paks/ ของเกม — ม็อดออกเป็น pak ใหม่ (pakchunk99) เท่านั้น
  - translations/master_th.json = คำแปลรวม (source of truth) เขียนผ่าน merge_qc.py เท่านั้น
"""
import os
from pathlib import Path

# ---- โปรเจกต์ ----
PROJECT = Path(__file__).resolve().parent.parent   # D:/Projects/like-a-dragon-ishin

SCRIPTS      = PROJECT / "scripts"
TOOLS        = PROJECT / "tools"
DOCS         = PROJECT / "docs"
EXTRACTED    = PROJECT / "extracted"
TRANSLATIONS = PROJECT / "translations"
BUILD        = PROJECT / "build"
FONT_DIR     = PROJECT / "font"
WORK         = PROJECT / "work"

MSG_EN   = EXTRACTED / "msg_en"        # .msg ภาษาอังกฤษที่แตกจาก pak (ต้นฉบับ อย่าแก้)
MSG_JA   = EXTRACTED / "msg_ja"        # .msg ญี่ปุ่น (ไว้เทียบเพศ/สรรพนาม/คำเรียก)
TEXT_EN  = EXTRACTED / "text_en"       # JSON ที่ถอดจาก .msg แล้ว

# ---- คำแปล ----
MASTER_TH = TRANSLATIONS / "master_th.json"
WORKLIST  = TRANSLATIONS / "worklist"
DONE      = TRANSLATIONS / "done"
REVIEW    = TRANSLATIONS / "review"

# ---- โปรเจกต์พี่น้อง (RGG ภาคอื่นที่แปลไว้แล้ว · อ่านอย่างเดียว) ----
# เรียงตามลำดับความสำคัญของคำ (ใหม่กว่า/ใกล้กว่าชนะ)
# หมายเหตุเฉพาะภาคนี้: Ishin เป็นยุคบาคุมัตสึ ตัวละครใช้ "หน้าตา" ของนักแสดงชุด Yakuza
# (เรียวมะ = คิริว, โซจิ = มาจิม่า ฯลฯ) แต่ **เป็นคนละตัวละคร** — คำล็อกชื่อจึงห้ามยกมาตรง ๆ
# ยกมาได้คือ: ระบบสรรพนาม/ระดับภาษา · ศัพท์เมนู/ระบบ · ศัพท์การต่อสู้ · แนวทาง QC
SIBLING_ROOT = Path(os.environ.get("RGG_PROJECTS", "D:/Projects"))
SIBLINGS = [
    ("LJ",       "lost-judgment-thai",           "glossary.md"),
    ("Judgment", "judgment-thai",                "glossary.md"),
    ("K3",       "yakuza-kiwami-3",              "glossary.md"),
    ("Gaiden",   "yakuza-gaiden",                "glossary.md"),
    ("Y8",       "y8-infinite-wealth",           "glossary.md"),
    ("Y7",       "yakuza-7-like-a-dragon-thai",  "glossary.md"),
    ("Pirate",   "pirate-yakuza-hawaii-thai",    "glossary.md"),
    ("K2R",      "yakuza-kiwami-2-mod",          "glossary_k2.md"),
]


def sibling_paths(warn=True):
    """คืน [(ชื่อ, path ของ master_th, path ของ glossary)] เรียงตามลำดับความสำคัญ

    `warn=True` จะพิมพ์เตือนถ้าโฟลเดอร์ไหนหาย — ห้ามเงียบ เพราะการหายแบบเงียบทำให้
    เครื่องมือรายงานผลที่ดูสวยแต่ไม่เคยเทียบภาคนั้นเลย (บทเรียนจากโปรเจกต์ LJ sprint 15)
    """
    out, missing = [], []
    for name, folder, gloss in SIBLINGS:
        base = SIBLING_ROOT / folder / "translations"
        m = base / "master_th.json"
        if m.exists():
            out.append((name, str(m), str(base / gloss)))
        else:
            missing.append("%s (%s)" % (name, folder))
    if warn and missing:
        import sys as _sys
        print("!! โหลดภาคพี่น้องไม่ได้: " + " · ".join(missing), file=_sys.stderr)
    return out


# ---- เกม (Like a Dragon: Ishin! PC 2023 · Unreal Engine 4.27) ----
GAME      = Path(os.environ.get("ISHIN_GAME",
                 r"E:/SteamLibrary/steamapps/common/LikeADragonIshin"))
GAME_EXE  = GAME / "LikeaDragonIshin/Binaries/Win64/LikeaDragonIshin-Win64-Shipping.exe"
PAKS      = GAME / "LikeaDragonIshin/Content/Paks"      # !! ห้ามเขียน/ลบไฟล์เดิมในนี้ !!

# คอนเทนเนอร์ที่ยืนยันแล้ว (1 ก.ย. 2026)
PAK_MAIN  = PAKS / "pakchunk0-WindowsNoEditor.pak"      # 23.9 GB · 35,646 ไฟล์ · ข้อมูล RGG อยู่ที่นี่
UTOCS     = sorted(PAKS.glob("*.utoc")) if PAKS.exists() else []

# path ภายในเกม (ขึ้นต้นเหมือนกันหมด — ตัดให้สั้นเวลาเรียกใช้)
CONTENT   = "LikeaDragonIshin/Content/"
DATA      = CONTENT + "Projects/Devil2/data/"           # Devil2 = ชื่อโปรเจกต์ภายในของ Ishin!
MSG_DIR   = DATA + "wdr_%s/msg/"                        # %s = ja/en/fr/de/it/es/ko/cn
PAC_DIR   = DATA + "wdr_%s/pac/"
TEXTBRIDGE = CONTENT + "TextBridge/"                    # StringTable ของ UI (ต้นฉบับเป็น JA)

LANGS = ["ja", "en", "fr", "de", "it", "es", "ko", "cn"]
CARRIER = "en"                                          # ภาษาที่จะทับด้วยไทย (ตัดสินใจ 1 ก.ย. 2026)

# ---- ฟอนต์ (⏳ ยังไม่ survey) ----
# Sarabun-Regular-ishin.ttf = Sarabun-Regular.ttf ที่แก้ metric แนวตั้ง (hhea/OS2 ascender 1068->1290 ·
# descender -232->-350) เพราะกลิฟวรรณยุกต์ที่ซ้อนบนสระ (uni0E49.small ฯลฯ) สูงถึง 1265 เกิน ascender เดิม
# -> ในเกม Slate ตัดขอบบนตามความสูงบรรทัด ไม้โท/ไม้ตรีบน "งั้น" โดน crop (รายงาน 3 ก.ย. 2026)
SARABUN_TTF = FONT_DIR / "Sarabun-Regular-ishin.ttf"

# ---- ม็อด ----
MOD_NAME  = "LikeADragonIshinThai"
# วิธีติดตั้งม็อดของ Ishin! ตามที่ชุมชน Nexus ใช้กันจริง (ยืนยันจากหน้าม็อดหลายตัว 1 ก.ย. 2026):
#   1. วาง pak ไว้ที่ Content/Paks/~mods/ (ถ้าไม่มีโฟลเดอร์ให้สร้างเอง)
#   2. ชื่อไฟล์ต้องลงท้ายด้วย _P  เช่น  MyMod_P.pak
# ทดสอบบนเครื่องนี้แล้ว: วางไว้ที่ Paks/ เฉย ๆ ชื่อไม่มี _P → เกมไม่โหลด (เมนูยังอังกฤษ)
MOD_PAK   = "LikeADragonIshinThai_P.pak"
MODS_DIR  = PAKS / "~mods"

# ---- เครื่องมือของโปรเจกต์นี้ ----
IOSTORE = TOOLS / "iostore.py"                          # อ่าน .utoc/.ucas
PAKFILE = TOOLS / "pakfile.py"                          # อ่าน .pak (legacy v11)

# ---- โปรเจกต์พี่น้อง (อ่านอย่างเดียว) ----
LJ_PROJECT       = Path(r"D:/Projects/lost-judgment-thai")   # ต้นแบบ pipeline ข้อความ/QC/เพศผู้พูด
JUDGMENT_PROJECT = Path(r"D:/Projects/judgment-thai")
K3_PROJECT       = Path(r"D:/Projects/yakuza-kiwami-3")
Y0_PROJECT       = Path(r"D:/Projects/yakuza-0-direct")      # Old Engine — ฟอร์แมต .msg ใกล้ภาคนี้
Y5_PROJECT       = Path(r"D:/Projects/yakuza-5")             # Old Engine
KIWAMI_PROJECT   = Path(r"D:/Projects/yakuza-kiwami-mod")    # Old Engine


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"MOD_NAME = {MOD_NAME}  ·  CARRIER = {CARRIER}")
    names = ["PROJECT", "EXTRACTED", "MSG_EN", "MASTER_TH", "GAME", "GAME_EXE",
             "PAKS", "PAK_MAIN", "SARABUN_TTF", "IOSTORE", "PAKFILE", "LJ_PROJECT"]
    for n in names:
        v = globals()[n]
        p = Path(v)
        print(f'{"OK" if p.exists() else "--"}  {n:12s} {p}')
    print(f'{"OK" if UTOCS else "--"}  UTOCS        {len(UTOCS)} containers')
