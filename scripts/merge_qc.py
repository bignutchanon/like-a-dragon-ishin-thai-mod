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
  P  สรรพนามต้องจับคู่ระดับเดียวกันตาม PRONOUN_MATRIX §0 (ข้า/ท่าน · ข้า/เจ้า · กู/มึง)
  M  บทพูดของตัวละครในยุค (priority 1/4/9) ห้ามใช้ ผม/คุณ/ครับ/ค่ะ (§0) — เมนู/ระบบใช้ได้ปกติ
     คำยืมสมัยใหม่ (โอเค · ไอเดีย · ทีม) = เตือน ไม่ตก เพราะรายการยาวได้ไม่รู้จบ ตีกลับอัตโนมัติเสี่ยงเกิน
  G  บรรทัดที่ไฟล์บริบทระบุ `neutral: true` ห้ามมีคำลงท้ายบอกเพศ (ขอรับ/เจ้าค่ะ/ครับ/ค่ะ) — §1.2
  J  คำลงท้าย "ขอรับ/เจ้าค่ะ" ต้องมีหลักฐานในต้นฉบับญี่ปุ่น (`ref_ja` ใช้รูป ですます/ございます)
     ถ้าญี่ปุ่นเป็น**รูปธรรมดาชัดเจน** (だぜ · だろ · やがる) = ตก · ถ้าแค่ "ไม่พบรูปสุภาพ" = เตือน
     (คำตัดสิน lead 2 ก.ย. 2026 · PRONOUN_MATRIX §4 ข้อ 1 — คุมความหนาแน่นไม่ให้อ่านเกร็ง)
  H  ต้นฉบับมีคำต่อท้ายชื่อ (-san · -kun · -chan · -dono) แต่คำแปลไม่มี ซัง/คุง/จัง/ท่าน/ไอ้หนู
     (เฉพาะบทพูด) — ระดับความสัมพันธ์หายไปจากบทถ้าปล่อยผ่าน
  D  ตัวเลขอารบิกที่มีใน EN ควรอยู่ครบใน TH = เตือน (ไม่ตก เพราะบางที่แปลเป็นตัวหนังสือ)
  L  ยาวเกิน 1.8x ของ EN = เตือน (ไม่ตก)

ด่านที่ **ตัดทิ้งตอนพอร์ตจาก Lost Judgment** (2 ก.ย. 2026): X และ S ซึ่งผูกกับ donor slot map
ของฟอนต์ Dragon Engine · ภาคนี้เป็น UE4 + FreeType อ่าน UTF-8 ตรง ๆ ไม่มี slotmap ให้ตรวจ
ด่านระดับ batch (ตรวจทั้งไฟล์ ไม่ใช่ทีละคู่ — เพิ่ม 26 ส.ค. 2026):
  A1 ลำดับคีย์: ชุดคีย์และ**ลำดับ**ใน done ต้องตรงกับ worklist เป๊ะ
     คีย์หล่นไปหนึ่งตัวทำให้คำแปลที่เหลือ "เลื่อนไปผิดคีย์ทั้งแถว" โดยด่านคู่ต่อคู่ทั้ง 7 ด่านมองไม่เห็น
     (เกิดจริงกับ b124 ใน sprint 15 — คีย์ `Whiteboard Phone Number` หล่น คำแปล 200 บรรทัดเลื่อน)
     **ตกข้อนี้ = ทั้ง batch ไม่ถูกรวม** เพราะรวมไปก็ผิดคีย์หมด
  A2 สถิติจับคู่: สหสัมพันธ์ความยาว EN/TH — จับกรณีที่ลำดับคีย์ถูกแต่ค่าถูกวางเลื่อน
     รายละเอียดและค่าที่ใช้ตั้งเกณฑ์อยู่ใน `scripts/check_alignment.py`
TH == EN ถือว่า "คงต้นฉบับ" (ระบบ/enum/ชื่อเฉพาะ) — ผ่านทุกด่าน

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
import thai_pronouns as tp
from check_pronoun_pairs import check_text as pronoun_problems
from check_alignment import MIN_CORR as ALIGN_MIN_CORR
from check_alignment import SHIFT_WINS as ALIGN_SHIFT_WINS
from check_alignment import SHIFT_LOSES_BADLY as ALIGN_SHIFT_LOSES_BADLY
from check_alignment import _judge as align_judge
from check_alignment import _locate as align_locate

