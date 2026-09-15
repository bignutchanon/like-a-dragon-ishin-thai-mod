#!/usr/bin/env python3
"""ด่านตรวจ pac_STID_*.bin (tools/pac.py) — เทียบ **ไบต์ดิบ** กับไฟล์เกมเท่านั้น (บทเรียน LJ-011)

อ่านไฟล์ตรงจาก pakchunk0 (อ่านอย่างเดียว) ทุกภาษาใต้ data/wdr_<lang>/pac/

oracle 1  parse -> rebuild ไม่แก้อะไร == ต้นฉบับ              (ทุกไฟล์ × ทุกภาษา)
oracle 2  parse(EN) -> แทนด้วยของอีกภาษาในไฟล์เดียวกัน -> rebuild == ไฟล์ภาษานั้น
   2a  แทน "สตริง" อย่างเดียว (บรรทัด + label ตามคีย์) + retime_cmds อัตโนมัติ
       → ไม่ผ่านได้โดยชอบธรรม เพราะแต่ละภาษาใส่คำสั่งจังหวะ (`02 09` ฯลฯ) ไม่เท่ากัน
         และบางภาษารวม label ซ้ำเป็นตัวเดียว — สคริปต์แยกสาเหตุให้ทุกบรรทัด
   2b  แทนสตริง + บล็อกคำสั่งของภาษานั้น (+ label/ข้อมูลกลุ่ม ในเรคคอร์ดที่จำนวน label ต่าง)
       → **ต้องผ่านทุกไฟล์** = พิสูจน์ว่าทุกฟิลด์ที่ขึ้นกับความยาว/ตำแหน่งถูกคำนวณใหม่ครบ
   retime  บรรทัดที่คำสั่งตรงกันทุกไบต์ยกเว้นตำแหน่ง: จุดจบบรรทัดหลัง retime ต้องตรง **ทุกบรรทัด**
           (จุดกลางบรรทัดสเกลตามสัดส่วน จึงรายงานเป็นสถิติ ไม่ใช่ความผิด)

ใช้:  python scripts/check_pac_roundtrip.py [--langs ja,de] [--show 8]
ผลที่ต้องได้ก่อนบิลด์: บรรทัดสรุปสุดท้าย "ต่าง 0" ทุกด่าน
"""
import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                              # noqa: E402
from pakfile import PakFile                               # noqa: E402
import pac                                                # noqa: E402

ALL_LANGS = ["en", "ja", "de", "fr", "it", "es", "ko", "cn", "tw"]


def load_lang(pak, lang):
    prefix = paths.PAC_DIR % lang
    return {p[len(prefix):]: pak.read(p) for p in pak.files if p.startswith(prefix + "pac_STID_")}


def pos_of(c):
    return (c[6] << 8) | c[7]


