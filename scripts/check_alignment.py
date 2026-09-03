#!/usr/bin/env python3
"""ด่าน A — จับ "คำแปลจับคู่ผิดคีย์" (misalignment) ใน `translations/done/*.done.json`

ทำไมต้องมี (26 ส.ค. 2026 · ช่องโหว่ที่บันทึกไว้ใน HANDOFF §29.8 ข้อ 3):
sprint 15 นักแปล b124 เขียนสคริปต์ช่วยกรอกคำแปลของตัวเอง แล้วสคริปต์ **ทำคีย์หล่นไปหนึ่งคีย์**
(`Whiteboard Phone Number`) ผลคือคำแปลตั้งแต่ลำดับที่ 50 เป็นต้นไป **เลื่อนไปทั้งแถว** —
ทุกบรรทัดยังเป็นภาษาไทยที่ถูกต้องสวยงาม แต่ไปอยู่ผิดคีย์ทั้งหมด
เขาจับได้เองแล้วแก้เอง แต่ **ด่านทั้ง 7 ของ `merge_qc.py` มองไม่เห็น** เพราะทุกด่านตรวจ "คู่ต่อคู่"
ไม่มีด่านไหนถามว่า "คู่นี้เป็นคู่ที่ถูกต้องจริงไหม"

## วิธีตรวจ
ใช้สองสัญญาณที่ไม่ต้องรู้ภาษาไทยเลย และวัดทั้ง batch พร้อมกัน:
  1. **สหสัมพันธ์ความยาว** — คำแปลไทยยาวตามต้นฉบับอย่างเป็นระบบ
     วัดกับไฟล์จริงทั้ง 130 ไฟล์แล้ว: อยู่ในช่วง **0.902 - 0.994** และ
     **ไม่มีไฟล์ไหนเลยที่ "จับคู่แบบเลื่อน" ได้คะแนนดีกว่าจับคู่ตามลำดับจริง** (ดีสุดคือ -0.162)
     ไฟล์เลื่อนจำลองของ b124: ตรงลำดับ 0.507 · เลื่อน +1 = 0.900
  2. **สหสัมพันธ์จำนวนขึ้นบรรทัด** — ไฟล์ที่ผ่านด่าน N แล้วจะได้ 1.000 เป๊ะเสมอ

เกณฑ์ตก (ตั้งจากค่าที่วัดจริง ไม่ได้เดา):
  - สหสัมพันธ์ความยาวของ "จับคู่ตามลำดับจริง" < 0.85  (ต่ำกว่าไฟล์จริงที่แย่ที่สุด 0.902)
  - หรือมีการเลื่อน ±1..3 ที่ได้คะแนนดีกว่าตรงลำดับเกิน 0.05
  - หรือมีหน้าต่าง 30 คีย์ตั้งแต่ **สองหน้าต่างขึ้นไป** ที่การเลื่อนชนะเกิน 0.05 (จับกรณีเลื่อนแค่ท้ายไฟล์)
    ⚠ ระดับหน้าต่างใช้ได้เฉพาะเกณฑ์ "การเลื่อนชนะ" — ห้ามใช้ "corr ต่ำ" เป็นเกณฑ์ของหน้าต่าง
      (ลองแล้วกล่าวหาไฟล์ที่ถูกต้องผิด 8 ไฟล์จาก 130)

⚠ ด่านนี้ตอบได้แค่ "คู่นี้เข้ากันไหม" **ไม่ได้ตอบว่าแปลถูกความหมายไหม** — นั่นยังเป็นงานคน
⚠ batch ที่คีย์ยาวใกล้กันหมด (ส่วนเบี่ยงเบนความยาว < 8) = หลักฐานอ่อน → รายงานว่า "หลักฐานไม่พอ"
   แทนที่จะเดา (ไฟล์จริงที่ต่ำสุดคือ batch_001 sd=14.3 ยังห่างจากเกณฑ์นี้พอสมควร)

ใช้:
  python scripts/check_alignment.py                 # ตรวจไฟล์ done ทั้งหมด
  python scripts/check_alignment.py --only 124      # เฉพาะ batch เดียว
  python scripts/check_alignment.py --verbose       # แสดงคะแนนทุกไฟล์แม้ผ่าน
  python scripts/check_alignment.py --self-test     # พิสูจน์ตัวตรวจด้วยเคสเลื่อนจำลอง
`merge_qc.py` เรียกด่านนี้ให้อัตโนมัติต่อ batch — ไม่ต้องรันมือทุกครั้ง
"""
import argparse
import io
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

