#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ถอดเพศผู้พูด **รายบรรทัด** จากคิวเสียงใน sound_auth.bin

## ทำไมต้องมีตัวนี้แยกจาก make_cue_gender.py

`make_cue_gender.py` ตัดสินเพศ *ต่อชื่อผู้พูด* ด้วยเสียงข้างมากของคิวเสียงทั้งหมดที่ชื่อนั้นใช้
พอเกมเอาชื่อเดียวไปใช้กับคนหลายคน (`Sakura` = ทั้งนักเรียนชายและครูหญิง — ไฟล์เกมมี
`Sakura-sensei's Mother` อยู่ด้วย) เสียงข้างมากจะกลบฝั่งน้อยทิ้ง แล้วธง `neutral` ก็ยังเป็น false
ผลคือบทของตัวละครหญิงถูกแปลด้วย "ครับ/ผม" (docs/ISSUES.md LJ-006)

ข้อมูลที่ต้องใช้มีอยู่แล้วในลูปเดียวกัน แค่ไม่ได้เก็บไว้: ทุก **แถวบทพูด** ผูกกับคิวเสียงของตัวเอง
และคิวนั้นบอกเพศได้ตรง ๆ ผ่าน `sound_voicer.sex` สคริปต์นี้จึงเก็บผลลัพธ์แบบไม่ยุบ:

    ข้อความ EN -> {gender, votes, speakers, voice_types, cues}

ถ้าข้อความเดียวถูกใช้ซ้ำหลายคิวและเพศไม่ตรงกัน จะได้ `gender: "mixed"` ซึ่งแปลว่า
**บรรทัดนั้นต้องแปลกลางเพศจริง ๆ** ต่างจากกรณีที่ทุกคิวของบรรทัดนั้นเป็นเพศเดียวกัน
ซึ่งชี้ขาดได้เลยว่าเป็นเพศไหน

ผลลัพธ์: `extracted/facts/line_gender.json`

ใช้:
  python scripts/make_line_gender.py            # ดูสรุปเฉย ๆ
  python scripts/make_line_gender.py --write
