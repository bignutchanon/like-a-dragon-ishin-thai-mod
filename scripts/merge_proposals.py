#!/usr/bin/env python3
"""ตรวจ + ลงข้อเสนอแก้คำแปลแบบรายการ (15 ก.ย. 2026) — คลื่น EN=JA และคลื่นมุกทายคำ

ข้อมูลเข้า (ชุดใดชุดหนึ่ง):
  --wave enja      work/revise_wave/enja/out/packet_*.json  [{key, th_new, problem, severity}]
  --wave wordplay  work/wordplay/proposals.json              [{key, en, th_old, th_new, why}]
    (key = "uid…#NNN" หรือ "label:<uid>:<label EN>")

ด่านเครื่อง (ตกด่าน = ไม่ลง ไม่ว่า lead จะรับหรือไม่):
  1. หา EN ของคีย์ได้ และ EN มีคำแปลใน master
  2. th_old (ถ้าให้มา) ต้องเท่าคำแปลปัจจุบัน (ไม่นับช่องว่าง) — กันเขียนทับงานที่ลงทีหลัง
  3. จำนวนขึ้นบรรทัด · แท็ก <…> เท่าเดิม · th_new ต่างจากเดิม
  4. คำลงท้ายบอกเพศ (ขอรับ · เจ้าค่ะ/เจ้าคะ · จ๊ะ/จ้ะ) ต้องเท่าเดิม · ห้ามคำภาคปัจจุบันใหม่ (ผม/คุณ/ครับ/ค่ะ)
  5. สตริงเดียวกันถูกเสนอสองแบบ = ขัดกัน ส่ง lead

ขั้น lead: รายงาน `<wave>/review.md` → lead เขียน `<wave>/lead_accept.json` {"คีย์": true | "ข้อความที่ lead แก้"}
ลง: --apply (เฉพาะคีย์ที่ lead รับ) แล้วต่อด้วย python scripts/merge_qc.py

ใช้: python scripts/merge_proposals.py --wave enja [--apply]
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                      # noqa: E402
import thai_pronouns as tp        # noqa: E402
import merge_revise_wave as RW    # noqa: E402

WAVES = {
    "enja": (paths.PROJECT / "work" / "revise_wave" / "enja", "out/packet_*.json"),
    "wordplay": (paths.PROJECT / "work" / "wordplay", "proposals.json"),
}
TAG_RE = re.compile(r"<[^>]*>")
ENDINGS = (tp.RE_KHORAP, tp.RE_CHAOKHA, tp.FEM_CASUAL)


def endings(s):
    return tuple(len(rx.findall(s)) for rx in ENDINGS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", choices=sorted(WAVES), required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    wave, pattern = WAVES[args.wave]

    par = json.loads((paths.EXTRACTED / "parallel" / "msg.json").read_text(encoding="utf-8"))
    en_of = {r["key"]: r.get("en") or "" for r in par}
    ja_of = {r["key"]: r.get("ja") or "" for r in par}
    master = json.loads(paths.MASTER_TH.read_text(encoding="utf-8"))

    items = []
    for p in sorted(wave.glob(pattern)):
        if ".part" in p.name:
            continue
        for it in json.loads(p.read_text(encoding="utf-8")):
            items.append((p.name, it))

    ok, bad, stats = [], [], Counter()
    for src, it in items:
        key, th_new = it.get("key") or "", it.get("th_new") or ""
        en = it.get("en") or (key.split(":", 2)[2] if key.startswith("label:") else en_of.get(key, ""))
        old = master.get(en)
        why = None
        if not en or old is None:
            why = "หา EN/คำแปลไม่ได้"
        elif it.get("th_old") is not None and RW.norm(it["th_old"]) != RW.norm(old):
            why = "th_old ไม่ตรงคำแปลปัจจุบัน"
        elif th_new.count("\n") != old.count("\n"):
            why = "จำนวนขึ้นบรรทัดเปลี่ยน"
        elif sorted(TAG_RE.findall(th_new)) != sorted(TAG_RE.findall(old)):
            why = "แท็กไม่ตรง"
        elif RW.norm(th_new) == RW.norm(old):
            why = "เท่าคำแปลเดิม"
        elif endings(th_new) != endings(old):
            why = "จำนวนคำลงท้ายบอกเพศเปลี่ยน"
        elif tp.MODERN_SPEECH.findall(th_new) and not tp.MODERN_SPEECH.findall(old):
            why = "ใส่คำภาคปัจจุบัน"
        if why:
            bad.append((src, key, why))
            stats["ตก"] += 1
        else:
            ok.append((src, key, en, old, th_new, it))
            stats["ผ่าน"] += 1

    by_en = defaultdict(list)
    for row in ok:
        by_en[row[2]].append(row)
    conflict = {en for en, rows in by_en.items() if len({RW.norm(r[4]) for r in rows}) > 1}

    with (wave / "review.md").open("w", encoding="utf-8") as fh:
        fh.write("# ข้อเสนอคลื่น %s — ผ่านด่านเครื่อง %d · ตก %d · ขัดกัน %d สตริง\n\n"
                 % (args.wave, len(ok), len(bad), len(conflict)))
        for src, key, en, old, th_new, it in ok:
            fh.write("- `%s` (%s)%s %s\n  - EN: %s\n  - JA: %s\n  - เดิม: %s\n  - เสนอ: %s\n  - เหตุผล: %s\n"
                     % (key, src, " ⚠ขัดกัน" if en in conflict else "", it.get("severity", ""),
                        RW.flat(en), RW.flat(ja_of.get(key, "")), RW.flat(old), RW.flat(th_new),
                        RW.flat(it.get("problem") or it.get("why") or "")))
        fh.write("\n## ตกด่านเครื่อง\n\n")
        for src, key, why in bad:
            fh.write("- %s `%s` — %s\n" % (src, key, why))
    print(dict(stats), "ขัดกัน", len(conflict), "-> %s" % (wave / "review.md"))

    if args.apply:
        acc = json.loads((wave / "lead_accept.json").read_text(encoding="utf-8"))
        take = {}
        for src, key, en, old, th_new, it in ok:
            v = acc.get(key)
            if v is True and en not in conflict:
                take[en] = th_new
            elif isinstance(v, str):
                if v.count("\n") != old.count("\n") or endings(v) != endings(old):
                    print("!! ข้อความที่ lead แก้ตกด่าน: %s" % key)
                    continue
                take[en] = v
        nf, nk = RW.apply_to_done(take)
        print("ลง done %d ไฟล์ · %d คีย์ (%d สตริง) -> ต่อด้วย python scripts/merge_qc.py" % (nf, nk, len(take)))


if __name__ == "__main__":
    main()
