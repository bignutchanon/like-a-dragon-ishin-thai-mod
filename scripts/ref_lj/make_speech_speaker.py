#!/usr/bin/env python3
"""ถอด "ใครพูด" ของ **ทุกบรรทัดคัตซีน** ใน `sound_auth.bin` (คิวแปลก้อนใหญ่ที่สุดของเกม)

ที่มา (พบ 25 ส.ค. 2026): ทุกแถวในตาราง `speech_list_*` ของ `sound_auth.bin` มีคอลัมน์
  "1"  = cue เสียง
  "2"  = ลำดับในกลุ่มบทสนทนา
  "3"  = **id ผู้พูด** ที่ชี้ไปยังแถวใน `talk_talker.bin` (3 = 八神/Yagami)
  "4"  = ซับตอนเล่นเสียง **ญี่ปุ่น**
  "13" = ซับตอนเล่นเสียง **อังกฤษ** (`message_for_audio_language_en`)
ก่อนหน้านี้เราได้ผู้พูดจาก `subTable` เท่านั้น ซึ่งครอบแค่ 2,230 จาก 15,950 แถว —
คอลัมน์ "3" ให้ผู้พูด **ครบทุกแถว**

⚠ ต้องแปลทั้งคอลัมน์ 4 และ 13 (ผู้เล่นเลือกเสียง JA/EN ได้ ซับคนละชุด)

ผลลัพธ์: `extracted/facts/speech_speaker.json` — โครงเดียวกับ `talk_speaker.json`
  {ข้อความ EN: {"table", "chapter", "speaker", "speaker_ja", "speaker_id",
                "gender", "column", "dupes": [...]}}

ใช้:
  python scripts/make_speech_speaker.py --write
  python scripts/make_speech_speaker.py --find "Kosuke-kun always says he only ever eats\\nfast food for lunch."
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

SRC = paths.DB_EN / "sound_auth.bin.json"
TALKER = paths.DB_EN / "talk_talker.bin.json"
GENDER = paths.EXTRACTED / "facts" / "gender_evidence.json"
OUT = paths.EXTRACTED / "facts" / "speech_speaker.json"

CHAP_RE = re.compile(r"_(?:dlc_)?main_c(\d+)")
COL_TEXT = {"4": "ja_audio", "13": "en_audio"}   # ซับสองชุดตามภาษาเสียง


def load(p):
    return json.load(io.open(p, encoding="utf-8"))


def talker_names():
    """id -> (ชื่อ EN, ชื่อ JA)"""
    t = load(TALKER)
    out = {}
    for k, v in t.items():
        if not k.isdigit() or not isinstance(v, dict):
            continue
        ja, row = list(v.items())[0]
        if not isinstance(row, dict):
            continue
        out[int(k)] = ((row.get("talk_talker") or "").strip(), (ja or "").strip())
    return out


def gender_table():
    if not os.path.exists(GENDER):
        return {}
    d = load(GENDER)
    d.pop("_meta", None)
    return {k.lower(): v.get("gender", "unknown") for k, v in d.items()}


def iter_speech_tables(node, path=()):
    if not isinstance(node, dict):
        return
    for k, v in node.items():
        if isinstance(k, str) and k.startswith("speech_list") and isinstance(v, dict):
            yield k, v
        else:
            yield from iter_speech_tables(v, path + (k,))


def build():
    data = load(SRC)
    names = talker_names()
    genders = gender_table()
    out = {}
    stats = collections.Counter()
    for list_key, node in iter_speech_tables(data):
        table = node.get("table")
        if not isinstance(table, dict):
            continue
        m = CHAP_RE.search(list_key)
        chapter = int(m.group(1)) if m else None
        for rk, rv in table.items():
            if not rk.isdigit() or not isinstance(rv, dict):
                continue
            row = list(rv.values())[0]
            if not isinstance(row, dict):
                continue
            sid = row.get("3")
            en_name, ja_name = names.get(sid, ("", ""))
            for col, kind in COL_TEXT.items():
                text = row.get(col)
                if not isinstance(text, str) or len(text.strip()) < 2:
                    continue
                stats[kind] += 1
                rec = {"table": list_key, "chapter": chapter, "speaker": en_name,
                       "speaker_ja": ja_name, "speaker_id": sid, "column": col,
                       "gender": genders.get(en_name.lower(), "unknown")}
                prev = out.get(text)
                if prev is None:
                    out[text] = rec
                    continue
                seen = [(prev["table"], prev["speaker_id"])]
                seen += [(d["table"], d["speaker_id"]) for d in prev.get("dupes", [])]
                if (list_key, sid) in seen:
                    continue
                prev.setdefault("dupes", []).append(rec)
                stats["dupe"] += 1
    return out, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--find")
    a = ap.parse_args()

    table, stats = build()
    if a.find:
        rec = table.get(a.find)
        print(json.dumps(rec, ensure_ascii=False, indent=1) if rec else "ไม่พบข้อความนี้")
        return 0

    c = collections.Counter(v["speaker"] or "(ไม่มีชื่อ)" for v in table.values())
    g = collections.Counter(v["gender"] for v in table.values())
    dup = sum(1 for v in table.values() if v.get("dupes"))
    print("ถอดได้ %s บรรทัด (ซับเสียงญี่ปุ่น %s · ซับเสียงอังกฤษ %s)"
          % (format(len(table), ","), format(stats["ja_audio"], ","), format(stats["en_audio"], ",")))
    print("ผู้พูดไม่ซ้ำ %d คน · ข้อความใช้ซ้ำหลายที่ %d" % (len(c), dup))
    print("เพศของผู้พูด: %s" % dict(g))
    print("5 อันดับแรก: %s" % " · ".join("%s(%d)" % x for x in c.most_common(5)))

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
