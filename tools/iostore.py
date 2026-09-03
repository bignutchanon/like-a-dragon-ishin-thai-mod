#!/usr/bin/env python3
"""ตัวอ่านคอนเทนเนอร์ UE4 IoStore (.utoc/.ucas) ของ Like a Dragon: Ishin!

Ishin! (รีเมค 2023) ใช้ Unreal Engine 4.27 ไม่ใช่ Dragon Engine — ไฟล์เกมจึงเป็น
IoStore (.utoc = สารบัญ, .ucas = ข้อมูล) ไม่ใช่ .par/ARMP แบบภาคอื่นในซีรีส์

ข้อเท็จจริงที่ยืนยันกับไฟล์เกมจริงแล้ว (1 ก.ย. 2026):
  - TOC version 3 · block size 65536 · compression = Zlib อย่างเดียว
  - EncryptionKeyGuid = 0 และ container flags = 0x9 (Compressed|Indexed) -> ไม่มี AES
    อ่าน/แตกได้ด้วย Python ล้วน ไม่ต้องพึ่ง oo2core หรือคีย์จากที่ไหน
  - pakchunk0/1/2/3 รวม 279,328 ไฟล์ · ข้อความอยู่ใต้ Content/TextBridge/ และ Content/L10N/<lang>/

หมายเหตุ: ไฟล์ .uasset ที่ได้จาก IoStore เป็นแพ็กเกจรูปแบบ Zen (ไม่ใช่ .uasset แบบ legacy
ที่มี .uexp แยก) — การถอดตารางข้อความต้องอ่านต่อด้วยตัว parser ของ Zen package
"""
import struct
import sys
import zlib
from pathlib import Path

TOC_MAGIC = b"-==--==--==--==-"
INVALID = 0xFFFFFFFF


def _read_fstring(buf, off):
    """FString ของ UE: ความยาวบวก = ASCII/UTF-8, ความยาวลบ = UTF-16LE (นับรวม NUL ปิดท้าย)"""
    (n,) = struct.unpack_from("<i", buf, off)
    off += 4
    if n == 0:
        return "", off
    if n > 0:
        return buf[off:off + n - 1].decode("utf-8", "replace"), off + n
    n = -n
    return buf[off:off + (n - 1) * 2].decode("utf-16-le", "replace"), off + n * 2


