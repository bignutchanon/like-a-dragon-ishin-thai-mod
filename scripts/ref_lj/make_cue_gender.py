#!/usr/bin/env python3
"""ถอดเพศผู้พูดจาก **ชื่อคิวเสียง** ใน `sound_auth.bin` — หลักฐานชั้นดีที่สุดของโปรเจกต์

ที่มา (26 ส.ค. 2026): เดิมเรารู้เพศจาก `sound_voicer.bin` เฉพาะตัวละครที่ชื่อในเกมตรงกับ
ชื่อแถวของ voicer เท่านั้น ทำให้ NPC ที่ชื่อเป็นคำบรรยาย ("Rugged Thug" / "Siren Owner")
ค้างเป็น `unknown` ทั้งหมด → คิวถูกบังคับแปลกลางเพศทั้งที่เกมรู้เพศอยู่แล้ว

โครงที่พบ: ทุกตาราง `speech_list_*` มี `table.subTable` ที่แถวชื่อว่า
    speech_ja20130_ikatsui_hangure
    speech_m04_03900_seiren
คือ **ชื่อคิวเสียง** ซึ่งลงท้ายด้วย *id ของ voicer* · และคอลัมน์ `0` ของแถวคิว = เลขคิวสากล
ซึ่งตรงกับคอลัมน์ `1` ของแถวบทพูดในตารางหลัก (ตรวจแล้ว 15,622/15,622 แถว = 100%)

    บทพูด.col1  ==  คิว.col0   →  ชื่อคิว  →  ตัดคำหน้าออกจนเจอ id ใน sound_voicer  →  sex

`sound_voicer.bin` คอลัมน์ `sex`: 1 = ชาย · 2 = หญิง · 0 = ไม่ระบุ
และคอลัมน์ `voice_type` เป็นคำญี่ปุ่นบอกประเภทเสียง (เช่น `男性_老人` = ชายสูงอายุ)
ซึ่งใช้เลือกทะเบียนภาษาไทยได้ด้วย จึงเก็บไว้ในผลลัพธ์

ผลลัพธ์: `extracted/facts/cue_gender.json`
    {ชื่อผู้พูด EN: {"gender", "votes", "voice_types", "examples"}}

ใช้:
  python scripts/make_cue_gender.py            # ดูสรุปเฉย ๆ
  python scripts/make_cue_gender.py --write
"""
import argparse
import collections
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

SRC = paths.DB_EN / "sound_auth.bin.json"
VOICER = paths.DB_EN / "sound_voicer.bin.json"
TALKER = paths.DB_EN / "talk_talker.bin.json"
OUT = paths.EXTRACTED / "facts" / "cue_gender.json"

SEX_NAME = {1: "male", 2: "female"}


def load(p):
    return json.load(io.open(p, encoding="utf-8"))


def first_row(v):
    """แถว ARMP หนึ่งแถว = {ชื่อแถว: {คอลัมน์...}} — คืน (ชื่อแถว, dict คอลัมน์)"""
    if not isinstance(v, dict) or not v:
        return None, None
    k = list(v.keys())[0]
    r = v[k]
    return (k or ""), (r if isinstance(r, dict) else None)


def voicer_table():
    """id ของ voicer (ตัวเล็ก) -> (sex, voice_type) เฉพาะตัวที่ระบุเพศ"""
    out = {}
    for k, v in load(VOICER).items():
        if not k.isdigit():
            continue
        name, row = first_row(v)
        if not row or not name:
            continue
        sex = row.get("sex") or 0
        if sex in SEX_NAME:
            out[name.lower()] = (sex, (row.get("voice_type") or "").strip())
    return out


def talker_names():
    out = {}
    for k, v in load(TALKER).items():
        if not k.isdigit():
            continue
        ja, row = first_row(v)
        if row:
            out[int(k)] = ((row.get("talk_talker") or "").strip(), ja)
    return out


def iter_speech_tables(node):
    if not isinstance(node, dict):
        return
    for k, v in node.items():
        if isinstance(k, str) and k.startswith("speech_list") and isinstance(v, dict):
            yield k, v
        else:
            yield from iter_speech_tables(v)


def suffix_voicer(cue, vox):
    """ตัดคำหน้าของชื่อคิวทีละท่อนจนเจอ id ที่มีจริงใน sound_voicer"""
    parts = (cue or "").lower().split("_")
    for i in range(1, len(parts)):
        cand = "_".join(parts[i:])
        if cand in vox:
            return cand
    return None


def build():
    vox = voicer_table()
    names = talker_names()
    data = load(SRC)

    votes = collections.defaultdict(collections.Counter)
    vtypes = collections.defaultdict(collections.Counter)
    voicers = collections.defaultdict(collections.Counter)   # ชื่อผู้พูด -> id ของ voicer ที่ใช้จริง
    examples = {}
    stats = collections.Counter()

    for _, node in iter_speech_tables(data):
        tbl = node.get("table")
        if not isinstance(tbl, dict):
            continue
        # แผนที่ เลขคิวสากล -> ชื่อคิว
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
            if len(((row.get("4") or "") + (row.get("13") or "")).strip()) < 2:
                continue
            stats["lines"] += 1
            cue = by_cue.get(row.get("1"))
            if not cue:
                continue
            stats["cued"] += 1
            vid = suffix_voicer(cue, vox)
            if not vid:
                continue
            stats["sexed"] += 1
            en = names.get(row.get("3"), ("", ""))[0]
            if not en:
                continue
            sex, vtype = vox[vid]
            votes[en][sex] += 1
            voicers[en][vid] += 1
            if vtype:
                vtypes[en][vtype] += 1
            examples.setdefault(en, cue)

    out = {}
    for en, c in votes.items():
        m, f = c.get(1, 0), c.get(2, 0)
        gender = "male" if m > f else ("female" if f > m else "unknown")
        rec = {"gender": gender, "votes": {"male": m, "female": f},
               "example_cue": examples.get(en, "")}
        if vtypes.get(en):
            rec["voice_types"] = [t for t, _ in vtypes[en].most_common(3)]
        # เก็บ id ของ voicer ไว้ให้ make_speaker_aliases.py ใช้ยุบ "ชื่อที่แสดงผล" กับ "id ของ voicer"
        # ที่เป็นคนเดียวกันแต่ถูกนับแยก (Siren Owner ↔ seiren · Chubby Thug ↔ fat_hangure)
        rec["voicers"] = [v for v, _ in voicers[en].most_common()]
        # เสียงปนสองเพศ = ชื่อผู้พูดนี้ใช้ร่วมกันหลายคน -> เตือนไว้
        if m and f:
            rec["mixed"] = True
        out[en] = rec
    return out, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    table, stats = build()
    print("บรรทัดที่มีข้อความ %s · จับคิวได้ %s · คิวชี้ voicer ที่ระบุเพศ %s"
          % tuple(format(stats[k], ",") for k in ("lines", "cued", "sexed")))
    g = collections.Counter(v["gender"] for v in table.values())
    mixed = sum(1 for v in table.values() if v.get("mixed"))
    print("ผู้พูดที่ได้เพศจากคิวเสียง %d คน: %s · เสียงปนสองเพศ %d คน"
          % (len(table), dict(g), mixed))

    if not a.write:
        print("(ใส่ --write เพื่อเขียนไฟล์)")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(
        json.dumps(table, ensure_ascii=False, indent=1) + "\n")
    print("เขียน %s แล้ว" % OUT)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
