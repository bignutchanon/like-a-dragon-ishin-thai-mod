#!/usr/bin/env python3
"""Parser/rebuilder สำหรับฟอร์แมต `font` ของ Dragon Engine (raster/SDF fonts)
พอร์ตจาก pirate-yakuza-hawaii-thai แล้วแก้ให้รองรับไฟล์ K2R (Kiwami 2 R / lexus2)
สเปกฐาน: PIRATE/docs/font_format.md · ส่วนต่างของ K2R: docs/toolchain_k2r.md

โครง: [header 0x90][cp_table u32][aux 128B][arrayA UV 16B/g][arrayB metrics 10B/g][tail]
- cp = UTF-8 big-endian packed เป็น u32 (เก็บ/เขียน u32 LE ตรงๆ)
- arrayA = 4×float32 (u0,v0,u1,v1) normalized
- arrayB = 5×s16 [bearingX, yBottom, width, yTop, advance] (y-up จาก baseline, em≈1024)
  ยืนยันจาก glyph เดิม: '_'=(0,-168,500,-120,500) height ติดลบถ้าตีเป็น h -> field4 = yTop

การรองรับ tail (สิ่งที่แก้จากเวอร์ชัน pirate ซึ่ง assert 'arrayB does not reach EOF'):
- load() เก็บ bytes ทั้งหมดหลังจบ arrayB ไว้เป็น s.tail (blob ทึบ) และ build() ต่อ
  s.tail กลับท้ายไฟล์เสมอ — ไฟล์ที่ arrayB ยาวถึง EOF พอดีได้ tail = b'' เหมือนเดิม
- K2R system_main_en_all_sdf.bin: tail = 4 bytes ศูนย์ (padding จัดท้ายไฟล์ให้ตรง 16)
  และ header field 0x40/0x48 = 0 -> เคสง่าย
- ไฟล์ SDF ฝั่ง pirate: tail = section เสริม ~27KB โดย header field 0x40/0x48 เป็น
  offset สัมบูรณ์ชี้เข้าไปใน tail
- build() คง header เดิมทั้ง 0x90 (รวม field 0x40/0x48 — ห้าม overwrite เป็นศูนย์)
  อัปเดตเฉพาะ offset 4 ช่อง (0x18 aux / 0x20 cp / 0x30 arrayB / 0x38 arrayA)
  และถ้าจำนวน glyph เปลี่ยนจน layout ขยับ จะเลื่อนค่า 0x40/0x48 ที่ชี้เข้าโซน tail
  ตาม delta ให้อัตโนมัติ (best effort)

!! คำเตือน: ถ้า tail มี offset "ภายในตัวมันเอง" (เคสไฟล์ pirate ~27KB) การ insert/ลบ
   glyph จะทำให้ offset ภายใน tail เพี้ยน — tool นี้มอง tail เป็น blob ทึบ แก้ให้ไม่ได้
   โหมดปลอดภัย = แก้แบบ "แทนที่ค่าเดิม จำนวน glyph เท่าเดิม" (แก้ cp/uv/met ใน slot
   เดิม ไม่เพิ่มไม่ลด -> ทุก offset คงที่ทั้งไฟล์)
   ไฟล์ K2R tail เป็น zero padding ล้วน การเพิ่ม/ลบ glyph จึงไม่พังโครงสร้าง แต่ท้ายไฟล์
   อาจไม่ align 16 เหมือนต้นฉบับ — ใช้ round-trip/in-game test ยืนยันก่อนใช้จริงเสมอ

quirk เพิ่มเติมที่พบในชุดไฟล์ K2R (แก้แล้วในเวอร์ชันนี้):
- ไฟล์ที่จำนวน glyph (K) เป็นคี่ จะมี zero padding 4B ปิดท้าย cp table ให้ aux ตรง
  align 8 -> สูตรเดิม K=(aux_off-cp_off)//4 นับเกิน 1 (ได้ glyph ผี cp=0 แถมมา)
  เวอร์ชันนี้วัด K จากระยะ arrayA->arrayB (=16*K เพราะ 2 array ติดกันเสมอ) แทน
- ตระกูล *_svg เป็นคนละฟอร์แมต (vector) — parse ไม่ได้ เป็นเรื่องคาดหมาย
"""
import struct

HDR = 0x90
AUX = 128