# ⚠ แท็กทรง ~...~ **ไม่มีในเกมนี้เลยสักแถว** (วัดทั้งคลัง 54,318 แถว = 0)
#   แต่รูปเดิมจับอักษรอะไรก็ได้ระหว่างขีด จึงไปจับคำไทยที่ลากเสียง ("สุ~ซุ~จัง")
#   เป็นแท็กเกิน แล้วด่าน T ตีตกบรรทัดที่ถูกต้อง (ผู้แปลก้อน MSG_053 รายงาน 3 ก.ย. 2026)
#   → จำกัดให้เนื้อในแท็กเป็น ASCII เท่านั้น (ยังรับแท็กจริงของภาคก่อนได้ถ้าโผล่มา)
TAG_RE = re.compile(r"<[^<>]*>|%[0-9]*\$?[sdxufi%]|\$\{[^}]*\}|~[!-}]{0,40}~")
CJK_RE = re.compile(r"[ᄀ-ᇿ぀-ヿ㐀-鿿가-힯ｦ-ﾟ]")
THAI_RE = re.compile(r"[฀-๿]")

DONE = paths.TRANSLATIONS / "done"
# บรรทัดที่ "ผสมระดับสรรพนามโดยตั้งใจ" (เช่น ตัวร้ายใช้ "คุณ" แบบประชด ขณะแทนตัวว่า "กู")
# ใส่ EN key ไว้ที่นี่พร้อมเหตุผล แล้วด่าน P จะข้ามให้ — ต้องมีเหตุผลกำกับเสมอ ห้ามใช้กลบความผิดพลาด
PRONOUN_EXCEPTIONS = paths.TRANSLATIONS / "pronoun_exceptions.json"
REPORT = paths.TRANSLATIONS / "qc_report.md"
FAILURES = paths.TRANSLATIONS / "qc_failures.json"


# บทพูดของตัวละครในยุค (ต้องใช้ภาษาบาคุมัตสึ) เทียบกับข้อความเมนู/ระบบ (ภาษาไทยปัจจุบัน)
# เส้นแบ่งอยู่ที่ช่อง `priority` ของ batch — PRONOUN_MATRIX §4 ข้อ 3
ERA_PRIORITIES = {1, 4, 9}

# รูปสุภาพของญี่ปุ่น — หลักฐานว่าบรรทัดนั้น "นอบน้อมจริง" จึงใส่ ขอรับ/เจ้าค่ะ ได้
POLITE_JA = ("です", "ます", "ません", "ました", "ましょ", "でしょ", "ございま", "くださ",
             "なさい", "いたしま", "おります", "ありません",
             # 下さい รูปคันจิ (119 แถว) · まして = te-form ของ ます (78 แถว)
             # — วัดแล้วเป็น ましてや (ไม่สุภาพ) แค่ 2 แถว จึงรับได้
             "下さ", "まして",
             # รูปสุภาพสำเนียงซัตสุมะ (ยามเฝ้าประตูสถานกงสุลพูดทั้งฉาก)
             # ⚠ ห้ามใส่ "もす" เปล่า — วัดแล้ว 62 แถว ส่วนใหญ่เป็นบวกปลอม (気もす · 何でもす)
             "ごわす", "ごわし", "ごわは", "しもす", "りもす", "じもす", "もはん", "もした",
             # รูปสุภาพสำเนียงคันไส (เกมนี้ตัวละครเกียวโต/โทสะพูดกันทั้งเกม) — สุภาพจริง ด่าน J ต้องนับด้วย
             "でっか", "まっせ", "まへん", "くだはれ", "ましたわ", "どすか",
             # รูปสุภาพโบราณของซามูไร — วัดทั้งคลังได้ 79 แถว ทุกแถวเป็น でござる
             # ไม่มีบวกปลอมเลย (ผู้แปลก้อน MSG_047 รายงาน 3 ก.ย. 2026)
             "ござる",
             # รูปพูดของ すみません (3 แถว) · รูปสุภาพคันไซเข้าชุดกับ でっか/まっせ (2 แถว)
             # · คำขอบคุณแบบซามูไร (4 แถว) — ผู้แปลก้อน MSG_052 รายงาน 3 ก.ย. 2026
             # (すんまへん 21 แถว เข้าเกณฑ์อยู่แล้วผ่าน "まへん")
             "すいやせん", "っしゃろ", "かたじけない",
             # รูปปฏิเสธของ ござる (ござらん) และคำลาแบบทางการ 御免 (19 แถว)
             # — ผู้แปลก้อน MSG_053 รายงาน 3 ก.ย. 2026
             "ござら", "御免")

