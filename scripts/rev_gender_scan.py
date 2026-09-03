"""ผู้ตรวจ: หาบรรทัดที่ใส่คำลงท้าย/คำแทนตัวผูกเพศ แต่ไม่มีหลักฐานในบรรทัดของตัวเอง"""
import sys, json, re

sys.path.insert(0, "scripts")
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

import merge_qc as M
from rev_query import rows

MALE_TH = re.compile(r"ขอรับ|กระผม")
FEM_TH = re.compile(r"เจ้าค่ะ|เจ้าคะ|จ๊ะ|จ้ะ|ดิฉัน|อิฉัน")

for b in sys.argv[1:] or ["MSG_055", "MSG_056", "MSG_057"]:
    print("=" * 20, b)
    n = 0
    for r in rows(b):
        th, ja, en = r["th"], r["ja"], r["en"]
        mk = []
        if MALE_TH.search(th):
            mk.append("male")
        if FEM_TH.search(th):
            mk.append("female")
        if not mk:
            continue
        own = M.ja_gender(ja)
        lg = M.line_gender(en)
        sg = M.scene_gender(en)
        c = r["ctx"] or {}
        ev = c.get("evidence_gender") or {}
        ok = (own in mk) or (lg in mk)
        if ok:
            continue
        n += 1
        print(f"--- #{r['i']:03d} th_marks={mk} ja_gender={own} line_gender={lg} "
              f"scene={sg} ctx_gender={c.get('gender')} neutral={c.get('neutral')} "
              f"ev_from={ev.get('from')} ev_gender={ev.get('gender')}")
        print("  EN:", en.replace("\n", "\\n")[:220])
        print("  JA:", (ja or "").replace("\n", "\\n")[:220])
        print("  TH:", th.replace("\n", "\\n")[:220])
    print(f"[{b}] ต้องสอบเพิ่ม {n} บรรทัด")
