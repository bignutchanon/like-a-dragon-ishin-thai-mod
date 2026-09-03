#!/usr/bin/env python3
"""ระบุ "ใครส่ง" ในบทสนทนาแชทมือถือ (`pause_message.bin`) — ตอบคำถามที่ค้างมาหลาย batch

ที่มา: ผู้ตรวจ batch_082 ถอดโครงสร้างได้ว่าแต่ละแถวมี field `"2"` เป็น **ธงบอกฝั่งผู้ส่ง**
  2 = ข้อความที่ยากามิส่งออก        5 = ข้อความที่คู่สนทนาส่งมา
  1 = ข้อความบรรยาย/ระบบ            3 = แถวตัวเลือกคำตอบ (3 ตัวเลือก)
  7 = อ้างถึงตัวเลือกที่ผู้เล่นเลือก   8 = จบบทสนทนา
ตรวจแล้วสอดคล้องกันในตารางของหลายตัวละคร

สคริปต์นี้แปลงเป็น `extracted/facts/chat_sender.json` = {ข้อความ EN: {"role": ..., "contact": ...}}
ให้นักแปล/ผู้ตรวจ **ค้นด้วยข้อความ EN ตรง ๆ แล้วรู้ทันทีว่าเป็นบทของยากามิหรือของคู่สนทนา**
(ก่อนหน้านี้ต้องเดาจากเนื้อหาล้วน ๆ — batch_082/083/084 เจอปัญหานี้ทั้งสามตัว)

ใช้:  python scripts/make_chat_sender.py [--write]
"""
import argparse
import collections
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

SRC = paths.DB_EN / "pause_message.bin.json"
PERSON = paths.DB_EN / "pause_message_person.bin.json"
OUT = paths.EXTRACTED / "facts" / "chat_sender.json"
DOC = paths.DOCS / "reference" / "chat_sender.md"
ROLE = {
    1: "narration",     # บรรยาย/ระบบ
    2: "yagami",        # ยากามิส่งออก
    3: "choice",        # แถวตัวเลือกคำตอบ
    5: "contact",       # คู่สนทนาส่งมา
    7: "chosen_echo",   # อ้างถึงตัวเลือกที่เลือก
    8: "end",           # จบบทสนทนา
}


def person_names():
    """id ของคู่สนทนา -> ชื่อจริง จาก `pause_message_person.bin.json`

    (ผู้ตรวจ batch_084 เจอ: field `"3"` ของแต่ละแถวคือ **person id ของผู้ส่ง** และเชื่อกับตารางนี้
    · สำคัญกว่าชื่อระดับ subTable เพราะบางเธรดของนานามิมียุกโกะพูดแทรกทั้งชุด)
    """
    out = {}
    if not PERSON.exists():
        return out
    data = json.load(io.open(PERSON, encoding="utf-8"))
    for k, v in data.items():
        if k.isdigit() and isinstance(v, dict):
            for cells in v.values():
                if isinstance(cells, dict) and isinstance(cells.get("name"), str) and cells["name"].strip():
                    out[int(k)] = cells["name"].strip()
    return out


