#!/usr/bin/env python3
"""รวมคำแปลจาก `translations/done/*.done.json` เข้า `master_th.json` พร้อม QC อัตโนมัติ

**นี่คือทางเดียวที่เขียน `master_th.json` ได้** (กติกาเหล็กข้อ 4) — คู่ที่ไม่ผ่านด่านจะไม่ถูกรวม
และถูกส่งกลับให้ผู้แปลแก้ผ่าน `translations/qc_failures.json`

ด่านตรวจต่อคู่ (EN -> TH):
  K  ครบ:        ทุก key ของ batch ต้องมีใน done (ขาด = รายงาน ไม่ทำให้คู่อื่นตก)
  E  ไม่ว่าง
  N  จำนวนขึ้นบรรทัด (\\n) เท่ากับต้นฉบับ — กล่องข้อความในเกมตัดบรรทัดตายตัว
  T  tag/placeholder ครบและเท่ากัน: `<...>`, `${...}`, `%s/%d/%1$s`, `~...~`
  C  อักษร CJK/คานะที่มีใน EN ต้องอยู่ครบใน TH (ชื่อร้าน/ป้ายญี่ปุ่นห้ามหาย)
  X  encode ได้จริงด้วย `SlotMap` — ทุกกลิฟไทยต้องมีเซลล์ในฟอนต์ (ไม่งั้นขึ้น tofu)
  S  ห้ามมีอักษรที่ถูกใช้เป็น donor ของกลิฟไทย (เช่น À Ò ā) ปนในข้อความ — จะกลายเป็นไทยมั่วบนจอ
  P  สรรพนามต้องจับคู่ระดับเดียวกันตาม PRONOUN_MATRIX §0 (ผม/คุณ · ฉัน/แก · กู/มึง)
  L  ยาวเกิน 1.8x ของ EN = เตือน (ไม่ตก)
ด่านระดับ batch (ตรวจทั้งไฟล์ ไม่ใช่ทีละคู่ — เพิ่ม 26 ส.ค. 2026):
  A1 ลำดับคีย์: ชุดคีย์และ**ลำดับ**ใน done ต้องตรงกับ worklist เป๊ะ
     คีย์หล่นไปหนึ่งตัวทำให้คำแปลที่เหลือ "เลื่อนไปผิดคีย์ทั้งแถว" โดยด่านคู่ต่อคู่ทั้ง 7 ด่านมองไม่เห็น
     (เกิดจริงกับ b124 ใน sprint 15 — คีย์ `Whiteboard Phone Number` หล่น คำแปล 200 บรรทัดเลื่อน)
     **ตกข้อนี้ = ทั้ง batch ไม่ถูกรวม** เพราะรวมไปก็ผิดคีย์หมด
  A2 สถิติจับคู่: สหสัมพันธ์ความยาว EN/TH — จับกรณีที่ลำดับคีย์ถูกแต่ค่าถูกวางเลื่อน
     รายละเอียดและค่าที่ใช้ตั้งเกณฑ์อยู่ใน `scripts/check_alignment.py`
TH == EN ถือว่า "คงต้นฉบับ" (ระบบ/enum/ชื่อเฉพาะ) — ผ่าน แต่ยังตรวจ S เพราะตัวอักษรชน donor
ก็เพี้ยนบนจอแม้จะคง EN ไว้

ใช้:
  python scripts/merge_qc.py              # ตรวจ + รวมเข้า master_th.json
  python scripts/merge_qc.py --dry-run    # ตรวจอย่างเดียว ไม่เขียน
  python scripts/merge_qc.py --only 003   # เฉพาะ batch ที่ระบุ
  python scripts/merge_qc.py --status     # ไฟล์ done ไหนยังไม่ตรง master (ต้อง merge ซ้ำ) — ไม่เขียนอะไร
"""
import argparse
import io
import json
import os
import re
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
from check_pronoun_pairs import check_text as pronoun_problems
from check_alignment import MIN_CORR as ALIGN_MIN_CORR
from check_alignment import SHIFT_WINS as ALIGN_SHIFT_WINS
from check_alignment import _judge as align_judge
from check_alignment import _locate as align_locate

TAG_RE = re.compile(r"<[^<>]*>|%[0-9]*\$?[sdxufi%]|\$\{[^}]*\}|~[^~\s]{0,40}~")
CJK_RE = re.compile(r"[ᄀ-ᇿ぀-ヿ㐀-鿿가-힯ｦ-ﾟ]")
THAI_RE = re.compile(r"[฀-๿]")

