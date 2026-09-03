#!/usr/bin/env python3
"""ค่าคงที่ path กลางของโปรเจกต์ LJTH — Lost Judgment (แปลไทย)
ทุกสคริปต์ import จากที่นี่ — แก้ path ที่เดียว ได้ผลทุกตัว

override ได้ด้วย environment variable:
  LJ_GAME = โฟลเดอร์เกม (ค่า default คือที่ติดตั้งจริงบนเครื่องนี้)

กติกา:
  - GAME_DATA (runtime/media/data) ห้ามแก้/ลบ/ทับไฟล์เดิมเด็ดขาด — mod วางที่ MODS_DIR เท่านั้น
    ยกเว้นฟอนต์: drop-in ทับ font par โดย backup .orig ก่อนเสมอ (กติกาเหล็กข้อ 5)
  - translations/master_th.json = คำแปลรวม (source of truth) เขียนผ่าน merge_qc.py เท่านั้น

หมายเหตุ: port มาจาก judgment-thai (paths.py) 22 ส.ค. 2026 — ภาคพี่น้องใช้ pipeline ข้อความชุดเดียวกัน
ค่าที่ยังไม่ยืนยันกับไฟล์เกมจริงถูกทำเครื่องหมาย ⏳ — ต้อง verify ก่อนใช้ครั้งแรก
"""
import os
from pathlib import Path

# ---- โปรเจกต์ ----
PROJECT = Path(__file__).resolve().parent.parent   # D:/Projects/lost-judgment-thai

SCRIPTS      = PROJECT / "scripts"
TOOLS        = PROJECT / "tools"
DOCS         = PROJECT / "docs"
EXTRACTED    = PROJECT / "extracted"
DB_EN        = EXTRACTED / "db_en"                 # ARMP .bin อังกฤษ (ต้นฉบับ อย่าแก้)
TRANSLATIONS = PROJECT / "translations"
BUILD        = PROJECT / "build"
FONT_DIR     = PROJECT / "font"

# ---- คำแปล ----
MASTER_TH = TRANSLATIONS / "master_th.json"        # source of truth
WORKLIST  = TRANSLATIONS / "worklist"
DONE      = TRANSLATIONS / "done"
REVIEW    = TRANSLATIONS / "review"
TM_JUDGMENT = TRANSLATIONS / "tm_judgment.json"    # TM จาก Judgment ภาคแรก (50,297 คู่ · อ้างอิงเท่านั้น
                                                   # ห้าม auto-fill เข้า master_th — ต้องผ่าน worklist/QC)

