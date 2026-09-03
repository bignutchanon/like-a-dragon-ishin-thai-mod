"""กวาดคำร่วมสมัย "สู้ ๆ" ออกจากคลังทั้งหมด (งานค้าง sprint 14 §3.ข)

คำว่า "สู้ ๆ" เป็นสำนวนไทยร่วมสมัย ไม่เข้ากับระดับภาษายุคบาคุมัตสึที่ตั้งไว้ใน brief
ต้นฉบับญี่ปุ่นของทั้ง 12 คีย์เป็น 頑張れ / がんばって / 元気を出して ซึ่งเป็นคำให้กำลังใจกลาง ๆ
จึงแทนด้วยรูปที่คลังใช้อยู่แล้ว (ตั้งใจ 140 · พยายาม 152 · ขอให้โชคดี 15 · ทำใจ 14)
โดยเลือกรูปตามบริบทของแต่ละบรรทัด ไม่ใช่แทนที่แบบคำต่อคำ

รันแล้วต้องตามด้วย: merge_qc.py --only <ก้อนที่แก้> เพื่อให้ master_th.json ตรงกับไฟล์ done
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DONE = Path("translations/done")

# (ไฟล์ก้อน, ข้อความไทยเดิม) -> ข้อความไทยใหม่
# เดิม/ใหม่เขียนเต็มบรรทัด เพื่อให้ตรวจย้อนได้ว่าเปลี่ยนอะไรบ้าง และกันการแทนผิดบรรทัด
FIXES = [
    ("batch_016.done.json",
     "สู้ ๆ นะ นักบวช",
     "ทำใจดี ๆ ไว้เถอะ ท่านนักบวช"),
    ("batch_059.done.json",
     "ไปทำงานให้สู้ ๆ นะ",
     "ตั้งใจทำงานนะ"),
    ("batch_064.done.json",
     "เอาล่ะ สู้ ๆ นะ!",
     "เอาล่ะ ตั้งใจทำงานนะ!"),
    ("batch_074.done.json",
     "ครั้งหน้าสู้ ๆ นะ!",
     "ครั้งหน้าตั้งใจให้ดีนะ!"),
    ("batch_MSG_003.done.json",
     "ได้เลย สู้ ๆ นะ",
     "ได้เลย ขอให้โชคดีนะ"),
    ("batch_MSG_011.done.json",
     "งั้นเหรอ สู้ ๆ นะ",
     "งั้นเหรอ พยายามเข้านะ"),
    ("batch_MSG_012.done.json",
     "สู้ ๆ เลยไซโตซัง!",
     "ตั้งใจหน่อยนะไซโตซัง!"),
    ("batch_MSG_018.done.json",
     "เอาล่ะ สู้ ๆ นะ",
     "เอาล่ะ ตั้งใจให้ดีนะ"),
    ("batch_MSG_040.done.json",
     "ครั้งหน้าสู้ ๆ นะ!",
     "ครั้งหน้าตั้งใจใหม่นะ!"),
    ("batch_MSG_050.done.json",
     "(สู้ ๆ! ใจกล้าหน่อย!",
     "(เอาเลย! ใจกล้าหน่อย!"),
]


def main() -> int:
    changed_files = {}
    hits = 0
    for fname, old, new in FIXES:
        path = DONE / fname
        if not path.exists():
            print(f"[ข้าม] ไม่พบไฟล์ {fname}")
            continue
        data = changed_files.get(fname)
        if data is None:
            data = json.loads(path.read_text(encoding="utf-8"))
            changed_files[fname] = data
        strings = data["strings"]
        found = 0
        for en, th in strings.items():
            if th and old in th:
                strings[en] = th.replace(old, new)
                found += 1
                hits += 1
        if found == 0:
            print(f"[เตือน] {fname}: ไม่พบ {old!r}")
        else:
            print(f"{fname}: {found} คีย์ · {old!r} -> {new!r}")

    for fname, data in changed_files.items():
        (DONE / fname).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    left = 0
    for path in sorted(DONE.glob("*.done.json")):
        for th in json.loads(path.read_text(encoding="utf-8")).get("strings", {}).values():
            if th and "สู้ ๆ" in th:
                left += 1
                print(f"[เหลือ] {path.name}: {th[:80]}")
    print(f"\nแก้ {hits} คีย์ · {len(changed_files)} ไฟล์ · เหลือ 'สู้ ๆ' ในคลัง {left} คีย์")
    return 0 if left == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
