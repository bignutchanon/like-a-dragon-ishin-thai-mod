#!/usr/bin/env python3
"""รวมไฟล์ย่อย b039_p*.json (คีย์ = ดัชนีในลำดับของ worklist) เป็น done/batch_MSG_039.done.json

สร้าง dict โดย **loop ตามลำดับคีย์ของ todo.json** เสมอ — ห้ามพิมพ์คีย์เอง (ด่าน A1)
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODO = os.path.join(ROOT, "translations", "worklist", "batch_MSG_039.todo.json")
OUT = os.path.join(ROOT, "translations", "done", "batch_MSG_039.done.json")
PARTS_DIR = sys.argv[1] if len(sys.argv) > 1 else "."
NOTES_FILE = os.path.join(PARTS_DIR, "b039_notes.json")

parts = {}
for name in ("b039_p1.json", "b039_p2.json", "b039_p3.json"):
    p = os.path.join(PARTS_DIR, name)
    with io.open(p, encoding="utf-8") as f:
        parts.update(json.load(f))

todo = json.load(io.open(TODO, encoding="utf-8"))
keys = list(todo["strings"])

missing = [i for i in range(len(keys)) if str(i) not in parts]
if missing:
    print("!! ขาดคำแปล %d รายการ: %s" % (len(missing), missing[:20]))
    sys.exit(1)
extra = [k for k in parts if not k.isdigit() or int(k) >= len(keys)]
if extra:
    print("!! มีคีย์เกิน: %s" % extra[:20])
    sys.exit(1)

out_strings = {}
for i, en in enumerate(keys):
    out_strings[en] = parts[str(i)]

notes = []
if os.path.exists(NOTES_FILE):
    notes = json.load(io.open(NOTES_FILE, encoding="utf-8"))

data = {"batch": "MSG_039", "strings": out_strings, "notes": notes}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with io.open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("เขียน %s แล้ว · %d คีย์ · notes %d ข้อ" % (OUT, len(out_strings), len(notes)))
