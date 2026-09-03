#!/usr/bin/env python3
"""
สร้าง worklist ให้ทีมแปล Lost Judgment — port จาก K3 (21 ส.ค. 2026)

input:
  extracted/unique_strings.json   ({EN: {count, bins[]}} จาก extract_all_en.py)
  extracted/strings_by_bin.json   ({bin: [EN,...]})
  translations/master.json        (คำแปล v1.2 เดิม — ใช้เป็น "ร่างอ้างอิง" เท่านั้น ไม่ auto-fill)

output:
  translations/worklist/batch_NNN.json       (<=250 strings/batch)
  translations/worklist/batch_TALK_NNN.json  (talk.bin-only)
  translations/worklist_report.md

ต่างจาก K2R tm_match:
  - **ไม่ auto-fill master_th จาก TM** — user สั่งแปลใหม่ทั้งเกม ทุก string ต้องผ่านคู่
    ผู้แปล+ผู้ตรวจ; คำแปล v1.2 ใส่มากับ batch ในช่อง "ref_tm" เป็นร่างให้ผู้แปลพิจารณา
    (ดี=เก็บ, เพี้ยน=เขียนใหม่) — ผู้แปลต้องกรอก "strings" เองทุก key เสมอ
  - string ที่อยู่ใน master_th.json แล้ว (ผ่าน merge_qc จาก sprint ก่อน) จะไม่ถูกจัดเข้า batch ใหม่

รันซ้ำได้ (idempotent): ก่อน re-chunk เก็บเกี่ยวคำแปลที่กรอกไว้ใน batch เดิมเข้า master_th ก่อน
แล้วลบ batch เก่าทิ้งค่อยจัดใหม่ (เลข batch เลื่อนได้ — อย่าอ้างเลข batch ข้าม sprint)
"""

# ---- ตัวกันรันผิดไฟล์ ----
# ไฟล์นี้เป็นของโปรเจกต์ Lost Judgment ที่ copy มาไว้อ่านเทียบ ยังไม่ได้พอร์ตมาที่ Ishin
# (มันอ่าน extracted/unique_strings.json ซึ่งภาคนี้ไม่มี และเขียนทับ batch/บริบทของจริงได้)
import sys as _sys
_sys.stderr.reconfigure(encoding="utf-8")   # กติกาข้อ 5
_sys.exit("หยุด: ไฟล์นี้ยังเป็นของ Lost Judgment ยังไม่ได้พอร์ต — ใช้ make_worklist_ishin.py / make_batch_context_ishin.py แทน")

import io
import json
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")  # กัน cp1252
sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import EXTRACTED, MASTER_TH, TRANSLATIONS, WORKLIST  # noqa: E402

# ใช้ TM จากโปรเจกต์เก่า (อ่านอย่างเดียว) เป็นร่าง ref — ไม่ auto-fill
# ลำดับความน่าเชื่อ: Gaiden (ใหม่สุด + Kiryu เป็นตัวเอกเหมือนกัน) > Y8 > Y7 > Pirate > K2R
TM_SOURCES = [  # ตัวแรกในลิสต์ที่มี key ชนะ (ลำดับตาม glossary priority ของ CLAUDE.md)
    # Judgment ภาคแรกอยู่บนสุดสำหรับภาคนี้: ตัวละคร/องค์กร/ศัพท์กฎหมายเป็นชุดเดียวกันทั้งซีรีส์
    # (ยังเป็น "ร่างอ้างอิง" เท่านั้น — ห้าม auto-fill เข้า master_th เหมือนเดิม)
    (Path("D:/Projects/lost-judgment-thai/translations/tm_judgment.json"), "judgment"),
    (Path("D:/Projects/yakuza-kiwami-3/translations/master_th.json"), "k3"),
    (Path("D:/Projects/yakuza-gaiden/translations/master_th.json"), "gaiden"),
    (Path("D:/Projects/yakuza-6-thai/translations/master_th.json"), "y6"),
    (Path("D:/Projects/y8-infinite-wealth/translations/master_th.json"), "y8"),
    (Path("D:/Projects/yakuza-7-like-a-dragon-thai/translations/master_th.json"), "y7"),
    (Path("D:/Projects/pirate-yakuza-hawaii-thai/translations/master_th.json"), "pirate"),
    (Path("D:/Projects/yakuza-kiwami-2-mod/translations/master_th.json"), "k2r"),
]


