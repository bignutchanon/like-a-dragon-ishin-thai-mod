#!/usr/bin/env python3
"""คลื่นเกลา (§0.61) ถูกสร้างซองก่อนแก้ตารางเพศ (15 ก.ย. 2026) — หาว่าบรรทัดไหนในซองมีเพศเปลี่ยนไปแล้ว

ซอง `work/revise_wave/polish/in/` ฝังช่อง `gender` / `gender_from` / `decide` / `flag` ไว้ตอนสร้าง
หลังเพิ่มชั้นคิวเสียงรายบรรทัดและตัดฉากสองเพศออกจาก scene_gender เพศของบางบรรทัดเปลี่ยน
→ งาน A (คำลงท้าย) ที่ผู้ตรวจเสนอ/ผู้ยืนยันรับไว้บนเพศเดิมอาจผิด ต้องรู้ก่อนสั่ง `--apply`

พิมพ์: จำนวนบรรทัดที่เพศเปลี่ยน (แยกชนิด) · ข้อเสนอ A/D ที่ตกอยู่บนบรรทัดเหล่านั้น พร้อมคำตัดสินผู้ยืนยัน
เขียน: work/revise_wave/polish/gender_drift.json

ใช้: python scripts/audit_polish_gender_drift.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_polish_packets as PP     # noqa: E402  (โหลดตารางเพศล่าสุดตอน import)
import merge_polish_wave as P        # noqa: E402

OUT = P.WAVE / "gender_drift.json"


def main():
    lines, owner = P.load_packets()
    drift = {}
    kinds = Counter()
    for key, l in lines.items():
        old = l.get("gender")
        new, layer = PP.gender_of(key, l["en"], l.get("ja") or "")
        if old == new:
            continue
        kind = "%s->%s" % (old or "none", new or "none")
        kinds[kind] += 1
        drift[key] = {"packet": owner[key], "old": "%s(%s)" % (old, l.get("gender_from")),
                      "new": "%s(%s)" % (new, layer), "en": l["en"], "th": l["th"],
                      "decide": l.get("decide"), "flag": l.get("flag")}

    verdict = {}
    for p in P.VERDICT.glob("packet_*.json"):
        for row in json.loads(p.read_text(encoding="utf-8")):
            verdict[row["key"]] = row.get("decision")
    hits = Counter()
    for p in sorted(P.OUT.glob("packet_*.json")):
        if ".part" in p.name:
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        for task in ("gender_fix", "polish", "gender_wrong"):
            for item in data.get(task) or []:
                k = item.get("key")
                if k in drift:
                    drift[k].setdefault("proposals", []).append(
                        {"task": task, "th_new": item.get("th_new"), "particle": item.get("particle"),
                         "kind": item.get("kind"), "verdict": verdict.get(k)})
                    hits[task] += 1

    OUT.write_text(json.dumps(drift, ensure_ascii=False, indent=1), encoding="utf-8")
    print("บรรทัดในซองที่เพศเปลี่ยน %d: %s" % (len(drift), dict(kinds.most_common())))
    print("ข้อเสนอที่ตกบนบรรทัดเหล่านั้น: %s" % dict(hits))
    for k, d in drift.items():
        for pr in d.get("proposals", []):
            if pr["task"] == "gender_fix":
                print("  A %s %s -> %s · verdict=%s\n    เดิม: %s\n    เสนอ: %s"
                      % (k, d["old"], d["new"], pr["verdict"], d["th"], pr["th_new"]))
    print("-> %s" % OUT)


if __name__ == "__main__":
    main()
