#!/usr/bin/env python3
"""รวมไฟล์ย่อย b074_partN.json (index -> ไทย) เป็น translations/done/batch_MSG_074.done.json

สร้าง dict โดย loop ตามลำดับคีย์ของ `translations/worklist/batch_MSG_074.json` เสมอ
(ก้อนนี้ไม่มีไฟล์ .dnt.json · todo.json มีคีย์เท่าไฟล์เต็ม 250 คีย์)
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = os.environ.get(
    "B074_PARTS",
    r"C:\Users\BigNut\AppData\Local\Temp\claude\d--Projects-like-a-dragon-ishin"
    r"\9340e158-6aa9-4e6e-b6ea-dea8a40498ae\scratchpad")

WORKLIST = os.path.join(ROOT, "translations", "worklist", "batch_MSG_074.json")
OUT = os.path.join(ROOT, "translations", "done", "batch_MSG_074.done.json")

parts = {}
for n in (1, 2, 3):
    p = os.path.join(SCRATCH, "b074_part%d.json" % n)
    with io.open(p, encoding="utf-8") as f:
        parts.update(json.load(f))

with io.open(WORKLIST, encoding="utf-8") as f:
    wl = json.load(f)
keys = list(wl["strings"])

missing = [i for i in range(len(keys)) if str(i) not in parts]
if missing:
    print("!! ขาด index: %s" % missing[:20])
    sys.exit(1)
extra = [k for k in parts if not k.isdigit() or int(k) >= len(keys)]
if extra:
    print("!! index เกิน: %s" % extra[:20])
    sys.exit(1)

strings = {}
for i, k in enumerate(keys):
    strings[k] = parts[str(i)]

with io.open(OUT, "w", encoding="utf-8") as f:
    json.dump({"batch": "MSG_074", "strings": strings}, f, ensure_ascii=False, indent=1)
    f.write("\n")

print("เขียน %s · %d คีย์" % (OUT, len(strings)))
