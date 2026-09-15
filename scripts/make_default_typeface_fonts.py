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
# `DF-FutoKaiSho-W9` กับ `FOT-UDKakugo_LargePr6N-DB` เป็น DefaultTypeface ของ `Font_System` ด้วย
# v1.3 ทับสองตัวนี้ด้วย **Sarabun ดิบ** (metric 1.640 em) แล้วบรรทัดห่างขึ้นทั้งเกม จึงถูกคืนเป็นไฟล์เดิม
# ตอนนั้นยังไม่มีสำเนา metric เท่าต้นฉบับ — สองตัวนี้ไม่เคยถูกลองด้วยวิธีของสคริปต์นี้
# เพิ่มกลับ (test_12 · 13 ก.ย. 2026) ตอนนั้นเชื่อว่าจอแข่งไก่ป้ายว่างเพราะ widget เลือกฟอนต์ผ่าน `E_Font` ->
# `Font_CmnGothic`/`Font_CmnMincho` — ⚠ แก้แล้ว 16 ก.ย. 2026: widget แข่งไก่อ้าง `HTT-GFKaisho-E_Font` ตรง ๆ (research §5.2.2)
# สองตัวนี้ยังต้องคงไว้สำหรับ 14 widget ที่อ้าง Font_CmnMincho/Gothic ตรง ๆ แต่ไม่ใช่ตัวแก้จอแข่งไก่
# ⚠ ถ้าบรรทัดทั้งเกมห่างขึ้นอีก = วิธีสำเนา metric ใช้กับ Font_System ไม่ได้ ให้ถอดสองตัวนี้ออก
FACES = [
    "DF-FutoKaiSho-W9",
    "FOT-UDKakugo_LargePr6N-DB",
    "DF_GOKUBUTOKAISHO_W12",
    "DF_ENKAISHO_W5",
    "DF_REISHO_W6",
    "TT_KswHannya",
    "TT_KswHiryu",
    "TT_KswKaisho",
    "TT_KswReisho",
    "TT_KokinEdo-EB",
    # HUD มินิเกมอุด้ง (ภาพผู้ใช้ 15 ก.ย. 2026: ป้าย ยอดขาย/เวลาที่เหลือ/ชื่อชาม/หน้าสรุปผล ว่าง เหลือแต่ ":" กับตัวเลข)
    # widget WBP_Mg_Udon_* ใช้ CompositeFont `HTT-GFKaisho-E_Font` (ชื่อไม่ขึ้นต้น Font_ จึงหลุดจากรอบไล่ 21 ตัว)
    # sub-font EFIGS = Kuro-Medium ช่วงหยุดที่ U+077F · DefaultTypeface = FontFace/HTT-GFKaisho-E.ufont (research §5.2.2)
    # สแกน widget ทั้งเกม 2,061 ไฟล์: ฟอนต์นี้ใช้ 38 widget = อุด้ง 11 · แข่งไก่ 20 (ป้ายที่ว่างใน test_12) · โชฮัง 4 · ซีโล 2 · ผ่าฟืน 1
    "HTT-GFKaisho-E",
]


# FontFace ที่ต้องคง metric แนวตั้ง **เท่าต้นฉบับทุกช่อง** (ไม่ดัน ascender ครอบกลิฟ)
# ทำไม: สองตัวนี้เป็น DefaultTypeface ของ Font_System (ฟอนต์เกือบทั้งเกม) — test_12/13 ใช้วิธีดัน ascender
# แล้วหักคืนที่ lineGap แล้ว **ตัวหนังสือทั้งเมนูหยุดเกมหดลง** (ภาพผู้ใช้ 13 ก.ย. 2026)
# = Slate คิดความสูงจาก ascender-descender โดยไม่นับ lineGap (1.8 em แทน 1.0 em -> กล่อง auto-fit ย่อข้อความ)
# ข้อความไทยของ Font_System วาดด้วย sub-font EFIGS (Sarabun) อยู่แล้ว DefaultTypeface ให้แค่ metric
# → metric เท่าเดิม = เลย์เอาต์เท่าเกมเดิม · แลกกับวรรณยุกต์ซ้อนอาจโดน crop ในจอ Font_CmnGothic/CmnMincho
EXACT_METRICS = {"DF-FutoKaiSho-W9", "FOT-UDKakugo_LargePr6N-DB"}


