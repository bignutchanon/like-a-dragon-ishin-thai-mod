"""mark_dnt.py — คัดสตริงที่ "ห้ามแปล" (Do Not Translate) ออกจากคิวแปล

ที่มาของปัญหา: worklist สร้างด้วยตัวกรอง translatable() ที่ดูแต่ *หน้าตาสตริง*
คอลัมน์ที่เก็บ path รูป / ธงเนื้อเรื่อง / id ภายใน จึงหลุดเข้าคิวแปลไปด้วย
(เช่น "/WeaponThumbnail/T_UI_Thum_model3" · "TUTORIAL_BTL_掴み_開始" · "dragon_hawk")
ถ้าแปลของพวกนี้ = เกมหารูป/ธงไม่เจอ

วิธีคัด: ดู *คอลัมน์ต้นทางจริง* ของทุกครั้งที่สตริงโผล่ (จาก extracted/parallel/*.json)
สตริงจะเป็น DNT ก็ต่อเมื่อ **ทุกที่ที่มันโผล่** อยู่ในคอลัมน์ชนิดข้อมูล ไม่มีที่ไหนเป็นข้อความบนจอเลย

ชั้น .msg มีอีกกรณีหนึ่ง: ไฟล์บทสนทนาที่ RGG **ไม่เคยแปลเป็นอังกฤษเลย** (ทุกบรรทัด en เท่ากับ ja
และเนื้อในเป็นญี่ปุ่น) เช่น uid0134003a-c ที่เป็นบทคุยของ "桐生" (คิริว) ตกค้างมาจากภาคอื่น
ทั้งที่ Ishin ไม่มีตัวละครนี้ · และไฟล์ทดสอบของทีมพัฒนา (ป้ายผู้พูด 動作確認さん = "คุณตรวจการทำงาน")
ไฟล์พวกนี้ไม่ได้แสดงผลในเกมภาษาอังกฤษอยู่แล้ว จึงไม่คุ้มค่านักแปล -> คัดออกเป็น DNT

เขียนออก: translations/worklist/batch_NNN.dnt.json  (คีย์ -> เหตุผล)
โหมด --fill สร้างไฟล์ done ให้ก้อนที่เป็น DNT ล้วน โดย copy คีย์เป็นค่าเดิมทุกตัว
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import paths

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

PARALLEL = paths.EXTRACTED / "parallel"

# คอลัมน์ ARMP ที่เก็บข้อมูล ไม่ใช่ข้อความบนจอ (เทียบชื่อคอลัมน์แบบเต็ม)
DATA_COL_RE = re.compile(
    r"(^|_)(path|texture|texture_s|icon|icon_path|detail_path|silhouette_path|"
    r"uid|id|asset_id|table_id|item_id|down_id|up_id|left_id|right_id|"
    r"flag|scenario_flag|scenario_flag_sub|start_condition|finish_flag|success_flag|"
    r"material\d*|"
    r"kana|reward_item|item_armor|item_hachimaki|item_kote|derived|cuesheet|cue|"
    r"file|file_name|file_path|model|motion|se|bgm|sound)(\[\d+\])?$"
)

# ตารางที่ทั้งตารางเป็นข้อมูล
DATA_TABLE_RE = re.compile(r"^(item_file_name|item_file_path|motion_|sound_cuesheet|"
                           r"ui_texture_|input_key_texture_map|font_symbol|chara_common_)")

# หน้าตาสตริงที่เป็น id/path แน่นอน (ใช้เป็นหลักฐานเสริม ไม่ใช่ตัวตัดสินเดี่ยว)
PATH_RE = re.compile(r"^/[A-Za-z0-9_./-]+$")
FLAGNAME_RE = re.compile(r"^[A-Z0-9]+_[A-Za-z0-9_\-]*")
ROMAJI_ID_RE = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")


# รวมเครื่องหมายวรรคตอนญี่ปุ่น (　-〿) ด้วย — ไฟล์มาโครทดสอบกล้อง (uid00021bbb)
# เขียนเป็น "TURNHEAD。" ล้วน ไม่มีคานะเลย แต่เป็นบรรทัดของทีมพัฒนาเหมือนกัน
JP_CHAR_RE = re.compile(r"[　-ヿ㐀-鿿]")


def dead_msg_files(msg_rows):
    """ไฟล์ .msg ที่ RGG ไม่เคยแปลเป็นอังกฤษ: ทุกบรรทัด en เท่ากับ ja และเนื้อในเป็นญี่ปุ่นจริง

    เกณฑ์ต้องแน่นทั้งสองข้อ — ไฟล์ที่แค่มีบรรทัดญี่ปุ่นปนบางบรรทัด (ป้ายชื่อ/สัญลักษณ์)
    ไม่นับ เพราะบรรทัดอังกฤษที่เหลือยังต้องแปล
    """
    stat = defaultdict(lambda: [0, 0, 0])   # ไฟล์ -> [บรรทัด, en==ja, มีอักษรญี่ปุ่น]
    for r in msg_rows:
        v = stat[r["file"]]
        v[0] += 1
        if r["en"] == r["ja"]:
            v[1] += 1
        if JP_CHAR_RE.search(r["en"] or ""):
            v[2] += 1
    return {f for f, v in stat.items() if v[1] == v[0] and v[2] >= v[0] * 0.5}


# ตัวละครที่ **ไม่มีในภาคนี้** — ถ้าไฟล์ .msg ไหนเอ่ยชื่อนี้ แปลว่าเป็นบทตกค้างจากภาคอื่น
# (ยืนยันแล้วใน docs/research.md §14: uid0134xxxx = บทคุยโฮสเตสของคิริว)
# ⚠ ต้องตัดเฉพาะคีย์ที่โผล่ **เฉพาะใน** ไฟล์กลุ่มนี้เท่านั้น — คำอุทานสั้น ๆ อย่าง「ああ」
#   ใช้ร่วมกับฉากจริงของ Ishin ด้วย ถ้าตัดไปจะเสียบทจริง (เจอตอนตรวจก้อน MSG_016)
FOREIGN_NAME_RE = re.compile(r"桐生")


def foreign_msg_files(msg_rows):
    """ไฟล์ .msg ที่เอ่ยชื่อตัวละครนอกภาค — บทตกค้างจากเกมอื่น"""
    hit = set()
    for r in msg_rows:
        if FOREIGN_NAME_RE.search(r.get("ja") or ""):
            hit.add(r["file"])
    return hit


def load_sources():
    """สตริงอังกฤษ -> (เซตคอลัมน์ต้นทาง, ทุกครั้งที่โผล่ ja เท่ากับ en ไหม, ไฟล์ msg ที่ไม่เคยแปล)"""
    src = defaultdict(set)
    same_ja = {}
    db = json.loads((PARALLEL / "db.json").read_text(encoding="utf-8"))
    for r in db:
        src[r["en"]].add("armp:%s.%s" % (r["table"], r["col"]))
        same_ja[r["en"]] = same_ja.get(r["en"], True) and (r.get("ja") == r["en"])
    loc = json.loads((PARALLEL / "locres.json").read_text(encoding="utf-8"))
    for r in loc:
        src[r["en"]].add("locres:" + r["ns"])
        same_ja[r["en"]] = same_ja.get(r["en"], True) and (r.get("ja") == r["en"])
    msg = json.loads((PARALLEL / "msg.json").read_text(encoding="utf-8"))
    for r in msg:
        src[r["en"]].add("msg:" + r["file"])
        same_ja[r["en"]] = same_ja.get(r["en"], True) and (r.get("ja") == r["en"])
    dead = dead_msg_files(msg)
    # คีย์ที่โผล่ **เฉพาะใน** ไฟล์ของตัวละครนอกภาค = บทของเกมอื่นล้วน
    # (ตัดเป็นราย "คีย์" ไม่ใช่รายไฟล์ — ไฟล์พวกนี้บางไฟล์มีบทจริงของ Ishin ปนอยู่ด้วย)
    foreign = foreign_msg_files(msg)
    occ = defaultdict(set)
    for r in msg:
        occ[r["en"]].add(r["file"])
    foreign_keys = {en for en, files in occ.items() if files <= foreign}
    return src, same_ja, dead, foreign_keys


def is_data_source(s, dead_msg=frozenset()):
    if s.startswith("msg:"):
        return s.split(":", 1)[1] in dead_msg   # เฉพาะไฟล์ที่ไม่เคยแปลเป็นอังกฤษ
    if s.startswith("locres:"):
        return False          # ชั้นนี้เป็นข้อความบนจอทั้งหมด
    body = s.split(":", 1)[1]
    table, _, col = body.partition(".")
    if DATA_TABLE_RE.match(table):
        return True
    if re.search(r"(^|_)(id|uid)(_|$)", col):
        return True
    return bool(DATA_COL_RE.search(col))


# ชื่อ id ล้วน: ไม่มีช่องว่าง · ascii · ตัวเล็กผสมเลข/ขีดล่าง
IDENT_SHAPE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(?:[.-][A-Za-z0-9_]+)*$")


def classify(key, sources, same_ja=False, dead_msg=frozenset(), foreign_keys=frozenset()):
    """คืน (is_dnt, reason)"""
    if same_ja and IDENT_SHAPE_RE.match(key) and "_" in key or (
            same_ja and PATH_RE.match(key)):
        return True, "ชื่อ id (en เท่ากับ ja ทุกที่ที่โผล่)"
    if key in foreign_keys:
        return True, "บทของตัวละครนอกภาค (คิริว) ตกค้างจากเกมอื่น"
    if not sources:
        # ไม่พบต้นทาง — ตัดสินจากหน้าตาอย่างเดียว เฉพาะกรณีชัดมาก
        if PATH_RE.match(key):
            return True, "asset path"
        return False, ""
    if all(is_data_source(s, dead_msg) for s in sources):
        if all(s.startswith("msg:") for s in sources):
            return True, "ไฟล์ .msg ที่ไม่เคยแปลเป็นอังกฤษ: " + ", ".join(sorted(sources)[:3])
        return True, "คอลัมน์ข้อมูล: " + ", ".join(sorted(sources)[:3])
    return False, ""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    do_fill = "--fill" in sys.argv
    fill_threshold = 1.0 if "--only-pure" in sys.argv else 0.0

    src, same_ja, dead_msg, foreign_keys = load_sources()
    batches = sorted(paths.WORKLIST.glob("batch_*.json"))
    batches = [p for p in batches if ".prior" not in p.name and ".context" not in p.name
               and ".dnt" not in p.name]
    if args:
        want = {"batch_%s.json" % (a if not a.isdigit() else a.zfill(3)) for a in args}
        batches = [p for p in batches if p.name in want]

    total_dnt = 0
    for p in batches:
        d = json.loads(p.read_text(encoding="utf-8"))
        keys = list(d["strings"])
        dnt = {}
        for k in keys:
            ok, why = classify(k, src.get(k, set()), same_ja.get(k, False), dead_msg,
                               foreign_keys)
            if ok:
                dnt[k] = why
        n = p.stem[len("batch_"):]   # รับได้ทั้ง 042 และ MSG_007
        share = len(dnt) / max(1, len(keys))
        out = paths.WORKLIST / ("batch_%s.dnt.json" % n)
        if dnt:
            out.write_text(json.dumps(dnt, ensure_ascii=False, indent=1), encoding="utf-8")
        elif out.exists():
            out.unlink()
        total_dnt += len(dnt)
        mark = ""
        if do_fill and share >= max(fill_threshold, 0.999):
            done = paths.DONE / ("batch_%s.done.json" % n)
            if not done.exists():
                done.write_text(json.dumps(
                    {"batch": p.name, "strings": {k: k for k in keys}},
                    ensure_ascii=False, indent=1), encoding="utf-8")
                mark = " -> เขียน done แบบ copy ตรง"
        if dnt:
            print("batch_%s: DNT %d/%d (%.0f%%)%s" % (n, len(dnt), len(keys), share * 100, mark))
    print("รวม DNT %d สตริง จาก %d ก้อน" % (total_dnt, len(batches)))


if __name__ == "__main__":
    main()
