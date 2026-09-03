#!/usr/bin/env python3
"""ถอด "ใครพูด" ของทุกบรรทัดใน talk.bin — ตารางบทสนทนาที่เดิมทีมคิดว่าไม่มีข้อมูลผู้พูด

ที่มา (ผู้ตรวจ TALK_005 ขุดเจอ 21 ส.ค. 2026): แต่ละแถวใน subtable ของ `talk.bin`
มีฟิลด์ `"2"` = **id ผู้พูด** ที่ชี้ไปยังแถวใน `talk_talker.bin` (เช่น 3 = 八神/Yagami)
และฟิลด์ `"3"` = ตัวข้อความ · ชื่อ subtable บอกคดี/ฉาก (เช่น `coyote_side_a01`)

เดิมนักแปลคิว TALK ต้อง "อนุมานผู้พูดจากตรรกะบทสนทนา" ทุกบรรทัด — ไฟล์นี้ตอบให้ตรง ๆ

ผลลัพธ์: `extracted/facts/talk_speaker.json`
  {ข้อความ EN: {"table": <ชื่อ subtable>, "speaker_id": n, "speaker": <ชื่อ EN>,
                "speaker_ja": <ชื่อ JA>, "gender": male/female/unknown,
                "dupes": [ ...ผู้พูดคนอื่นที่พูดข้อความเดียวกันในตารางอื่น... ]}}

⚠ `dupes` มีเฉพาะข้อความที่ถูกใช้ซ้ำข้ามตาราง — ต้องอ่านก่อนเลือกทะเบียนภาษา
เพราะไฟล์คำแปลเป็น map แบน EN→TH ตัวเดียว คำแปลเดียวต้องใช้ได้กับผู้พูดทุกคนในรายการ

ใช้:
  python scripts/make_talk_speaker.py --write
  python scripts/make_talk_speaker.py --find "Oh, hello. Are you here about the job, Ma'am?"
"""
import argparse
import collections
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

DB = paths.DB_EN
OUT = paths.PROJECT / "extracted" / "facts" / "talk_speaker.json"


def load(name):
    return json.load(io.open(DB / name, encoding="utf-8"))


def talker_table():
    """id -> (ชื่อ EN, ชื่อ JA, voicer id)"""
    t = load("talk_talker.bin.json")
    out = {}
    for k in t:
        if not k.isdigit():
            continue
        ja, row = list(t[k].items())[0]
        if not isinstance(row, dict):
            continue
        out[int(k)] = (row.get("talk_talker") or "", ja or "", row.get("voicer", 0))
    return out


# ชื่อผู้พูดใน talk_talker.bin กับคีย์ใน voicer_gender.json สะกดคนละแบบ
# (ตารางของ Judgment ภาคแรกถูกล้างทิ้ง — ของ Lost Judgment ต้องเติมเองเมื่อเจอหลักฐาน)
ALIASES = {
}


# เพศที่พิสูจน์ได้จาก "เนื้อ EN ในเกม" แต่ voicer_gender.json ไม่มีข้อมูล
# กติกา: ห้ามเดาจากชื่อ — ต้องมีหลักฐานในไฟล์เกม แล้วบันทึกไว้ที่
# docs/reference/gender_evidence_lj.md ก่อนเพิ่มรายการที่นี่
OVERRIDES = {
}


def load_harvest():
    """ผลพิสูจน์เพศจาก scripts/harvest_gender_evidence.py (ถ้ามี) — แม่นกว่า voicer อย่างเดียว
    เพราะรวมหลักฐาน he/she · Mr./Ms. · ชื่อผู้พูดที่บอกเพศเอง เข้าไปด้วย"""
    p = paths.PROJECT / "extracted" / "facts" / "gender_evidence.json"
    if not p.exists():
        return {}
    d = json.load(io.open(p, encoding="utf-8"))
    d.pop("_meta", None)
    return {k.lower(): v.get("gender", "unknown") for k, v in d.items()}


HARVEST = None


def gender_of(name_en, voicer_gender):
    if not name_en:
        return "unknown"
    low = name_en.lower()
    if HARVEST and HARVEST.get(low, "unknown") != "unknown":
        return HARVEST[low]
    if low in OVERRIDES:
        return OVERRIDES[low]
    if low in ALIASES:
        return voicer_gender.get(ALIASES[low], "unknown")
    return voicer_gender.get(low.replace(" ", "_"), "unknown")


def build():
    global HARVEST
    HARVEST = load_harvest()
    talkers = talker_table()
    vg = json.load(io.open(paths.PROJECT / "extracted" / "facts" / "voicer_gender.json",
                           encoding="utf-8"))
    talk = load("talk.bin.json")
    out = {}
    for k in talk:
        if not k.isdigit():
            continue
        table, val = list(talk[k].items())[0]
        if not isinstance(val, dict):
            continue
        sub = val.get("text")
        if not isinstance(sub, dict):
            continue
        for kk in sub:
            if not kk.isdigit():
                continue
            row = list(sub[kk].values())[0]
            if not isinstance(row, dict):
                continue
            text = row.get("3")
            if not isinstance(text, str) or not text.strip():
                continue
            sid = row.get("2", 0)
            en, ja, _ = talkers.get(sid, ("", "", 0))
            rec = {"table": table, "speaker_id": sid, "speaker": en,
                   "speaker_ja": ja, "gender": gender_of(en, vg)}
            prev = out.get(text)
            if prev is None:
                out[text] = rec
                continue
            # ข้อความเดียวกันถูกใช้ซ้ำหลาย subtable — เดิมตัวหลังทับตัวแรกเงียบ ๆ
            # ทำให้ผู้ตรวจ TALK_010 เจอ "Wait, Yagami-san." ชี้ผิดคน (Kondo แทน Amamiya)
            # ตอนนี้เก็บทุกคู่ไว้ใน "dupes" แทน (ตัวแรกยังอยู่ระดับบนสุดเพื่อความเข้ากันได้)
            seen = [(prev["table"], prev["speaker_id"])]
            seen += [(d["table"], d["speaker_id"]) for d in prev.get("dupes", [])]
            if (table, sid) in seen:
                continue
            prev.setdefault("dupes", []).append(rec)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--find", help="ค้นข้อความ EN ตรง ๆ")
    a = ap.parse_args()
    table = build()

    if a.find:
        meta = table.get(a.find)
        if not meta:
            print("ไม่พบข้อความนี้ใน talk.bin")
            return 0
        print(json.dumps(meta, ensure_ascii=False))
        if meta.get("dupes"):
            print("⚠ ข้อความนี้ถูกใช้ %d ที่ — ต้องเลือกคำแปลที่ใช้ได้ทุกผู้พูด "
                  "หรือดูว่าตารางไหนตรงกับฉากของ batch" % (1 + len(meta["dupes"])))
        return 0

    c = collections.Counter(v["speaker"] or "(ไม่มีชื่อ)" for v in table.values())
    dup = sum(1 for v in table.values() if v.get("dupes"))
    print("ถอดได้ %s บรรทัด · ผู้พูดไม่ซ้ำ %d คน · ข้อความที่ใช้ซ้ำหลายตาราง %d"
          % (format(len(table), ","), len(c), dup))
    print("5 อันดับแรก: %s" % " · ".join("%s(%d)" % x for x in c.most_common(5)))
    if a.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        io.open(OUT, "w", encoding="utf-8").write(json.dumps(table, ensure_ascii=False, indent=1))
        print("เขียน %s แล้ว" % OUT)
    else:
        print("ใส่ --write เพื่อเขียนไฟล์")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
