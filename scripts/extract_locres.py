#!/usr/bin/env python3
"""แตก `Game.locres` (ตารางข้อความของ UE) ออกจาก pak แล้วถอดเป็น JSON

ชั้นข้อความชั้นที่สามของ Ishin! ต่อจาก `.msg` (บทพูด) และ ARMP (`db.macan`)
`LikeaDragonIshin/Content/Localization/Game/<lang>/Game.locres` — มีครบ 9 ภาษา

ยืนยันแล้ว 1 ก.ย. 2026 (ไฟล์ EN): locres version 3 · 493 namespace · 23,507 entry ·
สตริงไม่ซ้ำ 14,767 · ขนาด 1.77 MB

ตัวอ่านยกมาจากโปรเจกต์ Frostpunk 2 (`D:\\Projects\\frostpunk-2-translate/tools/locres.py`)
ซึ่งเป็นเกม UE เหมือนกัน — อ่าน/เขียนได้ทั้งคู่ (`dump_full` / `build_full`)

ใช้:
  python scripts/extract_locres.py            # ภาษา carrier (en)
  python scripts/extract_locres.py --lang ja
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                  # noqa: E402
import locres                                 # noqa: E402
from pakfile import PakFile                   # noqa: E402


def run(lang):
    pak = PakFile(paths.PAK_MAIN)
    print(pak, file=sys.stderr)
    needle = "Localization/Game/%s/Game.locres" % lang
    hits = [p for p in pak.files if p.endswith(needle)]
    if not hits:
        print("ไม่พบ %s ใน pak" % needle, file=sys.stderr)
        return 1

    out_dir = paths.EXTRACTED / "locres"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = out_dir / ("Game.%s.locres" % lang)
    raw.write_bytes(pak.read(hits[0]))

    js = out_dir / ("Game.%s.json" % lang)
    locres.dump_full(str(raw), str(js))

    d = json.loads(js.read_text(encoding="utf-8"))
    ns = d.get("namespaces") or []
    n_ns = len(ns) if isinstance(ns, list) else ns
    n_entries = sum(len(x.get("entries", [])) for x in ns) if isinstance(ns, list) else "?"
    n_str = len(d.get("strings") or [])
    print("%s: locres v%s · namespace %s · entry %s · สตริงไม่ซ้ำ %s · ไฟล์ %s"
          % (lang, d.get("version"), n_ns, n_entries, n_str, raw.name), file=sys.stderr)
    return 0


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default=paths.CARRIER)
    a = ap.parse_args()
    raise SystemExit(run(a.lang))


if __name__ == "__main__":
    main()