sys.stdout.reconfigure(encoding="utf-8")

DONE = os.path.join(str(paths.TRANSLATIONS), "done")

SHIFTS = (-3, -2, -1, 1, 2, 3)
MIN_CORR = 0.85      # ต่ำกว่านี้ = น่าสงสัย (ไฟล์จริงแย่สุด 0.902)
SHIFT_WINS = 0.05    # การเลื่อนดีกว่าตรงลำดับเกินเท่านี้ = ตก (ไฟล์จริงดีสุด -0.162)
# ⚠ เพิ่ม 2 ก.ย. 2026 (ISHTH คลื่น 042–067): ก้อนที่เป็น "บทพูดสั้นล้วน" ของภาคนี้ได้ corr
# 0.76–0.83 ทั้งที่คีย์ตรงทุกตัว (lead ไล่ตรวจด้วยมือหกก้อน) เพราะความยาวคีย์แทบไม่กระจาย
# เกณฑ์ corr ต่ำเดี่ยว ๆ จึงกล่าวหาผิดทั้งชั้น — ใช้ต่อเมื่อ **การเลื่อนไม่ได้แย่กว่ามาก** ด้วย
# ถ้าเลื่อนแล้วแย่ลงเกินค่านี้ แปลว่าลำดับปัจจุบันคือลำดับที่ดีที่สุดจริง = ไม่ได้เลื่อน
SHIFT_LOSES_BADLY = -0.25
MIN_PAIRS = 25       # คู่ที่ใช้วัดได้ขั้นต่ำ
MIN_SD = 8.0         # ส่วนเบี่ยงเบนความยาว EN ขั้นต่ำ ไม่งั้นหลักฐานอ่อน
WINDOW = 30          # ขนาดหน้าต่างสำหรับหาว่าเลื่อนตั้งแต่ตรงไหน


def _corr(a, b):
    n = len(a)
    if n < 3:
        return 0.0
    ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((x - mb) ** 2 for x in b))
    if sa == 0 or sb == 0:
        return 0.0
    return sum((a[i] - ma) * (b[i] - mb) for i in range(n)) / (sa * sb)


def _sd(a):
    n = len(a)
    if n < 2:
        return 0.0
    m = sum(a) / n
    return math.sqrt(sum((x - m) ** 2 for x in a) / n)


def _series(keys, vals, shift, lo=0, hi=None):
    """คืน (ความยาว EN, ความยาว TH, ขึ้นบรรทัด EN, ขึ้นบรรทัด TH) ของคู่ที่ใช้วัดได้

    ข้ามคู่ที่ TH == EN (คงต้นฉบับ) เพราะการเลื่อนก็ได้คะแนนเท่ากัน = ไม่ใช่หลักฐาน
    """
    hi = len(keys) if hi is None else min(hi, len(keys))
    le, lt, ne, nt = [], [], [], []
    for i in range(lo, hi):
        j = i + shift
        if not (0 <= j < len(vals)):
            continue
        k, v = keys[i], vals[j]
        if not isinstance(v, str) or not v.strip() or v == k:
            continue
        le.append(len(k))
        lt.append(len(v))
        ne.append(k.count("\n"))
        nt.append(v.count("\n"))
    return le, lt, ne, nt