DONE = paths.TRANSLATIONS / "done"
# บรรทัดที่ "ผสมระดับสรรพนามโดยตั้งใจ" (เช่น ตัวร้ายใช้ "คุณ" แบบประชด ขณะแทนตัวว่า "กู")
# ใส่ EN key ไว้ที่นี่พร้อมเหตุผล แล้วด่าน P จะข้ามให้ — ต้องมีเหตุผลกำกับเสมอ ห้ามใช้กลบความผิดพลาด
PRONOUN_EXCEPTIONS = paths.TRANSLATIONS / "pronoun_exceptions.json"
REPORT = paths.TRANSLATIONS / "qc_report.md"
FAILURES = paths.TRANSLATIONS / "qc_failures.json"


def load_slotmap():
    """คืน (SlotMap, ชุดตัวอักษร donor) — ถ้ายังไม่มี slotmap ให้ข้ามด่าน X/S พร้อมเตือน"""
    try:
        from slot_alloc import SLOTMAP, SlotMap
        if not SLOTMAP.exists():
            return None, set()
        sm = SlotMap.load(SLOTMAP)
        return sm, {chr(cp) for cp in sm.dec}
    except Exception as e:  # noqa: BLE001 — QC ต้องรันได้แม้ระบบฟอนต์ยังไม่พร้อม
        print("!! โหลด slotmap ไม่ได้ (ข้ามด่าน X/S): %s" % e)
        return None, set()


def load_exceptions():
    if PRONOUN_EXCEPTIONS.exists():
        return json.load(io.open(PRONOUN_EXCEPTIONS, encoding="utf-8"))
    return {}


def check_pair(en, th, sm, donor_chars, exceptions=()):
    fails, warns = [], []
    if not isinstance(th, str) or not th.strip():
        return ["E: ว่าง"], warns

    hits = sorted({c for c in th if c in donor_chars})

    if th == en:
        # คงต้นฉบับทั้งดุ้น = เขียนไบต์ชุดเดิมกลับลงไฟล์ ผลบนจอเท่ากับ "ไม่แตะคีย์นี้เลย"
        # ถ้าต้นฉบับเองมีอักษรชน donor (สตริงทดสอบฟอนต์ใน ui_preview_text.bin) การตีกลับไม่ช่วยอะไร
        # เพราะไม่มีคำแปลให้แก้ — จึงลดเป็นคำเตือน ไม่ใช่ตก (เคาะ 27 ส.ค. 2026 · sprint 17 · ผู้ตรวจ b152 จับได้)
        if hits:
            warns.append("S: ต้นฉบับเองมีอักษรชน donor %s (คงต้นฉบับ จึงไม่ตีกลับ)" % " ".join(hits))
        return fails, warns + ["= EN (คงต้นฉบับ)"]

    if hits:
        fails.append("S: มีอักษรที่ชน donor ฟอนต์ %s (จะขึ้นเป็นตัวไทยมั่วบนจอ)" % " ".join(hits))

    if en.count("\n") != th.count("\n"):
        fails.append("N: ขึ้นบรรทัดไม่เท่าต้นฉบับ (EN %d / TH %d)" % (en.count("\n"), th.count("\n")))

    en_tags, th_tags = Counter(TAG_RE.findall(en)), Counter(TAG_RE.findall(th))
    if en_tags != th_tags:
        miss = list((en_tags - th_tags).elements())
        extra = list((th_tags - en_tags).elements())
        fails.append("T: tag ไม่ตรง ขาด %s เกิน %s" % (miss or "-", extra or "-"))

    en_cjk, th_cjk = Counter(CJK_RE.findall(en)), Counter(CJK_RE.findall(th))
    if en_cjk - th_cjk:
        fails.append("C: อักษรญี่ปุ่น/CJK หาย %s" % "".join((en_cjk - th_cjk).elements()))

    if sm is not None and THAI_RE.search(th):
        try:
            sm.encode(th)
        except SystemExit as e:
            fails.append("X: encode ไม่ผ่าน — %s" % str(e).split("\n")[0][:120])

    if en in exceptions:
        warns.append("P: ข้ามด่านสรรพนามตามรายการยกเว้น — %s" % exceptions[en])
    else:
        for pr in pronoun_problems(th):
            fails.append("P: " + pr)

    if len(th) > len(en) * 1.8 + 10:
        warns.append("L: ยาว %d ตัวอักษร (EN %d)" % (len(th), len(en)))
    return fails, warns


ALIGN_EXCEPTIONS = paths.TRANSLATIONS / "alignment_exceptions.json"
_align_exc_cache = None


def align_exceptions():
    """ไฟล์ข้อยกเว้นด่าน A2 — {"ชื่อไฟล์ done": "เหตุผลที่ lead ตรวจแล้วยืนยันว่าไม่ได้เลื่อน"}"""
    global _align_exc_cache
    if _align_exc_cache is None:
        if ALIGN_EXCEPTIONS.exists():
            _align_exc_cache = json.load(io.open(ALIGN_EXCEPTIONS, encoding="utf-8"))
        else:
            _align_exc_cache = {}
    return _align_exc_cache


