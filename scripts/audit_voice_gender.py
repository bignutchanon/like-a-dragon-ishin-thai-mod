#!/usr/bin/env python3
"""วัดว่าคิวเสียงรายบรรทัด (ช่อง `voice` = คำสั่ง 0x03/0x35) เป็นหลักฐานเพศผู้พูดได้แค่ไหน

research §10.1 เคยตีตกป้ายคิวเสียง `haruka_*`/`oryo_*` ว่า "ตรงข้ามกับตัวละคร" แต่ตอนนั้นนับจาก
`labels` ทั้งหมด ซึ่งมีป้ายที่ค้างมาจากบรรทัดอื่น (ชนิดย่อย 0x16 · เช่น `uid01330c9e#107`
บทเรียวมะพก `haruka_door_s02_004`) — สคริปต์นี้นับเฉพาะช่อง `voice` ที่ research §9 ระบุว่ามี
อย่างมากหนึ่งตัวต่อบรรทัด

วิธี: ตัดคำนำหน้าคิว (ส่วนก่อน `_` ตัวแรก) แล้วนับเครื่องหมายเพศในต้นฉบับญี่ปุ่นของบรรทัดนั้นเอง
(`merge_qc.ja_gender`) แยกชาย/หญิง ต่อคำนำหน้า

ใช้: python scripts/audit_voice_gender.py [--min 1] [--show PREFIX]
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                      # noqa: E402
from merge_qc import ja_gender    # noqa: E402


def prefix(voice):
    return voice.split("_", 1)[0].lower() if "_" in voice else voice


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=1, help="แสดงเฉพาะคำนำหน้าที่มีเครื่องหมายรวม >= N")
    ap.add_argument("--show", help="พิมพ์บรรทัดที่ขัดของคำนำหน้านี้")
    args = ap.parse_args()

    rows = json.loads((paths.EXTRACTED / "parallel" / "msg.json").read_text(encoding="utf-8"))
    lines = Counter()
    marks = defaultdict(Counter)
    samples = defaultdict(lambda: defaultdict(list))
    n_voice = 0
    for r in rows:
        v = r.get("voice")
        if not v:
            continue
        n_voice += 1
        p = prefix(v)
        lines[p] += 1
        g = ja_gender(r.get("ja") or "")
        if g:
            marks[p][g] += 1
            samples[p][g].append(r)

    print("บรรทัดทั้งหมด %d · มี voice %d" % (len(rows), n_voice))
    print("%-18s %6s %5s %5s" % ("prefix", "lines", "male", "fem"))
    for p, n in lines.most_common():
        m, f = marks[p]["male"], marks[p]["female"]
        if m + f < args.min:
            continue
        flag = "  <-- ขัด" if m and f else ""
        print("%-18s %6d %5d %5d%s" % (p, n, m, f, flag))

    if args.show:
        p = args.show.lower()
        for g in ("male", "female"):
            print("\n== %s: ja_gender=%s (%d)" % (p, g, len(samples[p][g])))
            for r in samples[p][g][:40]:
                print("  %s  voice=%s\n    JA: %s\n    EN: %s"
                      % (r["key"], r["voice"], (r.get("ja") or "").replace("\r\n", " / ").replace("\n", " / "),
                         (r.get("en") or "").replace("\r\n", " / ").replace("\n", " / ")))


if __name__ == "__main__":
    main()
