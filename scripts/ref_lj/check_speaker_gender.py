#!/usr/bin/env python3
"""จับบรรทัดที่คำลงท้าย/สรรพนามไทย **ขัดกับเพศของผู้พูดจริงในไฟล์เกม**

ที่มา: ผู้พูดของแต่ละบรรทัดอยู่ใน `extracted/facts/talk_speaker.json` (จาก `talk.bin` โดยตรง)
แต่คำแปลถูกทำทีละ batch นักแปลจึงมีโอกาสให้ผู้หญิงพูด "ครับ" หรือให้ยากามิพูด "ค่ะ" ได้
`merge_qc` ไม่จับ เพราะประโยคถูกไวยากรณ์อยู่แล้ว

ข้ามให้อัตโนมัติ:
  * บรรทัดที่มี `dupes` (หลายคนพูดข้อความเดียวกัน — คำแปลต้องเป็นกลางอยู่แล้ว)
  * เพศ `unknown`
  * คำที่หน้าตาเหมือนสรรพนามแต่ไม่ใช่ (เส้นผม/ทรงผม/โยคะ/นะคะที่อยู่กลางคำ ฯลฯ)

ใช้:
    python scripts/check_speaker_gender.py                       # ตรวจ master_th.json
    python scripts/check_speaker_gender.py --files translations/done/batch_TALK_065.done.json
"""
import argparse
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from thai_pronouns import (RE_CHAN, RE_DICHAN, RE_KU,     # noqa: E402
                            RE_KAE, RE_MUENG, RE_PHOM, RE_KHRAP, RE_KHA)
MASTER = os.path.join(ROOT, "translations", "master_th.json")
FACTS = os.path.join(ROOT, "extracted", "facts", "talk_speaker.json")
# บทคัตซีน (`sound_auth.bin`) อยู่คนละไฟล์กับบทเดินเมือง (`talk.bin`) — ต้องอ่านทั้งคู่
# (แก้ 25 ส.ค. 2026: เดิมอ่านแต่ talk_speaker ทำให้ไม่เคยตรวจบรรทัดคัตซีนเลย 23,575 บรรทัด)
FACTS_SPEECH = os.path.join(ROOT, "extracted", "facts", "speech_speaker.json")

# ⚠ **ไฟล์นี้เคยมีสำเนา RE_PHOM/RE_KHA ของตัวเอง** ซึ่งเป็นบั๊กชนิดเดียวกับที่ `thai_pronouns.py`
# ถูกสร้างมาเพื่อกำจัดตั้งแต่ sprint 9 — สำเนานั้นรอดมาได้เพราะประกาศไว้**ก่อน**บรรทัด import
# ด้านล่าง จึงไม่มีใครสังเกต · ผลคือตอน sprint 12 แก้ RE_PHOM ที่โมดูลกลางให้เลิกจับ
# "สีผม/ผมของฉัน/ผมตัวเอง" ไฟล์นี้ยัง**เตือนเท็จต่อไป** เพราะใช้รูปเก่าของตัวเอง
# → ลบสำเนาทิ้งแล้ว ใช้จากโมดูลกลางอย่างเดียว (26 ส.ค. 2026)
# กันคำที่ขึ้นต้นด้วย "คะ" แต่ไม่ใช่คำลงท้าย (คะแนน · คะน้า · คะยั้นคะยอ)
# แก้สองจุด 26 ส.ค. 2026 (พบจากนักแปล batch_040/041):
# 1. ลุคอะเฮดเดิมกันแค่ "แ" → "คะเน" (ประเมิน) ถูกจับเป็นคำลงท้าย · เพิ่ม เ โ ใ ไ เข้าไปด้วย
# 2. **ตัดลุคบีไฮนด์ `(?<![ก-ฮ])` ทิ้ง** — ของเดิมบล็อก "คะ" ที่ตามหลังพยัญชนะ ซึ่งคือ *ทุกกรณีปกติ*
#    ("ใช่ไหมคะ" · "เหรอคะ") ทำให้สาขา "คะ" แทบไม่เคยทำงานเลยตั้งแต่ต้น
#    หลังแก้จับเพิ่ม 85 บรรทัดใน master_th (ตรวจแล้วเป็นคำลงท้ายจริงทั้งหมด) · ขัดเพศผู้พูดยังคง 0
# `RE_KHA` ของโมดูลกลางไม่รวม "ดิฉัน" (เป็นสรรพนาม ไม่ใช่คำลงท้าย) แต่ไฟล์นี้ต้องนับเป็น
# "เครื่องหมายเพศหญิง" ด้วย จึงต่อเพิ่มตรงนี้แทนการเขียนรูปใหม่
RE_FEMALE_MARK = re.compile(RE_KHA.pattern + r"|ดิฉัน")