def copy_metrics_exact(src, dst):
    """คัดลอก metric แนวตั้งจาก src มาเป๊ะ (สเกลตาม upem) — ไม่แตะเพื่อครอบกลิฟ"""
    k = dst["head"].unitsPerEm / src["head"].unitsPerEm

    def s(v):
        return int(round(v * k))

    sh, dh = src["hhea"], dst["hhea"]
    dh.ascent, dh.descent, dh.lineGap = s(sh.ascent), s(sh.descent), s(sh.lineGap)
    so, do = src["OS/2"], dst["OS/2"]
    do.sTypoAscender, do.sTypoDescender, do.sTypoLineGap = (
        s(so.sTypoAscender), s(so.sTypoDescender), s(so.sTypoLineGap))
    do.usWinAscent, do.usWinDescent = s(so.usWinAscent), s(so.usWinDescent)
    # ⭐ FontFace ของเกมนี้ตั้ง LayoutMethod = BoundingBox (อ่านจาก uasset ทุกตัว 13 ก.ย. 2026)
    # = Slate คิดความสูงบรรทัดจาก head.yMin/yMax ของทั้งฟอนต์ ไม่ใช่ ascender/descender
    # vanilla DF-FutoKaiSho-W9 = -144/881 (1.00 em) แต่ Sarabun = -535/1265 (1.80 em)
    # → ทับแล้วบรรทัด Font_System สูง 1.8 เท่า (test_13 ข้อความหด · test_14 บรรทัดหน้าคำเตือนห่าง)
    # ต้องบันทึกด้วย recalcBBoxes=False ไม่งั้น fontTools คำนวณ bbox จากกลิฟใหม่ทับค่านี้
    dst["head"].yMin, dst["head"].yMax = s(src["head"].yMin), s(src["head"].yMax)
    return (dh.ascent, dh.descent, dh.lineGap)


def copy_metrics(src, dst):
    """คัดลอก metric แนวตั้งจาก src มาใส่ dst โดยสเกลตามอัตราส่วน upem

    ascender/descender ถูกดันให้ครอบกลิฟสูงสุด/ต่ำสุดของ Sarabun เสมอ (yMax 1265 / yMin -535)
    แล้วหักส่วนที่เกินคืนที่ `lineGap` (ค่าติดลบ) เพื่อให้ **ความสูงบรรทัดเท่าฟอนต์ญี่ปุ่นต้นฉบับ**
    FreeType คิด `face->height` = ascender - descender + lineGap จึงคุมระยะบรรทัดได้จากช่องนี้
    ส่วนกรอบที่ใช้ crop กลิฟมาจาก ascender/descender ตรง ๆ (docs/research.md §5.3)
    """
    k = dst["head"].unitsPerEm / src["head"].unitsPerEm
    g_max, g_min = dst["head"].yMax, dst["head"].yMin

    def s(v):
        return int(round(v * k))

    sh, dh = src["hhea"], dst["hhea"]
    height = s(sh.ascent) - s(sh.descent) + s(sh.lineGap)   # ความสูงบรรทัดเดิมของเกม
    asc = max(s(sh.ascent), g_max)
    desc = min(s(sh.descent), g_min)
    gap = height - (asc - desc)                              # ติดลบ = ดึงบรรทัดกลับมาชิดเท่าเดิม

    dh.ascent, dh.descent, dh.lineGap = asc, desc, gap
    so, do = src["OS/2"], dst["OS/2"]
    do.sTypoAscender, do.sTypoDescender, do.sTypoLineGap = asc, desc, gap
    do.usWinAscent, do.usWinDescent = asc, -desc
    return (asc, desc, gap)


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
        dst = TTFont(paths.SARABUN_TTF, recalcBBoxes=face not in EXACT_METRICS)
        before = (dst["hhea"].ascent, dst["hhea"].descent, dst["hhea"].lineGap)
        upem_src = src["head"].unitsPerEm
        after = copy_metrics_exact(src, dst) if face in EXACT_METRICS else copy_metrics(src, dst)
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
    print("หมายเหตุ: ascender/descender ครอบกลิฟเต็ม (1265/-535) แล้วหักคืนที่ lineGap ติดลบ "
          "→ วรรณยุกต์ซ้อนสระบนไม่โดน crop และความสูงบรรทัดยังเท่าเกมเดิม")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
