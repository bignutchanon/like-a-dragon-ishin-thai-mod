#!/usr/bin/env python3
"""แตกตารางฐานข้อมูล ARMP (`db.macan/<lang>/*.bin`) ออกจาก pak แล้วแปลงเป็น JSON

ตารางพวกนี้คือ "ข้อความฝั่ง UI/ระบบ" ของ Ishin! — เมนู · ไอเทม · ทักษะ · tips · ชื่อศัตรู ฯลฯ
ฟอร์แมตเป็น **ARMP v2 ตัวเดียวกับ Dragon Engine** → ใช้ `tools/reARMP_fixed.py` ที่ยกมาจาก
โปรเจกต์ Lost Judgment ได้ตรง ๆ (ยืนยันแล้ว 1 ก.ย. 2026: magic `armp` ครบทั้ง 122 ตาราง)

⚠ reARMP ประกอบกลับ **ไม่ได้ไบต์เท่าเดิม** (ขนาดต่างเพราะ padding) — เป็นแบบนี้กับไฟล์ของ
   Lost Judgment เหมือนกัน ไม่ใช่ปัญหาเฉพาะภาคนี้ ด่านตรวจจึงต้องเทียบ **ไบต์ในแถว** กับ
   ต้นฉบับ ไม่ใช่เทียบทั้งไฟล์ (พอร์ต `check_layout_all.py` จาก ref_lj มาใช้ — ยังไม่ทำ)

ใช้:
  python scripts/extract_db.py               # ภาษา carrier (en)
  python scripts/extract_db.py --lang ja --force
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                  # noqa: E402
from pakfile import PakFile                   # noqa: E402

REARMP = paths.TOOLS / "reARMP_fixed.py"


def run(lang, force=False):
    pak = PakFile(paths.PAK_MAIN)
    print(pak, file=sys.stderr)
    needle = "db.macan/%s/" % lang
    files = sorted(p for p in pak.files if needle in p)
    bin_dir = paths.EXTRACTED / ("db_%s" % lang)
    bin_dir.mkdir(parents=True, exist_ok=True)

    n_new = n_json = 0
    for p in files:
        name = p.rsplit("/", 1)[-1]
        dst = bin_dir / name
        if force or not dst.exists():
            dst.write_bytes(pak.read(p))
            n_new += 1
        js = dst.with_suffix(".bin.json")
        if force or not js.exists():
            # reARMP เป็นสคริปต์ CLI (ไม่ใช่ไลบรารี) — เรียกเป็น subprocess และต้องป้อน stdin
            # เพราะมันจบด้วย input("Press ENTER to exit...")
            # ⚠ มันเขียนผลลัพธ์ลง **cwd ของตัวเอง** ไม่ใช่ข้าง ๆ ไฟล์ input → ต้องตั้ง cwd ให้
            subprocess.run([sys.executable, str(REARMP), dst.name],
                           cwd=str(bin_dir), input=b"\n", capture_output=True, check=False)
            if js.exists():
                n_json += 1

    # สรุปขนาดงานฝั่งข้อความ
    total_text = total_rows = 0
    per_table = []
    for js in sorted(bin_dir.glob("*.bin.json")):
        d = json.loads(js.read_text(encoding="utf-8"))
        t, r = d.get("TEXT_COUNT", 0), d.get("ROW_COUNT", 0)
        total_text += t
        total_rows += r
        per_table.append({"table": js.name.replace(".bin.json", ""), "text": t, "rows": r})
    per_table.sort(key=lambda x: -x["text"])
    (paths.EXTRACTED / ("db_%s_summary.json" % lang)).write_text(
        json.dumps({"tables": len(per_table), "rows": total_rows,
                    "text_count": total_text, "per_table": per_table},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print("%s: ตาราง %d · ดึงใหม่ %d · แปลง JSON %d · แถวรวม %d · TEXT_COUNT รวม %d"
          % (lang, len(files), n_new, n_json, total_rows, total_text), file=sys.stderr)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default=paths.CARRIER)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    run(a.lang, a.force)


if __name__ == "__main__":
    main()
