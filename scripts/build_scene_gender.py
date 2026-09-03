"""build_scene_gender.py — เพศผู้พูด "ระดับไฟล์ฉาก" ของชั้น .msg

ที่มาของปัญหา: ชั้น `.msg` รู้ป้ายผู้พูดแค่ 13% ไฟล์บริบทจึงตี `neutral: true` เกือบทั้งหมด
ด่าน G ยอมให้ใช้คำลงท้ายบอกเพศได้เฉพาะเมื่อ **บรรทัดนั้นเอง** มีเครื่องหมายในต้นฉบับญี่ปุ่น
ผลคือตัวละครเดียวกันได้คำลงท้ายบ้างไม่ได้บ้างสลับกันในฉากเดียว (เจอจริงในก้อน MSG_012)

วิธีแก้: บทสนทนาหนึ่งไฟล์ `.msg` = หนึ่งฉาก ถ้าทั้งไฟล์มีเครื่องหมายเพศเดียวล้วน
(ไม่มีของอีกเพศปนเลย) และมีมากพอ ก็ถือว่าฉากนั้นเป็นเพศนั้น

**ตัวเลขที่วัดได้จริง** (เทียบกับบรรทัดที่รู้ป้ายผู้พูดแน่นอน 4,476 บรรทัด):

| เกณฑ์ขั้นต่ำ | ไฟล์ที่ชี้ได้ | ชาย ตรง | หญิง ตรง |
|---|---:|---:|---:|
| ≥1 เครื่องหมาย | 408 | 97.4% | 100% |
| ≥2 | 253 | 97.8% | 100% |
| **≥3 (ที่ใช้จริง)** | **185** | **99.2%** | **100%** |

ที่พลาดคือไฟล์ที่มีทั้งเรียวมะ (ชาย) และ NPC หญิงอยู่ด้วยกัน แล้วมีแต่เครื่องหมายฝั่งชาย
เกณฑ์ ≥3 ตัดเคสพวกนั้นออกเกือบหมด

เขียนออก: translations/scene_gender.json  (สตริงอังกฤษ -> "male"/"female")
รันใหม่เมื่อ extracted/parallel/msg.json เปลี่ยน
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import paths
from merge_qc import ja_gender

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

MIN_MARKERS = 3
OUT = paths.TRANSLATIONS / "scene_gender.json"

# บรรทัดที่เป็นข้อความในเครื่องหมายคำพูดล้วน = เสียงของ "คนอื่น" ที่ถูกยกมาอ่าน
# (จดหมายของโอคินุใน uid000c1432 เป็นเสียงหญิง แต่ถูกอ่านอยู่ในฉากของฟูจิเอะซึ่งเป็นชาย)
# `ja_gender()` ตัด 「」『』 ออกก่อนตรวจอยู่แล้ว — ระดับฉากต้องไม่ยัดเพศของฉากทับบรรทัดพวกนี้
QUOTED_WHOLE = re.compile(r"^\s*[『「][\s\S]*[』」]\s*$")


def main():
    rows = json.loads((paths.EXTRACTED / "parallel" / "msg.json").read_text(encoding="utf-8"))

    per_file = defaultdict(Counter)
    for r in rows:
        g = ja_gender(r.get("ja") or "")
        if g:
            per_file[r["file"]][g] += 1

    scene = {}
    for f, c in per_file.items():
        if c["male"] >= MIN_MARKERS and not c["female"]:
            scene[f] = "male"
        elif c["female"] >= MIN_MARKERS and not c["male"]:
            scene[f] = "female"

    # สตริงหนึ่งอาจโผล่หลายไฟล์ — ต้องตรงกันทุกไฟล์ ไม่งั้นไม่นับ
    by_key = defaultdict(set)
    quoted = set()
    for r in rows:
        g = scene.get(r["file"])
        by_key[r["en"]].add(g)          # None ถ้าไฟล์นั้นชี้ไม่ได้ -> ทำให้เซตไม่บริสุทธิ์
        if QUOTED_WHOLE.match(r.get("ja") or ""):
            quoted.add(r["en"])
    out = {k: next(iter(v)) for k, v in by_key.items()
           if len(v) == 1 and next(iter(v)) is not None and k not in quoted}

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    n_m = sum(1 for v in out.values() if v == "male")
    print("ไฟล์ฉากที่ชี้เพศได้ %d/%d (เกณฑ์ >= %d เครื่องหมาย)"
          % (len(scene), len(per_file), MIN_MARKERS))
    print("สตริงที่ได้เพศจากฉาก %d (ชาย %d · หญิง %d) -> %s"
          % (len(out), n_m, len(out) - n_m, OUT))


if __name__ == "__main__":
    main()
