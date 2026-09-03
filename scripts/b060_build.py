#!/usr/bin/env python3
"""ประกอบไฟล์ done ของก้อน MSG_060 จากไฟล์ย่อยใน scratchpad

สร้าง dict โดย **loop ตามลำดับคีย์ของ worklist** (`batch_MSG_060.json`) เสมอ — ห้ามพิมพ์คีย์เอง
ไฟล์ย่อยเก็บเป็น {"<ดัชนีในลำดับ worklist>": "<คำแปลไทย>"} เพื่อไม่ให้พิมพ์คีย์ EN ผิด
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = (r"C:\Users\BigNut\AppData\Local\Temp\claude"
           r"\d--Projects-like-a-dragon-ishin"
           r"\9340e158-6aa9-4e6e-b6ea-dea8a40498ae\scratchpad")

WORKLIST = os.path.join(ROOT, "translations", "worklist", "batch_MSG_060.json")
OUT = os.path.join(ROOT, "translations", "done", "batch_MSG_060.done.json")

keys = list(json.load(io.open(WORKLIST, encoding="utf-8"))["strings"])

parts = {}
for n in range(1, 6):
    p = os.path.join(SCRATCH, "b060_p%d.json" % n)
    for k, v in json.load(io.open(p, encoding="utf-8")).items():
        i = int(k)
        if i in parts:
            raise SystemExit("ดัชนีซ้ำ: %d" % i)
        parts[i] = v

missing = [i for i in range(len(keys)) if i not in parts]
if missing:
    raise SystemExit("ขาดคำแปลที่ดัชนี: %s" % missing)
extra = [i for i in parts if i >= len(keys)]
if extra:
    raise SystemExit("ดัชนีเกินขอบเขต: %s" % extra)

strings = {}
for i, k in enumerate(keys):
    strings[k] = parts[i]

data = {"batch": "MSG_060", "strings": strings}
with io.open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
    f.write("\n")

print("เขียน %s (%d คีย์)" % (OUT, len(strings)))
print("ลำดับคีย์ตรงกับ worklist:", list(strings) == keys)
