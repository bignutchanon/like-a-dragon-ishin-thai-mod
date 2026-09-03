#!/usr/bin/env python3
"""ถอด "ใครพูด" ของทุกบรรทัดใน `auth.bin` — ซับที่เล่นทับคัตซีน (cinema telop)

ที่มา (พบ 25 ส.ค. 2026 — ปิดหนี้ speaker mapping ข้อ 2 และ 6 ใน HANDOFF):
`auth.bin` มีคอลัมน์เดียวชื่อ `cinema_telop` แต่ทุกแถว = ตารางย่อยหนึ่งฉาก
(ชื่อแถว = คีย์ฉาก เช่น `a01_0010` · `dlc_a02_0030`) แต่ละแถวในตารางย่อยคือซับหนึ่งบรรทัด:

  "1"/"2" = เฟรมเริ่ม/จบ
  "4"     = ซับตอนเล่นเสียง **ญี่ปุ่น**
  "5"     = ซับตอนเล่นเสียง **อังกฤษ**
  "8"     = **id ผู้พูด** ชี้ไปยังแถวใน `talk_talker.bin` (3 = 八神/Yagami · 869 = 海藤/Kaito)

ก่อนหน้านี้ทั้ง 3,157 บรรทัดของ `auth.bin` ไม่ผูกผู้พูดเลย นักแปลจึงเห็นแต่ประโยคลอย ๆ
(batch_018 ถูกตีกลับ 81 บรรทัดเพราะเดาเพศจากเนื้อฉาก) — คอลัมน์ "8" ตอบให้ตรง ๆ

ผลลัพธ์: `extracted/facts/auth_speaker.json` — โครงเดียวกับ `speech_speaker.json`
  {ข้อความ EN: {"table", "chapter", "speaker", "speaker_ja", "speaker_id",
                "gender", "column", "dupes": [...]}}

ใช้:
  python scripts/make_auth_speaker.py --write
  python scripts/make_auth_speaker.py --find "A hundred!?"
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

SRC = paths.DB_EN / "auth.bin.json"
TALKER = paths.DB_EN / "talk_talker.bin.json"
GENDER = paths.EXTRACTED / "facts" / "gender_evidence.json"
OUT = paths.EXTRACTED / "facts" / "auth_speaker.json"

CHAP_RE = re.compile(r"^(?:dlc_)?a(\d+)_")
SPEAKER_COL = "8"
COL_TEXT = {"4": "ja_audio", "5": "en_audio"}   # ซับสองชุดตามภาษาเสียงที่ผู้เล่นเลือก


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


def iter_scenes(data):
    """คืน (ชื่อฉาก, ตารางย่อย cinema_telop) ของทุกแถวใน auth.bin"""
    for k, v in data.items():
        if not k.isdigit() or not isinstance(v, dict):
            continue
        scene, inner = list(v.items())[0]
        if not isinstance(inner, dict):
            continue
        sub = inner.get("cinema_telop")
        if isinstance(sub, dict) and scene:
            yield scene, sub


def build():
    data = load(SRC)
    names = talker_names()
    genders = gender_table()
    out = {}
    stats = collections.Counter()
    for scene, sub in iter_scenes(data):
        m = CHAP_RE.match(scene)
        chapter = int(m.group(1)) if m else None
        for rk, rv in sub.items():
            if not rk.isdigit() or not isinstance(rv, dict):
                continue
            row = list(rv.values())[0]
            if not isinstance(row, dict):
                continue
            sid = row.get(SPEAKER_COL)
            en_name, ja_name = names.get(sid, ("", ""))
            for col, kind in COL_TEXT.items():
                text = row.get(col)
                if not isinstance(text, str) or len(text.strip()) < 2:
                    continue
                stats[kind] += 1
                rec = {"table": scene, "chapter": chapter, "speaker": en_name,
                       "speaker_ja": ja_name, "speaker_id": sid, "column": col,
                       "gender": genders.get(en_name.lower(), "unknown")}
                prev = out.get(text)
                if prev is None:
                    out[text] = rec
                    continue
                seen = [(prev["table"], prev["speaker_id"])]
                seen += [(d["table"], d["speaker_id"]) for d in prev.get("dupes", [])]
                if (scene, sid) in seen:
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
