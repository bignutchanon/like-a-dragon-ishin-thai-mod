#!/usr/bin/env python3
"""ตรวจ `ref_tm` ของ worklist ด้วยเครื่อง — แทนการให้ผู้ตรวจไล่ทีละคีย์

ทำไมต้องมี (26 ส.ค. 2026 · sprint 15):
กับดัก `ref_tm` ที่ยืนยันแล้วใน sprint 14 (§5.2) คือ **ref_tm หยิบคำของภาคที่ลำดับต่ำกว่า
มาแทนคำของภาคที่สูงกว่า** — เป็นงานที่คนต้องนั่งไล่ทีละคีย์ ทั้งที่เครื่องเทียบได้ตรง ๆ
พอรันจริงกับ sprint 15 (batch 119-130 · ref_tm 1,366 คีย์) พบว่า **ขัดแค่ 1 จุด**
(`Mapo Tofu`: ref_tm ให้ "หม่าโผเต้าหู้" แต่ Y8 ship "เต้าหู้หม่าโผ")
→ เวลาที่ผู้ตรวจ 12 คนจะเสียไปกับงานนี้ ย้ายไปทำกองที่ไม่มีตัวช่วยได้แทน

ด่านที่สอง (เพิ่มวันเดียวกัน · ผู้ตรวจ b121 จับได้ว่าด่านแรกมองไม่เห็น): **`master_th.json` ของ LJ เอง
อยู่ลำดับสูงกว่าภาคพี่น้อง** แต่คีย์ของ worklist แทบไม่เคยตรงกับคีย์ของ master ตรง ๆ (วัดแล้ว 0/3,000)
เพราะคำพวกนี้อยู่ **ข้างในประโยค** → ใช้ `batch_NNN.priorart.json` เทียบแทน
จับได้จริง 3 จุดที่ด่านแรกปล่อยผ่าน: `Earth Angel` (ref_tm คง EN ทั้งที่ glossary ล็อก "เอิร์ธแองเจิล") ·
`M Side Cafe` (ref_tm คง EN ทั้งที่ LJ ship "เอ็ม ไซด์ คาเฟ่") · `Batting Center` (ref_tm "ศูนย์ฝึกตี"
ทั้งที่ LJ ship "สนามตีลูก")

⚠ **ด่านที่สองมีเสียงรบกวนสูง (~ครึ่งหนึ่งเป็นคำพ้องรูป)** — `Toast` ที่แปลว่าขนมปังปิ้งไปชนกับ
"ชนแก้ว" ในบทพูด เป็นต้น · **เป็นลิสต์ให้คนไล่ดู ไม่ใช่คำตัดสิน** ตัวเลขที่รายงานคือ "จุดที่ควรเปิดดู"

⚠ **เครื่องตอบได้แค่ "ตรงกับภาคที่ลำดับสูงกว่าไหม"** — ตอบไม่ได้ว่า ref_tm แปลถูกความหมายไหม
หรือเข้าชุดกับคีย์อื่นใน batch เดียวกันไหม สองข้อนั้นยังเป็นงานคน

ลำดับ (ตาม CLAUDE.md): master_th ของ LJ > Judgment > K3 > Gaiden > Y8 > Y7 > Pirate > K2R

ใช้:
  python scripts/check_ref_tm.py 119 130      # ช่วง batch
  python scripts/check_ref_tm.py 127 127
  python scripts/check_ref_tm.py 119 130 --fresh   # แสดงจำนวนคีย์ที่ไม่มีตัวช่วยเลยด้วย
"""
import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

sys.stdout.reconfigure(encoding="utf-8")

WL = os.path.join(paths.PROJECT, "translations", "worklist")
# ⚠ รายชื่อโฟลเดอร์ภาคพี่น้องอยู่ที่ `paths.SIBLINGS` ที่เดียว (รวมมา 26 ส.ค. 2026 · sprint 16)
# เดิมสคริปต์นี้เดาชื่อโฟลเดอร์เองแล้วโหลดไม่ขึ้น 3 ภาคแบบเงียบ ๆ จนรายงานว่า "ขัด 0 จุด"
# ทั้งที่ไม่เคยเทียบเลย — ตอนนี้ `paths.sibling_paths()` จะเตือนดัง ๆ ถ้าโฟลเดอร์ไหนหาย

def load_siblings():
    out = []
    for name, master, _gloss in paths.sibling_paths():
        with io.open(master, encoding="utf-8") as f:
            out.append((name, json.load(f)))
    return out


