"""ด่านตรวจความยาว **เป็นไบต์ UTF-8** ของสตริงที่โค้ดเกมเก็บลง buffer ขนาดคงที่

กฎที่ 1 — locres 254 ไบต์ (13 ก.ย. 2026 · ภาพผู้ใช้): กล่องสรุปบทตอนเริ่มบทแสดง "…พวกนั้นดุร้ายไม่น้อย ควรเ?"
คำแปลยาว 110 ตัวอักษร = 324 ไบต์ และจุดที่ขาดคือ **ไบต์ที่ 255 พอดี** (ตัว ต ถูกตัดครึ่ง -> "?")
ภาษาอังกฤษของเกมยาวสุด 115 ไบต์ ญี่ปุ่น 206 ไบต์ จึงไม่เคยชนเพดาน แต่ไทยใช้ 3 ไบต์ต่อตัวอักษร
หน้าเมนูหยุดเกมแสดงสตริงเดียวกันครบ = เพดานอยู่ที่ทางแสดงผลของกล่องนั้น ไม่ใช่ที่ locres
เกณฑ์: ทุกคีย์ใน namespace ที่มีหลักฐานว่าชนเพดาน ต้องยาวไม่เกิน 254 ไบต์ (เผื่อ NUL ท้าย)

กฎที่ 2 — บรรทัด .msg 1,000 ไบต์ (15 ก.ย. 2026 · เกม crash ที่เควสต์ร้านอุด้ง): minidump ของ
exception 0xc0000409 (stack cookie check failure) แสดงว่าโค้ดหน้าต่างสอนเล่นคัดลอกข้อความบรรทัด
`uid010c16a4#001` (ไทย 1,098 ไบต์) ลง buffer บน stack **1,024 ไบต์พอดี** แล้วช่อง cookie ถัดจาก buffer
ถูกเขียนทับ · ภาษาทางการยาวสุด 572 ไบต์ · ดู research §11 · เกณฑ์ ≤ 1,000 เผื่อ NUL/ไบต์ที่โค้ดเขียนต่อท้าย
(ยังไม่รู้ว่าตาราง tips และ locres `rule_*` ที่ยาวเกิน 1,024 ผ่านทางเดียวกันไหม — ต้องมีหลักฐานจากจอจริงก่อนเพิ่ม)

เพิ่มกฎได้เฉพาะเมื่อมีภาพ/หลักฐานจากจอจริงหรือ crash dump — ห้ามเดาจากชื่อ (กติกาเหล็กข้อ 11)

ใช้: python scripts/check_byte_limits.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

LIMIT = 254
NAMESPACES = {
    "explanation_main_scenario_explanation": "กล่องสรุปบทตอนเริ่มบท (ภาพผู้ใช้ 13 ก.ย. 2026 · ขาดที่ไบต์ 255)",
}
MSG_LIMIT = 1000        # buffer 1,024 ไบต์ (minidump 15 ก.ย. 2026) หักส่วนเผื่อ


def check_locres(master):
    loc = json.loads((paths.EXTRACTED / "parallel" / "locres.json").read_text(encoding="utf-8"))
    bad, checked = [], 0
    for r in loc:
        if r["ns"] not in NAMESPACES:
            continue
        th = master.get(r["en"])
        if not th:
            continue
        checked += 1
        n = len(th.encode("utf-8"))
        if n > LIMIT:
            bad.append((n, r["key"], th))
    print("locres: สตริงที่ตรวจ %d (%s) · เกิน %d ไบต์ **%d**"
          % (checked, " · ".join(NAMESPACES), LIMIT, len(bad)))
    for n, key, th in sorted(bad, reverse=True)[:15]:
        print("  %3d ไบต์  %s  %r" % (n, key.split("/")[-1], th[:50]))
    return bad


def check_msg(master):
    """ทุกบรรทัด .msg ที่มีคำแปล (ตามที่ build_text.build_msg ใส่ลงไฟล์ — คำแปลใน master ไม่ถูกแปลงอีก)"""
    bad, checked, seen = [], 0, set()
    for js in sorted(paths.TEXT_EN.glob("*.json")):
        for r in json.loads(js.read_text(encoding="utf-8")):
            th = master.get(r["en"])
            if th is None or r["en"] in seen:
                continue
            seen.add(r["en"])
            checked += 1
            n = len(th.encode("utf-8"))
            if n > MSG_LIMIT:
                bad.append((n, "%s#%03d" % (js.stem, r["line"]), th))
    print("msg: สตริงที่ตรวจ %d · เกิน %d ไบต์ **%d**" % (checked, MSG_LIMIT, len(bad)))
    for n, key, th in sorted(bad, reverse=True)[:15]:
        print("  %4d ไบต์  %s  %r" % (n, key, th[:50]))
    return bad


def main():
    master = json.loads(paths.MASTER_TH.read_text(encoding="utf-8"))
    bad = check_locres(master) + check_msg(master)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