def load_tm():
    tm = {}
    for p, label in TM_SOURCES:
        if not p.exists():
            print(f"!! TM ไม่พบ: {label} ({p})")
            continue
        d = json.load(open(p, encoding="utf-8"))
        added = 0
        for en, th in d.items():
            if en not in tm and isinstance(th, str) and th.strip():
                tm[en] = th
                added += 1
        print(f"TM {label}: +{added:,} (รวม {len(tm):,})")
    return tm

UNIQUE_JSON = EXTRACTED / "unique_strings.json"
BY_BIN_JSON = EXTRACTED / "strings_by_bin.json"
REPORT_MD = TRANSLATIONS / "worklist_report.md"

BATCH_SIZE = 250

# tier ต่ำ = ทำก่อน (credits คง EN ทั้ง bin ตามบทเรียน K2R — ดันท้ายคิว)
TIER6_DEFER = {"credits.bin"}

# bin ที่ไม่ส่งเข้าคิวแปลเลย — ข้อความในนั้นเป็น identifier/ชื่อ object ไม่ใช่ข้อความที่ผู้เล่นเห็น
# (ตรวจแล้วจาก docs/research.md §3 — extractor ปล่อยผ่านมาเพราะเป็นคำอังกฤษล้วน)
DENY_BINS = {
    "minigame_rail_shooter_stage_object.bin",
    "minigame_rail_shooter_doll_z_head_node.bin",
    "character_npc_soldier_name_group.bin",   # ชื่อสกุลญี่ปุ่นดิบสำหรับสุ่ม NPC
    "sound_se_name_table.bin", "sound_cuesheet_info.bin", "sound_voice_table.bin",
    "motion_behavior_info.bin", "scene_config.bin", "timeline.bin",
    "ui_animation_all.bin", "ui_layer_all.bin", "ui_crop_all.bin", "ui_scene_property.bin",
    "character_model_model_data.bin", "character_model_model_data_judge.bin",
    # เพิ่ม 21 ส.ค. 2026 (ผู้ตรวจ batch_118 ยืนยัน): ทั้งไฟล์เป็น rig/bone identifier
    # (scratch/grip/hold/punch/standby + face) ไม่มีข้อความแสดงผลปนเลย
    "minigame_picking_job_picking_job.bin",
    # เพิ่ม 27 ส.ค. 2026 (ผู้ตรวจ batch_166 ยืนยันรายคีย์ · sprint 18): ตระกูล rail_shooter doll_*
    # เป็น rig/bone identifier ชุดเดียวกัน (scratch/grip/hold/punch/standby · [ss] · face)
    # ตกหล่นจากรอบ 21 ส.ค. เพราะชื่อไฟล์ไม่มี `_z_` — คีย์ 31+2 ตัวหลุดเข้า worklist ของ b166 ไปแล้ว
    # (แก้เฉพาะหน้าโดยให้คงต้นฉบับ th == en · กันไม่ให้หลุดอีกตอน re-chunk ครั้งหน้า)
    "minigame_rail_shooter_doll_hand.bin", "minigame_rail_shooter2_doll_hand.bin",
    "minigame_rail_shooter_doll_lod.bin", "minigame_rail_shooter2_doll_lod.bin",
    "minigame_rail_shooter_doll_node.bin", "minigame_rail_shooter2_doll_node.bin",
    "minigame_rail_shooter2_telop_text.bin", "minigame_robot_map.bin",
    # เพิ่ม 21 ส.ค. 2026 (นักแปล batch_123 ยืนยันรายคีย์): พารามิเตอร์เอฟเฟกต์เอนจิ้นล้วน
    # (blob ไบนารี · รหัสเอฟเฟกต์ 3 ตัวอักษร · ค่า weak/normal/strong) ไม่ใช่ข้อความแสดงผล
    "effect_body_damage.bin", "effect_character_use_effect.bin",
    "effect_charge_dust_generator.bin", "effect_splash_liquid_param.bin",
    # เพิ่ม 21 ส.ค. 2026 (ผู้ตรวจ batch_120 ยืนยันรายคีย์): enum/ค่าระบบล้วน
    "access_type.bin", "ai_param.bin", "camera_shake.bin",
    # เพิ่ม 21 ส.ค. 2026 (นักแปล batch_125 ยืนยันรายคีย์): ชื่อรูปทรง/สไตล์กล้อง enum ล้วน
    "post_effect_dof_shapes.bin", "post_effect_glare_shapes.bin",
    # เพิ่ม 25 ส.ค. 2026 (Lost Judgment — ยืนยันจาก extracted/strings_by_bin.json):
    # ภาคนี้มีมินิเกม rail shooter สองชุด (_1 กับ _2) โครงเหมือนกันเป๊ะ ทั้งสองชุดเป็น
    # identifier ของโมเดล/โหนดกระดูก ([inst_000][high]model · [l]face_l) ไม่ใช่ข้อความบนจอ
    "minigame_rail_shooter2_stage_object.bin",
    "minigame_rail_shooter2_doll_z_head_node.bin",
    "minigame_rail_shooter_doll_z_head.bin", "minigame_rail_shooter_doll_z_body.bin",
    "minigame_rail_shooter_doll_z_top.bin", "minigame_rail_shooter_doll_z_bottom.bin",
    "minigame_rail_shooter2_doll_z_head.bin", "minigame_rail_shooter2_doll_z_body.bin",
    "minigame_rail_shooter2_doll_z_top.bin", "minigame_rail_shooter2_doll_z_bottom.bin",
    # เพิ่ม 28 ส.ค. 2026 (lead ยืนยันรายคีย์ก่อนเปิด sprint 19): ทั้งห้าไฟล์เป็น identifier ล้วน
    # · character_character_data(.bin/_judge) + character_tex_chunk = id ตัวละครแบบโรมาจิพิมพ์เล็ก
    #   (mamiya · yagami · saibanchoA · firemanB) ไม่ใช่ชื่อที่แสดงบนจอ (ชื่อจริงอยู่ talk_talker/ui)
    # · character_primitive_texture_info = ชื่อ material/mesh ([l0]f01_eye_8 · sd_o1dzt[skin])
    # · font2_character_set = สตริงชุดอักขระของฟอนต์ (ห้ามแตะเด็ดขาด — แก้แล้วฟอนต์พัง)
    # หลุดเข้า worklist ของ b174/b175/b176 ไปแล้ว 152 คีย์ → รอบนี้ให้คงต้นฉบับ (th == en)
    "character_character_data.bin", "character_character_data_judge.bin",
    "character_tex_chunk.bin", "character_primitive_texture_info.bin",
    "font2_character_set.bin",
    # เพิ่ม 28 ส.ค. 2026 (ผู้ตรวจ b178 ยืนยัน · lead ตรวจซ้ำ): ทั้ง 37 คีย์เป็น **ข้อมูลรีเพลย์ไบนารี**
    # ของเครื่องเกมย้อนยุคจำลอง (สตริงยาว 34,616-131,072 ตัวอักษร · ไม่มีข้อความปนเลย · ไม่โผล่ใน bin อื่น)
    # หลุดเข้า worklist ของ b178 ไปแล้ว 37 คีย์ → รอบนี้ให้คงต้นฉบับ (th == en)
    "m3e_replay.bin",
    # เพิ่ม 28 ส.ค. 2026 (lead ยืนยันรายคีย์ก่อนเปิด sprint 20): identifier ล้วนอีกสามไฟล์
    # · motion_face_target = รหัส FACS ของกล้ามเนื้อใบหน้า (`AU01_L  Inner Brow Raiser`)
    # · particle_overwrite_param_list = รหัสพารามิเตอร์ 3 ตัวอักษร (`QSr` · `ODl`)
    # · scene_preload_st_yokohama_tex = พาธไฟล์ par ของฉาก (`file_area_bg/.../tex_archive_0_area_tex[l].par`)
    # หลุดเข้า worklist ของ b179 (88) · b180 (14) · b186 (41) · b187 (41) = 184 คีย์ → รอบนี้ให้คงต้นฉบับ
    "motion_face_target.bin", "particle_overwrite_param_list.bin",
    "scene_preload_st_yokohama_tex.bin",
    # เพิ่มรอบสอง 28 ส.ค. 2026 (ผู้ตรวจ b180/b186 ยืนยันรายคีย์ · lead ตรวจซ้ำ):
    # · scene_preload_effect_chara_bep = ชื่อไฟล์ .bep ของเอฟเฟกต์ (`JudgeGirlFndGood.bep`)
    # · rumble.bin = enum ของระบบสั่น (`linear` · `LightBar` · `BigMotor`)
    # · particle_mild_list = รหัสพารามิเตอร์ 3 ตัวอักษรชุดเดียวกับ particle_overwrite_param_list (`DDb` · `YNb`)
    "scene_preload_effect_chara_bep.bin", "rumble.bin", "particle_mild_list.bin",
    # เพิ่มรอบสาม 28 ส.ค. 2026 (ผู้ตรวจ b187/b188 ยืนยัน · lead เปิดไฟล์ดูเอง):
    # ตระกูล talk_party_* = ข้อมูลเครื่องมือทดสอบระบบ "แชตปาร์ตี้" ของยุค Y7 ที่ LJ ไม่มีฟีเจอร์นี้
    # (คีย์ชี้ชัด: `Coyoteパーティーチャットテスト` · `Kasuga and the Party` · ชื่อโมชัน `怒る　ST`)
    # เป็นเมทาดาทาของ editor ไม่ใช่ข้อความบนจอ · stage_instance_parts_enable_opaque_shader = ชื่อ shader
    "talk_party_chat_list.bin", "talk_party_talk_character.bin",
    "talk_party_talk_character_kind.bin", "talk_party_talk_expression.bin",
    "talk_party_talk_general_setting.bin", "talk_party_talk_list.bin",
    "talk_party_talk_motion.bin", "stage_instance_parts_enable_opaque_shader.bin",
    # เพิ่มรอบสี่ 28 ส.ค. 2026 (นักแปล b188 ยืนยัน · lead เปิดไฟล์ดูเอง):
    # · sound_movie_info(_judge) = รหัส viseme ลิปซิงค์ 3 ตัวอักษร (`bed` · `blk` · `hat` · `BED` · `BLK`)
    # · sound_category = enum ระบบสตรีมเสียง (`ZeroLatencyStream` · `LOW` · `MIDDLE` · `pack`)
    "sound_movie_info.bin", "sound_movie_info_judge.bin", "sound_category.bin",
}