"""
import argparse
import collections
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")           # กติกาเหล็กข้อ 6
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths                                        # noqa: E402
from make_cue_gender import (SRC, first_row, iter_speech_tables, load,     # noqa: E402
                             suffix_voicer, talker_names, voicer_table)

OUT = paths.EXTRACTED / "facts" / "line_gender.json"
SEX_NAME = {1: "male", 2: "female"}

# ---------------------------------------------------------------- SKIP_VOICERS
# แถวที่คอลัมน์ `sex` เป็นเพศของ **นักพากย์** ไม่ใช่ของตัวละคร (โปรเจกต์ Judgment เจอก่อน:
# sumire โฮสเตสหญิงแต่ sex=ชาย · kjart_woman sex=ชาย · alpes_boy เด็กเสิร์ฟชายแต่ sex=หญิง)
# ตัวละครหลักตรงหมด พลาดเฉพาะ NPC — ถ้าเจอเพิ่มให้ใส่ที่นี่พร้อมเหตุผลเสมอ
#
# กติกา: **ทะเบียนตัวละครชนะเสมอ** เมื่อขัดกับคอลัมน์ sex
# LJ ยังไม่พบแถวแบบนี้ (ตรวจ 29 ส.ค. 2026: sex ไม่ขัดกับทะเบียนตัวละครสักตัว)
# ที่ LJ เจอคือ **`voice_type` ต่างหากที่ผิด 4 แถว** — keiko / rabuho / staff_hat / friends_dress
# มี sex=หญิง แต่ voice_type ขึ้นต้น 男性 ทั้งที่เนื้อหาบทเป็นหญิงชัดเจน
# (keiko: "Kosuke-kun... He's a sweet guy, really!") จึงห้ามใช้ voice_type เป็นตัวตัดสินเพศ
SKIP_VOICERS = {
    # "voicer_id": "เหตุผล + หลักฐาน",
}


def cross_source_conflicts():
    """คืนเซ็ตข้อความที่ถูกใช้ทั้งในคัตซีนและใน talk.bin โดยผู้พูดคนละเพศ

    บรรทัดสั้น ๆ อย่าง "Good luck." / "Hello." / "Yeah..." ถูกเกมใช้ซ้ำข้ามตัวละคร
    ถ้าคิวเสียงบอกเพศหนึ่งแต่ผู้พูดใน talk.bin เป็นอีกเพศ แปลว่าบรรทัดนั้นใช้ร่วมกันจริง
    ต้องแปลกลางเพศ ไม่ใช่เชื่อคิวเสียงฝ่ายเดียว (โปรเจกต์ Judgment เจอก่อนจากเคส
    "Good luck." ที่เป็นได้ทั้งมาฟุยุและยากามิ)
    """
    chars = {}
    for name in ("characters_main.json", "characters_side.json"):
        f = paths.TRANSLATIONS / name
        if f.exists():
            chars.update(json.load(io.open(f, encoding="utf-8")))
    by_name = {}
    for v in chars.values():
        if v.get("gender") in ("male", "female"):
            for n in v.get("names_in_game", []):
                by_name[n] = v["gender"]

    tk = load(paths.DB_EN / "talk_talker.bin.json")
    talker = {int(k): (tk[k][list(tk[k])[0]].get("talk_talker") or "").strip()
              for k in tk if k.isdigit()}
    talk = load(paths.DB_EN / "talk.bin.json")

    out = collections.defaultdict(set)

    def walk(node, depth=0):
        if not isinstance(node, dict) or depth > 6:
            return
        for k, v in node.items():
            if k.isdigit() and isinstance(v, dict) and v:
                row = v[list(v)[0]]
                if isinstance(row, dict):
                    txt, sid = row.get("3"), row.get("2")
                    if isinstance(txt, str) and len(txt.strip()) > 2 and isinstance(sid, int):
                        g = by_name.get(talker.get(sid, ""))
                        if g:
                            out[txt].add(g)
            walk(v, depth + 1)

    walk(talk)
    return out


def build():
    vox = voicer_table()
    for vid, why in SKIP_VOICERS.items():
        vox.pop(vid, None)
    names = talker_names()
    data = load(SRC)

    votes = collections.defaultdict(collections.Counter)      # ข้อความ EN -> Counter เพศ
    speakers = collections.defaultdict(collections.Counter)
    vtypes = collections.defaultdict(collections.Counter)
    cues = {}
    stats = collections.Counter()

    for _, node in iter_speech_tables(data):
        tbl = node.get("table")
        if not isinstance(tbl, dict):
            continue
        by_cue = {}
        for k, v in (tbl.get("subTable") or {}).items():
            if not k.isdigit():
                continue
            cue, row = first_row(v)
            if row and row.get("0") is not None:
                by_cue[row["0"]] = cue

        for k, v in tbl.items():
            if not k.isdigit():
                continue
            _, row = first_row(v)
            if not row:
                continue
            # คอลัมน์ 4 และ 13 = บทพูด EN **สองรูป** ของคิวเดียวกัน (ฉบับเต็มกับฉบับย่อ)
            # ไม่ใช่ช่องเดียวที่ต้องต่อกัน — ถ้าต่อจะได้คีย์ที่ไม่มีอยู่จริงในเกม
            texts = [t for t in ((row.get("4") or "").strip(), (row.get("13") or "").strip())
                     if len(t) >= 2]
            if not texts:
                continue
            stats["lines"] += 1
            cue = by_cue.get(row.get("1"))
            if not cue:
                continue
            vid = suffix_voicer(cue, vox)
            if not vid:
                continue
            stats["sexed"] += 1
            sex, vtype = vox[vid]
            spk = names.get(row.get("3"), ("", ""))[0]
            for text in texts:
                votes[text][sex] += 1
                if spk:
                    speakers[text][spk] += 1
                if vtype:
                    vtypes[text][vtype] += 1
                cues.setdefault(text, cue)

    talk_genders = cross_source_conflicts()

    out = {}
    for text, c in votes.items():
        m, f = c.get(1, 0), c.get(2, 0)
        if m and f:
            gender = "mixed"          # ข้อความถูกใช้ซ้ำโดยผู้พูดคนละเพศ -> ต้องกลางเพศ
        else:
            gender = "male" if m else "female"
        rec = {"gender": gender, "votes": {"male": m, "female": f},
               "example_cue": cues.get(text, "")}
        # ข้อความเดียวกันถูกใช้ใน talk.bin โดยผู้พูดอีกเพศด้วย -> กลางเพศเช่นกัน
        others = talk_genders.get(text, set()) - {gender}
        if gender != "mixed" and others:
            rec["cross_source"] = sorted(others)
            rec["cue_gender"] = gender
            gender = "mixed"
            rec["gender"] = gender
        if speakers.get(text):
            rec["speakers"] = [s for s, _ in speakers[text].most_common(4)]
        if vtypes.get(text):
            rec["voice_types"] = [t for t, _ in vtypes[text].most_common(3)]
        out[text] = rec
    return out, stats


def main():
    ap = argparse.ArgumentParser(description="ตารางเพศผู้พูดรายบรรทัดจากคิวเสียง")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    table, stats = build()
    per = collections.Counter(v["gender"] for v in table.values())
    print("บทพูดที่มีข้อความ %d แถว · ผูกคิวเสียงและรู้เพศ %d แถว"
          % (stats["lines"], stats["sexed"]))
    print("ข้อความไม่ซ้ำที่ชี้ขาดได้ %d รายการ — ชาย %d · หญิง %d · ปนสองเพศ %d"
          % (len(table), per["male"], per["female"], per["mixed"]))
    if a.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        io.open(OUT, "w", encoding="utf-8", newline="\n").write(
            json.dumps(table, ensure_ascii=False, indent=1) + "\n")
        print("เขียน %s แล้ว" % OUT)


if __name__ == "__main__":
    main()
