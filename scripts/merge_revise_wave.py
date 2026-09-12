#!/usr/bin/env python3
"""ตรวจผลของทีมผู้ตรวจ (subagent) รอบแก้คำแปล sprint 21 — คำลงท้ายบอกเพศ + คำแปลเพี้ยน

ทำไมต้องมีด่านเครื่องก่อนสายตา lead: §0.54 วัดไว้แล้วว่าผลดิบของ agent ที่เป็นงาน
"เสนอคำแปล" ผิด **13 จาก 40 รายการ** ส่วน §0.58 ที่บังคับให้แนบหลักฐานตรวจซ้ำได้
ผ่านด่าน 100% · รอบนี้เป็นงานแก้คำแปล จึงต้องมีทั้งสองชั้น:
ชั้นเครื่อง (ไฟล์นี้) ตัดทิ้งอะไรที่ขัดกฎแน่ ๆ · ชั้น lead อ่านที่เหลือทีละรายการ

ชั้นเครื่องของงาน "คำลงท้าย" ตรวจแปดข้อ:
  1. คีย์ต้องอยู่ในซองนั้นจริง และถูกทำเครื่องหมาย `decide` ไว้ (ห้ามเสนอบรรทัดที่ไม่ได้ถาม)
  2. คำลงท้ายที่ใส่ต้องตรงคู่กับเพศ + ชนิดที่ซองบอก (ขอรับ ชาย · เจ้าค่ะ/เจ้าคะ หญิงสุภาพ · จ๊ะ/จ้ะ หญิงลำลอง)
  3. คำลงท้ายนั้นต้องอยู่ใน `th_new` จริง
  4. `ja_quote` ต้องเป็นสตริงย่อยของ `ja` ของบรรทัดนั้น **เป๊ะตัวอักษร** (กันการอ้างลอย)
  5. `ja_quote` ต้องมีรูปสุภาพ ですます/ございます อยู่จริง (หรือเครื่องหมายหญิงสำหรับชนิดลำลอง)
  6. จำนวนขึ้นบรรทัดต้องไม่เปลี่ยน — กล่องข้อความในเกมตัดบรรทัดตายตัว (ด่าน N ของ merge_qc)
  7. ห้ามมีคำลงท้ายฝั่งตรงข้าม และห้ามมีคำของภาคปัจจุบัน (ครับ/ค่ะ/ผม/คุณ)
  8. เทียบ `th_new` กับ `th` เดิมแล้วจัดชั้นการเปลี่ยน:
       add    = เติมคำลงท้ายเข้าไปเฉย ๆ                      -> รับได้อัตโนมัติ
       swap   = ถอดคำลงท้ายกลางเพศเดิมออกแล้วใส่คำใหม่แทน      -> รับได้อัตโนมัติ
       rewrite= เขียนประโยคใหม่                               -> **lead ต้องอ่านเอง**

  สุดท้ายยุบตามสตริงอังกฤษ (master_th.json ผูกคำแปลกับ EN ไม่ใช่กับบรรทัด)
  ถ้าสองซองเสนอคำแปลของ EN เดียวกันไม่เหมือนกัน = ขัดกัน ส่งให้ lead ตัดสิน

ใช้:
  python scripts/merge_revise_wave.py                 # ตรวจ + เขียนรายงาน (ไม่แตะ done/master)
  python scripts/merge_revise_wave.py --apply         # เขียนที่รับแล้วลง translations/done/*.done.json
แล้วต่อด้วย: python scripts/merge_qc.py
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

WAVE = paths.PROJECT / "work" / "revise_wave" / "gender"
IN, OUT = WAVE / "in", WAVE / "out"

# คำลงท้ายที่อนุญาต แยกตาม (เพศ, ชนิดที่ซองบอก) — PRONOUN_MATRIX §4 ข้อ 1 และ 1.5
ALLOWED = {
    ("male", "polite"): ("ขอรับ",),
    ("female", "polite"): ("เจ้าค่ะ", "เจ้าคะ"),
    ("female", "fem_casual"): ("จ๊ะ", "จ้ะ"),
}
# คำลงท้ายกลางเพศที่ถอดออกได้ตอนใส่คำใหม่ (ตำรา §1.3 ข้อ 3) — เรียงยาวไปสั้นเสมอ
NEUTRAL_TAILS = ("เหมือนกัน", "หรอก", "เถอะ", "ด้วย", "เลย", "น่ะ", "นะ", "สิ", "ล่ะ", "จ้า")
SPACE_RE = re.compile(r"\s+")


def flat(s):
    """ยุบจุดขึ้นบรรทัดให้เป็นช่องว่าง — รายงานหนึ่งรายการต้องอยู่บรรทัดเดียว"""
    return (s or "").replace(chr(13), " ").replace(chr(10), " ")


def norm(s):
    """ตัดช่องว่างทั้งหมด — ช่องว่างขอบคำที่ `fix_thai_wrap.py` แทรกไว้ (§0.52) ไม่ใช่เนื้อคำแปล"""
    return SPACE_RE.sub("", s)


def contains(hay, needle):
    """ยกมาเป๊ะตัวอักษรไหม — ยอมรับสามรูปของจุดขึ้นบรรทัด

    ซองฉบับอ่าน (`packet_NN.txt`) เขียนจุดขึ้นบรรทัดเป็นสองตัวอักษร backslash+n เพื่อให้
    หนึ่งช่องอยู่บรรทัดเดียว ผู้ตรวจที่ยกข้อความคร่อมจุดขึ้นบรรทัดจึงยกรูปนั้นมา ไม่ใช่ CRLF จริง
    ถ้าไม่ยอมรับรูปนี้ หลักฐานที่ถูกต้องจะถูกตีตกเพราะรูปแบบซอง ไม่ใช่เพราะเนื้อหา
    """
    if not needle:
        return False
    flat = hay.replace("\r\n", "\n")
    return any(needle in v for v in (hay, flat, flat.replace("\n", "\\n"), flat.replace("\n", " ")))


def classify(th, th_new, particle):
    """จัดชั้นการเปลี่ยน: add · swap · rewrite (ดู docstring ข้อ 8)

    "swap" คือถอดคำลงท้ายกลางเพศเดิมออกหนึ่งคำแล้วใส่คำบอกเพศแทน — **ที่ตำแหน่งไหนก็ได้**
    ไม่จำเป็นต้องท้ายสตริง เพราะบรรทัดจริงมักมีเครื่องหมายวรรคตอนต่อท้าย ("...นะ!" -> "...ขอรับ!")
    หรือมีหลายประโยคในบรรทัดเดียว ("อีกครั้งนะ แล้วดูว่า..." -> "อีกครั้งเจ้าค่ะ แล้วดูว่า...")
    รูปเดิมที่เช็กแค่ `endswith` ตีรายการพวกนี้เป็น rewrite ทั้งหมด (17 จาก 287 รายการรอบแรก)
    แล้วทำให้ lead ต้องอ่านงานที่จริง ๆ เป็นการสลับคำท้ายธรรมดา
    """
    a, b = norm(th), norm(th_new)
    stripped = b.replace(particle, "")
    if stripped == a:
        return "add"
    for tail in NEUTRAL_TAILS:
        i = a.find(tail)
        while i >= 0:
            if a[:i] + a[i + len(tail):] == stripped:
                return "swap"
            i = a.find(tail, i + 1)
    return "rewrite"


def load_packets():
    """คีย์บรรทัด -> ข้อมูลบรรทัด · ซอง -> ชุดคีย์ในซองนั้น · คีย์ -> ไฟล์ฉาก"""
    lines, in_packet, scene_of = {}, defaultdict(set), {}
    for p in sorted(IN.glob("packet_*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        for s in data["scenes"]:
            for l in s["lines"]:
                lines[l["key"]] = l
                in_packet[p.stem].add(l["key"])
                scene_of[l["key"]] = s["file"]
    return lines, in_packet, scene_of


def check_gender(item, line, reject):
    ja, th = line.get("ja", ""), line["th"]
    kind, g = line.get("decide"), line.get("gender")
    th_new = item.get("th_new") or ""
    particle = item.get("particle") or ""
    quote = item.get("ja_quote") or ""

    allowed = ALLOWED.get((g, kind), ())
    if particle not in allowed:
        return reject("คำลงท้าย %r ใช้กับ (%s, %s) ไม่ได้" % (particle, g, kind))
    if particle not in th_new:
        return reject("th_new ไม่มีคำลงท้าย %r" % particle)
    if not contains(ja, quote):
        return reject("ja_quote ไม่ใช่สตริงย่อยของ ja ของบรรทัดนี้")
    if kind == "polite":
        if not (any(m in quote for m in M.POLITE_JA) or M.POLITE_JA_RE.search(quote)):
            return reject("ja_quote ไม่มีรูปสุภาพ ですます/ございます")
    else:
        if not M.JA_FEMALE_RE.search(M.QUOTE_RE.sub(" ", quote)):
            return reject("ja_quote ไม่มีเครื่องหมายหญิงที่วัดแล้วเชื่อได้")
    if th_new.count("\n") != th.count("\n"):
        return reject("จำนวนขึ้นบรรทัดเปลี่ยน (%d -> %d)" % (th.count("\n"), th_new.count("\n")))
    other = M.TH_FEMALE_TOKENS if g == "male" else M.TH_MALE_TOKENS
    hit = [t for t in other if t in th_new and t not in ("ค่ะ", "คะ", "ผม")]
    if hit:
        return reject("มีคำลงท้ายฝั่งตรงข้าม %s" % " ".join(hit))
    modern = tp.MODERN_SPEECH.findall(th_new)
    if modern and not tp.MODERN_SPEECH.findall(th):
        return reject("ใส่คำของภาคปัจจุบัน %s" % modern[:3])
    if norm(th_new) == norm(th):
        return reject("th_new เท่ากับคำแปลเดิม")
    return classify(th, th_new, particle)


def check_weird(item, line, scene_keys, lines, reject):
    ev = item.get("evidence") or {}
    src, quote = ev.get("src"), ev.get("quote") or ""
    if src not in scene_keys:
        return reject("evidence.src ไม่อยู่ในไฟล์ฉากเดียวกัน")
    ref = lines[src]
    pool = [ref.get("en", ""), ref.get("ja", ""), ref.get("th", "")] + list(ref.get("labels") or [])
    if not any(contains(x, quote) for x in pool):
        return reject("evidence.quote ไม่ใช่สตริงย่อยของบรรทัดที่อ้าง")
    th_new = item.get("th_new") or ""
    if th_new and th_new.count("\n") != line["th"].count("\n"):
        return reject("จำนวนขึ้นบรรทัดเปลี่ยน")
    return "ok"


def check_gender_wrong(item, line, scene_keys, lines, reject):
    """ป้ายเพศในซองผิด — รายการนี้ไปแก้ **ตารางเพศ** ที่คลื่นแปลรอบหน้าทั้งคลังใช้

    เช็กสามชั้นเหมือนงาน B บวกข้อที่สี่: เพศที่ผู้ตรวจบอกว่า "ซองอ้าง" ต้องตรงกับที่ซองอ้างจริง
    (กันการจำผิด/อ้างบรรทัดอื่น) และเพศจริงต้องเป็นฝั่งตรงข้ามเท่านั้น
    """
    claimed, actual = item.get("claimed"), item.get("actual")
    if claimed != line.get("gender"):
        return reject("claimed=%r ไม่ตรงกับที่ซองบอก (%r)" % (claimed, line.get("gender")))
    if actual not in ("male", "female") or actual == claimed:
        return reject("actual=%r ต้องเป็นเพศฝั่งตรงข้าม" % (actual,))
    return check_weird(item, line, scene_keys, lines, reject)



def lock_gender(gwrong, lines, scene_of, by_en_files, write):
    """เขียนคำตัดสินเพศรายบรรทัดของผู้ตรวจลง `translations/gender_lines.json` (ชั้นหลักฐานสูงสุด)

    ⚠ ข้อจำกัดเชิงโครงสร้างที่ต้องรู้: ตารางเพศทุกชั้นของโปรเจกต์ผูกกับ **สตริงอังกฤษ**
    ไม่ใช่กับคีย์บรรทัด ล็อกหนึ่งสตริงจึงมีผลกับทุกที่ที่สตริงนั้นโผล่ทั้งเกม
    สตริงสั้น ๆ ที่ใครก็พูดได้ ("Let's see...") จึงล็อกไม่ได้ ต้องตัดออก ไม่งั้นจะไปทับ
    บทของตัวละครอื่นที่คนละเพศ

    เกณฑ์ที่ล็อกได้: สตริงนั้นโผล่ในไฟล์ฉาก **ไม่เกิน 3 ไฟล์** และยาว **ตั้งแต่ 18 ตัวอักษร**
    ที่ตกเกณฑ์จะถูกพิมพ์แยกไว้ให้ lead ตัดสินด้วยวิธีอื่น (คลื่นระบุผู้พูดรายบรรทัด)
    """
    p = paths.TRANSLATIONS / "gender_lines.json"
    gl = json.loads(p.read_text(encoding="utf-8"))
    locked, skipped = [], []
    for pk, key, line, item in gwrong:
        en = line["en"]
        files = by_en_files.get(en, set())
        if len(files) > 3 or len(en) < 18:
            skipped.append((key, en, len(files), item.get("actual")))
            continue
        if en in gl and isinstance(gl[en], dict) and gl[en].get("gender"):
            skipped.append((key, en, len(files), "มีอยู่แล้วใน gender_lines"))
            continue
        ev = item.get("evidence") or {}
        gl[en] = {"gender": item["actual"],
                  "why": "ผู้ตรวจ (%s) อ่านบทฉาก %s · ตารางเดิมตี %s(%s) ผิด · หลักฐาน %s = %s · %s"
                         % (pk, scene_of[key], item.get("claimed"), line.get("gender_from"),
                            ev.get("src", ""), flat(ev.get("quote")),
                            flat(item.get("why"))[:400])}
        locked.append((key, en, item["actual"]))
    if write:
        p.write_text(json.dumps(gl, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ล็อกเข้า gender_lines.json %d สตริง%s" % (len(locked), "" if write else " (ยังไม่เขียน)"))
    for key, en, g in locked:
        print("  + %-18s %-6s %s" % (key, g, en.replace(chr(10), " / ")[:60]))
    if skipped:
        print("ล็อกไม่ได้ %d รายการ — สตริงกว้างเกินหรือมีอยู่แล้ว (ต้องใช้คลื่นระบุผู้พูดรายบรรทัด)" % len(skipped))
        for key, en, nf, why in skipped:
            print("  - %-18s ไฟล์ฉาก %s · %s | %s" % (key, nf, why, en.replace(chr(10), " / ")[:45]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="เขียนที่รับแล้วลง translations/done/*.done.json")
    ap.add_argument("--apply-weird", action="store_true",
                    help="เขียนคำแปลเพี้ยนที่ lead รับแล้ว (work/revise_wave/gender/weird_accept.json) ลง done")
    ap.add_argument("--lock-gender", action="store_true",
                    help="เขียนคำตัดสินเพศของผู้ตรวจลง translations/gender_lines.json")
    ap.add_argument("--include-rewrite", action="store_true",
                    help="รับชั้น rewrite ด้วย (ใช้เมื่อ lead อ่านรายการใน review.md แล้ว)")
    args = ap.parse_args()

    lines, in_packet, scene_of = load_packets()
    by_scene = defaultdict(set)
    for k, f in scene_of.items():
        by_scene[f].add(k)

    stats = Counter()
    rejects = []
    fixes = defaultdict(list)      # en -> [(cls, th_new, key, packet, why)]
    weird, gwrong = [], []

    for p in sorted(OUT.glob("packet_*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print("!! อ่าน %s ไม่ได้: %s" % (p.name, e))
            stats["ซองเสีย"] += 1
            continue
        stats["ซอง"] += 1
        for item in data.get("gender_fix") or []:
            stats["เสนอคำลงท้าย"] += 1
            key = item.get("key")
            line = lines.get(key)

            def reject(msg, key=key, p=p):
                rejects.append((p.stem, key, msg))
                stats["ตก"] += 1
                return None
            if line is None:
                reject("ไม่พบคีย์นี้ในซองใด")
                continue
            if key not in in_packet[p.stem]:
                reject("คีย์นี้ไม่ได้อยู่ในซองของตัวเอง")
                continue
            if not line.get("decide"):
                reject("บรรทัดนี้ไม่ได้ถูกทำเครื่องหมาย decide")
                continue
            cls = check_gender(item, line, reject)
            if cls is None:
                continue
            stats["ผ่าน:" + cls] += 1
            fixes[line["en"]].append((cls, item["th_new"], key, p.stem, item.get("why", "")))
        for item in data.get("weird") or []:
            stats["เสนอคำแปลเพี้ยน"] += 1
            key = item.get("key")
            line = lines.get(key)

            def wreject(msg, key=key, p=p):
                rejects.append((p.stem, key, "weird: " + msg))
                stats["ตก(เพี้ยน)"] += 1
                return None
            if line is None:
                wreject("ไม่พบคีย์นี้ในซองใด")
                continue
            if check_weird(item, line, by_scene[scene_of[key]], lines, wreject) is None:
                continue
            stats["ผ่าน(เพี้ยน)"] += 1
            weird.append((p.stem, key, line, item))
        for item in data.get("gender_wrong") or []:
            stats["เสนอป้ายเพศผิด"] += 1
            key = item.get("key")
            line = lines.get(key)

            def greject(msg, key=key, p=p):
                rejects.append((p.stem, key, "gender_wrong: " + msg))
                stats["ตก(ป้ายเพศ)"] += 1
                return None
            if line is None:
                greject("ไม่พบคีย์นี้ในซองใด")
                continue
            if check_gender_wrong(item, line, by_scene[scene_of[key]], lines, greject) is None:
                continue
            stats["ผ่าน(ป้ายเพศ)"] += 1
            gwrong.append((p.stem, key, line, item))

    # ยุบตาม EN — คำแปลของ EN เดียวกันต้องตรงกัน
    accept, conflict, review = {}, [], []
    for en, props in fixes.items():
        news = {norm(t) for _, t, _, _, _ in props}
        if len(news) > 1:
            conflict.append((en, props))
            continue
        cls, th_new, key, pk, why = props[0]
        if cls == "rewrite" and not args.include_rewrite:
            review.append((en, th_new, key, pk, why))
            continue
        accept[en] = th_new

    WAVE.mkdir(parents=True, exist_ok=True)
    (WAVE / "accepted.json").write_text(json.dumps(accept, ensure_ascii=False, indent=1), encoding="utf-8")

    with (WAVE / "review.md").open("w", encoding="utf-8") as fh:
        fh.write("# รายการที่ lead ต้องอ่านเอง — คลื่นแก้คำแปล sprint 21\n\n")
        fh.write("## A. คำลงท้ายที่เขียนประโยคใหม่ (ชั้น rewrite) %d รายการ\n\n" % len(review))
        for en, th_new, key, pk, why in review:
            fh.write("- `%s` (%s)\n  - EN: %s\n  - JA: %s\n  - เดิม: %s\n  - เสนอ: %s\n  - เหตุผล: %s\n"
                     % (key, pk, en.replace("\n", " / "),
                        lines[key].get("ja", "").replace("\r\n", " / "),
                        lines[key]["th"].replace("\n", " / "), th_new.replace("\n", " / "), why))
        fh.write("\n## B. คำแปลของ EN เดียวกันที่สองซองเสนอไม่ตรงกัน %d รายการ\n\n" % len(conflict))
        for en, props in conflict:
            fh.write("- EN: %s\n" % en.replace("\n", " / "))
            for cls, th_new, key, pk, why in props:
                fh.write("  - [%s %s] %s — %s\n" % (pk, cls, th_new.replace("\n", " / "), why))
        fh.write("\n## C. คำแปลที่ผู้ตรวจว่าความหมายเพี้ยน %d รายการ\n\n" % len(weird))
        for pk, key, line, item in weird:
            ev = item.get("evidence") or {}
            fh.write("- `%s` (%s)\n  - EN: %s\n  - JA: %s\n  - เดิม: %s\n  - เสนอ: %s\n"
                     "  - ปัญหา: %s\n  - หลักฐาน: %s = %s\n"
                     % (key, pk, line["en"].replace("\n", " / "),
                        line.get("ja", "").replace("\r\n", " / "), line["th"].replace("\n", " / "),
                        (item.get("th_new") or "—").replace("\n", " / "), item.get("problem", ""),
                        ev.get("src", ""), (ev.get("quote") or "").replace("\r\n", " / ")))

    with (WAVE / "gender_wrong.md").open("w", encoding="utf-8") as fh:
        fh.write("# ป้ายเพศในตารางที่ผู้ตรวจว่าผิด %d รายการ — ไปแก้ตารางเพศ ไม่ใช่แก้คำแปล\n\n"
                 % len(gwrong))
        for pk, key, line, item in gwrong:
            ev = item.get("evidence") or {}
            fh.write("- `%s` ไฟล์ฉาก `%s` (%s)\n"
                     "  - ตารางบอก %s(%s) · ผู้ตรวจว่า **%s**\n"
                     "  - EN: %s\n  - JA: %s\n  - เหตุผล: %s\n  - หลักฐาน: %s = %s\n"
                     % (key, scene_of[key], pk, item.get("claimed"), line.get("gender_from"),
                        item.get("actual"), line["en"].replace("\n", " / "),
                        line.get("ja", "").replace("\r\n", " / "), item.get("why", ""),
                        ev.get("src", ""), (ev.get("quote") or "").replace("\r\n", " / ")))

    with (WAVE / "rejects.md").open("w", encoding="utf-8") as fh:
        fh.write("# ที่ตกด่านเครื่อง %d รายการ\n\n" % len(rejects))
        for pk, key, msg in rejects:
            fh.write("- %s `%s` — %s\n" % (pk, key, msg))

    for k in sorted(stats):
        print("%-22s %d" % (k, stats[k]))
    print("-" * 40)
    print("รับอัตโนมัติ %d สตริง · rewrite รอ lead %d · ขัดกัน %d · เพี้ยนรอ lead %d · ป้ายเพศผิด %d"
          % (len(accept), len(review), len(conflict), len(weird), len(gwrong)))
    print("รายงาน: %s · %s" % (WAVE / "review.md", WAVE / "rejects.md"))

    by_en_files = defaultdict(set)
    for k, l in lines.items():
        by_en_files[l["en"]].add(scene_of[k])
    if args.lock_gender:
        lock_gender(gwrong, lines, scene_of, by_en_files, write=True)

    if args.apply_weird:
        # คำแปลเพี้ยนต้องผ่านสายตา lead ทีละรายการก่อน — ไฟล์ allow-list เก็บคำตัดสินไว้
        # พร้อมเหตุผลของรายการที่ตัดทิ้ง (เกณฑ์ผู้ใช้ 12 ก.ย. 2026: แก้เฉพาะที่หน้าที่ประโยคเปลี่ยน)
        picks = json.loads((WAVE / "weird_accept.json").read_text(encoding="utf-8"))
        take, drop = {}, 0
        for pk, key, line, item in weird:
            if picks.get(key) is True and item.get("th_new"):
                take[line["en"]] = item["th_new"]
            else:
                drop += 1
        nf, nk = apply_to_done(take)
        print("คำแปลเพี้ยนที่ lead รับ %d สตริง (ตัดทิ้ง %d) -> เขียน done %d ไฟล์ · %d คีย์"
              % (len(take), drop, nf, nk))

    if args.apply:
        n_files, n_keys = apply_to_done(accept)
        print("เขียนลง done %d ไฟล์ · %d คีย์ — ต่อด้วย python scripts/merge_qc.py" % (n_files, n_keys))


def apply_to_done(accept):
    n_files = n_keys = 0
    for p in sorted((paths.TRANSLATIONS / "done").glob("batch_*.done.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        strings = data.get("strings") or {}
        hit = 0
        for en, th_new in accept.items():
            if en in strings and strings[en] != th_new:
                strings[en] = th_new
                hit += 1
        if hit:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
            n_files += 1
            n_keys += hit
    return n_files, n_keys


if __name__ == "__main__":
    main()
