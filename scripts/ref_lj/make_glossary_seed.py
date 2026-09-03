#!/usr/bin/env python3
"""สร้าง "ร่าง glossary" ของ Lost Judgment จากไฟล์เกมจริง + คำที่ภาคก่อนล็อกไว้แล้ว

ทำไมต้องมี: glossary ของภาคนี้ต้องครอบชื่อสถานที่/ร้าน/บท/คดี/ทักษะ ~2,000 รายการ
ถ้าให้ทีมแปลตั้งเองรายคน จะได้คำไม่ตรงกันทั้งเกม — แต่ถ้าให้ lead นั่งพิมพ์เองก็ช้าเกิน
สคริปต์นี้จึงทำ **ร่าง** ให้: ดึงรายการจริงจากเกม แล้ว *เติมคำไทยอัตโนมัติเฉพาะรายการที่
ภาคก่อนเคยล็อกไว้ตรงตัวอักษร* (K3 > Gaiden > Y8 > Y7 > Judgment) — ที่เหลือปล่อยว่างให้ lead ตัดสิน

⚠ ไม่มีการทับศัพท์อัตโนมัติ: คำที่ไม่เคยมีภาคไหนล็อก จะขึ้น "⏳" ไม่ใช่คำเดา

แหล่งคำล็อก:
  - translations/glossary.md ของ K3 / Gaiden / Y8 / Judgment  (บรรทัดรูป "EN → ไทย" และตาราง "| EN | ไทย |")
  - docs/reference/glossary_*.md ของ K3 (สรุปคำล็อกของภาคเก่า)
  - translations/tm_judgment.json (คู่ EN→TH ทั้งเกมของ Judgment — ใช้เฉพาะ string สั้นที่ตรงเป๊ะ)

ผลลัพธ์:
  translations/glossary_seed.json   {หมวด: [{en, th, source, id}]}
  translations/glossary_seed.md     ตารางให้ lead ไล่เคาะ (⏳ = ยังไม่มีใครล็อก)

ใช้:  python scripts/make_glossary_seed.py [--write]
"""
import argparse
import collections
import io
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

FACTS = paths.EXTRACTED / "facts"
OUT_JSON = paths.TRANSLATIONS / "glossary_seed.json"
OUT_MD = paths.TRANSLATIONS / "glossary_seed.md"

# ลำดับความน่าเชื่อของคำล็อก (ตัวแรกที่มีคำชนะ) ตาม CLAUDE.md: K3 > Gaiden > Y8 > Y7 > Judgment
GLOSSARY_SOURCES = [
    ("k3", paths.K3_PROJECT / "translations" / "glossary.md"),
    ("gaiden", paths.GAIDEN_PROJECT / "translations" / "glossary.md"),
    ("gaiden-ref", paths.K3_PROJECT / "docs" / "reference" / "glossary_gaiden.md"),
    ("y8", paths.Y8_PROJECT / "translations" / "glossary.md"),
    ("y8-ref", paths.K3_PROJECT / "docs" / "reference" / "glossary_y8.md"),
    ("y7-ref", paths.K3_PROJECT / "docs" / "reference" / "glossary_y7.md"),
    ("judgment", paths.JUDGMENT_PROJECT / "translations" / "glossary.md"),
]

THAI_RE = re.compile(r"[฀-๿]")
ARROW_RE = re.compile(r"^\s*[-*•]?\s*\*{0,2}([^|→]{2,80}?)\*{0,2}\s*→\s*\*{0,2}([^|→]{1,80}?)\*{0,2}\s*$")
ROW_RE = re.compile(r"^\|\s*`?([^|`]{2,80}?)`?\s*\|\s*([^|]{1,80}?)\s*\|")


def clean_en(s):
    s = s.strip().strip("`*").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def load_locked():
    """คืน {EN(lower): (ไทย, ที่มา)} จาก glossary ของภาคก่อน"""
    locked = {}
    for label, path in GLOSSARY_SOURCES:
        if not path.exists():
            print("!! ไม่พบ glossary: %s (%s)" % (label, path))
            continue
        n = 0
        for line in io.open(path, encoding="utf-8"):
            for rx in (ARROW_RE, ROW_RE):
                m = rx.match(line)
                if not m:
                    continue
                en, th = clean_en(m.group(1)), m.group(2).strip().strip("*").strip()
                if not en or not th or THAI_RE.search(en) or not THAI_RE.search(th):
                    continue
                if len(en) < 2 or en.lower() in ("en", "ไทย", "th"):
                    continue
                th = re.sub(r"\s*\(.*$", "", th).strip()      # ตัดหมายเหตุท้ายคำ
                th = th.strip("* ").strip()                   # ตัด ** ของ markdown ที่เหลือค้าง
                if not th or len(th) > 60:
                    continue
                if en.lower() not in locked:
                    locked[en.lower()] = (th, label)
                    n += 1
                break
        print("คำล็อกจาก %-10s +%d (รวม %d)" % (label, n, len(locked)))
    return locked


# TM ของภาคก่อน (คำแปลที่ ship แล้ว) — ใช้เป็น "คำเสนอ" สำหรับชื่อสั้นที่ตรงตัวอักษรเป๊ะ
# ลำดับเดียวกับ glossary: K3 > Gaiden > Y8 > Y7 > Judgment
# Y7/Y8 สำคัญเป็นพิเศษกับภาคนี้เพราะแผนที่ **อิจินโจ** เป็นชุดเดียวกัน (ชื่อถนน/ร้านซ้ำทั้งเมือง)
TM_SOURCES = [
    ("k3", paths.K3_PROJECT / "translations" / "master_th.json"),
    ("gaiden", paths.GAIDEN_PROJECT / "translations" / "master_th.json"),
    ("y8", paths.Y8_PROJECT / "translations" / "master_th.json"),
    ("y7", Path("D:/Projects/yakuza-7-like-a-dragon-thai/translations/master_th.json")),
    ("judgment", paths.TM_JUDGMENT),
]


