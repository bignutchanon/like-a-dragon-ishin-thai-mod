"""กวาดคำยืมสมัยใหม่ที่หลุดเข้าบทพูดยุคบาคุมัตสึ (sprint 16)

พบตอนสแกนทั้งคลังด้วย `thai_pronouns.modern_loanwords()` หลังแก้บวกปลอมของตัวตรวจแล้ว
— ด่าน M ของ `merge_qc.py` เป็น "คำเตือน" ไม่ใช่ "ตก" คำพวกนี้จึงผ่านมาได้ทีละก้อน

⚠ ที่ตรวจแล้วไม่ใช่คำยืมจริง (ตัวตรวจจับซับสตริงโดยบังเอิญ — แก้ที่ `LOAN_FALSE_HITS` แล้ว)
  ระดับ**อสูร** · กับ**อสูร** -> "บอส" 8 จุด · ท่าน**เคสุ**เกะ -> "เคส" 3 จุด
  · โชกุน**โอเคฮาซามะ** -> "โอเค" 1 จุด

⚠ ที่ตรวจแล้วปล่อยไว้: `เกม` 105 จุด · `เวอร์`(เซิร์ฟเวอร์/เวอร์ชัน) 17 · `รีเซ็ต` 7 · `โฟกัส` 3
  · `อีเมล` 2 · `เทคโนโลยี` 4 — ทั้งหมดอยู่ในชั้นเมนู/ข้อความระบบ ไม่ใช่บทพูดของตัวละคร

รันแล้วต้องตามด้วย: merge_qc.py --only <ก้อนที่แก้>
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DONE = Path("translations/done")

# (ไฟล์ก้อน, คีย์ EN, เดิม, ใหม่)
FIXES = [
    # --- โอเค ในบทพูด — ทุกบรรทัด ref_ja เป็นคำญี่ปุ่นธรรมดา ไม่มีคำยืม ---
    ("batch_MSG_008.done.json", "And... that's okay with you?",
     "เจ้าโอเคกับแบบนั้น", "เจ้ายอมรับแบบนั้น"),          # ref_ja それでいいのか？お前は？
    ("batch_MSG_013.done.json", "Okay, then...",
     "โอเค งั้น...", "เข้าใจแล้ว งั้น..."),               # ref_ja わ、わかりました
    ("batch_MSG_019.done.json", "Hey, all right. And your pay.",
     "โอเค เอาล่ะ", "ขอบใจ เอาล่ะ"),                      # ref_ja ありがとう
    ("batch_MSG_019.done.json", "Oh. Okay.",
     "อ๋อ โอเค", "อ๋อ เข้าใจแล้ว"),                        # ref_ja そうか。
    ("batch_MSG_019.done.json",
     "Okay! I mean, I'm disappointed, but maybe another time?",
     "โอเค! อือ ผิดหวัง", "งั้นหรือ อือ ผิดหวัง"),        # ref_ja そうか……残念だけど
    # --- แคร์ ---
    ("batch_MSG_029.done.json", "What do you care? It's just some stray.",
     "มึงจะแคร์ทำไมวะ", "มึงจะสนทำไมวะ"),
    # --- เช็ก (ศัพท์โป๊กเกอร์) -> "ขอผ่าน" ซึ่งเป็นคำไทยที่สื่อความเดียวกัน ---
    ("batch_038.done.json", None, "ทุกคนเช็กตาครบรอบแล้ว", "ทุกคนขอผ่านครบรอบแล้ว"),
]


def main() -> int:
    cache = {}
    total = 0
    problems = 0
    for fname, en_key, old, new in FIXES:
        path = DONE / fname
        if not path.exists():
            print(f"[ผิด] ไม่พบไฟล์ {fname}")
            problems += 1
            continue
        if fname not in cache:
            cache[fname] = json.loads(path.read_text(encoding="utf-8"))
        strings = cache[fname]["strings"]
        if en_key is not None and en_key not in strings:
            print(f"[ผิด] {fname}: ไม่มีคีย์ {en_key[:45]!r}")
            problems += 1
            continue
        keys = [
            k for k, v in strings.items()
            if v and old in v and (en_key is None or k == en_key)
        ]
        label = fname[len("batch_"):-len(".done.json")]
        if not keys:
            already = any(
                v and new in v and (en_key is None or k == en_key)
                for k, v in strings.items()
            )
            if already:
                print(f"{label:>9} · [กวาดแล้ว] {new!r}")
            else:
                print(f"[ผิด] {fname}: ไม่พบ {old!r}")
                problems += 1
            continue
        for k in keys:
            strings[k] = strings[k].replace(old, new)
            total += 1
        print(f"{label:>9} · {len(keys)} คีย์ · {old!r} -> {new!r}")

    for fname, data in cache.items():
        (DONE / fname).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(f"\nแก้ {total} คีย์ · {len(cache)} ไฟล์ · รายการที่มีปัญหา {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
