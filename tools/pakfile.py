#!/usr/bin/env python3
"""ตัวอ่านไฟล์ .pak แบบ legacy (UE4 PakFile v11) ของ Like a Dragon: Ishin!

ทำไมต้องมีตัวนี้แยกจาก tools/iostore.py:
  Ishin! วางของสองชั้น — asset ของ UE อยู่ใน IoStore (.utoc/.ucas) แต่ **ข้อมูลเกมจริง
  ของ RGG อยู่ใน pakchunk0-WindowsNoEditor.pak แบบ legacy** (data/wdr_<lang>/msg/*.msg,
  data/**/*.bin, *.gmd, *.par ฯลฯ) ซึ่ง IoStore ไม่มี → ข้อความที่ต้องแปลอยู่ในไฟล์นี้

ข้อเท็จจริงที่ยืนยันกับไฟล์เกมจริงแล้ว (1 ก.ย. 2026):
  - pak version 11 · index ไม่เข้ารหัส · EncryptionKeyGuid = 0 → ไม่ต้องใช้ AES key
  - pakchunk0 = 23.9 GB · 35,646 ไฟล์ · compression = Zlib
  - .msg 15,112 ไฟล์ (แยก 8 ภาษาใต้ data/wdr_{ja,en,fr,de,it,es,ko,cn}/msg/)
"""
import struct
import sys
import zlib
from pathlib import Path

PAK_MAGIC = b"\xe1\x12\x6fZ"
FOOTER_SCAN = 1024


def _read_fstring(buf, off):
    (n,) = struct.unpack_from("<i", buf, off)
    off += 4
    if n == 0:
        return "", off
    if n > 0:
        return buf[off:off + n - 1].decode("utf-8", "replace"), off + n
    n = -n
    return buf[off:off + (n - 1) * 2].decode("utf-16-le", "replace"), off + n * 2


class PakEntry:
    __slots__ = ("offset", "size", "usize", "method", "blocks", "encrypted",
                 "block_size", "header_size")

    def __init__(self, offset, size, usize, method, blocks, encrypted, block_size):
        self.offset = offset
        self.size = size
        self.usize = usize
        self.method = method
        self.blocks = blocks
        self.encrypted = encrypted
        self.block_size = block_size


