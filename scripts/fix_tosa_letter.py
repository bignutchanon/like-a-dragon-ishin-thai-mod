#!/usr/bin/env python3
"""แก้คำแปลเควสต์จดหมายสำเนียงโทซะของฟูจิเอะ (uid000c1432) ให้มุกทายคำเข้ากัน (15 ก.ย. 2026)

ผู้ใช้ส่งภาพจอ "งงๆ แปลแปลกๆ" — จดหมายของโอคินุมีคำเพี้ยนสองคำให้ผู้เล่นทายความหมาย
แต่ละคำมีตัวเลือกผิดที่เป็นมุก ต้องมีส่วนประกอบในคำไทยให้มุกเล่นได้:

  1. "This'n" (あて = 私)  -> "ข้าเจ้านี้"  **คงไว้**
     ถูก = "ข้า" · ผิด "Ow" (มือเป็นตะคริว) · ผิด "kimono" (อ่าน "นี้" เป็น "กิโมโนตัวนี้" #410)
  2. "all y'are, boyo" (おまさん = あなた) -> เดิม "เจ้าหนุ่มน้อยผู้นั้น" **ใช้ไม่ได้**
     ถูก = "เจ้า" (#419 "ทั้งหมดที่ข้าเป็น") · ผิด "เด็กน้อย" (#424 เพราะมีคำ "หนุ่มน้อย") ·
     ผิด "ทุกสิ่ง" (#430 "คำสำคัญคือ all") — "ผู้นั้น" ไม่ได้แปลว่า all มุกข้อสามจึงไม่มีความหมาย
     -> "เจ้าหนุ่มน้อยทั้งปวง" (เจ้า = you · หนุ่มน้อย = boyo · ทั้งปวง = all)

ตัวเลือก "I" ที่ขึ้นอังกฤษบนจอเป็นอีกบั๊ก (ตัวคัด label ตัวพิมพ์ใหญ่ล้วน) แก้ใน build_text.py

ใช้: python scripts/fix_tosa_letter.py [--write]   แล้วต่อด้วย python scripts/merge_qc.py
"""
import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

OLD_YOU, NEW_YOU = "เจ้าหนุ่มน้อยผู้นั้น", "เจ้าหนุ่มน้อยทั้งปวง"
# #430 อธิบายว่าคำสำคัญคือ "all" — ต้องชี้คำที่แปลว่า all ในคำไทยใหม่
KEY_WORD = ('คำสำคัญตรงนั้นคือ "ผู้นั้น"', 'คำสำคัญตรงนั้นคือ "ทั้งปวง"')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    n_files = n_keys = 0
    for p in sorted((paths.TRANSLATIONS / "done").glob("batch_*.done.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        strings = data.get("strings") or {}
        hit = 0
        for en, th in list(strings.items()):
            if not isinstance(th, str) or OLD_YOU not in th:
                continue
            new = th.replace(OLD_YOU, NEW_YOU).replace(*KEY_WORD)
            print("%s | %s\n  เดิม: %s\n  ใหม่: %s" % (p.name, en.replace("\n", " / "),
                                                   th.replace("\n", " / "), new.replace("\n", " / ")))
            strings[en] = new
            hit += 1
        if hit:
            n_files += 1
            n_keys += hit
            if args.write:
                p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print("%d ไฟล์ · %d คีย์%s" % (n_files, n_keys, "" if args.write else " (ยังไม่เขียน — ใส่ --write)"))
    add_choice_label(args.write)


# ตัวเลือกตอบ "I" (label ของ uid000c1432) — ไม่เคยเข้าคิวเพราะตัวคัด label ตีตัวพิมพ์ใหญ่ล้วนเป็นคีย์
# ปลอดภัยที่จะมีคีย์ "I" ใน master: ชั้นอื่นที่มีสตริง "I" ตรงตัวมีแค่ photo_stamp (อยู่ใน DENY_TABLES)
# ส่วน label "I" ของไฟล์อื่น (uid006e017b) ไม่ถูกแทนเพราะ build_text.LABEL_TEXT_ALLOW ผูกรายไฟล์
CHOICE_EN, CHOICE_TH = "I", "ข้า"
LABEL_BATCH = "batch_LABEL_002"


def add_choice_label(write):
    wl_path = paths.TRANSLATIONS / "worklist" / (LABEL_BATCH + ".json")
    dn_path = paths.TRANSLATIONS / "done" / (LABEL_BATCH + ".done.json")
    wl = json.loads(wl_path.read_text(encoding="utf-8"))
    dn = json.loads(dn_path.read_text(encoding="utf-8"))
    if CHOICE_EN in wl["strings"] and dn["strings"].get(CHOICE_EN) == CHOICE_TH:
        print("ตัวเลือก %r มีใน %s แล้ว" % (CHOICE_EN, LABEL_BATCH))
        return
    wl["strings"][CHOICE_EN] = ""            # ต่อท้าย — ด่าน A1 ของ merge_qc เทียบลำดับคีย์ worklist/done
    dn["strings"][CHOICE_EN] = CHOICE_TH
    print("เพิ่มตัวเลือก %r -> %r ท้าย %s%s" % (CHOICE_EN, CHOICE_TH, LABEL_BATCH, "" if write else " (ยังไม่เขียน)"))
    if write:
        wl_path.write_text(json.dumps(wl, ensure_ascii=False, indent=1), encoding="utf-8")
        dn_path.write_text(json.dumps(dn, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
