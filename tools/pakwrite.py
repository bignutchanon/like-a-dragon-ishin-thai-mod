#!/usr/bin/env python3
"""ตัวเขียนไฟล์ .pak แบบ legacy (UE4 PakFile v11) — ใช้ทำ pak ม็อดของ Ishin!

คู่กับ `tools/pakfile.py` (ตัวอ่าน) · ด่านตรวจอยู่ที่ `scripts/check_pak_roundtrip.py`

รูปแบบที่เขียน — **ถอดมาจาก pak แท้ของเกมทีละไบต์** (pakchunk1/3-WindowsNoEditor.pak):
  [FPakEntry header + data] × N  →  PathHashIndex  →  FullDirectoryIndex  →  Index  →  Footer 221 ไบต์

ค่าที่ยืนยันกับไฟล์จริงแล้ว (1 ก.ย. 2026):
  - mount point ของ pak แท้ = "../../../LikeaDragonIshin/Content/" (ไม่ใช่รากเปล่า ๆ)
  - pak แท้เขียน **ทั้ง** PathHashIndex และ FullDirectoryIndex (bHasPathHashIndex = 1)
  - encoded entry ของไฟล์ไม่บีบอัด = flags 0xE0000000 + offset u32 + uncompressed size u32
    (ตรงกับที่สคริปต์นี้เขียนทุกไบต์ — เทียบกับ pakchunk3 แล้ว)

⚠ บทเรียนที่เสียเวลาไปหนึ่งรอบ: **path hash ของ pak v11 เป็น FNV-1a 64 ไม่ใช่ CRC32**
  (ชื่อเวอร์ชันในซอร์ส UE คือ `Fnv64BugFix`) และค่าตั้งต้นคือ FNV offset basis **บวก** PathHashSeed
  แฮชคำนวณบน path ที่ตัด mount point ออกแล้ว แปลงเป็นตัวพิมพ์เล็ก เข้ารหัส UTF-16LE
  พิสูจน์แล้วโดยคำนวณย้อนกับ pakchunk3 ของเกม (ได้ค่าตรงกับที่อยู่ในไฟล์จริง)

การติดตั้งม็อด: วางไว้ที่ Content/Paks/~mods/ และชื่อไฟล์ต้องลงท้าย _P (ดู scripts/paths.py)
"""
import hashlib
import struct
import sys
from pathlib import Path

PAK_MAGIC = 0x5A6F12E1
PAK_VERSION = 11
ENTRY_HEADER_SIZE = 8 + 8 + 8 + 4 + 20 + 1 + 4      # ไฟล์ไม่บีบอัด = 53 ไบต์
DEFAULT_MOUNT = "../../../"   # ตรงกับที่ repak ใช้และเกมยอมรับ (ทดสอบในเกมแล้ว)

FNV_PRIME = 0x00000100000001B3
FNV_BASIS = 0xCBF29CE484222325
U64 = 0xFFFFFFFFFFFFFFFF


def fnv64_path(rel_path, seed):
    """แฮช path สำหรับ PathHashIndex ของ pak v11

    `rel_path` = path ที่ตัด mount point ออกแล้ว ไม่มี "/" นำหน้า
    """
    h = (FNV_BASIS + seed) & U64
    for b in rel_path.lower().encode("utf-16-le"):
        h = ((h ^ b) * FNV_PRIME) & U64
    return h


def _fstring(s):
    """FString แบบ UTF-8 + NUL (ความยาวเป็นบวก)"""
    b = s.encode("utf-8") + b"\0"
    return struct.pack("<i", len(b)) + b


def _encode_entry(offset, size):
    """encoded pak entry ของไฟล์ที่ไม่บีบอัด/ไม่เข้ารหัส

    บิต: 31 = offset ใส่ 32 บิตได้ · 30 = uncompressed size ใส่ 32 บิตได้ ·
         29 = size ใส่ 32 บิตได้ · 23-28 = compression method · 22 = encrypted ·
         6-21 = จำนวนบล็อก · 0-5 = block size
    """
    flags = 0
    parts = b""
    if offset <= 0xFFFFFFFF:
        flags |= 1 << 31
        parts += struct.pack("<I", offset)
    else:
        parts += struct.pack("<Q", offset)
    if size <= 0xFFFFFFFF:
        flags |= 1 << 30
        parts += struct.pack("<I", size)
    else:
        parts += struct.pack("<Q", size)
    flags |= 1 << 29
    return struct.pack("<I", flags) + parts


