#!/usr/bin/env python3
"""Donor slot map: ตัวอักษรไทย 83 ตัว -> donor codepoint ที่มีอยู่แล้วจริงใน e/gothic.bin
(REPLACE-MODE — ไม่เพิ่มจำนวน glyph, ไม่แก้ cp table เลยแม้แต่ byte เดียว)

วิธีเลือก donor (ดูหลักฐานเต็มใน docs/font_y6_slotmap.md):
  1. dump cp table ของ e/gothic.bin (14,166 glyph ที่ใช้จริง) แล้วจัดกลุ่มตาม Unicode block
  2. Cyrillic U+0400-0452 มีอยู่จริงแค่ 66/83 ช่อง (ยืนยันตรงกับ docs/recon_font.md §5a)
  3. หา 17 ช่องเพิ่มจาก block อื่นที่ (ก) มีอยู่จริงในฟอนต์ (ข) สแกน extracted/db_e/*.json
     ทั้ง 701 ไฟล์ (709,600 string values) แล้วไม่พบเลยแม้แต่ตัวเดียว — เลือก Samaritan
     U+0800-0810 (บล็อกที่ห่างไกลภาษาอังกฤษที่สุดในฟอนต์ ปลอดภัยกว่า Greek/Latin-1/
     เรขาคณิต/ลูกศร ที่อาจโผล่ใน UI จริง เช่น °,×,→,★ ฯลฯ — ดู docs/font_y6_slotmap.md
     หัวข้อ "ทำไมไม่ใช้ Greek/สัญลักษณ์อื่น")
  4. ยืนยันด้วยสคริปต์ scan_corpus (scratch) — 0 hit ทั้ง Cyrillic (U+0400-04FF) และ
     Samaritan (U+0800-082F) ทั้งคลัง db_e

ลำดับ mapping: ใช้ลำดับ THAI_CHARS แบบเดียวกับ K2R (segment ก-ฮ..เลขไทย) เพื่อให้ทีม
คุ้นเคย/เทียบกับ K2R ได้ง่าย — 66 ตัวแรกไปลง Cyrillic (เรียงจากค่า cp น้อยไปมาก),
17 ตัวหลังไปลง Samaritan (เรียงจากค่า cp น้อยไปมาก)
"""

# ---- ตาราง Thai 83 ตัว (เหมือน K2R เป๊ะ — ลำดับ segment ตาม codepoint ไทย) ----
_SEGMENTS = [(0x0E01, 0x0E3A), (0x0E3F, 0x0E3F), (0x0E40, 0x0E4D), (0x0E50, 0x0E59)]
THAI_CHARS = []
for _a, _b in _SEGMENTS:
    THAI_CHARS += [chr(c) for c in range(_a, _b + 1)]
assert len(THAI_CHARS) == 83

# ---- donor codepoints: Cyrillic 66 ตัวที่ "มีอยู่จริง" ใน e/gothic.bin (ไม่ใช่ 0400-0452
# ต่อเนื่อง — ขาด 17 ตัว: 0400, 0402-040F ยกเว้น 0401, 0450, 0452 ตาม recon_font.md §5a) ----
_CYRILLIC_MISSING = {0x0400, 0x0402, 0x0403, 0x0404, 0x0405, 0x0406, 0x0407, 0x0408,
                      0x0409, 0x040A, 0x040B, 0x040C, 0x040D, 0x040E, 0x040F,
                      0x0450, 0x0452}
CYRILLIC_DONORS = [cp for cp in range(0x0400, 0x0453) if cp not in _CYRILLIC_MISSING]
assert len(CYRILLIC_DONORS) == 66

# ---- donor เพิ่ม 17 ตัว: Samaritan U+0800-0810 (มีอยู่จริงในฟอนต์ทั้ง 40 ตัว U+0800-0827
# — ใช้แค่ 17 ตัวแรกก็พอ, สแกน db_e corpus แล้วไม่พบเลย) ----
SAMARITAN_DONORS = [cp for cp in range(0x0800, 0x0811)]
assert len(SAMARITAN_DONORS) == 17

DONOR_CPS = CYRILLIC_DONORS + SAMARITAN_DONORS
assert len(DONOR_CPS) == 83
assert len(set(DONOR_CPS)) == 83, "donor ต้องไม่ซ้ำกัน"
assert all(not (0x20 <= cp <= 0x7E) for cp in DONOR_CPS), "donor ต้องไม่ใช่ ASCII"
assert all(not (0x80 <= cp <= 0xFF) for cp in DONOR_CPS), "donor ต้องไม่ใช่ Latin-1"

# thai char -> donor cp (int)  /  donor cp (int) -> thai char
ENCODE = {th: cp for th, cp in zip(THAI_CHARS, DONOR_CPS)}
DECODE = {cp: th for th, cp in ENCODE.items()}

# ---- จำแนกชนิดตัวอักษรไทย (ใช้ตอน inject กำหนด scale/ตำแหน่งในเซลล์) ----
# มาร์ก (combining, advance=0 ในฟอนต์ที่แก้แล้ว) — เหมือน K2R เป๊ะ
COMBINING = set('ัิีึื็ํ่้๊๋์ฺุู')
assert len(COMBINING) == 15
UPPER = set('ัิีึื็ํ')   # สระบน/ไม้ไต่คู้/นิคหิต (7 ตัว) — วางค่อนบนเซลล์
TONE = set('่้๊๋์')       # วรรณยุกต์+การันต์ (5 ตัว) — วางบนสุด (สูงกว่า UPPER)
LOWER = set('ฺุู')        # สระล่าง (3 ตัว) — วางใต้ baseline
assert UPPER | TONE | LOWER == COMBINING
assert len(UPPER) + len(TONE) + len(LOWER) == 15


def is_cons(c):
    return 0x0E01 <= ord(c) <= 0x0E2E


if __name__ == '__main__':
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print(f'THAI_CHARS = {len(THAI_CHARS)} ตัว, DONOR_CPS = {len(DONOR_CPS)} ตัว')
    print(f'Cyrillic donors: {len(CYRILLIC_DONORS)} (U+{CYRILLIC_DONORS[0]:04X}..U+{CYRILLIC_DONORS[-1]:04X})')
    print(f'Samaritan donors: {len(SAMARITAN_DONORS)} (U+{SAMARITAN_DONORS[0]:04X}..U+{SAMARITAN_DONORS[-1]:04X})')
    for th, cp in list(ENCODE.items())[:5] + list(ENCODE.items())[-5:]:
        print(f'  {th!r} (U+{ord(th):04X}) -> U+{cp:04X} {chr(cp)!r}')
