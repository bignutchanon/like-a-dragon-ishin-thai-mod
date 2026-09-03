"""กวาดรูปคำยกย่องของ "ไซโต" ให้ตรงนโยบายเดียว (งานค้าง sprint 14 §3.ข ข้อ 2-3)

นโยบายอยู่ใน `translations/glossary.md` บรรทัด 75-82 (เคาะ 2 ก.ย. 2026):
  -san / -han (รูปคันไซของ -san) = "ซัง" ต่อท้ายชื่อ ติดกันไม่เว้นวรรค
  -sama / -dono            = "ท่าน" นำหน้าชื่อ
  -kun                     = "คุง" ต่อท้ายชื่อ

วัดทั้งคลังก่อนแก้ (เทียบกับ `ref_ja` ของทุกคีย์ที่ ja ชี้รูปเดียวไม่กำกวม):
  斎藤さん -> ไซโตซัง 231 : ผิดรูป 6      斎藤はん -> ไซโตซัง 13 : ผิดรูป 5
  斎藤様/殿 -> ท่านไซโต 44 (ถูกทั้งหมด)   斎藤君 -> ไซโตคุง 38 (ถูกทั้งหมด)
  EN "Hajime-san" -> ฮาจิเมะซัง 119 : ผิดรูป 5
  EN "Captain Saito" -> หัวหน้าหน่วยไซโต 13 : เติม "ท่าน" นำหน้าเกินมา 2

⚠ ที่ตรวจแล้ว **ไม่แก้**:
  - `ท่านไซโต` 16 คีย์ที่ EN ไม่มีคำว่า Saito — `ref_ja` มี 斎藤 ครบทั้ง 16 (EN ตัดชื่อทิ้งเอง)
    ที่แก้ในไฟล์นี้คือเฉพาะคีย์ที่ ja เป็น さん/はん ซึ่งต้องเป็น "ซัง" ไม่ใช่ "ท่าน"
  - batch_034 5 คีย์ ja=斎藤殿 แต่ EN เขียน "Saito-san" -> คงไซโตซัง ตาม §4.5 (ยึด EN)
  - MSG_053 `Sir Saito` = ท่านไซโต (ja 斎藤殿) ถูกแล้ว

รันแล้วต้องตามด้วย: merge_qc.py --only <ก้อนที่แก้>
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DONE = Path("translations/done")

# (ไฟล์ก้อน, คีย์ EN, ข้อความเดิมบางส่วน, ข้อความใหม่)
FIXES = [
    # --- ก. EN "Saito Hajime-san" / "Hajime-san" -> ฮาจิเมะซัง (รูปข้างมาก 119 คีย์) ---
    ("batch_003.done.json", "A pleasure, Saito Hajime-san.",
     "ท่านไซโต ฮาจิเมะ", "ไซโต ฮาจิเมะซัง"),
    ("batch_004.done.json", "Saito Hajime-san...",
     "ท่านไซโต ฮาจิเมะ", "ไซโต ฮาจิเมะซัง"),
    ("batch_004.done.json",
     "Hajime-san, you actually got up on your own?\nWill wonders never cease...",
     "ท่านฮาจิเมะ", "ฮาจิเมะซัง"),
    ("batch_004.done.json",
     "That'll be the day. Once Hajime-san realizes\njust what a Shinsengumi captain can have,",
     "ท่านฮาจิเมะ", "ฮาจิเมะซัง"),
    ("batch_MSG_027.done.json", None,  # ซังแทรกกลางชื่อ
     "ไซโตซัง ฮาจิเมะ", "ไซโต ฮาจิเมะซัง"),

    # --- ข. "ท่าน" + "ซัง" ซ้อนกัน (ja=斎藤さん) ---
    ("batch_MSG_011.done.json", None, "ท่านไซโตซัง", "ไซโตซัง"),

    # --- ค. ja=斎藤さん/斎藤はん แต่ไทยใช้ "ท่านไซโต" (EN ตัดชื่อทิ้ง) ---
    ("batch_MSG_014.done.json",
     "The gentleman went to Watami a while ago. You do remember my wish to entertain him, I hope.",
     "ท่านไซโต", "ไซโตซัง"),
    ("batch_MSG_014.done.json", "Actually, you might be just the person I need!",
     "ท่านไซโต", "ไซโตซัง"),
    ("batch_MSG_014.done.json", "Would you mind entertaining someone for me?",
     "ท่านไซโต", "ไซโตซัง"),
    ("batch_MSG_014.done.json",
     "Well, for one, you're very respectable. And two, you're quite versed in the arts, aren't you?",
     "ท่านไซโต", "ไซโตซัง"),
    ("batch_MSG_014.done.json",
     "I'm confident that someone as cultured as you would make fine—very fine—company for Kanda-sensei.",
     "ท่านไซโต", "ไซโตซัง"),
    ("batch_MSG_023.done.json",
     "Haha. Hey, care to join us for a drink? ...Well, I'm gonna guess you'd rather not.",
     "ท่านไซโต", "ไซโตซัง"),
    ("batch_MSG_025.done.json",
     "Well, I can't write good articles if I don't take some risks! Now, let's do an interview and change the course of kawaraban together!",
     "ท่านไซโต", "ไซโตซัง"),
    ("batch_MSG_026.done.json",
     "That was simply amazing. It seems I've nothing more to teach you.",
     "ท่านไซโต", "ไซโตซัง"),

    # --- ง. EN เขียน "Saito-san" ตรง ๆ แต่ไทยตกคำ "ซัง" ---
    ("batch_MSG_028.done.json", "Um, aren't you Saito-san from the Shinsengumi?",
     "ไซโตแห่ง", "ไซโตซังแห่ง"),
    # ja=斉藤さーん (ตัวคันจิ 斉 ของ NPC ambient) — คีย์พี่น้องอีก 7 คีย์ใช้ "ไซโตซัง" หมด
    ("batch_067.done.json", "Mister Saito!", "พี่ไซโต", "ไซโตซัง"),

    # --- จ. ja=斎藤の旦那 (คนหามเกี้ยว/นายหน้าข่าวเรียกลูกค้า) = "นายท่าน" ตาม glossary §ท้าย ---
    ("batch_MSG_023.done.json", "Sir? Mister Saito?",
     "...ท่านนี่เอง...ท่านไซโตนี่เอง", "...นายท่านนี่เอง...นายท่านไซโตนี่เอง"),

    # --- ฉ. ป้ายตำแหน่ง "Captain Saito" = หัวหน้าหน่วยไซโต (13 : 2) ---
    ("batch_MSG_002.done.json",
     "Captain Saito, sir? To get to the gambling den where Okada Izo is, I advise going around from the path where the pawn shop resides on East Shijo Street.",
     "ท่านหัวหน้าหน่วยไซโต", "หัวหน้าหน่วยไซโต"),
    ("batch_MSG_045.done.json", "Greetings, Captain Saito.",
     "ท่านหัวหน้าหน่วยไซโต", "หัวหน้าหน่วยไซโต"),
]


def main() -> int:
    cache = {}
    total = 0
    problems = 0
    for fname, en_key, old, new in FIXES:
        path = DONE / fname
        if not path.exists():
            print(f"[ข้าม] ไม่พบไฟล์ {fname}")
            problems += 1
            continue
        data = cache.get(fname)
        if data is None:
            data = json.loads(path.read_text(encoding="utf-8"))
            cache[fname] = data
        strings = data["strings"]

        if en_key is None:
            keys = [k for k, v in strings.items() if v and old in v]
        else:
            if en_key not in strings:
                print(f"[ผิด] {fname}: ไม่มีคีย์ {en_key[:50]!r}")
                problems += 1
                continue
            keys = [en_key] if old in (strings[en_key] or "") else []

        if not keys:
            # กวาดไปแล้วในรอบก่อน — ไม่นับเป็นปัญหา ให้สคริปต์รันซ้ำเพื่อตรวจได้
            done_already = [
                k for k, v in strings.items()
                if v and new in v and (en_key is None or k == en_key)
            ]
            if done_already:
                print(f"{fname[6:-10]:>9} · [กวาดแล้ว] {new!r}")
            else:
                print(f"[ผิด] {fname}: ไม่พบ {old!r} ในคีย์ที่ระบุ")
                problems += 1
            continue
        for k in keys:
            strings[k] = strings[k].replace(old, new)
            total += 1
        print(f"{fname[6:-10]:>9} · {len(keys)} คีย์ · {old!r} -> {new!r}")

    for fname, data in cache.items():
        (DONE / fname).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    print(f"\nแก้ {total} คีย์ · {len(cache)} ไฟล์ · รายการที่มีปัญหา {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