# bin ที่ "คงภาษาอังกฤษ" ตามกติกาเหล็กข้อ 10 (license/EULA/credits/เครื่องหมายการค้า)
KEEP_EN_BINS = {
    "credits.bin", "pause_license.bin", "pause_siea_eula.bin", "pause_siee_eula.bin",
    "platform_term.bin",
    # เพิ่ม 22 ส.ค. 2026: คำสั่งแชตของมินิเกม live chat เป็นโรมาจิญี่ปุ่นล้วน (AIDAYO,
    # AKIRAMENNNAYO ...) ผู้เล่นพิมพ์ตามตัวอักษร — แปลไม่ได้ ต้องคง EN
    "minigame_live_chat_chat_commands.bin",
    # เพิ่ม 25 ส.ค. 2026 (คำตัดสินผู้ใช้): **ชื่อบทคงอังกฤษไว้ก่อน**
    # สองไฟล์นี้เป็นชื่อบทล้วน จึงคง EN ทั้ง bin ได้เลย
    "chapter.bin", "title_movie_chapter.bin",
    # เพิ่ม 29 ส.ค. 2026 (คำตัดสินผู้ใช้หลังเห็นบนจอ · docs/ISSUES.md LJ-005):
    # ข้อความในไฟล์นี้บางส่วนถูกแสดงผ่าน **กล่อง MessageBox ของ Windows** ซึ่งวาดด้วย
    # ฟอนต์ระบบ ไม่ใช่ฟอนต์ในเกม ไบต์ donor ที่เราเขียนลงไปจึงขึ้นเป็นตัวละตินดิบเสมอ
    # อ่านไม่ออกทั้งกล่อง และ **ฉีดฟอนต์ยังไงก็แก้ไม่ได้** เพราะอยู่นอกระบบวาดข้อความของเกม
    # เนื้อหาทั้ง 28 สตริงเป็นข้อความระดับระบบล้วน (พื้นที่จัดเก็บ · ถ้วยรางวัล · คอนโทรลเลอร์ ·
    # ออกจากระบบ · อัปเดต) คุณค่าในการแปลต่ำ ความเสี่ยงอ่านไม่ออกสูง จึงคง EN ทั้ง bin
    "message_dialog.bin",
}