def _judge(keys, vals, lo=0, hi=None):
    """คืน dict ผลการวัดช่วงหนึ่ง · None ถ้าหลักฐานไม่พอ"""
    le, lt, ne, nt = _series(keys, vals, 0, lo, hi)
    if len(le) < MIN_PAIRS or _sd(le) < MIN_SD:
        return None
    base = _corr(le, lt)
    base_nl = _corr(ne, nt)
    best_sh, best = None, -2.0
    for sh in SHIFTS:
        a, b, _, _ = _series(keys, vals, sh, lo, hi)
        if len(a) < max(10, MIN_PAIRS // 2):
            continue
        c = _corr(a, b)
        if c > best:
            best, best_sh = c, sh
    return {"n": len(le), "sd": _sd(le), "corr": base, "corr_nl": base_nl,
            "best_shift": best_sh, "best": best, "diff": best - base}


def _locate(keys, vals):
    """หาว่าความเพี้ยนเริ่มราวลำดับไหน — เลื่อนหน้าต่างไปทีละครึ่งหน้าต่าง"""
    bad = []
    step = max(1, WINDOW // 2)
    for lo in range(0, max(1, len(keys) - WINDOW + 1), step):
        r = _judge(keys, vals, lo, lo + WINDOW)
        # ⚠ เกณฑ์ของหน้าต่างต้องเป็น "มีการเลื่อนที่ชนะ" เท่านั้น
        # ห้ามใช้ "corr ต่ำ" เป็นเกณฑ์ในระดับหน้าต่าง — วัดกับไฟล์จริง 130 ไฟล์แล้วพบว่า
        # หน้าต่าง 30 คีย์มีเสียงรบกวนสูงมาก (กล่าวหาผิด 8 ไฟล์) ทั้งที่ทั้งไฟล์ปกติดี
        if r and r["diff"] > SHIFT_WINS:
            bad.append((lo, r))
    return bad


def check_file(path, verbose=False):
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    st = d["strings"] if isinstance(d, dict) and "strings" in d else d
    keys = list(st)
    vals = [st[k] for k in keys]
    name = os.path.basename(path)

    r = _judge(keys, vals)
    if r is None:
        if verbose:
            print("  %-26s หลักฐานไม่พอ (คู่ที่วัดได้น้อย หรือคีย์ยาวใกล้กันหมด) — ข้าม" % name)
        return None

    global_bad = r["diff"] > SHIFT_WINS or (r["corr"] < MIN_CORR
                                            and r["diff"] > SHIFT_LOSES_BADLY)
    windows = _locate(keys, vals)
    # หน้าต่างเดียวโดด ๆ = เสียงรบกวน · ต้องติดกันอย่างน้อยสองหน้าต่างถึงจะเชื่อ
    win_bad = len(windows) >= 2

    if not global_bad and not win_bad:
        if verbose:
            print("  %-26s ok  corr=%.3f (เลื่อนดีสุด %+d = %.3f) n=%d"
                  % (name, r["corr"], r["best_shift"] or 0, r["best"], r["n"]))
        return None

    print("!! %s  **น่าจะจับคู่ผิดคีย์**" % name)
    print("     สหสัมพันธ์ความยาว ตรงลำดับ = %.3f   (ไฟล์ปกติอยู่ที่ 0.90-0.99)" % r["corr"])
    print("     สหสัมพันธ์ขึ้นบรรทัด ตรงลำดับ = %.3f  (ไฟล์ปกติได้ 1.000)" % r["corr_nl"])
    print("     จับคู่แบบเลื่อน %+d ได้ %.3f  (ต่าง %+.3f)" % (r["best_shift"] or 0, r["best"], r["diff"]))
    if windows:
        lo0 = windows[0][0]
        print("     ช่วงที่เพี้ยน %d หน้าต่าง · เริ่มราวลำดับที่ %d" % (len(windows), lo0))
        print("       คีย์แรกของช่วงนั้น: %s" % keys[lo0].replace("\n", "|")[:70])
    print("     -> เปิดไฟล์เทียบลำดับคีย์กับ translations/worklist/%s"
          % name.replace(".done.json", ".json"))
    return {"file": name, "corr": r["corr"], "shift": r["best_shift"],
            "diff": r["diff"], "at": windows[0][0] if windows else None}


def _selftest_pairs():
    """คืน (keys, vals) ที่ใช้พิสูจน์ตัวตรวจ พร้อมป้ายบอกว่าเป็นข้อมูลจริงหรือสังเคราะห์

    ภาคนี้ยังไม่มีไฟล์ `done` ตอนพอร์ตด่านนี้เข้ามา (2 ก.ย. 2026) จึงต้องมีทางสำรอง:
    ถ้ามีไฟล์ done จริงให้ใช้ไฟล์ใหญ่สุด ถ้าไม่มีก็สร้างคู่สังเคราะห์จาก `worklist/batch_001.json`
    โดยทำคำแปลปลอมที่ **ยาวตามต้นฉบับ** และมีจำนวนขึ้นบรรทัดเท่ากัน
    ข้อมูลสังเคราะห์พิสูจน์ได้แค่ "คณิตศาสตร์ของตัวตรวจทำงานถูก" ไม่ได้พิสูจน์คุณภาพคำแปลใด ๆ
    """
    files = sorted(f for f in os.listdir(DONE) if f.endswith(".done.json")) if os.path.isdir(DONE) else []
    if files:
        best = max(files, key=lambda f: os.path.getsize(os.path.join(DONE, f)))
        with io.open(os.path.join(DONE, best), encoding="utf-8") as fh:
            d = json.load(fh)
        st = d["strings"] if isinstance(d, dict) and "strings" in d else d
        keys = list(st)
        return keys, [st[k] for k in keys], "ไฟล์จริง %s" % best

    src = os.path.join(str(paths.WORKLIST), "batch_001.json")
    if not os.path.exists(src):
        return None, None, None
    with io.open(src, encoding="utf-8") as fh:
        keys = list(json.load(fh)["strings"])
    vals = []
    for k in keys:
        # คำแปลปลอม: ยาว ~1.25 เท่าของต้นฉบับ · ขึ้นบรรทัดเท่ากัน (ให้ด่านวัดได้เหมือนไฟล์จริง)
        parts = k.split("\n")
        vals.append("\n".join("ก" * max(1, int(len(p) * 1.25)) for p in parts))
    return keys, vals, "ข้อมูลสังเคราะห์จาก worklist/batch_001.json (ยังไม่มีไฟล์ done)"


def self_test():
    keys, vals, label = _selftest_pairs()
    if keys is None:
        print("ไม่มีทั้งไฟล์ done และ worklist/batch_001.json — ข้าม self-test")
        return 0
    print("แหล่งข้อมูล:", label)
    if len(keys) < 120:
        print("คู่น้อยเกินกว่าจะจำลองการเลื่อนได้ (%d คู่) — ข้าม self-test" % len(keys))
        return 0

    print("\n== 1) ชุดที่จับคู่ถูก (ต้องผ่าน) ==")
    r = _judge(keys, vals)
    if r is None:
        print("   หลักฐานไม่พอ (คีย์ยาวใกล้กันหมด) — ข้าม")
        return 0
    print("   corr=%.3f · เลื่อนดีสุด %+d = %.3f (ต่าง %+.3f)"
          % (r["corr"], r["best_shift"], r["best"], r["diff"]))
    ok1 = r["corr"] >= MIN_CORR and r["diff"] <= SHIFT_WINS and len(_locate(keys, vals)) < 2
    print("   ผล:", "ผ่าน" if ok1 else "!! ตรวจผิด — ชุดที่ถูกต้องถูกกล่าวหา")

    print("\n== 2) จำลองเคส b124 ของ LJ — ทำคีย์หล่นที่ลำดับ 50 (คำแปลที่เหลือเลื่อนหมด) ==")
    bk = keys[:50] + keys[51:]
    bv = vals[:50] + vals[50:-1]
    r2 = _judge(bk, bv)
    w2 = _locate(bk, bv)
    print("   corr=%.3f · เลื่อนดีสุด %+d = %.3f (ต่าง %+.3f) · หน้าต่างเพี้ยน %d"
          % (r2["corr"], r2["best_shift"], r2["best"], r2["diff"], len(w2)))
    ok2 = r2["corr"] < MIN_CORR or r2["diff"] > SHIFT_WINS or len(w2) >= 2
    print("   ผล:", "จับได้" if ok2 else "!! จับไม่ได้")

    print("\n== 3) เคสยากกว่า — เลื่อนแค่ช่วงท้ายไฟล์ ==")
    at = max(60, len(keys) - 40)
    bk3 = keys[:at] + keys[at + 1:]
    bv3 = vals[:at] + vals[at:-1]
    r3 = _judge(bk3, bv3)
    w3 = _locate(bk3, bv3)
    print("   corr=%.3f · เลื่อนดีสุด %+d = %.3f · หน้าต่างเพี้ยน %d"
          % (r3["corr"], r3["best_shift"], r3["best"], len(w3)))
    ok3 = r3["corr"] < MIN_CORR or r3["diff"] > SHIFT_WINS or len(w3) >= 2
    print("   ผล:", "จับได้" if ok3 else "จับไม่ได้ (ข้อจำกัดที่ยอมรับ — เลื่อนน้อยเกินกว่าจะเห็นทางสถิติ)")
    return 0 if (ok1 and ok2) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="เลขที่ batch เช่น 124 หรือชื่อไฟล์")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        sys.exit(self_test())

    files = sorted(f for f in os.listdir(DONE) if f.endswith(".done.json"))
    if a.only:
        want = a.only if a.only.endswith(".json") else "batch_%s.done.json" % a.only.zfill(3)
        files = [f for f in files if f == want]
        if not files:
            print("ไม่พบไฟล์:", want)
            sys.exit(2)

    bad = [r for r in (check_file(os.path.join(DONE, f), a.verbose) for f in files) if r]
    print("\nตรวจ %d ไฟล์ · น่าจะจับคู่ผิดคีย์ %d ไฟล์" % (len(files), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