def oracle2(e, t):
    """คืน (ผ่าน 2a, ผ่าน 2b, Counter สาเหตุรายบรรทัด, ตัวอย่าง)"""
    why = collections.Counter()
    samples = {}
    tr = {r.rid: r for r in t.records}
    if [r.rid for r in e.records] != [r.rid for r in t.records]:
        why["record id ไม่ตรงกัน"] += 1
        return False, False, why, samples
    rep = {}
    body_b = []
    struct_diff = False
    for r in e.records:
        rt = tr[r.rid]
        if bool(r.msg) != bool(rt.msg) or r.b != rt.b or (not r.msg and r.a != rt.a):
            why["เรคคอร์ดที่ไม่ใช่ข้อความต่างกัน"] += 1
            body_b.append((r.rid, rt.a, rt.b))
            continue
        if not r.msg:
            body_b.append((r.rid, r.a, r.b))
            continue
        m, n = r.msg, rt.msg
        for i, (a, b) in enumerate(zip(m.lines, n.lines)):
            if a != b:
                rep[e.key(r.rid, "line", i)] = pac._dec(b)
        same_labels = len(m.labels) == len(n.labels)
        if same_labels:
            for i, (a, b) in enumerate(zip(m.labels, n.labels)):
                if a != b:
                    rep[e.key(r.rid, "label", i)] = pac._dec(b)
        else:
            struct_diff = True
            why["label รวมซ้ำ (จำนวน label ต่าง · ข้อมูลกลุ่มอ้างดัชนีใหม่)"] += 1
            samples.setdefault("label", "%08x %s -> %s" % (
                r.rid, [pac._dec(x) for x in m.labels], [pac._dec(x) for x in n.labels]))
        body_b.append((r.rid, m.build(n.lines, n.cmds, n.labels,
                                      None if same_labels else n.gdata), r.b))
        # ---- สาเหตุรายบรรทัดของ 2a ----
        for i, (c, tc) in enumerate(zip(m.cmds, n.cmds)):
            if len(c) != len(tc):
                why["จำนวนคำสั่งต่าง (ภาษานั้นใส่จังหวะเอง)"] += 1
                continue
            if [x[:6] + x[8:] for x in c] != [x[:6] + x[8:] for x in tc]:
                why["ไบต์คำสั่งต่างนอกช่องตำแหน่ง"] += 1
                continue
            if m.lines[i] == n.lines[i]:
                why["retime ตรงทุกไบต์" if c == tc else "ตำแหน่งต่างทั้งที่สตริงเหมือนกัน"] += 1
                continue
            old, new = pac._dec(m.lines[i]), pac._dec(n.lines[i])
            got = pac.retime_cmds(c, old, new)
            if got == tc:
                why["retime ตรงทุกไบต์"] += 1
                continue
            od, nd = pac.disp_chars(old), pac.disp_chars(new)
            end_bad = any(pos_of(x) >= od and pos_of(y) != nd for x, y in zip(c, tc) if pos_of(x))
            if end_bad:
                why["!! retime จุดจบบรรทัดผิด"] += 1
                samples.setdefault("end", "%08x#%d %r -> %r %s vs %s" % (
                    r.rid, i, old[:30], new[:30], [pos_of(x) for x in got], [pos_of(x) for x in tc]))
            else:
                why["retime จุดจบตรง · จุดกลางบรรทัดประมาณ"] += 1
    out_a = None if struct_diff else e.rebuild(rep)
    out_b = pac.PacFile.assemble(body_b)
    return out_a == t.raw, out_b == t.raw, why, samples


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", default=",".join(ALL_LANGS))
    ap.add_argument("--show", type=int, default=6)
    a = ap.parse_args()
    langs = [x for x in a.langs.split(",") if x]
    if "en" not in langs:
        langs.insert(0, "en")

    pak = PakFile(paths.PAK_MAIN)
    data = {lang: load_lang(pak, lang) for lang in langs}
    names = sorted(data["en"])
    print("ไฟล์ EN %d · ภาษา %s" % (len(names), " ".join(langs)))

    # ---- oracle 1 ----
    print("\n[oracle 1] parse -> rebuild ไม่แก้ == ต้นฉบับ")
    o1_bad = 0
    for lang in langs:
        same = diff = err = recerr = 0
        bad = []
        for name, raw in sorted(data[lang].items()):
            try:
                pf = pac.PacFile(raw, name)
            except pac.PacFormatError as ex:
                err += 1
                bad.append("%s: อ่านไม่ได้ (%s)" % (name, ex))
                continue
            recerr += len(pf.errors)
            if pf.errors:
                bad.append("%s: เรคคอร์ดอ่านไม่ได้ %s" % (name, pf.errors[:2]))
            if pf.rebuild() == raw:
                same += 1
            else:
                diff += 1
                bad.append("%s: ไบต์ต่าง" % name)
        o1_bad += diff + err + recerr
        print("  %-3s ตรวจ %3d ไฟล์ · เหมือนเดิม %3d · ต่าง %d · อ่านไม่ได้ %d · เรคคอร์ดอ่านไม่ได้ %d"
              % (lang, len(data[lang]), same, diff, err, recerr))
        for line in bad[:a.show]:
            print("      " + line)

    # ---- oracle 2 ----
    print("\n[oracle 2] EN -> ภาษาอื่น (ไฟล์เดียวกัน)")
    en = {n: pac.PacFile(data["en"][n], n) for n in names}
    o2b_bad = end_bad = 0
    total_why = collections.Counter()
    for lang in langs:
        if lang == "en":
            continue
        pa = pb = 0
        why_l = collections.Counter()
        fails, samples = [], {}
        for n in names:
            if n not in data[lang]:
                fails.append("%s: ไม่มีในภาษานี้" % n)
                continue
            ok_a, ok_b, why, smp = oracle2(en[n], pac.PacFile(data[lang][n], n))
            pa += ok_a
            pb += ok_b
            why_l.update(why)
            for k, v in smp.items():
                samples.setdefault(k, "%s %s" % (n, v))
            if not ok_b:
                fails.append("%s: 2b ไม่ผ่าน" % n)
        o2b_bad += len(names) - pb
        end_bad += why_l["!! retime จุดจบบรรทัดผิด"]
        total_why.update(why_l)
        print("  %-3s 2a(สตริงล้วน) ผ่าน %3d/%d · 2b(สตริง+คำสั่ง) ผ่าน %3d/%d"
              % (lang, pa, len(names), pb, len(names)))
        for k, v in sorted(why_l.items()):
            print("        %6d  %s" % (v, k))
        for k, v in samples.items():
            print("        ตัวอย่าง[%s] %s" % (k, v[:200]))
        for line in fails[:a.show]:
            print("      " + line)

    ok = o1_bad == 0 and o2b_bad == 0 and end_bad == 0
    print("\nสรุป: oracle1 ต่าง %d · oracle2b ต่าง %d · retime จุดจบผิด %d  ->  %s"
          % (o1_bad, o2b_bad, end_bad, "ผ่าน (ต่าง 0)" if ok else "ไม่ผ่าน"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
