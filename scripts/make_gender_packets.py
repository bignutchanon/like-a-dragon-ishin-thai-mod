#!/usr/bin/env python3
"""แบ่งบทสนทนา .msg เป็น "ซอง" ให้ผู้ตรวจ (subagent) ไล่อ่าน EN คู่ JA เพื่อชี้เพศผู้พูด

ทำไมต้องใช้คน/agent อ่าน: `build_scene_gender.py` ตัดสินด้วยเครื่องหมายเพศในญี่ปุ่นแบบนับคำ
จึงชี้ได้เฉพาะฉากที่มีเครื่องหมายฝั่งเดียวล้วน (186 จาก 1,337 ไฟล์) ที่เหลือ 1,151 ไฟล์
มีหลักฐานอยู่แต่ต้อง "อ่านบทสนทนา" ถึงจะเห็น เช่น บรรทัดข้าง ๆ เรียกผู้พูดว่า 姉さん / お嬢さん
หรือ EN บรรทัดถัดไปใช้ he/she แทนผู้พูด

กติกาที่ทำให้ผลของ agent ตรวจซ้ำได้ด้วยเครื่อง (กันการเดา ตาม CLAUDE.md):
ทุกคำตัดสินต้องแนบ `evidence` = คีย์บรรทัดในซองเดียวกัน + ข้อความที่ยกมา **เป๊ะตัวอักษร**
`merge_gender_wave.py` จะเช็กว่าข้อความนั้นมีอยู่จริงในช่อง ja/en/labels ของบรรทัดที่อ้าง
ถ้าไม่มี = ทิ้งคำตัดสินนั้น

ซองควบคุม (`--control`) สร้างจากไฟล์ที่ `scene_gender.json` ชี้ได้แล้ว เอาไว้วัดว่า agent
ตอบตรงกับผลที่วัดความแม่นไว้แล้ว 99.2%/100% แค่ไหน — ใช้ตัดสินว่าจะเชื่อทั้งคลื่นหรือไม่

ใช้:
  python scripts/make_gender_packets.py --lines 800          # ซองงานจริง
  python scripts/make_gender_packets.py --control 2          # ซองควบคุม 2 ซอง
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

OUT = paths.PROJECT / "work" / "gender_wave" / "in"


def load_files():
    par = json.loads((paths.PROJECT / "extracted" / "parallel" / "msg.json").read_text(encoding="utf-8"))
    by = defaultdict(list)
    for r in par:
        if (r.get("en") or "").strip():
            by[r["file"]].append(r)
    return by


def packet_rows(rows):
    out = []
    for r in rows:
        item = {"key": r["key"], "en": r["en"], "ja": r.get("ja") or ""}
        if r.get("labels"):
            item["labels"] = r["labels"]
        out.append(item)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", type=int, default=800, help="จำนวนบรรทัดต่อซอง")
    ap.add_argument("--control", type=int, default=0, help="สร้างซองควบคุมกี่ซอง (จากไฟล์ที่ชี้เพศได้แล้ว)")
    args = ap.parse_args()

    by = load_files()
    scene = json.loads((paths.TRANSLATIONS / "scene_gender.json").read_text(encoding="utf-8"))
    determined = {f for f, rows in by.items() if any(r["en"] in scene for r in rows)}
    pool = sorted(determined) if args.control else sorted(set(by) - determined)
    prefix = "control" if args.control else "packet"

    OUT.mkdir(parents=True, exist_ok=True)
    packets, cur, n = [], [], 0
    for f in pool:
        cur.append(f)
        n += len(by[f])
        if n >= args.lines:
            packets.append(cur)
            cur, n = [], 0
            if args.control and len(packets) >= args.control:
                break
    if cur and not (args.control and len(packets) >= args.control):
        packets.append(cur)

    for i, files in enumerate(packets, 1):
        data = {"packet": "%s_%02d" % (prefix, i),
                "scenes": [{"file": f, "lines": packet_rows(by[f])} for f in files]}
        p = OUT / ("%s_%02d.json" % (prefix, i))
        p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print("%s  ไฟล์ฉาก %3d · บรรทัด %4d" % (p.name, len(files), sum(len(s["lines"]) for s in data["scenes"])))
    print("รวม %d ซอง -> %s" % (len(packets), OUT))


if __name__ == "__main__":
    main()
