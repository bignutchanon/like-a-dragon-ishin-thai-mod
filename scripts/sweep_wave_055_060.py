"""กวาดรูปที่ชนกันจากคลื่น MSG_055–060 (sprint 15)

ทุกข้อในไฟล์นี้ **วัดทั้งคลังก่อนตัดสิน** ไม่ได้ยึดตามก้อนที่รายงานมา
(บทเรียน sprint 14 §5: lead รับตัวเลขจากรายงานมาใช้ตัดสินโดยไม่นับซ้ำ แล้วผิดสองครั้ง)

⚠ ไม่แตะ `batch_MSG_057.done.json` — ก้อนนั้นยังแปลไม่เสร็จตอนเขียนสคริปต์นี้

รันแล้วต้องตามด้วย: merge_qc.py --only <ก้อนที่แก้>
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DONE = Path("translations/done")

BOND_OLD_MOMOKAWA = (
    "ท่านได้สร้างสายสัมพันธ์กับพี่น้องตระกูลโมโมกาวะแล้ว ท่านสามารถกระชับสายสัมพันธ์ให้แน่นแฟ้น"
    "ยิ่งขึ้นได้ด้วยการพูดคุยกับพวกเขาต่อไปเพื่อเติมเกจสายสัมพันธ์ให้เต็ม นอกจากนี้ยังตรวจสอบสถานะ"
    "ของเกจได้ที่ใบประกาศความพากเพียรในเมนูหยุดเกม พยายามแวะไปเยี่ยมพวกเขาบ่อย ๆ นะ"
)
BOND_NEW_MOMOKAWA = (
    "เจ้าได้ก่อร่างสายสัมพันธ์กับพี่น้องตระกูลโมโมกาวะแล้ว สานสัมพันธ์ให้แน่นแฟ้นขึ้นได้ด้วยการ"
    "พูดคุยกับพวกเขาต่อไปเรื่อย ๆ จนเติมเกจสายสัมพันธ์เต็ม ตรวจดูสถานะของเกจได้ที่ใบประกาศ"
    "ความพากเพียรในเมนูหยุดเกม พยายามไปเยี่ยมเยียนพวกเขาบ่อย ๆ นะ"
)
BOND_OLD_CAT = (
    "ท่านได้สร้างสายสัมพันธ์กับแมวนำโชคแล้ว ท่านสามารถกระชับสายสัมพันธ์ให้แน่นแฟ้น"
    "ยิ่งขึ้นได้ด้วยการพูดคุยกับมันต่อไปเพื่อเติมเกจสายสัมพันธ์ให้เต็ม นอกจากนี้ยังตรวจสอบสถานะ"
    "ของเกจได้ที่ใบประกาศความพากเพียรในเมนูหยุดเกม พยายามแวะไปเยี่ยมมันบ่อย ๆ นะ"
)
BOND_NEW_CAT = (
    "เจ้าได้ก่อร่างสายสัมพันธ์กับแมวนำโชคแล้ว สานสัมพันธ์ให้แน่นแฟ้นขึ้นได้ด้วยการ"
    "พูดคุยกับมันต่อไปเรื่อย ๆ จนเติมเกจสายสัมพันธ์เต็ม ตรวจดูสถานะของเกจได้ที่ใบประกาศ"
    "ความพากเพียรในเมนูหยุดเกม พยายามไปเยี่ยมเยียนมันบ่อย ๆ นะ"
)

# (ไฟล์ก้อน, คีย์ EN หรือ None = ทุกคีย์ในก้อนที่มีข้อความเดิม, เดิม, ใหม่)
FIXES = [
    # --- ก. お頭 / 御頭 (คำที่ลูกน้องใช้เรียกหัวหน้าโจร) = "หัวหน้า" เปล่า ---
    # วัดก้อนอื่นทั้งคลัง (ไม่นับ 058/059): หัวหน้า 12 : ท่านหัวหน้า 0
    # และ 12 คีย์นั้นรวมรูปเรียกตรง ๆ ด้วย (「お、お頭!?」= "หะ-หัวหน้า!?" · 「お頭。」= "หัวหน้า")
    # -> MSG_058 เป็นฝ่ายผิดรูป ไม่ใช่ MSG_059 แม้ MSG_058 จะเป็นเจ้าของฉากตามกติกาเลขน้อยกว่า
    ("batch_MSG_058.done.json", None, "ท่านหัวหน้า", "หัวหน้า"),

    # --- ข. 依頼書 (ใบงานที่ติดบนป้าย) = "ใบคำขอ" ---
    # ในคลังมีสามรูปพร้อมกัน: ใบคำขอ (MSG_057 · 8) · ใบร้องขอ (MSG_058 · 7) · ใบประกาศงาน (MSG_059 · 1)
    # เลือก "ใบคำขอ" เพราะ (1) เป็นรูปข้างมาก (2) เข้าชุดกับ batch_054 ที่แปล 依頼書 ว่า "คำขอ"
    # (3) ไม่ชนกับ 依頼掲示板 = "ป้ายประกาศงาน" ที่อยู่ใน master แล้ว
    ("batch_MSG_058.done.json", None, "ใบร้องขอ", "ใบคำขอ"),
    ("batch_MSG_059.done.json", None, "ใบประกาศงาน", "ใบคำขอ"),

    # --- ค. Lucky Cat = "แมวนำโชค" (13 : 2) ---
    ("batch_012.done.json", None, "แมวกวัก", "แมวนำโชค"),

    # --- ง. เทมเพลต "You have formed a bond with X" ---
    # รูปข้างมาก 38 คีย์ใช้ "เจ้าได้ก่อร่างสายสัมพันธ์… สานสัมพันธ์ให้แน่นแฟ้นขึ้น…"
    # MSG_015 สองคีย์ใช้ "ท่านได้สร้าง… กระชับสายสัมพันธ์…" (สรรพนามก็ต่าง: ท่าน vs เจ้า)
    ("batch_MSG_015.done.json", None, BOND_OLD_MOMOKAWA, BOND_NEW_MOMOKAWA),
    ("batch_MSG_015.done.json", None, BOND_OLD_CAT, BOND_NEW_CAT),
]


def apply_fix(strings, en_key, old, new):
    """คืนจำนวนคีย์ที่แก้ · -1 = กวาดไปแล้วในรอบก่อน · -2 = ไม่พบทั้งรูปเก่าและรูปใหม่"""
    if en_key is not None and en_key not in strings:
        return -2
    keys = [
        k for k, v in strings.items()
        if v and old in v and (en_key is None or k == en_key)
    ]
    if keys:
        for k in keys:
            strings[k] = strings[k].replace(old, new)
        return len(keys)
    already = any(
        v and new in v and (en_key is None or k == en_key) for k, v in strings.items()
    )
    return -1 if already else -2


def main() -> int:
    cache = {}
    total = 0
    problems = 0
    for fname, en_key, old, new in FIXES:
        path = DONE / fname
        if not path.exists():
            print(f"[ผิด] ไม่พบไฟล์ {fname}")
            problems += 1
            continue
        if fname not in cache:
            cache[fname] = json.loads(path.read_text(encoding="utf-8"))
        n = apply_fix(cache[fname]["strings"], en_key, old, new)
        label = fname[len("batch_"):-len(".done.json")]
        if n > 0:
            total += n
            print(f"{label:>9} · {n} คีย์ · {old[:28]!r} -> {new[:28]!r}")
        elif n == -1:
            print(f"{label:>9} · [กวาดแล้ว] {new[:34]!r}")
        else:
            print(f"[ผิด] {fname}: ไม่พบ {old[:34]!r}")
            problems += 1

    for fname, data in cache.items():
        (DONE / fname).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(f"\nแก้ {total} คีย์ · {len(cache)} ไฟล์ · รายการที่มีปัญหา {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
