"""ถอดคีย์ที่แปลไทยไปแล้วออกจากไฟล์ .dnt.json

ไฟล์ `translations/worklist/batch_*.dnt.json` เก็บคีย์ที่สั่งว่า "คงต้นฉบับ"
พร้อมเหตุผล  รอบคัดแยก JA ค้าง (sprint 16) พบว่าหลายคีย์ถูกตั้ง DNT ด้วย
เหตุผลที่ไม่ตรงของจริง (เป็นบทของ Ishin เอง ไม่ใช่บทตกค้างจากเกมอื่น)
และถูกแปลไทยลงไฟล์ done แล้ว  สคริปต์นี้ทำให้ไฟล์ DNT ตรงกับความจริง

เกณฑ์ถอด: คีย์นั้นมีในไฟล์ done ของก้อนเดียวกัน และคำแปล **มีอักษรไทย**
(ไม่ใช้เกณฑ์ "ไม่มีอักษรญี่ปุ่นแล้ว" เพราะจะกินคีย์ debug อังกฤษล้วนติดมาด้วย)

รันแบบไม่ใส่ --apply = ดูอย่างเดียว
"""
import json
import re
import sys

from paths import PROJECT

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

THAI = re.compile(r"[฀-๿]")
WORKLIST = PROJECT / "translations" / "worklist"
DONE = PROJECT / "translations" / "done"


def main() -> int:
    apply = "--apply" in sys.argv
    total = 0
    for dnt_path in sorted(WORKLIST.glob("*.dnt.json")):
        stem = dnt_path.name[: -len(".dnt.json")]
        done_path = DONE / f"{stem}.done.json"
        if not done_path.exists():
            print(f"{stem:20s} ไม่มีไฟล์ done — ข้าม")
            continue
        dnt = json.loads(dnt_path.read_text(encoding="utf-8"))
        done = json.loads(done_path.read_text(encoding="utf-8"))["strings"]
        drop = [k for k in dnt if THAI.search(done.get(k, ""))]
        if not drop:
            continue
        total += len(drop)
        print(f"{stem:20s} DNT {len(dnt):4d} -> {len(dnt) - len(drop):4d}  ถอด {len(drop):4d}")
        if apply:
            for k in drop:
                del dnt[k]
            dnt_path.write_text(
                json.dumps(dnt, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\nรวมถอด {total} คีย์" + ("" if apply else "  (ยังไม่เขียนไฟล์ — ใส่ --apply)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
