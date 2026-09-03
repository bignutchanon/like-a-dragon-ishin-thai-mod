#!/usr/bin/env python3
"""ทำแผนที่ "บทพูด -> ผู้พูด" จาก `sound_auth.bin` (ตัวช่วยที่ทีมแปลขาดมาตลอด)

ที่มา: ทีมแปล/ผู้ตรวจหลายรอบเสียเวลาเดาว่าใครพูดบรรทัดไหน เพราะ `auth.bin` เก็บบทเป็นตาราง
`cinema_telop` ที่ **ไม่มีคอลัมน์ผู้พูด** — แต่ `sound_auth.bin` (บทที่ผูกกับไฟล์เสียง) เก็บบทไว้ใต้
คีย์ที่ **มีชื่อผู้พูดอยู่ในตัวคีย์เอง** เช่น `speech_btl06_030_yagami`, `speech_btl11_010_hamura`
สคริปต์นี้จึงเดินโครงสร้างแล้วผูก "ข้อความ EN -> คีย์ผู้พูดที่ลึกที่สุดที่ครอบมันอยู่"

ใช้ได้ทันทีตอนแปล: เจอบรรทัดที่ไม่รู้ผู้พูด ให้เปิด `extracted/facts/speech_speaker_map.json`
แล้วค้นข้อความนั้น ถ้าเจอจะได้ชื่อผู้พูดจากไฟล์เกมจริง (ไม่ใช่การเดา)

ข้อจำกัด: ครอบคลุมเฉพาะบทที่มีเสียงพากย์ใน `sound_auth.bin` — บทใน `auth.bin`/`talk.bin`
ที่ไม่มีเสียงยังไม่มีผู้พูดกำกับ (ต้องอนุมานจากบริบทเหมือนเดิม)

ใช้:  python scripts/make_speaker_map.py
"""
import io
import json
import os
import re
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

SRC = paths.DB_EN / "sound_auth.bin.json"
OUT_JSON = paths.EXTRACTED / "facts" / "speech_speaker_map.json"
OUT_MD = paths.DOCS / "reference" / "speaker_map_lj.md"

KEY_RE = re.compile(r"^(speech|talk|hact|cmn)_[A-Za-z0-9_]+$")
LETTERS = re.compile(r"[A-Za-z]{3}")
# ชื่อผู้พูดคือหางของคีย์ (ตัดเลขลำดับท้ายออก) เช่น speech_btl11_010_hamura003 -> hamura
TAIL_RE = re.compile(r"^speech_(?:btl|hact|auth|list)?[0-9_]*(?:btl|hact)?[0-9_]*(.*?)(\d+)?$")


def speaker_token(key):
    """ดึงชื่อผู้พูดจากคีย์ — คืน None ถ้าเป็นคีย์รวมกลุ่ม (list) ที่ไม่ได้ระบุตัวคน"""
    if key.startswith("speech_list"):
        return None
    parts = key.split("_")
    tail = [p for p in parts[1:] if not re.fullmatch(r"(btl|hact|auth|cmn|talk)?\d*", p)]
    if not tail:
        return None
    name = "_".join(tail)
    name = re.sub(r"\d+$", "", name)
    # ตัดคำนำหน้าที่บอก "บท" ออก (m01_yagami -> yagami) เพราะบทอยู่ในฟิลด์ chapter แล้ว
    name = re.sub(r"^m\d+_", "", name)
    # gaya_gaya_m / gaya_gaya_f = เสียงชาวเมืองทั่วไป ชาย/หญิง (ใช้เป็นหลักฐานเพศได้)
    return name or None



