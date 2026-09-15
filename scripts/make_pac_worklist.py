#!/usr/bin/env python3
"""จัดคิวงานแปลของสตริงใน `pac_STID_*.bin` (บทพูดลอยของ NPC · ป้ายปุ่มโต้ตอบ) เป็น batch ซีรีส์ PAC

แยกจาก `make_worklist_ishin.py` โดยตั้งใจ — ตัวนั้น re-chunk ทั้งคลังและทำให้เลข batch เดิมเลื่อน
ตัวนี้เขียนเฉพาะ `translations/worklist/batch_PAC_NNN.*` ในรูปแบบเดียวกันทุกช่อง
(`strings` · `priority` · `ref_ja` + ไฟล์คู่ `.context.json` · `.todo.json`) merge_qc จึงตรวจได้ครบทุกด่าน

ต้นทาง: `extracted/pac_en.json` (`scripts/extract_pac_text.py`) · เอาเฉพาะแถว `translatable`
ที่ยังไม่มีคำแปลใน master_th

คัดออก (อธิบายได้ทุกข้อ):
  - ไฟล์ `pac_STID_TE_*` = ด่านทดสอบของผู้พัฒนา (label `Ｃ会話テスト` · `ターンテスト` · `自動生成会話Ａ`)
  - สตริงที่ไม่ใช่ UTF-8 (label Shift-JIS สองตัวใน KYOTO ที่เหมือนกันทุกภาษา)

priority: label = 3 (ป้ายร้าน/ปุ่ม/ชื่อผู้พูด — ไทยปัจจุบัน) · line = 4 (บทพูด NPC เดินถนน — ยุคบาคุมัตสึ)
เพศ: สตริง pac ไม่มีข้อมูลผู้พูด → neutral ทุกบรรทัด ยกเว้นบรรทัดที่ญี่ปุ่นมีเครื่องหมายเพศในตัว
(`merge_qc.ja_gender`) ซึ่งแนบเป็น `evidence_gender` from=ja_line

ใช้: python scripts/make_pac_worklist.py [--batch-size 200]
"""
import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402
from merge_qc import ja_gender  # noqa: E402

SRC = paths.EXTRACTED / "pac_en.json"
PRIORITY = {"label": 3, "line": 4}
PRIORITY_NAME = {3: "ป้ายใน pac_STID (ป้ายร้าน/ปุ่มโต้ตอบ/ชื่อผู้พูด)",
                 4: "บทพูดลอยของ NPC ใน pac_STID (เดินถนน/ในด่าน)"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=200)
    a = ap.parse_args()

    rows = json.loads(SRC.read_text(encoding="utf-8"))
    master = json.loads(paths.MASTER_TH.read_text(encoding="utf-8"))
    skipped = {"test": 0, "not_utf8": 0, "done": 0}
    groups = {"label": OrderedDict(), "line": OrderedDict()}
    for r in rows:
        if not r["translatable"]:
            continue
        if r["file"].startswith("pac_STID_TE_"):
            skipped["test"] += 1
            continue
        if "ไม่ใช่ UTF-8" in r["why"]:
            skipped["not_utf8"] += 1
            continue
        if r["en"] in master:
            skipped["done"] += 1
            continue
        g = groups[r["kind"]]
        if r["en"] not in g:
            g[r["en"]] = {"ja": r["ja"] or "", "files": [], "occurrences": 0}
        info = g[r["en"]]
        info["occurrences"] += 1
        if r["file"] not in info["files"]:
            info["files"].append(r["file"])

    existing = sorted(paths.WORKLIST.glob("batch_PAC_*.json"))
    if existing:
        print("!! มี batch_PAC อยู่แล้ว %d ไฟล์ — ลบเองก่อนถ้าจะจัดใหม่ (กันเขียนทับงานที่แจกไปแล้ว)" % len(existing))
        return 1

    n = 0
    for kind in ("label", "line"):
        items = list(groups[kind].items())
        for i in range(0, len(items), a.batch_size):
            n += 1
            chunk = items[i:i + a.batch_size]
            name = "batch_PAC_%03d" % n
            pri = PRIORITY[kind]
            batch = OrderedDict([
                ("priority", pri),
                ("priority_name", PRIORITY_NAME[pri]),
                ("sources", sorted({f for _, v in chunk for f in v["files"]})),
                ("strings", OrderedDict((en, "") for en, _ in chunk)),
                ("ref_ja", OrderedDict((en, v["ja"]) for en, v in chunk if v["ja"])),
            ])
            ctx_lines = OrderedDict()
            for en, v in chunk:
                c = OrderedDict([("speakers", []), ("gender", "unknown"), ("neutral", True),
                                 ("why_neutral", "สตริง pac_STID ไม่มีข้อมูลผู้พูดในไฟล์เกม"),
                                 ("chapters", []), ("ja", v["ja"]),
                                 ("occurrences", v["occurrences"]), ("files", v["files"])])
                g = ja_gender(v["ja"]) if kind == "line" else None
                if g:
                    c["evidence_gender"] = {"gender": g, "from": "ja_line",
                                            "why": "เครื่องหมายเพศในต้นฉบับญี่ปุ่นของบรรทัดนี้เอง"}
                ctx_lines[en] = c
            ctx = OrderedDict([
                ("batch", name + ".json"),
                ("readme", "ไฟล์คู่ของ batch — neutral:true = ไม่มีข้อมูลผู้พูด ให้เขียนกลางเพศตาม "
                           "PRONOUN_MATRIX §1.3 · ยกเว้นบรรทัดที่มี evidence_gender (from=ja_line) · "
                           "ช่อง files = ไฟล์ด่านที่สตริงนี้อยู่ (ST_KYOTO = เกียวโต เดินถนน)"),
                ("lines", ctx_lines),
            ])
            todo = OrderedDict([("batch", name + ".json"), ("priority", pri),
                                ("sources", batch["sources"]), ("strings", batch["strings"])])
            for suffix, obj in (("", batch), (".context", ctx), (".todo", todo)):
                (paths.WORKLIST / (name + suffix + ".json")).write_text(
                    json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
            print("%s  priority %d · %s · %d สตริง" % (name, pri, kind, len(chunk)))
    print("ข้าม: ด่านทดสอบ %(test)d · ไม่ใช่ UTF-8 %(not_utf8)d · มีคำแปลแล้ว %(done)d" % skipped)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