# คอลัมน์ที่ต้องคง EN แม้ bin นั้นแปลได้ — ค่าในคอลัมน์เป็น **identifier ที่เอนจิ้นใช้ค้นหา**
# ไม่ใช่ข้อความบนจอ แต่สะกดเป็นคำอังกฤษธรรมดาจนหลุดเข้า worklist ไปได้
# (พบ 29 ส.ค. 2026 ตอนไล่หาสาเหตุอาการ "ตกแมพ" — สแกนทุก bin ที่ deploy หาค่ารูป snake_case
#  ที่ถูกแปลไปแล้ว) แปลคอลัมน์พวกนี้ = เอนจิ้นหาสิ่งที่อ้างถึงไม่เจอ → พฤติกรรมพัง ไม่ใช่แค่ข้อความเพี้ยน
#
# ⚠ อันตรายสุดคือ `position_stage_warp.spc_pos_name` = ชื่อจุดเกิดในฉาก ถ้าหาไม่เจอผู้เล่นจะถูก
#   วางที่พิกัดตั้งต้นของฉาก ซึ่งมักอยู่ **ใต้พื้น** → ตกแมพ
KEEP_EN_COLUMNS = {
    "position_stage_warp.bin": {"spc_pos_name"},          # ชื่อจุดเกิดในฉาก (sugoroku/battle_start/survivor_in)
    "scene.bin": {"class_name"},                          # ชื่อคลาสซีน 224 ค่า (scene_action_first_tenkaichi)
    "effect_graffiti_category.bin": {"path"},             # พาธทรัพยากรเอฟเฟกต์
    "minigame_snack_talk_event.bin": {"talk_type", "after_talk_event"},   # enum (auto/button_maru · next/end)
    "minigame_snack_character_info.bin": {"kind"},        # enum (character/invisible)
    "minigame_darts_pattern.bin": {"type"},               # enum (absolute/relative)
    "minigame_dance_difficulty.bin": {"score_name"},      # คีย์ asset (ex_easy/easy/normal/hard)
                                                          # ป้ายที่โชว์จริงอยู่คอลัมน์ label_name
    "player_point.bin": {"format"},                       # คีย์รูปแบบตัวเลข (kilometer)
    "game_event_model_activity_outcome.bin": {"name"},    # enum (completed/failed/abandoned)
}