def check_batch_alignment(keys, vals, expected, name=None):
    """ด่าน A — ตรวจทั้ง batch ว่าคำแปล "จับคู่ถูกคีย์" ไหม · คืนรายการเหตุผลที่ตก (ว่าง = ผ่าน)

    A1 เทียบลำดับคีย์กับ worklist ตรง ๆ — ถูกที่สุดและจับเคส b124 ได้เต็ม ๆ
    A2 สถิติสหสัมพันธ์ความยาว — เผื่อกรณีลำดับคีย์ถูกแต่ค่าถูกวางเลื่อน (worklist หาย/ไม่มี)

    ⚠ A2 เป็นสถิติ ไม่ใช่หลักฐาน — batch ที่เป็น "เมนู/ตัวเลือกสั้นล้วน" ความยาวคีย์แทบไม่กระจาย
    ทำให้สหสัมพันธ์ต่ำได้ทั้งที่จับคู่ถูก (b195 sprint 21 = 0.828 · ไล่ทีละคีย์แล้วไม่มีเลื่อน)
    → ยกเว้นรายไฟล์ได้ที่ `translations/alignment_exceptions.json` รูปแบบ {"batch_195.done.json": "เหตุผล"}
    **ยกเว้นได้เฉพาะ A2 เท่านั้น — A1 (ชุด/ลำดับคีย์เทียบ worklist) ยกเว้นไม่ได้เด็ดขาด**
    """
    bad = []
    if expected:
        if keys != expected:
            miss = [k for k in expected if k not in set(keys)]
            extra = [k for k in keys if k not in set(expected)]
            if miss or extra:
                bad.append("A1: ชุดคีย์ไม่ตรง worklist — ขาด %d เกิน %d (ตัวอย่างที่ขาด: %s)"
                           % (len(miss), len(extra),
                              (miss[0].replace(chr(10), "|")[:60] if miss else "-")))
            else:
                # คีย์ครบแต่ลำดับสลับ — หาตำแหน่งแรกที่ต่าง
                at = next((i for i in range(len(keys)) if keys[i] != expected[i]), 0)
                bad.append("A1: ลำดับคีย์ไม่ตรง worklist ตั้งแต่ลำดับที่ %d (%s)"
                           % (at, expected[at].replace(chr(10), "|")[:60]))
    r = align_judge(keys, vals)
    if r is not None:
        wins = align_locate(keys, vals)
        if r["corr"] < ALIGN_MIN_CORR or r["diff"] > ALIGN_SHIFT_WINS or len(wins) >= 2:
            waiver = align_exceptions().get(name or "")
            if waiver and r["diff"] <= ALIGN_SHIFT_WINS and len(wins) < 2:
                print("   ~ %s: ข้าม A2 ตามข้อยกเว้นที่บันทึกไว้ (corr %.3f) — %s"
                      % (name, r["corr"], waiver))
                return bad
            msg = ("A2: สถิติบอกว่าคำแปลน่าจะเลื่อนคีย์ — สหสัมพันธ์ความยาวตรงลำดับ %.3f "
                   "(ไฟล์ปกติ 0.90-0.99) · จับคู่แบบเลื่อน %+d ได้ %.3f"
                   % (r["corr"], r["best_shift"] or 0, r["best"]))
            if wins:
                msg += " · เริ่มเพี้ยนราวลำดับที่ %d" % wins[0][0]
            bad.append(msg)
    return bad


