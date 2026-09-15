#!/usr/bin/env python3
"""ฉบับอ่านให้ lead ตัดสินเพศของสตริงที่ "มีคำลงท้ายบอกเพศแต่ไม่มีหลักฐาน" (audit_gender_endings.py ชั้น no_evidence)

แต่ละสตริง: คำแปลไทย + ทุกที่ที่มันโผล่ พร้อมบริบท ±4 บรรทัดในไฟล์ฉาก (voice · JA · EN)
และคำตัดสินของผู้ตรวจคลื่นสาม (ถ้ามี) ที่ยังไม่ผ่านด่านเข้ม — ให้ lead อ่านแล้วเลือก:
  รับ -> ใส่คีย์ลง work/gender_wave3/lead_accept.json (ถ้าผู้ตรวจอ้างหลักฐานถูก) หรือ translations/gender_lines.json
  ไม่รับ -> คำแปลต้องเขียนกลางเพศ

ใช้: python scripts/dump_gender_review.py   -> work/gender_fix/review_no_evidence.md
"""
import glob
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

OUT = paths.PROJECT / "work" / "gender_fix" / "review_no_evidence.md"
CTX = 4


def one(s, n=90):
    return (s or "").replace("\r\n", " / ").replace("\n", " / ")[:n]


def main():
    conflicts = json.loads((paths.PROJECT / "work" / "gender_fix" / "conflicts.json").read_text(encoding="utf-8"))
    rows = json.loads((paths.EXTRACTED / "parallel" / "msg.json").read_text(encoding="utf-8"))
    by_key = {r["key"]: r for r in rows}
    wave3 = {}
    for p in glob.glob(str(paths.PROJECT / "work" / "gender_wave3" / "out" / "packet_*.json")):
        if ".part" in p:
            continue
        for item in json.loads(Path(p).read_text(encoding="utf-8")).get("lines", []):
            wave3[item["key"]] = item

    out = ["# สตริงที่มีคำลงท้ายบอกเพศแต่ไม่มีหลักฐาน — lead อ่าน", ""]
    for n, it in enumerate(conflicts.get("no_evidence", []), 1):
        out.append("## %d. %s" % (n, one(it["en"], 140)))
        out.append("TH: %s" % one(it["th"], 200))
        for occ in it["occurrences"]:
            key = occ["key"]
            if "#" not in key or key not in by_key:
                out.append("- (นอก .msg) %s ป้าย %s" % (key, occ.get("labels")))
                continue
            f, i = key.split("#")
            i = int(i)
            w = wave3.get(key)
            if w:
                ev = w.get("evidence") or {}
                out.append("- **%s** ผู้ตรวจคลื่นสาม: %s อ้าง %s `%s` — %s"
                           % (key, w.get("gender"), ev.get("src"), one(ev.get("quote"), 60), w.get("why", "")))
            else:
                out.append("- **%s** ผู้ตรวจคลื่นสามไม่ได้ตัดสิน" % key)
            for j in range(i - CTX, i + CTX + 1):
                k = "%s#%03d" % (f, j)
                r = by_key.get(k)
                if not r or not (r.get("en") or r.get("ja")):
                    continue
                mark = ">>" if j == i else "  "
                out.append("    %s %s voice=%s | JA: %s | EN: %s"
                           % (mark, k, r.get("voice") or "", one(r.get("ja"), 60), one(r.get("en"), 80)))
        out.append("")
    OUT.write_text("\n".join(out), encoding="utf-8")
    print("%d สตริง -> %s" % (len(conflicts.get("no_evidence", [])), OUT))


if __name__ == "__main__":
    main()