# รูปสุภาพที่ต้องตัดข้อยกเว้นก่อน — ใส่ในทูเปิลตรง ๆ ไม่ได้เพราะจะชนคำที่ไม่สุภาพ
# どす = โคปูลาสุภาพสำเนียงเกียวโต (เจ้าของร้าน · นางคณิกา · อิคุมัตสึ พูดทั้งฉาก)
# ⚠ ต้องกัน どすこい (เสียงเชียร์ซูโม่) — วัดทั้งคลัง: どす 63 แถว · ในนั้น どすこい 12 แถว
# ตัวตรวจเดิมมีแต่ "どすか" จึงมองข้ามไป 33 แถว (ผู้ตรวจคลื่น MSG_073–075 รายงาน 3 ก.ย. 2026)
POLITE_JA_RE = re.compile(r"どす(?!こい)")
# รูปธรรมดา/หยาบที่ **ยืนยันได้ว่าไม่ใช่บทนอบน้อม** — เจอตัวใดตัวหนึ่ง + ไม่มีรูปสุภาพ = ตก
# ใช้รูปที่ผูกกับความห้วน/หยาบชัด ๆ เท่านั้น ไม่ใช่ "แค่ไม่เจอ ですます" (ซึ่งเป็นแค่คำเตือน)
PLAIN_JA = ("だぜ", "だろ", "だよ", "だな", "かよ", "じゃねえ", "じゃねぇ", "ねえよ", "やがる",
            "てめえ", "てめぇ", "ちくしょう", "うるせえ", "ふざけ", "しやがれ", "ぞ！", "ぜ！")

DIGITS_RE = re.compile(r"\d+")
# คำต่อท้ายชื่อของญี่ปุ่นที่ต้นฉบับอังกฤษยังเก็บไว้ — คำแปลต้องมีคำต่อท้ายไทยคู่กัน
# (กติกาใน glossary.md §1.2 · เคาะ 2 ก.ย. 2026) — ไม่งั้นระดับความสัมพันธ์หายไปจากบท
# วัดแล้วในคลื่นแรก: หลุดไป 19 จุดใน 3 batch โดยผู้ตรวจจับได้แค่จุดเดียว จึงต้องเป็นด่านอัตโนมัติ
HONORIFIC_EN = re.compile(r"-(san|kun|chan|dono|sama|han)(?![A-Za-z])", re.I)
HONORIFIC_TH = ("ซัง", "คุง", "จัง", "ท่าน", "ไอ้หนู")
# คำเรียกตำแหน่ง/บทบาทที่ EN เขียนติด -san แต่ **ไม่ใช่ชื่อคน** — ไทยแปลเป็นคำเรียกของตัวเอง
# ตามคำล็อกอยู่แล้ว จึงไม่ต้องมี ซัง/ท่าน ต่อท้าย (คลื่น 056–067: `Okami-san` = "แม่นาง")
HONORIFIC_TITLE_EN = re.compile(
    r"\b(okami|sensei|danna|oyaji|nee|nii|ojou|obaa|ojii|oka|otou|onee|onii)-",
    re.I)
# คำทับศัพท์ที่ลงท้าย -han/-san โดยบังเอิญ แต่ **ไม่ใช่ชื่อคน + คำต่อท้าย**
# (`Cho-han` 丁半 = ชื่อเกมทอยลูกเต๋า ล็อกไว้แล้วว่า "โชฮัง") — ก้อน MSG_004 โดนตีกลับเพราะข้อนี้
HONORIFIC_NOT_NAME_EN = re.compile(r"\b(cho|oicho|kabu|ban)-(han|san)\b", re.I)

