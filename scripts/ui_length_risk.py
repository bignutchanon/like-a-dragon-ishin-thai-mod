"""วัด "บรรทัดไทยยาวเกินกรอบ" ของชั้น UI/ตาราง — ใช้เขียน `docs/INGAME_TEST_CHECKLIST.md`

ทำไมต้องมี: ชั้น `.msg` (บทสนทนา) ขึ้นกล่องข้อความที่ยืดตามเนื้อหา แต่ชั้น ARMP (`db.macan`)
เป็นตาราง/ป้ายเมนูที่ความกว้างตายตัว — ไทยยาวกว่า EN มากจะล้นกรอบหรือถูกตัดท้าย
ด่านตรวจไบต์จับเรื่องนี้ไม่ได้ ต้องให้คนดูบนจอ สคริปต์นี้บอกว่า "ให้ไปดูตรงไหน"

เกณฑ์: ความยาวไทย / ความยาว EN > RATIO (ค่าเริ่มต้น 1.8) และ EN ยาวอย่างน้อย 6 ตัวอักษร
รูปแบบ: python scripts/ui_length_risk.py [--ratio 1.8] [--top 12]
"""
import json
import sys
from collections import Counter, defaultdict

from paths import PROJECT

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def cells(table):
    """คืนค่าสตริงทุกช่องในตาราง ARMP ที่แตกเป็น json แล้ว"""
    for key, row in table.items():
        if not key.isdigit() or not isinstance(row, dict):
            continue
        for group in row.values():
            if not isinstance(group, dict):
                continue
            for col, val in group.items():
                if isinstance(val, str) and val:
                    yield col, val


def main() -> int:
    argv = sys.argv[1:]
    ratio = float(argv[argv.index("--ratio") + 1]) if "--ratio" in argv else 1.8
    top = int(argv[argv.index("--top") + 1]) if "--top" in argv else 12

    master = json.loads((PROJECT / "translations" / "master_th.json").read_text(encoding="utf-8"))
    tally = Counter()
    worst = defaultdict(list)
    total = 0
    for path in sorted((PROJECT / "extracted" / "db_en").glob("*.bin.json")):
        table = json.loads(path.read_text(encoding="utf-8"))
        name = path.name[: -len(".bin.json")]
        seen = set()
        for _col, en in cells(table):
            if en in seen:
                continue
            seen.add(en)
            th = master.get(en)
            if not th or th == en or len(en) < 6:
                continue
            r = len(th) / len(en)
            if r > ratio:
                tally[name] += 1
                total += 1
                worst[name].append((r, en, th))

    # ชั้น locres — จัดกลุ่มตาม namespace (ป้ายเมนู/มินิเกม/ทิปส์อยู่ชั้นนี้)
    loc = json.loads((PROJECT / "extracted" / "locres" / "Game.en.json").read_text(encoding="utf-8"))
    pool = loc["strings"]
    for ns in loc["namespaces"]:
        name = "locres:" + (ns["ns"] or "(ไม่มีชื่อ)")
        seen = set()
        for e in ns["entries"]:
            en = pool[e["idx"]]
            if en in seen:
                continue
            seen.add(en)
            th = master.get(en)
            if not th or th == en or len(en) < 6:
                continue
            r = len(th) / len(en)
            if r > ratio:
                tally[name] += 1
                total += 1
                worst[name].append((r, en, th))

    print(f"สตริงชั้น UI/ตารางที่ไทยยาวเกิน {ratio}× ของ EN: **{total} สตริง**\n")
    for name, n in tally.most_common(top):
        r, en, th = max(worst[name])
        print(f"| `{name}` | {n} | `{en[:52]}` → \"{th[:52]}\" ({r:.1f}×) |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