def load_tm_short(maxlen=40):
    """คู่ EN→TH 'ชื่อสั้น' จาก TM ของภาคก่อน — คืน {en(lower): (ไทย, ที่มา)}"""
    out = {}
    for label, p in TM_SOURCES:
        if not p.exists():
            print("!! ไม่พบ TM: %s (%s)" % (label, p))
            continue
        tm = json.load(io.open(p, encoding="utf-8"))
        n = 0
        for en, th in tm.items():
            if not isinstance(th, str) or not th.strip():
                continue
            if len(en) <= maxlen and "\n" not in en and THAI_RE.search(th):
                k = en.lower()
                if k not in out:
                    out[k] = (th.strip(), label)
                    n += 1
        print("คู่ชื่อสั้นจาก TM %-9s +%s (รวม %s)" % (label, format(n, ","), format(len(out), ",")))
    return out


def facts(name):
    p = FACTS / (name + ".json")
    if not p.exists():
        return []
    return json.load(io.open(p, encoding="utf-8"))


def as_items(data, key="name"):
    out = []
    if isinstance(data, list):
        for r in data:
            if isinstance(r, dict):
                v = r.get(key) or r.get("title") or r.get("en") or ""
                if v:
                    out.append((r.get("id") or "", v))
            elif isinstance(r, str):
                out.append(("", r))
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str):
                out.append((k, v))
            elif isinstance(v, dict):
                nm = v.get("name") or v.get("title") or ""
                if nm:
                    out.append((k, nm))
    return out


CATEGORIES = [
    ("สถานที่ (คามุโรโจ)", lambda i, n: i.startswith("k_"), "places"),
    ("สถานที่ (อิจินโจ/โยโกฮาม่า)", lambda i, n: i.startswith("y_"), "places"),
    ("สถานที่ (อื่น ๆ)", lambda i, n: not i.startswith(("k_", "y_")), "places"),
    ("ร้านค้า", lambda i, n: True, "shops"),
    ("บท (chapter)", lambda i, n: True, "chapters"),
    ("คดี/เนื้อเรื่องย่อย", lambda i, n: True, "scenario_summary"),
    ("ทักษะ/สกิล", lambda i, n: True, "skills"),
    ("ไอเท็ม", lambda i, n: True, "items"),
    ("หมวดสะสม (completion)", lambda i, n: True, "complete_group"),
    ("หัวข้อช่วยเหลือ (help)", lambda i, n: True, "help"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    locked = load_locked()
    tm = load_tm_short()

    seed = collections.OrderedDict()
    stats = collections.Counter()
    for title, pred, src in CATEGORIES:
        items = [(i, n) for i, n in as_items(facts(src)) if pred(i, n)]
        seen, rows = set(), []
        for i, n in items:
            if n in seen:
                continue
            seen.add(n)
            th, source = locked.get(n.lower(), (None, None))
            if not th and n.lower() in tm:
                th, source = tm[n.lower()][0], "tm-%s(เสนอ)" % tm[n.lower()][1]
            rows.append({"id": i, "en": n, "th": th or "", "source": source or ""})
            stats[title + ("/locked" if th else "/⏳")] += 1
        seed[title] = rows

    total = sum(len(v) for v in seed.values())
    hit = sum(1 for v in seed.values() for r in v if r["th"])
    print("รายการทั้งหมด %d · มีคำจากภาคก่อน %d (%.0f%%)" % (total, hit, 100.0 * hit / max(total, 1)))
    for k in sorted(stats):
        print("   %-40s %d" % (k, stats[k]))

    if not a.write:
        print("(ใส่ --write เพื่อเขียนไฟล์)")
        return 0

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT_JSON, "w", encoding="utf-8", newline="\n").write(
        json.dumps(seed, ensure_ascii=False, indent=1) + "\n")

    L = ["# Glossary Seed — Lost Judgment (ร่างอัตโนมัติ)", "",
         "> สร้างด้วย `python scripts/make_glossary_seed.py --write` · ข้อมูลดิบ: `translations/glossary_seed.json`",
         "",
         "ทุกรายการในไฟล์นี้ **มีอยู่จริงในไฟล์เกม** (`extracted/facts/*.json`)",
         "ช่อง \"ไทย\" ที่มีคำแล้ว = ภาคก่อนล็อกไว้ตรงตัวอักษร (ที่มาระบุในช่องถัดไป) → **ใช้ตามนั้น ห้ามตั้งใหม่**",
         "ช่องว่าง = ยังไม่มีใครล็อก → lead ตัดสินก่อนเปิด sprint (ห้ามนักแปลตั้งเอง ให้จดใน `new_names` ของ batch)",
         "",
         "| หมวด | รายการ | มีคำล็อกแล้ว |", "|---|---|---|"]
    for title, rows in seed.items():
        L.append("| %s | %d | %d |" % (title, len(rows), sum(1 for r in rows if r["th"])))
    for title, rows in seed.items():
        L += ["", "## %s (%d)" % (title, len(rows)), "",
              "| EN | ไทย | ที่มา | id ในเกม |", "|---|---|---|---|"]
        for r in rows:
            L.append("| %s | %s | %s | `%s` |"
                     % (r["en"].replace("|", "\\|"), r["th"] or "⏳", r["source"], r["id"]))
    io.open(OUT_MD, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("เขียน %s\nเขียน %s" % (OUT_JSON, OUT_MD))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
