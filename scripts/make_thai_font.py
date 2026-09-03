#!/usr/bin/env python3
"""สร้าง font/Sarabun-Regular-ishin.ttf จาก font/Sarabun-Regular.ttf — ฟอนต์ที่ยัดทับ .ufont ของเกม

แก้สองอย่าง (เหตุผลและตัวเลขที่วัดได้: docs/research.md §5.3, HANDOFF.md §0.47):
  1. metric แนวตั้ง: ascender 1068 -> 1290 · descender -232 -> -350 (hhea + OS/2 typo + usWin)
     เพราะกลิฟวรรณยุกต์ที่ยกขึ้นเหนือสระบน (uni0E49.small ฯลฯ) สูงถึง 1265 เกิน ascender เดิม
     -> Slate ตัดขอบบนตามความสูงบรรทัด ไม้โทบน "งั้น" หาย
  2. cmap alias: ตัวอักษรเต็มหลัก (U+FF01-FF5E) · ช่องว่างเต็มหลัก (U+3000) · เครื่องหมายวรรคตอน CJK
     ที่ข้อความ EN/ไทยของเกมใช้จริง (「」。、～ ฯลฯ) ชี้ไปที่กลิฟ ASCII ตัวเดียวกัน
     เพราะ Sarabun ไม่มีกลิฟพวกนี้ -> เกมวาด .notdef (กล่องมี ?) เช่นชื่อการ์ดทหารหน่วยที่ยังไม่ปลดล็อก
     ซึ่งเป็น "？？？？？？？" (U+FF1F เต็มหลัก) ดูเหมือนฟอนต์พัง
     ⚠ ไม่ได้ทำ: ฮิรางานะ/คันจิ (ฟอนต์ไทยไม่มีให้ยืม) · สัญลักษณ์ ★●♪※ (ไม่มีกลิฟใกล้เคียง)

รันซ้ำได้ทุกครั้งที่เปลี่ยนตัวเลข · ผลลัพธ์ต้องผ่าน scripts/check_font_coverage.py (ถ้ามี) ก่อนแพ็ก
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                                  # noqa: E402
from fontTools.ttLib import TTFont            # noqa: E402

SRC = paths.FONT_DIR / "Sarabun-Regular.ttf"
DST = paths.FONT_DIR / "Sarabun-Regular-ishin.ttf"
ASCENDER, DESCENDER = 1290, -350

# codepoint ที่ขาด -> ลำดับ codepoint ที่จะยืมกลิฟ (เอาตัวแรกที่ฟอนต์มี)
ALIASES = {
    0x3000: [0x20],                 # ideographic space
    0x3001: [0x2C],                 # 、 -> ,
    0x3002: [0x2E],                 # 。 -> .
    0x300C: [0x201C, 0x22],         # 「 -> “
    0x300D: [0x201D, 0x22],         # 」 -> ”
    0x300E: [0x201C, 0x22],         # 『
    0x300F: [0x201D, 0x22],         # 』
    0x30FC: [0x2014, 0x2013, 0x2D], # ー -> —
    0xFF65: [0x00B7, 0x2E],         # ･ -> ·
    0x2025: [0x2026, 0x2E],         # ‥ -> …
}
for cp in range(0xFF01, 0xFF5F):    # ！ … ～ -> ! … ~
    ALIASES[cp] = [cp - 0xFF01 + 0x21]


def main():
    f = TTFont(SRC)
    h, o = f["hhea"], f["OS/2"]
    before = (h.ascent, h.descent, o.sTypoAscender, o.sTypoDescender, o.usWinAscent, o.usWinDescent)
    h.ascent, h.descent, h.lineGap = ASCENDER, DESCENDER, 0
    o.sTypoAscender, o.sTypoDescender, o.sTypoLineGap = ASCENDER, DESCENDER, 0
    o.usWinAscent, o.usWinDescent = ASCENDER, -DESCENDER

    cmap = f.getBestCmap()
    added, skipped = [], []
    tables = [t for t in f["cmap"].tables if t.isUnicode()]
    for cp, cands in ALIASES.items():
        if cp in cmap:
            continue
        g = next((cmap[c] for c in cands if c in cmap), None)
        if g is None:
            skipped.append(cp)
            continue
        for t in tables:
            if t.format in (4, 12) and (t.format == 12 or cp <= 0xFFFF):
                t.cmap[cp] = g
        added.append(cp)
    f.save(DST)

    g = TTFont(DST)
    hh, oo = g["hhea"], g["OS/2"]
    cm = g.getBestCmap()
    print("metric: %s -> hhea %d/%d typo %d/%d win %d/%d" % (
        before, hh.ascent, hh.descent, oo.sTypoAscender, oo.sTypoDescender, oo.usWinAscent, oo.usWinDescent))
    print("cmap: เพิ่ม alias %d ตัว · ข้าม %d (%s)" % (
        len(added), len(skipped), " ".join("U+%04X" % c for c in skipped)))
    for cp in (0xFF1F, 0x3000, 0x3002, 0x300C, 0x30FC, 0x0E49):
        print("   U+%04X -> %s" % (cp, cm.get(cp)))
    print("เขียน %s (%d ไบต์ · กลิฟ %d)" % (DST.name, DST.stat().st_size, len(g.getGlyphOrder())))


if __name__ == "__main__":
    main()
