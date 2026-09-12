#!/usr/bin/env python3
"""แบ่ง "ซอง" ให้ทีมผู้ตรวจ (subagent) สองงานของรอบแก้คำแปล (sprint 21)

ทำไมต้องแบ่งเป็นซองแทนที่จะให้ agent เปิดคลังเอง: คลังบทพูดมี 21,048 สตริงที่แปลแล้ว
ถ้าปล่อยให้ agent เลือกอ่านเอง มันจะสุ่มอ่านแล้วรายงานว่า "ตรวจแล้ว" (บทเรียน §0.54)
ซองบังคับให้ทุกบรรทัดถูกอ่านครบ และแยกไฟล์ผลลัพธ์ของแต่ละตัวไม่ให้ชนกัน

สองคลื่นที่ซองรองรับ:

  --wave gender  บรรทัดที่ "ตอนแปลยังพิสูจน์เพศไม่ได้จึงแปลกลางเพศ ตอนนี้พิสูจน์ได้แล้ว"
                 เกณฑ์คัดเข้า: รู้เพศผู้พูดแล้ว (ชั้นใดก็ได้ใน merge_qc) + ต้นฉบับญี่ปุ่นเป็นรูปสุภาพ
                 + คำแปลไทยยัง **ไม่มี** คำลงท้ายบอกเพศ (ขอรับ/เจ้าค่ะ)
                 ซองใส่ทั้งฉากเพื่อให้ผู้ตรวจเห็นน้ำเสียงรอบข้าง แต่ชี้ว่าบรรทัดไหนคือตัวที่ต้องตัดสิน

  --wave weird   กวาดคำแปลที่ความหมายเพี้ยน **อ่านเป็นฉาก** พร้อมต้นฉบับญี่ปุ่น
                 ต่างจากรอบ §0.54 ที่อ่าน EN->TH ทีละคู่โดด ๆ ไม่มี JA และไม่มีลำดับบทสนทนา
                 ของที่คลาสนี้จับได้แต่รอบก่อนจับไม่ได้: คำตอบไม่รับกับคำถามบรรทัดก่อน ·
                 สรรพนามชี้ผิดคน · EN กำกวมแต่ JA ชี้ชัด · น้ำเสียงสลับระดับกลางฉาก

ใช้:
  python scripts/make_revise_packets.py --wave gender --lines 450
  python scripts/make_revise_packets.py --wave weird  --lines 1100
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict, OrderedDict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                      # noqa: E402
import merge_qc as M              # noqa: E402
import thai_pronouns as tp        # noqa: E402


def gender_of(en, ja):
    """เพศ + ชื่อชั้นหลักฐาน ตามลำดับเดียวกับด่าน G ใน merge_qc.py (ห้ามเรียงใหม่)"""
    g = M.line_gender(en)
    if g:
        return g, "line"
    g = M.ja_gender(ja)
    if g:
        return g, "ja"
    g = M.dialogue_gender(en)
    if g:
        return g, "dialogue"
    g = M.scene_gender(en)
    if g:
        return g, "scene"
    return None, None


# รูปที่ **มี です/ます อยู่ข้างในแต่ไม่ใช่ความสุภาพ** — วัดจากรายงานผู้ตรวจ 6 ซอง (12 ก.ย. 2026)
# `POLITE_JA` ของ merge_qc เก็บ "です"/"ます" เป็นสตริงย่อย จึงจับรูปเหล่านี้ติดไปด้วยทั้งชุด:
#   ですわ · ますわ · ますやん · まっせ · でっか · でっせ = สำเนียงคันไซ (เรียวมะตัวเอกก็พูด)
#   くだされ = รูปโบราณ/วรรณกรรม ไม่ใช่ ください  ·  ますます = คำวิเศษณ์ "ยิ่งขึ้น"
#   ごっつぁんです = สำนวนตายตัวของนักซูโม่  ·  っす = รูปย่อกันเองของคนหนุ่ม
#   でしょ = รูปคาดเดา ไม่ใช่ teineigo (ผู้ตรวจซอง 16 · 23 รายงานตรงกัน)
# ⚠ ห้ามไปตัดรูปเหล่านี้ออกจาก `POLITE_JA` ของ `merge_qc.py` — ด่าน J ทั้งคลังใช้ลิสต์นั้น
#   การทำให้แคบลงที่นั่นกระทบคำแปลที่ผ่านด่านไปแล้วทั้งหมด
KANSAI_FAKE_POLITE = re.compile(r"ですわ|ますわ|ますやん|まっせ|でっか|でっせ|くだされ|ますます"
                                r"|ごっつぁんです|っす|でしょ")
# ข้อความระบบในไฟล์ .msg (สายสัมพันธ์ · ปลดล็อกวิชา · เลื่อนขั้น) — ไม่มีผู้พูดจริง จึงไม่มีเพศ
# ผู้ตรวจ 5 ซองรายงานตรงกันว่าบรรทัดพวกนี้ไม่ควรเข้าคิวตัดสินคำลงท้าย (วัดทั้งคลังได้ 95 แถว)
SYSTEM_MSG = re.compile(r"絆が芽生え|絆ゲージ|を習得|習得しました|解放されました|開放されました"
                        r"|ランクが|に到達|会得しました|が使えるように|精進目録")


def ja_polite(ja):
    """ต้นฉบับญี่ปุ่นบรรทัดนี้ "นอบน้อมจริง" ไหม

    ตัดคำพูดที่ยกมาอ้างใน 「」『』 ออกก่อนเสมอ เหมือนที่ `merge_qc.ja_gender()` ทำ —
    ความสุภาพในคำพูดที่ยกมาเป็นของ *คนที่ถูกอ้างถึง* ไม่ใช่ของผู้พูด (ซอง 07 มีราว 70 จาก 90
    บรรทัดที่ติดคิวเพราะครูสอนสำเนียงโทซะ *ท่อง* ประโยคสุภาพในเครื่องหมายคำพูด
    ขณะที่ตัวเขาเองใช้ 俺/だ ตลอดทั้งฉาก)
    """
    ja = M.QUOTE_RE.sub(" ", ja)
    ja = KANSAI_FAKE_POLITE.sub(" ", ja)
    return any(m in ja for m in M.POLITE_JA) or bool(M.POLITE_JA_RE.search(ja))


def decide_kind(en, ja, th, g):
    """บรรทัดนี้เข้าข่าย "เคยแปลกลางเพศเพราะพิสูจน์เพศไม่ได้" ไหม · คืนชนิดคำลงท้ายที่ใช้ได้

    "polite"     ต้นฉบับเป็นรูป ですます/ございます -> ขอรับ (ชาย) · เจ้าค่ะ/เจ้าคะ (หญิง)
    "fem_casual" ต้นฉบับลำลองแต่มีเครื่องหมายหญิงแน่ (かしら わよ のよ) -> จ๊ะ/จ้ะ (PRONOUN_MATRIX §4 ข้อ 1.5)
    None         ไม่เข้าข่าย (ยังไม่รู้เพศ · คำแปลมีคำลงท้ายบอกเพศอยู่แล้ว · เป็นป้ายชื่อ)
    """
    if not g or tp.is_name_label(en, th):
        return None
    if SYSTEM_MSG.search(ja):
        return None
    if tp.POLITE_OLD.search(th) or tp.FEM_CASUAL.search(th):
        return None                     # มีคำลงท้ายบอกเพศอยู่แล้ว ไม่ใช่บรรทัดที่ค้าง
    if ja_polite(ja):
        return "polite"
    if g == "female" and M.JA_FEMALE_RE.search(M.QUOTE_RE.sub(" ", ja)):
        return "fem_casual"
    return None


def load():
    par = json.loads((paths.PROJECT / "extracted" / "parallel" / "msg.json").read_text(encoding="utf-8"))
    mt = json.loads((paths.TRANSLATIONS / "master_th.json").read_text(encoding="utf-8"))
    byfile = defaultdict(list)
    for r in par:
        en = r.get("en") or ""
        if en.strip() and mt.get(en):
            byfile[r["file"]].append(r)
    return byfile, mt


def build_rows(rows, mt, wave, safe):
    """คืน (รายการบรรทัดของฉาก, จำนวนบรรทัดที่ต้องตัดสินในฉากนี้)"""
    out, todo, seen = [], 0, set()
    for r in rows:
        en = r["en"]
        th = mt[en]
        if (en, th) in seen:            # สตริงซ้ำในฉากเดียว — ให้ผู้ตรวจอ่านครั้งเดียว
            continue
        seen.add((en, th))
        ja = r.get("ja") or ""
        item = OrderedDict(key=r["key"], en=en, ja=ja, th=th)
        if r.get("labels"):
            item["labels"] = r["labels"]
        g, layer = gender_of(en, ja)
        if g:
            item["gender"] = g
            item["gender_from"] = layer
        kind = decide_kind(en, ja, th, g) if en in safe else None
        if kind:
            item["decide"] = kind
            todo += 1
        out.append(item)
    return out, todo


def safe_keys(byfile, mt):
    """คีย์อังกฤษที่ "แก้คำลงท้ายได้อย่างปลอดภัย" — `master_th.json` ผูกคำแปลกับ **สตริงอังกฤษ**
    ไม่ใช่กับบรรทัด จึงใส่คำลงท้ายบอกเพศได้เฉพาะสตริงที่ทุกที่ที่มันโผล่เป็นเพศเดียวกัน
    และ **ทุกที่** เข้าเกณฑ์ decide เหมือนกัน · ถ้ามีที่ไหนที่ยังต้องกลางเพศ = ห้ามแตะ
    (วัดแล้ว 12 ก.ย. 2026: เพศขัดกัน 0 สตริง · มีที่ที่ยังต้องกลางเพศ 19 สตริง)
    """
    g_by_en, kind_by_en = defaultdict(set), defaultdict(set)
    for rows in byfile.values():
        for r in rows:
            en, ja = r["en"], (r.get("ja") or "")
            g, _ = gender_of(en, ja)
            g_by_en[en].add(g)
            kind_by_en[en].add(decide_kind(en, ja, mt[en], g))
    return {en for en, kinds in kind_by_en.items()
            if kinds - {None} and None not in kinds and len(g_by_en[en] - {None}) == 1}


def render_txt(data):
    """ซองฉบับอ่าน — กะทัดรัดกว่า JSON ราว 40% และบังคับให้อ่านเรียงบรรทัดตามบทสนทนา

    การขึ้นบรรทัดในเนื้อข้อความเขียนเป็นสองตัวอักษร (backslash + n) เพื่อให้หนึ่งช่องอยู่บรรทัดเดียว
    ผู้ตรวจจะนับจำนวนจุดขึ้นบรรทัดได้ตรงและเห็นว่าห้ามเพิ่ม/ลด (ด่าน N ของ merge_qc)
    """
    def esc(s):
        return (s or "").replace(chr(13) + chr(10), "\\n").replace(chr(10), "\\n")

    out = ["ซอง %s — อ่านทุกบรรทัด เรียงตามลำดับ" % data["packet"], ""]
    for sc in data["scenes"]:
        out.append("=" * 70)
        out.append("### ไฟล์ฉาก %s (%d บรรทัด)" % (sc["file"], len(sc["lines"])))
        for l in sc["lines"]:
            head = "[%s]" % l["key"]
            if l.get("gender"):
                head += "  เพศ=%s(%s)" % (l["gender"], l.get("gender_from"))
            if l.get("decide"):
                head += "  *** ต้องตัดสิน: %s ***" % l["decide"]
            if l.get("labels"):
                head += "  ป้าย=%s" % " | ".join(l["labels"])
            out.append(head)
            out.append("  EN: " + esc(l["en"]))
            out.append("  JA: " + esc(l.get("ja")))
            out.append("  TH: " + esc(l["th"]))
        out.append("")
    return chr(10).join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", choices=("gender", "weird"), required=True)
    ap.add_argument("--lines", type=int, default=0, help="บรรทัดต่อซอง (0 = ค่าตั้งต้นของคลื่น)")
    args = ap.parse_args()
    per = args.lines or (450 if args.wave == "gender" else 1100)

    out_dir = paths.PROJECT / "work" / "revise_wave" / args.wave / "in"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in list(out_dir.glob("packet_*.json")) + list(out_dir.glob("packet_*.txt")):
        old.unlink()

    byfile, mt = load()
    safe = safe_keys(byfile, mt)
    scenes = []
    for f in sorted(byfile):
        rows, todo = build_rows(byfile[f], mt, args.wave, safe)
        if todo:
            scenes.append({"file": f, "todo": todo, "lines": rows})

    # ฉากยาวมาก (เควสต์/สารานุกรมในไฟล์เดียว) ต้องหั่นเป็นท่อน ไม่งั้นซองเดียวจะเกินที่ผู้ตรวจอ่านได้
    # หั่นแบบ **เรียงบรรทัดต่อเนื่อง** เพื่อให้ยังอ่านเป็นบทสนทนาได้ และตั้งชื่อไฟล์ท่อนว่า file#part
    MAXS = 550
    split = []
    for s in scenes:
        if len(s["lines"]) <= MAXS:
            split.append(s)
            continue
        for i in range(0, len(s["lines"]), MAXS):
            chunk = s["lines"][i:i + MAXS]
            split.append({"file": s["file"], "todo": sum(1 for l in chunk if l.get("decide")),
                          "lines": chunk})
    scenes = split

    # จำกัดทั้งจำนวนบรรทัด **และ** ขนาดไบต์ — ข้อความไทย/ญี่ปุ่นกิน token ต่อไบต์สูง
    # ซองที่ใหญ่เกินจะทำให้ผู้ตรวจอ่านไม่จบแล้วเงียบ ๆ ข้ามท้ายซอง (บทเรียน §0.54)
    MAXB = 220 * 1024
    packets, cur, n, b = [], [], 0, 0
    for s in scenes:
        sb = len(json.dumps(s, ensure_ascii=False).encode("utf-8"))
        if cur and (n + len(s["lines"]) > per * 1.35 or b + sb > MAXB):
            packets.append(cur)
            cur, n, b = [], 0, 0
        cur.append(s)
        n += len(s["lines"])
        b += sb
        if n >= per or b >= MAXB:
            packets.append(cur)
            cur, n, b = [], 0, 0
    if cur:
        packets.append(cur)

    tally = Counter()
    for i, group in enumerate(packets, 1):
        data = {"packet": "%s_%02d" % (args.wave, i),
                "scenes": [{"file": s["file"], "lines": s["lines"]} for s in group]}
        p = out_dir / ("packet_%02d.json" % i)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        (out_dir / ("packet_%02d.txt" % i)).write_text(render_txt(data), encoding="utf-8")
        nl = sum(len(s["lines"]) for s in group)
        nd = sum(s["todo"] for s in group)
        tally["lines"] += nl
        tally["decide"] += nd
        print("%s  ฉาก %3d · บรรทัด %4d · ต้องตัดสิน %4d" % (p.name, len(group), nl, nd))
    print("รวม %d ซอง · บรรทัด %d · ต้องตัดสิน %d -> %s"
          % (len(packets), tally["lines"], tally["decide"], out_dir))


if __name__ == "__main__":
    main()