def index_speakers(data):
    """คืน {(list_key, index): speaker_key} จากตาราง subTable ที่อ้าง index ของบทพูด

    โครงจริงใน `sound_auth.bin` (ยืนยัน 21 ส.ค. 2026):
      /<row>/speech_list_coyote_main_cNN/table/<index>//4  = บทพูด (สำนวนที่ 1)
      /<row>/speech_list_coyote_main_cNN/table/<index>//6  = บทพูด (สำนวนที่ 2)
      /<row>/speech_list_coyote_main_cNN/table/subTable/<n>/<speech_key>/2 = <index> ที่คีย์นั้นอ้างถึง
    คีย์ `speech_m01_04600_amour_boy` มี **ชื่อผู้พูดต่อท้าย** จึงได้ผู้พูดรายบรรทัดจริง ๆ
    """
    out = {}

    def scan(node, list_key=None):
        if not isinstance(node, dict):
            return
        for k, v in node.items():
            if isinstance(k, str) and k.startswith("speech_list"):
                sub = (v or {}).get("table", {}).get("subTable", {})
                for _n, group in (sub or {}).items():
                    if not isinstance(group, dict):
                        continue
                    for skey, sval in group.items():
                        if not (isinstance(skey, str) and skey.startswith("speech_")):
                            continue
                        idx = sval.get("2") if isinstance(sval, dict) else None
                        if isinstance(idx, int):
                            out[(k, idx)] = skey
                scan(v, k)
            else:
                scan(v, list_key)

    scan(data)
    return out


def texts_by_index(data):
    """คืน {(list_key, index): [บทพูดทุกสำนวน]}"""
    out = {}

    def scan(node, list_key=None):
        if not isinstance(node, dict):
            return
        for k, v in node.items():
            nk = k if isinstance(k, str) and k.startswith("speech_list") else list_key
            if nk and isinstance(v, dict) and k == "table":
                for idx, row in v.items():
                    if not idx.isdigit() or not isinstance(row, dict):
                        continue
                    cell = row.get("", {})
                    if not isinstance(cell, dict):
                        continue
                    txts = [t for c, t in cell.items()
                            if isinstance(t, str) and len(t) > 2 and LETTERS.search(t)]
                    if txts:
                        out[(nk, int(idx))] = txts
            scan(v, nk)

    scan(data)
    return out


