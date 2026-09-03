#!/usr/bin/env python3
"""จัดคิวงานแปลของ Ishin! ออกเป็น batch ให้ทีมแปล — พอร์ตจาก Lost Judgment มาต่อกับสามแหล่งของภาคนี้

ต่างจากภาค Dragon Engine ตรงที่ "หน่วยต้นทาง" ไม่ใช่ `.bin` ไฟล์เดียว แต่มีสามชั้น:
  1. `Game.locres` — UI ที่ UE จัดการ **และบทคัตซีนหลักทั้งหมด**
     namespace ที่มีคู่ `<ns>_speaker` = บทคัตซีน (รู้ผู้พูดรายบรรทัด)
  2. ARMP `db.macan/en/*.bin` — เมนู ไอเทม ทักษะ ทิปส์ มินิเกม บทพูด NPC
  3. `.msg` — บทสนทนาเดินเมือง/ADV (ก้อนใหญ่ที่สุด · แยกเป็นซีรีส์ batch ของตัวเอง)

ทุก batch แนบสองอย่างที่ภาคก่อน ๆ ไม่มี:
  - `ref_ja` = **ต้นฉบับญี่ปุ่นของบรรทัดนั้น** (จาก pak เดียวกัน) ใช้ตัดสินเพศ/ระดับภาษา/คำนำหน้าชื่อ
  - `ref_tm` = คำแปลจากภาคพี่น้อง เป็นร่างให้พิจารณา **ไม่ใช่คำตอบ** และ
    **ห้ามใช้กับชื่อตัวละคร** (Ishin เป็นบาคุมัตสึ คนละตัวละครกับซีรีส์หลัก)

รันซ้ำได้: ก่อน re-chunk จะเก็บเกี่ยวคำแปลที่กรอกค้างใน batch เดิมเข้า master_th ก่อน แล้วจัดใหม่
(เลขbatch เลื่อนได้ — อย่าอ้างเลข batch ข้าม sprint)

ใช้: python scripts/make_worklist_ishin.py [--batch-size 250]
ต้องมีมาก่อน: scripts/build_parallel.py
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")   # console Windows = cp1252 (กติกาข้อ 5)
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                            # noqa: E402

PARALLEL = paths.EXTRACTED / "parallel"
REPORT_MD = paths.TRANSLATIONS / "worklist_report.md"
DEFAULT_BATCH = 250

# ---- คำแปลอ้างอิงจากภาคพี่น้อง (อ่านอย่างเดียว · ตัวแรกที่มีคีย์ชนะ) ----
# ลำดับตาม CLAUDE.md: LJ > Judgment > K3 > Gaiden > Y8 > Y7 > Pirate > K2R
TM_SOURCES = [
    ("lost-judgment-thai", "LJ"), ("judgment-thai", "Judgment"),
    ("yakuza-kiwami-3", "K3"), ("yakuza-gaiden", "Gaiden"),
    ("y8-infinite-wealth", "Y8"), ("yakuza-7-like-a-dragon-thai", "Y7"),
    ("pirate-yakuza-hawaii-thai", "Pirate"), ("yakuza-kiwami-2-mod", "K2R"),
]

# ---- เกณฑ์คัดออก (ต้องอธิบายได้ทุกข้อ · ชุดเดียวกับ scope_report.py) ----
SKIP_TABLES = re.compile(r"^staffroll_", re.I)          # เครดิตท้ายเกม คง EN (กติกาข้อ 9)
SKIP_NS = re.compile(r"^(staffroll|credit|license|kiyaku)", re.I)
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
TOKEN_ONLY = re.compile(r"^(\s|<[^>]*>|\{[^}]*\}|\$\w+)*$")
IDENT_ONLY = re.compile(r"^[A-Z0-9_\-./]+$")

# ตาราง ARMP ที่ค่าข้างในเป็น identifier ของเอนจิ้น ไม่ใช่ข้อความบนจอ — แปลแล้วเกมพัง
# (ยืนยันด้วยการเปิดไฟล์ดูค่าจริงทุกตาราง 1 ก.ย. 2026 · ห้ามเติมจากการเดาชื่อไฟล์ — กติกาข้อ 10)
DENY_TABLES = {
    "battle_ctrltype",              # model_name / reactor_id = ชื่อโมเดลกับรหัสรีแอคเตอร์
    "chara_common_draw_list", "chara_common_draw_list_human",
    "chara_common_human_draw_list", "chara_common_list_human",
    "motion_gmt", "motion_pack",    # ชื่อไฟล์โมชัน
    "item_file_name", "item_file_path",
    "sound_cuesheet", "sound_macan_cuesheet",   # ชื่อ cuesheet ของระบบเสียง
    "ui_texture_input_device_remapper", "ui_texture_ngen_remapper",
    "ui_texture_platform_remapper", "tips_platform_texture",
    "input_key_texture_map",
    "db_example_array_of_table", "db_sample_parameter", "db_sample_parameter_csv",
    "taishi_card_weapon",           # TEX_NAME = ชื่อเท็กซ์เจอร์
    "photo_stamp", "photo_stamp_color",         # ชื่อไฟล์สแตมป์
    "wdr_init_anim", "hact_list",
}

# ตารางที่ "คงภาษาอังกฤษ" ตามกติกาเหล็กข้อ 9
KEEP_EN_TABLES = {
    "staffroll_staffroll_pc", "staffroll_staffroll_pc_en",
    "staffroll_staffroll_ps", "staffroll_staffroll_ps_en",
    "staffroll_staffroll_xb", "staffroll_staffroll_xb_en",
    "dlc_package", "dlc_item_pack",             # ชื่อสินค้าบนร้านค้าแพลตฟอร์ม
    "ps5_activity",
}

TIER_NAMES = {
    1: "บทคัตซีนเนื้อเรื่อง (locres มีคู่ _speaker)",
    2: "เรื่องย่อ/คำอธิบายเนื้อเรื่องและตัวละคร",
    3: "เมนู/ระบบ/ไอเทม/ทักษะ/ร้านค้า",
    4: "บทพูด NPC เดินถนน (ARMP sound_speak_data)",
    5: "มินิเกม/การ์ดไทชิ/โหมดถ่ายรูป",
    6: "ที่เหลือ",
    9: "บทสนทนา .msg (แยกเป็นซีรีส์ MSG)",
}

UI_TABLE_RE = re.compile(
    r"^(option|tips|tutorial|btl_tutorial|string_tbl_|pause_|ui_texture_text|ultimate_|"
    r"localization_category|play_go_message|game_difficult|dictionary_|book_|mark|item_|"
    r"blacksmith_|skill_|battle_|font_|correlation_diagram|stay_enemy_name_all)")
MINIGAME_TABLE_RE = re.compile(r"^(taishi_|minigame_|photo_)")

# locres แยก tier ตาม namespace — ดูรูปแบบชื่อจริงทั้ง 271 แบบก่อนตั้ง (1 ก.ย. 2026)
LOCRES_STORY_RE = re.compile(
    r"^(explanation_|correlation_|caption_name|activity_list_|chapter|mission_|substory)")
LOCRES_MINIGAME_RE = re.compile(
    r"^(minigame_|card_list|taishi|surfboard|soldier_training|leader_skill|normal_skill|"
    r"cooking|fishing|karuta|gambling)")


def locres_tier(ns, has_speaker):
    if has_speaker:
        return 1
    if LOCRES_STORY_RE.match(ns):
        return 2
    if LOCRES_MINIGAME_RE.match(ns):
        return 5
    return 3


def translatable(s):
    """สตริงนี้ต้องส่งให้นักแปลไหม (เกณฑ์เดียวกับ scope_report.py)"""
    if not s or not s.strip():
        return False
    if CONTROL.search(s):
        return False
    if TOKEN_ONLY.match(s):
        return False
    if IDENT_ONLY.match(s.strip()):
        return False
    return bool(re.search(r"[A-Za-z぀-ヿ一-鿿]{2,}", s))


def armp_tier(table):
    if table in ("sound_speak_data", "sound_macan_cue_subtitle"):
        return 4
    if MINIGAME_TABLE_RE.match(table):
        return 5
    if UI_TABLE_RE.match(table):
        return 3
    return 6


def load_tm():
    tm, order = {}, []
    for folder, label in TM_SOURCES:
        p = Path(paths.SIBLING_ROOT) / folder / "translations" / "master_th.json"
        if not p.exists():
            print("!! TM ไม่พบ: %s (%s)" % (label, p))
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        added = 0
        for en, th in d.items():
            if en not in tm and isinstance(th, str) and th.strip():
                tm[en] = th
                added += 1
        order.append("%s +%d" % (label, added))
    print("TM อ้างอิง: %s (รวม %d คู่)" % (" · ".join(order), len(tm)))
    return tm


def collect():
    """รวมสตริงอังกฤษไม่ซ้ำจากทั้งสามชั้น พร้อม tier · ต้นทาง · คู่ญี่ปุ่น"""
    uniq = {}
    ja_votes = defaultdict(Counter)
    stats = Counter()

    def add(en, ja, tier, source):
        stats["raw"] += 1
        if not translatable(en):
            stats["skip_not_text"] += 1
            return
        e = uniq.setdefault(en, {"count": 0, "tier": tier, "sources": set()})
        e["count"] += 1
        e["tier"] = min(e["tier"], tier)
        if len(e["sources"]) < 8:
            e["sources"].add(source)
        if ja and ja.strip():
            ja_votes[en][ja] += 1

    # --- locres ---
    loc = json.loads((PARALLEL / "locres.json").read_text(encoding="utf-8"))
    speaker_ns = {r["ns"][:-len("_speaker")] for r in loc if r["ns"].endswith("_speaker")}
    for r in loc:
        ns = r["ns"]
        if SKIP_NS.match(ns):
            stats["skip_ns"] += 1
            continue
        if ns.endswith("_speaker"):
            # ชื่อผู้พูดเป็นชื่อเฉพาะ — จัดคิวแยกผ่าน name_proposals ไม่ปนกับบทพูด
            stats["speaker_names"] += 1
            continue
        add(r["en"], r["ja"], locres_tier(ns, ns in speaker_ns), "locres:" + ns)

    # --- ARMP ---
    db = json.loads((PARALLEL / "db.json").read_text(encoding="utf-8"))
    for r in db:
        t = r["table"]
        if SKIP_TABLES.match(t) or t in KEEP_EN_TABLES:
            stats["skip_keep_en"] += 1
            continue
        if t in DENY_TABLES:
            stats["skip_deny_table"] += 1
            continue
        add(r["en"], r["ja"], armp_tier(t), "armp:%s.%s" % (t, r["col"]))

    # --- .msg ---
    msg = json.loads((PARALLEL / "msg.json").read_text(encoding="utf-8"))
    for r in msg:
        add(r["en"], r["ja"], 9, "msg:" + r["file"])

    ja_of = {en: c.most_common(1)[0][0] for en, c in ja_votes.items()}
    return uniq, ja_of, stats


def dump(obj, p):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def harvest_old(master):
    """เก็บคำแปลที่กรอกค้างใน batch เดิมเข้า master_th ก่อนลบทิ้ง (idempotent)"""
    paths.WORKLIST.mkdir(parents=True, exist_ok=True)
    old = sorted(b for b in paths.WORKLIST.glob("batch_*.json")
                 if not b.name.endswith(".context.json"))
    got = 0
    for bf in old:
        try:
            data = json.loads(bf.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            print("!! ข้าม batch เสีย: %s" % bf.name)
            continue
        for en, th in (data.get("strings") or {}).items():
            if isinstance(th, str) and th.strip() and not master.get(en):
                master[en] = th
                got += 1
    for bf in old:
        bf.unlink()
    for cf in paths.WORKLIST.glob("batch_*.context.json"):
        cf.unlink()      # บริบทเก่าอ้าง batch ที่หายไปแล้ว — สร้างใหม่ด้วย make_batch_context_ishin.py
    return got, len(old)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=DEFAULT_BATCH)
    a = ap.parse_args()

    uniq, ja_of, stats = collect()
    tm = load_tm()
    master = json.loads(paths.MASTER_TH.read_text(encoding="utf-8")) \
        if paths.MASTER_TH.exists() else {}
    harvested, n_old = harvest_old(master)

    remaining = [(v["tier"], i, en) for i, (en, v) in enumerate(uniq.items())
                 if not master.get(en)]
    remaining.sort()
    main_items = [r for r in remaining if r[0] != 9]
    msg_items = [r for r in remaining if r[0] == 9]

    ref_tm_hits = ref_ja_hits = 0

    def write_series(items, fmt):
        nonlocal ref_tm_hits, ref_ja_hits
        seq, n = 1, 0
        groups, cur_tier, cur = [], None, []
        for it in items:                       # ไม่ให้ batch คร่อม tier
            if it[0] != cur_tier and cur:
                groups.append((cur_tier, cur))
                cur = []
            cur_tier = it[0]
            cur.append(it)
        if cur:
            groups.append((cur_tier, cur))
        for tier, group in groups:
            for i in range(0, len(group), a.batch_size):
                chunk = group[i:i + a.batch_size]
                ens = [en for _, _, en in chunk]
                ref_tm = {en: tm[en] for en in ens if tm.get(en)}
                ref_ja = {en: ja_of[en] for en in ens if ja_of.get(en)}
                ref_tm_hits += len(ref_tm)
                ref_ja_hits += len(ref_ja)
                dump({
                    "priority": tier,
                    "priority_name": TIER_NAMES[tier],
                    "sources": sorted({s for en in ens for s in uniq[en]["sources"]})[:40],
                    "strings": {en: "" for en in ens},
                    "ref_ja": ref_ja,
                    "ref_tm": ref_tm,
                }, paths.WORKLIST / (fmt % seq))
                seq += 1
                n += 1
        return n

    n_main = write_series(main_items, "batch_%03d.json")
    n_msg = write_series(msg_items, "batch_MSG_%03d.json")
    dump(master, paths.MASTER_TH)

    # ---- รายงาน ----
    tier_counts = Counter(t for t, _, _ in remaining)
    L = []
    A = L.append
    A("# Worklist Report — Like a Dragon: Ishin! (ISHTH)")
    A("")
    A("สร้างโดย `scripts/make_worklist_ishin.py` — รันซ้ำได้ (เก็บเกี่ยวคำแปลค้างก่อน re-chunk)")
    A("")
    A("- สตริงอังกฤษไม่ซ้ำที่ต้องแปล: **%s**" % f"{len(uniq):,}")
    A("- อยู่ใน `master_th.json` แล้ว: %s (เก็บเกี่ยวจาก batch เดิมรอบนี้ %s จาก %d ไฟล์)"
      % (f"{len(uniq) - len(remaining):,}", f"{harvested:,}", n_old))
    A("- เหลือจัดคิว: **%s** (สาย locres+ARMP %s · สาย .msg %s)"
      % (f"{len(remaining):,}", f"{len(main_items):,}", f"{len(msg_items):,}"))
    A("- batch: **%d** `batch_NNN.json` + **%d** `batch_MSG_NNN.json` (≤%d สตริง/batch)"
      % (n_main, n_msg, a.batch_size))
    A("- มีต้นฉบับญี่ปุ่นแนบ (`ref_ja`): **%s** สตริง — ใช้ตัดสินเพศ/ระดับภาษา/คำนำหน้าชื่อ"
      % f"{ref_ja_hits:,}")
    A("- มีร่างอ้างอิงจากภาคก่อน (`ref_tm`): %s สตริง — **ไม่ใช่คำตอบ**"
      % f"{ref_tm_hits:,}")
    A("")
    A("| priority | ความหมาย | สตริง |")
    A("|---:|---|---:|")
    for t in sorted(tier_counts):
        A("| %d | %s | %s |" % (t, TIER_NAMES[t], f"{tier_counts[t]:,}"))
    A("")
    A("## สตริงที่ไม่ส่งเข้าคิว")
    A("")
    A("| เหตุผล | จำนวน |")
    A("|---|---:|")
    A("| ไม่ใช่ข้อความ (โทเคน/ID/ตัวเลข/control byte) | %s |" % f"{stats['skip_not_text']:,}")
    A("| namespace เครดิต/ลิขสิทธิ์ (คง EN) | %s |" % f"{stats['skip_ns']:,}")
    A("| ตาราง ARMP ที่คง EN (เครดิต/DLC/ร้านค้า) | %s |" % f"{stats['skip_keep_en']:,}")
    A("| ตาราง ARMP ที่เป็น identifier ของเอนจิ้น | %s |" % f"{stats['skip_deny_table']:,}")
    A("| ชื่อผู้พูด (`*_speaker`) — จัดคิวแยกที่ name_proposals | %s |"
      % f"{stats['speaker_names']:,}")
    A("")
    A("## ลำดับการทำงานที่แนะนำ")
    A("")
    A("1. `batch_001+` priority 1 — บทคัตซีนเนื้อเรื่อง (มีชื่อผู้พูดครบ 99%)")
    A("2. priority 2-3 — UI/เมนู/ไอเทม (ทำให้เกมเล่นเป็นไทยได้ก่อน)")
    A("3. priority 4-6 — NPC/มินิเกม/ที่เหลือ")
    A("4. `batch_MSG_001+` — บทสนทนาเดินเมือง (ก้อนใหญ่สุด · ต้องเปิด `.context.json` คู่เสมอ)")
    REPORT_MD.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")

    print("\nไม่ซ้ำ %s · เหลือแปล %s (main %s / msg %s) · batch %d + %d"
          % (f"{len(uniq):,}", f"{len(remaining):,}", f"{len(main_items):,}",
             f"{len(msg_items):,}", n_main, n_msg))
    print("ref_ja %s · ref_tm %s" % (f"{ref_ja_hits:,}", f"{ref_tm_hits:,}"))
    print("-> %s" % paths.WORKLIST)
    print("-> %s" % REPORT_MD)


if __name__ == "__main__":
    main()
