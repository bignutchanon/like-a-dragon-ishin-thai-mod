#!/usr/bin/env python3
"""สร้างชุด "สปอย" ภาษาไทยของ Lost Judgment — เมนูไตเติล + คัตซีนเปิดเรื่อง (บทที่ 1)

ทำไมต้องมี slot map สองชุด (ยืนยันกับไฟล์เกมจริง 22 ส.ค. 2026):
  * เมนูไตเติลวาดด้วย `metaoffcpro-condbook` (มี Latin-1 accented ครบ) -> `thai_encode.py`
  * ซับคัตซีนโหมด EN วาดด้วย `tbgm_0p_hires` (`font2_style.font_face_en`) ซึ่งเป็นฟอนต์ญี่ปุ่น
    ไม่มี Latin-1 accented แต่มี Cyrillic ครบ 66 ตัวพอดี -> `thai_encode_cyr.py`
  ดังนั้นข้อความคนละไฟล์ต้อง encode คนละ map — สคริปต์นี้จัดให้ตามชนิดของ bin

โพรบที่ฝังมาด้วย: สองบรรทัดของคัตซีน (แถว PROBE_ROWS) เขียนด้วย **codepoint ไทยจริง**
(U+0E01..) แทน donor เพราะ `inject_thai_sdf.py --alias-thai` ใส่ alias ไว้ให้แล้ว
-> ภาพเดียวตอบได้ว่าเอนจิ้น route ตัวอักษรไทยตรง ๆ ได้ไหม ถ้าได้ทั้งโปรเจกต์เลิกใช้ donor ได้

ผลลัพธ์ลง `build/text/db.coyote.en/`:
  title_root.bin · font2_face.bin (ถ้าขนาด atlas เปลี่ยน) · sound_auth.bin

ใช้:  python scripts/make_spoil.py
อ่าน  extracted/db_en/*.bin.json (ต้นฉบับ — ไม่แตะ)
"""
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                                              # noqa: E402
import thai_encode as MAP_LATIN1                          # noqa: E402
import thai_encode_cyr as MAP_CYR                         # noqa: E402

STAGE = paths.BUILD / "text" / "db.coyote.en"
WORK = paths.BUILD / "text" / "_work"
REPORT = paths.BUILD / "text" / "SPOIL.md"

# face ที่ atlas ถูกขยาย -> ต้องอัปเดต texture_height ใน font2_face.bin ให้ตรง
ATLAS_HEIGHT = {"metaoffcpro-condbook": 1184}

