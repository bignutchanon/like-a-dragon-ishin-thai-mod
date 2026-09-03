"""Minimal UE4/UE5 .locres reader/writer (Optimized_CityHash64_UTF16 / Optimized / Compact versions).

Usage:
  python locres.py dump <file.locres> <out.json>
  python locres.py build <in.json> <out.locres>

JSON format: { "namespace": { "key": "value", ... }, ... }
"""
import json
import struct
import sys

MAGIC = bytes([0x0E, 0x14, 0x74, 0x75, 0x67, 0x4A, 0x03, 0xFC, 0x4A, 0x15, 0x90, 0x9D, 0xC3, 0x37, 0x7F, 0x1B])


def read_ue_string(f):
    (n,) = struct.unpack("<i", f.read(4))
    if n == 0:
        return ""
    if n < 0:
        data = f.read(-n * 2)
        return data.decode("utf-16-le").rstrip("\x00")
    data = f.read(n)
    return data.decode("utf-8").rstrip("\x00")


def write_ue_string(out, s):
    # Match common locres writers: ASCII-safe -> utf-8 with null, else utf-16
    if s == "":
        # UE serializes empty FString as length 1 + null terminator
        out += struct.pack("<i", 1) + b"\x00"
        return out
    try:
        enc = (s + "\x00").encode("ascii")
        out += struct.pack("<i", len(enc))
        out += enc
    except UnicodeEncodeError:
        enc = (s + "\x00").encode("utf-16-le")
        out += struct.pack("<i", -(len(enc) // 2))
        out += enc
    return out


def crc32_table():
    # UE uses a custom CRC32 (reflected, poly 0x04C11DB7) via lookup - standard zlib crc32 works for StrCrc32 on bytes? No.
    pass


def _crc_table(poly):
    table = []
    for i in range(256):
        c = i
        for _ in range(8):
            c = (c >> 1) ^ (poly if c & 1 else 0)
        table.append(c)
    return table


_CRC32_TABLE = _crc_table(0xEDB88320)


def strcrc32(s):
    """UE FCrc::StrCrc32 for a python string (handles UTF-16 code units per UE logic)."""
    crc = 0xFFFFFFFF
    for ch in s:
        c = ord(ch)
        crc = (crc >> 8) ^ _CRC32_TABLE[(crc ^ c) & 0xFF]
        c >>= 8
        crc = (crc >> 8) ^ _CRC32_TABLE[(crc ^ c) & 0xFF]
        c >>= 8
        crc = (crc >> 8) ^ _CRC32_TABLE[(crc ^ c) & 0xFF]
        c >>= 8
        crc = (crc >> 8) ^ _CRC32_TABLE[(crc ^ c) & 0xFF]
    return (~crc) & 0xFFFFFFFF


def dump(path, out_path):
    f = open(path, "rb")
    magic = f.read(16)
    if magic != MAGIC:
        raise SystemExit("Not a modern locres file (legacy format not supported)")
    version = f.read(1)[0]
    (strings_offset,) = struct.unpack("<q", f.read(8))
    if version >= 2:  # Optimized: has entry count
        (total_count,) = struct.unpack("<I", f.read(4))
    (ns_count,) = struct.unpack("<I", f.read(4))

    # read localized string array first
    pos_after_header = f.tell()
    f.seek(strings_offset)
    (str_count,) = struct.unpack("<I", f.read(4))
    strings = []
    for _ in range(str_count):
        s = read_ue_string(f)
        if version >= 2:
            f.read(4)  # ref count
        strings.append(s)
    f.seek(pos_after_header)

    result = {}
    for _ in range(ns_count):
        if version >= 1:
            f.read(4)  # namespace key hash
        ns = read_ue_string(f)
        (key_count,) = struct.unpack("<I", f.read(4))
        entries = {}
        for _ in range(key_count):
            if version >= 1:
                f.read(4)  # key hash
            key = read_ue_string(f)
            f.read(4)  # source string hash
            (idx,) = struct.unpack("<i", f.read(4))
            entries[key] = strings[idx]
        result[ns] = entries
    f.close()
    with open(out_path, "w", encoding="utf-8") as o:
        json.dump({"version": version, "data": result}, o, ensure_ascii=False, indent=1)
    total = sum(len(v) for v in result.values())
    print(f"version={version} namespaces={len(result)} entries={total} strings={len(strings)}")


def dump_hashes(path, out_path):
    """Dump with source-string hashes preserved so build can round-trip them."""
    f = open(path, "rb")
    magic = f.read(16)
    if magic != MAGIC:
        raise SystemExit("Not a modern locres file")
    version = f.read(1)[0]
    (strings_offset,) = struct.unpack("<q", f.read(8))
    if version >= 2:
        struct.unpack("<I", f.read(4))
    (ns_count,) = struct.unpack("<I", f.read(4))
    pos_after_header = f.tell()
    f.seek(strings_offset)
    (str_count,) = struct.unpack("<I", f.read(4))
    strings = []
    for _ in range(str_count):
        s = read_ue_string(f)
        if version >= 2:
            f.read(4)
        strings.append(s)
    f.seek(pos_after_header)
    result = {}
    for _ in range(ns_count):
        if version >= 1:
            f.read(4)
        ns = read_ue_string(f)
        (key_count,) = struct.unpack("<I", f.read(4))
        entries = {}
        for _ in range(key_count):
            if version >= 1:
                f.read(4)
            key = read_ue_string(f)
            (src_hash,) = struct.unpack("<I", f.read(4))
            (idx,) = struct.unpack("<i", f.read(4))
            entries[key] = {"hash": src_hash, "text": strings[idx]}
        result[ns] = entries
    f.close()
    with open(out_path, "w", encoding="utf-8") as o:
        json.dump({"version": version, "data": result}, o, ensure_ascii=False, indent=1)
    total = sum(len(v) for v in result.values())
    print(f"version={version} namespaces={len(result)} entries={total} strings={len(strings)}")


def build(in_path, out_path):
    with open(in_path, "r", encoding="utf-8") as i:
        doc = json.load(i)
    version = doc["version"]
    data = doc["data"]
    if version < 2:
        raise SystemExit("build only supports version >= 2 (Optimized)")

    # collect unique strings with ref counts
    strings = []
    string_index = {}
    refcount = []
    total_entries = 0
    for ns, entries in data.items():
        for key, val in entries.items():
            text = val["text"] if isinstance(val, dict) else val
            if text not in string_index:
                string_index[text] = len(strings)
                strings.append(text)
                refcount.append(0)
            refcount[string_index[text]] += 1
            total_entries += 1

    body = b""
    for ns, entries in data.items():
        body = body + struct.pack("<I", strcrc32(ns))
        body = write_ue_string(body, ns)
        body += struct.pack("<I", len(entries))
        for key, val in entries.items():
            if isinstance(val, dict):
                text, src_hash = val["text"], val["hash"]
            else:
                text, src_hash = val, 0
            body += struct.pack("<I", strcrc32(key))
            body = write_ue_string(body, key)
            body += struct.pack("<I", src_hash)
            body += struct.pack("<i", string_index[text])

    header = MAGIC + bytes([version])
    strings_offset = len(header) + 8 + 4 + 4 + len(body)
    header += struct.pack("<q", strings_offset)
    header += struct.pack("<I", total_entries)
    header += struct.pack("<I", len(data))

    out = header + body
    out += struct.pack("<I", len(strings))
    for i, s in enumerate(strings):
        out = write_ue_string(out, s)
        out += struct.pack("<I", refcount[i])
    with open(out_path, "wb") as o:
        o.write(out)
    print(f"wrote {out_path}: namespaces={len(data)} entries={total_entries} strings={len(strings)}")


def dump_full(path, out_path):
    """Dump preserving ALL raw hashes (namespace hash, key hash, source hash) for exact rebuild."""
    f = open(path, "rb")
    magic = f.read(16)
    if magic != MAGIC:
        raise SystemExit("Not a modern locres file")
    version = f.read(1)[0]
    (strings_offset,) = struct.unpack("<q", f.read(8))
    if version >= 2:
        struct.unpack("<I", f.read(4))
    (ns_count,) = struct.unpack("<I", f.read(4))
    pos_after_header = f.tell()
    f.seek(strings_offset)
    (str_count,) = struct.unpack("<I", f.read(4))
    strings = []
    raw_lengths = []
    for _ in range(str_count):
        (n,) = struct.unpack("<i", f.read(4))
        if n == 0:
            s = ""
        elif n < 0:
            s = f.read(-n * 2).decode("utf-16-le").rstrip("\x00")
        else:
            s = f.read(n).decode("utf-8").rstrip("\x00")
        raw_lengths.append(n)
        if version >= 2:
            f.read(4)
        strings.append(s)
    f.seek(pos_after_header)
    namespaces = []
    for _ in range(ns_count):
        (ns_hash,) = struct.unpack("<I", f.read(4))
        ns = read_ue_string(f)
        (key_count,) = struct.unpack("<I", f.read(4))
        entries = []
        for _ in range(key_count):
            (key_hash,) = struct.unpack("<I", f.read(4))
            key = read_ue_string(f)
            (src_hash,) = struct.unpack("<I", f.read(4))
            (idx,) = struct.unpack("<i", f.read(4))
            entries.append({"kh": key_hash, "key": key, "sh": src_hash, "idx": idx})
        namespaces.append({"nh": ns_hash, "ns": ns, "entries": entries})
    f.close()
    doc = {"version": version, "namespaces": namespaces, "strings": strings, "raw_lengths": raw_lengths}
    with open(out_path, "w", encoding="utf-8") as o:
        json.dump(doc, o, ensure_ascii=False, indent=1)
    total = sum(len(n["entries"]) for n in namespaces)
    print(f"version={version} namespaces={len(namespaces)} entries={total} strings={len(strings)}")


def build_full(in_path, out_path):
    """Rebuild from a dump_full document, preserving raw hashes and structure exactly."""
    doc = json.load(open(in_path, encoding="utf-8"))
    version = doc["version"]
    namespaces = doc["namespaces"]
    strings = doc["strings"]

    # ref counts from entry indices
    refcount = [0] * len(strings)
    total_entries = 0
    for n in namespaces:
        for e in n["entries"]:
            refcount[e["idx"]] += 1
            total_entries += 1

    body = b""
    for n in namespaces:
        body += struct.pack("<I", n["nh"])
        body = write_ue_string(body, n["ns"])
        body += struct.pack("<I", len(n["entries"]))
        for e in n["entries"]:
            body += struct.pack("<I", e["kh"])
            body = write_ue_string(body, e["key"])
            body += struct.pack("<I", e["sh"])
            body += struct.pack("<i", e["idx"])

    header = MAGIC + bytes([version])
    strings_offset = len(header) + 8 + 4 + 4 + len(body)
    header += struct.pack("<q", strings_offset)
    header += struct.pack("<I", total_entries)
    header += struct.pack("<I", len(namespaces))

    raw_lengths = doc.get("raw_lengths")
    out = header + body
    out += struct.pack("<I", len(strings))
    for i, s in enumerate(strings):
        rl = raw_lengths[i] if raw_lengths and i < len(raw_lengths) else None
        out += encode_table_string(s, rl)
        out += struct.pack("<I", refcount[i])
    with open(out_path, "wb") as o:
        o.write(out)
    print(f"wrote {out_path}: namespaces={len(namespaces)} entries={total_entries} strings={len(strings)}")


def encode_table_string(s, raw_len=None):
    """Encode a localized string UE-style. If raw_len (from an exact dump) still fits, honor it."""
    if raw_len is not None:
        if raw_len < 0:
            enc = (s + "\x00").encode("utf-16-le")
            if len(enc) // 2 == -raw_len:
                return struct.pack("<i", raw_len) + enc
        elif raw_len > 0:
            try:
                enc = (s + "\x00").encode("ascii")
                if len(enc) == raw_len:
                    return struct.pack("<i", raw_len) + enc
            except UnicodeEncodeError:
                pass
        else:
            return struct.pack("<i", 0)
    # heuristic (UE writer behaviour): empty -> length 1 + null; pure-ANSI -> bytes+null; else UTF-16+null
    if s == "":
        return struct.pack("<i", 1) + b"\x00"
    try:
        enc = (s + "\x00").encode("ascii")
        return struct.pack("<i", len(enc)) + enc
    except UnicodeEncodeError:
        enc = (s + "\x00").encode("utf-16-le")
        return struct.pack("<i", -(len(enc) // 2)) + enc


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "dump":
        dump(sys.argv[2], sys.argv[3])
    elif cmd == "dumph":
        dump_hashes(sys.argv[2], sys.argv[3])
    elif cmd == "build":
        build(sys.argv[2], sys.argv[3])
    elif cmd == "dumpfull":
        dump_full(sys.argv[2], sys.argv[3])
    elif cmd == "buildfull":
        build_full(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit("unknown command")