class Font:
    def __init__(s, path=None):
        s.header = bytearray(HDR)
        s.cps = []       # list[int]  (packed UTF-8 BE as u32 value)
        s.uv = []        # list[tuple(4 float)]
        s.met = []       # list[tuple(5 int)]
        s.aux = bytes(AUX)
        s.tail = b''     # ข้อมูลหลังจบ arrayB (K2R: padding 4B / pirate SDF: section ~27KB)
        if path: s.load(path)

    def load(s, path):
        d = open(path, 'rb').read()
        assert d[:4] == b'font', 'not a font file'
        cp_off  = struct.unpack_from('<Q', d, 0x20)[0]
        aux_off = struct.unpack_from('<Q', d, 0x18)[0]
        a_off   = struct.unpack_from('<Q', d, 0x38)[0]   # arrayA (UV)
        b_off   = struct.unpack_from('<Q', d, 0x30)[0]   # arrayB (metrics)
        # ลำดับ section มาตรฐาน cp -> aux -> A -> B (tail อยู่หลัง B เท่านั้น)
        assert HDR <= cp_off <= aux_off <= a_off <= b_off, 'unexpected section order'
        s.header = bytearray(d[:HDR])
        # จำนวน glyph จริงวัดจากระยะ arrayA->arrayB (2 array นี้ติดกันเสมอ)
        # สูตร pirate เดิม (aux_off-cp_off)//4 นับเกิน 1 เมื่อ K เป็นคี่ เพราะ cp table
        # มี zero padding 4B ปิดท้ายให้ aux ตรง align 8 (เจอในไฟล์ K2R เช่น *_ja_all_fhd)
        assert (b_off - a_off) % 16 == 0, 'arrayA..arrayB not multiple of 16'
        K = (b_off - a_off) // 16
        assert (aux_off - cp_off) // 4 == K + (K & 1), \
            'cp table size mismatch vs arrayA/B geometry'
        b_end = b_off + 10 * K
        assert b_end <= len(d), 'arrayB out of file bounds (truncated?)'
        s.cps = list(struct.unpack_from('<%dI' % K, d, cp_off))
        s.aux = d[aux_off:aux_off + AUX]
        s.uv  = [struct.unpack_from('<4f', d, a_off + 16*i) for i in range(K)]
        s.met = [struct.unpack_from('<5h', d, b_off + 10*i) for i in range(K)]
        # เดิม: assert b_end == len(d) -> fail กับ K2R (เกิน 4B) / pirate SDF (เกิน ~27KB)
        # ใหม่: เก็บส่วนเกินเป็น tail แล้วให้ build() ต่อกลับ
        s.tail = d[b_end:]

    def build(s):
        K = len(s.cps)
        assert len(s.uv) == K and len(s.met) == K
        pad = (K & 1) * 4                    # K คี่ -> pad cp table 4B ให้ aux ตรง align 8
        cp_off = HDR
        aux_off = cp_off + 4*K + pad
        a_off = aux_off + AUX
        b_off = a_off + 16*K
        out = bytearray(s.header)            # คง header เดิมทั้ง 0x90 (รวม 0x40/0x48 ฯลฯ)
        struct.pack_into('<Q', out, 0x20, cp_off)
        struct.pack_into('<Q', out, 0x18, aux_off)
        struct.pack_into('<Q', out, 0x38, a_off)
        struct.pack_into('<Q', out, 0x30, b_off)
        # field 0x40/0x48: offset สัมบูรณ์ชี้เข้าโซน tail (เคส pirate; K2R = 0)
        # ถ้าจำนวน glyph เปลี่ยนจน tail ขยับ เลื่อนค่าตาม delta — ค่า 0 หรือค่าที่ชี้
        # ก่อนโซน tail ไม่แตะ (offset ภายใน tail เองแก้ไม่ได้ ดูคำเตือนใน docstring)
        old_a = struct.unpack_from('<Q', s.header, 0x38)[0]
        old_b = struct.unpack_from('<Q', s.header, 0x30)[0]
        if old_b > old_a:
            old_end = old_b + 10 * ((old_b - old_a) // 16)     # จุดเริ่ม tail ตอน load
            delta = (b_off + 10*K) - old_end
            if delta:
                for foff in (0x40, 0x48):
                    v = struct.unpack_from('<Q', s.header, foff)[0]
                    if v >= old_end:
                        struct.pack_into('<Q', out, foff, v + delta)
        out += struct.pack('<%dI' % K, *s.cps)
        out += b'\x00' * pad
        out += s.aux
        for uv in s.uv: out += struct.pack('<4f', *uv)
        for m in s.met: out += struct.pack('<5h', *m)
        out += s.tail                        # ต่อ tail กลับท้ายไฟล์
        return bytes(out)

    def add_glyph(s, cp_packed, uv, met):
        """แทรก/แทนที่ glyph ตามลำดับ sort ของ cp_packed
        (cp ที่มีอยู่แล้ว = แทนที่ค่าเดิม ไม่ขยับ layout — โหมดปลอดภัยสำหรับไฟล์มี tail)"""
        import bisect
        i = bisect.bisect_left(s.cps, cp_packed)
        if i < len(s.cps) and s.cps[i] == cp_packed:
            s.uv[i] = uv; s.met[i] = met
        else:
            s.cps.insert(i, cp_packed); s.uv.insert(i, uv); s.met.insert(i, met)

def cp_pack(ch):
    """ตัวอักษร -> u32 (UTF-8 big-endian packed)"""
    return int.from_bytes(ch.encode('utf-8'), 'big')

def cp_unpack(v):
    """u32 (UTF-8 BE packed) -> ตัวอักษร ('' ถ้า decode ไม่ได้)"""
    b = v.to_bytes(4, 'big').lstrip(b'\x00') or b'\x00'
    try: return b.decode('utf-8')
    except UnicodeDecodeError: return ''

if __name__ == '__main__':
    import sys
    # round-trip test: python font_tool.py <font.bin> [...]
    for p in sys.argv[1:]:
        f = Font(p)
        rebuilt = f.build()
        orig = open(p, 'rb').read()
        ok = rebuilt == orig
        print(f'{p}: glyphs={len(f.cps)} tail={len(f.tail)}B '
              f'round-trip={"OK" if ok else "MISMATCH len %d vs %d" % (len(rebuilt), len(orig))}')