# ---------------------------------------------------------------- เมนูไตเติล
# (row_key, column, ไทย) — encode ด้วย map Latin-1
TITLE_EDITS = [
    ("new_game", "name", "เริ่มเกมใหม่"),
    ("new_game", "explanation", "เริ่มเล่นตั้งแต่ต้นเรื่อง"),
    ("new_game", "explanation2",
     "เริ่มเล่นตั้งแต่ต้นเรื่อง ต้องเขียนทับไฟล์เซฟเดิมจึงจะไปต่อได้ (สูงสุด 30 ไฟล์)"),
    ("new_game_after_clear", "name", "เริ่มเกมใหม่"),
    ("new_game_after_clear", "explanation", "เริ่มเล่นตั้งแต่ต้นเรื่อง"),
    ("new_game_after_clear", "explanation2",
     "เริ่มเล่นตั้งแต่ต้นเรื่อง และเที่ยวสำรวจได้โดยไม่ต้องเดินตามเนื้อเรื่องหลัก"),
    ("new_game_after_clear_main_story", "name", "เริ่มเล่นแบบปกติ"),
    ("new_game_after_clear_main_story", "explanation", "เริ่มเกมใหม่ตั้งแต่ต้น"),
    ("new_game_after_clear_padv", "name", "เริ่มเล่นด้วยข้อมูลจบเกม"),
    ("new_game_after_clear_padv", "explanation",
     "เริ่มเกมใหม่โดยยกเงิน สกิล ไอเทม\nและความคืบหน้า TownGo มาด้วย"),
    ("continue", "name", "เล่นต่อ"),
    ("continue", "explanation", "เล่นต่อจากไฟล์เซฟ"),
    ("continue_after_clear", "name", "เล่นต่อ"),
    ("continue_after_clear", "explanation", "เล่นต่อจากไฟล์เซฟ"),
    ("continue_playstation_previous_generation", "name", "ย้ายข้อมูลจาก PlayStation®4"),
    ("continue_playstation_previous_generation", "explanation",
     "ย้ายไฟล์เซฟจาก \"Lost Judgment\" เวอร์ชัน PlayStation®4\n"
     "ข้อมูลของ The Gauntlet และ Master System จะไม่ถูกย้ายมา"),
    ("option", "name", "ตั้งค่าเกม"),
    ("option", "explanation", "ปรับตั้งค่าที่มีผลต่อการเล่น"),
    ("audio_option", "name", "ตั้งค่าเสียง"),
    ("audio_option", "explanation", "ปรับตั้งค่าเสียงในเกม"),
    ("movie", "name", "ดูฉากย้อนหลัง"),
    ("movie", "explanation", "ดูฉากเนื้อเรื่องหลักที่เคยผ่านมาแล้ว"),
    ("coyote_premium_adventure", "name", "พรีเมียมแอดเวนเจอร์"),
    ("coyote_premium_adventure", "explanation",
     "ตะลุยเมืองได้อิสระโดยไม่ต้องเดินตามเนื้อเรื่องหลัก"),
    ("coyote_photo_gallery", "name", "คลังภาพถ่าย"),
    ("coyote_photo_gallery", "explanation", "ดูภาพที่ถ่ายด้วยมือถือในเกม"),
    ("kaito_story_root", "name", "แฟ้มคดีไคโตะ"),
    ("kaito_story_root", "explanation", "เริ่มเนื้อหาเสริมที่มีมาซาฮารุ ไคโตะเป็นตัวเอก"),
    ("kaito_story_new_game", "name", "เริ่มเกมใหม่"),
    ("kaito_story_new_game", "explanation", "เริ่มเล่นตั้งแต่ต้นเรื่อง"),
    ("kaito_story_continue", "name", "เล่นต่อ"),
    ("kaito_story_continue", "explanation", "เล่นต่อจากไฟล์เซฟ"),
    ("profile_change", "name", "เปลี่ยนโปรไฟล์"),
    ("profile_change", "explanation", "สลับผู้ใช้ที่กำลังเล่นอยู่"),
    ("two_player_game", "name", "มินิเกมต่อสู้ 2 ผู้เล่น"),
    ("two_player_game", "explanation",
     "เกมคลาสสิกที่เล่นสู้กันได้สองคน\n"
     "* ต้องใช้<platform_type=pc>คอนโทรลเลอร์</platform_type>"
     "<platform_type=ps>คอนโทรลเลอร์ไร้สาย</platform_type>"
     "<platform_type=xb>คอนโทรลเลอร์</platform_type>สองอัน\n"
     "* ไม่นับรวมในรายการความสำเร็จ"),
    ("gauntlet", "name", "เดอะ กอนต์เล็ต"),
    ("gauntlet", "explanation",
     "โหมดความยากสูงที่ต้องลุยภารกิจหลากหลายเงื่อนไข\n"
     "เคลียร์ภารกิจครั้งแรกจะได้ไอเทมหายาก"),
    ("dlc", "name", "เนื้อหาดาวน์โหลด"),
    ("dlc", "explanation", "เปิดหน้าร้านค้าเพื่อดูเนื้อหาเสริมบน ${platform.term.store}"),
    ("staffroll", "name", "เครดิตเพิ่มเติม"),
    ("staffroll", "explanation", "ดูเครดิตทีมงานที่เพิ่มมาพร้อมเนื้อหาดาวน์โหลด"),
    ("staffroll_steam", "name", "ทีมพัฒนาเวอร์ชัน PC"),
    ("staffroll_steam", "explanation", "ดูเครดิตทีมพัฒนาเวอร์ชัน PC"),
    ("auto_save_attention", "name", "เปิดบันทึกอัตโนมัติไหม"),
    ("auto_save_attention", "explanation",
     "เลือกใช่เพื่อบันทึกก่อนเริ่มเล่น\nเลือกไม่เพื่อเริ่มเล่นโดยไม่สร้างไฟล์เซฟ"),
    ("quit_game", "name", "ออกจากเกม"),
    ("quit_game", "explanation", "จบเกมแล้วกลับสู่เดสก์ท็อป"),
    ("difficulty_easy", "name", "ง่าย"),
    ("difficulty_normal", "name", "ปกติ"),
    ("difficulty_hard", "name", "ยาก"),
    ("difficulty_legend", "name", "ตำนาน"),
    ("difficulty_ex_easy", "name", "ง่ายมาก"),
]
# License Information / Detective Essentials Pack / School Stories Expansion Pack /
# ชื่อเกม Virtua Fighter 5 ฯลฯ คงอังกฤษ (กติกาเหล็กข้อ 10 + ชื่อผลิตภัณฑ์)