# ---- โปรเจกต์พี่น้อง (RGG ภาคอื่นที่แปลไว้แล้ว) ----
# ⚠ **นี่คือแหล่งเดียวของรายชื่อโฟลเดอร์ภาคพี่น้อง** (รวมมาไว้ที่นี่ 26 ส.ค. 2026 · sprint 16)
# ก่อนหน้านี้รายชื่อถูกคัดลอกไว้สองที่ (`find_term.py` และ `check_ref_tm.py`) แล้ว `check_ref_tm.py`
# **เดาชื่อโฟลเดอร์เอง 3 ภาคจนโหลดไม่ขึ้นแบบเงียบ ๆ** — รายงานว่า "ขัด 0 จุด" ทั้งที่ไม่เคยเทียบเลย
# เรียงตามลำดับความสำคัญของคำ (ใหม่กว่า/ใกล้กว่าชนะ) ตาม CLAUDE.md
SIBLING_ROOT = Path(os.environ.get("RGG_PROJECTS", "D:/Projects"))
SIBLINGS = [
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

    `warn=True` จะพิมพ์เตือนถ้าโฟลเดอร์ไหนหาย — **ห้ามเงียบ** เพราะการหายแบบเงียบทำให้
    เครื่องมือรายงานผลที่ดูสวยแต่ไม่เคยเทียบภาคนั้นเลย (บทเรียน sprint 15)
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


# ---- เกม (Lost Judgment PC 2021, Dragon Engine ยุค Y7 — ติดตั้งแล้ว 20 ส.ค. 2026) ----
GAME      = Path(os.environ.get("LJ_GAME",
                 r"E:/SteamLibrary/steamapps/common/Lost Judgment"))
GAME_EXE  = GAME / "runtime/media/LostJudgment.exe"  # ยืนยันแล้ว
GAME_DATA = GAME / "runtime/media/data"              # !! ห้ามเขียน/ลบไฟล์ในนี้ !!

CODENAME  = "coyote"                                 # ยืนยันแล้วจากชื่อไฟล์จริง
DB_EN_PAR = GAME_DATA / "db.coyote.en.par"           # ยืนยันแล้ว 22 ส.ค. 2026 — 19.8 MB
# db par มีตัวเดียวในเกม (ไม่มี db.coyote.ja.par) → carrier = EN เหมือน Judgment ภาคแรก
UI_EN_PAR     = GAME_DATA / "ui.coyote.en.par"       # 324 MB — เผื่อ texture text
UI_COMMON_PAR = GAME_DATA / "ui.coyote.common.par"   # 800 MB
TALK_PAR      = GAME_DATA / "talk_coyote.par"        # ⏳ ยังไม่ตรวจว่ามีข้อความหรือแค่เสียง

# ⏳ The Kaito Files (DLC เนื้อเรื่อง): ไม่มี db par แยกใน data/ — คาดว่าข้อความอยู่ใน DB_EN_PAR
#    ตรวจตอน extract (ดู sddlc/stmdlc_en.par ถ้าไม่เจอ)

# ---- ฟอนต์ (⏳ ยังไม่ survey — ต่างจาก Judgment ภาคแรก!) ----
# Judgment ภาคแรก: ฟอนต์เป็นโฟลเดอร์ loose (data/font.judge/en/*.dds) ยุค bitmap grid
# Lost Judgment: เป็น **par** ขนาด 215 MB · magic `FONT!` (ตระกูล Y6) มี tbgm_0p_ja / tbcgr_0p /
#   metaoffcpro-condbook / symbol / yakuza + ชุด _hires/_s/_fallback_for_ko/_zh และโฟลเดอร์ debug/
# → ต้อง survey ว่าจอ EN วาดจากไฟล์ไหนก่อน ห้าม copy slot map จากภาคอื่น (FONT_PLAYBOOK)
FONT_PAR      = GAME_DATA / "font.coyote.par"        # ยืนยันแล้ว 215 MB
FONT_EXTRACT  = EXTRACTED / "font"                   # ปลายทางตอนแตก par
FONT_BASENAME = None                                 # ⏳ รอผล survey_fonts.py
FONT_SRC_BIN  = None                                 # ⏳
FONT_SRC_DDS  = None                                 # ⏳
SARABUN_TTF   = FONT_DIR / "Sarabun-Regular.ttf"

MOD_NAME  = "LostJudgmentThai"
MODS_ROOT = GAME / "runtime/media/mods"
MODS_DIR  = MODS_ROOT / MOD_NAME
# SRMM/Parless รองรับ Lost Judgment อย่างเป็นทางการ (Steam) — db วาง loose ใน MODS_DIR ได้
# ⏳ ยังไม่ได้ติดตั้ง SRMM ในเกมนี้ (mods/ ยังว่าง) — เช็คก่อน deploy db แบบ loose

# ---- เครื่องมือ ----
REARMP  = TOOLS / "reARMP_fixed.py"
PARTOOL = TOOLS / "ParTool.exe"

# ---- โปรเจกต์พี่น้อง (อ่านอย่างเดียว) ----
JUDGMENT_PROJECT = Path(r"D:/Projects/judgment-thai")   # ต้นแบบ pipeline ข้อความ + TM + glossary
Y6_PROJECT       = Path(r"D:/Projects/yakuza-6-thai")
Y8_PROJECT       = Path(r"D:/Projects/y8-infinite-wealth")  # ต้นแบบฟอนต์ SDF + glossary อิจินโจ
K3_PROJECT       = Path(r"D:/Projects/yakuza-kiwami-3")
GAIDEN_PROJECT   = Path(r"D:/Projects/yakuza-gaiden")

if __name__ == "__main__":
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    names = ["PROJECT", "DB_EN", "MASTER_TH", "TM_JUDGMENT", "WORKLIST", "DONE",
             "GAME", "GAME_EXE", "GAME_DATA", "DB_EN_PAR", "UI_EN_PAR", "FONT_PAR",
             "MODS_ROOT", "MODS_DIR", "SARABUN_TTF", "REARMP", "PARTOOL",
             "JUDGMENT_PROJECT", "Y6_PROJECT"]
    print(f"MOD_NAME = {MOD_NAME}  ·  CODENAME = {CODENAME}")
    for n in names:
        v = globals()[n]
        if v is None:
            print(f"--  {n:16s} (ยังไม่กำหนด — รอ survey)")
            continue
        p = Path(v)
        print(f'{"OK" if p.exists() else "--"}  {n:16s} {p}')
