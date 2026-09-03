"""กวาดหาฟิลด์ "ที่คำนวณจากความยาวข้อความอังกฤษ" ในทุกชั้นที่บิลด์ — บั๊กชนิด "ซากาโมโตะซัง"

ต้นเรื่อง (3 ก.ย. 2026): บล็อกคำสั่งของ .msg เก็บตำแหน่งตัวอักษรที่ไบต์ [6:8] คิดจากประโยค EN
→ ไทยที่ยาวกว่าถูกตัดท้าย (แก้แล้วด้วย `msg.retime_cmds`) — สคริปต์นี้ตอบว่า "มีฟิลด์แบบเดียวกัน
ซ่อนที่อื่นอีกไหม" โดยไม่เดา: เทียบ EN กับ JA ของไฟล์เดียวกัน ฟิลด์ที่ผูกกับความยาวข้อความ
ต้องต่างกันระหว่างสองภาษาและต้องเท่ากับ/สเกลตามจำนวนตัวอักษร

ส่วนที่ 1 .msg  — ทุกฟิลด์ 2 ไบต์ในคำสั่ง 16 ไบต์ (offset 2..14) ต่อ (op, sub)
                นับ: เท่ากับ nchars(EN) · เท่ากับความยาวไบต์ utf-8 · ต่างจาก JA (และต่างทั้งที่ยาวเท่ากัน)
ส่วนที่ 2 ARMP  — ตารางที่แปล (build/text/db.macan.en) เทียบคอลัมน์ที่ไม่ใช่ข้อความ EN vs JA ทีละแถว
                (รวมตารางซ้อนใน row["table"]) + คอลัมน์ตัวเลขที่บังเอิญเท่ากับ len(ข้อความ) ในแถวเดียวกัน
locres         — ไม่มีฟิลด์ต่อสตริงนอกจาก length prefix ที่ตัวเขียนคำนวณใหม่อยู่แล้ว จึงไม่ต้องกวาด

ผลรอบแรก (3 ก.ย. 2026): 1,678 ไฟล์ .msg · 54,318 บรรทัด · 35,608 คู่ EN/JA
  - ฟิลด์ที่เท่ากับจำนวนตัวอักษรมีที่ offset 6 เท่านั้น (ทุก op/sub) = ตัวที่ retime_cmds จัดการแล้ว
  - (02,09) offset 2 = 10/20 คงที่ (หน่วงจังหวะ) ต่าง EN/JA เพราะบรรณาธิการเลือกต่าง ไม่ใช่ความยาว
  - (02,00) offset 10 ต่าง EN/JA 0 ครั้ง ทั้งที่ความยาวต่างเกือบทุกบรรทัด → ไม่ใช่ตำแหน่ง
  - ARMP 30 ตาราง: คอลัมน์ที่ไม่ใช่ข้อความ EN = JA ทุกช่อง ยกเว้น `*` ของ sound_speak_data
    (ค่าที่ตัวอ่านสังเคราะห์ — ดู HANDOFF §0.4) → ไม่มีฟิลด์ผูกความยาวข้อความ
"""
import glob
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from msg import MsgFile, nchars  # noqa: E402


def load(p):
    try:
        return MsgFile(open(p, "rb").read(), p)
    except Exception:
        return None


