#!/usr/bin/env python3
"""ย่อบรรทัด .msg ที่ยาวเกิน 1,000 ไบต์ UTF-8 — แก้เกม crash ที่เควสต์ร้านอุด้ง (15 ก.ย. 2026)

ที่มา: ผู้ใช้รายงานเกมปิดตัวเองตอนเควสต์ร้านอุด้ง · Event Log = exception 0xc0000409 data 2
(stack cookie check failure) · minidump `%LOCALAPPDATA%\\CrashDumps\\LikeaDragonIshin-Win64-Shipping.exe.*.dmp`
บน stack ของเธรดที่พังมี 1,024 ไบต์แรกของบรรทัด `uid010c16a4#001` (คำอธิบายวิธีเล่นมินิเกมอุด้ง ไทย 1,098 ไบต์)
วางอยู่ที่ rsp+0x70..0x470 แล้วช่อง cookie ถัดจาก buffer ถูกเขียนทับ → โค้ดเกมคัดลอกข้อความหน้าต่างสอนเล่น
ลง buffer บน stack ขนาด 1,024 ไบต์ · ภาษาทางการยาวสุด 572 ไบต์จึงไม่เคยชน (รายละเอียด research §11)

ทั้งคลังมีบรรทัด .msg ไทยเกิน 1,000 ไบต์อยู่ 3 บรรทัด — ย่อทั้งสามให้ ≤ 1,000 (ด่าน `check_byte_limits.py`)
  uid010c16a4#001  วิธีเล่นมินิเกมอุด้ง (ตัวที่ทำให้ crash)
  uid0102220f#000 · uid01160726#013  ประกาศฟีเจอร์ SHARE ของ PlayStation4 (EN ก็ทิ้งเป็นญี่ปุ่น · ย่อกันไว้ก่อน)

ใช้: python scripts/fix_msg_byte_limit.py [--write]   แล้วต่อด้วย python scripts/merge_qc.py
"""
import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

LIMIT = 1000

# คีย์บรรทัด -> คำแปลใหม่ (ขึ้นบรรทัดเขียนเป็น \n · สคริปต์แปลงเป็น \r\n ถ้าคำแปลเดิมใช้ CRLF)
NEW = {
    "uid010c16a4#001":
        "<kf:10>จำอุด้งที่ลูกค้าสั่งให้ดีแล้วรีบเสิร์ฟ! พอสั่งครบ ให้กดปุ่มที่ตรงกันตามลำดับเดิมให้ทันเวลา "
        "ยิ่งจัดการเส้นเก่งขึ้น ร้านก็ยิ่งคึกคัก งานอาจหนักขึ้นแต่ค่าจ้างก็สูงขึ้นตาม\n\n"
        "กด <symbol=button_l1> เพื่อ \"แนะนำ\" เมนูให้ลูกค้าทุกคน รวมออร์เดอร์ทั้งรอบเป็นแบบเดียวกัน "
        "ใช้ได้ครั้งเดียวต่อกะ เว้นแต่ทำรอบที่แนะนำพลาด",
    # ต้นฉบับเขียน "PlayStation\x7f4" (รหัสควบคุมคั่นก่อนเลข · มีใน EN/JA ทั้งสามสตริงของคลัง) — คงไว้
    "uid0102220f#000":
        "บน PlayStation\x7f4 ใช้ฟีเจอร์ SHARE ในสนามประลองได้\n\n"
        "เมื่อถ่ายทอดสดการเล่น ความเห็นของผู้ชมจะขึ้นในเกมทันที และหากได้รับความเห็นเฉพาะ (ไลฟ์คอมมานด์) "
        "จากผู้ชมระหว่างแข่ง จะได้ผลอย่างพลังโจมตีเพิ่มหรือเกจฮีทฟื้น คำสำคัญและจังหวะใช้ไลฟ์คอมมานด์จะแสดงระหว่างแข่ง\n\n"
        "ร่วมมือกับผู้ชมแล้วทำให้การแข่งเป็นต่อกันเถอะ!",
    "uid01160726#013":
        "บน PlayStation\x7f4 ใช้ฟีเจอร์ SHARE ในสังเวียนได้\n"
        "เมื่อถ่ายทอดสดการเล่น ความเห็นของผู้ชม\n"
        "จะขึ้นในเกมทันที\n\n"
        "อีกทั้งเมื่อได้รับความเห็นเฉพาะ (ไลฟ์คอมมานด์) จากผู้ชมระหว่างแข่ง\n"
        "จะได้ผล เช่น พลังโจมตีเพิ่ม หรือเกจฮีทฟื้น\n"
        "คำสำคัญและจังหวะใช้ไลฟ์คอมมานด์จะแสดงระหว่างแข่ง\n\n"
        "ร่วมมือกับผู้ชมทุกคน\n"
        "แล้วทำให้การแข่งเป็นต่อกันเถอะ!",
}


def en_of(key):
    uid, line = key.split("#")
    for r in json.loads((paths.TEXT_EN / (uid + ".json")).read_text(encoding="utf-8")):
        if r["line"] == int(line):
            return r["en"]
    raise SystemExit("ไม่พบบรรทัด " + key)


def one(s):
    return s.replace("\r\n", " / ").replace("\n", " / ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    want = {en_of(k): (k, th) for k, th in NEW.items()}
    hit = 0
    for p in sorted((paths.TRANSLATIONS / "done").glob("batch_*.done.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        strings = data.get("strings") or {}
        changed = False
        for en, (key, new) in want.items():
            old = strings.get(en)
            if not isinstance(old, str):
                continue
            if "\r\n" in old:
                new = new.replace("\n", "\r\n")
            n_old, n_new = len(old.encode("utf-8")), len(new.encode("utf-8"))
            if n_old <= LIMIT and old != new:
                print("!! %s ยาว %d ไบต์ ไม่เกินเพดานแล้ว — ข้าม (คำแปลถูกแก้ทีหลัง?)" % (key, n_old))
                continue
            if old.count("\n") != new.count("\n"):
                raise SystemExit("%s จำนวนขึ้นบรรทัดไม่เท่าเดิม (%d -> %d)" % (key, old.count("\n"), new.count("\n")))
            if n_new > LIMIT:
                raise SystemExit("%s คำแปลใหม่ยังยาว %d ไบต์" % (key, n_new))
            print("%s | %s (%s)\n  เดิม %4d ไบต์: %s\n  ใหม่ %4d ไบต์: %s" % (p.name, key, one(en)[:50], n_old, one(old)[:110], n_new, one(new)[:110]))
            strings[en] = new
            hit += 1
            changed = True
        if changed and args.write:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print("%d คีย์%s" % (hit, "" if args.write else " (ยังไม่เขียน — ใส่ --write)"))


if __name__ == "__main__":
    main()