# string ที่คง EN แม้อยู่ใน bin ที่ต้องแปล (ใช้เมื่อ bin นั้นมีทั้งของที่แปลและไม่แปลปนกัน)
# ชื่อบท: `mission_title.bin` มีทั้ง **ชื่อบท** (คง EN) และ **เรื่องย่อของบท** (ต้องแปล) ในไฟล์เดียว
KEEP_EN_STRINGS = [
    re.compile(r"^\s*(Chapter\s*\d+|Final Chapter|Finale)\s*[:\-]", re.I),
    re.compile(r"^\s*The Kaito Files\s*-\s*Chapter\s*\d+\s*[:\-]", re.I),
    # ป้ายสั้น "Chapter 1" / "Final Chapter" (activity_activity.bin · manual.bin)
    # คง EN ให้เข้าชุดกับชื่อบทที่คง EN — ถ้าภายหลังตัดสินแปลชื่อบท ต้องลบสองบรรทัดนี้ด้วย
    re.compile(r"^\s*Chapter\s*\d+\s*$", re.I),
    re.compile(r"^\s*(Final Chapter|Finale)\s*$", re.I),
    # เพิ่ม 27 ส.ค. 2026 (ผู้ตรวจ batch_155 · sprint 18): การ์ดชื่อบทใน `ui_texture_text.bin`
    # ห่อด้วยแท็กจนตัวคัดเดิม (anchored ^) จับไม่ได้ → หลุดเข้า worklist 17 คีย์
    re.compile(r"chapter_texture_(header|number)", re.I),
]


def keep_en_string(s):
    return any(rx.search(s) for rx in KEEP_EN_STRINGS)

TIER_NAMES = {
    1: "caption (ซับสั้นบนจอ)",
    2: "auth/sound_auth (บทคัตซีน)",
    3: "msg/pause_message/message dialog",
    4: "item/ui/title/help/manual/map/talk_talker",
    5: "minigame/drone",
    6: "rest",
    7: "talk-only (บทสนทนาเดินเมือง)",
}