class IoStoreContainer:
    """เปิดคู่ .utoc/.ucas หนึ่งชุด แล้วอ่านสารบัญ + แตกไฟล์ตาม path ในเกม"""

    def __init__(self, utoc_path):
        self.utoc_path = Path(utoc_path)
        self.ucas_path = self.utoc_path.with_suffix(".ucas")
        if not self.ucas_path.exists():
            raise FileNotFoundError(self.ucas_path)
        self._parse_toc()

    # ---- สารบัญ ----
    def _parse_toc(self):
        d = self.utoc_path.read_bytes()
        if d[:16] != TOC_MAGIC:
            raise ValueError("not a .utoc file: %s" % self.utoc_path)
        self.version = d[16]
        (self.header_size, self.entry_count, self.block_count, self.block_entry_size,
         self.cm_count, self.cm_len, self.block_size,
         self.dir_index_size, self.partition_count) = struct.unpack_from("<9I", d, 20)
        self.container_id, = struct.unpack_from("<Q", d, 56)
        self.enc_guid = d[64:80].hex()
        self.container_flags = d[80]
        if self.enc_guid != "0" * 32:
            raise NotImplementedError("container is AES-encrypted; reader does not support it")

        off = self.header_size
        off += self.entry_count * 12                       # FIoChunkId[]
        ol_off = off
        off += self.entry_count * 10                       # FIoOffsetAndLength[]
        if self.version >= 4:                              # perfect-hash (ยังไม่พบใน Ishin)
            raise NotImplementedError("TOC version >= 4 not supported")
        blk_off = off
        off += self.block_count * self.block_entry_size
        cm_off = off
        off += self.cm_count * self.cm_len
        dir_off = off

        # offset/length ของแต่ละ chunk = big-endian 5 ไบต์ สองตัว
        self.chunk_ol = []
        for i in range(self.entry_count):
            b = d[ol_off + i * 10: ol_off + i * 10 + 10]
            self.chunk_ol.append((int.from_bytes(b[:5], "big"), int.from_bytes(b[5:], "big")))

        # บล็อกบีบอัด: offset 5 · compressed 3 · uncompressed 3 · method 1
        self.blocks = []
        for i in range(self.block_count):
            b = d[blk_off + i * 12: blk_off + i * 12 + 12]
            self.blocks.append((int.from_bytes(b[:5], "little"),
                                int.from_bytes(b[5:8], "little"),
                                int.from_bytes(b[8:11], "little"),
                                b[11]))

        self.methods = [None] + [
            d[cm_off + i * self.cm_len: cm_off + (i + 1) * self.cm_len].rstrip(b"\0").decode()
            for i in range(self.cm_count)
        ]

        self.files = {}
        if self.dir_index_size:
            self._parse_dir_index(d[dir_off:dir_off + self.dir_index_size])

    def _parse_dir_index(self, di):
        o = 0
        self.mount_point, o = _read_fstring(di, o)
        nd, = struct.unpack_from("<I", di, o)
        o += 4
        dirs = [struct.unpack_from("<4I", di, o + i * 16) for i in range(nd)]
        o += nd * 16
        nf, = struct.unpack_from("<I", di, o)
        o += 4
        files = [struct.unpack_from("<3I", di, o + i * 12) for i in range(nf)]
        o += nf * 12
        ns, = struct.unpack_from("<I", di, o)
        o += 4
        strs = []
        for _ in range(ns):
            s, o = _read_fstring(di, o)
            strs.append(s)

        base = self.mount_point.replace("../../../", "")

        def walk(idx, prefix):
            while idx != INVALID:
                name, first_child, next_sib, first_file = dirs[idx]
                pre = prefix if name == INVALID else prefix + strs[name] + "/"
                fi = first_file
                while fi != INVALID:
                    fname, next_file, user_data = files[fi]
                    self.files[pre + strs[fname]] = user_data
                    fi = next_file
                if first_child != INVALID:
                    walk(first_child, pre)
                idx = next_sib

        walk(0, base)

    # ---- อ่านข้อมูล ----
    def read_chunk(self, chunk_index):
        offset, length = self.chunk_ol[chunk_index]
        first = offset // self.block_size
        last = (offset + length - 1) // self.block_size
        out = bytearray()
        with open(self.ucas_path, "rb") as f:
            for bi in range(first, last + 1):
                boff, csize, usize, method = self.blocks[bi]
                f.seek(boff)
                raw = f.read(csize)
                name = self.methods[method] if method < len(self.methods) else None
                if method == 0 or name is None:
                    data = raw[:usize]
                elif name.lower() == "zlib":
                    data = zlib.decompress(raw)
                else:
                    raise NotImplementedError("unsupported compression: %s" % name)
                out += data
        start = offset - first * self.block_size
        return bytes(out[start:start + length])

    def read_file(self, game_path):
        return self.read_chunk(self.files[game_path])

    def __repr__(self):
        return "<IoStore %s ver=%d entries=%d files=%d>" % (
            self.utoc_path.name, self.version, self.entry_count, len(self.files))


class IoStoreSet:
    """รวมทุก .utoc ในโฟลเดอร์ Paks ให้ค้น/แตกไฟล์ได้เหมือนเป็นระบบไฟล์เดียว"""

    def __init__(self, paks_dir):
        self.containers = []
        for utoc in sorted(Path(paks_dir).glob("*.utoc")):
            try:
                self.containers.append(IoStoreContainer(utoc))
            except Exception as e:   # ข้ามคอนเทนเนอร์ที่อ่านไม่ได้ แต่ต้องบอกเสมอ ห้ามเงียบ
                print("!! skip %s: %s" % (utoc.name, e), file=sys.stderr)
        self.index = {}
        for c in self.containers:
            for p in c.files:
                self.index[p] = c    # คอนเทนเนอร์ท้ายสุดชนะ (patch ทับ base)

    def glob(self, needle):
        n = needle.lower()
        return sorted(p for p in self.index if n in p.lower())

    def read(self, game_path):
        return self.index[game_path].read_file(game_path)

    def extract(self, game_path, out_root):
        data = self.read(game_path)
        dst = Path(out_root) / game_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        return dst


def _main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) < 3:
        print(__doc__)
        print("usage: python tools/iostore.py <paks_dir> list [substring]")
        print("       python tools/iostore.py <paks_dir> extract <substring> <out_dir>")
        return 2
    paks, cmd = argv[1], argv[2]
    s = IoStoreSet(paks)
    for c in s.containers:
        print(c, file=sys.stderr)
    if cmd == "list":
        needle = argv[3] if len(argv) > 3 else ""
        for p in s.glob(needle):
            print(p)
    elif cmd == "extract":
        needle, out = argv[3], argv[4]
        hits = s.glob(needle)
        for p in hits:
            s.extract(p, out)
        print("extracted %d files -> %s" % (len(hits), out))
    else:
        print("unknown command: %s" % cmd)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
