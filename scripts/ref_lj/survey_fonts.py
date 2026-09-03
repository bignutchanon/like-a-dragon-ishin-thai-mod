#!/usr/bin/env python3
"""สำรวจฟอนต์ทั้งหมดใน extracted/font ของ Kiwami 3 — ขั้นแรกของ font phase
ต่อไฟล์ .bin: parse ด้วย font_tool (svg = parse ไม่ได้ เป็นเรื่องคาดหมาย), นับ glyph,
เช็ค round-trip, อ่านฟอร์แมต DDS คู่กัน, และวัด overlap กับ donor slots ของ thai_encode
(donor ที่ "มีหมึกจริง" = ฉีดได้ / ฟอนต์ไหน overlap>0 = ถ้าจอนั้นแสดงข้อความแปล ต้องฉีด)

output: docs/font_survey.md + extracted/font_survey.json
"""
import io, json, struct, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
from paths import EXTRACTED, DOCS
from font_tool import Font, cp_pack, cp_unpack
from thai_encode import ENCODE

FONT_DIR = EXTRACTED / "font"
DONORS = sorted({cp for cp in ENCODE.values() if cp > 0x7F})

def dds_info(p: Path):
    if not p.exists():
        return None
    d = p.open("rb").read(148)
    if d[:4] != b"DDS ":
        return {"fmt": "?not-dds"}
    h = struct.unpack_from("<I", d, 12)[0]
    w = struct.unpack_from("<I", d, 16)[0]
    mips = struct.unpack_from("<I", d, 28)[0]
    pf_flags = struct.unpack_from("<I", d, 80)[0]
    fourcc = d[84:88]
    bitcount = struct.unpack_from("<I", d, 88)[0]
    if pf_flags & 0x4:  # FOURCC
        fmt = fourcc.decode("ascii", "replace")
        if fourcc == b"DX10":
            dxgi = struct.unpack_from("<I", d, 128)[0]
            fmt = f"DX10:{dxgi}"
    else:
        fmt = f"raw{bitcount}"
    return {"w": w, "h": h, "mips": mips, "fmt": fmt, "size": p.stat().st_size}

rows = []
for binp in sorted(FONT_DIR.glob("*.bin")):
    name = binp.stem
    row = {"name": name, "bin_size": binp.stat().st_size,
           "dds": dds_info(binp.with_suffix(".dds"))}
    try:
        f = Font(str(binp))
        row["glyphs"] = len(f.cps)
        row["tail"] = len(f.tail)
        row["roundtrip"] = f.build() == binp.open("rb").read()
        row["cp_sorted"] = f.cps == sorted(f.cps)
        chars = {cp_unpack(v) for v in f.cps}
        row["ascii"] = sum(1 for c in chars if c and ord(c[0]) < 0x80)
        donors_hit = sorted(c for c in chars if c and 0x7F < ord(c[0]) and ord(c[0]) in
                            {d for d in DONORS})
        row["donor_overlap"] = len(donors_hit)
        row["donor_chars"] = "".join(donors_hit)
        row["thai"] = sum(1 for c in chars if c and 0x0E00 <= ord(c[0]) <= 0x0E7F)
        sample = [c for c in ("A", "a", "0", "ก") if cp_pack(c) in set(f.cps)]
        row["has"] = "".join(sample)
    except Exception as e:
        row["error"] = str(e)[:80]
    rows.append(row)

(EXTRACTED / "font_survey.json").write_text(
    json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

parse_ok = [r for r in rows if "glyphs" in r]
errs = [r for r in rows if "error" in r]
md = ["# Font survey — Kiwami 3 (`font.bis.par`)", "",
      f"parse ได้ {len(parse_ok)} / error {len(errs)} (ส่วนใหญ่ควรเป็น *_svg = vector คนละฟอร์แมต)", "",
      "## parse ได้ (SDF/raster)",
      "| font | glyphs | tail | rt | cp_sorted | ascii | donor∩ | donor chars | DDS |",
      "|---|---|---|---|---|---|---|---|---|"]
for r in parse_ok:
    dds = r["dds"]
    ddss = f'{dds["w"]}x{dds["h"]} {dds["fmt"]} m{dds["mips"]}' if dds else "-"
    md.append(f'| {r["name"]} | {r["glyphs"]} | {r["tail"]} | '
              f'{"OK" if r["roundtrip"] else "FAIL"} | {"Y" if r["cp_sorted"] else "N"} | '
              f'{r["ascii"]} | {r["donor_overlap"]} | {r["donor_chars"]} | {ddss} |')
md += ["", "## parse ไม่ได้", "| font | size | error | DDS |", "|---|---|---|---|"]
for r in errs:
    dds = r["dds"]
    ddss = f'{dds["w"]}x{dds["h"]} {dds["fmt"]}' if dds else "-"
    md.append(f'| {r["name"]} | {r["bin_size"]} | {r["error"]} | {ddss} |')
(DOCS / "font_survey.md").write_text("\n".join(md), encoding="utf-8")
print(f"parse OK {len(parse_ok)} / err {len(errs)} -> docs/font_survey.md")
print("donors =", len(DONORS), "slots:", " ".join(chr(d) for d in DONORS))
