"""ด่านใหม่: จับ "ป้ายบนจอที่แปลไม่ตรงกับป้ายจริงที่ ship ไปแล้ว"

ที่มาของด่านนี้ (บทเรียน sprint 16): คู่มือแบล็กแจ็กเขียนหัวข้อว่า `Hit` / `Stand` แล้วอธิบายต่อ
ในเกมมีคีย์ป้ายปุ่มชื่อ `Hit` = "ตี" และ `Stand` = "อยู่" ship อยู่แล้ว
แต่คำแปลของคู่มือดันใช้ "ฮิต"/"สแตนด์" → ผู้เล่นอ่านคู่มือแล้วหาปุ่มบนจอไม่เจอ
ด่านทั้ง 8 ตัวเดิมจับไม่ได้เลย เพราะทุกตัวตรวจแบบ "คู่คีย์" ไม่มีตัวไหนมองข้ามคีย์

หลักการ: ตัดทั้งฝั่ง EN และฝั่งไทยเป็น "ช่อง" ด้วยแท็กและการขึ้นบรรทัด
ด่าน T (แท็กครบ) กับด่าน N (จำนวนบรรทัดเท่ากัน) ของ merge_qc บังคับให้สองฝั่งมีโครงเดียวกันอยู่แล้ว
→ ช่องที่ i ของสองฝั่งคือที่เดียวกันบนจอ
ถ้าช่อง EN ตรงเป๊ะกับ "คีย์ป้ายสั้น" ที่ ship ไปแล้วใน master → ช่องไทยตำแหน่งเดียวกันต้องใช้คำที่ ship

ใช้:
    python scripts/check_label_consistency.py                 # ตรวจ done ทุกไฟล์
    python scripts/check_label_consistency.py --only 137      # ตรวจไฟล์เดียว
    python scripts/check_label_consistency.py --self-test
"""
import argparse
import json
import re
import sys

from paths import PROJECT

sys.stdout.reconfigure(encoding="utf-8")

MASTER = PROJECT / "translations" / "master_th.json"
DONE = PROJECT / "translations" / "done"

TAG = re.compile(r"<[^<>]*>")
MAX_LABEL = 28
MIN_LABEL = 3


def load_labels(master):
    """คีย์สั้น ๆ ที่เป็น "ป้ายบนจอ" และมีคำแปลไทยแล้ว"""
    out = {}
    for k, v in master.items():
        if not isinstance(k, str) or not isinstance(v, str):
            continue
        if "\n" in k or "\n" in v:
            continue
        if not (MIN_LABEL <= len(k) <= MAX_LABEL):
            continue
        if not k.isascii() or not any(c.isalpha() for c in k):
            continue
        if TAG.search(k) or "${" in k:
            continue
        if v == k:  # คงอังกฤษไว้ → ไม่มีอะไรให้เทียบ
            continue
        out[k] = v
    return out


def cells(s):
    """ตัดสตริงเป็นช่อง พร้อมบอกว่าช่องนั้นถูก "แท็กขนาบ" ทั้งสองข้างไหม

    คืนลิสต์ของ (ข้อความ, ถูกแท็กขนาบสองข้าง)
    ช่องที่ถูกแท็กขนาบสองข้าง = ตำแหน่งป้าย/หัวข้อบนจอจริง ๆ (เช่น `<subhead>Hit<arrow>`)
    ส่วนบรรทัดบทพูดธรรมดาจะไม่เข้าเงื่อนไขนี้ — สำคัญมาก เพราะบทพูดบรรทัดเดียวกัน
    ที่โผล่เป็นคีย์เดี่ยวที่อื่นด้วย **ควร**แปลต่างกันตามบริบท ไม่ใช่ข้อผิดพลาด
    """
    out = []
    pos = 0
    prev_is_tag = False
    for m in TAG.finditer(s):
        lines = s[pos:m.start()].split("\n")
        for i, line in enumerate(lines):
            # ช่องนี้จะ "ถูกแท็กขนาบสองข้าง" ก็ต่อเมื่อไม่มีการขึ้นบรรทัดคั่นทั้งสองด้าน
            boxed = prev_is_tag and i == 0 and i == len(lines) - 1
            out.append((line.strip(), boxed))
        pos = m.end()
        prev_is_tag = True
    # ส่วนหางหลังแท็กตัวสุดท้าย — ไม่มีแท็กปิดท้าย จึงไม่นับเป็นตำแหน่งป้าย
    for line in s[pos:].split("\n"):
        out.append((line.strip(), False))
    return out


def check_pair(en, th, labels):
    """เทียบช่องต่อช่อง — เฉพาะช่องที่อยู่ในตำแหน่งป้าย (ถูกแท็กขนาบสองข้าง)"""
    a, b = cells(en), cells(th)
    if len(a) != len(b):
        return []  # โครงไม่ตรง — ด่าน T/N จับเอง
    bad = []
    for (x, boxed), (y, _) in zip(a, b):
        if not boxed or not x or x not in labels:
            continue
        if x == en.strip():
            continue
        want = labels[x]
        if y != want and not y.startswith(want):
            bad.append((x, want, y))
    return bad


def run(files, labels):
    total = 0
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        s = d.get("strings", d)
        hits = []
        for en, th in s.items():
            if not isinstance(th, str) or th == en:
                continue
            for seg, want, got in check_pair(en, th, labels):
                hits.append((seg, want, got, en))
        if hits:
            print("%-28s พบ %d จุด" % (f.name, len(hits)))
            for seg, want, got, en in hits[:12]:
                print("   ป้าย %r -> ใช้ %r แต่ที่ ship คือ %r | คีย์ %r" % (seg, got, want, en[:55]))
            total += len(hits)
    print("\nรวม %d จุดที่ป้ายในคีย์ยาวไม่ตรงกับป้ายที่ ship แล้ว" % total)
    return total


def self_test():
    labels = {"Hit": "ตี", "Stand": "อยู่", "Surrender": "ยอมแพ้"}
    en = "<head>Blackjack\n\n <sub>Hit<arrow>Draw a card.\n\n <sub>Stand<arrow>Stay."
    old = check_pair(en, "<head>แบล็กแจ็ก\n\n <sub>ฮิต<arrow>จั่วไพ่\n\n <sub>สแตนด์<arrow>อยู่เฉย", labels)
    new = check_pair(en, "<head>แบล็กแจ็ก\n\n <sub>ตี<arrow>จั่วไพ่\n\n <sub>อยู่<arrow>คงไพ่", labels)
    prose = check_pair("I told him to stand up and hit the road.", "บอกให้เขาลุกแล้วไปซะ", labels)
    solo = check_pair("Hit", "ฮิต", labels)
    print("รูปเก่า (ควรเจอ 2)        =", len(old))
    print("รูปใหม่ (ควรเจอ 0)        =", len(new))
    print("ประโยคธรรมดา (ควรเจอ 0)   =", len(prose))
    print("คีย์ป้ายเดี่ยว (ควรเจอ 0)  =", len(solo))
    assert len(old) == 2 and len(new) == 0 and len(prose) == 0 and len(solo) == 0
    print("self-test ผ่าน")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    labels = load_labels(master)
    print("ป้ายที่ ship แล้วและใช้เทียบได้: %d คำ" % len(labels))
    files = sorted(DONE.glob("batch_*.done.json"))
    if args.only:
        files = [f for f in files if args.only in f.name]
    run(files, labels)


if __name__ == "__main__":
    main()