def rows_of(obj, contact=""):
    """คืน (ชื่อตาราง, ชื่อคู่สนทนา, dict แถว) — field `name` ของ subTable บอกชื่อคู่สนทนาตรง ๆ

    (ผู้ตรวจ batch_083 เจอ: subTable ของแต่ละบทสนทนามี `"name": "Tsukino Saotome"` กำกับไว้)
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(v, dict):
                continue
            name = v.get("name")
            child = contact
            if isinstance(name, str) and name.strip() and name not in ("Inbox", "Outbox"):
                child = name.strip()
            if "table" in v and isinstance(v["table"], dict):
                yield k, child, v["table"]
            yield from rows_of(v, child)


def collect(data):
    out = collections.OrderedDict()
    counts = collections.Counter()
    people = person_names()
    for table_name, contact, table in rows_of(data):
        for idx, row in table.items():
            if not isinstance(row, dict):
                continue
            for cells in row.values():
                if not isinstance(cells, dict):
                    continue
                flag = cells.get("2")
                # field "3" = person id ของผู้ส่งบรรทัดนั้น — แม่นกว่าชื่อระดับ subTable
                pid = cells.get("3")
                line_contact = people.get(pid) if isinstance(pid, int) else None
                # เอาเฉพาะค่าที่เป็นข้อความจริง — บางคอลัมน์เก็บตัวเลขไว้เป็นสตริง
                texts = [v for k, v in cells.items()
                         if isinstance(v, str) and len(v.strip()) > 1
                         and any(c.isalpha() for c in v) and k not in ("0", "1", "2", "3")]
                if not isinstance(flag, int) or not texts:
                    continue
                role = ROLE.get(flag, "flag%d" % flag)
                # ⚠ ธง 2 = "ข้อความที่**ผู้เล่น**ส่งออก" ไม่ใช่ "ยากามิ" เสมอไป —
                # ในบท The Kaito Files (ตารางขึ้นต้น `coyote_dlc_`) ผู้เล่นคือ **ไคโตะ**
                # เจอ 26 ส.ค. 2026 (sprint 14 · นักแปล batch_118 ไล่เนื้อหาแล้วพบว่าบล็อกที่ role
                # บอกว่า "yagami" จริง ๆ เป็นบทของไคโตะที่คุยกับยากามิ — หลักฐานคือถูกเรียก "Kaito-san"
                # และ contact ของข้อความขาเข้าคือ "Takayuki Yagami")
                player = "kaito" if str(table_name).startswith("coyote_dlc_") else "yagami"
                counts[role] += len(texts)
                for t in texts:
                    prev = out.get(t)
                    if prev is None:
                        out[t] = collections.OrderedDict(
                            [("role", role), ("player", player),
                             ("contact", line_contact or contact or "?"),
                             ("table", table_name)])
                    elif prev["role"] != role:
                        prev["role"] = "ambiguous"   # ข้อความเดียวใช้ทั้งสองฝั่ง (เช่น "Yeah.")
    return out, counts


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="เขียนไฟล์จริง")
    a = ap.parse_args()

    if not SRC.exists():
        print("ไม่พบ %s — ยังไม่ได้ extract?" % SRC)
        return 1
    data = json.load(io.open(SRC, encoding="utf-8"))
    mapping, counts = collect(data)
    amb = sum(1 for v in mapping.values() if v["role"] == "ambiguous")
    print("ข้อความแชทที่ระบุฝั่งได้ %s บรรทัด (กำกวม %d)" % (format(len(mapping), ","), amb))
    print("แยกตามบทบาท: %s" % " · ".join("%s=%s" % (k, format(v, ",")) for k, v in counts.most_common()))

    if not a.write:
        for t, v in list(mapping.items())[:8]:
            print("   %-8s %s" % (v["role"], t.replace("\n", " / ")[:62]))
        print("(ใส่ --write เพื่อเขียนไฟล์)")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(
        json.dumps(mapping, ensure_ascii=False, indent=1) + "\n")
    lines = [
        "# ใครส่งข้อความแชท — `pause_message.bin`",
        "",
        "สร้างด้วย `python scripts/make_chat_sender.py --write` → `extracted/facts/chat_sender.json`",
        "รูปแบบ: `{ข้อความ EN: {\"role\": ..., \"contact\": ชื่อคู่สนทนา, \"table\": ...}}`",
        "",
        "| role | ความหมาย |",
        "|---|---|",
        "| `yagami` | ข้อความที่**ผู้เล่น**ส่งออก — ดูช่อง `player` ว่าเป็นใคร: `yagami` (เนื้อเรื่องหลัก) หรือ `kaito` (ตารางขึ้นต้น `coyote_dlc_` = The Kaito Files) |",
        "| `contact` | ข้อความที่คู่สนทนาส่งมา |",
        "| `choice` | แถวตัวเลือกคำตอบ — **แปลสั้นแบบปุ่ม** |",
        "| `chosen_echo` | ตัวเลือกที่ผู้เล่นเลือก แสดงซ้ำเป็นข้อความที่ส่งออก |",
        "| `narration` | ข้อความบรรยาย/ระบบ — ไม่ผูกสรรพนาม |",
        "| `end` | หมายจบบทสนทนา |",
        "| `ambiguous` | ข้อความเดียวถูกใช้ทั้งสองฝั่ง (เช่น \"Yeah.\") — ต้องดูบริบท |",
        "",
        "**ที่มา**: ผู้ตรวจ batch_082 ถอดได้ว่า field `\"2\"` ของแต่ละแถวคือธงบอกฝั่งผู้ส่ง",
        "(2=ยากามิ · 5=คู่สนทนา · 1=บรรยาย · 3=ตัวเลือก · 7=echo · 8=จบ) ตรวจแล้วสอดคล้องหลายตาราง",
        "",
        "**ใช้เมื่อไร**: ทุก batch ที่มี `pause_message.bin` ใน `source_bins` (เนื้อหา Friends/Girlfriend/แชท)",
        "— ก่อนหน้านี้นักแปลต้องเดาจากเนื้อหาล้วน ๆ ทำให้คำเรียก (เช่น \"นานามิซัง\" vs \"ยุกโกะซัง\") ผิดได้",
        "",
        "| ตัวเลข | ค่า |",
        "|---|---|",
        "| ข้อความที่ระบุฝั่งได้ | %s |" % format(len(mapping), ","),
        "| กำกวม (ใช้ทั้งสองฝั่ง) | %s |" % format(amb, ","),
        "",
    ]
    io.open(DOC, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("เขียน %s" % OUT)
    print("เขียน %s" % DOC)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
