"""check_gender_lines.py — ตรวจไฟล์คำตัดสินเพศรายบรรทัดของ lead ก่อนใช้งาน

`translations/gender_lines.json` เป็นชั้นหลักฐานสูงสุดของด่าน G จึงต้องคุมสองอย่าง:

1. **ทุกคีย์ต้องมี `why` ที่อ้างไฟล์/บรรทัดในเกม** — กันการ "เดาแล้วล็อก"
   (`merge_qc.line_gender()` ทิ้งคีย์ที่ไม่มี `why` อยู่แล้ว สคริปต์นี้ทำให้เห็นก่อนว่าตกไปกี่คีย์)

2. **คีย์ต้องเป็นสตริงที่โผล่ในไฟล์ฉากเดียว** — ไฟล์นี้คีย์ด้วย "ข้อความอังกฤษ" ซึ่งสตริงเดียวกัน
   ถูกใช้ซ้ำได้ทั้งเกม การล็อกเพศให้สตริงที่ใช้ร่วมกันจะไปบังคับเพศให้ผู้พูดคนอื่นด้วย
   เจอจริงตอนสร้างไฟล์นี้: `"What?"` โผล่ **57 ครั้ง** ทั่วเกม แต่ถูกล็อกเป็นชายเพราะยามซัตสึมะพูด

   **ข้อยกเว้นเดียว (เพิ่ม 12 ก.ย. 2026 · sprint 21)**: โผล่หลายฉากได้ ถ้า **ต้นฉบับญี่ปุ่นของทุกที่
   ที่มันโผล่เหมือนกันเป๊ะทุกตัวอักษร** — นั่นคือ "บรรทัดเดียวกันที่เกมทำสำเนาฉากไว้หลายชุด"
   ไม่ใช่ "คนละคนพูดประโยคอังกฤษเดียวกัน" · เกมนี้ทำสำเนาฉากย่อยไว้เยอะจริง (ฉากอาบน้ำของฮารุกะ
   มีสามชุด `uid016c00be/c6/c7` · ฉากโรงเรียนวัดมีสามชุด `uid01400014`/`uid016f000b`/`uid0178000a`)
   ถ้าไม่มีข้อยกเว้นนี้ หลักฐานที่ถูกต้องจะถูกตีตกเพราะวิธีที่ *เกม* จัดไฟล์ ไม่ใช่เพราะเนื้อหา
   ⚠ ถ้า `ja` ต่างกันแม้แต่ชุดเดียว = คนละบรรทัด ให้ตกเหมือนเดิม (นั่นคือเคส `"What?"` ที่ทำให้มีด่านนี้)

ใช้: python scripts/check_gender_lines.py
คืนค่า 1 ถ้ามีคีย์ที่ใช้ไม่ได้ (ต้องแก้ก่อนแจกคลื่น)
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import paths

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def main():
    p = paths.TRANSLATIONS / "gender_lines.json"
    if not p.exists():
        print("ยังไม่มี %s (ปกติได้ ถ้า lead ยังไม่เคยล็อกบรรทัดไหน)" % p.name)
        return 0
    data = json.loads(p.read_text(encoding="utf-8"))
    rows = json.loads((paths.EXTRACTED / "parallel" / "msg.json").read_text(encoding="utf-8"))
    files = defaultdict(set)
    jas = defaultdict(set)
    for r in rows:
        if r.get("en"):
            files[r["en"]].add(r["file"])
            jas[r["en"]].add(r.get("ja") or "")

    bad_why, bad_shared, bad_missing, dup_scene, ok = [], [], [], [], 0
    for k, v in data.items():
        if k.startswith("_"):
            continue
        if not isinstance(v, dict) or v.get("gender") not in ("male", "female") or not v.get("why"):
            bad_why.append(k)
            continue
        fs = files.get(k)
        if not fs:
            bad_missing.append(k)          # อาจเป็นสตริงของชั้น locres/ARMP ไม่ใช่ชั้น .msg
            continue
        if len(fs) > 1 and len(jas[k]) > 1:
            bad_shared.append((k, sorted(fs)))
            continue
        if len(fs) > 1:
            dup_scene.append((k, sorted(fs)))
        ok += 1

    print("คีย์ที่ใช้ได้ %d · ขาด why/gender %d · ใช้ร่วมหลายฉาก %d · ฉากสำเนา (ยกเว้นได้) %d"
          " · ไม่พบในชั้น .msg %d"
          % (ok, len(bad_why), len(bad_shared), len(dup_scene), len(bad_missing)))
    for k, fs in dup_scene:
        print("  ~ โผล่ %d ฉากแต่ ja เหมือนกันทุกที่ = ฉากสำเนาของเกม ผ่านตามข้อยกเว้น (%s…): %s"
              % (len(fs), " ".join(fs[:3]), repr(k)[:55]))
    for k in bad_why:
        print("  ✗ ขาด why/gender: %s" % repr(k)[:70])
    for k, fs in bad_shared:
        print("  ✗ สตริงนี้โผล่ %d ฉาก (%s…) — ล็อกแล้วจะบังคับเพศให้ผู้พูดคนอื่นด้วย: %s"
              % (len(fs), " ".join(fs[:3]), repr(k)[:60]))
    for k in bad_missing:
        print("  ⚠ ไม่พบในชั้น .msg (ตรวจเองว่าเป็นสตริงของ locres/ARMP จริงไหม): %s" % repr(k)[:60])
    return 1 if (bad_why or bad_shared) else 0


if __name__ == "__main__":
    sys.exit(main())
