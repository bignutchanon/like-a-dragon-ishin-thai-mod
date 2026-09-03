"""กวาด 闘技場 ให้เป็น "สังเวียน" รูปเดียวทั้งคลัง (sprint 16)

`place_locks.json` (`context_only`) ล็อกไว้แล้วว่า `Arena` = **สังเวียน**
แต่คลังมีสองรูปปนกัน: สังเวียน 64 : สนามประลอง 48 — และรูปหลังไม่เคยถูกเคาะให้ใช้ในร้อยแก้ว

⚠ **ข้อยกเว้นที่ต้องคงไว้**: `Arena Points` (闘玉) = **แต้มสนามประลอง**
glossary §1.9.10 ข เคาะไว้แล้วว่าให้ยึดรูปที่ ship ไปแล้ว 5 จุด (ร่างแรกของ lead เขียน
"แต้มสังเวียน" ผิด) — สคริปต์นี้จึงข้ามทุกบรรทัดที่มีคำว่า "แต้มสนามประลอง"

ขอบเขต: เฉพาะคีย์ที่ `ref_ja` มี 闘技場 จริง (33 คีย์) — ไม่แตะบรรทัดที่ "สนามประลอง"
มาจากคำอื่น (วัดแล้ว 2 คีย์ที่ ja ไม่มี 闘技場 เลย)

รันแล้วต้องตามด้วย: merge_qc.py --only <ก้อนที่แก้>
"""
import collections
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DONE = ROOT / "translations" / "done"
PAR = ROOT / "extracted" / "parallel"
KEEP = "แต้มสนามประลอง"      # คำที่เคาะไว้แล้ว ห้ามแตะ
OLD, NEW = "สนามประลอง", "สังเวียน"


def load_ja():
    par = collections.defaultdict(list)
    for name in ("msg.json", "db.json", "locres.json"):
        for r in json.loads((PAR / name).read_text(encoding="utf-8")):
            if r.get("en") and r.get("ja"):
                par[r["en"]].append(r["ja"])
    return par


def main() -> int:
    par = load_ja()
    total = 0
    files = 0
    for path in sorted(DONE.glob("*.done.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        strings = data["strings"]
        hits = 0
        for en, th in list(strings.items()):
            if not th or OLD not in th or KEEP in th:
                continue
            if "闘技場" not in " ".join(par.get(en, [])):
                continue
            strings[en] = th.replace(OLD, NEW)
            hits += 1
        if hits:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            total += hits
            files += 1
            print(f"{path.name[len('batch_'):-len('.done.json')]:>9} · {hits} คีย์")
    print(f"\nแก้ {total} คีย์ · {files} ไฟล์ · คง '{KEEP}' ไว้ตาม glossary §1.9.10 ข")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
