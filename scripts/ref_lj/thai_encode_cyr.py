#!/usr/bin/env python3
"""slot map ชุดที่สองของ LJTH — donor = **Cyrillic** สำหรับฟอนต์ตระกูล `tbgm_0p` / `tbcgr_0p`

ทำไมต้องมีสองชุด (ยืนยันกับไฟล์เกมจริง 22 ส.ค. 2026):
- เมนู/ไตเติลวาดด้วย `metaoffcpro-condbook` ซึ่งมี Latin-1 accented ครบ → ใช้ `thai_encode.py` (สาย Y8)
- ซับบทสนทนาโหมด EN วาดด้วย `tbgm_0p_hires` (`font2_style.font_face_en`) ซึ่งเป็นฟอนต์ญี่ปุ่น
  **ไม่มี Latin-1 accented เลย** (มีแค่ ¥ § ¨ ¬ ° ± ´ ¶ × ÷) แต่มี **Cyrillic ครบ 66 ตัวพอดี**
  → ชุดนี้ใช้ Cyrillic เป็น donor แบบเดียวกับ K2R/K3

ตัวอักษรไทย 66 ตัวเป็นชุดเดียวกับ `thai_encode.py` (จะได้ใช้คำแปลชุดเดียวกันได้ทั้งสองฟอนต์)
เรียงตาม codepoint ไทย map ลง Cyrillic slot ที่ **มีอยู่จริงในฟอนต์** เรียงตาม codepoint:
  U+0401 (Ё) · U+0410..U+044F (А..я 64 ตัว) · U+0451 (ё)
ไม่แตะ ASCII และไม่แตะ Latin-1 → ตัวเลข/ชื่ออังกฤษ/tag ในเกมยังแสดงปกติ

พฤติกรรม encode เหมือนกันทั้งสองชุด: มาร์ก (สระบน/ล่าง/วรรณยุกต์) ถูกเรียงไป **หน้า** พยัญชนะฐาน
เพราะกลิฟมาร์กถูกตั้ง advance = 0 แล้ววาดทับตำแหน่งปากกาเดียวกัน
"""
from thai_encode import COMBINING, is_cons  # ใช้กติกา reorder ชุดเดียวกัน
from thai_encode import DECODE as _LATIN1_DECODE

# ตัวอักษรไทยชุดเดียวกับ thai_encode.py (66 ตัว เรียงตาม codepoint)
THAI_CHARS = sorted(set(_LATIN1_DECODE.values()))
assert len(THAI_CHARS) == 66

# Cyrillic slot ที่มีจริงใน tbgm_0p / tbgm_0p_hires / tbcgr_0p (66 ตัวพอดี)
DONOR_SLOTS = [0x0401] + list(range(0x0410, 0x0450)) + [0x0451]
assert len(DONOR_SLOTS) == 66

DECODE = {cp: th for cp, th in zip(DONOR_SLOTS, THAI_CHARS)}
ENCODE = {th: cp for cp, th in DECODE.items()}
assert all(not (0x20 <= cp <= 0x7E) for cp in DECODE), "donor ต้องไม่ใช่ ASCII"


def encode(s):
    """ไทย (Unicode ปกติ) -> สตริง codepoint slot (มาร์กเรียงก่อนพยัญชนะฐาน)"""
    n = len(s)
    out = []
    i = 0
    while i < n:
        c = s[i]
        if is_cons(c):
            j = i + 1
            marks = []
            while j < n and s[j] in COMBINING:
                marks.append(s[j])
                j += 1
            if marks:
                for m in marks:
                    out.append(chr(ENCODE[m]) if m in ENCODE else m)
                out.append(chr(ENCODE[c]) if c in ENCODE else c)
                i = j
                continue
        out.append(chr(ENCODE[c]) if c in ENCODE else c)
        i += 1
    return "".join(out)


def coverage(text):
    """คืนตัวอักษรไทยใน text ที่ยังไม่มีใน map"""
    return sorted({c for c in text if 0x0E00 <= ord(c) <= 0x0E7F and c not in ENCODE})


if __name__ == "__main__":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    print("ไทย %d ตัว -> donor Cyrillic %d slot" % (len(THAI_CHARS), len(DONOR_SLOTS)))
    for w in ["เริ่มเกมใหม่", "เล่นต่อ", "ยากามิ", "ไคโตะ"]:
        print("%-16s -> %s" % (w, " ".join("%04X" % ord(c) for c in encode(w))))
