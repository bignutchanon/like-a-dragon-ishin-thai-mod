#!/usr/bin/env python3
"""ด่านตรวจบังคับ: ประกอบ .msg กลับโดยไม่แก้อะไรเลย ต้องได้ไบต์เท่าเดิมทุกไฟล์

บทเรียนที่จ่ายแพงมาแล้วในโปรเจกต์ก่อน (LJ-011): ถ้าเครื่องมือ decode/encode ตัวเดียวกัน
มีบั๊กเลย์เอาต์ การเทียบ "decode แล้ว encode" จะไม่มีวันจับได้ — ต้องเทียบ **ไบต์ดิบ**
กับต้นฉบับตรง ๆ เท่านั้น สคริปต์นี้ทำแบบนั้น

ใช้:
  python scripts/check_msg_roundtrip.py                 # ตรวจ extracted/msg_en ทั้งโฟลเดอร์
  python scripts/check_msg_roundtrip.py --lang ja --limit 200

ผลที่ต้องได้ก่อนจะเริ่มบิลด์ม็อด: ต่าง 0 ไฟล์
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                  # noqa: E402
from msg import MsgFile                       # noqa: E402


def run(lang, limit=0, show=10):
    src = paths.EXTRACTED / ("msg_%s" % lang)
    if not src.exists():
        print("ยังไม่มี %s — รัน scripts/extract_msg.py ก่อน" % src)
        return 2
    files = sorted(src.glob("*.msg"))
    if limit:
        files = files[:limit]
    same = diff = err = 0
    bad = []
    for f in files:
        raw = f.read_bytes()
        try:
            out = MsgFile(raw, f.name).rebuild({})
        except Exception as e:
            err += 1
            bad.append("%s: อ่านไม่ได้ (%s)" % (f.name, e))
            continue
        if out == raw:
            same += 1
        else:
            diff += 1
            where = next((i for i in range(min(len(out), len(raw))) if out[i] != raw[i]), -1)
            bad.append("%s: ต่างที่ไบต์ 0x%x (ขนาด %d -> %d)" % (f.name, where, len(raw), len(out)))
    print("ตรวจ %d ไฟล์ · เหมือนเดิม %d · ต่าง %d · อ่านไม่ได้ %d" % (len(files), same, diff, err))
    for line in bad[:show]:
        print("   " + line)
    if len(bad) > show:
        print("   ... อีก %d รายการ" % (len(bad) - show))
    return 0 if (diff == 0 and err == 0) else 1


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default=paths.CARRIER)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--show", type=int, default=10)
    a = ap.parse_args()
    raise SystemExit(run(a.lang, a.limit, a.show))


if __name__ == "__main__":
    main()
