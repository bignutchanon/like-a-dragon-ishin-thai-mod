#!/usr/bin/env python3
"""เสนอชื่อไทยของตัวละคร Lost Judgment ทุกตัว พร้อม **ที่มาของคำ** ให้ lead เคาะ

ลำดับการหาคำ (บนสุดชนะ):
  1. `locked`   — ชื่อที่ล็อกแล้วร่วมกับโปรเจกต์ JUDGMENT / คำสั่ง lead
  2. `tm-<ภาค>` — ชื่อสะกดเดียวกันที่ **ship ไปแล้วจริง** ในภาคก่อน (K3 > Gaiden > Y8 > Y7 > Judgment)
                  ⚠ อาจเป็นคนละตัวละคร — ใช้เป็น "แบบสะกด" เพื่อให้ผู้เล่นเห็นคำเดิม ไม่ใช่การยืนยันตัวบุคคล
  3. `rule`     — ทับศัพท์ตามกฎ (`scripts/romaji_to_thai.py`) — **ต้องมีคนเคาะเสมอ**
  4. `desc`     — ชื่อบรรยาย (Shop Owner / Dealer) → แปลความหมาย ไม่ทับศัพท์

ทุกแถวมี **คันจิจากไฟล์เกม** (`talk_talker.bin` เก็บชื่อ JA ไว้ทุกตัว) เพื่อให้ตรวจการอ่านได้

ผลลัพธ์:
  translations/name_proposals.md      ตารางให้ lead เคาะ (เรียงตามจำนวนบรรทัด)
  translations/name_proposals.json    {คีย์ตัวละคร: {en, ja, th, source, lines, gender}}
  + เขียนช่อง `name_th_proposal` กลับเข้า characters_main.json / characters_side.json

ใช้:  python scripts/make_name_proposals.py [--write] [--min-lines 20]
"""
import argparse
import collections
import io
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
from romaji_to_thai import convert as romaji_convert

THAI_RE = re.compile(r"[฀-๿]")
TALKER = paths.DB_EN / "talk_talker.bin.json"
OUT_MD = paths.TRANSLATIONS / "name_proposals.md"
OUT_JSON = paths.TRANSLATIONS / "name_proposals.json"

TM_SOURCES = [
    ("k3", paths.K3_PROJECT / "translations" / "master_th.json"),
    ("gaiden", paths.GAIDEN_PROJECT / "translations" / "master_th.json"),
    ("y8", paths.Y8_PROJECT / "translations" / "master_th.json"),
    ("y7", Path("D:/Projects/yakuza-7-like-a-dragon-thai/translations/master_th.json")),
    ("judgment", paths.TM_JUDGMENT),
]

# คำตัดสินรายชื่อที่กฎทับศัพท์ให้ผลผิด — ยืนยันการอ่านจากคันจิ/คาตาคานะในไฟล์เกม
# (ยังเป็น "ข้อเสนอ" เหมือนกัน แต่ผ่านการตรวจการอ่านแล้ว ไม่ใช่ผลดิบจากกฎ)
OVERRIDE = {
    "emily": "เอมิลี่",        # エミリ · ชื่อเต็ม Emily S. Mochizuki (ฝรั่ง ไม่ใช่ชื่อญี่ปุ่น)
    "tesso": "เท็ตโซ",         # 鉄爪 = てっそう (Tessō) เสียงซ้อน っ + สระยาว
    "suou": "ซูโอ",            # 周防 = すおう (Suō)
    "soma": "โซมะ",            # 相馬 = そうま (Sōma)
    "kalashnikov": "คาลาชนิคอฟ",  # カラシニコフ (ชื่อรัสเซีย)
    "ryan": "ไรอัน",           # ライアン
    "joe": "โจ",               # ジョー
    "seiryo": "เซเรียว",       # 誠稜 — คำสั่งผู้ใช้ 25 ส.ค. 2026
    "kitakata": "คิตาคาตะ",    # 北方 — ชื่อจริงของ Kuwana (เปิดในบทที่ 7 · ห้ามใช้ก่อนหน้านั้น)
    "fudo": "ฟุโด",            # 不動 = ふどう (Fudō) สระยาวท้ายคำ
    "bando": "บันโด",          # 坂東 = ばんどう (Bandō)
    "kento": "เคนโตะ",         # 研人 — น้องชายของ 天沢鏡子 (ยืนยันจากวิกิญี่ปุ่น)
}