# ------------------------------------------------- คัตซีนเปิดเรื่อง (บทที่ 1)
SPEECH_ROW = ("267", "speech_list_coyote_main_c01")
COL_MSG = "4"       # ซับตอนเสียงญี่ปุ่น
COL_MSG_EN = "13"   # ซับตอนเสียงอังกฤษ
# แถวที่จะเขียนด้วย codepoint ไทยจริงแทน donor (โพรบ)
PROBE_ROWS = {18, 19}

# index -> (ไทยสำหรับคอลัมน์ 4, ไทยสำหรับคอลัมน์ 13)
CUTSCENE = {
    0: ("โคสุเกะคุงบอกตลอดว่ามื้อกลางวัน\nกินแต่ฟาสต์ฟู้ด",
        "โคสุเกะคุงเคยบอกว่ามื้อกลางวันกินแต่ฟาสต์ฟู้ด..."),
    1: ("เข้าไปตั้งเกือบยี่สิบนาทีแล้วนะ เขากินช้าหรือเปล่า",
        "อือ แต่ปาเข้าไปยี่สิบนาที น่าจะกินเสร็จได้แล้วมั้ง"),
    2: ("ไม่รู้สิคะ แต่เป็นห่วงเขาจัง หวังว่าจะสั่งผักกินบ้างนะ",
        "ไม่รู้สิคะ... เขาทำให้เป็นห่วงตลอด เรื่องกินก็ด้วย"),
    3: ("นี่ เคโกะจัง สาวดี ๆ อย่างเธอไปรีบคบกับหมอนี่จากเน็ตทำไม",
        "นี่ เคโกะจัง สาวดี ๆ อย่างเธอไปโดนหมอนี่จากเน็ตหลอกได้ยังไง"),
    4: ("เปล่านะคะ ไม่ได้รีบเลย", "ไม่ได้เป็นแบบนั้นเลยค่ะ"),
    5: ("เราค่อย ๆ คบกันจริง ๆ นะคะ โคสุเกะคุงเข้าใจหนูมากกว่าใคร",
        "ถ้าบอกว่าตอนแรกเราค่อย ๆ คบกันจะเชื่อไหมคะ ความอดทนของเขาได้ผลนะ"),
    6: ("เขาเป็นคนดีจริง ๆ นะคะ", "พี่อาจมองไม่เห็น แต่เขาเป็นคนใส่ใจนะคะ"),
    7: ("ดีถึงขั้นลากเธอไปโดนบาร์ตุ๋นเลยเหรอ แถมที่คามุโรโจอีก",
        "ลากเธอไปบาร์กระจอกที่สุดในคามุโรโจแล้วเรียกว่าเดต ยอดชายจริง ๆ"),
    8: ("เขาคงไม่รู้ว่าร้านแบบนั้นเป็นยังไงค่ะ",
        "เขาแค่อยากทำให้หนูประทับใจ ไม่มีทางรู้หรอกว่าจะเกิดเรื่องแบบนี้"),
    9: ("เหรอ แล้วทำไมโยนบิลทั้งใบมาให้เธอจ่ายล่ะ",
        "แล้วก็ทิ้งบิลไว้ให้แฟนตัวเองจ่าย เรียกว่าไอ้เวรยังน้อยไป"),
    10: ("ก็เขายังเป็นนักศึกษาอยู่นี่คะ แล้วก็...", "ก็เขายังเรียนอยู่นะคะ แล้วก็..."),
    11: ("เขาบอกว่าถ้าไม่จ่าย พวกยากูซ่าจะฆ่าเขาค่ะ",
         "เขาบอกว่าถ้าไม่จ่าย พวกนั้นจะเรียกยากูซ่ามาทวงค่ะ"),
    12: ("เธอบอกว่ายอดรวม 1.2 ล้าน แล้วยังค้างอีก 4 แสนใช่ไหม",
         "โดนรีดไป 8 แสน เหลืออีก 4 แสน รวมเป็น 1.2 ล้าน"),
    13: ("ไม่ใช่เงินเล่น ๆ เลยนะ", "จะจ่ายทีเดียวหมดนี่แทบเป็นไปไม่ได้เลย"),
    14: ("ค่ะ โคสุเกะคุงก็พูดแบบนั้นเหมือนกัน", "ใช่ค่ะ โคสุเกะคุงเลยเสนอไอเดียมา..."),
    15: ("เขาบอกว่าทางเร็วที่สุดคือไปทำงานร้านขายบริการ",
         "เขาบอกว่าหนูหาเงินง่าย ๆ ได้ ถ้าไปทำงานร้าน \"แบบนั้น\""),
    16: ("มุกคลาสสิก โคสุเกะคุงกับร้านตุ๋นนั่นสมคบกันมาตั้งแต่แรก",
         "นั่นสินะ เขาพูดถึงเรื่องร่วมมือกับพวกยากูซ่ามาตั้งแต่ต้นไหม"),
    17: ("รีดเงินก้อนโตจากผู้หญิง แล้วบีบให้ไปขายตัวใช้หนี้",
         "หนุ่มเจอสาว ออกเดต ก่อหนี้ แล้วสุดท้ายเธอก็ต้องไปขายตัวใช้หนี้"),
    18: ("เมืองนี้มันเป็นแบบนี้แหละ น่าเศร้า", "เรื่องเดิม ๆ ในเมืองนี้แหละ"),
    19: ("...เรายังไม่รู้แน่ชัดสักหน่อยค่ะ", "พี่ด่วนสรุปไปเองแล้วนะคะ"),
    20: ("แล้วทำไมไม่ไปสั่งปิดร้านแย่ ๆ พวกนั้นให้หมดล่ะคะ",
         "อีกอย่าง ร้านที่เอาเปรียบคนแบบนั้นน่าจะโดนสั่งปิดไปนานแล้วไม่ใช่เหรอคะ"),
    21: ("กฎหมายข้ามเส้นนั้นไม่ได้ เขาเรียกว่า \"ไม่แทรกแซง\"",
         "ไม่ได้หรอก บางเส้นกฎหมายข้ามไม่ได้จนกว่าจะสายเกินไป"),
}


