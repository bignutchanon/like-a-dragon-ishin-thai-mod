#!/usr/bin/env python3
"""ตัดข้อเสนอคลื่นเกลาที่เปลี่ยน "ท่าน…" เป็น "…ซัง/คุง" ออก (คำเคาะผู้ใช้ 15 ก.ย. 2026)

ผู้ใช้เคาะ: ต้นฉบับ -san ที่ทีมแปลเป็น "ท่าน…" ไว้ **คงไว้** เพราะอ่านง่าย
→ ข้อเสนอในคลื่นเกลา (§0.61) ที่ถอด ท่าน แล้วใส่ ซัง/คุง แทน ต้องไม่ลง done

เกณฑ์ (ต่อข้อเสนอหนึ่งรายการในงาน D/A/B): คำแปลเดิมมี "ท่าน" มากกว่าฉบับเสนอ
และฉบับเสนอมี ซัง/คุง มากกว่าคำแปลเดิม → เขียนคีย์ลง `lead_drop.json` พร้อมเหตุผล
(ไม่ทับเหตุผลเดิมของคีย์ที่ lead ตัดไว้แล้ว)

ใช้:
  python scripts/drop_san_proposals.py          # พิมพ์รายการ ไม่เขียน
  python scripts/drop_san_proposals.py --write  # เขียนลง lead_drop.json
"""
import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import merge_polish_wave as P     # noqa: E402

REASON = "ผู้ใช้เคาะ 15 ก.ย. 2026: -san คงเป็น ท่าน… (อ่านง่าย) ไม่เปลี่ยนเป็น ซัง/คุง"


def honorific_swap(th_old, th_new):
    return (th_old.count("ท่าน") > th_new.count("ท่าน")
            and th_new.count("ซัง") + th_new.count("คุง") > th_old.count("ซัง") + th_old.count("คุง"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    lines, _ = P.load_packets()
    hits = {}
    for p in sorted(P.OUT.glob("packet_*.json")):
        if ".part" in p.name:
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            print("!! อ่านไม่ได้ %s: %s" % (p.name, e))
            continue
        for task in ("polish", "gender_fix", "weird"):
            for item in data.get(task) or []:
                key, th_new = item.get("key"), item.get("th_new")
                line = lines.get(key)
                if not line or not isinstance(th_new, str):
                    continue
                if honorific_swap(line["th"], th_new):
                    hits[key] = (p.stem, task, line["en"], line["th"], th_new)

    for key, (pk, task, en, th, th_new) in sorted(hits.items()):
        print("%s %s %s\n  EN: %s\n  เดิม: %s\n  เสนอ: %s" % (pk, task, key, en, th, th_new))
    print("\nรวม %d คีย์" % len(hits))

    if args.write:
        drop = json.loads(P.LEAD_DROP.read_text(encoding="utf-8")) if P.LEAD_DROP.exists() else {}
        added = 0
        for key in hits:
            if key not in drop:
                drop[key] = REASON
                added += 1
        P.LEAD_DROP.write_text(json.dumps(drop, ensure_ascii=False, indent=1), encoding="utf-8")
        print("เขียน lead_drop.json เพิ่ม %d คีย์ (รวม %d)" % (added, len(drop)))


if __name__ == "__main__":
    main()
