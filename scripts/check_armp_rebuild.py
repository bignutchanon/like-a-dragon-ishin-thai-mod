#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ด่านบังคับของชั้น ARMP: ประกอบ `.bin` กลับจาก JSON ต้นฉบับ **โดยไม่แก้อะไรเลย**
แล้วเทียบไบต์ในแถวกับ vanilla ทุกตาราง

ต่างจาก `check_layout_all.py` ตรงที่ตัวนั้นตรวจเฉพาะไฟล์ที่บิลด์จริง (ซึ่งมีเฉพาะตารางที่มีคำแปล)
ส่วนตัวนี้ตรวจ **ทุกตารางในเกม** เพื่อพิสูจน์ล่วงหน้าว่าตัวเขียนของ reARMP ปลอดภัยกับตารางไหนบ้าง
ก่อนจะมีคำแปลมากพอให้แตะตารางเหล่านั้นจริง

ตารางที่ตกด่านนี้ = **ห้ามแตะจนกว่าจะแก้ตัวเขียนได้** (ใส่ชื่อไว้ใน DENY ของ build_text.py)
เพราะ layout ที่เลื่อนไปทับคอลัมน์อื่นทำให้ค่าพารามิเตอร์ของเกมกลายเป็นขยะ ไม่ใช่แค่ข้อความเพี้ยน

ใช้:
  python scripts/check_armp_rebuild.py               # ทุกตาราง (ใช้เวลาหลายนาที)
  python scripts/check_armp_rebuild.py --only tips   # เฉพาะตารางที่ชื่อมีคำนี้
  python scripts/check_armp_rebuild.py --workers 4
"""
import argparse
import concurrent.futures as cf
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                                            # noqa: E402
from armp_layout_check import layout_mismatch           # noqa: E402
from armp_graft import graft                            # noqa: E402

REARMP = paths.TOOLS / "reARMP_fixed.py"
VANILLA = paths.EXTRACTED / "db_en"
REPORT = paths.BUILD / "armp_rebuild_report.md"
DENY = paths.BUILD / "armp_deny.json"


def rebuild_one(js):
    """คืน (ชื่อตาราง, รายการปัญหา) — รายการว่าง = ผ่าน"""
    table = js.name[:-len(".bin.json")]
    van = VANILLA / (table + ".bin")
    if not van.exists():
        return table, ["ไม่มีไฟล์ vanilla ให้เทียบ"]
    with tempfile.TemporaryDirectory(prefix="ishin_armp_") as td:
        td = Path(td)
        src = td / js.name
        src.write_bytes(js.read_bytes())
        subprocess.run([sys.executable, str(REARMP), src.name],
                       cwd=str(td), input=b"\n", capture_output=True, check=False)
        out = td / (src.name + ".bin")
        if not out.exists():
            return table, ["reARMP ประกอบไม่สำเร็จ (ไม่มีไฟล์ผลลัพธ์)"]
        try:
            data, _notes = graft(van, out.read_bytes())
            out.write_bytes(data)
            return table, layout_mismatch(van, out)
        except Exception as e:                          # noqa: BLE001
            return table, ["ตรวจไม่ได้: %s: %s" % (type(e).__name__, e)]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="ตรวจเฉพาะตารางที่ชื่อมีคำนี้")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    files = sorted(VANILLA.glob("*.bin.json"))
    if a.only:
        files = [f for f in files if a.only in f.name]
    if not files:
        sys.exit("!! ไม่พบ JSON ของตาราง ARMP — รัน scripts/extract_db.py ก่อน")

    bad = {}
    done = 0
    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        for table, problems in ex.map(rebuild_one, files):
            done += 1
            if problems:
                bad[table] = problems
                print("  !! %-40s %s" % (table, problems[0][:80]))
            if done % 20 == 0:
                print("     ...ตรวจแล้ว %d/%d" % (done, len(files)))

    print("ตาราง %d · ผ่าน %d · ต่าง %d" % (len(files), len(files) - len(bad), len(bad)))
    L = ["# ARMP rebuild check — ประกอบกลับโดยไม่แก้ แล้วเทียบไบต์ในแถวกับ vanilla", "",
         "> `python scripts/check_armp_rebuild.py` — ห้ามแก้ด้วยมือ", "",
         "| ตัวชี้วัด | ค่า |", "|---|---|",
         "| ตารางที่ตรวจ | %d |" % len(files),
         "| ผ่าน | %d |" % (len(files) - len(bad)),
         "| ต่าง (ห้ามแตะ) | %d |" % len(bad), ""]
    if bad:
        L += ["## ตารางที่ห้ามแตะจนกว่าจะแก้ตัวเขียนได้", ""]
        for t, d in sorted(bad.items()):
            L.append("- **%s** — %s" % (t, " · ".join(d[:3])))
    else:
        L += ["## ผลตรวจ", "", "ผ่านครบทุกตาราง"]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    io.open(REPORT, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    # รายชื่อตารางต้องห้ามในรูปที่สคริปต์อื่นอ่านได้ — build_text.py โหลดไฟล์นี้แล้วข้ามให้เอง
    # (ตรวจครบทั้งชุดเมื่อไหร่ก็เขียนทับ ไม่ต้องมีรายชื่อฝังในโค้ดสองที่)
    if not a.only:
        DENY.write_text(json.dumps({"tables": sorted(bad),
                                    "reason": {t: d[:3] for t, d in sorted(bad.items())}},
                                   ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
        print("เขียน %s (%d ตาราง)" % (DENY, len(bad)))
    print("เขียน %s" % REPORT)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