RE_QUOTE = re.compile(r"[\"“”「『][^\"“”」』]*[\"“”」』]")


def outside_quotes(th):
    """ตัดข้อความในเครื่องหมายคำพูดออก — ตัวละครยกคำพูดของคนอื่นมาเล่าได้
    (เคสจริง: มิฮารุเล่าคำสารภาพของผู้ชาย จึงมี ผม/ครับ อยู่ในบรรทัดของผู้หญิงอย่างถูกต้อง)"""
    return RE_QUOTE.sub(" ", th)


def male_markers(th):
    t = outside_quotes(th)
    return bool(RE_KHRAP.search(t)) or bool(RE_PHOM.search(t))


def female_markers(th):
    return bool(RE_FEMALE_MARK.search(outside_quotes(th)))


# สรรพนามที่ "ล็อกรายตัวละคร" — ผู้ตรวจ TALK_052/056/066 เจอหลุดซ้ำสามสปรินต์
# `check_pronoun_pairs.py` จับไม่ได้เพราะแต่ละคำถูกไวยากรณ์ในตัวเอง ต้องรู้ว่าใครพูดถึงจะรู้ว่าผิด
# ใช้ขอบเขตคำชุดเดียวกับ check_pronoun_pairs.py (กัน ฉันทะ · แก๊ง/แก้/แกล้ง · กูเกิล/ยากูซ่า ฯลฯ)

SELF_LOCK = {
    "yagami": ([RE_CHAN, RE_DICHAN, RE_KU], "ยากามิต้องใช้ \"ผม\" เสมอ"),
}
ADDRESS_LOCK = {
    "yagami": ([RE_KAE, RE_MUENG], "ยากามิห้ามเรียกคู่สนทนาว่า \"แก\"/\"มึง\""),
}


def lock_hits(speaker, th):
    """คืนรายการเหตุผลที่บรรทัดนี้ผิดคำล็อกรายตัวละคร"""
    out = []
    key = (speaker or "").lower()
    t = outside_quotes(th)
    for table in (SELF_LOCK, ADDRESS_LOCK):
        if key in table:
            pats, why = table[key]
            if any(p.search(t) for p in pats):
                out.append(why)
    return out


def load_pairs(path):
    with io.open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("strings", data)


def load_facts():
    """รวมผู้พูดจากทั้งบทเดินเมือง (`talk_speaker`) และบทคัตซีน (`speech_speaker`)

    ถ้าสตริงเดียวกันถูกใช้โดยผู้พูดที่เพศไม่ตรงกัน (line reuse ข้ามฉาก — เกิดจริงในเกมนี้)
    ให้ถือว่าเป็น `dupes` แล้วข้ามไป เพราะคำแปลต้องเป็นกลางเพศอยู่แล้วตาม glossary §7.2
    """
    facts = {}
    with io.open(FACTS, encoding="utf-8") as fh:
        facts.update(json.load(fh))

    if os.path.exists(FACTS_SPEECH):
        with io.open(FACTS_SPEECH, encoding="utf-8") as fh:
            speech = json.load(fh)
        for en, info in speech.items():
            old = facts.get(en)
            if old is None:
                facts[en] = dict(info)
                continue
            # เพศขัดกันระหว่างสองแหล่ง = สตริงถูกใช้ซ้ำหลายปาก -> ข้าม
            if old.get("gender") != info.get("gender"):
                old["dupes"] = old.get("dupes") or ["conflict:%s" % info.get("speaker", "?")]
            elif not old.get("gender") or old.get("gender") == "unknown":
                facts[en] = dict(info)
    return facts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="*", default=[MASTER])
    ap.add_argument("--max", type=int, default=30)
    a = ap.parse_args()

    facts = load_facts()

    for path in a.files:
        pairs = load_pairs(path)
        hits = []
        for en, info in facts.items():
            th = pairs.get(en)
            if not th or info.get("dupes"):
                continue
            g = info.get("gender")
            for why in lock_hits(info.get("speaker"), th):
                hits.append((why, info.get("speaker"), en, th))
            if g == "female" and male_markers(th):
                hits.append(("ผู้พูดหญิงแต่ใช้คำชาย", info.get("speaker"), en, th))
            elif g == "male" and female_markers(th):
                hits.append(("ผู้พูดชายแต่ใช้คำหญิง", info.get("speaker"), en, th))
        print("== %s · %d คู่ · ขัดเพศผู้พูด %d" % (os.path.basename(path), len(pairs), len(hits)))
        for why, sp, en, th in hits[: a.max]:
            print("  [%s] %s" % (sp, why))
            print("    EN:", en.replace("\n", " ")[:84])
            print("    TH:", th.replace("\n", " ")[:84])
        if len(hits) > a.max:
            print("  ... อีก %d" % (len(hits) - a.max))


if __name__ == "__main__":
    main()
