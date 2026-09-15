#!/usr/bin/env python3
"""ตรวจผลคลื่นเกลาบทพูดทั้งเกม (sprint 22) — ด่านเครื่องก่อนสายตาผู้ยืนยัน

สี่งานในซองเดียว (บรีฟ `work/revise_wave/polish/BRIEF.md`):
  D polish       เกลาสำนวน          -> ด่านในไฟล์นี้ แล้ว **ต้องผ่านผู้ยืนยัน (verdict) ก่อนลง done**
  A gender_fix   คำลงท้ายบอกเพศ      -> ด่านเดิมของ merge_revise_wave.check_gender (add/swap รับอัตโนมัติ)
  B weird        ความหมายผิด         -> รายงานให้ lead เลือก (weird_accept.json)
  C gender_wrong ป้ายเพศผิด           -> รายงาน

ทำไมงาน D ต้องมีผู้ยืนยันอีกชั้น: §0.54 วัดไว้ว่างาน "เสนอคำแปล" ของ agent ผิด 13/40 และงานเกลา
ไม่มีหลักฐานที่เครื่องตรวจได้ (ต่างจากงาน A ที่ยก ja_quote มาเช็กได้) ด่านเครื่องจึงตัดได้แค่สิ่งที่ผิดกฎแน่ ๆ

ด่านเครื่องของงาน D:
  1. คีย์อยู่ในซองของตัวเอง · `kind` อยู่ในรายการ · `th_new` ต่างจากเดิม (ไม่นับช่องว่าง)
  2. จำนวนขึ้นบรรทัด · แท็กทุกตัว เท่าคำแปลเดิม
  3. `merge_qc.check_pair` ต้องไม่ตก (N T C P M H)
  4. จำนวนคำลงท้ายบอกเพศ (ขอรับ · เจ้าค่ะ/เจ้าคะ · จ๊ะ/จ้ะ) **เพิ่มไม่ได้** — เป็นงาน A
     ลดลง = รอ lead (ยกเว้น kind=gender_ending บนบรรทัดที่ซองติดธง)
  5. คำยืมสมัยใหม่ใหม่ = ตก
  6. ยาวเกิน 1.25 เท่าของเดิม + 4 ตัวอักษร = ตก
  7. เพิ่มสรรพนามชนิดที่บรรทัดเดิมไม่มี · ชื่อ/สถานที่ล็อกหายไป · สตริงใช้ร่วมหลายฉาก = รอ lead

ใช้:
  python scripts/merge_polish_wave.py --packet 07      # ผู้ตรวจรันเช็กซองตัวเอง (ไม่เขียนอะไร)
  python scripts/merge_polish_wave.py                  # ตรวจทุกซอง + เขียนรายงาน + ไฟล์ให้ผู้ยืนยัน
  python scripts/merge_polish_wave.py --apply          # ลง done: A(add/swap) + D ที่ผู้ยืนยันรับ
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
import merge_qc as M              # noqa: E402
import thai_pronouns as tp        # noqa: E402
import merge_revise_wave as RW    # noqa: E402
import make_revise_packets as R   # noqa: E402

WAVE = paths.PROJECT / "work" / "revise_wave" / "polish"
IN, OUT, VERDICT = WAVE / "in", WAVE / "out", WAVE / "verdict"
KINDS = ("typo", "stiff", "tone", "register", "consistency", "unclear", "gender_ending")
# ป้ายของตัวละครหญิงที่ scene_gender ตีเป็นชาย — apply ไม่ลง ขอรับ ให้บรรทัดที่ติดป้ายเหล่านี้
FEMALE_LABEL = re.compile(r"\b(oryo|haruka|otose|omitsu|sumire|ikumatsu|okami|akari|yae)", re.I)
# คีย์ที่ lead อ่านแล้วตัดทิ้ง (ทุกงาน) — {"คีย์บรรทัด": "เหตุผล"} · apply ข้ามให้
LEAD_DROP = WAVE / "lead_drop.json"
GENDER_ENDINGS = (tp.RE_KHORAP, tp.RE_CHAOKHA, tp.FEM_CASUAL)
PRONOUNS = {"ข้า": tp.RE_KHA_SELF, "กระผม": tp.RE_KRAPHOM, "ท่าน": tp.RE_THAN, "เจ้า": tp.RE_CHAO,
            "นาย": tp.RE_NAI, "กู": tp.RE_KU, "มึง": tp.RE_MUENG, "แก": tp.RE_KAE}


def load_locks():
    """รูปไทยของชื่อคน/สถานที่ที่ล็อกแล้ว — ยาวไปสั้น (ถ้าชื่อเต็มหาย ไม่ต้องรายงานชื่อสั้นซ้ำ)"""
    out = set()
    n = json.loads((paths.TRANSLATIONS / "name_locks.json").read_text(encoding="utf-8"))
    out |= set(n.get("full", {}).values()) | set(n.get("short", {}).values())
    p = json.loads((paths.TRANSLATIONS / "place_locks.json").read_text(encoding="utf-8"))
    out |= set(p.get("places", {}).values())
    return sorted((RW.norm(v) for v in out if len(RW.norm(v)) >= 3), key=len, reverse=True)


def load_packets(only=None):
    lines, owner = {}, {}
    for p in sorted(IN.glob("packet_*.json")):
        if only and p.stem != only:
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        for s in data["scenes"]:
            for l in s["lines"]:
                l["_file"] = s["file"]
                lines[l["key"]] = l
                owner[l["key"]] = p.stem
    return lines, owner


def ending_count(s):
    return sum(len(r.findall(s)) for r in GENDER_ENDINGS)


def same_newlines(th_new, en):
    """ใช้รูปจุดขึ้นบรรทัดของต้นฉบับ — ผู้ตรวจเขียน \\n ใน JSON แต่ต้นฉบับบางบรรทัดเป็น CRLF"""
    t = th_new.replace("\r\n", "\n")
    return t.replace("\n", "\r\n") if "\r\n" in en else t


def check_polish(item, line, locks):
    """คืน (สถานะ, เหตุผล) · สถานะ = "reject" | "review" | "ok" """
    kind = item.get("kind")
    th, en, ja = line["th"], line["en"], line.get("ja") or ""
    th_new = item.get("th_new")
    if kind not in KINDS:
        return "reject", "kind %r ไม่อยู่ในรายการ" % (kind,)
    if not isinstance(th_new, str) or not th_new.strip():
        return "reject", "th_new ว่าง"
    th_new = same_newlines(th_new, en)
    item["th_new"] = th_new
    if RW.norm(th_new) == RW.norm(th):
        return "reject", "th_new เท่าของเดิม (ต่างแค่ช่องว่าง)"
    if th_new.count("\n") != th.count("\n"):
        return "reject", "จำนวนขึ้นบรรทัดเปลี่ยน (%d -> %d)" % (th.count("\n"), th_new.count("\n"))
    if Counter(M.TAG_RE.findall(th_new)) != Counter(M.TAG_RE.findall(th)):
        return "reject", "แท็กไม่เท่าคำแปลเดิม"
    fails, _ = M.check_pair(en, th_new, ja=ja, era=True, neutral=False)
    if fails:
        return "reject", "ด่าน merge_qc: " + " | ".join(fails)
    loan = set(tp.modern_loanwords(th_new)) - set(tp.modern_loanwords(th))
    if loan:
        return "reject", "คำยืมสมัยใหม่ " + " ".join(sorted(loan))
    if len(RW.norm(th_new)) > len(RW.norm(th)) * 1.25 + 4:
        return "reject", "ยาวเกิน (%d -> %d ตัวอักษร)" % (len(RW.norm(th)), len(RW.norm(th_new)))
    e_old, e_new = ending_count(th), ending_count(th_new)
    review = []
    if kind == "gender_ending":
        if line.get("flag") != "ending_gender_conflict":
            return "reject", "gender_ending ใช้ได้เฉพาะบรรทัดที่ซองติดธงคำลงท้ายขัดเพศ"
        review.append("แก้คำลงท้ายตามเพศ")
    elif e_new > e_old:
        return "reject", "เพิ่มคำลงท้ายบอกเพศ (%d -> %d) = งาน A" % (e_old, e_new)
    elif e_new < e_old:
        review.append("คำลงท้ายบอกเพศหายไป (%d -> %d)" % (e_old, e_new))
    added = [k for k, r in PRONOUNS.items() if r.search(th_new) and not r.search(th)]
    if added:
        review.append("สรรพนามใหม่ " + " ".join(added))
    a, b = RW.norm(th), RW.norm(th_new)
    lost = [v for v in locks if v in a and v not in b]
    if lost:
        review.append("ชื่อล็อกหาย " + " ".join(lost[:3]))
    if line.get("shared"):
        review.append("ใช้ร่วม %d ฉาก" % line["shared"])
    return ("review", " · ".join(review)) if review else ("ok", "")


def run(only=None):
    lines, owner = load_packets(only)
    locks = load_locks()
    stats = Counter()
    rejects, polish, genders, weird, gwrong = [], [], [], [], []
    outs = sorted(p for p in OUT.glob("packet_*.json") if ".part" not in p.name)
    if only:
        outs = [p for p in outs if p.stem == only]
    for p in outs:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            rejects.append((p.stem, "-", "อ่าน JSON ไม่ได้: %s" % e))
            continue
        stats["ซอง"] += 1
        nl = sum(1 for k, o in owner.items() if o == p.stem)
        if data.get("lines_read") != nl:
            rejects.append((p.stem, "-", "lines_read=%r แต่ซองมี %d บรรทัด" % (data.get("lines_read"), nl)))

        def mine(item, task):
            key = item.get("key")
            if key not in lines:
                rejects.append((p.stem, key, "%s: ไม่พบคีย์นี้ในซองใด" % task))
                return None
            if owner[key] != p.stem:
                rejects.append((p.stem, key, "%s: คีย์นี้ไม่ได้อยู่ในซองของตัวเอง" % task))
                return None
            return lines[key]

        for item in data.get("polish") or []:
            stats["D เสนอ"] += 1
            line = mine(item, "D")
            if line is None:
                continue
            st, why = check_polish(item, line, locks)
            if st == "reject":
                rejects.append((p.stem, item.get("key"), "D: " + why))
                continue
            stats["D " + st] += 1
            polish.append((p.stem, line, item, st, why))
        for item in data.get("gender_fix") or []:
            stats["A เสนอ"] += 1
            line = mine(item, "A")
            if line is None:
                continue
            if not line.get("decide"):
                rejects.append((p.stem, item.get("key"), "A: บรรทัดนี้ไม่ได้ถูกทำเครื่องหมาย decide"))
                continue
            if isinstance(item.get("th_new"), str):
                item["th_new"] = same_newlines(item["th_new"], line["en"])
            msgs = []
            cls = RW.check_gender(item, line, lambda m: msgs.append(m))
            if cls is None:
                rejects.append((p.stem, item.get("key"), "A: " + (msgs[0] if msgs else "ตก")))
                continue
            # check_gender ใช้ POLITE_JA ของ merge_qc ซึ่งนับ でしょ/ですわ/っす ด้วย — บรีฟบอกว่าไม่นับ
            # ใช้ตัวกรองเดียวกับตัวสร้างซอง (ผู้ตรวจซองนำร่อง 05 จับได้ว่าสองชั้นขัดกัน)
            if line.get("decide") == "polite" and not R.ja_polite(item.get("ja_quote") or ""):
                rejects.append((p.stem, item.get("key"),
                                "A: ja_quote มีแต่รูปที่ไม่นับเป็นความสุภาพ (でしょ · ですわ · っす · คันไซ · ในเครื่องหมายคำพูด)"))
                continue
            stats["A " + cls] += 1
            genders.append((p.stem, line, item, cls))
        for item in data.get("weird") or []:
            stats["B เสนอ"] += 1
            line = mine(item, "B")
            if line is None:
                continue
            scene = {k for k, l in lines.items() if l["_file"] == line["_file"]}
            msgs = []
            if RW.check_weird(item, line, scene, lines, lambda m: msgs.append(m)) is None:
                rejects.append((p.stem, item.get("key"), "B: " + (msgs[0] if msgs else "ตก")))
                continue
            weird.append((p.stem, line, item))
        for item in data.get("gender_wrong") or []:
            stats["C เสนอ"] += 1
            line = mine(item, "C")
            if line is None:
                continue
            scene = {k for k, l in lines.items() if l["_file"] == line["_file"]}
            msgs = []
            if RW.check_gender_wrong(item, line, scene, lines, lambda m: msgs.append(m)) is None:
                rejects.append((p.stem, item.get("key"), "C: " + (msgs[0] if msgs else "ตก")))
                continue
            gwrong.append((p.stem, line, item))
    return stats, rejects, polish, genders, weird, gwrong


def one(s):
    return (s or "").replace("\r\n", " / ").replace("\n", " / ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", help="เลขซอง เช่น 07 — ตรวจซองเดียว พิมพ์ผล ไม่เขียนไฟล์")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--cand", default="", help="เขียนไฟล์ข้อเสนอเฉพาะซอง เช่น 49,54,57 (ว่าง = ทุกซอง)")
    args = ap.parse_args()

    only = "packet_%02d" % int(args.packet) if args.packet else None
    stats, rejects, polish, genders, weird, gwrong = run(only)

    if only:
        for k in sorted(stats):
            print("%-12s %d" % (k, stats[k]))
        print("ตก %d" % len(rejects))
        for pk, key, msg in rejects:
            print("  ตก  %s — %s" % (key, msg))
        for pk, line, item, st, why in polish:
            if st == "review":
                print("  รอ lead  %s — %s" % (line["key"], why))
        for pk, line, item, cls in genders:
            if cls == "rewrite":
                print("  รอ lead  %s — งาน A เขียนประโยคใหม่" % line["key"])
        return 0

    # ยุบตามสตริงอังกฤษ — สองซองเสนอคนละแบบ หรืองาน A กับ D ชนกัน = ขัดกัน ไม่ลงอัตโนมัติ
    by_en = defaultdict(list)
    for pk, line, item, st, why in polish:
        by_en[line["en"]].append(("D", pk, line, item, st))
    for pk, line, item, cls in genders:
        by_en[line["en"]].append(("A", pk, line, item, cls))
    conflict = {en for en, props in by_en.items()
                if len({RW.norm(x[3]["th_new"]) for x in props}) > 1}

    VERDICT.mkdir(parents=True, exist_ok=True)
    drop = json.loads(LEAD_DROP.read_text(encoding="utf-8")) if LEAD_DROP.exists() else {}
    cand = defaultdict(list)
    for pk, line, item, st, why in polish:
        if line["key"] in drop:          # lead ตัดแล้ว ไม่ต้องเสียแรงผู้ยืนยัน
            continue
        cand[pk].append({"key": line["key"], "file": line["_file"], "kind": item["kind"],
                         "en": line["en"], "ja": line.get("ja", ""), "th_old": line["th"],
                         "th_new": item["th_new"], "why": item.get("why", ""),
                         "gate": st if line["en"] not in conflict else "conflict", "gate_note": why})
    # งาน A ต้องผ่านผู้ยืนยันด้วย — ซอง 26 (13 ก.ย.) เติมเจ้าค่ะให้โอเรียวที่คุยกับไซโตระดับ T2 และถอดเจ้าค่ะ
    # ที่ถูกอยู่แล้วออก ทั้งที่ผ่านด่านเครื่องครบ (ด่านเครื่องตรวจหลักฐาน JA ได้ แต่ตรวจข้อ 2/4/5 ของบรีฟไม่ได้)
    for pk, line, item, cls in genders:
        if line["key"] in drop:
            continue
        cand[pk].append({"key": line["key"], "file": line["_file"], "kind": "gender_fix:" + item["particle"],
                         "decide": line.get("decide"), "gender": "%s(%s)" % (line.get("gender"), line.get("gender_from")),
                         "en": line["en"], "ja": line.get("ja", ""), "th_old": line["th"],
                         "th_new": item["th_new"], "ja_quote": item.get("ja_quote", ""), "why": item.get("why", ""),
                         "gate": cls if line["en"] not in conflict else "conflict", "gate_note": ""})
    cdir = WAVE / "candidates"
    cdir.mkdir(parents=True, exist_ok=True)
    # --cand 49,54,58 = เขียนไฟล์ข้อเสนอเฉพาะซองที่ระบุ (กันเขียนทับไฟล์ที่ผู้ยืนยันกำลังอ่านอยู่)
    only_cand = {"packet_%02d" % int(x) for x in (args.cand or "").split(",") if x.strip()}
    for pk, rows in cand.items():
        if only_cand and pk not in only_cand:
            continue
        (cdir / (pk + ".json")).write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

    with (WAVE / "rejects.md").open("w", encoding="utf-8") as fh:
        fh.write("# ตกด่านเครื่อง %d รายการ\n\n" % len(rejects))
        for pk, key, msg in rejects:
            fh.write("- %s `%s` — %s\n" % (pk, key, msg))
    with (WAVE / "review.md").open("w", encoding="utf-8") as fh:
        fh.write("# รายการที่ lead ต้องอ่าน\n\n## A ชั้น rewrite\n\n")
        for pk, line, item, cls in genders:
            if cls == "rewrite":
                fh.write("- `%s` (%s)\n  - EN: %s\n  - JA: %s\n  - เดิม: %s\n  - เสนอ: %s\n  - เหตุผล: %s\n"
                         % (line["key"], pk, one(line["en"]), one(line.get("ja")), one(line["th"]),
                            one(item["th_new"]), item.get("why", "")))
        fh.write("\n## ขัดกัน (สตริงเดียวกันถูกเสนอคนละแบบ) %d สตริง\n\n" % len(conflict))
        for en in sorted(conflict):
            fh.write("- EN: %s\n" % one(en))
            for task, pk, line, item, st in by_en[en]:
                fh.write("  - [%s %s %s] %s\n" % (task, pk, st, one(item["th_new"])))
        fh.write("\n## B ความหมายผิด %d รายการ\n\n" % len(weird))
        for pk, line, item in weird:
            ev = item.get("evidence") or {}
            fh.write("- `%s` (%s)\n  - EN: %s\n  - JA: %s\n  - เดิม: %s\n  - เสนอ: %s\n  - ปัญหา: %s\n"
                     "  - หลักฐาน: %s = %s\n"
                     % (line["key"], pk, one(line["en"]), one(line.get("ja")), one(line["th"]),
                        one(item.get("th_new") or "—"), item.get("problem", ""), ev.get("src"),
                        one(ev.get("quote"))))
        fh.write("\n## C ป้ายเพศผิด %d รายการ\n\n" % len(gwrong))
        for pk, line, item in gwrong:
            ev = item.get("evidence") or {}
            fh.write("- `%s` ฉาก `%s` (%s) ตาราง %s(%s) -> **%s**\n  - EN: %s\n  - เหตุผล: %s\n"
                     "  - หลักฐาน: %s = %s\n"
                     % (line["key"], line["_file"], pk, item.get("claimed"), line.get("gender_from"),
                        item.get("actual"), one(line["en"]), item.get("why", ""), ev.get("src"),
                        one(ev.get("quote"))))

    for k in sorted(stats):
        print("%-12s %d" % (k, stats[k]))
    print("ตกด่านเครื่อง %d · ขัดกัน %d สตริง · B %d · C %d" % (len(rejects), len(conflict), len(weird), len(gwrong)))
    print("ไฟล์ให้ผู้ยืนยัน: %s · รายงาน: %s" % (cdir, WAVE / "review.md"))

    if args.apply:
        apply(polish, genders, conflict)


def apply(polish, genders, conflict):
    """ลง done: A ชั้น add/swap · D ที่ผู้ยืนยันตอบ keep (ไฟล์ verdict/packet_NN.json)
    แล้วแทรกช่องว่างขอบคำใหม่ด้วย fix_thai_wrap.fix (ข้อเสนอใหม่ไม่มีช่องว่างเทียม)"""
    import fix_thai_wrap as W      # โหลด pythainlp — ช้า จึงนำเข้าเฉพาะตอนลงจริง
    import make_polish_packets as PP   # โหลดตารางเพศล่าสุด
    verdict = {}
    for p in VERDICT.glob("packet_*.json"):
        for row in json.loads(p.read_text(encoding="utf-8")):
            verdict[row["key"]] = row
    drop = json.loads(LEAD_DROP.read_text(encoding="utf-8")) if LEAD_DROP.exists() else {}
    take, skipped = {}, Counter()
    # คำแปล ณ วันสร้างซอง (13 ก.ย.) — ใช้กันการเขียนทับงานที่ลง master ทีหลัง (ดูท้ายฟังก์ชัน)
    orig = {}
    for _, line, *_ in list(genders) + list(polish):
        orig.setdefault(line["en"], line["th"])
    for pk, line, item, cls in genders:
        en = line["en"]
        # ซองสร้างก่อนแก้ตารางเพศ 15 ก.ย. 2026 (ชั้นคิวเสียง · ตัดฉากสองเพศ) — เพศที่ฝังในซองอาจไม่ใช่เพศปัจจุบัน
        # วัดแล้ว 3,466 บรรทัดเปลี่ยน (audit_polish_gender_drift.py) · งาน A บนบรรทัดพวกนี้ห้ามลงจนกว่าจะออกซองใหม่
        now, _ = PP.gender_of(line["key"], en, line.get("ja") or "")
        if now != line.get("gender"):
            skipped["A เพศเปลี่ยนหลังแก้ตาราง"] += 1
            continue
        if line["key"] in drop:
            skipped["A lead ตัด"] += 1
        elif item.get("particle") == "ขอรับ" and FEMALE_LABEL.search(" ".join(line.get("labels") or [])):
            # ตาราง scene_gender ตีบทตัวละครหญิงเป็นชาย (วัดในซอง 13 ก.ย.: ฮารุกะ 147 · โอกามิ 84 · โอเรียว 52)
            # ป้ายเชื่อรายบรรทัดไม่ได้ จึงใช้แค่ "ข้าม" ไม่ใช่ "แก้" — กันขอรับหลุดเข้าปากตัวละครหญิง
            skipped["A ขอรับ บนป้ายตัวละครหญิง"] += 1
        elif en in conflict:
            skipped["A ขัดกัน"] += 1
            continue
        elif (verdict.get(line["key"]) or {}).get("decision") != "keep":
            skipped["A ผู้ยืนยันไม่รับ/ยังไม่ตัดสิน"] += 1
            continue
        else:
            take[en] = item["th_new"]
    for pk, line, item, st, why in polish:
        en = line["en"]
        v = verdict.get(line["key"]) or {}
        if line["key"] in drop:
            skipped["D lead ตัด"] += 1
        elif en in conflict:
            skipped["D ขัดกัน"] += 1
        elif v.get("decision") != "keep":
            skipped["D ผู้ยืนยันไม่รับ/ยังไม่ตัดสิน"] += 1
        elif st == "review" and not v.get("lead_ok"):
            skipped["D รอ lead"] += 1
        else:
            take[en] = item["th_new"]      # ผู้ยืนยันรับ/ไม่รับเท่านั้น ห้ามเขียนแทน (จะข้ามด่านเครื่อง)
    # สตริงที่หลายซองเสนอไม่ตรงกัน (ขัดกัน) — lead เลือกไว้ใน lead_pick.json {"EN": "th_new ที่เลือก"}
    # ลงได้เฉพาะเมื่อฉบับที่เลือกตรงกับข้อเสนอของซองใดซองหนึ่งที่ผู้ยืนยันรับแล้ว (กันการพิมพ์คำแปลใหม่ข้ามด่าน)
    pick_path = WAVE / "lead_pick.json"
    picks = json.loads(pick_path.read_text(encoding="utf-8")) if pick_path.exists() else {}
    offered = defaultdict(set)
    for pk, line, item, st, why in polish:
        if (verdict.get(line["key"]) or {}).get("decision") == "keep" and line["key"] not in drop:
            offered[line["en"]].add(item["th_new"])
    for pk, line, item, cls in genders:
        if (verdict.get(line["key"]) or {}).get("decision") == "keep" and line["key"] not in drop:
            offered[line["en"]].add(item["th_new"])
    for en, th in picks.items():
        if en in conflict and th in offered.get(en, set()):
            take[en] = th
            skipped["ขัดกัน→lead เลือกแล้ว"] += 1
        else:
            print("!! lead_pick ใช้ไม่ได้ (ไม่ขัดกัน หรือฉบับที่เลือกไม่อยู่ในข้อเสนอที่ผู้ยืนยันรับ): %s" % en[:60])
    # งาน B (ความหมายผิด) ไม่ผ่านผู้ยืนยันอัตโนมัติ — lead อ่านเองทีละรายการแล้วจดใน weird_accept.json {"คีย์": true}
    # (บทเรียน §0.54/§0.59: ข้อเสนอความหมายผิดของ agent ผิดบ่อย และมักขัดกับนโยบาย "คำแปลที่ตาม JA ไม่ต้องย้ายไปตาม EN")
    wa_path = WAVE / "weird_accept.json"
    weird_ok = json.loads(wa_path.read_text(encoding="utf-8")) if wa_path.exists() else {}
    if weird_ok:
        _, _, _, _, weird_items, _ = run()
        for pk, line, item in weird_items:
            en = line["en"]
            if weird_ok.get(line["key"]) is not True or not item.get("th_new") or line["key"] in drop:
                continue
            if en in take and RW.norm(take[en]) != RW.norm(item["th_new"]):
                print("!! B ชนกับข้อเสนออื่นของสตริงเดียวกัน — ข้าม: %s" % line["key"])
                continue
            take[en] = same_newlines(item["th_new"], en)
            orig.setdefault(en, line["th"])
            skipped["B lead รับ"] += 1
    # ซองสร้าง 13 ก.ย. แต่ master เปลี่ยนหลังจากนั้น (คลื่นคำลงท้าย gender3 116 สตริง · ชื่อดาบ · เควสต์โทซะ · ถอดคำลงท้าย)
    # ข้อเสนอเขียนทับคำแปลทั้งสตริง จึงลงเฉพาะสตริงที่ master ยังเท่าคำแปลในซอง — ไม่งั้นงานที่ลงทีหลังจะถูกย้อนทิ้ง
    master = json.loads(paths.MASTER_TH.read_text(encoding="utf-8"))
    stale = [en for en in take if RW.norm(master.get(en) or "") != RW.norm(orig.get(en) or "")]
    for en in stale:
        del take[en]
    skipped["คำแปลใน master เปลี่ยนหลังสร้างซอง"] = len(stale)
    take = {en: W.fix(th, W.MAX_RUN) for en, th in take.items()}
    nf, nk = RW.apply_to_done(take)
    print("ลง done %d ไฟล์ · %d คีย์ (%d สตริง) · ข้าม %s" % (nf, nk, len(take), dict(skipped)))
    print("ต่อด้วย: python scripts/merge_qc.py")


if __name__ == "__main__":
    raise SystemExit(main())
