#!/usr/bin/env python3
"""ด่านตรวจ: ตำแหน่งตัวอักษรในบล็อกคำสั่งของ .msg ที่บิลด์แล้ว ต้องตรงกับข้อความจริง

ทุกบรรทัดใน .msg มีบล็อกคำสั่ง 16 ไบต์ต่อคำสั่ง และทุกคำสั่งเก็บ "ตำแหน่งตัวอักษรในบรรทัด"
ที่ไบต์ [6:8] คำสั่งปิดบรรทัด (`01 01` · `02 09`) เก็บค่าเท่ากับความยาวของบรรทัด
เกมวาดข้อความถึงตำแหน่งนั้นแล้วหยุด — ถ้าค่าน้อยกว่าความยาวจริง ตัวท้ายจะหายไปจากจอ

หน่วยที่เกมนับคือ **ตัวอักษรที่วาดบนจอ** ไม่นับแท็ก (`msg.disp_chars`) ยกเว้น
`<symbol=...>` กับ `<Sign:...>` ที่นับเป็นหนึ่ง — พิสูจน์กับคลัง vanilla en + ja
65,853 จาก 65,855 บรรทัด (ที่เหลือคือแท็ก `<%download_content%>` ที่เกมแทนตอนรัน)

บั๊กจริงที่ด่านนี้จับได้ (11 ก.ย. 2026): `retime_cmds` รุ่นแรกนับเป็น code point ของสตริงดิบ
บรรทัดที่มีแท็กจึงหาจุดจบบรรทัดไม่เจอ แล้วไปเข้าทางสเกลตามสัดส่วนแทน
"ได้รับ <Color:8>โมเดล 2<Color:Default> แล้ว" ได้จุดจบ 18 ทั้งที่ต้องเป็น 19
บนจอขึ้น "ได้รับ โมเดล 2 แล้" — 343 บรรทัดในบิลด์ v1.3 ตัวท้ายหาย

    python scripts/check_msg_charpos.py            # ต้องได้ "เกิน 0 · ขาด 0"
"""
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import msg as msgmod  # noqa: E402

BUILD = Path(__file__).resolve().parent.parent / "build" / "text" / "msg"
# แท็กที่เกมแทนด้วยข้อความจริงตอนรัน ความยาวบนจอจึงไม่ตรงกับในไฟล์
RUNTIME_TAGS = ("<%",)


def main():
    if not BUILD.is_dir():
        print("ยังไม่มี %s — รัน scripts/build_text.py ก่อน" % BUILD)
        return 1
    files = sorted(BUILD.glob("*.msg"))
    hist, short, over = Counter(), [], []
    lines = 0
    for f in files:
        try:
            m = msgmod.load(f)
        except Exception as e:
            print("อ่านไม่ได้ %s: %s" % (f.name, e))
            return 1
        for ln in m.lines:
            if not ln.text or not ln.cmds:
                continue
            if any(t in ln.text for t in RUNTIME_TAGS):
                continue
            top = max(((c[6] << 8) | c[7]) for c in ln.cmds)
            if top == 0:
                continue
            lines += 1
            diff = top - msgmod.disp_chars(ln.text)
            hist[diff] += 1
            if diff < 0:
                short.append((f.name, ln.index, diff, ln.text))
            elif diff > 0:
                over.append((f.name, ln.index, diff, ln.text))

    print("ไฟล์ %d · บรรทัดที่วัด %d" % (len(files), lines))
    print("ขาด (ตัวท้ายหายบนจอ) %d · เกิน %d" % (len(short), len(over)))
    for name, idx, diff, text in (short + over)[:20]:
        print("  %s#%03d  %+d  %s" % (name, idx, diff, text[:70]))
    return 1 if (short or over) else 0


if __name__ == "__main__":
    raise SystemExit(main())
