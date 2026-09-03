"""scene_audit.py — ตรวจบรรทัดที่ใช้ "เพศระดับฉาก" เป็นหลักฐานอย่างเดียว

`scene_gender.json` ตัดสินจากทั้งไฟล์ `.msg` ว่าเป็นเพศเดียวล้วนไหม ฉากที่มีหลายคนพูดสลับกัน
บรรทัดของตัวประกอบจึง "ยืมเพศ" จากตัวเอกในฉากเดียวกันได้ (บทเรียน MSG_025 — ถอน "ขอรับ" 58 บรรทัด)

สคริปต์นี้ดึงบรรทัดที่ต้องสงสัยออกมา **พร้อมฉากรอบตัว** เพื่อให้ผู้ตรวจอ่านแล้วชี้ว่าบรรทัดนั้น
เป็นบทของใคร · ไม่ใช่เครื่องมือแก้อัตโนมัติ (ห้ามแก้เป็นชุดด้วย regex)

ใช้: python scripts/scene_audit.py MSG_013 [MSG_019 ...]   -> work/audit/scene_MSG_013.md
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import merge_qc as M
import paths
import thai_pronouns as tp

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

CONTEXT = 4          # บรรทัดก่อน/หลังที่พิมพ์ประกอบ
OUT = paths.PROJECT / "work" / "audit"


def load_rows():
    rows = json.loads((paths.PROJECT / "extracted" / "parallel" / "msg.json")
                      .read_text(encoding="utf-8"))
    by_file = defaultdict(list)
    for r in rows:
        by_file[r["file"]].append(r)
    for v in by_file.values():
        v.sort(key=lambda r: r["line"])
    by_en = defaultdict(list)
    for r in rows:
        by_en[r["en"]].append(r)
    return by_file, by_en


def marker(row):
    """เครื่องหมายเพศของบรรทัดนั้นเอง (จากต้นฉบับญี่ปุ่น)"""
    g = M.ja_gender(row.get("ja") or "")
    return {"male": "♂", "female": "♀"}.get(g, " ")


def audit(name, by_file, by_en):
    done = paths.PROJECT / "translations" / "done" / ("batch_%s.done.json" % name)
    if not done.exists():
        print("ไม่พบ", done.name)
        return
    wl = json.loads((paths.WORKLIST / ("batch_%s.json" % name)).read_text(encoding="utf-8"))
    ref, ctx = wl.get("ref_ja") or {}, M.load_context("batch_%s.json" % name)
    strings = json.loads(done.read_text(encoding="utf-8"))["strings"]

    flagged = []
    for en, th in strings.items():
        info = ctx.get(en) or {}
        if en == th or not M.is_neutral(info) or not tp.POLITE_OLD.search(th):
            continue
        if M.ja_gender(ref.get(en) or info.get("ja") or ""):
            continue                      # มีหลักฐานในบรรทัดเอง = ปลอดภัย
        if M.scene_gender(en):
            flagged.append(en)
    if not flagged:
        print("%s: ไม่มีบรรทัดต้องสงสัย" % name)
        return

    # จัดกลุ่มตามไฟล์ฉาก
    scenes = defaultdict(set)
    for en in flagged:
        for r in by_en.get(en, []):
            scenes[r["file"]].add(r["line"])

    OUT.mkdir(parents=True, exist_ok=True)
    out = ["# %s — บรรทัดที่ใช้เพศระดับฉากอย่างเดียว (%d บรรทัด · %d ฉาก)"
           % (name, len(flagged), len(scenes)), "",
           "⚠ บรรทัดที่ขึ้นต้นด้วย `>>>` คือบรรทัดที่ต้องตัดสิน — ที่เหลือพิมพ์มาให้อ่านบริบท",
           "· `♂`/`♀` = บรรทัดนั้น**เอง**มีเครื่องหมายเพศในต้นฉบับญี่ปุ่น", ""]
    for f in sorted(scenes):
        rows = by_file[f]
        want = scenes[f]
        show = set()
        for ln in want:
            for i in range(ln - CONTEXT, ln + CONTEXT + 1):
                show.add(i)
        out.append("## ฉาก `%s`" % f)
        labels = sorted({l for r in rows for l in (r.get("labels") or [])})
        if labels:
            out.append("ป้ายผู้พูดในไฟล์นี้: %s" % " · ".join(labels))
        out.append("")
        prev = None
        for r in rows:
            if r["line"] not in show:
                continue
            if prev is not None and r["line"] != prev + 1:
                out.append("    …")
            prev = r["line"]
            lab = "/".join(r.get("labels") or []) or "-"
            mark = ">>>" if r["line"] in want else "   "
            out.append("%s [%03d] %s %s" % (mark, r["line"], marker(r), lab))
            out.append("      JA: %s" % (r.get("ja") or "").replace("\n", "⏎"))
            out.append("      EN: %s" % (r.get("en") or "").replace("\n", "⏎"))
            if r["line"] in want:
                th = strings.get(r["en"], "")
                out.append("      TH: %s" % th.replace("\n", "⏎"))
        out.append("")
    dest = OUT / ("scene_%s.md" % name)
    dest.write_text("\n".join(out), encoding="utf-8")
    print("%s: %d บรรทัด · %d ฉาก -> %s" % (name, len(flagged), len(scenes), dest))


def main():
    names = sys.argv[1:]
    if not names:
        print(__doc__)
        return
    by_file, by_en = load_rows()
    for n in names:
        audit(n, by_file, by_en)


if __name__ == "__main__":
    main()
