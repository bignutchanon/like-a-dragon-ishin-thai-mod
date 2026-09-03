#!/usr/bin/env python3
"""เข้ารหัสไทย -> codepoint slot ของ SDF font (system_main_en_all_sdf) แนว glyph-remapping
อ้างอิงม็อด AI v1.3 (ดู docs/refmod_analysis.md) — ยืนยัน map ด้วยการ decode db เขากลับเป็นไทยถูกต้อง

หลักการ:
- เกมไม่ route Thai Unicode -> ใช้ slot Latin/Cyrillic/Greek ที่ฟอนต์วาดรูปไทยทับไว้
- สระลอย/วรรณยุกต์ (combining) เรียง "ก่อน" พยัญชนะฐาน (มาร์ก adv=0 วาดที่ pen, พยัญชนะวาดทับ)
"""

# ⚠ 29 ส.ค. 2026 — ย้าย donor ของ ก / ุ / ู จาก U+03B2 (β) · U+0101 (ā) · U+014D (ō)
# ไปที่ U+00A4 (¤) · U+00A6 (¦) · U+00A2 (¢) เพราะฟอนต์ tt2025m ซึ่งวาดเทลอปสถานที่/วันที่
# (ui_texture_text.bin) ไม่มีสามตัวเดิมอยู่ในไฟล์เลย และไฟล์นั้นมี tail จริง 18,248 ไบต์
# จึงแทรก glyph ใหม่เข้าไปไม่ได้อย่างปลอดภัย (ดู docs/ISSUES.md LJ-002)
# สามตัวใหม่เลือกจากชุดที่ฟอนต์ฝั่ง Latin ทั้งแปดตัวมีครบ และไม่ปรากฏในต้นฉบับอังกฤษเลยสักครั้ง
# (นับจาก extracted/strings_by_bin.json) จึงไม่ชนกับข้อความเดิมของเกม

# codepoint slot -> ตัวอักษรไทย (verified: decode db ม็อดเขาออกมาอ่านถูก)
DECODE = {
 0xAA:'ป',0xB5:'ฎ',0xB6:'ฐ',0xC6:'ฌ',0xC7:'ฏ',0xC9:'ญ',0xCB:'ฝ',0xD0:'ณ',0xD1:'ซ',
 0xD2:'ฉ',0xD3:'ฤ',0xD4:'โ',0xD5:'ใ',0xD6:'ไ',0xD8:'ฬ',0xD9:'ศ',0xDA:'ส',0xDB:'ฑ',
 0xDC:'ฟ',0xDD:'ช',0xDE:'ต',0xDF:'ษ',0xE0:'ฯ',0xE2:'ข',0xE3:'ค',0xE4:'ฮ',0xE5:'ล',
 0xE6:'ฆ',0xE7:'ด',0xE8:'ผ',0xE9:'ธ',0xEA:'น',0xEB:'บ',0xEC:'แ',0xED:'เ',0xEE:'า',
 0xEF:'ะ',0xF0:'ง',0xF1:'พ',0xF2:'ภ',0xF3:'ว',0xF4:'ม',0xF5:'ย',0xF6:'ถ',0xF8:'ๆ',
 0xF9:'ร',0xFA:'ห',0xFB:'อ',0xFD:'ท',0xFF:'จ',0x00A4:'ก',0x0152:'ฒ',
 # สระบน/วรรณยุกต์ (upper) + สระล่าง (lower) — เรียงก่อน base
 0xC0:'ิ',0xC1:'์',0xC2:'ั',0xC3:'ี',0xC4:'ึ',0xC5:'ื',0xC8:'็',0xCA:'้',0xCC:'๊',
 0xCD:'่',0xCE:'๋',0xCF:'ำ',0x00A6:'ุ',0x00A2:'ู',
}
# ไทย -> codepoint (เลือกตัวแรกถ้ามีหลาย slot)
ENCODE = {}
for cp, th in DECODE.items():
    ENCODE.setdefault(th, cp)

# combining ที่ต้องเรียงก่อน base (สระบน/ล่าง/วรรณยุกต์) — ไม่รวมสระเรียง เ แ โ ใ ไ ะ า ำ
COMBINING = set('ิีึืั็่้๊๋์ฺุู')  # + ำ? ำ เป็นสระเรียง (มี advance) ไม่ reorder

def is_cons(c):      return 0x0E01 <= ord(c) <= 0x0E2E

def encode(s):
    """ไทย(Unicode ปกติ) -> สตริง codepoint slot (มาร์กเรียงก่อนพยัญชนะ)
    ตัวที่ไม่มีใน map (อังกฤษ/เลข/สัญลักษณ์) ส่งผ่านตามเดิม"""
    n = len(s); out = []; i = 0
    while i < n:
        c = s[i]
        if is_cons(c):
            j = i + 1; marks = []
            while j < n and s[j] in COMBINING:
                marks.append(s[j]); j += 1
            if marks:
                for m in marks:                      # มาร์กก่อน
                    out.append(chr(ENCODE[m]) if m in ENCODE else m)
                out.append(chr(ENCODE[c]) if c in ENCODE else c)   # พยัญชนะหลัง
                i = j; continue
        out.append(chr(ENCODE[c]) if c in ENCODE else c)
        i += 1
    return ''.join(out)

def coverage(text):
    """คืนชุดตัวอักษรไทยใน text ที่ยังไม่มีใน ENCODE"""
    return sorted({c for c in text if 0x0E00 <= ord(c) <= 0x0E7F and c not in ENCODE})

if __name__ == '__main__':
    import sys, io, json
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    for w in ['เกมใหม่','เล่นต่อ','ตั้งค่า','มินิเกม','ซื้อ','ที่นี่','ผู้เล่น','ข้อมูลใบอนุญาต']:
        print(f'{w:18s} -> ' + ' '.join('%04X'%ord(c) for c in encode(w)))
    if len(sys.argv) > 1:
        m = json.load(io.open(sys.argv[1], encoding='utf-8'))
        allth = ''.join(v for v in m.values() if isinstance(v, str))
        miss = coverage(allth)
        print(f'\nตัวอักษรไทยใน {sys.argv[1]} ที่ยังไม่มีใน map: {len(miss)}')
        print('  ', ' '.join(f'{c}(U+{ord(c):04X})' for c in miss))
