#!/usr/bin/env python3
"""เพิ่มคิวแปล label ตัวเลือกตอบที่มีตัวเลขปน (15 ก.ย. 2026) — batch_LABEL_003

ตัวคัด label เดิม (`build_text.LABEL_KEY_RE`) ตีทุก label ที่มีตัวเลขเป็นคีย์เอนจิ้น จึงไม่เคยเข้าคิวแปล
กวาด label ทั้ง 1,678 ไฟล์ .msg แล้วเหลือข้อความบนจอจริง 16 คำ (ที่เหลือเป็น 15,0,0,0 · ACDEV7020 · ENC1 ฯลฯ)
คำแปลอิงคำที่คลังใช้อยู่แล้ว: tags = ป้ายไม้ (I need tags.) · ryo = เรียว · mon = มอน · points = แต้ม ·
Low/High = ต่ำ/สูง (โป๊กเกอร์) · label JA ของแต่ละไฟล์ใช้ยืนยันความหมาย:
  uid000c0d8a 10 ryo showdown = １０両勝負をする · uid000c14bf = １０００文やってみる ·
  uid00330051 = １０万００００点分 · uid00330455 = 低掛け率（５点／１０点） ·
  uid0033092b/uid006e0056/uid016e0057 = ５０００文で ５０点に交換 · uid016c00b1 Country 1 = １の国
("Regarding the Incident on the 18th" มีคำแปลใน master อยู่แล้ว ไม่ต้องเพิ่ม)

ใช้: python scripts/add_digit_labels.py [--write]  แล้วต่อด้วย python scripts/merge_qc.py
"""
import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

BATCH = "batch_LABEL_003"
STRINGS = {
    "10 ryo showdown": "ประลองเดิมพัน 10 เรียว",
    "Give the cat 1,000 mon": "ให้เงินแมว 1,000 มอน",
    "100,000 Points": "100,000 แต้ม",
    "25,000 Points": "25,000 แต้ม",
    "10,000 Points": "10,000 แต้ม",
    "Low (5/10 points)": "ต่ำ (5/10 แต้ม)",
    "High (50/100 points)": "สูง (50/100 แต้ม)",
    "Buy 50 tags for 5,000 mon": "ซื้อป้ายไม้ 50 ป้าย ด้วย 5,000 มอน",
    "Buy 50 tags for 5000 mon": "ซื้อป้ายไม้ 50 ป้าย ด้วย 5000 มอน",
    "Buy 100 tags for 1 ryo": "ซื้อป้ายไม้ 100 ป้าย ด้วย 1 เรียว",
    "Buy 1000 tags for 10 ryo": "ซื้อป้ายไม้ 1000 ป้าย ด้วย 10 เรียว",
    "Country 1": "ประเทศที่ 1",
    "Country 2": "ประเทศที่ 2",
    "Country 3": "ประเทศที่ 3",
    "Country 4": "ประเทศที่ 4",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    master = json.loads(paths.MASTER_TH.read_text(encoding="utf-8"))
    clash = [k for k in STRINGS if k in master]
    if clash:
        raise SystemExit("มีคำแปลใน master อยู่แล้ว ห้ามซ้ำ batch: %s" % clash)
    ref_wl = json.loads((paths.TRANSLATIONS / "worklist" / "batch_LABEL_002.json").read_text(encoding="utf-8"))
    ref_dn = json.loads((paths.TRANSLATIONS / "done" / "batch_LABEL_002.done.json").read_text(encoding="utf-8"))
    wl = {k: v for k, v in ref_wl.items() if k not in ("strings", "ref_ja", "ref_tm")}
    wl["priority_name"] = "label ของ .msg รอบสาม (ตัวเลือกตอบที่มีตัวเลขปน)"
    wl["strings"] = {k: "" for k in STRINGS}
    wl["ref_ja"], wl["ref_tm"] = {}, {}
    dn = {k: v for k, v in ref_dn.items() if k != "strings"}
    if isinstance(dn.get("batch"), str):
        dn["batch"] = dn["batch"].replace("LABEL_002", "LABEL_003").replace("002", "003")
    dn["strings"] = dict(STRINGS)
    for k, v in STRINGS.items():
        print("%-28s -> %s" % (k, v))
    if args.write:
        (paths.TRANSLATIONS / "worklist" / (BATCH + ".json")).write_text(
            json.dumps(wl, ensure_ascii=False, indent=1), encoding="utf-8")
        (paths.TRANSLATIONS / "done" / (BATCH + ".done.json")).write_text(
            json.dumps(dn, ensure_ascii=False, indent=1), encoding="utf-8")
        print("เขียน %s (worklist + done) %d คำ" % (BATCH, len(STRINGS)))


if __name__ == "__main__":
    main()
