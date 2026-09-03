#!/usr/bin/env python3
"""หา batch ที่ไฟล์ done ไม่ตรงกับ master_th แล้ว merge ใหม่ให้อัตโนมัติ

ทำไมต้องมี: ทุกครั้งที่รัน `normalize_terms.py --write` ทั้งโปรเจกต์ คำในไฟล์ `done/*.done.json`
จะถูกแก้ แต่ `master_th.json` **ไม่ได้อัปเดตตาม** จนกว่าจะ `merge_qc.py --only NNN` ของ batch นั้นซ้ำ
— รอบ 21 ส.ค. 2026 มีคำเก่าตกค้างใน master แบบนี้จริง (Ass Catchem 1 จุด จาก batch_089)

ใช้:
  python scripts/remerge_stale.py            # ดูว่ามี batch ไหนค้าง (ไม่เขียนอะไร)
  python scripts/remerge_stale.py --write    # merge ใหม่ให้ทุก batch ที่ค้าง
"""
import argparse
import io
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

DONE = paths.TRANSLATIONS / "done"


REVIEW = paths.TRANSLATIONS / "review"


def stale_batches():
    master = json.load(io.open(paths.MASTER_TH, encoding="utf-8"))
    out = []
    for p in sorted(DONE.glob("*.done.json")):
        d = json.load(io.open(p, encoding="utf-8"))
        bid = str(d.get("batch") or p.name.split(".")[0].replace("batch_", ""))
        # ข้าม batch ที่ยังไม่ผ่านผู้ตรวจ — สคริปต์นี้มีหน้าที่ "ซิงก์ของที่ merge ไปแล้ว"
        # ไม่ใช่ merge งานใหม่แทน lead (เคยเผลอ merge batch ที่ผู้ตรวจยังทำอยู่ 21 ส.ค. 2026)
        if not (REVIEW / ("batch_%s.review.md" % bid)).exists():
            continue
        diff = 0
        for k, v in d["strings"].items():
            if k in master and master[k] != v:
                diff += 1
        if diff:
            out.append((bid, diff))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="merge ใหม่จริง")
    a = ap.parse_args()

    stale = stale_batches()
    if not stale:
        print("master_th ตรงกับไฟล์ done ทุก batch แล้ว")
        return 0
    print("batch ที่ค้าง %d ตัว: %s" % (len(stale), " ".join("%s(%d)" % s for s in stale)))
    if not a.write:
        print("ใส่ --write เพื่อ merge ใหม่")
        return 0
    for bid, _ in stale:
        r = subprocess.run([sys.executable, str(paths.SCRIPTS / "merge_qc.py"), "--only", bid],
                           capture_output=True, text=True, encoding="utf-8")
        tail = [l for l in (r.stdout or "").splitlines() if l.strip()][-1:]
        print("  %s -> %s" % (bid, tail[0] if tail else "(ไม่มีผลลัพธ์)"))
    left = stale_batches()
    print("เหลือค้าง %d ตัว" % len(left))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