def main():
    if not SRC.exists():
        print("ไม่พบ %s — รัน extract_all_en.py ก่อน" % SRC)
        return 2
    data = json.load(io.open(SRC, encoding="utf-8"))

    lines = OrderedDict()        # ข้อความ EN -> set(คีย์ผู้พูด)
    key_counts = Counter()

    def walk(obj, key_ctx=None):
        if isinstance(obj, dict):
            for k, v in obj.items():
                nk = k if isinstance(k, str) and KEY_RE.match(k) else key_ctx
                walk(v, nk)
        elif isinstance(obj, list):
            for v in obj:
                walk(v, key_ctx)
        elif isinstance(obj, str):
            if key_ctx and len(obj) > 3 and LETTERS.search(obj):
                lines.setdefault(obj, [])
                if key_ctx not in lines[obj]:
                    lines[obj].append(key_ctx)
                key_counts[key_ctx] += 1

    walk(data)

    # ---- ผู้พูดรายบรรทัดจริง (จาก subTable ที่อ้าง index) ----
    idx_spk = index_speakers(data)
    idx_txt = texts_by_index(data)
    exact = {}
    for key, txts in idx_txt.items():
        skey = idx_spk.get(key)
        if not skey:
            continue
        tok = speaker_token(skey)
        for t in txts:
            exact.setdefault(t, set()).add(tok or skey)

    named = OrderedDict()
    for text, keys in lines.items():
        toks = [t for t in (speaker_token(k) for k in keys) if t]
        chaps = sorted({m.group(1) for k in keys
                        for m in [re.search(r"(?:judge|coyote)_(?:dlc_)?main_c(\d+)", k)] if m})
        ex = sorted(exact.get(text, []))
        if toks or chaps or ex:
            ent = {"keys": keys}
            if ex:
                ent["speaker_exact"] = ex      # ผู้พูดรายบรรทัดจากไฟล์เกม (แม่นที่สุด)
            if toks:
                ent["speaker"] = sorted(set(toks))
            if chaps:
                ent["chapter"] = chaps          # บทที่บรรทัดนี้อยู่ (จากชื่อ list ของเสียงพากย์)
            named[text] = ent

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT_JSON, "w", encoding="utf-8", newline="\n").write(
        json.dumps(named, ensure_ascii=False, indent=1) + "\n")

    exact_n = sum(1 for v in named.values() if v.get("speaker_exact"))
    tok_counts = Counter()
    for v in named.values():
        for t in v.get("speaker_exact", []):
            tok_counts["[exact] " + str(t)] += 1
    for v in named.values():
        for t in v.get("speaker", []):
            tok_counts[t] += 1
        for c in v.get("chapter", []):
            tok_counts["บทที่ " + str(int(c))] += 1

    L = ["# แผนที่ผู้พูด (speaker map) — จาก `sound_auth.bin`", "",
         "> สร้างด้วย `python scripts/make_speaker_map.py` · ข้อมูลดิบ: `extracted/facts/speech_speaker_map.json`",
         "",
         "ใช้ตอนแปล/ตรวจ: บรรทัดไหนไม่รู้ว่าใครพูด ให้ค้นข้อความ EN ในไฟล์ JSON ข้างบน — ถ้าเจอ จะได้",
         "ชื่อผู้พูดจากไฟล์เกมจริง (คีย์ของบทพูดมีชื่อตัวละครติดมา เช่น `speech_btl11_010_hamura`)",
         "",
         "| ตัวชี้วัด | ค่า |", "|---|---|",
         "| บทพูดที่มีคีย์กำกับ | %s |" % format(len(lines), ","),
         "| บทพูดที่ผูก **บท (chapter)** หรือผู้พูดได้ | %s |" % format(len(named), ","),
         "| บทพูดที่รู้ **ตัวผู้พูดรายบรรทัด** (`speaker_exact`) | %s |" % format(exact_n, ","),
         "| ชื่อผู้พูดที่พบ | %d |" % len(tok_counts), "",
         "## ผู้พูดที่พบบ่อยที่สุด", "",
         "| ผู้พูด (จากคีย์) | จำนวนบรรทัด |", "|---|---|"]
    for t, n in tok_counts.most_common(40):
        L.append("| `%s` | %d |" % (t, n))
    L += ["", "## ข้อจำกัด", "",
          "- ครอบคลุมเฉพาะบทที่มีเสียงพากย์ (`sound_auth.bin`) — บทใน `auth.bin`/`talk.bin` ที่ไม่มีเสียง",
          "  ยังต้องอนุมานผู้พูดจากบริบทเหมือนเดิม",
          "- คีย์ที่ขึ้นต้น `speech_list_*` เป็นกลุ่มรวม (เช่น เสียงชาวเมืองทั่วไป) ไม่ระบุตัวคน",
          "- ชื่อในคีย์เป็นโค้ดเนมของทีมพัฒนา (เช่น `knt_m_chinpira_tough` = นักเลงคามุโรโจ)",
          "- **กับดักที่ 2**: บรรทัดสั้น ๆ ทั่วไป (\"The ADDC, huh?\" / \"...yeah?\") ถูกใช้ซ้ำหลายฉากในเกม แต่ map เก็บผู้พูดไว้แค่ครั้งเดียว → ถ้า `speaker_exact` ขัดกับตัวละครที่อยู่ในฉากจริง **ให้เชื่อฉาก** (ผู้ตรวจ batch_040 ยืนยัน)",
          "- **กับดักสำคัญ**: เลข speaker-slot id (field `\"1\"`) ใน `sound_auth.bin` เป็นเลข **ต่อตาราง** ไม่ใช่ id ตัวละครทั้งเกม — ห้ามเอาไปเทียบกับ `speakers.json` (จะได้ชื่อมั่ว) ใช้ได้เฉพาะไล่ผู้พูดภายในตารางเดียวกัน",
          "- ฉากออฟฟิศกฎหมายบทที่ 4 (\"Are you butting heads with Hamura?\") ผู้พูดคือ **เก็นดะ** ไม่ใช่มัตสึกาเนะ (ยืนยันโดยผู้ตรวจ batch_035 — มัตสึกาเนะไม่อยู่ในฉากนั้น)",
          "  ไม่ใช่ชื่อที่แสดงบนจอ — เทียบกับ `translations/characters_main.json` ก่อนใช้"]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT_MD, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")

    print("บทพูดที่มีคีย์ %s · ระบุผู้พูดได้ %s · ชื่อผู้พูด %d"
          % (format(len(lines), ","), format(len(named), ","), len(tok_counts)))
    print("เขียน", OUT_JSON)
    print("เขียน", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
