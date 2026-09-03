"""ดึงชื่อทักษะภาษาไทยที่ ship ไปแล้ว ออกมาจากข้อความ "The skill X has been unlocked" ใน master_th.json

ที่มา: ตาราง `player_skill.bin` เก็บ "ชื่อทักษะ" เป็นคีย์สั้น ๆ ที่ไม่มีบริบทเลย
แต่ข้อความปลดล็อกทักษะ (`The skill <ชื่อ> has been unlocked. ...`) ถูกแปลไปแล้วตั้งแต่ batch ก่อน ๆ
และในนั้น "มีชื่อไทยของทักษะอยู่ครบ" — ตัวนี้จับคู่สองฝั่งให้อัตโนมัติ เพื่อไม่ให้นักแปลตั้งชื่อใหม่ทับของที่ ship แล้ว

ใช้:
    python scripts/make_skill_priorart.py 146 148            # ดูผล
    python scripts/make_skill_priorart.py 146 148 --write    # เขียน translations/worklist/batch_NNN.skillart.json
"""
import argparse
import json
import re
import sys

from paths import PROJECT

sys.stdout.reconfigure(encoding="utf-8")

MASTER = PROJECT / "translations" / "master_th.json"
WORKLIST = PROJECT / "translations" / "worklist"

# รูปประโยคปลดล็อกทักษะที่เกมใช้ (EN) — จับชื่อทักษะในกลุ่มที่ 1
UNLOCK_EN = re.compile(r"^The skill (.+?) has been unlocked\.")
# ฝั่งไทยที่แปลไปแล้วใช้รูป "ทักษะ<ชื่อ>ถูกปลดล็อกแล้ว" หรือ "ทักษะ <ชื่อ> ถูกปลดล็อกแล้ว"
UNLOCK_TH = re.compile(r"ทักษะ\s*(.+?)\s*ถูกปลดล็อก")


def build_index(master):
    """คืน dict: ชื่อทักษะ EN -> ชื่อทักษะไทยที่ ship แล้ว"""
    out = {}
    for k, v in master.items():
        if not isinstance(v, str):
            continue
        m = UNLOCK_EN.match(k)
        if not m:
            continue
        t = UNLOCK_TH.search(v)
        if t:
            out[m.group(1).strip()] = t.group(1).strip()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("start", type=int)
    ap.add_argument("end", type=int)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    master = json.loads(MASTER.read_text(encoding="utf-8"))
    index = build_index(master)
    print("ชื่อทักษะที่ ship แล้ว (จากข้อความปลดล็อก): %d ชื่อ" % len(index))

    for i in range(args.start, args.end + 1):
        wl = WORKLIST / ("batch_%03d.json" % i)
        if not wl.exists():
            continue
        strings = json.loads(wl.read_text(encoding="utf-8")).get("strings", {})
        hit = {k: index[k] for k in strings if k in index}
        print("batch_%03d: ชื่อทักษะที่มีคำไทยอยู่แล้ว %d/%d คีย์" % (i, len(hit), len(strings)))
        if args.write:
            out = WORKLIST / ("batch_%03d.skillart.json" % i)
            out.write_text(json.dumps(hit, ensure_ascii=False, indent=1), encoding="utf-8")
            print("   -> %s" % out.name)


if __name__ == "__main__":
    main()