# เครื่องหมายบอกเพศผู้พูดในต้นฉบับญี่ปุ่น — เป็นหลักฐานจากไฟล์เกม ลำดับที่ 2 ตาม
# docs/reference/gender_evidence_ishin.md (รองจากประวัติในแผนผัง he/she)
# ใช้แก้กรณีที่ไฟล์บริบทบอก neutral เพราะ *ไม่มีป้ายผู้พูด* ทั้งที่ต้นฉบับบอกเพศชัดเจน
# (เจอจริงในก้อน MSG_003: บทของตัวละครที่พูด 拙者/でござる ทุกบรรทัด = ซามูไรชาย)
# ⚠ わし ต้องตามด้วยคำช่วย ไม่งั้นจะไปตรงกับกลางคำกริยา (交わした = แลกเปลี่ยน/ให้สัญญา)
#   และ のよ ต้องกัน のような/のように (แปลว่า 'เหมือน' ไม่ใช่คำลงท้ายหญิง)
#   ทั้งสองเคสเจอจริงตอนลงน้ำเสียงหญิงลำลองในก้อน MSG_005 · MSG_006 (3 ก.ย. 2026)
JA_MALE_RE = re.compile(r"(拙者|でござる|ござるよ|ござるか|俺|オレ|おれ|オイ(?=[がのは])|僕|ぼく|ワシ|わし(?=[はがのもらやだ、。！？])|だぜ|だぞ|やがる|てめえ|ですぞ|であるか)")
# ⚠ วัดกับผู้พูดที่รู้เพศแน่นอน 6,382 บรรทัดแล้ว (3 ก.ย. 2026) — ผลที่ได้บังคับให้ตัดหลายคำทิ้ง:
#   ですわ / ますわ = **สำเนียงคันไซ ไม่ใช่คำหญิง** (ชาย 25/6 · เรียวมะพูดเองบ่อย) -> เอาออก
#   わ ท้ายประโยคเดี่ยว ๆ = ชาย 83 หญิง 41 -> ใช้เป็นหลักฐานไม่ได้เลย
#   わよ/わね ต้องกัน ますわよ・でしたわね (คันไซ) · だわ ต้องกัน こだわる · のよ ต้องกัน 〜んのよ (คันไซ)
#   ชุดที่เหลือ: ชาย 3 หญิง 28 (สามจุดที่เหลือเป็นป้ายผู้พูดที่ทะเบียนเพศผิด ไม่ใช่บั๊ก regex)
JA_FEMALE_RE = re.compile(r"(?<!お)かしら(?:って|[んね]?(?=[。！？…、」』〜～ーぁぃぅぇぉ\r\n]|$))|ですもの|あたし|アタシ|あたい|わたくし|ワタクシ|(?<!ます)(?<!です)(?<!した)わよ(?=ね|[。！？…、」』〜～ーぁぃぅぇぉ\r\n]|$)|(?<!ます)(?<!です)(?<!した)(?<![一-鿿])わね(?=[。！？…、」』〜～ーぁぃぅぇぉ\r\n]|$)|(?<!こ)だわ(?=[。！？…、」』〜～ーぁぃぅぇぉ\r\n]|$)|(?<![んンでだ])のよ(?=[。！？…、」』〜～ーぁぃぅぇぉ\r\n]|$)")
# คำไทยที่บอกเพศผู้พูด แยกฝั่ง — ใช้เทียบว่าตรงกับเพศที่ต้นฉบับญี่ปุ่นบอกไหม
TH_MALE_TOKENS = ("ขอรับ", "ผม", "กระผม")
TH_FEMALE_TOKENS = ("เจ้าค่ะ", "เจ้าคะ", "ดิฉัน", "ค่ะ", "คะ", "จ๊ะ", "จ้ะ")


QUOTE_RE = re.compile(r"[「『][^」』]*[」』]")


def ja_gender(ja):
    """เพศผู้พูดที่อ่านได้จากต้นฉบับญี่ปุ่น — "male" · "female" · None (ไม่ชี้ชัด)

    ตัดคำพูดที่ยกมาอ้างใน 「」 『』 ออกก่อนเสมอ — สรรพนามข้างในเป็นของ *คนที่ถูกอ้างถึง*
    ไม่ใช่ของผู้พูด (เจอจริงในก้อน MSG_008: บทซุบซิบของหญิงที่ยกคำพูดชายมาเล่า 「俺の後ろに立つな」)
    """
    if not ja:
        return None
    ja = QUOTE_RE.sub(" ", ja)
    m, f = bool(JA_MALE_RE.search(ja)), bool(JA_FEMALE_RE.search(ja))
    if m and not f:
        return "male"
    if f and not m:
        return "female"
    return None


