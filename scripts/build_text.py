#!/usr/bin/env python3
"""บิลด์ข้อความไทยทั้งเกมจาก `translations/master_th.json` แล้วแพ็กเป็น pak ม็อดหนึ่งไฟล์

ภาคนี้มีข้อความอยู่สามชั้น (ยืนยันกับไฟล์เกมจริงแล้ว — `docs/research.md`):

| ชั้น | ต้นฉบับที่แตกไว้ | ตัวประกอบกลับ | ปลายทางในเกม |
|---|---|---|---|
| `.msg` (บทสนทนา) | `extracted/msg_en/*.msg` | `tools/msg.py` `rebuild()` | `…/data/wdr_en/msg/uid00xxxxxx/<uid>.msg` |
| ARMP (`db.macan`) | `extracted/db_en/*.bin.json` | `tools/reARMP_fixed.py` | `…/data/db.macan/en/<table>.bin` |
| `Game.locres` | `extracted/locres/Game.en.json` | `tools/locres.py` `build_full()` | `…/Content/Localization/Game/en/Game.locres` |

คำแปลอ้างอิงด้วย **ข้อความอังกฤษ** เป็นกุญแจ (เหมือนทุกภาคในชุดนี้) — สตริงอังกฤษเดียวกัน
ที่โผล่หลายที่จะถูกแทนที่ทุกที่ที่พบ ยกเว้นตารางที่กติกาสั่งให้คง EN

⚠ locres ใช้ **ตารางสตริงร่วม**: หลายคีย์ชี้ไปที่สตริงเดียวกันได้ การเขียนทับสตริงในตำแหน่งเดิม
จะไปโผล่ที่คีย์อื่นด้วย → สคริปต์นี้ **เพิ่มสตริงไทยเข้าไปท้ายตารางแล้วชี้ `idx` ใหม่** เสมอ
(วิธีเดียวกับที่ `make_title_poc.py` พิสูจน์บนจอจริงแล้ว)

⚠ reARMP ประกอบ `.bin` กลับ **ไม่ได้ไบต์เท่าเดิม** (padding ต่าง) ซึ่งเป็นสภาพเดียวกับตอนที่
Lost Judgment ปล่อยม็อดสำเร็จ ด่านตรวจของชั้นนี้จึงเป็น `check_layout_all.py` ที่เทียบ
**ไบต์ในแถว** กับ vanilla ไม่ใช่เทียบทั้งไฟล์

ใช้:
  python scripts/build_text.py                     # บิลด์ทั้งสามชั้น + แพ็ก pak
  python scripts/build_text.py --layers msg,locres # เฉพาะบางชั้น
  python scripts/build_text.py --dry-run           # นับอย่างเดียว ไม่เขียนไฟล์
  python scripts/build_text.py --no-font           # ไม่ใส่ฟอนต์ไทยลง pak
  python scripts/build_text.py --install           # คัดลอก pak เข้า Content/Paks/~mods/ ของเกม

กติกาที่สคริปต์นี้เคารพ:
  - ไม่แตะไฟล์ใน `extracted/` (ต้นฉบับ) และไม่แตะไฟล์เกม นอกจากตอน `--install` ที่เขียน
    เฉพาะไฟล์ม็อดของเราเองใน `~mods/`
  - ตาราง staffroll/credit/license คง EN ตามกติกาเหล็กข้อ 9
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths
import armp_graft                                        # noqa: E402
import locres                                       # noqa: E402
import msg as msgmod                                # noqa: E402
from pakwrite import write_pak                      # noqa: E402
from make_worklist_ishin import (                   # noqa: E402
    DENY_COLUMNS, DENY_TABLES, KEEP_EN_TABLES, SKIP_TABLES, SKIP_NS,
)

REARMP = paths.TOOLS / "reARMP_fixed.py"
PAK_LIST = paths.EXTRACTED / "pak0_files.txt"

STAGE = paths.BUILD / "text"
STAGE_MSG = STAGE / "msg"
STAGE_DB = STAGE / "db.macan.en"
STAGE_LOCRES = STAGE / "locres"

LOCRES_GAME_PATH = "LikeaDragonIshin/Content/Localization/Game/en/Game.locres"
DB_GAME_DIR = "LikeaDragonIshin/Content/Projects/Devil2/data/db.macan/en/"
FONT_DIR_GAME = "LikeaDragonIshin/Content/Projects/Devil2/UI/Font/FontFace/"

# FontFace ทุกตัวที่ CompositeFont เลือกใช้กับ culture ชุด EFIGS ("en;fr;it;de;es")
# ยืนยันจากการแตก Font_*.uasset ทั้ง 21 ตัวออกมาอ่านจริง (work/font_dump/):
#   Kuro-Medium         <- Font_System · Font_CmnGothic · Font_MgEnkaisho · Font_MgKaishoUB
#                          · Font_MgKaraoke{Enkaisho,Fude,Kanteiryu,Reisho} · Font_MgKsw{Hiryu,Reisho}
#                          · Font_MgLisence · Font_MgNichibuHiryu
#   edosz               <- Font_CmnFude · Font_MgKswKaisho · Font_MgTaishiFude
#                          · Font_MgKaraokeKokinedo · Font_MgPhotoModeStamp
#   FOT-TelopMinProN-D  <- Font_MgTaishiKaisho
# ทั้งสามตัวในเกมต้นฉบับ **ไม่มีกลิฟไทยเลย** (ตรวจตาราง cmap ของ .ufont ทั้ง 33 ไฟล์แล้ว)
# ถ้าไม่ทับให้ครบ จอที่ใช้ฟอนต์พู่กัน/มินโจแสดงข้อความไทยไม่ได้
FONT_GAME_PATHS = [
    FONT_DIR_GAME + "EFIGS/Kuro-Medium.ufont",
    FONT_DIR_GAME + "EFIGS/edosz.ufont",
    FONT_DIR_GAME + "EFIGS/FOT-TelopMinProN-D.ufont",
]

# หมายเหตุที่ยังไม่ได้ทำ: Font_CmnMincho และ Font_MacanNum ไม่มี CompositeSubFont ของ EFIGS เลย
# -> ภาษาอังกฤษ/ไทยบนจอที่ใช้สองตัวนี้ตกไปที่ DefaultTypeface ซึ่งเป็นฟอนต์ญี่ปุ่น
#    (DF-FutoKaiSho-W9 · Myfont_fude-Regular) ซึ่งก็ไม่มีกลิฟไทยเช่นกัน
#    ยังไม่ทับเพราะทับแล้วจะเสียกลิฟคันจิของฟอนต์นั้นไปด้วย — รอยืนยันว่ามีจอไหนใช้จริงก่อน


def load_master():
    """คืน {EN: TH} เฉพาะคู่ที่ "แปลแล้วจริง" (TH ต่างจาก EN และไม่ว่าง)"""
    if not paths.MASTER_TH.exists():
        return {}
    data = json.loads(paths.MASTER_TH.read_text(encoding="utf-8"))
    return {en: th for en, th in data.items()
            if isinstance(th, str) and th.strip() and th != en}


def msg_game_paths():
    """คืน {uid: path ในเกม} — โฟลเดอร์ย่อยของ .msg ไม่เหมือนกันทุกไฟล์ จึงต้องอ่านจากสารบัญ pak"""
    out = {}
    if not PAK_LIST.exists():
        return out
    for line in PAK_LIST.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if "/wdr_en/msg/" in line and line.endswith(".msg"):
            out[line.rsplit("/", 1)[-1][:-len(".msg")]] = line
    return out


# ------------------------------------------------------------------ .msg
LABEL_KEY_RE = re.compile(r"[_\d]|^[A-Z0-9 ]+$|^dummy$|[一-鿿ぁ-ヿ]")


def label_is_text(label):
    """label ในตาราง .msg ที่เป็น **ข้อความบนจอ** (ชื่อผู้พูด · ตัวเลือกตอบ) ไม่ใช่คีย์ของเอนจิ้น

    หลักฐาน: POC "Young Woman"→"หญิงสาว" (Repak7 · 3 ก.ย. 2026) ขึ้นไทยบนจอจริง = ชื่อผู้พูดเป็นข้อความล้วน
    เกณฑ์คัด: ไม่มี `_`/ตัวเลข (Talk_Yes · Talk_Ojigi · wepct9000) · ไม่ใช่ตัวพิมพ์ใหญ่ล้วน (ArmsID/ID) ·
    ไม่ใช่ dummy · ไม่มีอักษรญี่ปุ่น (龍馬 = คีย์ฝั่ง JA) · ขึ้นต้นด้วยตัวพิมพ์ใหญ่หรือเครื่องหมายคำพูด
    (คิวเสียง `haruka`/`iku` เป็นตัวพิมพ์เล็กล้วน — ห้ามแตะ)
    """
    if not label or LABEL_KEY_RE.search(label):
        return False
    return label[0].isupper() or label[0] in "\"'("


def label_replacements_for(labels, th_map):
    """{label เดิม: ไทย} เฉพาะ label ที่เป็นข้อความและ master มีคำแปล"""
    out = {}
    for lab in labels:
        if lab in out or not label_is_text(lab):
            continue
        th = th_map.get(lab)
        if th is not None and th != lab:
            out[lab] = th
    return out


def build_msg(th_map, dry_run=False):
    """ประกอบ `.msg` ใหม่เฉพาะไฟล์ที่มีบรรทัดถูกแปล · คืน {path ในเกม: ไบต์}"""
    game_paths = msg_game_paths()
    files, n_lines, n_labels, missing_path = {}, 0, 0, []
    for js in sorted(paths.TEXT_EN.glob("*.json")):
        records = json.loads(js.read_text(encoding="utf-8"))
        repl = {}
        for r in records:
            th = th_map.get(r["en"])
            if th is not None:
                repl[r["line"]] = th
        uid = js.stem
        src = paths.MSG_EN / (uid + ".msg")
        if not src.exists():
            continue
        m = msgmod.load(src)
        lab_repl = label_replacements_for(m.labels, th_map)     # ชั้น label (ชื่อผู้พูด/ตัวเลือก)
        if not repl and not lab_repl:
            continue
        gp = game_paths.get(uid)
        if gp is None:
            missing_path.append(uid)
            continue
        n_lines += len(repl)
        n_labels += len(lab_repl)
        if dry_run:
            files[gp] = b""
            continue
        data = m.rebuild(repl, lab_repl or None)
        STAGE_MSG.mkdir(parents=True, exist_ok=True)
        (STAGE_MSG / (uid + ".msg")).write_bytes(data)
        files[gp] = data
    if missing_path:
        print("!! ไม่พบ path ในเกมของ %d ไฟล์ .msg (ตัวอย่าง: %s)"
              % (len(missing_path), " ".join(missing_path[:3])))
    print("msg   : ไฟล์ที่เปลี่ยน %d · บรรทัดที่แทนที่ %d · label ที่แทนที่ %d"
          % (len(files), n_lines, n_labels))
    return files


# ------------------------------------------------------------------ ARMP
def _rebuild_armp(table, doc):
    """เขียน JSON ที่แก้แล้วลง temp แล้วให้ reARMP ประกอบเป็น .bin · คืนไบต์ (None = ล้มเหลว)

    reARMP เป็นสคริปต์ CLI ที่เขียนผลลัพธ์ลง **cwd ของตัวเอง** และตั้งชื่อไฟล์ออกเป็น
    `<ชื่อไฟล์เข้า>.bin` จึงต้องทำงานในโฟลเดอร์ชั่วคราวแล้วเปลี่ยนชื่อเอง
    """
    with tempfile.TemporaryDirectory(prefix="ishin_armp_") as td:
        td = Path(td)
        src = td / (table + ".bin.json")
        src.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        subprocess.run([sys.executable, str(REARMP), src.name],
                       cwd=str(td), input=b"\n", capture_output=True, check=False)
        out = td / (src.name + ".bin")
        if not out.exists():
            return None
        data = out.read_bytes()
        # คืนไบต์ของคอลัมน์ชนิดที่ reARMP ไม่รู้จัก (30/31) จาก vanilla — ดู scripts/armp_graft.py
        van = paths.EXTRACTED / "db_en" / (table + ".bin")
        if van.exists():
            data, _notes = armp_graft.graft(van, data)
        return data


def deny_tables():
    """ตารางที่ `check_armp_rebuild.py` พิสูจน์แล้วว่าตัวเขียนของ reARMP ทำ layout พัง

    เคสจริงของภาคนี้ (2 ก.ย. 2026): คอลัมน์ชนิด 30/31 ถูกเขียนกลับเป็นศูนย์ทั้งก้อน
    ตาราง `tips` จึงจะเสียเงื่อนไขการแสดงผลทั้งตารางถ้ายอมประกอบกลับ — ข้อความ 172 ช่อง
    ของตารางนั้นต้องรอวิธีอื่น (แพตช์ไบต์ตรง ๆ) ไม่ใช่ปล่อยผ่าน
    """
    p = paths.BUILD / "armp_deny.json"
    if not p.exists():
        print("!! ยังไม่มี %s — รัน scripts/check_armp_rebuild.py ก่อนบิลด์จริง" % p.name)
        return set()
    return set(json.loads(p.read_text(encoding="utf-8")).get("tables") or [])


def _table_text_cols(tbl):
    return {c for c, t in (tbl.get("columnTypes") or {}).items() if t == 13}


def _replace_table(tbl, th_map, denied, table=None):
    """แทนที่ช่องข้อความของตาราง ARMP หนึ่งตาราง **รวมตารางที่ซ้อนอยู่ในแถว**

    ⚠ ตาราง ARMP ของภาคนี้ซ้อนกันได้: แถวหนึ่งมีคีย์ `table` ที่เป็นตารางเต็ม ๆ อีกชั้น
    ข้อความจริงของ `tips` (ทิปส์/สมุดบันทึก) อยู่ชั้นซ้อนทั้งหมด — เวอร์ชันแรกของตัวแทนที่
    เดินแค่ชั้นบน จึงแปลไม่ถึง 968 ช่อง และผู้เล่นเห็นจอทิปส์เป็นอังกฤษ (เจอ 3 ก.ย. 2026)
    """
    cols = _table_text_cols(tbl)
    if table is not None:                       # ล็อกคอลัมน์ที่เกมใช้ประกอบพาธ (DENY_COLUMNS)
        cols = {c for c in cols if (table, c) not in DENY_COLUMNS}
    changed = skipped = 0
    for k, v in tbl.items():
        if not k.isdigit() or not isinstance(v, dict):
            continue
        for row in v.values():
            if not isinstance(row, dict):
                continue
            for col in cols:
                s = row.get(col)
                if not isinstance(s, str):
                    continue
                th = th_map.get(s)
                if th is None:
                    continue
                if denied:
                    skipped += 1
                    continue
                row[col] = th
                changed += 1
            inner = row.get("table")
            if isinstance(inner, dict):
                c, s2 = _replace_table(inner, th_map, denied)
                changed += c
                skipped += s2
    return changed, skipped



def build_db(th_map, dry_run=False):
    """แทนที่ข้อความในตาราง ARMP ทุกคอลัมน์ชนิด 13 (string) · คืน {path ในเกม: ไบต์}"""
    files, n_cells, n_tables_failed = {}, 0, []
    deny = deny_tables()
    n_denied = 0
    for js in sorted((paths.EXTRACTED / "db_en").glob("*.bin.json")):
        table = js.name[:-len(".bin.json")]
        if SKIP_TABLES.match(table) or table in KEEP_EN_TABLES or table in DENY_TABLES:
            continue
        doc = json.loads(js.read_text(encoding="utf-8"))
        denied = table in deny      # ห้ามประกอบกลับ (ดู build/armp_rebuild_report.md)
        if not _table_text_cols(doc):
            continue
        changed, skipped = _replace_table(doc, th_map, denied, table=table)
        n_denied += skipped
        if not changed:
            continue
        n_cells += changed
        gp = DB_GAME_DIR + table + ".bin"
        if dry_run:
            files[gp] = b""
            continue
        data = _rebuild_armp(table, doc)
        if data is None:
            n_tables_failed.append(table)
            continue
        STAGE_DB.mkdir(parents=True, exist_ok=True)
        (STAGE_DB / (table + ".bin")).write_bytes(data)
        files[gp] = data
    if n_tables_failed:
        print("!! reARMP ประกอบไม่สำเร็จ %d ตาราง: %s"
              % (len(n_tables_failed), " ".join(n_tables_failed[:5])))
    msg_deny = ""
    if deny:
        msg_deny = (" · ข้ามตารางต้องห้าม %d ตาราง (ช่องที่แปลไว้แล้วแต่ยังใส่ไม่ได้ %d)"
                    % (len(deny), n_denied))
    print("armp  : ตารางที่เปลี่ยน %d · ช่องที่แทนที่ %d%s" % (len(files), n_cells, msg_deny))
    return files


# ------------------------------------------------------------------ locres
def build_locres(th_map, dry_run=False):
    """ชี้คีย์ที่แปลแล้วไปยังสตริงไทยที่เพิ่มท้ายตาราง · คืน {path ในเกม: ไบต์}"""
    src_json = paths.EXTRACTED / "locres" / "Game.en.json"
    if not src_json.exists():
        print("locres: ไม่มี %s — ข้าม (รัน scripts/extract_locres.py ก่อน)" % src_json.name)
        return {}
    doc = json.loads(src_json.read_text(encoding="utf-8"))
    strings = doc["strings"]
    raw_lengths = doc.get("raw_lengths") or []

    added = {}          # ข้อความไทย -> ดัชนีใหม่ (สตริงเดียวกันใช้ช่องเดียวพอ)
    n_changed = 0
    for node in doc["namespaces"]:
        ns = node["ns"]
        if SKIP_NS.match(ns):            # staffroll/credit/license/kiyaku คง EN
            continue
        for entry in node["entries"]:
            en = strings[entry["idx"]]
            th = th_map.get(en)
            if th is None:
                continue
            idx = added.get(th)
            if idx is None:
                strings.append(th)
                if raw_lengths:
                    raw_lengths.append(None)
                idx = added[th] = len(strings) - 1
            entry["idx"] = idx
            n_changed += 1
    print("locres: คีย์ที่เปลี่ยน %d · สตริงไทยที่เพิ่ม %d" % (n_changed, len(added)))
    if not n_changed or dry_run:
        return {LOCRES_GAME_PATH: b""} if (n_changed and dry_run) else {}

    if raw_lengths:
        doc["raw_lengths"] = raw_lengths
    STAGE_LOCRES.mkdir(parents=True, exist_ok=True)
    patched_json = STAGE_LOCRES / "Game.th.json"
    patched_json.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    patched = STAGE_LOCRES / "Game.locres"
    locres.build_full(str(patched_json), str(patched))
    return {LOCRES_GAME_PATH: patched.read_bytes()}


# ------------------------------------------------------------------ pak
def install(pak):
    dst = paths.MODS_DIR / paths.MOD_PAK
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pak, dst)
    print("ติดตั้งแล้ว: %s (%d ไบต์)" % (dst, dst.stat().st_size))
    print("การทดสอบในเกมเป็นหน้าที่ผู้ใช้ — สคริปต์นี้ไม่เปิดเกม (กติกาเหล็กข้อ 2)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layers", default="msg,armp,locres",
                    help="ชั้นที่จะบิลด์ คั่นด้วยจุลภาค (msg · armp · locres)")
    ap.add_argument("--dry-run", action="store_true", help="นับอย่างเดียว ไม่เขียนไฟล์")
    ap.add_argument("--no-font", action="store_true", help="ไม่ใส่ฟอนต์ไทยลง pak")
    ap.add_argument("--install", action="store_true", help="คัดลอก pak เข้าโฟลเดอร์ ~mods ของเกม")
    a = ap.parse_args()

    th_map = load_master()
    print("คำแปลใน master_th: %d คู่ (นับเฉพาะที่ต่างจากต้นฉบับ)" % len(th_map))
    if not th_map:
        print("ยังไม่มีคำแปล — ไม่มีอะไรให้บิลด์")
        return 0

    want = {s.strip() for s in a.layers.split(",") if s.strip()}

    # ⚠ ล้างโฟลเดอร์ stage ของชั้นที่กำลังจะบิลด์ทุกครั้ง
    # ตัวบิลด์เขียนทับเฉพาะไฟล์ที่มันสร้างรอบนี้ ไฟล์เก่าที่ค้างอยู่จะถูกแพ็กเข้า pak ไปด้วย
    # (เกิดจริง 3 ก.ย. 2026: ไฟล์จากบิลด์ทดสอบเมื่อ 2 ก.ย. หลุดเข้าม็อด — `battle_bomb_info.bin`
    #  มี asset id เป็น "ทดสอบไทย wepct9000" และ .msg สองไฟล์มีข้อความทดสอบนำหน้า)
    if not a.dry_run:
        for layer, folder in (("msg", STAGE_MSG), ("armp", STAGE_DB), ("locres", STAGE_LOCRES)):
            if layer in want and folder.exists():
                shutil.rmtree(folder)

    files = {}
    if "msg" in want:
        files.update(build_msg(th_map, a.dry_run))
    if "armp" in want:
        files.update(build_db(th_map, a.dry_run))
    if "locres" in want:
        files.update(build_locres(th_map, a.dry_run))

    if a.dry_run:
        print("dry-run: ไฟล์ที่จะเข้า pak %d รายการ (ไม่ได้เขียนอะไร)" % len(files))
        return 0
    if not files:
        print("ไม่มีไฟล์ที่เปลี่ยน — ไม่แพ็ก pak")
        return 0

    if not a.no_font:
        if paths.SARABUN_TTF.exists():
            ttf = paths.SARABUN_TTF.read_bytes()
            for gpath in FONT_GAME_PATHS:
                files[gpath] = ttf
            print("ฟอนต์: ทับ %d FontFace ด้วย %s"
                  % (len(FONT_GAME_PATHS), paths.SARABUN_TTF.name))
        else:
            print("!! ไม่พบฟอนต์ %s — แพ็กโดยไม่ใส่ฟอนต์" % paths.SARABUN_TTF)

    paths.BUILD.mkdir(parents=True, exist_ok=True)
    pak = write_pak(paths.BUILD / paths.MOD_PAK, files)
    total = sum(len(v) for v in files.values())
    print("pak: %s · ไฟล์ %d · เนื้อข้อมูล %.1f MB · ขนาดไฟล์ %.1f MB"
          % (pak, len(files), total / 1e6, pak.stat().st_size / 1e6))
    print("ด่านบังคับก่อนส่ง: python scripts/check_pak_roundtrip.py และ "
          "python scripts/check_layout_all.py")
    if a.install:
        install(pak)
    return 0


if __name__ == "__main__":
    sys.exit(main())
