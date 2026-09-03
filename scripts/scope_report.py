#!/usr/bin/env python3
"""นับขนาดงานแปลจริงของทั้งเกม จากไฟล์ที่แตกมาแล้วทั้งสามชั้น

ชั้นข้อความของ Ishin!:
  1. `.msg`      — บทพูด/คัตซีน          (extracted/text_en/*.json)
  2. ARMP        — UI/ระบบ/ไอเทม/ทักษะ   (extracted/db_en/*.bin.json · คอลัมน์ชนิด 13 = string)
  3. `Game.locres` — UI ที่ UE จัดการเอง  (extracted/locres/Game.en.json)

รายงานทั้ง "ดิบ" และ "ที่ต้องแปลจริง" — ตัวเลขที่เอาไปวางแผนคือตัวหลัง
เกณฑ์ตัดออก เขียนไว้ในค่าคงที่ด้านล่าง ปรับได้และต้องอธิบายได้ทุกข้อ

ใช้: python scripts/scope_report.py [--write]
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                        # noqa: E402

# ---- เกณฑ์ตัดออก (อธิบายได้ทุกข้อ) ----
# เครดิตท้ายเกม: คงอังกฤษตามกติกาข้อ 9 (ชื่อคน/บริษัท) · มี 6 ตารางแยกตามแพลตฟอร์ม
SKIP_TABLES = re.compile(r"^staffroll_", re.I)
# namespace ของ locres ที่ไม่ต้องแปล
SKIP_NS = re.compile(r"^(staffroll|credit|license|kiyaku)", re.I)
# สตริงที่ไม่ใช่ข้อความ: ว่าง · มี control byte (เศษจากตัวสแกน .msg) · ตัวเลข/สัญลักษณ์ล้วน ·
# โทเคนล้วน (เช่น "<Color:8>") · ID แบบ ALLCAPS/snake_case ที่ไม่มีช่องว่าง
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
TOKEN_ONLY = re.compile(r"^(\s|<[^>]*>|\{[^}]*\}|\$\w+)*$")
IDENT_ONLY = re.compile(r"^[A-Z0-9_\-./]+$")


def translatable(s):
    """สตริงนี้ต้องส่งให้นักแปลไหม"""
    if not s or not s.strip():
        return False
    if CONTROL.search(s):
        return False
    if TOKEN_ONLY.match(s):
        return False
    if IDENT_ONLY.match(s.strip()):
        return False
    return bool(re.search(r"[A-Za-z぀-ヿ一-鿿]{2,}", s))


def collect_msg():
    out = Counter()
    files = sorted((paths.EXTRACTED / "text_en").glob("*.json"))
    raw = 0
    for f in files:
        for r in json.loads(f.read_text(encoding="utf-8")):
            raw += 1
            if translatable(r["en"]):
                out[r["en"]] += 1
    return {"layer": ".msg (บทพูด)", "files": len(files), "raw": raw, "uniq": out}


def collect_armp():
    out = Counter()
    raw = skipped = 0
    files = sorted((paths.EXTRACTED / "db_en").glob("*.bin.json"))
    used = 0
    for f in files:
        table = f.name.replace(".bin.json", "")
        if SKIP_TABLES.match(table):
            skipped += 1
            continue
        used += 1
        d = json.loads(f.read_text(encoding="utf-8"))
        text_cols = {c for c, t in (d.get("columnTypes") or {}).items() if t == 13}
        if not text_cols:
            continue
        for k, v in d.items():
            if not k.isdigit() or not isinstance(v, dict):
                continue
            for row in v.values():
                if not isinstance(row, dict):
                    continue
                for col in text_cols:
                    s = row.get(col)
                    if isinstance(s, str):
                        raw += 1
                        if translatable(s):
                            out[s] += 1
    return {"layer": "ARMP db.macan (UI/ระบบ)", "files": used, "raw": raw,
            "uniq": out, "skipped_tables": skipped}


def collect_locres():
    p = paths.EXTRACTED / "locres" / "Game.en.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    S = d["strings"]

    def txt(i):
        s = S[i]
        return s if isinstance(s, str) else str(s)

    out = Counter()
    raw = skipped_ns = 0
    for ns in d["namespaces"]:
        if SKIP_NS.match(ns["ns"]):
            skipped_ns += 1
            continue
        for e in ns["entries"]:
            raw += 1
            s = txt(e["idx"])
            if translatable(s):
                out[s] += 1
    return {"layer": "Game.locres (UI)", "files": 1, "raw": raw,
            "uniq": out, "skipped_ns": skipped_ns}


def bucket(n):
    if n <= 20:
        return "สั้นมาก (≤20)"
    if n <= 60:
        return "สั้น (21-60)"
    if n <= 150:
        return "กลาง (61-150)"
    return "ยาว (>150)"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="เขียนผลลง docs/scope.md")
    a = ap.parse_args()

    layers = [collect_msg(), collect_armp(), collect_locres()]
    lines = []

    def out(s=""):
        print(s)
        lines.append(s)

    out("# ขนาดงานแปล — Like a Dragon: Ishin!")
    out()
    out("| ชั้น | ไฟล์ | สตริงดิบ | ต้องแปล (นับซ้ำ) | **ไม่ซ้ำ** | ตัวอักษรรวม |")
    out("|---|---:|---:|---:|---:|---:|")
    grand = Counter()
    for L in layers:
        u = L["uniq"]
        total = sum(u.values())
        chars = sum(len(s) * c for s, c in u.items())
        out("| %s | %d | %d | %d | **%d** | %d |"
            % (L["layer"], L["files"], L["raw"], total, len(u), chars))
        grand.update(u)
    out("| **รวม (หักซ้ำข้ามชั้นแล้ว)** | | | | **%d** | %d |"
        % (len(grand), sum(len(s) for s in grand)))
    out()

    overlap = sum(1 for s in grand if sum(1 for L in layers if s in L["uniq"]) > 1)
    out("ซ้ำข้ามชั้น (สตริงเดียวกันโผล่มากกว่าหนึ่งชั้น): **%d** รายการ" % overlap)
    out()

    out("## แจกแจงตามความยาว (สตริงไม่ซ้ำทั้งเกม)")
    out()
    b = Counter(bucket(len(s)) for s in grand)
    out("| ช่วงความยาว | จำนวน | สัดส่วน |")
    out("|---|---:|---:|")
    for k in ["สั้นมาก (≤20)", "สั้น (21-60)", "กลาง (61-150)", "ยาว (>150)"]:
        out("| %s | %d | %.0f%% |" % (k, b[k], 100 * b[k] / max(len(grand), 1)))
    out()

    n = len(grand)
    out("## ประมาณการงาน")
    out()
    out("- สตริงไม่ซ้ำที่ต้องแปล: **%s**" % f"{n:,}")
    out("- ตัวอักษรอังกฤษรวม: **%s**" % f"{sum(len(s) for s in grand):,}")
    out("- แบ่ง batch ละ 250 สตริง (ขนาดเดียวกับโปรเจกต์ Lost Judgment) = **%d batch**"
        % -(-n // 250))
    out()
    out("### เทียบกับภาคที่เคยทำ")
    out("Lost Judgment = 68,179 สตริง / 275 batch → ภาคนี้ **%.0f%%** ของ LJ" % (100 * n / 68179))
    out()
    out("### ตัดออกแล้ว")
    for L in layers:
        extra = {k: v for k, v in L.items() if k.startswith("skipped")}
        if extra:
            out("- %s: %s" % (L["layer"], extra))
    out("- เครดิตท้ายเกม (`staffroll_*` 6 ตาราง) คงอังกฤษตามกติกาข้อ 9")
    out("- สตริงที่เป็นโทเคนล้วน / ID / ตัวเลข / เศษจากตัวสแกน `.msg` ถูกกรองออก")

    if a.write:
        p = paths.DOCS / "scope.md"
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("\nเขียนแล้ว: %s" % p)


if __name__ == "__main__":
    main()
