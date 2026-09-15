#!/usr/bin/env python3
"""ถอดสตริงแสดงผลจาก pac_STID_*.bin (wdr_en) -> extracted/text_en/pac.json

แต่ละแถว: key · file · record · kind (line = บรรทัดของ entry · label = ตาราง label)
· index · en · ja (คีย์เดียวกันในไฟล์ wdr_ja · null ถ้าไม่มีคีย์นั้น) · ncmds · translatable · why

การแยก "ข้อความบนจอ" กับ "ไอดี" ใช้หลักฐานจากไฟล์ ไม่ใช่เดาจากหน้าตา:
  สตริงที่เป็นไอดี (`Talk_Kamae` · `M_BUS_TLK_...` · `7e008100` · คิวเสียง) เหมือนกันทุกภาษา
  สตริงแสดงผลถูกแปลอย่างน้อยหนึ่งภาษา → translatable = ต่างจาก EN ในภาษาใดภาษาหนึ่งจาก 8 ภาษา
  ข้อยกเว้นเดียว: บรรทัดญี่ปุ่นที่ตกค้างในไฟล์ EN (`く 苦しぃ～`) มีคานะ/คันจิ → นับว่าต้องแปล
แถวที่หน้าตาขัดกับหลักฐาน (ดูเหมือนประโยคแต่เหมือนทุกภาษา / ดูเหมือนไอดีแต่ถูกแปล) พิมพ์ออกมาให้คนดู

สตริงว่างไม่ถูกเขียนลงไฟล์ (นับไว้ในผลสรุป)
"""
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                              # noqa: E402
from pakfile import PakFile                               # noqa: E402
import pac                                                # noqa: E402

OTHER = ["ja", "de", "fr", "it", "es", "ko", "cn", "tw"]
# ไม่วางใน text_en/ — build_text.build_msg · scope_report · build_parallel อ่านทุก *.json ในนั้นเป็น .msg
OUT = paths.EXTRACTED / "pac_en.json"
CJK_RE = re.compile(r"[぀-ヿ㐀-鿿！-～]")
IDENT_RE = re.compile(r"^[A-Za-z0-9_.,:\-]+$")


def load(pak, lang):
    prefix = paths.PAC_DIR % lang
    return {p[len(prefix):]: pak.read(p) for p in pak.files if p.startswith(prefix + "pac_STID_")}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    pak = PakFile(paths.PAK_MAIN)
    en_raw = load(pak, "en")
    others = {lang: load(pak, lang) for lang in OTHER}

    rows = []
    empty = 0
    not_utf8 = []
    odd_same, odd_diff = [], []
    for name in sorted(en_raw):
        e = pac.PacFile(en_raw[name], name)
        if e.errors:
            raise SystemExit("%s: มีเรคคอร์ดที่อ่านไม่ได้ %s — รัน check_pac_roundtrip.py" % (name, e.errors[:2]))
        alt = {}                                  # ภาษา -> {record id: MsgBlock}
        for lang in OTHER:
            if name in others[lang]:
                alt[lang] = {r.rid: r.msg for r in pac.PacFile(others[lang][name], name).records if r.msg}

        def other_value(lang, s):
            """(ค่าในภาษานั้นที่คีย์เดียวกัน หรือ None, ต่างจาก EN ไหม)

            ⚠ label: บางภาษารวม label ซ้ำ ทำให้จำนวนต่างจาก EN และดัชนีเดียวกันคนละตัว
            ถ้าเทียบตามดัชนีตรง ๆ ไอดีท่าทาง (`M_CHO_TLK_seiza_kamae`) จะดูเหมือน "ถูกแปล"
            → จำนวนไม่เท่า: ถือว่าต่างก็ต่อเมื่อสตริง EN ไม่อยู่ในตาราง label ของภาษานั้นเลย
            """
            m = alt.get(lang, {}).get(s["record"])
            if m is None:
                return None, False
            if s["kind"] == "line":
                v = m.lines[s["index"]]
                return v, v != s["raw"]
            if len(m.labels) == len(e.by_rid[s["record"]].msg.labels):
                v = m.labels[s["index"]]
                return v, v != s["raw"]
            return None, s["raw"] not in m.labels

        for s in e.strings():
            if not s["raw"]:
                empty += 1
                continue
            try:
                s["raw"].decode("utf-8")
                utf8 = True
            except UnicodeDecodeError:
                utf8 = False
                not_utf8.append(s["key"])
            differs = [lang for lang in OTHER if other_value(lang, s)[1]]
            has_cjk = utf8 and bool(CJK_RE.search(s["text"]))
            translatable = bool(differs) or has_cjk
            why = ("ต่างใน " + ",".join(differs)) if differs else ("มีอักษรญี่ปุ่นตกค้าง" if has_cjk
                                                                   else "เหมือนกันทุกภาษา")
            if not utf8:
                why += " · ไม่ใช่ UTF-8"
            ja = other_value("ja", s)[0]
            rows.append({
                "key": s["key"], "file": e.stem, "record": "%08x" % s["record"],
                "kind": s["kind"], "index": s["index"], "en": s["text"],
                "ja": None if ja is None else pac._dec(ja),
                "ncmds": s["ncmds"], "translatable": translatable, "why": why,
            })
            looks_ident = bool(IDENT_RE.match(s["text"]))
            if translatable and looks_ident:
                odd_diff.append(s["text"])
            if not translatable and not looks_ident:
                odd_same.append(s["text"])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)

    tr = [r for r in rows if r["translatable"]]
    ids = [r for r in rows if not r["translatable"]]
    by_kind = collections.Counter((r["kind"], r["translatable"]) for r in rows)
    by_file = collections.Counter(r["file"] for r in tr)
    print("เขียน %s" % OUT)
    print("สตริงไม่ว่าง %d (unique EN %d) · สตริงว่างที่ข้าม %d"
          % (len(rows), len({r["en"] for r in rows}), empty))
    print("  ต้องแปล   %5d  (unique %d)" % (len(tr), len({r["en"] for r in tr})))
    print("  ไอดี/ไม่แปล %5d  (unique %d)" % (len(ids), len({r["en"] for r in ids})))
    for (kind, t), n in sorted(by_kind.items()):
        print("    %-5s %-9s %d" % (kind, "ต้องแปล" if t else "ไอดี", n))
    print("  ประโยค (มีช่องว่าง) ในกลุ่มต้องแปล: %d" % sum(" " in r["en"] for r in tr))
    print("  ไม่มีค่าเทียบใน JA (label รวมซ้ำ): %d" % sum(r["ja"] is None for r in rows))
    print("  ไม่ใช่ UTF-8: %d %s" % (len(not_utf8), not_utf8))
    print("  ไฟล์ที่มีข้อความต้องแปลมากสุด: %s" % ", ".join("%s %d" % kv for kv in by_file.most_common(8)))
    print("  ไฟล์ที่มีข้อความต้องแปล: %d / %d" % (len(by_file), len(en_raw)))
    print("ตรวจด้วยตา — เหมือนทุกภาษาแต่หน้าตาไม่ใช่ไอดี (%d): %s"
          % (len(odd_same), sorted(set(odd_same))[:40]))
    print("ตรวจด้วยตา — ถูกแปลแต่หน้าตาเหมือนไอดี (%d): %s"
          % (len(odd_diff), sorted(set(odd_diff))[:60]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
