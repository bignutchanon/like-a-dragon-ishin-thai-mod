"""กวาดเครื่องหมายไม้ยมก (ๆ) ให้เว้นวรรคข้างหน้าเสมอ

ทำไม (3 ก.ย. 2026 · คลื่น MSG_043–048): คลังมีสองรูปปนกันมาตั้งแต่คลื่นแรก
เว้นวรรค 2,429 จุด · ติดกัน 560 จุด — และผู้ตรวจสองคนสั่งกันคนละทางในคลื่นเดียวกัน
เพราะต่างยึด "รูปข้างมากในกลุ่มที่ตัวเองเห็น"

lead เคาะ: **เว้นวรรคก่อน ๆ เสมอ** — เป็นรูปที่ราชบัณฑิตยสภากำหนด และเป็นรูปข้างมาก
ของคลังอยู่แล้ว (81%) · เทมเพลตข้อความสายสัมพันธ์ที่ ship รูปติดกันไว้ 30 จุด
คือรูปที่ผิด ไม่ใช่บรรทัดฐาน

ใช้:
  python scripts/sweep_maiyamok.py --dry-run     # นับอย่างเดียว
  python scripts/sweep_maiyamok.py               # แก้ไฟล์ done
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DONE = ROOT / "translations" / "done"
# ไม้ยมกที่ติดกับอักษรไทยข้างหน้า — ไม่แตะกรณีที่หน้ามันเป็นช่องว่าง/ต้นสตริงอยู่แล้ว
STUCK = re.compile(r"([ก-๙])ๆ")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    total_files = total_keys = total_hits = 0
    for path in sorted(DONE.glob("batch_*.done.json")):
        d = json.load(io.open(path, encoding="utf-8"))
        strings = d["strings"]
        hits = keys = 0
        for k, v in strings.items():
            if not isinstance(v, str):
                continue
            new, n = STUCK.subn(r"\1 ๆ", v)
            if n:
                hits += n
                keys += 1
                strings[k] = new
        if not hits:
            continue
        total_files += 1
        total_keys += keys
        total_hits += hits
        print("%-32s %3d จุด · %3d คีย์" % (path.name, hits, keys))
        if not a.dry_run:
            io.open(path, "w", encoding="utf-8", newline="\n").write(
                json.dumps(d, ensure_ascii=False, indent=1) + "\n")

    print("\nรวม %d จุด · %d คีย์ · %d ไฟล์%s"
          % (total_hits, total_keys, total_files, "  (dry-run ไม่ได้เขียนไฟล์)" if a.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
