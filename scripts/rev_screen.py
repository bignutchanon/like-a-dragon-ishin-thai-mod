"""ผู้ตรวจ: ชุดตะแกรงอัตโนมัติสำหรับก้อนที่รับตรวจ"""
import sys, json, re, glob, os

sys.path.insert(0, "scripts")
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
from rev_query import rows

BATCHES = sys.argv[1:] or ["MSG_055", "MSG_056", "MSG_057"]

MODERN = ["โอเค", "ไอเดีย", "เช็ก", "ทีม", "แฟน", "บอส", "เกม", "เก๋าเกม",
          "กองบัญชาการ", "สถานทูต", "แก๊ง", "สู้ ๆ", "สู้ๆ", "โทรศัพท์",
          "คอมพิวเตอร์", "รถไฟ", "โรงพยาบาล", "ตำรวจ", "โรงเรียน", "บริษัท",
          "ร้อยละ", "เปอร์เซ็นต์", "ซุปเปอร์", "เซอร์ไพรส์", "ช็อก", "ปาร์ตี้",
          "เมนู", "ล็อบบี้", "โปรเจกต์", "แคมเปญ"]
POLITE_MOD = ["ครับ", "ค่ะ", "คะ", "ผม", "คุณ", "ดิฉัน", "ฉัน", "เธอ"]

TAG = re.compile(r"<[^<>]+>|\{[^{}]+\}|\$\{[^}]*\}|%[sd]")
NUM = re.compile(r"\d+")


def hdr(t):
    print("\n" + "=" * 8, t)


for b in BATCHES:
    R = rows(b)
    print("\n" + "#" * 30, b, len(R), "keys")

    hdr("1. คำร่วมสมัยในบัญชีห้าม")
    for r in R:
        for w in MODERN:
            if w in r["th"]:
                print(f"  #{r['i']:03d} [{w}] {r['th'][:110]}")

    hdr("2. ผม/คุณ/ครับ/ค่ะ/ฉัน/เธอ (ต้องเป็นข้อความระบบเท่านั้น)")
    for r in R:
        hits = [w for w in POLITE_MOD if re.search(r"(?<![ก-ฮ])" + w, r["th"])]
        if hits:
            print(f"  #{r['i']:03d} {hits} EN:{r['en'][:70]}")
            print(f"        TH:{r['th'][:130]}")

    hdr("3. ไม้ยมกไม่เว้นวรรค")
    for r in R:
        if re.search(r"[ก-ฮะ-ๅ]ๆ", r["th"]):
            print(f"  #{r['i']:03d} {r['th'][:110]}")

    hdr("4. จำนวน \\n ไม่ตรง")
    for r in R:
        if r["en"].count("\n") != r["th"].count("\n"):
            print(f"  #{r['i']:03d} en={r['en'].count(chr(10))} th={r['th'].count(chr(10))}")

    hdr("5. แท็ก/placeholder ไม่ครบ")
    for r in R:
        a, c = sorted(TAG.findall(r["en"])), sorted(TAG.findall(r["th"]))
        if a != c:
            print(f"  #{r['i']:03d} en={a} th={c}")
            print(f"        EN:{r['en'][:90]}")
            print(f"        TH:{r['th'][:90]}")

    hdr("6. ตัวเลขไม่ตรง")
    for r in R:
        a, c = sorted(NUM.findall(r["en"])), sorted(NUM.findall(r["th"]))
        if a != c:
            print(f"  #{r['i']:03d} en={a} th={c} | EN:{r['en'][:70]} | TH:{r['th'][:70]}")

    hdr("7. อัตราส่วนความยาวผิดปกติ (สั้นกว่า 0.55 เท่า หรือ ยาวกว่า 2.2 เท่า)")
    for r in R:
        le, lt = len(r["en"]), len(r["th"])
        if le < 25:
            continue
        rt = lt / le
        if rt < 0.55 or rt > 2.2:
            print(f"  #{r['i']:03d} ratio={rt:.2f} en={le} th={lt}")
            print(f"        EN:{r['en'][:120]}")
            print(f"        TH:{r['th'][:120]}")

    hdr("8. คำแปลว่าง / เท่ากับ EN")
    for r in R:
        if not r["th"].strip():
            print(f"  #{r['i']:03d} ว่าง EN:{r['en'][:70]}")
        elif r["th"] == r["en"]:
            print(f"  #{r['i']:03d} คง EN: {r['en'][:90]}")

    hdr("9. อักษรละติน/คันจิตกค้างใน TH")
    for r in R:
        lat = re.findall(r"[A-Za-z]{2,}", r["th"])
        cjk = re.findall(r"[぀-ヿ一-鿿]+", r["th"])
        if lat or cjk:
            print(f"  #{r['i']:03d} lat={lat} cjk={cjk} | TH:{r['th'][:90]}")