def check(th, mapping, where):
    miss = mapping.coverage(th)
    if miss:
        sys.exit("ตัวอักษรไทยไม่มีใน %s: %s (%s)" % (mapping.__name__, miss, where))


def nl(a, b, where):
    if a.count("\n") != b.count("\n"):
        sys.exit("จำนวน \\n ไม่ตรงต้นฉบับที่ %s (%d != %d)"
                 % (where, b.count("\n"), a.count("\n")))


def rearmp(json_path):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, str(paths.REARMP), json_path.name],
                       cwd=str(WORK), env=env, capture_output=True, timeout=3600)
    out = WORK / (json_path.name + ".bin")
    if r.returncode != 0 or not out.exists() or out.stat().st_size == 0:
        err = r.stderr.decode("utf-8", "replace").strip().splitlines()
        sys.exit("reARMP ล้ม (%s): %s" % (json_path.name, err[-1] if err else "?"))
    return out


def load(name):
    return json.load(io.open(paths.EXTRACTED / "db_en" / (name + ".bin.json"), encoding="utf-8"))


def build_title():
    doc = load("title_root")
    index = {k: v for i in range(doc["ROW_COUNT"]) for k, v in doc[str(i)].items()}
    log = []
    for key, col, th in TITLE_EDITS:
        fields = index.get(key)
        if fields is None:
            sys.exit("ไม่พบแถว %r ใน title_root.bin" % key)
        en = fields.get(col, "")
        check(th, MAP_LATIN1, "title_root/%s/%s" % (key, col))
        nl(en, th, "title_root/%s/%s" % (key, col))
        fields[col] = MAP_LATIN1.encode(th)
        log.append(("title_root", key, col, en, th, "latin1"))
    return doc, log


