"""กวาดรูปทับศัพท์ชื่อญี่ปุ่นที่สะกดต่างกันข้ามก้อน ให้เหลือรูปเดียว

ที่มา (3 ก.ย. 2026): หลังแก้บั๊กถังของ `check_cross_batch.py` (ก้อน MSG ทั้งซีรีส์เคยยุบ
เป็นถังเดียว) ตัวตรวจถึงเห็น drift ข้ามก้อนเป็นครั้งแรก · `check_name_forms.py` กรองเหลือ
คู่ที่เป็น **ชื่อเดียวกันสะกดต่างกันจริง** แล้ว lead เคาะทีละคู่ตามลำดับ:
  1) `translations/name_locks.json`  2) กฎใน `scripts/romaji_to_thai.py`  3) รูปข้างมากในคลัง

ใช้:
  python scripts/sweep_name_forms.py --dry-run
  python scripts/sweep_name_forms.py
"""
import argparse
import io
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DONE = ROOT / "translations" / "done"

# (รูปที่ต้องแก้, รูปที่ใช้, เหตุผล)
RULES = [
    # 郎 = -rō สระเสียงยาว **ไม่เติม ะ ท้าย** (glossary §1.9.18 — โทชิโซ · โทโด · อิโต · อิโซ)
    # ⚠ ห้ามแตะ "ชิโระ" — Tashiro 田代 / Oshiro 大城 เป็นสระเสียงสั้น ต้องมี ะ (§1.9.18 ระบุตรง ๆ)
    ("จิโระ", "จิโร", "-jirō/-ichirō (郎) สระยาว ไม่เติม ะ · คลัง 44:26"),
    ("อิจิโระ", "อิจิโร", "-ichirō (一郎) สระยาว ไม่เติม ะ"),
    ("โกโระ", "โกโร", "-gorō (五郎) · คลัง 23:5 · name_locks ใช้ โคโงโร / โกโร"),
    ("ทาโระ", "ทาโร", "-tarō (太郎) สระยาว ไม่เติม ะ"),
    # -tarō: name_locks ใช้ "ทาโร" กับชื่อที่ล็อกแล้ว 4 ชื่อ (ชินทาโร · คาชิทาโร · รินทาโร · ชุนทาโร)
    # และคลังใช้ 69:41 — รูปเดียวกันทั้งเกม (แก้ glossary §9.3 ที่เคยเขียน "-ตาโร" แล้ว)
    ("ตาโร", "ทาโร", "-tarō รูปเดียวทั้งเกม ตาม name_locks + คลัง 69:41"),
    # k กลางคำ = ก (กฎ romaji_to_thai) — ต้นคำยังเป็น ค
    ("ฮิโคอิจิ", "ฮิโกอิจิ", "k กลางคำ = ก (彦一)"),
    ("คาวาคามิ", "คาวากามิ", "k กลางคำ = ก · คลัง 3:2"),
    ("โคมาคิ", "โคมากิ", "k กลางคำ = ก · คลัง 54:1"),
    ("มิคามิ", "มิกามิ", "k กลางคำ = ก · คลัง 2:1"),
    ("โรคุโร", "โรกุโร", "k กลางคำ = ก (六郎)"),
    ("ซาคุเบ", "ซากุเบ", "k กลางคำ = ก (作兵衛)"),
    ("ทาโรคิจิ", "ทาโรกิจิ", "k กลางคำ = ก (太郎吉)"),
    # t กลางคำ = ต
    ("คุราทะ", "คุราตะ", "t กลางคำ = ต (倉田) · คลัง 5:1"),
    # สระสั้นในพยางค์ปิดใส่ ไม้ไต่คู้
    ("เดนโกโร", "เด็นโกโร", "สระสั้นพยางค์ปิด (伝五郎) เข้าชุดกับ เท็ตสึ"),
    ("ไทเกน", "ไทเก็น", "สระสั้นพยางค์ปิด"),
    ("เทตสึ", "เท็ตสึ", "สระสั้นพยางค์ปิด (鉄) · คลัง 6:2"),
    ("เอกซ์", "เอ็กซ์", "รูปไทยของอักษร X"),
    # ความยาวสระ
    ("จุเบ", "จูเบ", "-bei (兵衛) สระยาว · คลัง 4:1"),
    ("ชุเฮ", "ชูเฮ", "Shūhei สระยาว"),
    ("ยูกิมิตสึ", "ยุกิมิตสึ", "幸 yuki สระสั้น"),
    ("บูโย", "บุโย", "舞踊 buyō — bu สระสั้น · คลัง 14:2"),
    ("คิจิเบะ", "คิจิเบ", "-bei (兵衛) สระยาว ไม่เติม ะ เข้าชุดกับ จูเบ · ซากุเบ"),
    # อื่น ๆ
    ("รีจิ", "รีชิ", "chi = ชิ · คลัง 8:1"),
    # ⚠ ข้อยกเว้นของกฎ "k กลางคำ = ก": หน่วยคำ 武/竹 (take-) ล็อกเป็น **ทาเค-** อยู่แล้ว
    #   ทาเคจิ (武市 ฮันเปตะ · name_locks) · ทาเคดะ (竹田 · §1.9.18) → Takei 武井 ต้องเข้าชุด
    ("ทาเกอิ", "ทาเคอิ", "หน่วยคำ 武 take- = ทาเค- เข้าชุดกับ ทาเคจิ · ทาเคดะ"),
    ("โทโยดะ", "โทโยตะ", "豊田 — EN ถอดเป็น Toyota (t) ยึดรูปโรมาจิของเกม"),
    ("มิโฮจัง", "มิโฮะจัง", "Miho 美穂 ล็อกเป็น มิโฮะ ใน name_locks (สระสั้นเติม ะ)"),
]
# รูปที่ห้ามแตะเด็ดขาด (เป็นคำที่ถูกอยู่แล้วและมีซับสตริงชนกับกฎข้างบน)
KEEP = ("ชิโระ", "ทาชิโระ", "โอชิโระ", "ทาเคจิ", "ทาเคดะ")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    total = 0
    per_rule = {}
    for path in sorted(DONE.glob("batch_*.done.json")):
        d = json.load(io.open(path, encoding="utf-8"))
        changed = 0
        for k, val in d["strings"].items():
            if not isinstance(val, str):
                continue
            new = val
            for old, good, _why in RULES:
                if old not in new:
                    continue
                # กันคำใน KEEP ที่มีซับสตริงชนกัน
                hits = new.count(old)
                tmp = new.replace(old, good)
                for keep in KEEP:
                    if keep in val and keep not in tmp:
                        tmp = new          # ยกเลิกการแทนที่รอบนี้
                        hits = 0
                        break
                if hits:
                    per_rule[old] = per_rule.get(old, 0) + hits
                    new = tmp
            if new != val:
                d["strings"][k] = new
                changed += 1
        if changed:
            total += changed
            print("%-32s %3d คีย์" % (path.name, changed))
            if not a.dry_run:
                io.open(path, "w", encoding="utf-8", newline="\n").write(
                    json.dumps(d, ensure_ascii=False, indent=1) + "\n")

    print("\nแยกตามกฎ:")
    for old, good, why in RULES:
        n = per_rule.get(old, 0)
        if n:
            print("   %-12s -> %-12s %3d จุด   (%s)" % (old, good, n, why))
    print("\nรวม %d คีย์%s" % (total, "  (dry-run ไม่ได้เขียนไฟล์)" if a.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
