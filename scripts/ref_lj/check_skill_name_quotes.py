"""ตรวจ/แก้บรรทัดที่อ้างชื่อทักษะเป็นภาษาอังกฤษ ทั้งที่ชื่อทักษะนั้นถูกแปลไทยไปแล้ว

ที่มาของปัญหา: ข้อความแจ้งปลดล็อก ("...has unlocked Re-guard...") มาคนละ bin กับตารางชื่อทักษะ
(`player_skill.bin`) นักแปลจึงคงชื่ออังกฤษไว้ แต่หน้า Skill App ในเกมแสดงชื่อไทย
ผู้เล่นอ่านข้อความแจ้งแล้วหาทักษะในเมนูไม่เจอ

ใช้:
    python scripts/check_skill_name_quotes.py                # ดูอย่างเดียว
    python scripts/check_skill_name_quotes.py --write        # แก้ไฟล์ translations/done/*.done.json
"""
import argparse
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, "translations", "master_th.json")
BY_BIN = os.path.join(ROOT, "extracted", "strings_by_bin.json")
DONE_GLOB = os.path.join(ROOT, "translations", "done", "*.done.json")

THAI = re.compile(r"[฀-๿]")
NAME_OK = re.compile(r"[A-Za-z0-9' \-\.:]+")


def load_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def skill_names():
    """ชื่อทักษะจาก player_skill.bin ที่มีคำแปลไทยอยู่ใน master แล้ว -> {EN: TH}"""
    master = load_json(MASTER)
    by_bin = load_json(BY_BIN)
    out = {}
    for s in by_bin.get("player_skill.bin", []):
        if not isinstance(s, str) or not (1 < len(s) < 40):
            continue
        if not NAME_OK.fullmatch(s):
            continue
        th = master.get(s)
        # ชื่อที่ยังคงอังกฤษทั้งดุ้น (เช่น EX Bond) ไม่ต้องแทนที่
        if th and THAI.search(th):
            out[s] = th
    return out


def scan(write=False):
    names = skill_names()
    pats = [
        (en, th, re.compile(r"(?<![A-Za-z])" + re.escape(en) + r"(?![A-Za-z])", re.IGNORECASE))
        for en, th in sorted(names.items(), key=lambda kv: -len(kv[0]))
    ]
    total = 0
    for path in sorted(glob.glob(DONE_GLOB)):
        data = load_json(path)
        strings = data.get("strings", {})
        changed = 0
        for key, val in list(strings.items()):
            if not THAI.search(val):
                continue
            new = val
            for en, th, pat in pats:
                # ข้ามคีย์ที่ตัวมันเองคือชื่อทักษะ (ตารางชื่อ ไม่ใช่ประโยค)
                if key.strip() == en:
                    continue
                if pat.search(new):
                    new = pat.sub(th, new)
            if new != val:
                total += 1
                changed += 1
                print("--", os.path.basename(path))
                print("   EN :", key.replace("\n", " ")[:100])
                print("   เดิม:", val.replace("\n", " ")[:100])
                print("   ใหม่:", new.replace("\n", " ")[:100])
                strings[key] = new
        if changed and write:
            with io.open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=1)
            print(f"   เขียนแล้ว {changed} จุด -> {os.path.basename(path)}")
    print(f"รวม {total} จุด" + ("" if write else " (ยังไม่แก้ — ใส่ --write)"))
    return total


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    scan(write=args.write)
