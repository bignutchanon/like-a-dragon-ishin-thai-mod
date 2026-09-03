#!/usr/bin/env python3
"""แตกคลังข้อความ .msg ของ Ishin! ออกจาก pak แล้วถอดเป็น JSON ให้ทีมแปลใช้

ทำสองอย่างในรอบเดียว:
  1. คัดไฟล์ .msg ของภาษาที่เลือกออกจาก pakchunk0 มาไว้ที่ extracted/msg_<lang>/ (ต้นฉบับ ห้ามแก้)
  2. ถอดสตริงออกเป็น extracted/text_<lang>/<uid>.json (คีย์ = ชื่อไฟล์#ออฟเซ็ต)

ใช้:
  python scripts/extract_msg.py            # ภาษา carrier (en) + ja ไว้เทียบ
  python scripts/extract_msg.py --lang en --force

กติกา: ไฟล์ในเกมห้ามแตะ — สคริปต์นี้เปิด pak แบบอ่านอย่างเดียวเท่านั้น
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                  # noqa: E402  (ต้อง insert path ก่อน)
from pakfile import PakFile                   # noqa: E402
from msg import MsgFile                       # noqa: E402


def run(langs, force=False):
    pak = PakFile(paths.PAK_MAIN)
    print(pak, file=sys.stderr)
    summary = {}
    for lang in langs:
        needle = "/wdr_%s/msg/" % lang
        files = sorted(p for p in pak.files if needle in p)
        raw_dir = paths.EXTRACTED / ("msg_%s" % lang)
        json_dir = paths.EXTRACTED / ("text_%s" % lang)
        raw_dir.mkdir(parents=True, exist_ok=True)
        json_dir.mkdir(parents=True, exist_ok=True)

        n_ok = n_fail = n_str = 0
        failures = []
        for p in files:
            name = p.rsplit("/", 1)[-1]
            dst = raw_dir / name
            if force or not dst.exists():
                dst.write_bytes(pak.read(p))
            try:
                m = MsgFile(dst.read_bytes(), name)
            except Exception as e:            # เก็บไว้รายงาน ห้ามเงียบ
                n_fail += 1
                failures.append("%s: %s" % (name, e))
                continue
            recs = m.to_records()
            n_ok += 1
            n_str += len(recs)
            (json_dir / (Path(name).stem + ".json")).write_text(
                json.dumps(recs, ensure_ascii=False, indent=1), encoding="utf-8")

        summary[lang] = {"files": len(files), "parsed": n_ok, "failed": n_fail,
                         "strings": n_str, "failures": failures}
        print("%s: ไฟล์ %d · ถอดสำเร็จ %d · พัง %d · สตริง %d"
              % (lang, len(files), n_ok, n_fail, n_str), file=sys.stderr)

    (paths.EXTRACTED / "extract_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    return summary


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")   # console Windows = cp1252 ห้ามลืม
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", action="append", help="ระบุได้หลายครั้ง (ค่าเริ่มต้น: en ja)")
    ap.add_argument("--force", action="store_true", help="ดึงไฟล์ .msg ใหม่ทับของเดิม")
    a = ap.parse_args()
    langs = a.lang or [paths.CARRIER, "ja"]
    run(langs, a.force)


if __name__ == "__main__":
    main()
