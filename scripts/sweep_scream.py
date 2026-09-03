"""กวาดรูปเสียงกรี๊ด ひいい ให้เหลือรูปเดียว: ฮี้ย…  (ไม้โท ไม่ใช่ไม้ตรี)

ที่นับได้ตอนเคาะ (3 ก.ย. 2026 · หลัง merge คลื่น MSG_073–083):
  ฮี้ย… 9 คีย์  ·  ฮี๊ย… 5 คีย์  — ต้นฉบับเป็น ひいい／ひぃぃ เหมือนกันทุกคีย์
ฮ เป็นอักษรต่ำ ไม้ตรีไม่ใช่รูปมาตรฐาน · รูปไม้โทเป็นฝ่ายมากกว่าอยู่แล้ว
⚠ ไม่แตะ `ฮี่ยะฮ่ะฮ่า` (เสียงหัวเราะ คนละคำ) และไม่แตะ `เฮ่อ ๆ` (へへへ หัวเราะ ≠ เฮ้อ ถอนหายใจ)

รันแบบไม่ใส่ --apply = ดูอย่างเดียว
"""
import json
import sys

from paths import PROJECT

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OLD, NEW = "ฮี๊ย", "ฮี้ย"


def sweep(path, key=None):
    data = json.loads(path.read_text(encoding="utf-8"))
    table = data[key] if key else data
    hits = [k for k, v in table.items() if OLD in v]
    for k in hits:
        table[k] = table[k].replace(OLD, NEW)
    return data, hits


def main() -> int:
    apply = "--apply" in sys.argv
    targets = [(PROJECT / "translations" / "master_th.json", None)]
    targets += [(p, "strings") for p in sorted((PROJECT / "translations" / "done").glob("*.done.json"))]
    total = 0
    for path, key in targets:
        data, hits = sweep(path, key)
        if not hits:
            continue
        total += len(hits)
        print(f"{path.name:30s} {len(hits)} คีย์")
        if apply:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"รวม {total} คีย์" + ("" if apply else "  (ยังไม่เขียนไฟล์ — ใส่ --apply)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
