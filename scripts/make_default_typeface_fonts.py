"""สร้างสำเนา Sarabun สำหรับช่อง DefaultTypeface ของ CompositeFont แต่ละตัว

ทำไมต้องแยกไฟล์ต่อ FontFace แทนที่จะใช้ `font/Sarabun-Regular-ishin.ttf` ตัวเดียวทับทุกช่อง:
Slate คิด "ความสูงบรรทัด" ของ CompositeFont จาก **DefaultTypeface** เท่านั้น ไม่ใช่จาก sub-font
ที่วาดตัวอักษรจริง (ยืนยันบนจอ 8 ก.ย. 2026: v1.3 ทับ DefaultTypeface ด้วย Sarabun ที่ดัน
ascender เป็น 1290/-350 แล้วบรรทัดทั้งเกมห่างขึ้น ~64% เพราะของเดิม DF-FutoKaiSho-W9
สูง 880/-144 ที่ upem 1024 = 1.000 em ส่วน Sarabun-ishin = 1.640 em)

สคริปต์นี้จึงคัดลอก metric แนวตั้งของฟอนต์ญี่ปุ่นต้นฉบับ (hhea · OS/2 typo · OS/2 win)
มาใส่ในสำเนา Sarabun ทีละไฟล์ โดยสเกลจาก upem ของต้นฉบับมาเป็น upem 1000 ของ Sarabun
ผลคือความสูงบรรทัดทุกจอเท่าเกมต้นฉบับเป๊ะ แต่ยังมีกลิฟไทยให้วาด

ใช้:  python scripts/make_default_typeface_fonts.py
ผลลัพธ์: font/defaults/<ชื่อ FontFace>.ttf  (build_text.py หยิบไปแพ็กลง pak)
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths  # noqa: E402
from pakfile import PakFile  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402

FONT_DIR_GAME = "LikeaDragonIshin/Content/Projects/Devil2/UI/Font/FontFace/"
OUT_DIR = paths.PROJECT / "font" / "defaults"

# FontFace ที่เป็น DefaultTypeface ของ CompositeFont ซึ่ง sub-font EFIGS ไม่ครอบช่วงตัวอักษรไทย
# (docs/research.md §5.2) — ต้องทับด้วยฟอนต์ที่มีกลิฟไทย แต่ต้องคง metric เดิมไว้
# ⚠ ไม่มี `DF-FutoKaiSho-W9` กับ `FOT-UDKakugo_LargePr6N-DB` ในรายการนี้โดยตั้งใจ —
# สองตัวนั้นเป็น DefaultTypeface ของ `Font_System` ด้วย ซึ่งเป็นฟอนต์ของเกือบทั้งเกม
# v1.3 ทับสองตัวนี้แล้วบรรทัดห่างขึ้นทั้งเกมและข้อความล้นกรอบในจอสมุดบันทึก/สารานุกรม
# (ภาพจากผู้ใช้ 8 ก.ย. 2026) จึงคืนเป็นไฟล์เดิมของเกม
FACES = [
    "DF_GOKUBUTOKAISHO_W12",
    "DF_ENKAISHO_W5",
    "DF_REISHO_W6",
    "TT_KswHannya",
    "TT_KswHiryu",
    "TT_KswKaisho",
    "TT_KswReisho",
    "TT_KokinEdo-EB",
]


def copy_metrics(src, dst):
    """คัดลอก metric แนวตั้งจาก src มาใส่ dst โดยสเกลตามอัตราส่วน upem"""
    k = dst["head"].unitsPerEm / src["head"].unitsPerEm

    def s(v):
        return int(round(v * k))

    sh, dh = src["hhea"], dst["hhea"]
    dh.ascent, dh.descent, dh.lineGap = s(sh.ascent), s(sh.descent), s(sh.lineGap)
    so, do = src["OS/2"], dst["OS/2"]
    do.sTypoAscender, do.sTypoDescender = s(so.sTypoAscender), s(so.sTypoDescender)
    do.sTypoLineGap = s(so.sTypoLineGap)
    do.usWinAscent, do.usWinDescent = s(so.usWinAscent), s(so.usWinDescent)
    return (dh.ascent, dh.descent, dh.lineGap)


def main():
    if not paths.SARABUN_TTF.exists():
        print("!! ไม่พบ %s" % paths.SARABUN_TTF)
        return 1
    pk = PakFile(paths.PAK_MAIN)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = OUT_DIR / "_vanilla.ufont"
    for face in FACES:
        gpath = FONT_DIR_GAME + face + ".ufont"
        tmp.write_bytes(pk.read(gpath))
        src = TTFont(tmp, fontNumber=0, lazy=True)
        dst = TTFont(paths.SARABUN_TTF)
        before = (dst["hhea"].ascent, dst["hhea"].descent, dst["hhea"].lineGap)
        upem_src = src["head"].unitsPerEm
        after = copy_metrics(src, dst)
        out = OUT_DIR / (face + ".ttf")
        dst.save(out)
        h_src = (src["hhea"].ascent - src["hhea"].descent + src["hhea"].lineGap) / upem_src
        h_out = (after[0] - after[1] + after[2]) / dst["head"].unitsPerEm
        print("%-26s vanilla %5d/%-5d gap %-4d upem %-4d = %.3f em -> สำเนา %5d/%-5d gap %-4d = %.3f em"
              % (face, src["hhea"].ascent, src["hhea"].descent, src["hhea"].lineGap,
                 upem_src, h_src, after[0], after[1], after[2], h_out))
        src.close()
        dst.close()
    tmp.unlink(missing_ok=True)
    print("เขียน %d ไฟล์ -> %s (metric เท่าต้นฉบับ · กลิฟ/cmap เป็นของ %s)"
          % (len(FACES), OUT_DIR, paths.SARABUN_TTF.name))
    print("หมายเหตุ: สำเนาพวกนี้ ascender เตี้ยกว่าตัวหลัก จึงอาจ crop วรรณยุกต์ที่ซ้อนสระบน "
          "(กลิฟ .small ของ Sarabun สูงถึง 1265) — เป็นราคาที่แลกกับความสูงบรรทัดเท่าเกมเดิม")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
