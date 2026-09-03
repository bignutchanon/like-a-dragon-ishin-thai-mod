"""bond_gender.py — เพศของ NPC สายสัมพันธ์ จากสรรพนามในข้อความอังกฤษของเกมเอง

ป้ายสายสัมพันธ์ของภาคนี้เขียนไว้ตรง ๆ ว่า NPC คนนั้นเป็นเพศอะไร:

    "You have formed a bond with the Trash Dealer. You can deepen your bond by
     continuing to interact with **him** and filling the bond gauge."

เป็นหลักฐานจากไฟล์เกม (ไม่ใช่การเดา) และปิดช่องว่างที่หลักฐานญี่ปุ่นให้ไม่ได้ —
NPC ที่พูดสุภาพตลอดจะไม่มีสรรพนาม 俺/あたし ให้จับเลย ตาราง `speakers.json` จึงขึ้น `unknown`

⚠ **ทำไมไม่เอาเข้าด่าน G อัตโนมัติ**
หลักฐานนี้บอกเพศของ **ตัวละคร** ได้แน่ แต่การชี้ว่า *บรรทัดไหน* เป็นบทของเขาไม่แน่:
ป้ายผู้พูดในชั้น `.msg` ติดมาแบบหลวม ๆ (แถวเดียวมีหลายป้าย) วัดแล้วตรงกับเครื่องหมาย
ในต้นฉบับญี่ปุ่นของป้ายเดียวกันแค่ **17 ตรง · 6 ขัด (74%)** ต่ำกว่าเกณฑ์ 99.2%
ที่ `build_scene_gender.py` ใช้อยู่มาก → ใช้เป็น **ตารางอ้างอิงให้คนอ่าน** เท่านั้น
นักแปล/ผู้ตรวจอ่านฉากแล้วชี้เองว่าบรรทัดนั้นเป็นบทของ NPC คนนี้จริงไหม

เขียนออก:
  translations/bond_gender.json          NPC -> เพศ + ไฟล์ฉาก + ประโยคหลักฐาน (เครื่องอ่าน)
  docs/reference/bond_npc_gender.md      ตารางให้คนอ่าน

ใช้: python scripts/bond_gender.py
ต้องมีมาก่อน: scripts/build_parallel.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import paths

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BOND = re.compile(r"formed a bond with (?:the )?(.+?)\.\s", re.S)
PRON = re.compile(r"interact(?:ing)? with (him|her)\b")
OUT_JSON = paths.TRANSLATIONS / "bond_gender.json"
OUT_DOC = paths.PROJECT / "docs" / "reference" / "bond_npc_gender.md"


def main():
    rows = json.loads((paths.EXTRACTED / "parallel" / "msg.json").read_text(encoding="utf-8"))

    npcs = {}
    for r in rows:
        en = r.get("en") or ""
        m, p = BOND.search(en), PRON.search(en)
        if not (m and p):
            continue
        name = m.group(1).strip()
        gender = "male" if p.group(1) == "him" else "female"
        prev = npcs.get(name)
        if prev and prev["gender"] != gender:
            print("⚠ %s ได้สรรพนามขัดกันสองที่ (%s vs %s) — ตัดออก"
                  % (name, prev["gender"], gender))
            prev["conflict"] = True
            continue
        npcs.setdefault(name, {
            "gender": gender,
            "scenes": [],
            "evidence": p.group(0),
            "ja": r.get("ja") or "",
        })["scenes"].append("%s#%03d" % (r["file"], r["line"]))

    npcs = {k: v for k, v in npcs.items() if not v.get("conflict")}
    OUT_JSON.write_text(json.dumps(npcs, ensure_ascii=False, indent=1), encoding="utf-8")

    n_f = sum(1 for v in npcs.values() if v["gender"] == "female")
    doc = ["# เพศของ NPC สายสัมพันธ์ — จากสรรพนามในข้อความอังกฤษของเกม", "",
           "สร้างโดย `scripts/bond_gender.py` · **ทุกแถวมาจากไฟล์เกม ไม่มีการเดา**", "",
           "ป้ายสายสัมพันธ์เขียนเพศของ NPC ไว้ตรง ๆ (\"…interact with **him/her**…\") "
           "ซึ่งเป็นหลักฐานที่ต้นฉบับญี่ปุ่นให้ไม่ได้ เพราะ NPC ที่พูดสุภาพตลอด"
           "จะไม่มีสรรพนาม 俺/あたし ให้จับเลย", "",
           "⚠ **ใช้อย่างไร** — หลักฐานนี้บอกเพศของ**ตัวละคร** ไม่ได้บอกว่า*บรรทัดไหน*เป็นบทของเขา",
           "ป้ายผู้พูดในชั้น `.msg` ติดมาหลวม ๆ (วัดแล้วตรงกับเครื่องหมายญี่ปุ่นของป้ายเดียวกัน 74%)",
           "→ อ่านฉากก่อนเสมอ ถ้าบรรทัดนั้นเป็นบทของ NPC คนนี้จริงจึงใช้คำลงท้ายตามเพศได้",
           "**ด่าน G ไม่ได้ใช้ตารางนี้อัตโนมัติ**", "",
           "รวม %d ตัว (ชาย %d · หญิง %d)" % (len(npcs), len(npcs) - n_f, n_f), "",
           "| NPC | เพศ | ฉากที่พบ |", "|---|---|---|"]
    for name in sorted(npcs, key=lambda n: (npcs[n]["gender"], n)):
        v = npcs[name]
        doc.append("| %s | **%s** | %s |"
                   % (name, "หญิง" if v["gender"] == "female" else "ชาย",
                      " · ".join("`%s`" % s for s in v["scenes"][:3])))
    OUT_DOC.write_text("\n".join(doc) + "\n", encoding="utf-8")

    print("NPC สายสัมพันธ์ที่รู้เพศจากป้าย %d ตัว (ชาย %d · หญิง %d)"
          % (len(npcs), len(npcs) - n_f, n_f))
    print("->", OUT_JSON)
    print("->", OUT_DOC)


if __name__ == "__main__":
    main()