def sweep_msg():
    eq_chars, eq_bytes, total, diff_ja, diff_same = (Counter() for _ in range(5))
    files = lines = pairs = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "extracted", "msg_en", "*.msg"))):
        en = load(p)
        if en is None:
            continue
        ja = load(p.replace("msg_en", "msg_ja"))
        files += 1
        for i, L in enumerate(en.lines):
            lines += 1
            nc, nb = nchars(L.text), len(L.text.encode("utf-8"))
            JL = ja.lines[i] if ja and i < len(ja.lines) and len(ja.lines[i].cmds) == len(L.cmds) else None
            pairs += bool(JL)
            for ci, c in enumerate(L.cmds):
                for off in range(2, 16, 2):
                    v = (c[off] << 8) | c[off + 1]
                    k = (c[0], c[1], off)
                    total[k] += 1
                    if v and v == nc:
                        eq_chars[k] += 1
                    if v and v == nb and nb != nc:
                        eq_bytes[k] += 1
                    if JL:
                        jc = JL.cmds[ci]
                        if ((jc[off] << 8) | jc[off + 1]) != v:
                            diff_ja[k] += 1
                            if nchars(JL.text) == nc:
                                diff_same[k] += 1
    print("== .msg: ไฟล์ %d · บรรทัด %d · คู่ EN/JA %d" % (files, lines, pairs))
    print("-- ฟิลด์ที่เท่ากับ nchars(EN) >= 10%% และ >= 20 ครั้ง (นอก offset 6 = ต้องสงสัย)")
    sus = 0
    for k in sorted(total):
        # ต้องเจอบ่อยพอ (>=10%% และ >=20 ครั้ง) ไม่งั้นเป็นค่าเล็ก ๆ ที่บังเอิญตรง
        if eq_chars[k] >= 20 and eq_chars[k] / total[k] >= 0.10:
            flag = "" if k[2] == 6 else "   <-- นอก offset 6"
            if k[2] != 6:
                sus += 1
            print("  op=%02x sub=%02x off=%2d  eq=%d/%d%s" % (k[0], k[1], k[2], eq_chars[k], total[k], flag))
    print("-- ฟิลด์ที่เท่ากับความยาวไบต์ utf-8 (ไม่ใช่ตัวอักษร)")
    for k in sorted(total):
        if eq_bytes[k] / total[k] >= 0.01:
            print("  op=%02x sub=%02x off=%2d  eq=%d/%d" % (k[0], k[1], k[2], eq_bytes[k], total[k]))
    print("-- ฟิลด์นอก offset 6 ที่ต่าง EN/JA เกิน 5%% ของบรรทัดที่ความยาวต่างกัน")
    for k in sorted(total):
        if k[2] == 6 or not diff_ja[k]:
            continue
        lendiff = diff_ja[k] - diff_same[k]
        if lendiff / total[k] >= 0.05:
            print("  op=%02x sub=%02x off=%2d  ต่าง=%d/%d (ยาวเท่ากันแต่ต่าง=%d)" % (k[0], k[1], k[2], diff_ja[k], total[k], diff_same[k]))
    return sus


def rows_of(tbl, prefix=""):
    tcols = {c for c, t in (tbl.get("columnTypes") or {}).items() if t == 13}
    for k, v in tbl.items():
        if not k.isdigit() or not isinstance(v, dict):
            continue
        for rk, row in v.items():
            if not isinstance(row, dict):
                continue
            yield prefix + k + "/" + rk, row, tcols
            inner = row.get("table")
            if isinstance(inner, dict):
                yield from rows_of(inner, prefix + k + "/" + rk + "/")


def sweep_armp():
    tables = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "build", "text", "db.macan.en", "*.bin")))
    print("== ARMP: ตารางที่แปล %d" % len(tables))
    sus = 0
    for t in tables:
        pe = os.path.join(ROOT, "extracted", "db_en", t + ".json")
        pj = os.path.join(ROOT, "extracted", "db_ja", t + ".json")
        if not (os.path.exists(pe) and os.path.exists(pj)):
            print("  %s: ไม่มี json EN/JA" % t)
            continue
        en = json.load(open(pe, encoding="utf-8"))
        ja = json.load(open(pj, encoding="utf-8"))
        jrows = {k: r for k, r, _ in rows_of(ja)}
        diffcols, ncols, lencorr = Counter(), Counter(), Counter()
        for k, r, tc in rows_of(en):
            jr = jrows.get(k)
            for c, v in r.items():
                if c in tc or c == "table":
                    continue
                ncols[c] += 1
                if jr is not None and v != jr.get(c):
                    diffcols[c] += 1
                # นับเฉพาะช่องข้อความที่ EN != JA (ชื่อ texture/คีย์ที่เหมือนกันสองภาษาไม่บอกอะไร)
                if isinstance(v, int) and v > 1 and jr is not None:
                    for tn in tc:
                        s = r.get(tn)
                        if isinstance(s, str) and s and s != jr.get(tn) and v in (len(s), len(s.encode("utf-8"))):
                            lencorr[(c, tn)] += 1
        lc = {k: n for k, n in lencorr.items() if n >= 5 and n / ncols[k[0]] >= 0.2}
        diffcols.pop("*", None) if t == "sound_speak_data.bin" else None  # ค่าสังเคราะห์ของตัวอ่าน — HANDOFF §0.4
        if diffcols or lc:
            sus += 1
            print("  %s: คอลัมน์ไม่ใช่ข้อความที่ต่าง EN/JA=%s · เท่ากับ len(ข้อความ)=%s" % (t, dict(diffcols), lc))
    return sus


if __name__ == "__main__":
    a = sweep_msg()
    b = sweep_armp()
    print("\nสรุป: ฟิลด์ต้องสงสัยใน .msg นอก offset 6 = %d · ตาราง ARMP ต้องสงสัย = %d" % (a, b))
    print("(ARMP: sound_speak_data คอลัมน์ `*` เป็นค่าที่ตัวอ่านสังเคราะห์ — ไม่นับ · ดู HANDOFF §0.4)")
