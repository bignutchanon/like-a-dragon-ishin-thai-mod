#!/usr/bin/env python3
"""วัด "ความหนาแน่นของคำลงท้าย ครับ/ค่ะ" รายตัวละคร — ตัวตรวจกลางของกฎข้อ 11

ทำไมต้องมี (26 ส.ค. 2026): กฎข้อ 11 ใน `docs/reference/SPRINT_TASKS.md` บอกว่าความหนาแน่นของ
คำลงท้ายต้องสม่ำเสมอทั้งไฟล์ — ไม่ใช่ต้นไฟล์ 16% ท้ายไฟล์ 93% (รอยต่อของการแบ่งงานเป็นก้อน)
แต่ที่ผ่านมา **นักแปลกับผู้ตรวจต่างคนต่างเขียนสคริปต์วัดเอง** แล้วได้ตัวเลขคนละชุด
(คนหนึ่งนับเฉพาะท้ายบรรทัด อีกคนนับทุกตำแหน่ง · คนหนึ่งรวมมอนอโลก อีกคนไม่รวม)
จนเถียงกันไม่จบว่าตัวเลขไหนจริง — ผู้ตรวจ batch_049 ขอให้ทำตัวกลาง

**นิยามที่ใช้ (ตกลงเป็นมาตรฐานเดียวของโปรเจกต์)**
- นับ "บรรทัดที่มีคำลงท้าย" = บรรทัดที่มี ครับ/คร้าบ/ค่ะ/คะ ที่ตำแหน่งใดก็ได้
  (ภาษาไทยวางคำสุภาพกลางประโยคได้ เช่น "ใช่ครับ แต่ว่า...")
- **ไม่นับ** บรรทัดมอนอโลก (`<color=monologue>`) เพราะกฎข้อ 11 บอกว่ามอนอโลกไม่ใส่คำลงท้ายอยู่แล้ว
- **ไม่นับ** บรรทัดที่ติดธง `neutral` เพราะห้ามใส่คำลงท้ายอยู่แล้ว
- **ไม่นับ** ตัวละคร T2/T3 (ทะเบียนที่ห้ามใช้ ครับ/ค่ะ) — รายงานแยกว่า "ต้องเป็น 0%"
- แบ่งไฟล์ตามลำดับคีย์เป็น N ส่วนเท่า ๆ กัน (ค่าตั้งต้น 2 = ครึ่งไฟล์)

ใช้:
  python scripts/check_particle_density.py --only 049
  python scripts/check_particle_density.py --only 049 --parts 4
  python scripts/check_particle_density.py --done          # ทุกไฟล์ใน translations/done/
"""
import argparse
import collections
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

PARTICLE_RE = re.compile(r"ครับ|คร้าบ|ค่ะ|คะ(?![ก-ฮเแโใไ])(?<!คะยอ)")
MONOLOGUE_RE = re.compile(r"<color=monologue>", re.I)

# ตัวละครที่ทะเบียนห้ามใช้ ครับ/ค่ะ — ความหนาแน่นต้องเป็น 0% เสมอ
NO_PARTICLE_TIERS = {"T2", "T3"}

# เตือนเมื่อส่วนใดต่างจากส่วนที่สูงสุดเกินกี่จุด (จากเคสจริง: batch_035 ต่าง 77 จุด · batch_033 ต่าง 41)
GAP_WARN = 25


def load_tiers():
    """คืน {ชื่อผู้พูด (ตัวเล็ก): tier} จาก characters_*.json"""
    out = {}
    for name in ("characters_main.json", "characters_side.json"):
        p = paths.TRANSLATIONS / name
        if not p.exists():
            continue
        for k, v in json.load(io.open(p, encoding="utf-8")).items():
            t = (v.get("tier") or "").strip()
            out[k.lower()] = t
            for n in v.get("names_in_game", []) or []:
                out[str(n).lower()] = t
    return out