# เพศผู้พูดระดับ "ไฟล์ฉาก" — สร้างด้วย scripts/build_scene_gender.py (ดูตัวเลขความแม่นในไฟล์นั้น)
# ใช้เป็นหลักฐานชั้นรองเมื่อบรรทัดนั้นเองไม่มีเครื่องหมาย แต่ทั้งฉากเป็นเพศเดียวล้วน
# แก้อาการที่ตัวละครเดียวกันได้คำลงท้ายบ้างไม่ได้บ้างสลับกันในฉากเดียว (เจอในก้อน MSG_012)
_SCENE_GENDER = None


def scene_gender(en):
    global _SCENE_GENDER
    if _SCENE_GENDER is None:
        p = paths.TRANSLATIONS / "scene_gender.json"
        _SCENE_GENDER = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    return _SCENE_GENDER.get(en)


_LINE_GENDER = None


def line_gender(en):
    """เพศที่ lead ล็อกไว้ "รายบรรทัด" — ชั้นหลักฐานสูงสุดของด่าน G

    มีไว้สำหรับบรรทัดที่พิสูจน์เพศได้จากไฟล์เกมด้วยหลักฐานที่เครื่องอ่านเองไม่ได้:
    ป้ายผู้พูดที่เป็นคำเรียกบอกเพศ (Mother · 巫女) · สรรพนามบุรุษที่สามในข้อความอังกฤษ
    ("interact with **her**" ในป้ายสายสัมพันธ์ · "(Oh, **she's** seeing somebody...)")
    ทุกคีย์ต้องมีช่อง `why` ที่อ้างไฟล์/บรรทัดในเกม — ไม่มี why = ไม่นับ (กัน "เดาแล้วล็อก")
    """
    global _LINE_GENDER
    if _LINE_GENDER is None:
        p = paths.TRANSLATIONS / "gender_lines.json"
        raw = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        _LINE_GENDER = {}
        for k, v in raw.items():
            if k.startswith("_") or not isinstance(v, dict):
                continue
            if v.get("gender") in ("male", "female") and v.get("why"):
                _LINE_GENDER[k] = v["gender"]
    return _LINE_GENDER.get(en)


def load_context(batch_id):
    """คืน dict EN -> ข้อมูลบริบทของ batch (`neutral` · `speakers` · `ja`) — ว่างถ้าไม่มีไฟล์"""
    if not isinstance(batch_id, str):
        return {}
    name = batch_id if batch_id.endswith(".json") else "batch_%s.json" % batch_id
    f = paths.WORKLIST / name.replace(".json", ".context.json")
    if not f.exists():
        return {}
    try:
        return json.load(io.open(f, encoding="utf-8")).get("lines", {})
    except Exception as e:  # noqa: BLE001 — ไฟล์บริบทเสียต้องไม่ทำให้ merge ทั้งรอบล้ม
        print("!! อ่านไฟล์บริบทไม่ได้ (ข้ามด่าน G): %s" % e)
        return {}


def load_exceptions():
    if PRONOUN_EXCEPTIONS.exists():
        return json.load(io.open(PRONOUN_EXCEPTIONS, encoding="utf-8"))
    return {}


def is_neutral(info):
    """บรรทัดนี้ต้องเขียนกลางเพศจริงไหม

    ตัวสร้างไฟล์บริบทตั้ง `neutral: true` เมื่อช่อง `gender` เป็น unknown — แต่บางบรรทัด
    ช่อง `speakers` ระบุผู้พูด **คนเดียว** พร้อมเพศชัดเจนอยู่แล้ว (เช่น Yamazaki · male)
    กรณีนี้เพศพิสูจน์ได้จากไฟล์เกม จึงใช้คำลงท้ายตามเพศได้ ไม่ใช่บรรทัดกลางเพศ
    (คลื่น 056–067: ด่าน G ตีกลับบรรทัดของยามาซากิที่ใส่ "ขอรับ" ถูกต้องแล้ว)

    ยังถือว่ากลางเพศเมื่อ: ไม่มีข้อมูลผู้พูดเลย · มีผู้พูดหลายคน · หรือผู้พูดคนเดียวที่ไม่รู้เพศ
    """
    if not info.get("neutral"):
        return False
    sp = info.get("speakers") or []
    if len(sp) == 1 and isinstance(sp[0], dict) and sp[0].get("gender") in ("male", "female"):
        return False
    return True


