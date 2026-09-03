#!/usr/bin/env python3
"""จับคู่ EN↔TH ที่ "สลับคู่กัน" (คำแปลไปติดคีย์ผิด)

ที่มา: ผู้ตรวจ TALK_057 เจอ 6 คู่ในบล็อกเดียวถูกสลับข้ามกัน (คำแปลของอามาเนะไปอยู่กับคีย์ของยากามิ)
`merge_qc` จับไม่ได้เพราะทั้งสองฝั่งเป็นภาษาไทยถูกไวยากรณ์ แค่ผูกกับคีย์ผิดตัว

สัญญาณที่ใช้ (ทั้งหมดคิดจากคู่เดียว ไม่ต้องรู้บริบท):
  Q  = EN เป็นคำถาม (ลงท้าย ?) แต่ TH ไม่ใช่ หรือกลับกัน
  D  = ชุดตัวเลขใน EN กับ TH ไม่ตรงกัน
  L  = อัตราส่วนความยาว TH/EN หลุดช่วงปกติมาก (ใช้เฉพาะสตริงยาวกว่า 25 ตัว)
คู่ที่ติดสัญญาณ **ตั้งแต่ 2 อย่างขึ้นไป** = น่าสงสัยจริง (สัญญาณเดียวมี false positive เยอะ)

ใช้:
    python scripts/check_pair_shuffle.py                    # ตรวจ master_th.json
    python scripts/check_pair_shuffle.py --files a.json b.json
    python scripts/check_pair_shuffle.py --min-signals 1    # ดูกว้างขึ้น
"""
import argparse
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, "translations", "master_th.json")
THAI = re.compile(r"[฀-๿]")
DIGITS = re.compile(r"\d+")
THAI_Q = re.compile(r"ไหม|มั้ย|เหรอ|หรือ|รึ|อะไร|ทำไม|ใคร|ไหน|เมื่อไห?ร่|ยังไง|เท่าไ?ร่?|กี่|ใช่ไหม|ป่ะ|มะ")
TAG = re.compile(r"<[^>]*>|\$\{[^}]*\}|%[sd]|~[^~]*~")


def strip_tags(s):
    return TAG.sub("", s)


def signals(en, th):
    out = []
    e, t = strip_tags(en).strip(), strip_tags(th).strip()
    if not e or not t or not THAI.search(t):
        return out
    # ไทยมักละเครื่องหมาย ? แต่ต้องมีคำแสดงคำถามเสมอ — ใช้คำถามไทยเป็นตัวชี้แทนเครื่องหมาย
    if e.endswith("?") and "?" not in t and not THAI_Q.search(t):
        out.append("Q")
    if not e.endswith("?") and t.endswith("?") and not THAI_Q.search(t):
        out.append("Q")
    if DIGITS.findall(e) != DIGITS.findall(t):
        out.append("D")
    if len(e) > 25:
        ratio = len(t) / len(e)
        if ratio < 0.45 or ratio > 2.4:
            out.append("L")
    return out


def load_pairs(path):
    with io.open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("strings", data) if isinstance(data, dict) else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="*", default=[MASTER])
    ap.add_argument("--min-signals", type=int, default=2)
    ap.add_argument("--max", type=int, default=40)
    a = ap.parse_args()

    total = 0
    for path in a.files:
        pairs = load_pairs(path)
        hits = []
        for en, th in pairs.items():
            sig = signals(en, th)
            if len(sig) >= a.min_signals:
                hits.append((sig, en, th))
        print("== %s · %d คู่ · น่าสงสัย %d" % (os.path.basename(path), len(pairs), len(hits)))
        for sig, en, th in hits[: a.max]:
            print("  [%s] EN: %s" % ("".join(sig), en.replace("\n", " ")[:88]))
            print("      TH: %s" % th.replace("\n", " ")[:88])
        if len(hits) > a.max:
            print("  ... อีก %d คู่ (ใส่ --max)" % (len(hits) - a.max))
        total += len(hits)
    print("รวมน่าสงสัย %d คู่ (เกณฑ์ >= %d สัญญาณ)" % (total, a.min_signals))


if __name__ == "__main__":
    main()