def bin_tier(bin_name: str) -> int:
    b = bin_name.lower()
    if b == "caption.bin":
        return 1
    if b in ("auth.bin", "sound_auth.bin"):
        return 2
    if b in ("msg.bin", "pause_message.bin") or b.startswith(("message_", "explanation_", "loading_")):
        return 3
    if (b in ("item.bin", "talk_talker.bin", "manual.bin", "help.bin")
            or b.startswith(("item_", "ui", "title_", "help", "tips", "manual", "map_",
                             "evidence", "mission_", "complete", "player_skill"))):
        return 4
    if b.startswith(("minigame_", "drone_")):
        return 5
    if b == "talk.bin":
        return 7
    return 6


def string_tier(bins: list) -> tuple:
    return min((bin_tier(b), b) for b in bins)


def tier6_sort_key(bin_name: str):
    return (1 if bin_name in TIER6_DEFER else 0, bin_name)


def word_count(s: str) -> int:
    return len(re.sub(r"<[^>]*>", " ", s).split())


def load_json(p: Path):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump_json(obj, p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def main():
    unique = load_json(UNIQUE_JSON)      # {EN: {count, bins[]}}
    by_bin = load_json(BY_BIN_JSON)      # {bin: [EN,...]}
    legacy = load_tm()   # ร่างอ้างอิงจาก Y7/Pirate/K2R — ไม่ใช่คำตอบ ผู้แปลพิจารณาใหม่ทุกตัว

    # ---- master_th (ของ rework) + เก็บเกี่ยวคำแปลที่ค้างใน batch เดิม ------
    master_th = load_json(MASTER_TH) if MASTER_TH.exists() else {}
    harvested = 0
    WORKLIST.mkdir(parents=True, exist_ok=True)
    # ข้ามไฟล์บริบท (batch_NNN.context.json) — เป็นไฟล์คู่ที่ make_batch_context.py สร้าง
    # ไม่ใช่ batch คำแปล · ถูกลบทิ้งพร้อมกันตอน re-chunk แล้วสร้างใหม่ทีหลัง
    old_batches = sorted(b for b in WORKLIST.glob("batch_*.json")
                         if not b.name.endswith(".context.json"))
    for bf in old_batches:
        try:
            data = load_json(bf)
        except (json.JSONDecodeError, OSError):
            print(f"!! ข้าม batch เสีย: {bf.name}")
            continue
        for en, th in data.get("strings", {}).items():
            if isinstance(th, str) and th.strip() and not master_th.get(en):
                master_th[en] = th
                harvested += 1
    for bf in old_batches:
        bf.unlink()
    for cf in WORKLIST.glob("batch_*.context.json"):
        cf.unlink()      # บริบทเก่าอ้าง batch ที่หายไปแล้ว — รัน make_batch_context.py ใหม่หลังจากนี้

    # ---- จัด tier ให้ string ที่ยังไม่มีใน master_th ------------------------
    remaining = []  # (tier, primary_bin, orig_index, EN)
    denied = keep_en = 0
    for idx, (en, meta) in enumerate(unique.items()):
        if master_th.get(en):
            continue
        bins_ok = [b for b in meta["bins"] if b not in DENY_BINS]
        if not bins_ok:          # string นี้อยู่แต่ใน bin ที่ไม่แปล
            denied += 1
            continue
        # string ที่อยู่เฉพาะใน bin "คง EN" (credits/EULA/license) — build_text ข้ามอยู่แล้ว
        # ถ้าปล่อยเข้าคิวจะเสียแรงทีมแปลฟรี ๆ (ภาคนี้ = credits.bin 1,718 string)
        if all(b in KEEP_EN_BINS for b in bins_ok) or keep_en_string(en):
            keep_en += 1
            continue
        tier, primary = min((bin_tier(b), b) for b in bins_ok)
        remaining.append((tier, primary, idx, en))

    def sort_key(item):
        tier, primary, idx, _ = item
        if tier == 6:
            return (tier, tier6_sort_key(primary), idx)
        return (tier, (0, primary), idx)

    remaining.sort(key=sort_key)
    normal = [r for r in remaining if r[0] != 7]
    talk = [r for r in remaining if r[0] == 7]

    # ---- เขียน batch (มี ref_tm = คำแปลเดิมให้พิจารณา ไม่ใช่คำตอบ) --------
    ref_hits = 0

    def write_batches(items, name_fmt):
        nonlocal ref_hits
        n_batch, seq = 0, 1
        groups, cur_tier, cur = [], None, []
        for it in items:  # ตัด batch ไม่ให้คร่อม tier
            if it[0] != cur_tier and cur:
                groups.append((cur_tier, cur))
                cur = []
            cur_tier = it[0]
            cur.append(it)
        if cur:
            groups.append((cur_tier, cur))
        for tier, group in groups:
            for i in range(0, len(group), BATCH_SIZE):
                chunk = group[i:i + BATCH_SIZE]
                ens = [en for _, _, _, en in chunk]
                ref = {en: legacy[en] for en in ens if legacy.get(en)}
                ref_hits += len(ref)
                payload = {
                    "priority": tier,
                    "source_bins": sorted({b for en in ens for b in unique[en]["bins"]}),
                    "strings": {en: "" for en in ens},
                    "ref_tm": ref,
                }
                dump_json(payload, WORKLIST / (name_fmt % seq))
                seq += 1
                n_batch += 1
        return n_batch

    n_normal_batches = write_batches(normal, "batch_%03d.json")
    n_talk_batches = write_batches(talk, "batch_TALK_%03d.json")

    dump_json(master_th, MASTER_TH)

    # ---- report -------------------------------------------------------------
    tier_counts = {}
    for tier, _, _, _ in remaining:
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    words_normal = sum(word_count(en) for _, _, _, en in normal)
    words_talk = sum(word_count(en) for _, _, _, en in talk)

    key_bins = ["caption.bin", "auth.bin", "sound_auth.bin", "message_dialog.bin",
                "msg.bin", "item.bin", "ui_text.bin", "title_root.bin",
                "map_area.bin", "talk.bin", "credits.bin"]
    lines = []
    a = lines.append
    a("# Worklist Report — Lost Judgment (make_worklist.py)")
    a("")
    a(f"- unique strings ทั้งเกม: **{len(unique):,}**")
    a(f"- อยู่ใน master_th แล้ว (ผ่าน QC): {len(unique) - len(remaining):,} "
      f"(เก็บเกี่ยวจาก batch เดิมรอบนี้ {harvested:,})")
    a(f"- เหลือจัดเข้า batch: **{len(remaining):,}** "
      f"(normal {len(normal):,} / talk-only {len(talk):,})")
    a(f"- batch: **{n_normal_batches}** normal + **{n_talk_batches}** TALK "
      f"(≤{BATCH_SIZE} strings/batch)")
    a(f"- มีร่างอ้างอิง v1.2 (`ref_tm`): {ref_hits:,} strings "
      f"— **ไม่ใช่คำตอบ** ผู้แปลต้องพิจารณาใหม่ทุกตัว")
    a(f"- ปริมาณงาน: ~{words_normal + words_talk:,} คำ EN "
      f"(normal {words_normal:,} / talk {words_talk:,})")
    a("")
    a("| priority | ความหมาย | strings |")
    a("|---:|---|---:|")
    for t in sorted(tier_counts):
        a(f"| {t} | {TIER_NAMES[t]} | {tier_counts[t]:,} |")
    a("")
    a("## bin สำคัญ")
    a("")
    a("| bin | strings |")
    a("|---|---:|")
    for b in key_bins:
        if by_bin.get(b):
            a(f"| {b} | {len(by_bin[b]):,} |")
    a("")
    a("สร้างโดย `scripts/make_worklist.py` — รันซ้ำได้ (harvest ก่อน re-chunk)")
    a("")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8", newline="\n")

    print(f"unique={len(unique):,} มีใน master_th แล้ว={len(unique) - len(remaining) - denied - keep_en:,} "
          f"ตัดทิ้งเพราะอยู่ใน DENY_BINS={denied:,} คง EN={keep_en:,} "
          f"เหลือแปล={len(remaining):,} (normal {len(normal):,}/talk {len(talk):,})")
    print(f"batches: {n_normal_batches} normal + {n_talk_batches} TALK | "
          f"ref_tm hits {ref_hits:,}")
    print(f"-> {WORKLIST}")
    print(f"-> {REPORT_MD}")


if __name__ == "__main__":
    main()