# ชื่อบรรยาย/ชื่อฝรั่งที่กฎทับศัพท์ทำแทนไม่ได้ — แปลความหมาย/ทับศัพท์ด้วยมือ
# (คำตัดสินผู้ใช้ 25 ส.ค. 2026: "ที่เหลือใช้ทับศัพท์ไปก่อน" — เปลี่ยนภายหลังได้)
MANUAL = {
    "siren owner": "เจ้าของบาร์ไซเรน",
    "woman who dropped something": "หญิงที่ทำของหาย",
    "man who dropped something": "ชายที่ทำของหาย",
    "student who dropped something": "นักเรียนที่ทำของหาย",
    "shop owner": "เจ้าของร้าน",
    "high court judge": "ผู้พิพากษาศาลอุทธรณ์",
    "suou's mother": "แม่ของซูโอ",
    "shady bar owner": "เจ้าของร้านตีแพง",
    "rouge owner": "เจ้าของร้านรูจ",
    "female teacher": "ครูหญิง",
    "hanasaki's dad": "พ่อของฮานาซากิ",
    "scared woman": "หญิงที่หวาดกลัว",
    "portly middle-aged man": "ชายวัยกลางคนร่างท้วม",
    "long-faced basketball girl": "นักบาสหญิงหน้ายาว",
    "blond man": "ชายผมบลอนด์",
    "restaurant staff": "พนักงานร้านอาหาร",
    "boys' basketball captain": "กัปตันทีมบาสชาย",
    "senpai leader": "หัวหน้ารุ่นพี่",
    "policeman": "ตำรวจ",
    "milkee": "มิลค์กี้",              # みるきぃ (ชื่อเล่นแบบคาตาคานะ)
    "old_mamiya": "มามิยะ (รุ่นผู้ใหญ่)",  # คีย์เสียง ไม่ใช่ชื่อที่โผล่บนจอ
    "dealer": "เจ้ามือ",
    "mc": "พิธีกร",                    # MC = ผู้ดำเนินรายการบนเวที/มินิเกม
    "suspicious man": "ชายน่าสงสัย",
    "rugged thug": "อันธพาลหยาบกระด้าง",
}

# ชื่อที่ไม่ใช่ญี่ปุ่น (มี l/v/x หรือรูปคำฝรั่ง) — กฎทับศัพท์ญี่ปุ่นใช้ไม่ได้
FOREIGN_RE = re.compile(r"[lvx]", re.I)

# ชื่อบรรยาย (ไม่ใช่ชื่อคน) — แปลความหมาย
DESCRIPTIVE = re.compile(
    r"\b(man|woman|lady|girl|boy|owner|master|staff|clerk|dealer|judge|thug|student|teacher|"
    r"customer|guest|driver|officer|police|doctor|nurse|chef|waiter|waitress|guard|"
    r"receptionist|manager|worker|passerby|kid|child|announcer|caster|reporter)\b", re.I)


def load_talker_ja():
    """{ชื่อ EN (lower): ชื่อ JA} จาก talk_talker.bin"""
    if not TALKER.exists():
        return {}
    t = json.load(io.open(TALKER, encoding="utf-8"))
    out = {}
    for k, v in t.items():
        if not k.isdigit() or not isinstance(v, dict):
            continue
        ja, row = list(v.items())[0]
        en = (row.get("talk_talker") or "").strip() if isinstance(row, dict) else ""
        if en:
            out.setdefault(en.lower(), (ja or "").strip())
    return out


def load_tm():
    """{ชื่อ EN (lower): (ไทย, ภาค)} — เฉพาะ string สั้นที่ ship แล้ว"""
    out = {}
    for label, p in TM_SOURCES:
        if not p.exists():
            continue
        d = json.load(io.open(p, encoding="utf-8"))
        for en, th in d.items():
            if not isinstance(th, str) or not th.strip() or "\n" in en or len(en) > 24:
                continue
            if THAI_RE.search(th) and en.lower() not in out:
                out[en.lower()] = (th.strip(), label)
    return out


