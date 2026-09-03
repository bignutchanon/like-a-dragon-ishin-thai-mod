#!/usr/bin/env python3
"""Parser/rebuilder สำหรับฟอร์แมต `FONT!` ของ Y6 (Yakuza 6: The Song of Life)

**ต่างจาก K2R/PIRATE โดยสิ้นเชิง** — ห้ามใช้ font_tool.py (K2R) กับไฟล์ Y6 (parse ไม่ผ่าน
แน่นอน, ยืนยันแล้วด้วย known-answer test ใน docs/recon_font.md §4b: font_tool.py ของ K2R
คาด magic `font` lowercase 4 byte แต่ Y6 ใช้ `FONT!` uppercase+`!` 5 byte + โครง section
คนละแบบสิ้นเชิง — parallel-array (K2R) vs flat interleaved record (Y6))

สเปกที่ reverse-engineer ไว้แล้ว (ที่มา: docs/recon_font.md, ยืนยันด้วยข้อมูลไฟล์จริง
ไม่ใช่เดา — ดู "แหล่งอ้างอิง" ท้ายไฟล์):

  header (48 bytes, offset 0x00-0x2F):
    0x00  magic "FONT!" (5 bytes) + 3 bytes zero padding
    0x10  u32  declared record count (glyph ที่ "ใช้จริง" — น้อยกว่า capacity เสมอถ้ามี
               zero-padding ท้ายตาราง)
    0x14  u32  ค่าคงที่ = 40 ทุกไฟล์ที่เจอ (0x28) — ไม่ใช่ "header size" ตรงๆ แต่ data
               จริงเริ่มที่ align16(40) = 48 (0x30) เสมอ (ยืนยันทุกไฟล์ทดสอบ)
    ที่เหลือ (0x08-0x0F, 0x18-0x2F) = zero ทุกไฟล์ที่เจอ — เก็บทั้ง 48 byte แรกเป็น blob
    ทึบ (ไม่ตีความแยกฟิลด์เกินจำเป็น) แล้วต่อกลับตอน build() เพื่อไม่เสี่ยง byte ที่ยังไม่รู้
    ความหมาย

  record area (offset 0x30 เป็นต้นไป, ยาวจนจบไฟล์):
    ไม่มี "capacity" เก็บตรงในไฟล์ — คำนวณจาก (file_size - 48) / 32 เสมอ (ยืนยัน 7/7 ไฟล์:
    เช่น e/gothic.bin ขนาด 592,048 -> (592048-48)/32 = 18,500 ตรงกับ recon_font.md เป๊ะ)
    ทุก slot (ทั้ง "ใช้จริง" declared_count ตัวแรก และ zero-padding ที่เหลือ) เป็น record
    32 byte รูปแบบเดียวกันหมด — โหลด/เขียนกลับทุก slot เพื่อ round-trip ปลอดภัย 100%
    ไม่ต้องแยก special-case zero-padding เป็นก้อนทึบต่างหาก (ต่างจาก K2R font_tool.py ที่ต้อง
    เก็บ tail แยกเพราะ K2R มี section เสริมที่ตีความไม่ได้ — Y6 ไม่มีปัญหานี้เพราะทุก slot
    เป็น record แบบเดียวกันสม่ำเสมอทั้งไฟล์)

    record (32 bytes):
      +0x00  u32   cp   (UTF-8 bytes packed big-endian เป็นค่าเดียว — สูตรเดียวกับ K2R
                         cp_pack/cp_unpack ใน font_tool.py, ยืนยันด้วยค่า max cp ที่เจอ =
                         0xEFBFA5 decode UTF-8 ได้ตรง U+FFE5 ¥)
      +0x04  u32   variant flag (0 หรือ 1 — e/gothic.bin มี 2 record/cp สลับ flag; ไฟล์อื่น
                         ส่วนใหญ่มี 1 record/cp, flag คงที่ — ความหมายที่แน่ชัดยังไม่ยืนยัน
                         ใน task นี้ เก็บ/คืนค่าตรงๆ พอ ไม่ตีความ)
      +0x08  4×f32 UV [u0, v0, u1, v1] normalized — สูตรเดียวกับ K2R เป๊ะ
      +0x18  4×s16 metrics — K2R มี 5 field (bearingX,bearingY,width,height,advance),
                         Y6 มีแค่ 4 — ความหมายรายฟิลด์ยังไม่ยืนยัน (ต้อง render เทียบภาพจริง
                         ก่อน) เก็บ/คืนค่าตรงๆ เป็น tuple 4 ค่า ไม่ตีความความหมาย

**ขอบเขตงานนี้ (ตามสั่ง): parser/rebuilder + round-trip proof + cp-table dump เท่านั้น
ห้ามเขียน injection logic (แทรก/แก้ glyph) จนกว่าจะมี task แยกต่างหาก**

ใช้:
  python scripts/y6_font_tool.py <file.bin> [<file2.bin> ...]   # round-trip self-test
  python scripts/y6_font_tool.py --dump-cp <file.bin> [--limit N] [--all]

แหล่งอ้างอิง: docs/recon_font.md (หัวข้อ 4b, hexdump + field-by-field), ไฟล์ทดสอบ:
extracted/font/{c,e,j}/{gothic,symbol,mincho}.bin (7 ไฟล์, อ่านอย่างเดียว — extract มาจาก
data/font.par ด้วย ParTool.exe แล้ว ไม่ได้แตะไฟล์เกมตรงๆ)
"""
import argparse
import io
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from font_tool import cp_unpack  # noqa: E402

MAGIC = b"FONT!"
HEADER_SIZE = 0x30   # 48 bytes — align16(40) ยืนยันทุกไฟล์ทดสอบ (ดู docstring)
RECORD_SIZE = 32


