"""batch_overlap.py — บอกว่าก้อนไหนใช้ไฟล์ฉาก .msg ร่วมกับก้อนไหน

ที่มา: เนื้อเรื่องย่อยหนึ่งเรื่องมักพาดหลายก้อน (จดหมายสำเนียงโทสะของฟูจิเอะกิน MSG_012 + MSG_013)
ถ้าไม่บอกนักแปล ต่างคนต่างตั้งคำ/ตั้งวิธีเล่ามุกคนละแบบ แล้วต้องมาแก้ทีหลังทั้งก้อน

ใช้: python scripts/batch_overlap.py MSG_019 MSG_020 ...   (ไม่ใส่ = ทุกก้อน MSG)
พิมพ์ว่าแต่ละก้อนใช้ไฟล์ร่วมกับก้อนใดบ้าง และก้อนนั้น merge ไปแล้วหรือยัง
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import paths

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def load_sources():
    out = {}
    for p in sorted(paths.WORKLIST.glob("batch_MSG_*.json")):
        if any(x in p.name for x in (".context", ".prior", ".todo", ".dnt")):
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        name = p.stem[len("batch_"):]
        out[name] = {s.split(":", 1)[1] for s in d.get("sources", []) if s.startswith("msg:")}
    return out


def main():
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    src = load_sources()
    done = {p.stem[len("batch_"):-len(".done")] for p in paths.DONE.glob("batch_MSG_*.done.json")}
    for b in (want or sorted(src)):
        if b not in src:
            print("ไม่พบ", b)
            continue
        rows = [(o, len(src[b] & src[o])) for o in src if o != b and src[b] & src[o]]
        rows.sort(key=lambda x: -x[1])
        if not rows:
            print("%-8s ไม่ใช้ไฟล์ร่วมกับก้อนอื่น" % b)
            continue
        txt = " · ".join("%s(%d%s)" % (o, n, " ✓แปลแล้ว" if o in done else "")
                         for o, n in rows[:5])
        print("%-8s ใช้ไฟล์ฉากร่วมกับ: %s" % (b, txt))


if __name__ == "__main__":
    main()