def propose(name, tm):
    """คืน (ไทย, ที่มา)"""
    low = name.strip().lower()
    if low in OVERRIDE:
        return OVERRIDE[low], "checked"
    if low in MANUAL:
        return MANUAL[low], "manual"
    th, how = romaji_convert(name)
    if how == "locked":
        return th, "locked"
    for cand in (name, name + "-san", name + "-kun", name + "-chan"):
        hit = tm.get(cand.lower())
        if hit:
            val = re.sub(r"(ซัง|คุง|จัง)$", "", hit[0]).strip()
            return val, "tm-%s" % hit[1]
    if FOREIGN_RE.search(name) and not DESCRIPTIVE.search(name):
        return "", "foreign"     # ชื่อฝรั่ง/คาตาคานะ — ต้องให้คนทับศัพท์เอง
    if DESCRIPTIVE.search(name) or " " in name.strip():
        hit = tm.get(low)
        if hit:
            return hit[0], "tm-%s" % hit[1]
        return "", "desc"        # ชื่อบรรยาย ไม่มีคำเดิม -> ให้คนแปลความหมาย
    return th, "rule"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--min-lines", type=int, default=0,
                    help="เสนอเฉพาะตัวละครที่มีบทตั้งแต่กี่บรรทัดขึ้นไป")
    a = ap.parse_args()

    ja_names = load_talker_ja()
    tm = load_tm()
    print("ชื่อ JA จากไฟล์เกม %d · คู่ชื่อจาก TM ภาคก่อน %s"
          % (len(ja_names), format(len(tm), ",")))

    files = [paths.TRANSLATIONS / "characters_main.json",
             paths.TRANSLATIONS / "characters_side.json"]
    result = collections.OrderedDict()
    stats = collections.Counter()
    changed = {}

    for f in files:
        if not f.exists():
            continue
        data = json.load(io.open(f, encoding="utf-8"),
                         object_pairs_hook=collections.OrderedDict)
        for key, rec in data.items():
            if rec.get("lines", 0) < a.min_lines:
                continue
            names = rec.get("names_in_game") or [key]
            en = next((n for n in names if not re.search(r"[_0-9]", n)), names[0])
            ja = ""
            for n in names:
                ja = ja_names.get(n.lower(), "")
                if ja:
                    break
            if rec.get("name_th") and rec["name_th"] != "⏳":
                th, how = rec["name_th"], "locked"
            else:
                th, how = propose(en, tm)
            rec["name_th_proposal"] = th or (
                "⏳ (ชื่อฝรั่ง — ทับศัพท์เอง)" if how == "foreign"
                else "⏳ (ชื่อบรรยาย — แปลความหมาย)")
            rec["name_source"] = how
            rec["name_ja"] = ja
            result[key] = {"en": en, "ja": ja, "th": th, "source": how,
                           "lines": rec.get("lines", 0), "gender": rec.get("gender", "unknown"),
                           "file": f.name}
            stats[how.split("-")[0]] += 1
        changed[f] = data

    print("เสนอชื่อ %d ตัวละคร: %s" % (len(result), dict(stats)))
    if not a.write:
        print("(ใส่ --write เพื่อเขียนไฟล์)")
        return 0

    for f, data in changed.items():
        io.open(f, "w", encoding="utf-8", newline="\n").write(
            json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    io.open(OUT_JSON, "w", encoding="utf-8", newline="\n").write(
        json.dumps(result, ensure_ascii=False, indent=1) + "\n")

    rows = sorted(result.items(), key=lambda kv: -kv[1]["lines"])
    L = ["# ชื่อไทยของตัวละคร — ร่างให้ lead เคาะ (Lost Judgment)", "",
         "> สร้างด้วย `python scripts/make_name_proposals.py --write`", "",
         "| ที่มาของคำ | ความหมาย |", "|---|---|",
         "| `locked` | ล็อกแล้ว (ร่วมกับโปรเจกต์ JUDGMENT หรือคำสั่ง lead) — **ห้ามเปลี่ยน** |",
         "| `tm-<ภาค>` | สะกดเดียวกันเคย ship แล้วในภาคนั้น — ใช้ต่อเพื่อให้ผู้เล่นเห็นคำเดิม "
         "(⚠ อาจเป็นคนละตัวละคร ตรวจคันจิประกอบ) |",
         "| `rule` | ทับศัพท์ตามกฎ `romaji_to_thai.py` — **ต้องเคาะ** |",
         "| `desc` | ชื่อบรรยาย ไม่ใช่ชื่อคน → แปลความหมาย |",
         "| `checked` | กฎให้ผลผิด — ตรวจการอ่านจากคันจิ/คาตาคานะในไฟล์เกมแล้วแก้ให้ |",
         "| `foreign` | ชื่อฝรั่ง/คาตาคานะ กฎญี่ปุ่นใช้ไม่ได้ → คนทับศัพท์เอง |",
         "| `manual` | ชื่อบรรยาย/ชื่อฝรั่งที่คนใส่คำไทยให้แล้ว (แก้ที่ตาราง MANUAL ในสคริปต์) |", "",
         "| ตัวละคร | EN | คันจิในเกม | ไทย (เสนอ) | ที่มา | เพศ | บรรทัด |",
         "|---|---|---|---|---|---|---|"]
    for key, r in rows:
        L.append("| `%s` | %s | %s | **%s** | %s | %s | %d |"
                 % (key, r["en"], r["ja"] or "-", r["th"] or "⏳", r["source"],
                    r["gender"], r["lines"]))
    io.open(OUT_MD, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("เขียน %s\nเขียน %s\n+ ช่อง name_th_proposal ในไฟล์ตัวละคร" % (OUT_MD, OUT_JSON))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
