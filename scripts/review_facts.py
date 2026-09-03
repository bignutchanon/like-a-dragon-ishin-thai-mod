"""สรุปตัวเลขจริงของก้อนหนึ่ง ๆ ไว้เขียนไฟล์รีวิว

ใช้ตอนปิดคลื่น: lead ต้องเขียน `translations/review/batch_MSG_0NN.review.md`
โดยห้ามเดาตัวเลข  สคริปต์นี้ดึงจากไฟล์จริงทั้งหมด —
worklist (คีย์ทั้งก้อน) · dnt (คีย์ที่สั่งคงต้นฉบับ) · done (คำแปล)
· gender_lines (บรรทัดที่ล็อกเพศ) · ไฟล์ฉาก `.msg` ที่ก้อนนี้กิน

รูปแบบ: python scripts/review_facts.py MSG_073 [MSG_074 ...]
"""
import json
import re
import sys

from paths import PROJECT

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

THAI = re.compile(r"[฀-๿]")
JA = re.compile(r"[぀-ヿ一-鿿]")
WORKLIST = PROJECT / "translations" / "worklist"
DONE = PROJECT / "translations" / "done"
TEXT_EN = PROJECT / "extracted" / "text_en"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def scene_owner(sources):
    """คีย์ -> ไฟล์ฉากแรกที่มีคีย์นั้น (อ่านจาก extracted/text_en)"""
    owner = {}
    for src in sources:
        if not src.startswith("msg:"):
            continue
        uid = src[4:]
        path = TEXT_EN / f"{uid}.json"
        if not path.exists():
            continue
        for item in load(path):
            text = item.get("en")
            if text:
                owner.setdefault(text, uid)
    return owner


def report(name):
    batch = load(WORKLIST / f"batch_{name}.json")
    done = load(DONE / f"batch_{name}.done.json")["strings"]
    dnt_path = WORKLIST / f"batch_{name}.dnt.json"
    dnt = load(dnt_path) if dnt_path.exists() else {}
    gl = load(PROJECT / "translations" / "gender_lines.json")

    keys = list(batch["strings"])
    thai = [k for k in keys if THAI.search(done.get(k, ""))]
    kept = [k for k in keys if done.get(k, "") == k]
    ja_left = [k for k in keys if JA.search(done.get(k, "")) and not THAI.search(done.get(k, ""))]
    locked = [k for k in keys if k in gl]

    print(f"== {name}")
    print(f"   คีย์ {len(keys)} · แปลไทย {len(thai)} · คงต้นฉบับ {len(kept)} "
          f"· DNT ในไฟล์ {len(dnt)} · ญี่ปุ่นค้าง {len(ja_left)} · gender_lines {len(locked)}")
    print(f"   ไฟล์ฉาก {len(batch['sources'])}: " + " ".join(s[4:] for s in batch["sources"]))

    owner = scene_owner(batch["sources"])
    tally = {}
    for k in keys:
        tally.setdefault(owner.get(k, "(ไม่พบไฟล์)"), []).append(k)
    for uid, ks in sorted(tally.items(), key=lambda kv: -len(kv[1])):
        n_th = sum(1 for k in ks if THAI.search(done.get(k, "")))
        head = ks[0].replace("\r\n", " / ")[:60]
        print(f"     {uid:14s} {len(ks):4d} คีย์ · ไทย {n_th:4d} · {head}")
    print()


def main() -> int:
    names = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not names:
        print("ใส่ชื่อก้อน เช่น MSG_073")
        return 1
    for n in names:
        report(n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