def analyse(batch, parts):
    ctx_p = paths.WORKLIST / ("batch_%s.context.json" % batch)
    done_p = paths.TRANSLATIONS / "done" / ("batch_%s.done.json" % batch)
    src_p = paths.WORKLIST / ("batch_%s.json" % batch)
    if not (done_p.exists() and src_p.exists()):
        return None
    ctx = json.load(io.open(ctx_p, encoding="utf-8")) if ctx_p.exists() else {}
    done = json.load(io.open(done_p, encoding="utf-8"))["strings"]
    keys = list(json.load(io.open(src_p, encoding="utf-8"))["strings"])

    tiers = load_tiers()
    # {speaker: [ (part_index, มีคำลงท้ายไหม) ]}
    per = collections.defaultdict(list)
    n = max(len(keys), 1)
    for i, k in enumerate(keys):
        rec = ctx.get(k) or {}
        th = done.get(k, "")
        spk = (rec.get("speaker") or "").strip()
        if not spk or rec.get("neutral") or MONOLOGUE_RE.search(k) or MONOLOGUE_RE.search(th):
            continue
        part = min(i * parts // n, parts - 1)
        per[spk].append((part, bool(PARTICLE_RE.search(th))))
    return per, tiers


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", help="เลข batch เช่น 049")
    ap.add_argument("--done", action="store_true", help="ทุกไฟล์ใน translations/done/")
    ap.add_argument("--parts", type=int, default=2, help="แบ่งไฟล์เป็นกี่ส่วน (ค่าตั้งต้น 2)")
    ap.add_argument("--min-lines", type=int, default=8,
                    help="ข้ามตัวละครที่มีบทน้อยกว่านี้ (เสียงรบกวน)")
    a = ap.parse_args()

    batches = []
    if a.only:
        batches = [a.only]
    else:
        for p in sorted((paths.TRANSLATIONS / "done").glob("batch_*.done.json")):
            batches.append(p.name[len("batch_"):-len(".done.json")])
    if not batches:
        print("ไม่พบไฟล์ done")
        return 2

    warned = 0
    for b in batches:
        res = analyse(b, a.parts)
        if res is None:
            print("batch_%s: ไม่พบไฟล์" % b)
            continue
        per, tiers = res
        rows = []
        for spk, items in sorted(per.items(), key=lambda x: -len(x[1])):
            if len(items) < a.min_lines:
                continue
            tier = tiers.get(spk.lower(), "?")
            buckets = [[0, 0] for _ in range(a.parts)]
            for part, hit in items:
                buckets[part][1] += 1
                buckets[part][0] += hit
            pcts = [(100.0 * h / t) if t else None for h, t in buckets]
            seen = [p for p in pcts if p is not None]
            gap = (max(seen) - min(seen)) if len(seen) > 1 else 0.0
            bad = (tier in NO_PARTICLE_TIERS and any(p for p in seen if p > 0)) or \
                  (tier not in NO_PARTICLE_TIERS and gap > GAP_WARN)
            rows.append((spk, tier, len(items), pcts, gap, bad))
            warned += bad
        if not rows:
            continue
        print("\n== batch_%s (แบ่ง %d ส่วน · ไม่นับมอนอโลก/neutral)" % (b, a.parts))
        for spk, tier, n_lines, pcts, gap, bad in rows:
            cells = " ".join("  n/a" if p is None else "%5.1f%%" % p for p in pcts)
            flag = "  <-- ตรวจ" if bad else ""
            note = " [ต้องเป็น 0%]" if tier in NO_PARTICLE_TIERS else ""
            print("  %-28s %-4s %3d บรรทัด  %s  ห่าง %4.1f%s%s"
                  % (spk, tier, n_lines, cells, gap, note, flag))
    if warned:
        print("\nจุดที่ควรตรวจด้วยตา: %d" % warned)
        print("(ห่างเกิน %d จุด = อาจเป็นรอยต่อการแบ่งงาน · T2/T3 ที่ไม่ใช่ 0%% = ทะเบียนหลุด)" % GAP_WARN)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