def write_pak(out_path, files, mount_point=DEFAULT_MOUNT, path_hash_seed=0x1234ABCD):
    """สร้าง .pak จาก {path เต็มในเกม: bytes}

    `path เต็มในเกม` = แบบที่ pakfile.py คืนออกมา เช่น
    "LikeaDragonIshin/Content/Localization/Game/en/Game.locres"
    ต้องอยู่ใต้ mount point ที่ระบุ
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    base = mount_point.replace("../../../", "")

    body = bytearray()
    entries = {}                                     # rel_path -> (offset, size)
    for gpath, data in files.items():
        if not gpath.startswith(base):
            raise ValueError("path ไม่อยู่ใต้ mount point %r: %s" % (mount_point, gpath))
        offset = len(body)
        body += struct.pack("<qqq", 0, len(data), len(data))   # offset(ในหัวเขียน 0), size, usize
        body += struct.pack("<I", 0)                           # CompressionMethodIndex
        body += hashlib.sha1(data).digest()
        body += struct.pack("<B", 0)                           # bEncrypted
        body += struct.pack("<I", 0)                           # CompressionBlockSize
        assert len(body) - offset == ENTRY_HEADER_SIZE, "หัว entry ขนาดไม่ตรง"
        body += data
        entries[gpath[len(base):]] = (offset, len(data))

    # ---- encoded pak entries ----
    encoded = bytearray()
    enc_off = {}
    for rel in sorted(entries):
        offset, size = entries[rel]
        enc_off[rel] = len(encoded)
        encoded += _encode_entry(offset, size)

    # ---- PathHashIndex (+ pruned directory index ว่าง) ----
    phi = bytearray(struct.pack("<I", len(entries)))
    for rel in sorted(entries):
        phi += struct.pack("<Q", fnv64_path(rel, path_hash_seed))
        phi += struct.pack("<i", enc_off[rel])
    phi += struct.pack("<I", 0)          # pruned directory index = 0 โฟลเดอร์ (เหมือน pakchunk3 ของเกม)
    phi_offset = len(body)
    body += phi

    # ---- FullDirectoryIndex ----
    # ⚠ ต้องเขียน **ทุกชั้น** ของโฟลเดอร์ ไม่ใช่แค่โฟลเดอร์ปลายทาง
    # (บทเรียนที่ทำให้ pak ไม่ถูก mount อยู่หลายรอบ: ของเราเขียน 2 โฟลเดอร์ ส่วน repak เขียน 12
    #  = ไล่ตั้งแต่ "/" ลงไปทีละชั้น โดยชั้นกลางมี 0 ไฟล์ — UE ต้องการครบถึงจะ mount ให้)
    dirs = {"/": {}}
    for rel in entries:
        d, _, fname = rel.rpartition("/")
        parts = [x for x in d.split("/") if x]
        for i in range(len(parts)):
            dirs.setdefault("/" + "/".join(parts[:i + 1]) + "/", {})
        dirs.setdefault("/" + d + "/" if d else "/", {})[fname] = rel
    fdi = bytearray(struct.pack("<I", len(dirs)))
    for dname in sorted(dirs):
        fdi += _fstring(dname)
        fdi += struct.pack("<I", len(dirs[dname]))
        for fname in sorted(dirs[dname]):
            fdi += _fstring(fname)
            fdi += struct.pack("<i", enc_off[dirs[dname][fname]])
    fdi_offset = len(body)
    body += fdi

    # ---- Index ----
    index = bytearray()
    index += _fstring(mount_point)
    index += struct.pack("<I", len(entries))
    index += struct.pack("<Q", path_hash_seed)
    index += struct.pack("<I", 1)                    # bReaderHasPathHashIndex
    index += struct.pack("<qq", phi_offset, len(phi))
    index += hashlib.sha1(bytes(phi)).digest()
    index += struct.pack("<I", 1)                    # bReaderHasFullDirectoryIndex
    index += struct.pack("<qq", fdi_offset, len(fdi))
    index += hashlib.sha1(bytes(fdi)).digest()
    index += struct.pack("<i", len(encoded))
    index += bytes(encoded)
    index += struct.pack("<i", 0)                    # จำนวน entry ที่ encode ไม่ได้

    index_offset = len(body)
    body += index

    # ---- Footer ----
    footer = bytearray()
    footer += b"\0" * 16                             # EncryptionKeyGuid
    footer += b"\0"                                  # bEncryptedIndex
    footer += struct.pack("<I", PAK_MAGIC)
    footer += struct.pack("<I", PAK_VERSION)
    footer += struct.pack("<qq", index_offset, len(index))
    footer += hashlib.sha1(bytes(index)).digest()
    footer += b"\0" * (32 * 5)                       # ชื่อวิธีบีบอัด (ว่าง = ไม่บีบอัด)
    assert len(footer) == 221, len(footer)
    body += footer

    out_path.write_bytes(bytes(body))
    return out_path


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(__doc__)
