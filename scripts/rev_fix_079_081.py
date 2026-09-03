"""ผู้ตรวจ: แก้จุดที่นับหลักฐานจากคลังแล้วในก้อน MSG_079 · MSG_080
(MSG_081 ไม่มีจุดแก้)

แก้แบบแทนที่ข้อความดิบในไฟล์ เพื่อคงรูปแบบไฟล์เดิมทุกไบต์ที่ไม่เกี่ยว
(ไฟล์ done ใช้ CRLF และท้ายไฟล์ไม่เหมือนกันทุกก้อน — re-serialize จะเปลี่ยนทั้งไฟล์)

หลักฐาน
  1) MSG_079  "เช่อะ" -> "เชอะ"   x4
     master_th.json: เช่อะ = 0 · เชอะ = 37
     ไฟล์ done ทั้งโปรเจกต์: เช่อะ = 4 (MSG_079 ก้อนเดียว) · เชอะ = 44 (24 ก้อน)
     MSG_081 ในคลื่นเดียวกันใช้ "เชอะ"

  2) MSG_080  "เหอะ" (คำแปล ふっ/フッ ของไซโต) -> "ฮึ"   x4
     บรรทัดที่ ref_ja ขึ้นต้น ふっ/フッ เดี่ยว ทั้งคลัง 290 บรรทัด
     โทเคนแรกของคำแปล: ฮึ/ฮึ... = 166 · ตระกูล ฟุ/ฟึ = 39 · เหอะ = 6 (3 ในนั้นเป็นของ MSG_080 เอง)
     MSG_079 ในคลื่นเดียวกันใช้ "ฮึ" กับ ふっ ตัวเดียวกัน 3 บรรทัด
     (ไม่แตะ "เฮอะ" ซึ่งเป็นคนละคำ — คู่ เฮอะ/เฮ้อ อยู่ในบัญชีขาวของ check_cross_batch)

  3) MSG_080  ฉากร่วม uid016e0131 บรรทัด 44 (บทไซโต) "เหรอ" -> "หรือ"  x2 ในบรรทัดเดียว
     MSG_079 เป็นเจ้าของฉากนี้ (40 จาก 48 บรรทัด) บทถามของไซโตในฉากใช้
     "หรือ" 2 ครั้ง · "อย่างไร" 1 ครั้ง · "เหรอ" 0 ครั้ง
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

D = "translations/done"

FIXES = {
    "MSG_079": [("เช่อะ", "เชอะ", 4)],
    "MSG_080": [
        ("เหอะ", "ฮึ", 4),
        (
            "ของที่ไม่ใช้แล้วเหรอ... อะไรก็ได้จริง ๆ น่ะเหรอ?",
            "ของที่ไม่ใช้แล้วหรือ... อะไรก็ได้จริง ๆ น่ะหรือ?",
            1,
        ),
    ],
}

for batch, rules in FIXES.items():
    path = f"{D}/batch_{batch}.done.json"
    raw = io.open(path, encoding="utf-8", newline="").read()
    before = json.loads(raw)
    keys_before = list(before["strings"])

    for old, new, expect in rules:
        n = raw.count(old)
        if n != expect:
            raise SystemExit(f"{batch}: {old!r} พบ {n} จุด (คาด {expect}) — หยุด ไม่แก้")
        raw = raw.replace(old, new)
        print(f"{batch}: {old!r} -> {new!r}  แก้ {n} จุด")

    after = json.loads(raw)
    keys_after = list(after["strings"])
    if keys_after != keys_before:
        raise SystemExit(f"{batch}: ลำดับ/ชุดคีย์เปลี่ยน — หยุด ไม่เขียน")
    if len(keys_after) != 250:
        raise SystemExit(f"{batch}: จำนวนคีย์ = {len(keys_after)} — หยุด ไม่เขียน")

    io.open(path, "w", encoding="utf-8", newline="").write(raw)
    print(f"{batch}: เขียนแล้ว · คีย์ {len(keys_after)} · ลำดับเดิม\n")