class PakFile:
    """เปิด .pak แล้วอ่านสารบัญเต็ม (FullDirectoryIndex) + คลายข้อมูลราย entry"""

    def __init__(self, path):
        self.path = Path(path)
        self.f = open(self.path, "rb")
        self._read_footer()
        self._read_index()

    # ---- footer ----
    def _read_footer(self):
        size = self.path.stat().st_size
        self.f.seek(max(0, size - FOOTER_SCAN))
        tail = self.f.read()
        pos = tail.rfind(PAK_MAGIC)
        if pos < 0:
            raise ValueError("ไม่พบ pak magic: %s" % self.path)
        self.encrypted_index = tail[pos - 1] != 0
        if self.encrypted_index:
            raise NotImplementedError("index is AES-encrypted; not supported")
        o = pos + 4
        self.version, = struct.unpack_from("<I", tail, o)
        o += 4
        self.index_offset, self.index_size = struct.unpack_from("<qq", tail, o)
        o += 16 + 20                                  # ข้าม index hash
        self.methods = [None] + [
            tail[o + i * 32: o + (i + 1) * 32].rstrip(b"\0").decode("ascii", "replace")
            for i in range(5)
        ]

    # ---- index ----
    def _read_index(self):
        self.f.seek(self.index_offset)
        idx = self.f.read(self.index_size)
        o = 0
        self.mount_point, o = _read_fstring(idx, o)
        self.num_entries, = struct.unpack_from("<I", idx, o)
        o += 4
        o += 8                                        # PathHashSeed
        has_ph, = struct.unpack_from("<I", idx, o)
        o += 4
        if has_ph:
            o += 16 + 20                              # PathHashIndex offset/size + hash
        has_fd, = struct.unpack_from("<I", idx, o)
        o += 4
        if not has_fd:
            raise NotImplementedError("pak has no FullDirectoryIndex")
        fd_off, fd_size = struct.unpack_from("<qq", idx, o)
        o += 16 + 20
        enc_size, = struct.unpack_from("<i", idx, o)
        o += 4
        self.encoded = idx[o:o + enc_size]

        self.f.seek(fd_off)
        fd = self.f.read(fd_size)
        base = self.mount_point.replace("../../../", "")
        self.files = {}
        p = 0
        ndir, = struct.unpack_from("<I", fd, p)
        p += 4
        for _ in range(ndir):
            dname, p = _read_fstring(fd, p)
            nfile, = struct.unpack_from("<I", fd, p)
            p += 4
            for _ in range(nfile):
                fname, p = _read_fstring(fd, p)
                enc_off, = struct.unpack_from("<i", fd, p)
                p += 4
                self.files[(base + dname.lstrip("/") + fname)] = enc_off

    # ---- entry ----
    def _decode_entry(self, enc_off):
        b = self.encoded
        flags, = struct.unpack_from("<I", b, enc_off)
        o = enc_off + 4
        if (flags & 0x3F) == 0x3F:          # sentinel = block size ตามหลังมาเป็น uint32
            block_size, = struct.unpack_from("<I", b, o)
            o += 4
        else:
            block_size = (flags & 0x3F) << 11
        block_count = (flags >> 6) & 0xFFFF
        encrypted = bool(flags & (1 << 22))
        method = (flags >> 23) & 0x3F
        if flags & (1 << 31):
            offset, = struct.unpack_from("<I", b, o); o += 4
        else:
            offset, = struct.unpack_from("<Q", b, o); o += 8
        if flags & (1 << 30):
            usize, = struct.unpack_from("<I", b, o); o += 4
        else:
            usize, = struct.unpack_from("<Q", b, o); o += 8
        if method:
            if flags & (1 << 29):
                size, = struct.unpack_from("<I", b, o); o += 4
            else:
                size, = struct.unpack_from("<Q", b, o); o += 8
        else:
            size = usize
        # ขนาดหัว FPakEntry ที่ serialize ไว้หน้าข้อมูลจริง — ต้องรู้ก่อนคำนวณตำแหน่งบล็อก
        hdr = 8 + 8 + 8 + 4 + 20                      # offset,size,usize,method,hash
        if method:
            hdr += 4 + block_count * 16               # จำนวนบล็อก + (start,end) แบบ int64
        hdr += 1 + 4                                  # bEncrypted + CompressionBlockSize

        # บล็อกใน encoded index เก็บ "ขนาดบีบอัด" ตัวละ uint32 · start/end นับจากต้น entry
        blocks = []
        if method:
            if block_count == 1 and not encrypted:
                blocks = [(hdr, hdr + size)]
            else:
                align = 16 if encrypted else 1
                cur = hdr
                for _ in range(block_count):
                    csize, = struct.unpack_from("<I", b, o)
                    o += 4
                    blocks.append((cur, cur + csize))
                    cur += (csize + align - 1) // align * align
        e = PakEntry(offset, size, usize, method, blocks, encrypted, block_size)
        e.header_size = hdr
        return e

    def read(self, game_path):
        e = self._decode_entry(self.files[game_path])
        if e.encrypted:
            raise NotImplementedError("entry is encrypted: %s" % game_path)
        if not e.method:
            self.f.seek(e.offset + e.header_size)
            return self.f.read(e.size)
        name = self.methods[e.method] if e.method < len(self.methods) else None
        out = bytearray()
        for s, en in e.blocks:
            self.f.seek(e.offset + s)
            raw = self.f.read(en - s)
            if name and name.lower() == "zlib":
                out += zlib.decompress(raw)
            else:
                raise NotImplementedError("unsupported compression: %s" % name)
        return bytes(out[:e.usize])

    def glob(self, needle):
        n = needle.lower()
        return sorted(p for p in self.files if n in p.lower())

    def extract(self, game_path, out_root):
        dst = Path(out_root) / game_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(self.read(game_path))
        return dst

    def __repr__(self):
        return "<PakFile %s v%d files=%d>" % (self.path.name, self.version, len(self.files))


def _main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) < 3:
        print(__doc__)
        print("usage: python tools/pakfile.py <file.pak> list [substring]")
        print("       python tools/pakfile.py <file.pak> extract <substring> <out_dir>")
        return 2
    pak = PakFile(argv[1])
    print(pak, file=sys.stderr)
    cmd = argv[2]
    if cmd == "list":
        for p in pak.glob(argv[3] if len(argv) > 3 else ""):
            print(p)
    elif cmd == "extract":
        hits = pak.glob(argv[3])
        for p in hits:
            pak.extract(p, argv[4])
        print("extracted %d files -> %s" % (len(hits), argv[4]))
    else:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
