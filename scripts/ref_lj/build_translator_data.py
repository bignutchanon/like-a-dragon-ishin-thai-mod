#!/usr/bin/env python3
"""รันสายข้อมูลนักแปลทั้งชุดตามลำดับที่ถูกต้อง (ลำดับสำคัญ — แต่ละขั้นกินผลของขั้นก่อน)

    extract_all_en          สกัด string ทั้งเกม (ช้าสุด ~3 นาที · ข้ามได้ถ้า JSON ครบแล้ว)
      -> make_translator_facts / make_bin_index
      -> make_story_context         เรื่องย่อรายบท + แฟ้มคดีในเกม (ใช้เป็นทั้งบริบทและหลักฐานเพศ)
      -> make_gender_table          เพศจาก sound_voicer.bin (หลักฐานชั้นดีที่สุด)
      -> make_speaker_map           ผู้พูดจากคีย์เสียง (ของเดิม — เก็บไว้เป็นหลักฐานเสริม)
      -> make_speech_speaker  (1)   ผู้พูดรายบรรทัดของคัตซีน
      -> make_talk_speaker    (1)   ผู้พูดรายบรรทัดของบทเดินเมือง
      -> make_auth_speaker    (1)   ผู้พูดรายบรรทัดของซับทับคัตซีน (auth.bin)
      -> make_cue_gender            เพศจากชื่อคิวเสียง -> sound_voicer (ครอบคลุมเกือบทุกบรรทัดคัตซีน)
      -> make_speaker_aliases       ยุบ id ของ voicer กับชื่อที่แสดงบนจอที่เป็นคนเดียวกัน
      -> harvest_gender_evidence    รวมหลักฐานเพศทั้งหมด -> gender_evidence.json
      -> make_speech_speaker  (2)   รันซ้ำเพื่อเติมเพศที่เพิ่งพิสูจน์ได้
      -> make_talk_speaker    (2)   เช่นกัน
      -> make_auth_speaker    (2)   เช่นกัน
      -> make_characters_seed       แฟ้มตัวละคร + สรรพนามตั้งต้น
      -> make_name_proposals        ร่างชื่อไทย (คำล็อก > TM ภาคก่อน > กฎทับศัพท์)
      -> make_glossary_seed         ตารางชื่อ 2,000+ รายการ + คำที่ภาคก่อนล็อกไว้
      -> make_worklist              จัดคิวแปลเป็น batch
      -> make_batch_context         แนบผู้พูด/เพศ/ธง neutral ให้ทุก batch

(1)/(2) = ต้องรันสองรอบเพราะเพศของผู้พูดมาจาก harvest ที่ต้องใช้รายชื่อผู้พูดจากรอบแรก

ใช้:
  python scripts/build_translator_data.py            # ทั้งสาย (ข้าม extract ถ้ามี JSON แล้ว)
  python scripts/build_translator_data.py --extract  # บังคับสกัด string ใหม่
  python scripts/build_translator_data.py --no-worklist   # ไม่แตะคิวแปล (กันลบ batch ที่ทีมกำลังทำ)
"""
import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

PY = sys.executable
SCRIPTS = paths.SCRIPTS

STEPS_FACTS = [
    ("make_translator_facts.py", []),
    ("make_bin_index.py", []),
    ("make_story_context.py", ["--write"]),   # เรื่องย่อรายบท + แฟ้มคดี (ต้องมาก่อน characters_seed)
    ("make_gender_table.py", ["--write"]),
    ("make_speaker_map.py", []),
    ("make_speech_speaker.py", ["--write"]),
    ("make_talk_speaker.py", ["--write"]),
    ("make_auth_speaker.py", ["--write"]),
    ("make_cue_gender.py", ["--write"]),
    ("make_speaker_aliases.py", ["--write"]),
    ("harvest_gender_evidence.py", ["--write"]),
    ("make_speech_speaker.py", ["--write"]),
    ("make_talk_speaker.py", ["--write"]),
    ("make_auth_speaker.py", ["--write"]),
    ("make_characters_seed.py", ["--write"]),
    ("make_name_proposals.py", ["--write", "--min-lines", "20"]),
    ("make_glossary_seed.py", ["--write"]),
]
STEPS_WORKLIST = [
    ("make_worklist.py", []),
    ("make_batch_context.py", ["--write"]),
]


def run(script, args):
    t0 = time.time()
    print("\n=== %s %s" % (script, " ".join(args)), flush=True)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    res = subprocess.run([PY, str(SCRIPTS / script)] + args, env=env)
    print("--- %s -> exit %d (%.0fs)" % (script, res.returncode, time.time() - t0), flush=True)
    return res.returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--extract", action="store_true", help="รัน extract_all_en.py ใหม่ทั้งหมด")
    ap.add_argument("--no-worklist", action="store_true",
                    help="ไม่รัน make_worklist/make_batch_context (กันลบ batch ที่ทีมกำลังแปลอยู่)")
    a = ap.parse_args()

    if not (paths.EXTRACTED / "unique_strings.json").exists() or a.extract:
        if run("extract_all_en.py", ["--bins-dir", str(paths.DB_EN)]):
            print("!! extract ล้มเหลว — หยุด")
            return 1

    steps = list(STEPS_FACTS) + ([] if a.no_worklist else list(STEPS_WORKLIST))
    failed = [s for s, args in steps if run(s, args)]
    if failed:
        print("\n!! ขั้นที่ล้มเหลว: %s" % ", ".join(failed))
        return 1
    print("\nเสร็จทั้งสาย — ข้อมูลนักแปลพร้อมใช้")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
