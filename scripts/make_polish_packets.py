#!/usr/bin/env python3
"""ซองคลื่น "เกลาบทพูดทั้งเกม" (sprint 22 · 13 ก.ย. 2026)

สองแหล่ง:
  --source msg    บทพูดในไฟล์ .msg (คัตซีน · เควสต์ · สายสัมพันธ์) อ่านเรียงเป็นฉาก -> ซอง 01-50
  --source extra  บทพูดที่อยู่นอก .msg -> ซอง 51 ขึ้นไป
                  ARMP `sound_speak_data` (บอลลูน NPC 3,553 สตริง) · `sound_macan_cue_subtitle`
                  locres `walk_*` (คนเดินถนน) · `s_c*` (ซับไตเติลฉาก) · `minigame_mahjong` · `minigame_toba` · `shop*`
                  pac_STID บทพูดลอยของ NPC (§0.60)
                  ไม่มีไฟล์ฉาก จึงจัด "ฉาก" ตามกลุ่มของแหล่ง (ตาราง/namespace/ผู้พูด) เรียงตามคีย์

ต่างจาก `make_revise_packets.py` (คลื่นคำลงท้าย §0.59) สามข้อ:
  1. ซองครอบ **ทุกฉากที่มีคำแปล** — งาน D (เกลาสำนวน) ต้องอ่านทุกบรรทัด งาน A/B/C อาศัยการอ่านรอบเดียวกัน
  2. เพศผู้พูดอ่าน **ตารางรายบรรทัด** `gender_dialogue_keys.json` (คลื่นเพศสอง §0.60) ด้วย
  3. ตัดข้อมูลตายของภาคปัจจุบัน (`DEAD_FILES`) ออก — คลื่นก่อนเสียแรงไปสองซองเต็ม

เครื่องหมายเพิ่มในซอง:
  `shared`  สตริงอังกฤษเดียวกันโผล่กี่ไฟล์ฉาก — `master_th.json` ผูกคำแปลกับสตริงอังกฤษ แก้ที่เดียวโดนทุกที่
  `flag`    คำแปลเดิมมีคำลงท้ายที่ขัดกับเพศในตาราง (วัดได้ 31 บรรทัด 13 ก.ย. 2026 ส่วนใหญ่ตารางผิด —
            อิกุมัตสึ · ฉากโฮสเตส uid016c008c) ให้ผู้ตรวจชี้ว่าฝั่งไหนผิด

ใช้:
  python scripts/make_polish_packets.py                      # บทพูด .msg
  python scripts/make_polish_packets.py --source extra       # บทพูดนอก .msg
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict, OrderedDict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                              # noqa: E402
import merge_qc as M                      # noqa: E402
import thai_pronouns as tp                # noqa: E402
import make_revise_packets as R           # noqa: E402
from make_gender_packets import DEAD_FILES  # noqa: E402

WAVE = paths.PROJECT / "work" / "revise_wave" / "polish"
KEYS = json.loads((paths.TRANSLATIONS / "gender_dialogue_keys.json").read_text(encoding="utf-8"))
# คิวเสียงรายบรรทัด (build_voice_gender.py · 15 ก.ย. 2026) — ขัดกับเครื่องหมายในบรรทัดเอง 0/475
_VOICE_PATH = paths.TRANSLATIONS / "gender_voice_keys.json"
VOICE = json.loads(_VOICE_PATH.read_text(encoding="utf-8")) if _VOICE_PATH.exists() else {}
EXTRA_START = 51                          # เลขซองแรกของแหล่ง extra — ซอง msg ต้องไม่เกิน 50
EXTRA_TABLES = ("sound_speak_data", "sound_macan_cue_subtitle")
EXTRA_NS = re.compile(r"^(walk_|s_c\d|minigame_mahjong$|minigame_toba$|shop)")
SCENE_ROWS = 60                           # แหล่ง extra ไม่มีไฟล์ฉาก หั่นกลุ่มยาวเป็นท่อนละเท่านี้


def gender_of(key, en, ja):
    """ลำดับชั้นเดียวกับด่าน G ของ merge_qc บวกชั้นรายบรรทัดต่อจากเครื่องหมายในบรรทัดเอง
    (วัด 13 ก.ย. 2026: ชั้นรายบรรทัดขัดกับ gender_lines 0 · ขัดกับทั้งสายเดิม 0)"""
    g = M.line_gender(en)
    if g:
        return g, "line"
    g = (VOICE.get(key) or {}).get("gender")
    if g in ("male", "female"):
        return g, "voice"
    g = M.ja_gender(ja)
    if g:
        return g, "ja"
    g = (KEYS.get(key) or {}).get("gender")
    if g in ("male", "female"):
        return g, "key"
    g = M.dialogue_gender(en)
    if g:
        return g, "dialogue"
    g = M.scene_gender(en)
    if g:
        return g, "scene"
    return None, None


def ending_conflict(th, g):
    if g == "female" and tp.RE_KHORAP.search(th):
        return True
    return g == "male" and bool(tp.RE_CHAOKHA.search(th) or tp.FEM_CASUAL.search(th))


def usable(en, mt):
    th = mt.get(en)
    return bool(en.strip()) and bool(th) and th != en   # คงต้นฉบับ = ไม่มีอะไรให้เกลา


def load_msg(mt):
    par = json.loads((paths.PROJECT / "extracted" / "parallel" / "msg.json").read_text(encoding="utf-8"))
    byfile = defaultdict(list)
    for r in par:
        if r["file"] not in DEAD_FILES and usable(r.get("en") or "", mt):
            byfile[r["file"]].append(r)
    return [(f, byfile[f]) for f in sorted(byfile)]


def ui_word(en):
    """ปุ่ม/ป้ายเมนูในกลุ่มมินิเกม (`Yes` · `Other` · `Nevermind`) ไม่ใช่บทพูด"""
    return len(en.split()) <= 2 and not re.search(r"[.!?…]", en)


def load_extra(mt):
    groups = defaultdict(list)
    db = json.loads((paths.PROJECT / "extracted" / "parallel" / "db.json").read_text(encoding="utf-8"))
    speaker = {}
    for r in db:
        if r["table"] in EXTRA_TABLES and r["col"] == "speaker":
            speaker[(r["table"], r["key"].split("#")[1])] = r["en"]
    for r in db:
        if r["table"] not in EXTRA_TABLES or r["col"] != "message" or not usable(r.get("en") or "", mt):
            continue
        row = r["key"].split("#")[1]
        item = dict(r, labels=[speaker[(r["table"], row)]] if speaker.get((r["table"], row)) else [])
        groups[r["table"]].append((int(row), item))
    loc = json.loads((paths.PROJECT / "extracted" / "parallel" / "locres.json").read_text(encoding="utf-8"))
    for r in loc:
        en = r.get("en") or ""
        if not EXTRA_NS.match(r["ns"]) or not usable(en, mt):
            continue
        if r["ns"].startswith("minigame_toba") and ui_word(en):
            continue
        path = r["key"].split("::", 1)[-1].split("/")
        g = "/".join(path[:2]) if len(path) > 2 else path[0]
        groups["locres:" + g].append((r["key"], dict(r, labels=[])))
    pac = json.loads((paths.PROJECT / "extracted" / "pac_en.json").read_text(encoding="utf-8"))
    for r in pac:
        if r.get("kind") == "line" and r.get("translatable") and usable(r.get("en") or "", mt):
            groups[r["file"]].append(((r["record"], r["index"]), dict(r, labels=[])))
    out = []
    for g in sorted(groups):
        rows = [x for _, x in sorted(groups[g], key=lambda t: t[0])]
        for i in range(0, len(rows), SCENE_ROWS):
            out.append(("%s@%d" % (g, i // SCENE_ROWS), rows[i:i + SCENE_ROWS]))
    return out


def build(scenes_src, mt, with_gender):
    files_of = defaultdict(set)
    g_by_en, kind_by_en = defaultdict(set), defaultdict(set)
    for f, rows in scenes_src:
        for r in rows:
            en, ja = r["en"], r.get("ja") or ""
            files_of[en].add(f)
            if with_gender:
                g, _ = gender_of(r["key"], en, ja)
                g_by_en[en].add(g)
                kind_by_en[en].add(R.decide_kind(en, ja, mt[en], g))
    # เหมือน make_revise_packets.safe_keys แต่เพศมาจากชั้นรายบรรทัด
    safe = {en for en, kinds in kind_by_en.items()
            if kinds - {None} and None not in kinds and len(g_by_en[en] - {None}) == 1}

    scenes, tally = [], Counter()
    for f, rows in scenes_src:
        out, seen = [], set()
        for r in rows:
            en = r["en"]
            th = mt[en]
            if (en, th) in seen:
                continue
            seen.add((en, th))
            ja = r.get("ja") or ""
            item = OrderedDict(key=r["key"], en=en, ja=ja, th=th)
            if r.get("labels"):
                item["labels"] = r["labels"]
            g = None
            if with_gender:
                g, layer = gender_of(r["key"], en, ja)
                if g:
                    item["gender"], item["gender_from"] = g, layer
            if len(files_of[en]) > 1:
                item["shared"] = len(files_of[en])
                tally["shared"] += 1
            kind = R.decide_kind(en, ja, th, g) if en in safe else None
            if kind:
                item["decide"] = kind
                tally["decide"] += 1
            if g and ending_conflict(th, g):
                item["flag"] = "ending_gender_conflict"
                tally["flag"] += 1
            out.append(item)
        if out:
            scenes.append({"file": f, "lines": out})
    return scenes, tally


def pack(scenes, per):
    MAXS, MAXB = 550, 220 * 1024
    split = []
    for s in scenes:
        for i in range(0, len(s["lines"]), MAXS):
            split.append({"file": s["file"], "lines": s["lines"][i:i + MAXS]})
    packets, cur, n, b = [], [], 0, 0
    for s in split:
        sb = len(json.dumps(s, ensure_ascii=False).encode("utf-8"))
        if cur and (n + len(s["lines"]) > per * 1.35 or b + sb > MAXB):
            packets.append(cur)
            cur, n, b = [], 0, 0
        cur.append(s)
        n += len(s["lines"])
        b += sb
        if n >= per or b >= MAXB:
            packets.append(cur)
            cur, n, b = [], 0, 0
    if cur:
        packets.append(cur)
    return packets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=("msg", "extra"), default="msg")
    ap.add_argument("--lines", type=int, default=450)
    args = ap.parse_args()

    mt = json.loads((paths.TRANSLATIONS / "master_th.json").read_text(encoding="utf-8"))
    if args.source == "msg":
        scenes, tally = build(load_msg(mt), mt, with_gender=True)
        start = 1
    else:
        scenes, tally = build(load_extra(mt), mt, with_gender=False)
        start = EXTRA_START
    packets = pack(scenes, args.lines)
    if args.source == "msg" and len(packets) >= EXTRA_START:
        raise SystemExit("ซอง msg %d ซอง ชนช่วงเลขของ extra (%d) — เพิ่ม --lines" % (len(packets), EXTRA_START))

    in_dir = WAVE / "in"
    in_dir.mkdir(parents=True, exist_ok=True)
    for old in list(in_dir.glob("packet_*.json")) + list(in_dir.glob("packet_*.txt")):
        num = int(re.search(r"\d+", old.stem).group())
        if (num >= EXTRA_START) == (args.source == "extra"):
            old.unlink()
    for i, group in enumerate(packets, start):
        nl = sum(len(s["lines"]) for s in group)
        tally["lines"] += nl
        data = {"packet": "polish_%02d" % i, "scenes": group}
        (in_dir / ("packet_%02d.json" % i)).write_text(
            json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        (in_dir / ("packet_%02d.txt" % i)).write_text(render_txt(data), encoding="utf-8")
        nd = sum(1 for s in group for l in s["lines"] if l.get("decide"))
        print("packet_%02d  ฉาก %3d · บรรทัด %4d · ต้องตัดสินคำลงท้าย %3d · %s"
              % (i, len(group), nl, nd, group[0]["file"]))
    print("รวม %d ซอง · บรรทัด %d · ต้องตัดสินคำลงท้าย %d · สตริงใช้ร่วมหลายฉาก %d · คำลงท้ายขัดเพศ %d"
          % (len(packets), tally["lines"], tally["decide"], tally["shared"], tally["flag"]))


def render_txt(data):
    def esc(s):
        return (s or "").replace(chr(13) + chr(10), "\\n").replace(chr(10), "\\n")

    out = ["ซอง %s — อ่านทุกบรรทัด เรียงตามลำดับ" % data["packet"], ""]
    for sc in data["scenes"]:
        out.append("=" * 70)
        out.append("### ไฟล์ฉาก %s (%d บรรทัด)" % (sc["file"], len(sc["lines"])))
        for l in sc["lines"]:
            head = "[%s]" % l["key"]
            if l.get("gender"):
                head += "  เพศ=%s(%s)" % (l["gender"], l.get("gender_from"))
            if l.get("shared"):
                head += "  ใช้ร่วม=%d ฉาก" % l["shared"]
            if l.get("decide"):
                head += "  *** ต้องตัดสิน: %s ***" % l["decide"]
            if l.get("flag"):
                head += "  !!! คำลงท้ายขัดกับเพศ !!!"
            if l.get("labels"):
                head += "  ป้าย=%s" % " | ".join(l["labels"])
            out.append(head)
            out.append("  EN: " + esc(l["en"]))
            out.append("  JA: " + esc(l.get("ja")))
            out.append("  TH: " + esc(l["th"]))
        out.append("")
    return chr(10).join(out)


if __name__ == "__main__":
    main()
