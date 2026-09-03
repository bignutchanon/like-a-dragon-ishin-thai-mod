#!/usr/bin/env python3
"""ด่านตรวจ: บทพูดที่ซ่อนอยู่ในก้อน priority 3 ต้องใช้ภาษายุค ไม่ใช่ภาษาเมนู

ที่มาของปัญหา (คลื่น 030-041): ชั้น priority 3 ถือกันว่าเป็น "เมนู/ระบบ" จึงใช้ภาษาไทย
ปัจจุบันได้ และด่าน M ของ `merge_qc.py` ก็ยกเว้นชั้นนี้ไว้ — แต่ในชั้นนี้มีสตริงที่เป็น
**คำพูดของตัวละครในยุค** ปนอยู่หลายร้อยบรรทัด (นักพนันโปกเกอร์ · คนในโรงมาจง · ช่างตีเหล็ก
· จดหมาย · เสียงพูดตอนเดินถนน · บทสัตว์เลี้ยง) ถ้าแปลด้วย ผม/คุณ/ครับ/ค่ะ จะผิดทั้งชุด
และไม่มีด่านไหนจับได้เลย

ตัวตรวจนี้จึงระบุ "แหล่งที่เป็นบทพูด" จากไฟล์เกมจริง (locres namespace + ตาราง ARMP)
แล้วตรวจเฉพาะบรรทัดที่มาจากแหล่งเหล่านั้น

ใช้:
  python scripts/check_speech_layer.py --only 037
  python scripts/check_speech_layer.py            # ทุกก้อนที่มีไฟล์ done
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402
import thai_pronouns as TP  # noqa: E402

# locres namespace ที่เป็นบทพูด — ตรวจจากตัวอย่างจริงในไฟล์เกม ไม่ใช่เดาจากชื่อ
SPEECH_NS_PREFIX = (
    "poker_computre_",      # บทพูดนักพนันโปกเกอร์ (bluff · game · retire)
    "pet_text_",            # บทพูดตอนเล่นกับหมา/แมว
    "walk_",                # เสียงคนเดินถนนแต่ละย่าน
    "mail_text_",           # จดหมาย
    "minigame_chohan_",     # เสียงเจ้ามือโชฮัง
    "poker_computre",
)
SPEECH_NS_EXACT = {
    "mail_sender", "minigame_mahjong", "minigame_shogi", "minigame_udon",
    "minigame_drink", "walk_drunkard",
}

# ตาราง ARMP ที่ช่องข้อความเป็นบทพูด
SPEECH_ARMP = {
    "blacksmith_blacksmith_message": ("blacksmith_message",),
    "sound_speak_data": ("message",),
    "pause_msg_taiken": ("text",),
}

# คำล็อกที่มี "คุณ/ผม/ค่ะ" อยู่ข้างในและถูกต้องแล้ว — ห้ามนับเป็นภาษาสมัยใหม่
ALLOW = re.compile(r"คุณภาพ|คุณลักษณะ|คุณสมบัติ|คุณูปการ|สรรพคุณ|เจ้าค่ะ|เจ้าคะ|"
                   r"ทรงผม|เส้นผม|มวยผม|กระผม|"
                   # คำไทยปกติที่ซับสตริงไปชนคำยืมในรายการ MODERN_LOANWORDS
                   r"ดีล่ะ|ยินดีลอง|มินิเกม")


def load_speech_strings():
    """เซตของสตริง EN ที่มาจากแหล่งซึ่งเป็นบทพูด"""
    out = set()
    locres = paths.EXTRACTED / "locres" / "Game.en.json"
    if locres.exists():
        d = json.load(io.open(locres, encoding="utf-8"))
        strings = d["strings"]
        for nsd in d["namespaces"]:
            ns = nsd["ns"]
            if ns in SPEECH_NS_EXACT or ns.startswith(SPEECH_NS_PREFIX):
                for e in nsd["entries"]:
                    out.add(strings[e["idx"]])
    db = paths.EXTRACTED / "db_en"
    for table, cols in SPEECH_ARMP.items():
        p = db / f"{table}.bin.json"
        if not p.exists():
            continue
        d = json.load(io.open(p, encoding="utf-8"))
        for key, row in d.items():
            if not isinstance(row, dict):
                continue
            for col in cols:
                v = row.get(col)
                if isinstance(v, str) and v.strip():
                    out.add(v)
    return out


def modern_hits(th):
    """คืน (คำที่ตก, คำที่เตือน) — คำยืมเป็นแค่ 'เตือน' เพราะจับด้วย substring แล้วชนคำไทยปกติ
    ("ยินดีลองดู" มี "ดีล" · "มินิเกม" มี "เกม") — ตรงกับที่ thai_pronouns.py จดไว้ว่าเป็นตัวเตือน
    """
    probe = ALLOW.sub("", th)
    hits = []
    for label, rx in (
        ("ผม", TP.RE_PHOM), ("คุณ", TP.RE_KHUN), ("ครับ", TP.RE_KHRAP),
        ("ค่ะ/คะ", TP.RE_KHA_MODERN), ("ฉัน", TP.RE_CHAN), ("ดิฉัน", TP.RE_DICHAN),
    ):
        if rx.search(probe):
            hits.append(label)
    warns = [w for w in TP.MODERN_LOANWORDS if w in probe]
    return hits, warns


def check(batch, speech):
    p = paths.TRANSLATIONS / "done" / f"batch_{batch}.done.json"
    if not p.exists():
        print(f"batch_{batch}: ยังไม่มีไฟล์ done")
        return 0, 0
    data = json.load(io.open(p, encoding="utf-8"))
    strings = data.get("strings", data)
    checked = 0
    bad = 0
    warned = []
    for en, th in strings.items():
        if en not in speech or not isinstance(th, str) or not th.strip():
            continue
        checked += 1
        hits, warns = modern_hits(th)
        if hits:
            bad += 1
            print(f"batch_{batch}  บทพูดแต่ใช้ภาษาปัจจุบัน ({' · '.join(hits)})")
            print(f"   EN: {en[:100]}")
            print(f"   TH: {th[:100]}")
        elif warns:
            warned.append((en, th, warns))
    for en, th, warns in warned:
        print(f"batch_{batch}  ⚠ อาจมีคำยืมสมัยใหม่ ({' · '.join(warns)}) — ตรวจด้วยตา")
        print(f"   TH: {th[:100]}")
    print(f"batch_{batch}: บรรทัดที่เป็นบทพูด {checked} · ตก {bad} · เตือน {len(warned)}")
    return checked, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    a = ap.parse_args()
    speech = load_speech_strings()
    print(f"สตริงที่มาจากแหล่งบทพูด (จากไฟล์เกม): {len(speech):,}")
    if a.only:
        batches = [a.only.zfill(3)]
    else:
        batches = [p.name[len("batch_"):-len(".done.json")]
                   for p in sorted((paths.TRANSLATIONS / "done").glob("batch_*.done.json"))]
    total = fails = 0
    for b in batches:
        c, f = check(b, speech)
        total += c
        fails += f
    print(f"\nรวม: ตรวจบทพูด {total} บรรทัด · ตก {fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
