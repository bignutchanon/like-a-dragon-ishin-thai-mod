#!/usr/bin/env python3
"""ตรวจผลเพศผู้พูดที่ผู้ตรวจ (subagent) ส่งกลับ แล้วรวมเป็น translations/gender_dialogue.json

**ไม่เชื่อคำตัดสินใด ๆ ที่ตรวจซ้ำด้วยเครื่องไม่ได้** (กติกา CLAUDE.md "ห้ามเดา")
ทุกรายการต้องมี `evidence` = {"src": คีย์บรรทัด, "quote": ข้อความที่ยกมา} และด่านนี้เช็กว่า
  1. คีย์บรรทัดที่ตัดสิน และคีย์ที่อ้างเป็นหลักฐาน อยู่ใน "ไฟล์ฉากเดียวกัน" จริง
  2. `quote` เป็นสตริงย่อยของช่อง ja / en / labels ของบรรทัดที่อ้างจริง (เทียบตรงตัว)
  3. gender เป็น male/female เท่านั้น · quote ยาว 1 ตัวได้ถ้าเป็นคันจิ/คานะ (俺 · 僕 · 儂)
รายการที่ตกข้อใดข้อหนึ่ง = ทิ้ง พร้อมรายงานเหตุผล

**สองมาตรวัดที่พิมพ์ออกมา**
- `ja_gender` = เครื่องหมายเพศในบรรทัดนั้นเอง (ตรรกะเดียวกับ merge_qc) — บรรทัดที่มีเครื่องหมาย
  อยู่แล้วเป็น "ข้อสอบที่รู้คำตอบ" ใช้วัดผู้ตรวจได้ทุกซอง ไม่ใช่เฉพาะซองควบคุม
- `scene_gender` = เพศระดับไฟล์ฉาก (build_scene_gender.py) — ตีทั้งฉากเป็นเพศเดียว
  บรรทัดของตัวละครอีกเพศในฉากเดียวกันจึงขัดกันได้ **โดยที่ผู้ตรวจเป็นฝ่ายถูก**
  ต้องอ่านรายการที่ขัดกันทีละอันก่อนสรุป ห้ามดูแต่เปอร์เซ็นต์

ยุบจาก "รายบรรทัด" เป็น "ต่อสตริงอังกฤษ" (คีย์ที่ merge_qc ใช้) ตอนเขียนไฟล์:
สตริงเดียวกันที่ถูกตัดสินคนละเพศในคนละฉาก = ทิ้งทั้งคู่ (กำกวม แปลกลางเพศปลอดภัยกว่า)

ใช้:
  python scripts/merge_gender_wave.py --check     # ตรวจอย่างเดียว
  python scripts/merge_gender_wave.py             # ตรวจ + เขียน translations/gender_dialogue.json
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402
from merge_qc import ja_gender  # noqa: E402

WAVE = paths.PROJECT / "work" / "gender_wave"
OUT_FILE = paths.TRANSLATIONS / "gender_dialogue.json"
CJK_RE = re.compile("[぀-ヿ㐀-鿿]")

# รูปที่โปรเจกต์วัดแล้วว่า **ไม่บอกเพศ** ในเกมนี้ (merge_qc.py บรรทัด 136-137 · วัดกับผู้พูดที่รู้เพศ 6,382 บรรทัด)
#   ですわ / ますわ = สำเนียงคันไซ ชาย 25 : หญิง 6 (เรียวมะพูดเอง) · わ ท้ายประโยคเดี่ยว ๆ ชาย 83 : หญิง 41
# ผู้ตรวจที่ยกรูปพวกนี้ "เดี่ยว ๆ" มาเป็นหลักฐาน = หลักฐานใช้ไม่ได้ ต้องไปหาคำอื่นในฉากมาอ้างแทน
WEAK_QUOTES = {"ですわ", "ますわ", "わ", "ぜよ", "おます", "でおます", "どす", "やねん", "ですやろ"}


def load_index():
    """คีย์บรรทัด -> (ไฟล์ฉาก, en, ja, labels)"""
    par = json.loads((paths.PROJECT / "extracted" / "parallel" / "msg.json").read_text(encoding="utf-8"))
    return {r["key"]: (r["file"], r.get("en") or "", r.get("ja") or "", r.get("labels") or [])
            for r in par}


def verify(rows, idx, report):
    """คืนรายการที่ผ่านด่าน — rows = [{"key","gender","evidence":{"src","quote"}}]"""
    ok = []
    for row in rows:
        key = row.get("key")
        gender = row.get("gender")
        ev = row.get("evidence") or {}
        src = ev.get("src")
        quote = (ev.get("quote") or "").strip()
        if gender not in ("male", "female"):
            report["เพศไม่ถูกรูปแบบ"] += 1
            continue
        if key not in idx or src not in idx:
            report["คีย์บรรทัดไม่มีจริง"] += 1
            continue
        if idx[key][0] != idx[src][0]:
            report["หลักฐานอยู่คนละไฟล์ฉาก"] += 1
            continue
        if not quote or (len(quote) == 1 and not CJK_RE.match(quote)):
            report["quote สั้นเกินไป"] += 1
            continue
        if quote in WEAK_QUOTES:
            report["quote เป็นรูปที่วัดแล้วว่าไม่บอกเพศ (สำเนียงคันไซ)"] += 1
            continue
        _, en, ja, labels = idx[src]
        if quote not in ja and quote not in en and not any(quote in lab for lab in labels):
            report["quote ไม่มีอยู่จริงในบรรทัดที่อ้าง"] += 1
            continue
        ok.append((key, gender, src, quote))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    idx = load_index()
    scene = json.loads((paths.TRANSLATIONS / "scene_gender.json").read_text(encoding="utf-8"))
    out_dir = WAVE / "out"
    files = sorted(out_dir.glob("*.json")) if out_dir.exists() else []
    if not files:
        print("ไม่พบผลลัพธ์ใน %s" % out_dir)
        return 1

    report = defaultdict(int)
    passed, control_rows = [], []
    for p in files:
        data = json.loads(p.read_text(encoding="utf-8"))
        rows = data["lines"] if isinstance(data, dict) and "lines" in data else data
        good = verify(rows, idx, report)
        print("%-22s ส่งมา %5d · ผ่านด่าน %5d" % (p.name, len(rows), len(good)))
        (control_rows if p.name.startswith("control") else passed).extend(good)

    if report:
        print("\nที่ทิ้ง:")
        for k, v in sorted(report.items(), key=lambda x: -x[1]):
            print("  %-36s %d" % (k, v))

    # --- มาตรวัดที่ 1: เครื่องหมายในบรรทัดนั้นเอง (รู้คำตอบแน่) ---
    gsame = gdiff = 0
    gbad = []
    for key, gender, src, quote in passed + control_rows:
        want = ja_gender(idx[key][2])
        if want is None:
            continue
        if want == gender:
            gsame += 1
        else:
            gdiff += 1
            gbad.append((key, gender, want, src, quote))
    if gsame + gdiff:
        tot = gsame + gdiff
        print("\nเทียบเครื่องหมายในบรรทัดเอง (ja_gender): ตรง %d/%d = %.1f%%"
              % (gsame, tot, gsame / tot * 100))
        for key, got, want, src, quote in gbad[:12]:
            print("   ขัดกัน %s: ผู้ตรวจว่า %s · บรรทัดเองบอก %s (อ้าง %s: %s)"
                  % (key, got, want, src, quote))

    # --- มาตรวัดที่ 2: เพศระดับไฟล์ฉาก (หยาบกว่า ดูประกอบเท่านั้น) ---
    if control_rows:
        same = diff = 0
        bad = []
        for key, gender, src, quote in control_rows:
            want = scene.get(idx[key][1])
            if want is None:
                continue
            if want == gender:
                same += 1
            else:
                diff += 1
                bad.append((key, gender, want, src, quote))
        tot = same + diff
        if tot:
            print("\nซองควบคุม เทียบ scene_gender: ตรง %d/%d = %.1f%%" % (same, tot, same / tot * 100))
            print("  (scene_gender ตีทั้งไฟล์เป็นเพศเดียว — บรรทัดของตัวละครอีกเพศในฉากเดียวกัน")
            print("   ขัดกันได้โดยผู้ตรวจถูก ต้องอ่านทีละอัน)")
            for key, got, want, src, quote in bad[:12]:
                print("   ขัดกัน %s: ผู้ตรวจว่า %s · scene_gender ว่า %s (อ้าง %s: %s)"
                      % (key, got, want, src, quote))

    # --- ยุบเป็นต่อสตริงอังกฤษ ---
    by_en = defaultdict(set)
    why = {}
    for key, gender, src, quote in passed:
        en = idx[key][1]
        by_en[en].add(gender)
        why.setdefault(en, (gender, src, quote))
    final, dropped = {}, 0
    for en, genders in by_en.items():
        if len(genders) != 1:
            dropped += 1
            continue
        g, src, quote = why[en]
        final[en] = {"gender": g, "why": "ผู้ตรวจอ่าน EN คู่ JA · หลักฐาน %s: %s" % (src, quote)}
    print("\nคำตัดสินรายบรรทัดที่ผ่าน %d · สตริงอังกฤษที่ได้ %d · ทิ้งเพราะขัดกันเอง %d"
          % (len(passed), len(final), dropped))
    already = sum(1 for en in final if en in scene)
    print("ในนั้นซ้ำกับ scene_gender เดิม %d · เพิ่มของใหม่ %d" % (already, len(final) - already))

    if not args.check:
        OUT_FILE.write_text(json.dumps(final, ensure_ascii=False, indent=1), encoding="utf-8")
        print("เขียน %s" % OUT_FILE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