def build_speech():
    doc = load("sound_auth")
    row, col = SPEECH_ROW
    table = doc[row][col]["table"]
    log = []
    for idx, (th4, th13) in sorted(CUTSCENE.items()):
        fields = list(table[str(idx)].values())[0]
        mapping = MAP_CYR
        mode = "cyr"
        if idx in PROBE_ROWS:
            mapping = None
            mode = "thai-real"
        for c, th in ((COL_MSG, th4), (COL_MSG_EN, th13)):
            en = fields.get(c) or ""
            where = "%s[%d]/%s" % (col, idx, c)
            check(th, MAP_CYR, where)          # ตรวจด้วย map เดียวกันเสมอ (ชุดตัวอักษรเท่ากัน)
            nl(en, th, where)
            fields[c] = th if mapping is None else mapping.encode(th)
            log.append(("sound_auth", "%s[%d]" % (col, idx), c, en, th, mode))
    return doc, log


def build_font2_face():
    doc = load("font2_face")
    changed = []
    for i in range(doc["ROW_COUNT"]):
        for key, fields in doc[str(i)].items():
            if key in ATLAS_HEIGHT and fields.get("texture_height") not in (None, ATLAS_HEIGHT[key]):
                changed.append((key, fields["texture_height"], ATLAS_HEIGHT[key]))
                fields["texture_height"] = ATLAS_HEIGHT[key]
    return doc, changed


def write_report(log, atlas_changes):
    L = ["# ชุดสปอยภาษาไทย — Lost Judgment", "",
         "> สร้างด้วย `python scripts/make_spoil.py` — ห้ามแก้ด้วยมือ", "",
         "ฟอนต์ที่ต้องคู่กัน (`build/font/`):", "",
         "```",
         "python scripts/inject_thai_sdf.py metaoffcpro-condbook --grow",
         "python scripts/inject_thai_sdf.py tbgm_0p_hires tbgm_0p --map=cyr --grow --alias-thai",
         "```", ""]
    if atlas_changes:
        L += ["## `font2_face.bin`", "", "| face | texture_height เดิม | ใหม่ |", "|---|---|---|"]
        L += ["| %s | %d | %d |" % c for c in atlas_changes] + [""]
    L += ["## ข้อความที่แก้ (%d ช่อง)" % len(log), "",
          "| bin | แถว | คอลัมน์ | map | อังกฤษ | ไทย |", "|---|---|---|---|---|---|"]
    for b, key, col, en, th, mode in log:
        L.append("| `%s` | `%s` | %s | %s | %s | %s |"
                 % (b, key, col, mode, en.replace("\n", " / ").replace("|", "\\|")[:70],
                    th.replace("\n", " / ")))
    L += ["", "## โพรบ codepoint ไทยจริง", "",
          "แถว %s ของ `%s` เขียนด้วย U+0E01.. ตรง ๆ (ไม่ผ่าน donor) — "
          "ถ้าบนจอขึ้นไทยแปลว่าเอนจิ้น route ตัวอักษรไทยได้เอง และทั้งโปรเจกต์เลิกใช้ donor map ได้"
          % (sorted(PROBE_ROWS), SPEECH_ROW[1]), ""]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    io.open(REPORT, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")


def main():
    STAGE.mkdir(parents=True, exist_ok=True)
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    title_doc, title_log = build_title()
    speech_doc, speech_log = build_speech()
    face_doc, atlas_changes = build_font2_face()

    jobs = [("title_root", title_doc), ("sound_auth", speech_doc)]
    if atlas_changes:
        jobs.append(("font2_face", face_doc))
    for name, doc in jobs:
        jp = WORK / ("%s.bin.json" % name)
        io.open(jp, "w", encoding="utf-8", newline="\n").write(
            json.dumps(doc, ensure_ascii=False, indent=1))
        out = rearmp(jp)
        dst = STAGE / ("%s.bin" % name)
        shutil.copy2(out, dst)
        print("เขียน %s (%s B)" % (dst.name, "{:,}".format(dst.stat().st_size)))

    write_report(title_log + speech_log, atlas_changes)
    print("แก้ %d ช่อง (ไตเติล %d · คัตซีน %d) · รายงาน: %s"
          % (len(title_log) + len(speech_log), len(title_log), len(speech_log), REPORT))


if __name__ == "__main__":
    main()