def report_status():
    """บอกว่าไฟล์ done ไหนยังไม่ตรง master — ต้องรัน merge ซ้ำ

    ทำไมต้องมี (26 ส.ค. 2026 · sprint 16): **ผู้ตรวจเฟส 2 แก้ไฟล์ `done` หลังจาก lead merge ไปแล้ว**
    ถ้าไม่ merge ซ้ำ คำที่เขาแก้จะไม่เข้า master เลย และไม่มีอะไรเตือน
    รอบนี้เกิดจริงกับ b133 (แก้ 1 จุด) · b140 (3 จุด) · b141 (9 จุด) · b142 (4 จุด)
    """
    if not paths.MASTER_TH.exists():
        print("ยังไม่มี master_th.json")
        return 0
    master = json.load(io.open(paths.MASTER_TH, encoding="utf-8"))
    files = sorted(DONE.glob("*.done.json")) if DONE.exists() else []
    stale = []
    for f in files:
        data = json.load(io.open(f, encoding="utf-8"))
        strings = data.get("strings", data)
        n = sum(1 for en, th in strings.items() if master.get(en) != th)
        if n:
            stale.append((f.name, n, len(strings)))
    print("done %d ไฟล์ · master %d คู่" % (len(files), len(master)))
    if not stale:
        print("ทุกไฟล์ตรงกับ master แล้ว")
        return 0
    print("ไฟล์ที่ยังไม่ตรง master (ต้อง merge ซ้ำ):")
    for name, n, tot in stale:
        print("  %-28s ไม่ตรง %d/%d" % (name, n, tot))
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="เลข batch เช่น 003 หรือ TALK_007")
    ap.add_argument("--status", action="store_true",
                    help="รายงานว่าไฟล์ done ไหนยัง 'ไม่ตรง' master (ต้อง merge ซ้ำ) แล้วออก — ไม่เขียนอะไร")
    a = ap.parse_args()

    if a.status:
        return report_status()

    sm, donor_chars = load_slotmap()
    exceptions = load_exceptions()
    master = json.load(io.open(paths.MASTER_TH, encoding="utf-8")) if paths.MASTER_TH.exists() else {}
    master = OrderedDict(master)

    files = sorted(DONE.glob("*.done.json")) if DONE.exists() else []
    if a.only:
        files = [f for f in files if a.only in f.name]
    if not files:
        print("ไม่พบไฟล์ใน translations/done/ (ยังไม่มีคำแปลส่งเข้ามา)")
        return 0

    added = kept = failed = 0
    failures = OrderedDict()
    lines = ["# QC report — LJTH", ""]
    for f in files:
        data = json.load(io.open(f, encoding="utf-8"))
        strings = data.get("strings", data)
        batch_id = data.get("batch", f.name)
        src = paths.WORKLIST / ("batch_%s.json" % batch_id) if isinstance(batch_id, str) else None
        expected = None
        if src and src.exists():
            expected = list(json.load(io.open(src, encoding="utf-8"))["strings"].keys())

        keys = list(strings)
        vals = [strings[k] for k in keys]
        align_fails = check_batch_alignment(keys, vals, expected, f.name)
        if align_fails:
            # ทั้ง batch ไม่ถูกรวม — ถ้ารวมไปก็ผิดคีย์ทั้งไฟล์
            failures.setdefault(f.name, {})["__alignment__"] = align_fails
            failed += len(strings)
            lines.append("- `%s`: **ตกด่าน A (จับคู่ผิดคีย์) — ไม่รวมทั้ง batch**" % f.name)
            print("%-32s !! ตกด่าน A — ไม่รวมทั้ง batch" % f.name)
            for m in align_fails:
                print("      - " + m)
            continue

        b_added = b_fail = b_kept = 0
        for en, th in strings.items():
            fails, warns = check_pair(en, th, sm, donor_chars, exceptions)
            if fails:
                failures.setdefault(f.name, {})[en] = {"th": th, "fails": fails}
                b_fail += 1
                continue
            if th == en:
                b_kept += 1
            master[en] = th
            b_added += 1
        missing = [k for k in (expected or []) if k not in strings]
        added += b_added
        failed += b_fail
        kept += b_kept
        lines.append("- `%s`: ผ่าน %d (คง EN %d) · ตก %d · ขาด %d"
                     % (f.name, b_added, b_kept, b_fail, len(missing)))
        if missing:
            failures.setdefault(f.name, {})["__missing__"] = missing[:50]
        print("%-32s ผ่าน %4d  ตก %3d  ขาด %3d" % (f.name, b_added, b_fail, len(missing)))

    lines += ["", "รวม: ผ่าน %d · คง EN %d · ตก %d · master_th ตอนนี้ %d คู่"
              % (added, kept, failed, len(master))]
    if not a.dry_run:
        io.open(paths.MASTER_TH, "w", encoding="utf-8", newline="\n").write(
            json.dumps(master, ensure_ascii=False, indent=1) + "\n")
        io.open(REPORT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
        io.open(FAILURES, "w", encoding="utf-8", newline="\n").write(
            json.dumps(failures, ensure_ascii=False, indent=1) + "\n")
    print()
    print("รวม: ผ่าน %d · คง EN %d · ตก %d%s" % (added, kept, failed,
          "" if a.dry_run else " · master_th %d คู่" % len(master)))
    if failures and not a.dry_run:
        print("รายละเอียดที่ตก: translations/qc_failures.json")
    elif failures:
        # โหมด dry-run ไม่เขียนไฟล์ — พิมพ์ตัวที่ตกออกมาเลย ไม่งั้นผู้แปลหาไม่เจอ
        for fname, items in failures.items():
            for en, info in list(items.items())[:20]:
                if en == "__missing__":
                    print("  ขาด %d key" % len(info)); continue
                if en == "__alignment__":
                    for m in info:
                        print("  [%s] %s" % (fname, m))
                    continue
                print("  [%s] %s" % (fname, en.replace(chr(10), " / ")[:70]))
                for f in info["fails"]:
                    print("      - " + f)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
