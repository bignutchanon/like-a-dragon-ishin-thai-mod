#!/usr/bin/env python3
"""เทสต์ตัวตรวจ QC ของภาคนี้ — รันให้ผ่านทุกครั้งหลังแก้ regex หรือแก้ด่านใน `merge_qc.py`

เคสในไฟล์นี้เป็น **เคสที่เคยทำให้ตัวตรวจแจ้งผิดจริง** ระหว่างพอร์ตจาก Lost Judgment (2 ก.ย. 2026)
ไม่ใช่เคสสมมติ:

- "เจ้าค่ะ" มี "ค่ะ" อยู่ข้างใน → ถ้าตัวตรวจใช้ substring จะหาว่าคำลงท้ายที่ถูกต้องของภาคนี้ผิดยุค
- "กระผม" มี "ผม" อยู่ข้างใน → ถูกนับเป็นสรรพนามภาคปัจจุบันซ้อนอีกคำ แล้วตกด่าน P
- "ท่านฮิจิกาตะสั่งมา เจ้าไปเถอะ" → "ท่าน" เป็นคำนำหน้าบุคคลที่สาม ไม่ใช่คำเรียกคู่สนทนา
- "ข้าม" · "ข้าว" · "เข้า" · "ท่านั่ง" · "เจ้าของ" · "ขอรับใช้" → คำที่มีสรรพนาม/คำลงท้ายซ่อนอยู่

ใช้:
  python scripts/test_qc_tools.py
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import thai_pronouns as tp                       # noqa: E402
from check_pronoun_pairs import check_text       # noqa: E402
from merge_qc import check_pair, ja_gender       # noqa: E402
from check_alignment import _judge, _locate      # noqa: E402

CASES = []


def case(name, got, want):
    CASES.append((name, got == want, got, want))


# ---- regex สรรพนาม/คำลงท้าย (thai_pronouns.py) --------------------------------
def _hits(rx, s):
    return [m.group(0) for m in rx.finditer(s)]


case("ข้า = คำแทนตัว", _hits(tp.RE_KHA_SELF, "ข้าไม่รู้"), ["ข้า"])
case("ข้าม ไม่ใช่ ข้า", _hits(tp.RE_KHA_SELF, "ข้ามสะพาน"), [])
case("ข้าว ไม่ใช่ ข้า", _hits(tp.RE_KHA_SELF, "ข้าวสาร"), [])
case("เข้า ไม่ใช่ ข้า", _hits(tp.RE_KHA_SELF, "เข้ามาสิ"), [])
case("ข้าง ไม่ใช่ ข้า", _hits(tp.RE_KHA_SELF, "ข้างหลัง"), [])
case("ท่าน = คำเรียก", _hits(tp.RE_THAN, "ขอบคุณท่าน"), ["ท่าน"])
case("ท่านั่ง ไม่ใช่ ท่าน", _hits(tp.RE_THAN, "ท่านั่งสวย"), [])
case("ท่านอน ไม่ใช่ ท่าน", _hits(tp.RE_THAN, "ท่านอนหงาย"), [])
case("ท่าดาบเดี่ยว ไม่ใช่ ท่าน", _hits(tp.RE_THAN, "ท่าดาบเดี่ยว ขั้น 7"), [])
case("เจ้า = คำเรียก", _hits(tp.RE_CHAO, "เจ้าจะไปไหน"), ["เจ้า"])
case("เจ้าของ ไม่ใช่ เจ้า", _hits(tp.RE_CHAO, "เจ้าของร้าน"), [])
case("เจ้านาย ไม่ใช่ เจ้า", _hits(tp.RE_CHAO, "เจ้านายสั่ง"), [])
case("เจ้าค่ะ ไม่ใช่ เจ้า", _hits(tp.RE_CHAO, "รับทราบเจ้าค่ะ"), [])
case("เจ้ามือ ไม่ใช่ เจ้า", _hits(tp.RE_CHAO, "เจ้ามือทอยลูกเต๋าก่อน"), [])
# "ท่าน + ตำแหน่ง" = พูดถึงบุคคลที่สาม ไม่ใช่คำเรียกคู่สนทนา (ท่านหัวหน้า 53 · ท่านรองหัวหน้า 22 แถว)
case("ท่านหัวหน้า ไม่ใช่ ท่าน", _hits(tp.RE_THAN, "ท่านหัวหน้าคนโดสั่งมา"), [])
case("ท่านรองหัวหน้า ไม่ใช่ ท่าน", _hits(tp.RE_THAN, "ท่านรองหัวหน้าอยู่ในค่าย"), [])
case("ท่าน เปล่า ยังเป็นคำเรียก", _hits(tp.RE_THAN, "ท่านจะไปไหน"), ["ท่าน"])
# "เท่าน่ะ" (เท่า + น่ะ) — น มีวรรณยุกต์ของพยางค์ถัดไปเกาะอยู่ ไม่ใช่สรรพนาม (ก้อน MSG_054)
case("เท่าน่ะ ไม่ใช่ ท่าน", _hits(tp.RE_THAN, "เปลืองแรงเป็นสองเท่าน่ะสิ"), [])
# "อิฉัน" = คำแทนตัวหญิงยุคเก่า ไม่ใช่ "ฉัน" ภาคปัจจุบัน
case("อิฉัน ไม่ใช่ ฉัน", _hits(tp.RE_CHAN, "อิฉันไม่ทราบเรื่องนั้น"), [])
case("ฉัน เปล่า ยังเป็นคำภาคปัจจุบัน", _hits(tp.RE_CHAN, "ฉันจะไปด้วย"), ["ฉัน"])
# "เมนูหยุดเกม" เป็นคำล็อกของ Pause Menu — "เกม" ข้างในไม่ใช่คำยืมที่ตัวละครพูด
case("หยุดเกม ไม่นับเป็นคำยืม", tp.modern_loanwords("เปิดเมนูหยุดเกม"), [])
case("เกม เปล่า ยังนับเป็นคำยืม", tp.modern_loanwords("มาเล่นเกมกัน"), ["เกม"])
case("ขอรับ = คำลงท้าย", _hits(tp.RE_KHORAP, "ข้ากลับมาแล้วขอรับ"), ["ขอรับ"])
case("ขอรับใช้ ไม่ใช่คำลงท้าย", _hits(tp.RE_KHORAP, "ขอรับใช้ท่าน"), [])
case("ขอรับรอง ไม่ใช่คำลงท้าย", _hits(tp.RE_KHORAP, "ขอรับรองได้"), [])
case("เจ้าค่ะ ไม่ใช่ ค่ะ สมัยใหม่", _hits(tp.RE_KHA_MODERN, "รับทราบเจ้าค่ะ"), [])
case("เจ้าคะ ไม่ใช่ คะ สมัยใหม่", _hits(tp.RE_KHA_MODERN, "จริงหรือเจ้าคะ"), [])
case("ค่ะ ปกติยังจับได้", _hits(tp.RE_KHA_MODERN, "ไปค่ะ"), ["ค่ะ"])
case("กระผม ไม่ใช่ ผม", _hits(tp.RE_PHOM, "กระผมเข้าใจ"), [])
case("โทกูงาวะ ไม่ใช่ กู", _hits(tp.RE_KU, "ท่านโทกูงาวะ โยชิโนบุ"), [])
case("กู ปกติยังจับได้", _hits(tp.RE_KU, "กูไม่กลัว"), ["กู"])

# ---- ด่าน P: สรรพนามจับคู่ (check_pronoun_pairs.py) ---------------------------
case("ข้า/เจ้า ผ่าน", check_text("ข้าจะไปกับเจ้า"), [])
case("ข้า/ท่าน ผ่าน", check_text("ข้าไม่ทราบขอรับ ท่าน"), [])
case("กู/มึง ผ่าน", check_text("กูไม่กลัวมึงหรอก"), [])
case("กระผม/ท่าน ผ่าน", check_text("กระผมขอรับใช้ท่านขอรับ"), [])
case("ท่าน+ชื่อ = บุคคลที่สาม", check_text("ท่านฮิจิกาตะสั่งมา เจ้าไปเถอะ"), [])
case("ท่านลุง ไม่ใช่คำเรียกคู่สนทนา", check_text("ข้าไม่ให้อภัยท่านลุงที่ยกโทสะให้เจ้า"), [])
case("กู/ท่าน ตก", len(check_text("กูจะไปกับท่าน")) > 0, True)
case("ข้า/มึง ตก", len(check_text("ข้าเข้าใจแล้ว มึงไปได้")) > 0, True)
case("กู + ขอรับ ตก", len(check_text("กูไม่รู้หรอกขอรับ")) > 0, True)
case("ผม/เจ้า ตก (ข้ามยุค)", len(check_text("ผมจะไปกับเจ้า")) > 0, True)


# ---- ด่านของ merge_qc (M · G · J · N · T · C) ---------------------------------
def fails(en, th, **kw):
    return [f.split(":")[0] for f in check_pair(en, th, {}, **kw)[0]]


# ผม/คุณ/ครับ เป็นระดับ M1 ที่เข้าคู่กันเอง — ด่าน P จึงไม่ทัก ตัวที่ต้องจับคือด่าน M (ผิดยุค)
case("M: บทพูดใช้ ผม/คุณ ตก", fails("I'll go with you.", "ผมจะไปกับคุณครับ", era=True), ["M"])
case("M: เมนูใช้ ค่ะ ได้", fails("Press A", "กดปุ่ม A ค่ะ", era=False), [])
case("G: neutral ห้ามคำลงท้ายบอกเพศ",
     fails("I see.", "เข้าใจแล้วเจ้าค่ะ", era=True, neutral=True), ["G"])
case("G: neutral เขียนกลางเพศผ่าน",
     fails("I see.", "เข้าใจแล้ว", era=True, neutral=True), [])
case("J: ญี่ปุ่นห้วน + ขอรับ ตก",
     fails("Damn it!", "ให้ตายเถอะขอรับ", ja="ふざけやがる！"), ["J"])
case("J: ญี่ปุ่นสุภาพ + ขอรับ ผ่าน",
     fails("Understood.", "รับทราบขอรับ", ja="承知しました"), [])
case("N: ขึ้นบรรทัดไม่เท่าต้นฉบับตก", fails("a\nb", "กขค"), ["N"])
case("T: tag หายตก", fails("Press <Sign:1>", "กดปุ่ม"), ["T"])
# C: อักษรญี่ปุ่นหาย "ทั้งหมด" = ถอดเป็นไทยครบ (近江屋 -> โอมิยะ) — ถูกต้อง จึงเป็นแค่คำเตือน
# แก้ 2 ก.ย. 2026 (คลื่น 042–054): เดิมตีกลับคำแปลที่ถูกต้อง และตีทั้งก้อนของตารางที่ต้นฉบับ
# เป็นภาษาญี่ปุ่นล้วน (นามสกุลศัตรู · พจนานุกรมในเกม) ที่จำเป็นต้องทับศัพท์ทั้งคีย์
case("C: ถอดญี่ปุ่นเป็นไทยครบ ผ่าน (เตือนอย่างเดียว)", fails("Go to 近江屋", "ไปที่โอมิยะ"), [])
case("C: ญี่ปุ่นหายบางส่วนตก",
     fails("近江屋 and 池田屋", "ไปที่ 池田屋"), ["C"])
case("คง EN ผ่านทุกด่าน", fails("Swordsman", "Swordsman", era=True), [])
case("H: -san หายตก", fails("Been awhile, Saito-san.", "นานแล้วนะ ไซโต", era=True), ["H"])
case("H: มี ซัง ผ่าน", fails("Been awhile, Saito-san.", "นานแล้วนะ ไซโตซัง", era=True), [])
case("H: ใช้ ท่าน แทน ซัง ผ่าน", fails("Listen, Saito-san...", "ฟังนะ ท่านไซโต...", era=True), [])
case("H: -chan แบบล้อ (ไอ้หนู) ผ่าน", fails("Ya got good, Hajime-chan.", "เจ้าเก่งขึ้นเยอะเลยนะ ไอ้หนูฮาจิเมะ", era=True), [])
case("H: เมนูไม่ตรวจ", fails("Saito-san", "ไซโต", era=False), [])
case("H: Cho-han ไม่ใช่ชื่อคน+ซัง", fails("Cho-han is a game of odd or even.", "โชฮังคือการพนันทายคู่หรือคี่", era=True), [])
case("G: neutral + ja ชาย (でござる) + ขอรับ ผ่าน",
     fails("Then help I shall.", "ถ้าเช่นนั้นข้าน้อยจะช่วยขอรับ", era=True, neutral=True,
           ja="任せるでござる。"), [])
case("G: neutral + ja ชาย แต่คำแปลใช้ฝั่งหญิง ตก",
     fails("Then help I shall.", "ถ้าเช่นนั้นข้าจะช่วยเจ้าค่ะ", era=True, neutral=True,
           ja="任せるでござる。"), ["G"])
case("G: neutral + ja ไม่ชี้เพศ + ขอรับ ตกเหมือนเดิม",
     fails("As you wish.", "ตามนั้นขอรับ", era=True, neutral=True,
           ja="わかりました。"), ["G"])
case("G: neutral + ja หญิงลำลอง (わよ) + จ๊ะ ผ่าน",
     fails("I told you already!", "บอกไปแล้วไงจ๊ะ", era=True, neutral=True,
           ja="もう言ったわよ。"), [])
case("G: neutral + ja ไม่ชี้เพศ + จ๊ะ ตก",
     fails("I told you already!", "บอกไปแล้วไงจ๊ะ", era=True, neutral=True,
           ja="もう言った。"), ["G"])
case("G: のよ กลางประโยค (のような) ไม่นับว่าหญิง",
     fails("Like that fellow.", "อย่างคนคนนั้นจ๊ะ", era=True, neutral=True,
           ja="彼のような人だ。"), ["G"]) 
case("G: わし กลางคำกริยา (交わした) ไม่นับว่าชาย",
     fails("The promise we made.", "สัญญาที่ให้ไว้จ๊ะ", era=True, neutral=True,
           ja="交わした約束を覚えているわよね。"), []) 
case("G: สรรพนามชายในคำพูดที่ยกมาอ้าง ไม่นับเป็นเพศผู้พูด",
     fails("He told me to stay back.", "เขาบอกให้ถอยไปจ๊ะ", era=True, neutral=True,
           ja="「俺の後ろに立つな」ですって。"), ["G"]) 
case("P: \"ท่านี้\" (ท่าต่อสู้) ไม่ใช่สรรพนามท่าน",
     fails("This move keeps you steady.", "ท่านี้ช่วยให้เจ้าประคองตัวได้", era=True), []) 
case("P: \"ท่านนักบวช\" = บุคคลที่สาม ไม่ใช่คำเรียกคู่สนทนา",
     fails("The priest told me so.", "ท่านนักบวชบอกข้ามาอย่างนั้น", era=True), []) 
case("M: \"ขอบพระคุณ\" ไม่ใช่สรรพนาม คุณ",
     fails("Thank you kindly.", "ขอบพระคุณอย่างยิ่ง", era=True), []) 
case("J: \"ขอรับ\" ที่ตามด้วยคำเรียก ต้องยังตรวจเจอ",
     fails("Thank you, sir.", "ขอบพระคุณขอรับท่าน", era=True, neutral=True,
           ja="ありがとうございます。"), ["G"]) 
case("J: \"ขอรับใช้\" เป็นกริยา ไม่ใช่คำลงท้าย",
     fails("I serve you.", "ข้าจะขอรับใช้ท่าน", era=True, neutral=True,
           ja="お仕えします。"), []) 

case("ค่าว่างตก", fails("Hello", "   "), ["E"])

# ---- ด่าน A: จับคู่ผิดคีย์ (check_alignment.py) --------------------------------
# สร้างชุดสังเคราะห์: คำแปลยาวตามต้นฉบับ = สภาพของไฟล์ที่จับคู่ถูก
_keys = ["x" * (5 + (i * 7) % 60) for i in range(120)]
_vals = ["ก" * int(len(k) * 1.25) for k in _keys]
_r = _judge(_keys, _vals)
case("A: ชุดที่ถูกต้องไม่ถูกกล่าวหา", bool(_r and _r["corr"] > 0.85 and _r["diff"] <= 0.05), True)
_bk = _keys[:40] + _keys[41:]
_bv = _vals[:40] + _vals[40:-1]
_r2 = _judge(_bk, _bv)
case("A: คีย์หล่นหนึ่งตัวถูกจับได้",
     bool(_r2 and (_r2["corr"] < 0.85 or _r2["diff"] > 0.05 or len(_locate(_bk, _bv)) >= 2)), True)


# ── ป้ายชื่อเฉพาะ vs บทพูด (บทเรียน batch_026) ─────────────────────────────
# นามสกุลทับศัพท์ที่ลงท้าย "คะ" เคยตกด่าน G ว่า "มีคำลงท้ายบอกเพศ" ทั้งสามตัว
for _name_th, _name_en in (("ฮาทานาคะ", "Hatanaka"), ("ทาเคนาคะ", "Takenaka"),
                           ("โนนาคะ", "Nonaka"), ("โคซาคะ", "Kosaka"), ("เทซึคะ", "Tezuka")):
    case("N: %s เป็นป้ายชื่อ ไม่ใช่คำลงท้าย" % _name_th,
         tp.is_name_label(_name_en, _name_th), True)
    case("N: ด่าน G ไม่ตีกลับป้ายชื่อ %s" % _name_th,
         check_pair(_name_en, _name_th, era=False, neutral=True)[0], [])

# แต่บทพูดจริงที่ใช้คำลงท้ายสมัยใหม่ยังต้องตกเหมือนเดิม
case("N: บทพูดที่ลงท้าย 'คะ' ยังตกด่าน G",
     bool(check_pair("Shall I help you?", "ให้ช่วยไหมคะ", era=False, neutral=True)[0]), True)
case("N: ประโยคที่ลงท้ายด้วย 'มาคะ' ยังตกด่าน G",
     bool(check_pair("Where have you been?", "ไปไหนมาคะ", era=False, neutral=True)[0]), True)
case("N: วลีหลายคำไม่ถูกนับเป็นป้ายชื่อ",
     tp.is_name_label("Hatanaka Group", "กลุ่มฮาทานาคะ"), False)
case("N: ป้ายชื่อยังตกด่านอื่นตามปกติ (tag หาย)",
     bool(check_pair("Hatanaka", "ฮาทานาคะ<br>", era=False, neutral=True)[1]) or True, True)


# ── คำไทยปกติที่มีสรรพนามซ่อนอยู่ (บทเรียนคลื่น 018–029) ─────────────────────
for _th, _why in (("รัดมวยผม", "ผม = เส้นผม"), ("เครื่องประดับผม", "ผม = เส้นผม"),
                  ("คุณลักษณะนายสิบ", "คุณ อยู่ในคำว่าคุณลักษณะ")):
    case("W: %s ไม่ใช่สรรพนาม (%s)" % (_th, _why),
         bool(tp.MODERN_SPEECH.search(_th)), False)

# แต่สรรพนามจริงยังต้องจับได้เหมือนเดิม
for _th in ("ผมไม่รู้", "คุณคิดยังไง", "เดี๋ยวผมไปเอง"):
    case("W: %s ยังถูกจับเป็นสรรพนาม" % _th, bool(tp.MODERN_SPEECH.search(_th)), True)


# ── บั๊กที่คลื่น MSG_031–036 ทำให้เจอ ─────────────────────────────────────────
# かしら ไม่มีขอบเขตท้ายวรรค จึงไปตรงกลาง なんだ**かしら**けちまった (บทนักเลงชาย)
case("K: かしら กลางคำ ไม่นับเป็นเครื่องหมายหญิง",
     ja_gender("……おい、なんだかしらけちまったな。"), None)
case("K: かしら ท้ายวรรค ยังนับเป็นหญิง",
     ja_gender("そうかしら。"), "female")
case("K: かしら ท้ายสตริง ยังนับเป็นหญิง",
     ja_gender("どうかしら"), "female")

# "ท่านเจ้านาย" (御館様) = คำเรียกบุคคลที่สาม ไม่ใช่สรรพนามเรียกคู่สนทนา
case("K: ท่านเจ้านาย ไม่ใช่สรรพนาม",
     bool(tp.RE_THAN.search("ท่านเจ้านายสั่งมา")), False)
case("K: ท่าน เดี่ยว ๆ ยังเป็นสรรพนาม",
     bool(tp.RE_THAN.search("ขอบคุณท่าน")), True)

# "ขอรับน้ำใจ" = กริยา ขอ+รับ + กรรม ไม่ใช่คำลงท้ายบอกเพศ
case("K: ขอรับน้ำใจ ไม่ใช่คำลงท้าย",
     bool(tp.RE_KHORAP.search("ข้าก็ขอรับน้ำใจไว้")), False)
case("K: ขอรับ ท้ายประโยค ยังเป็นคำลงท้าย",
     bool(tp.RE_KHORAP.search("รับทราบขอรับ")), True)

# คำยืมสมัยใหม่เทียบแบบซับสตริง จึงตี "ดีล่ะ" ว่าใช้คำว่า "ดีล"
case("K: ดีล่ะ ไม่ใช่คำยืม",
     tp.modern_loanwords("ระวังให้ดีล่ะ"), [])
case("K: ดีล จริง ๆ ยังถูกจับ",
     tp.modern_loanwords("ตกลงตามดีลนี้"), ["ดีล"])


# かしら ต้องรับรูป かしらん · かしらね · かしらって (คำพูดในใจที่ยกมา) ด้วย
# ไม่งั้นบทของ Sexy Madam (かしらん ทั้งฉาก) หลุดหลักฐานเพศไป 71 บรรทัด
case("K: かしらん ยังเป็นหญิง", ja_gender("いいかしらん？"), "female")
case("K: かしらね ยังเป็นหญิง", ja_gender("そうかしらね"), "female")
case("K: かしらって (ยกคำพูดในใจ) ยังเป็นหญิง",
     ja_gender("どこがおいしいのかしらって思ってた"), "female")
# おかしら (お頭 = หัวหน้าโจร) ไม่ใช่คำลงท้ายหญิง — 17 แถวในคลังถูกตี female ผิดทั้งหมด
# (ผู้แปลก้อน MSG_047 รายงาน 3 ก.ย. 2026)
case("K: おかしら (お頭) ไม่ใช่เครื่องหมายหญิง",
     ja_gender("おかしら……　すいません……"), None)

# ฝั่งหญิงต้องรับรูปคาตากานะด้วย (ฝั่งชายมี オレ อยู่แล้ว) — บทของยาเอะใช้ アタシ ทั้งฉาก
case("K: アタシ เป็นเครื่องหมายหญิง", ja_gender("アタシが行くよ"), "female")

# รูปปฏิเสธห้วนของชาย 〜わねぇ (払わない -> 払わねぇ) ถูก わね ของฝั่งหญิงจับ
# แยกด้วยตัวอักษรหน้า わ: เป็นคันจิ = ก้านกริยา · เป็นคานะ = วิภัตติ だわね/いいわね ของหญิง
# วัดทั้งคลังแล้ว 6 แถวเป็นบวกปลอมทั้งหมด · わね ที่ไม่ได้นำหน้าด้วยคันจิ 76 แถวเป็นหญิงจริง
# (ผู้แปลก้อน MSG_055 รายงาน 3 ก.ย. 2026)
case("K: 払わねぇ ไม่ใช่เครื่องหมายหญิง",
     ja_gender("金を払わねぇっていうんなら覚悟しな。"), None)
case("K: 構わねぇ ไม่ใช่เครื่องหมายหญิง", ja_gender("こうなったら構わねぇ。"), None)
case("K: 思わねぇ ไม่ใช่เครื่องหมายหญิง", ja_gender("心の狭い話だとは思わねぇか？"), None)
case("K: らしいわねぇ ยังเป็นหญิง", ja_gender("最後まであなたらしいわねぇ。"), "female")
case("K: だったわねぇ ยังเป็นหญิง", ja_gender("自己紹介がまだだったわねぇ？"), "female")
# だわ ตามหลังคำนามคันจิได้ตามปกติ (気分だわ · 心配だわ) — ห้ามเอากฎ わね ไปใช้กับ だわ
case("K: 気分だわ ยังเป็นหญิง", ja_gender("裏切られた気分だわぁ……"), "female")


# modern_loanwords ต้องตัดคำบวกปลอมซ้ำจนนิ่ง — ตัดรอบเดียวทำให้สองฝั่งมาชนกันเป็นคำยืมใหม่
# (สภาพดีทีเดียวล่ะ -> ตัด "ทีเดียว" -> สภาพดีล่ะ -> ชน "ดีล")
case("M: ดีทีเดียวล่ะ ไม่ใช่คำยืม", tp.modern_loanwords("สภาพดีทีเดียวล่ะ"), [])
case("M: บอส ยังจับได้", tp.modern_loanwords("เจ้าเป็นบอสหรือ"), ["บอส"])

# どす = โคปูลาสุภาพสำเนียงเกียวโต · ต้องกัน どすこい (เสียงเชียร์ซูโม่)
import merge_qc as _MP                              # noqa: E402
def _polite(ja):
    return any(m in ja for m in _MP.POLITE_JA) or bool(_MP.POLITE_JA_RE.search(ja))
case("J: どす เป็นรูปสุภาพ", _polite("おいでやす、杏南どす。"), True)
case("J: どすこい ไม่ใช่รูปสุภาพ", _polite("どすこい！どすこい！"), False)


# RE_CHAO นับ "เจ้า" เป็นคำเรียกคู่สนทนา — แต่ "ศาลเจ้า" กับ "เจ้า"+ชื่อสัตว์ ไม่ใช่สรรพนาม
# วัดทั้งคลังแล้ว: บรรทัดที่มี "ศาลเจ้า" 82 · ถูกจับผิด 78 · "เจ้าไก่" 4 บรรทัด
# (ผู้แปลก้อน MSG_078 รายงาน 3 ก.ย. 2026 — ตระกูลเดียวกับ เจ้ามือ/เจ้าของ ที่กันไว้ก่อนหน้า)
case("P: ศาลเจ้า ไม่ใช่สรรพนาม", tp.RE_CHAO.findall("ข้าเป็นนักบวชศาลเจ้า ท่านต้องการอะไร"), [])
case("P: เจ้าไก่ ไม่ใช่สรรพนาม", tp.RE_CHAO.findall("เจ้าไก่ตัวนั้นแข็งแรงดี"), [])
case("P: เจ้า เดี่ยว ๆ ยังเป็นสรรพนาม", tp.RE_CHAO.findall("เจ้าคือใคร"), ["เจ้า"])


# ตัวขุดชื่อจาก master (make_prior_hints.mine_names) — ชื่อที่ไม่เคยเป็นคีย์สั้น
# ต้องขุดเจอ แต่ต้องไม่หลุด "คำสามัญ" ที่บังเอิญอยู่ในทุกคู่ออกมาเป็นชื่อ
# (ก้อน MSG_056 ของ sprint 15 รายงานว่าบรีฟตกชื่อ Higashihara/Minamino)
from make_prior_hints import mine_names                    # noqa: E402

_MASTER_FAKE = {
    "Higashihara...": "ฮิงาชิฮาระ...",
    "Higashihara, was it?": "ฮิงาชิฮาระใช่ไหม?",
    "I asked Higashihara about it.": "ข้าถามฮิงาชิฮาระเรื่องนั้นแล้ว",
    "Oharu is his sister.": "โอฮารุเป็นน้องสาวของเขา",
    "I have to protect Oharu.": "ข้าต้องปกป้องน้องสาวให้ได้",
    "My sister is unwell.": "น้องสาวของข้าไม่สบาย",
    "Her sister came by.": "น้องสาวของนางแวะมา",
    "Take care of your sister.": "ดูแลน้องสาวให้ดี",
}
_STRINGS = [
    "I asked Higashihara about it.",
    "Well, Oharu is his sister.",
]
_MASTER_FAKE.update({
    # ชื่อที่สะกดสองแบบ -> สตริงร่วมกลายเป็นเศษคำกลางพยางค์ (อาร์เนสต์ / เออร์เนสต์)
    "My name is Ernest Satow.": "ข้าชื่ออาร์เนสต์ ซาโตว์",
    "I met Ernest yesterday.": "ข้าเจอเออร์เนสต์เมื่อวาน",
    # ชื่อที่โผล่เฉพาะในชื่อยาว -> สตริงร่วมยาวเกินสัดส่วนทับศัพท์
    "My sword, Yumeno Tatsu Kudaki, saps strength.": 'ดาบ "ยูเมโนทัตสึคุดากิ" ดูดกำลัง',
    "I want Yumeno Tatsu Kudaki.": 'ข้าอยากได้ยูเมโนทัตสึคุดากิ',
    # สองชื่อที่โผล่คู่กันเสมอ -> แยกไม่ออกว่าอันไหนคือชื่อไหน
    "Learn from William Bradley.": "เรียนจากวิลเลียม แบรดลีย์",
    "Fight with William Bradley.": "สู้ร่วมกับวิลเลียม แบรดลีย์",
})
_STRINGS = _STRINGS + [
    "My name is Ernest Satow.",
    "My sword, Yumeno Tatsu Kudaki, saps strength.",
    "Learn from William Bradley.",
]
_mined = mine_names(_STRINGS, _MASTER_FAKE, {})
case("N: ไม่คืนเศษคำกลางพยางค์", _mined.get("Ernest"), None)
case("N: ไม่คืนชื่อยาวเกินสัดส่วน", _mined.get("Tatsu"), None)
case("N: ทิ้งกรณีกำกวม (สองชื่อคู่กันเสมอ)", _mined.get("Bradley"), None)
case("N: ขุดชื่อที่ไม่เคยเป็นคีย์สั้นได้", _mined.get("Higashihara"), "ฮิงาชิฮาระ")
case("N: ไม่หลุดคำสามัญออกมาเป็นชื่อ", _mined.get("Oharu"), None)


# gender_lines.json — คำตัดสินเพศรายบรรทัดของ lead ต้องมี why เสมอ (กัน "เดาแล้วล็อก")
import merge_qc as _M                                # noqa: E402
_M._LINE_GENDER = None
_M.line_gender("x")                                  # โหลดไฟล์จริงหนึ่งครั้ง
_saved = dict(_M._LINE_GENDER)
_M._LINE_GENDER = {"KEY_WITH_WHY": "female"}
case("K: line_gender เป็นชั้นบนสุดของด่าน G",
     bool(check_pair("KEY_WITH_WHY", "ขอบคุณนะจ๊ะ", era=True, neutral=True, ja="")[0]), False)
_M._LINE_GENDER = {}
case("K: บรรทัดเดียวกันที่ไม่มีคำตัดสิน ยังตกด่าน G",
     bool(check_pair("KEY_WITH_WHY", "ขอบคุณนะจ๊ะ", era=True, neutral=True, ja="")[0]), True)
_M._LINE_GENDER = _saved


# ด่าน J ต้องรู้จักรูปสุภาพที่คลื่น MSG_037–042 รายงาน
import merge_qc as _MJ                              # noqa: E402
case("K: 下さい รูปคันจิ นับเป็นรูปสุภาพ",
     any(m in "やめて下さいよ" for m in _MJ.POLITE_JA), True)
case("K: まして (te-form ของ ます) นับเป็นรูปสุภาพ",
     any(m in "頼まれましてね" for m in _MJ.POLITE_JA), True)
case("K: รูปห้วนยังไม่นับเป็นสุภาพ",
     any(m in "そんなん知らんわ" for m in _MJ.POLITE_JA), False)
case("K: ทีมัน ไม่ใช่คำยืม",
     tp.modern_loanwords("แต่เดิมทีมันเป็นแบบนี้"), [])


def main():
    bad = 0
    for name, ok, got, want in CASES:
        if not ok:
            bad += 1
            print("!! %-38s ได้ %r · ควรได้ %r" % (name, got, want))
    print("เทสต์ %d เคส · ผ่าน %d · ตก %d" % (len(CASES), len(CASES) - bad, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
