#!/usr/bin/env python3
"""ยุบ "ชื่อผู้พูดที่แสดงบนจอ" กับ "id ของ voicer" ที่เป็นคนเดียวกันแต่ถูกนับแยก

ที่มา (26 ส.ค. 2026 · sprint 6): ผู้ตรวจสาม batch เจอปัญหาเดียวกันโดยไม่ได้นัดกัน —
บทของ `Siren Owner` ติดธง `neutral` เพราะระบบเห็นว่ามีผู้พูดสองคนใช้ข้อความเดียวกัน
คือ `Siren Owner` กับ `seiren` ทั้งที่เป็นคนเดียวกัน (ชื่อบนจอ กับ id ของ voicer)
คู่แบบเดียวกันที่เจอ: `Chubby Thug`↔`fat_hangure` · `Jo Masuda`↔`tender_master` ·
`Yokomichi Owner`↔`yokomichi` · `Gaudy Thug`↔`chara_hangure` · `Rugged Thug`↔`ikatsui_hangure`
ผลคือคิวถูกบังคับแปลกลางเพศเกินจริง และตารางตัวละครมีคนซ้ำสองแถวคนละทะเบียน

วิธีพิสูจน์ว่าเป็นคนเดียวกัน (ไม่ใช่เดาจากชื่อ):
  `extracted/facts/cue_gender.json` บันทึกไว้แล้วว่าชื่อบนจอแต่ละชื่อใช้ voicer id ใดบ้าง
  (มาจากชื่อคิวเสียงในไฟล์เกม ดู make_cue_gender.py) — ถ้า voicer id นั้น
  **ถูกใช้โดยชื่อบนจอเพียงชื่อเดียว** และตัว id เองก็โผล่มาเป็น "ชื่อผู้พูด" ในไฟล์ facts ด้วย
  แปลว่าทั้งสองคือคนเดียวกัน

ผลลัพธ์: `extracted/facts/speaker_aliases.json`  {"id ของ voicer": "ชื่อบนจอ"}
ใช้โดย `make_batch_context.py` (ยุบก่อนนับ dupes) และ `harvest_gender_evidence.py`

ใช้:
  python scripts/make_speaker_aliases.py            # ดูสรุป
  python scripts/make_speaker_aliases.py --write
"""
import argparse
import collections
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

CUE = paths.EXTRACTED / "facts" / "cue_gender.json"
FACTS = [paths.EXTRACTED / "facts" / n for n in
         ("speech_speaker.json", "talk_speaker.json", "auth_speaker.json")]
OUT = paths.EXTRACTED / "facts" / "speaker_aliases.json"


def load(p, default=None):
    if not os.path.exists(p):
        return default if default is not None else {}
    return json.load(io.open(p, encoding="utf-8"))


def speaker_names():
    """ชื่อผู้พูดทั้งหมดที่โผล่จริงในไฟล์ facts -> จำนวนบรรทัด (ใช้เรียงลำดับตอนรายงานเท่านั้น)"""
    c = collections.Counter()
    for p in FACTS:
        for rec in load(p).values():
            if not isinstance(rec, dict):
                continue
            for r in [rec] + list(rec.get("dupes") or []):
                n = (r.get("speaker") or "").strip()
                if n:
                    c[n] += 1
    # ชื่อผู้พูดตัวเล็กที่เป็นปัญหาจริงมาจาก speech_speaker_map.json (คีย์เสียงดิบ) ไม่ใช่สามไฟล์ข้างบน
    for rec in load(paths.EXTRACTED / "facts" / "speech_speaker_map.json").values():
        if isinstance(rec, dict):
            for n in rec.get("speaker_exact") or []:
                if n:
                    c[str(n)] += 1
    return c


def build():
    cue = load(CUE)
    cue.pop("_meta", None)
    names = speaker_names()
    lower = {n.lower(): n for n in names}

    # voicer id -> ชื่อบนจอที่ใช้ id นั้น (อาจมีหลายชื่อ = ใช้เสียงร่วมกัน ห้ามยุบ)
    owners = collections.defaultdict(set)
    for display, rec in cue.items():
        for vid in rec.get("voicers") or []:
            owners[vid].add(display)

    alias, skipped = {}, []
    for vid, ds in sorted(owners.items()):
        if len(ds) != 1:                  # เสียงเดียวใช้กับหลายตัวละคร = คนละคนจริง ห้ามยุบ
            skipped.append((vid, sorted(ds)))
            continue
        display = list(ds)[0]
        if display.lower() == vid.lower():
            continue
        # เก็บทั้งรูปที่โผล่จริงในไฟล์ facts และตัว id ดิบ — คีย์เสียงบางแหล่งใช้ id ตรง ๆ
        alias[lower.get(vid.lower(), vid)] = display
    return alias, skipped, names


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    alias, skipped, names = build()
    print("คู่ที่ยุบได้ %d คู่" % len(alias))
    for k, v in sorted(alias.items(), key=lambda kv: -names.get(kv[0], 0)):
        print("   %-28s -> %-28s (%d บรรทัด)" % (k, v, names.get(k, 0)))
    if skipped:
        print("\nไม่ยุบ %d id (เสียงเดียวใช้หลายตัวละคร):" % len(skipped))
        for vid, ds in skipped[:10]:
            print("   %-24s %s" % (vid, ", ".join(ds)))

    if not a.write:
        print("\n(ใส่ --write เพื่อเขียนไฟล์)")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(
        json.dumps(alias, ensure_ascii=False, indent=1) + "\n")
    print("\nเขียน %s แล้ว" % OUT)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
