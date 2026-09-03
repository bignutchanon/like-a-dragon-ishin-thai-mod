#!/usr/bin/env python3
"""สถานะ sprint แปล — ใช้ทุกครั้งที่จะแจกงาน batch ถัดไป (lead ใช้)

พิมพ์: batch ทั้งหมด · ส่งงานแล้ว (done) · ตรวจแล้ว (review) · merge เข้า master_th แล้วเท่าไร
· และ **batch ถัดไปที่ยังไม่มีใครทำ** (จะได้ไม่แจกซ้ำหลังจาก context ถูกสรุป)

ใช้:  python scripts/sprint_status.py [--next 6]
"""
import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

REVIEW = paths.TRANSLATIONS / "review"
DONE = paths.TRANSLATIONS / "done"


def batch_ids():
    out = []
    # ข้ามไฟล์คู่ที่ไม่ใช่ไฟล์งานแปล: บริบทผู้พูด/เพศ (.context.json) ·
    # ผลค้นของที่ ship แล้ว (.priorart.json · .skillart.json)
    for p in sorted(b for b in paths.WORKLIST.glob("batch_*.json")
                    if not b.name.endswith((".context.json", ".priorart.json",
                                            ".skillart.json"))):
        out.append(p.stem.replace("batch_", ""))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--next", type=int, default=6, help="โชว์ batch ว่างถัดไปกี่ตัว")
    a = ap.parse_args()

    inflight = {"translating": [], "reviewing": []}
    fp = paths.BUILD / "sprint_inflight.json"
    if fp.exists():
        inflight = json.load(io.open(fp, encoding="utf-8"))

    ids = batch_ids()
    done = {p.name.split(".")[0].replace("batch_", "") for p in DONE.glob("*.done.json")} if DONE.exists() else set()
    reviewed = {p.name.split(".")[0].replace("batch_", "") for p in REVIEW.glob("*.review.md")} if REVIEW.exists() else set()
    master = json.load(io.open(paths.MASTER_TH, encoding="utf-8")) if paths.MASTER_TH.exists() else {}

    total_strings = 0
    todo = []
    busy = set(inflight.get("translating", [])) | set(inflight.get("reviewing", []))
    for b in ids:
        if b not in done and b not in busy:
            todo.append(b)
    # ⚠ worklist มีไฟล์คู่หลายชนิด (.context.json · .priorart.json) ที่ไม่มีช่อง "strings"
    for p in (b for b in paths.WORKLIST.glob("batch_*.json")
              if not b.name.endswith((".context.json", ".priorart.json", ".skillart.json"))):
        total_strings += len(json.load(io.open(p, encoding="utf-8"))["strings"])

    print("batch ทั้งหมด %d (normal %d · talk %d) · string รวมในคิว %s"
          % (len(ids), sum(1 for b in ids if not b.startswith("TALK")),
             sum(1 for b in ids if b.startswith("TALK")), format(total_strings, ",")))
    print("ส่งงานแล้ว %d · ตรวจแล้ว %d · master_th ตอนนี้ %s คู่"
          % (len(done), len(reviewed), format(len(master), ",")))
    waiting = sorted(done - reviewed)
    print("รอผู้ตรวจ %d: %s" % (len(waiting), " ".join(waiting[:20]) or "-"))
    print("กำลังแปลอยู่ %s · กำลังตรวจอยู่ %s"
          % (" ".join(inflight.get("translating", [])) or "-",
             " ".join(inflight.get("reviewing", [])) or "-"))
    print("ว่างถัดไป %d: %s" % (a.next, " ".join(todo[:a.next]) or "- (แจกครบแล้ว)"))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