def _align16(x):
    return (x + 15) // 16 * 16


class Y6Font:
    def __init__(s, path=None):
        s.header = bytearray(HEADER_SIZE)   # 48 byte แรก เก็บทั้งก้อนแบบทึบ (คืนกลับตรงๆ)
        s.records = []                      # list[[cp:int, flag:int, uv:tuple4float, met:tuple4int16]]
        s.declared_count = 0                # จาก header 0x10 (สะดวกสำหรับ dump — ไม่ใช้ตอน build)
        if path:
            s.load(path)

    def load(s, path):
        d = open(path, "rb").read()
        assert d[:5] == MAGIC, f"not a Y6 FONT! file (magic={d[:5]!r})"
        declared_count = struct.unpack_from("<I", d, 0x10)[0]
        hdr_field = struct.unpack_from("<I", d, 0x14)[0]
        data_off = _align16(hdr_field)
        assert data_off == HEADER_SIZE, (
            f"unexpected header-size field @0x14={hdr_field} -> aligned {data_off} "
            f"(ทุกไฟล์ที่ตรวจไว้ใน recon_font.md ได้ 0x30/48 คงที่ — ไฟล์นี้ต่าง ต้องตรวจสอบเพิ่ม)"
        )
        rest = d[data_off:]
        assert len(rest) % RECORD_SIZE == 0, (
            f"record area ({len(rest)} bytes) ไม่ใช่ผลคูณของ {RECORD_SIZE} — ไฟล์อาจเสีย/ผิดสเปก"
        )
        s.header = bytearray(d[:data_off])
        s.declared_count = declared_count
        capacity = len(rest) // RECORD_SIZE
        s.records = []
        for i in range(capacity):
            off = i * RECORD_SIZE
            cp, flag = struct.unpack_from("<II", rest, off)
            uv = struct.unpack_from("<4f", rest, off + 8)
            met = struct.unpack_from("<4h", rest, off + 24)
            s.records.append([cp, flag, uv, met])

    def build(s):
        out = bytearray(s.header)
        for cp, flag, uv, met in s.records:
            out += struct.pack("<II", cp, flag)
            out += struct.pack("<4f", *uv)
            out += struct.pack("<4h", *met)
        return bytes(out)

    def capacity(s):
        return len(s.records)

    def used_records(s):
        """คืนเฉพาะ record ที่อยู่ในช่วง declared_count ตัวแรก (ตามลำดับในไฟล์ — ไม่ได้ตรวจว่า
        cp!=0 จริง เพราะ K2R ก็นับแบบนี้เหมือนกัน: 'used' = อยู่ในช่วงที่ header ประกาศไว้)"""
        return s.records[: s.declared_count]


def dump_cp_table(path, limit=None, show_all=False):
    """พิมพ์ตาราง cp (index, char, U+XXXX, flag, uv, met) — สำหรับตรวจ/debug ไม่ใช่ injection"""
    f = Y6Font(path)
    print(f"{path}: capacity={f.capacity()} declared_count={f.declared_count} "
          f"header={len(f.header)}B")
    recs = f.records if show_all else f.used_records()
    n = len(recs) if limit is None else min(limit, len(recs))
    print(f"{'idx':>6} {'cp(hex)':>10}  {'char':^6} {'flag':>4}  {'uv':>34}  {'met':>20}")
    for i in range(n):
        cp, flag, uv, met = recs[i]
        ch = cp_unpack(cp)
        if ch and ch.isprintable():
            ch_disp = ch
        elif ch:
            ch_disp = "<U+%04X>" % ord(ch)
        else:
            ch_disp = "<empty>"
        uv_s = "(%.4f,%.4f,%.4f,%.4f)" % uv
        print(f"{i:6d} {cp:#010x}  {ch_disp:^6} {flag:4d}  {uv_s:>34}  {met!s:>20}")
    if n < len(recs):
        print(f"... ({len(recs) - n} record อีก — ใช้ --limit 0 หรือค่ามากขึ้นเพื่อดูทั้งหมด)")


def roundtrip(path):
    f = Y6Font(path)
    orig = open(path, "rb").read()
    built = f.build()
    return f, built == orig, len(orig), len(built)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help=".bin file(s) ของ Y6 (FONT! format)")
    ap.add_argument("--dump-cp", action="store_true", help="พิมพ์ตาราง cp แทนการทำ round-trip test")
    ap.add_argument("--limit", type=int, default=40, help="จำนวนแถวสูงสุดที่พิมพ์ตอน --dump-cp (0 = ไม่จำกัด)")
    ap.add_argument("--all", action="store_true", help="ตอน --dump-cp: รวม zero-padding slot ด้วย (เกิน declared_count)")
    args = ap.parse_args()

    if args.dump_cp:
        for p in args.files:
            dump_cp_table(p, limit=(None if args.limit == 0 else args.limit), show_all=args.all)
        return 0

    ok_count = 0
    for p in args.files:
        try:
            f, ok, n_orig, n_built = roundtrip(p)
        except (AssertionError, struct.error) as e:
            print(f"{p}: PARSE-FAIL {type(e).__name__}: {e}")
            continue
        ok_count += ok
        used = sum(1 for r in f.records if r[0] != 0)
        print(f"{p}: capacity={f.capacity()} declared_count={f.declared_count} "
              f"used(cp!=0)={used} size={n_orig}B "
              f"round-trip={'OK' if ok else f'MISMATCH ({n_orig}B vs {n_built}B)'}")
    print(f"\nสรุป: round-trip OK {ok_count}/{len(args.files)}")
    return 0 if ok_count == len(args.files) else 1


if __name__ == "__main__":
    sys.exit(main())
