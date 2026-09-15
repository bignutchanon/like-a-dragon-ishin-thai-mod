#!/usr/bin/env python3
"""ซองตรวจย้อน "สตริงที่ RGG ทิ้งช่อง EN เป็นญี่ปุ่น แต่ทีมเราแปลไทยไว้" (HANDOFF §0.59 ข้อ 2)

ในไฟล์ .msg ภาษาอังกฤษบางฉาก ช่อง EN เป็นข้อความญี่ปุ่นทุกตัวอักษร (EN == JA) — คำแปลไทยของบรรทัด
พวกนี้จึงแปลจากญี่ปุ่นโดยปริยาย ไม่มีต้นฉบับอังกฤษให้เทียบ และยังไม่มีใครตรวจ
วัด 15 ก.ย. 2026: 1,329 แถว · สตริงไม่ซ้ำ 631 · 54 ไฟล์ · หนาที่สุดคือฉากโรงเรียนวัดสามชุดสำเนา

ซองให้ผู้ตรวจอ่าน **ความหมายเทียบญี่ปุ่น** (ไม่ใช่เกลาสำนวน) — ทั้งฉากเรียงบรรทัด บรรทัดเป้าหมายติด `***`
ฉากสำเนา (ชุดสตริงเป้าหมายเป็นเซตย่อยของฉากที่ใส่ไปแล้ว) ข้ามทั้งไฟล์

ผลผู้ตรวจ: work/revise_wave/enja/out/packet_NN.json
  [{"key": "uid…#NNN", "th_new": "…", "problem": "…", "severity": "meaning|nuance"}]
ลง: python scripts/merge_enja_wave.py (lead อ่านก่อน)

ใช้: python scripts/make_enja_packets.py [--per 220]
"""
import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                                   # noqa: E402
from make_gender_packets import DEAD_FILES     # noqa: E402

WAVE = paths.PROJECT / "work" / "revise_wave" / "enja"


def flat(s):
    return (s or "").replace("\r\n", "\\n").replace("\n", "\\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per", type=int, default=220, help="สตริงเป้าหมายต่อซองโดยประมาณ")
    args = ap.parse_args()

    par = json.loads((paths.EXTRACTED / "parallel" / "msg.json").read_text(encoding="utf-8"))
    mt = json.loads(paths.MASTER_TH.read_text(encoding="utf-8"))
    byfile = OrderedDict()
    for r in par:
        if r["file"] in DEAD_FILES:
            continue
        byfile.setdefault(r["file"], []).append(r)

    def is_target(r):
        en = r.get("en") or ""
        return en.strip() and en == r.get("ja") and mt.get(en) and mt[en] != en

    seen, scenes = set(), []
    for f, rows in byfile.items():
        targets = {r["en"] for r in rows if is_target(r)}
        if not targets or targets <= seen:
            continue                    # ไม่มีเป้าหมาย หรือเป็นฉากสำเนาที่ใส่ไปแล้ว
        scenes.append((f, rows, targets - seen))
        seen |= targets

    packets, cur, n = [], [], 0
    for sc in scenes:
        if cur and n + len(sc[2]) > args.per:
            packets.append(cur)
            cur, n = [], 0
        cur.append(sc)
        n += len(sc[2])
    if cur:
        packets.append(cur)

    (WAVE / "in").mkdir(parents=True, exist_ok=True)
    (WAVE / "out").mkdir(exist_ok=True)
    for i, pk in enumerate(packets, 1):
        out, cnt = [], 0
        for f, rows, new in pk:
            out.append("### ไฟล์ฉาก %s (%d บรรทัด · เป้าหมาย %d)" % (f, len(rows), len(new)))
            done = set()
            for r in rows:
                en = r.get("en") or ""
                if not en.strip():
                    continue
                th = mt.get(en, "")
                mark = ""
                if en in new and en not in done:
                    mark, cnt = "  ***", cnt + 1
                    done.add(en)
                labels = [x for x in (r.get("labels") or []) if not x.startswith("Talk_") and x != "dummy"][:3]
                out.append("[%s]%s  ป้าย=%s" % (r["key"], mark, " | ".join(labels)))
                if en != r.get("ja"):
                    out.append("  EN: %s" % flat(en))
                out.append("  JA: %s" % flat(r.get("ja")))
                out.append("  TH: %s" % flat(th))
            out.append("")
        (WAVE / "in" / ("packet_%02d.txt" % i)).write_text("\n".join(out), encoding="utf-8")
        print("packet_%02d  ฉาก %2d  เป้าหมาย %d" % (i, len(pk), cnt))
    print("รวม %d ซอง · ฉาก %d · สตริงเป้าหมาย %d" % (len(packets), len(scenes), len(seen)))


if __name__ == "__main__":
    main()