def check_pair(en, th, exceptions=(), ja=None, era=True, neutral=False):
    """ตรวจคู่ EN -> TH หนึ่งคู่ · คืน (รายการที่ตก, รายการคำเตือน)

    `ja`      ต้นฉบับญี่ปุ่นของบรรทัดนี้ (ช่อง ref_ja ของ batch) — ใช้ตัดสินด่าน J
    `era`     True = บทพูดของตัวละครในยุค (priority 1/4/9) · False = เมนู/ระบบ
    `neutral` True = ไฟล์บริบทสั่งให้แปลกลางเพศ (ห้ามคำลงท้ายบอกเพศ)
    """
    fails, warns = [], []
    if not isinstance(th, str) or not th.strip():
        return ["E: ว่าง"], warns

    if th == en:
        # คงต้นฉบับทั้งดุ้น = เขียนไบต์ชุดเดิมกลับลงไฟล์ ผลบนจอเท่ากับ "ไม่แตะคีย์นี้เลย"
        return fails, warns + ["= EN (คงต้นฉบับ)"]

    if en.count("\n") != th.count("\n"):
        fails.append("N: ขึ้นบรรทัดไม่เท่าต้นฉบับ (EN %d / TH %d)" % (en.count("\n"), th.count("\n")))

    en_tags, th_tags = Counter(TAG_RE.findall(en)), Counter(TAG_RE.findall(th))
    if en_tags != th_tags:
        miss = list((en_tags - th_tags).elements())
        extra = list((th_tags - en_tags).elements())
        fails.append("T: tag ไม่ตรง ขาด %s เกิน %s" % (miss or "-", extra or "-"))

    # ⚠ ต้นฉบับที่เป็นภาษาญี่ปุ่นล้วน (ไม่มีอักษรละตินเลย) = ตารางที่ทีมอังกฤษไม่ได้แปล
    # (นามสกุลศัตรู `stay_enemy_name_all` · พจนานุกรมในเกม `dictionary_word_list`)
    # ของพวกนี้ **ต้องแปล/ทับศัพท์ให้หมด** อักษรญี่ปุ่นจึงหายไปโดยตั้งใจ — ด่าน C ไม่ใช้กับกรณีนี้
    # (คลื่น 042–054 · ก้อน 051 · 052 · 053 · 054 ตกด่านนี้ทั้งที่คำแปลถูก)
    ja_only_source = bool(CJK_RE.search(en)) and not re.search(r"[A-Za-z]", en)
    en_cjk, th_cjk = Counter(CJK_RE.findall(en)), Counter(CJK_RE.findall(th))
    lost = en_cjk - th_cjk
    if lost and not ja_only_source:
        # หายทั้งหมด = ตั้งใจถอดเป็นไทย (ป้ายสองภาษา 言語設定/Language) -> เตือน
        # หายบางส่วน = น่าจะทำตกจริง (มีศัพท์ญี่ปุ่นหลายคำแล้วหายไปคำเดียว) -> ตก
        if not th_cjk:
            warns.append("C: อักษรญี่ปุ่น/CJK ในต้นฉบับถูกถอดเป็นไทยทั้งหมด %s"
                         % "".join(lost.elements()))
        else:
            fails.append("C: อักษรญี่ปุ่น/CJK หาย %s" % "".join(lost.elements()))

    # ⚠ ด่าน P ตั้งขึ้นสำหรับ "บทพูดหนึ่งบรรทัด" — เอกสารยาว (ตำราประวัติศาสตร์ · จดหมาย · บันทึก
    # ในตาราง `book_book`) มีหลายย่อหน้าและหลายน้ำเสียงในสตริงเดียว จึงมีทั้งคำนำหน้าบุคคลที่สาม
    # ("ท่านไทโร") และสรรพนามของผู้เขียนปนกันได้โดยไม่ผิด — ยกเว้นด่านนี้แล้วเตือนแทน
    # (คลื่น 042–054 · ก้อน 050: บทความสองชิ้นตกทั้งที่ถูกต้อง)
    is_document = len(en) > 400 or en.count(chr(10) + chr(10)) >= 2
    if en in exceptions:
        warns.append("P: ข้ามด่านสรรพนามตามรายการยกเว้น — %s" % exceptions[en])
    elif is_document:
        for pr in pronoun_problems(th):
            warns.append("P: (เอกสารยาว — เตือนอย่างเดียว) " + pr)
    else:
        for pr in pronoun_problems(th):
            fails.append("P: " + pr)

    old_end = tp.POLITE_OLD.search(th)
    # ป้ายชื่อเฉพาะ (นามสกุลทับศัพท์ ฯลฯ) ไม่ใช่ประโยค — ด่าน M/G ที่ตรวจสำนวนไม่มีอะไรให้ตรวจ
    # และจะตีกลับผิดเพราะ "คะ" ท้ายชื่อ (ฮาทานาคะ · โนนาคะ) ตรงกับคำลงท้ายสมัยใหม่พอดี
    name_label = tp.is_name_label(en, th)
    if era and not name_label:
        modern = tp.MODERN_SPEECH.findall(th)
        if modern:
            fails.append("M: บทพูดในยุคใช้คำของภาคปัจจุบัน %s (ต้องเป็น ข้า/ท่าน/เจ้า + ขอรับ/เจ้าค่ะ)"
                         % " ".join(sorted({m if isinstance(m, str) else m[0] for m in modern})))
        loan = tp.modern_loanwords(th)
        if loan:
            warns.append("M: คำยืมสมัยใหม่ในบทพูดยุคเก่า %s" % " ".join(loan))

    if neutral and not name_label:
        gendered = []
        if old_end:
            gendered.append(old_end.group(0))
        m = tp.MODERN_GENDERED.search(th)
        if m:
            gendered.append(m.group(0))
        fem = tp.FEM_CASUAL.search(th)
        if fem:
            gendered.append(fem.group(0))
        # ไฟล์บริบทตี neutral เมื่อ "ไม่มีป้ายผู้พูด" — แต่ต้นฉบับญี่ปุ่นอาจบอกเพศไว้เองชัด ๆ
        # (拙者/でござる = ซามูไรชาย · わよ/かしら = หญิง) ซึ่งเป็นหลักฐานจากไฟล์เกมลำดับที่ 2
        # ถ้าคำไทยตรงกับเพศที่ต้นฉบับบอก = ไม่ใช่การเดา -> ปล่อยผ่านเป็นคำเตือน
        # ถ้าสวนทางกับต้นฉบับ = ตกเหมือนเดิม (เป็นการเดาผิดจริง)
        jg = line_gender(en) or ja_gender(ja) or scene_gender(en)
        if gendered and jg:
            side = TH_MALE_TOKENS if jg == "male" else TH_FEMALE_TOKENS
            other = TH_FEMALE_TOKENS if jg == "male" else TH_MALE_TOKENS
            if any(t in th for t in side) and not any(t in th for t in other):
                warns.append("G: บริบทไม่มีป้ายผู้พูด แต่ต้นฉบับญี่ปุ่นบอกเพศ %s "
                             "และคำแปลใช้ฝั่งเดียวกัน (%s) — ผ่านตามหลักฐานในไฟล์เกม"
                             % (jg, " ".join(gendered)))
                gendered = []
        if gendered:
            fails.append("G: บรรทัดนี้ต้องกลางเพศ (neutral) แต่มีคำลงท้าย/สรรพนามบอกเพศ %s"
                         % " ".join(sorted(set(gendered))))

    if old_end and isinstance(ja, str) and ja.strip():
        ja_polite = any(m in ja for m in POLITE_JA) or bool(POLITE_JA_RE.search(ja))
        ja_plain = any(m in ja for m in PLAIN_JA)
        if not ja_polite and ja_plain:
            fails.append("J: ใส่ \"%s\" แต่ต้นฉบับญี่ปุ่นเป็นรูปธรรมดา/ห้วนชัดเจน — %s"
                         % (old_end.group(0), ja.replace("\n", " ")[:40]))
        elif not ja_polite:
            warns.append("J: ใส่ \"%s\" แต่ไม่พบรูป ですます ในต้นฉบับญี่ปุ่น — %s"
                         % (old_end.group(0), ja.replace("\n", " ")[:40]))

    if (era and HONORIFIC_EN.search(en) and not HONORIFIC_TITLE_EN.search(en)
            and not HONORIFIC_NOT_NAME_EN.search(en)
            and not any(h in th for h in HONORIFIC_TH)):
        fails.append("H: ต้นฉบับมีคำต่อท้ายชื่อ %s แต่คำแปลไม่มี ซัง/คุง/จัง/ท่าน"
                     % " ".join(sorted({m.group(0) for m in HONORIFIC_EN.finditer(en)})))

    en_digits, th_digits = Counter(DIGITS_RE.findall(en)), Counter(DIGITS_RE.findall(th))
    if en_digits - th_digits:
        warns.append("D: ตัวเลขที่มีใน EN ไม่พบใน TH %s"
                     % " ".join((en_digits - th_digits).elements()))

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
        corr_bad = r["corr"] < ALIGN_MIN_CORR and r["diff"] > ALIGN_SHIFT_LOSES_BADLY
        if corr_bad or r["diff"] > ALIGN_SHIFT_WINS or len(wins) >= 2:
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
    ap.add_argument("--only", action="append", default=None,
                    help="ชื่อก้อน เช่น 003 หรือ MSG_007 (ใส่ซ้ำได้หลายก้อน) — จับชื่อไฟล์แบบตรงตัวก่อน")
    ap.add_argument("--status", action="store_true",
                    help="รายงานว่าไฟล์ done ไหนยัง 'ไม่ตรง' master (ต้อง merge ซ้ำ) แล้วออก — ไม่เขียนอะไร")
    a = ap.parse_args()

    if a.status:
        return report_status()

    exceptions = load_exceptions()
    master = json.load(io.open(paths.MASTER_TH, encoding="utf-8")) if paths.MASTER_TH.exists() else {}
    master = OrderedDict(master)

    files = sorted(DONE.glob("*.done.json")) if DONE.exists() else []
    if a.only:
        # ตรงตัวก่อนเสมอ — "--only 022" เคยกิน batch_MSG_022 ไปด้วยเพราะจับแบบ substring
        picked, missing = [], []
        for name in a.only:
            exact = [f for f in files if f.name == "batch_%s.done.json" % name]
            if exact:
                picked += exact
                continue
            loose = [f for f in files if name in f.name]
            if loose:
                print("⚠ --only %s ไม่ตรงชื่อไฟล์ใด จับแบบคร่าว ๆ ได้ %s"
                      % (name, " · ".join(f.name for f in loose)))
                picked += loose
            else:
                missing.append(name)
        if missing:
            print("ไม่พบก้อน: %s" % " · ".join(missing))
        files = sorted(set(picked))
    if not files:
        print("ไม่พบไฟล์ใน translations/done/ (ยังไม่มีคำแปลส่งเข้ามา)")
        return 0

    added = kept = failed = 0
    failures = OrderedDict()
    lines = ["# QC report — ISHTH", ""]
    for f in files:
        data = json.load(io.open(f, encoding="utf-8"))
        strings = data.get("strings", data)
        batch_id = data.get("batch", f.name)
        name = batch_id if isinstance(batch_id, str) and batch_id.endswith(".json") \
            else "batch_%s.json" % batch_id
        src = paths.WORKLIST / name if isinstance(batch_id, str) else None
        expected, ref_ja, era = None, {}, True
        if src and src.exists():
            wl = json.load(io.open(src, encoding="utf-8"))
            expected = list(wl["strings"].keys())
            ref_ja = wl.get("ref_ja") or {}
            era = wl.get("priority") in ERA_PRIORITIES
        else:
            print("%-32s !! ไม่พบไฟล์ worklist คู่กัน — ข้ามด่าน A1/J/M/G" % f.name)
        ctx = load_context(batch_id)

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
            info = ctx.get(en) or {}
            fails, warns = check_pair(en, th, exceptions,
                                      ja=ref_ja.get(en) or info.get("ja"),
                                      era=era, neutral=is_neutral(info))
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
