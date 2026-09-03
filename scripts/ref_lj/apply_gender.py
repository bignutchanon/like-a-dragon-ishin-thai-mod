#!/usr/bin/env python3
"""ผสมผลพิสูจน์เพศ (`extracted/facts/gender_evidence.json`) เข้าไฟล์ตัวละคร

ทำไมแยกเป็นขั้นตอนของ lead: ทีมพิสูจน์เพศกับทีมสรรพนามทำงานขนานกันคนละไฟล์ (กันชนกัน)
ตัวนี้คือขั้นรวมผล — เขียนฟิลด์ `gender` / `gender_confidence` / `gender_evidence` ลงทุก entry
ที่ match กัน แล้วรายงานตัวที่ยังพิสูจน์ไม่ได้ (นักแปลต้องเลี่ยงสรรพนามกับคนพวกนี้)

กติกา: ผลพิสูจน์เป็นความจริงเสมอ — ถ้าไฟล์ตัวละครเดาเพศไว้ก่อนแล้วขัดกัน ให้ผลพิสูจน์ชนะ
และรายงานความขัดแย้งออกมา

ใช้:  python scripts/apply_gender.py [--write]
"""
import argparse
import collections
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

EVIDENCE = paths.EXTRACTED / "facts" / "gender_evidence.json"
TARGETS = [paths.TRANSLATIONS / "characters_main.json",
           paths.TRANSLATIONS / "characters_side.json"]


def load(p):
    return json.load(io.open(p, encoding="utf-8"), object_pairs_hook=collections.OrderedDict)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    ev = load(EVIDENCE)
    ev.pop("_meta", None)
    unknown, applied, missing, conflicts = [], 0, [], []

    for p in TARGETS:
        data = load(p)
        for key, entry in data.items():
            e = ev.get(key)
            if e is None:
                missing.append("%s:%s" % (p.name, key))
                continue
            old = entry.get("gender")
            if old and old != e["gender"]:
                conflicts.append("%s:%s  %s -> %s" % (p.name, key, old, e["gender"]))
            entry["gender"] = e["gender"]
            entry["gender_confidence"] = e.get("confidence", "?")
            entry["gender_evidence"] = e.get("evidence", [])
            applied += 1
            if e["gender"] == "unknown":
                unknown.append("%s:%s" % (p.name, key))
        if a.write:
            io.open(p, "w", encoding="utf-8", newline="\n").write(
                json.dumps(data, ensure_ascii=False, indent=1) + "\n")

    print("ผสมแล้ว %d entry%s" % (applied, " (เขียนไฟล์แล้ว)" if a.write else " (ยังไม่เขียน — ใส่ --write)"))
    print("ไม่มีผลพิสูจน์ %d: %s" % (len(missing), ", ".join(missing) or "-"))
    print("ขัดแย้งกับค่าที่เดาไว้เดิม %d: %s" % (len(conflicts), " · ".join(conflicts) or "-"))
    print("ยังพิสูจน์ไม่ได้ (ห้ามใช้สรรพนามบอกเพศ) %d:" % len(unknown))
    for u in unknown:
        print("   " + u)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
