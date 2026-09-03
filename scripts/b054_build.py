#!/usr/bin/env python3
"""รวมชิ้นคำแปล b054_p*.json ใน scratchpad -> translations/done/batch_MSG_054.done.json

สร้าง dict โดย loop ตามลำดับคีย์ของ translations/worklist/batch_MSG_054.json (ไฟล์เต็ม)
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SCRATCH = (r"C:\Users\BigNut\AppData\Local\Temp\claude"
           r"\d--Projects-like-a-dragon-ishin"
           r"\a683aa70-45f7-4ef1-a743-932e17ecf9cf\scratchpad")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

parts = {}
for i in (1, 2, 3, 4):
    p = os.path.join(SCRATCH, "b054_p%d.json" % i)
    with io.open(p, encoding="utf-8") as f:
        parts.update(json.load(f))

full_path = os.path.join(ROOT, "translations", "worklist", "batch_MSG_054.json")
with io.open(full_path, encoding="utf-8") as f:
    full = json.load(f)
keys = list(full["strings"])

missing = [i for i in range(len(keys)) if str(i) not in parts]
if missing:
    print("!! ขาดคำแปล index: %s" % missing)
    sys.exit(1)
extra = [k for k in parts if not k.isdigit() or int(k) >= len(keys)]
if extra:
    print("!! index เกิน: %s" % extra)
    sys.exit(1)

out = {}
for i, k in enumerate(keys):
    out[k] = parts[str(i)]

notes = [
    "Kanda ยังไม่มีในคำล็อก — ใช้ 'คันดะ' ตาม master_th.json (Kanda-sensei = ท่านอาจารย์คันดะ) ขอ lead ลงล็อก",
    "'Uncle Saito' (JA おじさん จากปากฮารุกะ) = 'ลุงไซโต' ตามแบบเดียวกับคำล็อก Uncle Hajime = ลุงฮาจิเมะ",
    "爺さん ที่เรียวมะเรียกคันดะ/ตาเฒ่าคู่ผัวเมีย = 'ตาเฒ่า' ตามรูปที่ master ใช้อยู่แล้ว (ไม่ใช้ 'คุณตา')",
    "'As you know,' ในบรีฟล็อกไว้ว่า 'ตามที่ทุกท่านทราบ' — บรรทัด 'As you know, I had a son...' "
    "เป็นบทคุยตัวต่อตัวของคันดะ (JA さっきの連中が言っておった通り) จึงเขียนเป็น 'อย่างที่พวกเมื่อกี้พูดไว้นั่นแหละ' "
    "รูปล็อกเป็นคำแปลของสตริงคนละตัวในบริบทประกาศ — ขอ lead ยืนยัน",
    "'Essence of' ในบรรทัด <i>essence of truth and beauty</i> ใช้รูป 'แก่นแท้แห่ง…' ตามคำล็อก Essence of X",
    "singing bar = 'ร้านเหล้าเสียงเพลง' ตามรูปที่ master ship แล้ว",
]

done_path = os.path.join(ROOT, "translations", "done", "batch_MSG_054.done.json")
with io.open(done_path, "w", encoding="utf-8") as f:
    json.dump({"batch": "MSG_054", "strings": out, "notes": notes},
              f, ensure_ascii=False, indent=1)
print("เขียน %s (%d คีย์)" % (done_path, len(out)))