def batch_range(first, last):
    """คืนรายชื่อ id ของ batch ตั้งแต่ first ถึง last (เลขล้วน หรือ TALK_NNN)

    เพิ่ม 28 ส.ค. 2026 · sprint 22 — เดิมรับเฉพาะ int จึงใช้กับคิว TALK ไม่ได้
    ⚠ ตัวเดียวกับใน `make_prior_art.py` — แก้ที่หนึ่งต้องแก้อีกที่
    """
    f, l = str(first).upper(), str(last).upper()
    pre = ""
    if f.startswith("TALK_") or l.startswith("TALK_"):
        if not (f.startswith("TALK_") and l.startswith("TALK_")):
            raise SystemExit("first/last ต้องเป็นชนิดเดียวกัน (เลขล้วน หรือ TALK_NNN ทั้งคู่)")
        pre, f, l = "TALK_", f[5:], l[5:]
    return ["%s%03d" % (pre, i) for i in range(int(f), int(l) + 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("first", help="เลข batch หรือ TALK_NNN")
    ap.add_argument("last", help="เลข batch หรือ TALK_NNN")
    ap.add_argument("--fresh", action="store_true",
                    help="นับคีย์ที่ไม่มี ref_tm และไม่มีในภาคพี่น้องเลย (= คิดคำใหม่ล้วน)")
    a = ap.parse_args()

    sibs = load_siblings()
    print("ภาคพี่น้องที่โหลดได้: " + " > ".join(n for n, _ in sibs))
    total_ref = total_bad = total_fresh = total_keys = total_pa = 0

    for n in batch_range(a.first, a.last):
        src = os.path.join(WL, "batch_%s.json" % n)
        if not os.path.exists(src):
            continue
        with io.open(src, encoding="utf-8") as f:
            batch = json.load(f)
        ref = batch.get("ref_tm", {})
        keys = list(batch["strings"])
        bad = []
        for k, tm in ref.items():
            for name, M in sibs:
                if k in M:
                    if M[k] != tm:
                        bad.append((k, name, M[k], tm))
                    break
        # ⚠ ด่านที่สอง (เพิ่ม 26 ส.ค. 2026 · sprint 15 — ผู้ตรวจ b121 จับได้ว่ารูปแรกมองไม่เห็น):
        # ภาคพี่น้องไม่ใช่ลำดับสูงสุด — **`master_th.json` ของ LJ เองสูงกว่า** แต่คีย์ของ worklist
        # แทบไม่เคยตรงกับคีย์ของ master ตรง ๆ (วัดแล้ว 0/3,000) เพราะคำพวกนี้อยู่ **ข้างในประโยค**
        # → ใช้ `batch_NNN.priorart.json` เป็นตัวแทน: ถ้าคำไทยของ ref_tm **ไม่โผล่เลย**
        #   ในคำแปลที่ ship ไปแล้วของประโยคที่มีคำนี้ = สัญญาณว่า ref_tm ใช้คำที่ LJ ไม่ได้ใช้
        # ตัวอย่างจริงที่รูปแรกปล่อยผ่าน: `Earth Angel` · `M Side Cafe` · `Batting Center`
        pa_path = os.path.join(WL, "batch_%s.priorart.json" % n)
        pa_bad = []
        if os.path.exists(pa_path):
            with io.open(pa_path, encoding="utf-8") as f:
                pa = json.load(f)
            for k, hits in pa.items():
                tm = ref.get(k)
                if not tm:
                    continue
                if not any(tm in h["th"] for h in hits):
                    pa_bad.append((k, tm, hits[0]["th"]))

        fresh = [k for k in keys if k not in ref and not any(k in M for _, M in sibs)]
        total_ref += len(ref)
        total_bad += len(bad)
        total_pa += len(pa_bad)
        total_fresh += len(fresh)
        total_keys += len(keys)

        line = ("batch_%s  ref_tm %4d  ขัดกับภาคลำดับสูงสุด %d  ·  ไม่ตรงกับที่ LJ ship เอง %d"
                % (n, len(ref), len(bad), len(pa_bad)))
        if a.fresh:
            line += "  ·  ไม่มีตัวช่วยเลย %3d/%d" % (len(fresh), len(keys))
        print(line)
        for k, name, win, tm in bad:
            print("    คีย์: %s" % k)
            print("      %s ship: %s" % (name, win))
            print("      ref_tm  : %s" % tm)
        for k, tm, th in pa_bad:
            print("    [LJ] คีย์: %s" % k)
            print("      ref_tm      : %s" % tm)
            print("      LJ ship อยู่ใน: %s" % th.replace(chr(10), "|")[:70])

    print("\nรวม: ref_tm %d คีย์ · ขัดภาคพี่น้อง %d จุด · ควรเปิดดู (เทียบที่ LJ ship เอง) %d จุด"
          % (total_ref, total_bad, total_pa), end="")
    if a.fresh:
        print(" · ไม่มีตัวช่วยเลย %d/%d คีย์" % (total_fresh, total_keys), end="")
    print()


if __name__ == "__main__":
    main()
