#!/usr/bin/env python3
"""ทะเบียนผู้พูด + หลักฐานเพศ ของ Ishin! — ทุกบรรทัดมาจากไฟล์เกม ไม่มีการเดา

ภาคนี้ **ไม่มีตารางเพศในไฟล์เกม** (ต่างจาก Dragon Engine ที่มี `sound_voicer.bin` คอลัมน์ `sex`)
ตรวจครบทั้ง 244 ตาราง ARMP แล้วไม่มีคอลัมน์ sex/gender เลย · `TextBridge/AuthSpeaker/` เป็นแค่
ข้อความชื่อผู้พูด ไม่มีเมทาดาทา  → ต้องใช้หลักฐานทางอ้อมที่ยังอยู่ **ในไฟล์เกม** แทน

หลักฐานที่ใช้ (เรียงจากชี้ขาดที่สุด):
  A. **ต้นฉบับญี่ปุ่น** — pak เดียวกันมี `wdr_ja/msg` + `db.macan/ja` + `Game.locres` ภาษา ja ครบ
     ญี่ปุ่นทำเครื่องหมายเพศไว้ในสรรพนามบุรุษที่หนึ่งและคำลงท้าย ซึ่งอังกฤษตัดทิ้งหมด
     นับเฉพาะ **เครื่องหมายที่ผูกกับเพศแน่น** (ดูตาราง MARKERS) ตัวที่กำกวมไม่นับ
  B. ชื่อผู้พูดที่บอกเพศในตัวเอง (`Mother` · `Geisha` · `Boy`) — ตาราง ROLE_GENDER
  C. คิวเสียงที่ระบุตัวละครตรง ๆ ใน `sound_macan_cue_subtitle.bin`

เกณฑ์ตัดสิน (เข้มกว่าที่ควรไว้ก่อน — พลาดฝั่ง "ไม่รู้" ถูกกว่าพลาดฝั่งเดา):
  male/female = มีเครื่องหมายฝั่งเดียว >= MIN_HITS ครั้ง และฝั่งตรงข้าม <= อัตราส่วน MAX_CONTRA
  ที่เหลือทั้งหมด = unknown → **ต้องแปลกลางเพศ** ตามกติกา CLAUDE.md

ผลลัพธ์:
  translations/speakers.json               ทะเบียนรวม (เครื่องอ่าน)
  docs/reference/gender_evidence_ishin.md  หลักฐานรายคน (คนอ่าน)

ใช้: python scripts/build_speaker_gender.py
ต้องมีมาก่อน: scripts/build_parallel.py
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")   # console Windows = cp1252 (กติกาข้อ 5)
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                              # noqa: E402

MIN_HITS = 3          # ต้องเจอเครื่องหมายฝั่งที่ชนะอย่างน้อยกี่ครั้ง
MAX_CONTRA = 0.25     # ฝั่งตรงข้ามต้องไม่เกินสัดส่วนนี้ของฝั่งที่ชนะ

# ---- เครื่องหมายเพศในภาษาญี่ปุ่น (เฉพาะที่ผูกแน่น) --------------------------
# ที่ตัดออกโดยตั้งใจ เพราะกำกวม:
#   わたし/私   ใช้ได้ทั้งสองเพศ
#   わ ท้ายประโยค  ผู้ชายคันไซใช้ (Ishin มีสำเนียงคันไซเต็มไปหมด)
#   だな / かい   ผู้หญิงห้าวใช้ได้
#   うち          คันไซ ใช้ได้ทั้งสองเพศในยุคนี้
MARKERS = {
    "male": [
        (r"俺", "สรรพนาม 俺"),
        (r"オレ", "สรรพนาม オレ"),
        (r"儂|わし|ワシ", "สรรพนาม わし (ชายสูงวัย)"),
        (r"拙者", "สรรพนาม 拙者 (ซามูไร)"),
        (r"僕|ぼく|ボク", "สรรพนาม 僕"),
        (r"おいら|オイラ", "สรรพนาม おいら"),
        # ⚠ ต้องกัน「どうぞ。」(คำสุภาพ) ไม่งั้นตัดสินฮารุกะเป็นชายจากบรรทัด「ごゆっくりどうぞ。」
        (r"(?<!どう)[ぞぜ](?=[。！？…\s]|$)", "คำลงท้าย ぞ/ぜ"),
        (r"てめえ|てめぇ|貴様", "คำเรียกฝ่ายตรงข้ามแบบชาย"),
        (r"だろうが(?=[。！？…]|$)", "คำลงท้าย だろうが"),
    ],
    "female": [
        (r"あたし|アタシ|あたい", "สรรพนาม あたし"),
        (r"わらわ|妾", "สรรพนาม わらわ"),
        (r"かしら(?=[。！？…\s]|$)", "คำลงท้าย かしら"),
        (r"わよ|わね|わよね", "คำลงท้าย わよ/わね"),
        (r"のよ(?=[。！？…\s]|$)", "คำลงท้าย のよ"),
        (r"ですわ|ますわ", "คำลงท้าย ですわ"),
        (r"ちょうだい(?=[。！？…\s]|$)", "คำขอ ちょうだい"),
        (r"だわ(?=[。！？…\s]|$)", "คำลงท้าย だわ"),
        (r"ないわ(?=[。！？…\s]|$)", "คำลงท้าย ないわ"),
    ],
}

# เครื่องหมาย "ชั้นรอง" — ใช้ต่อเมื่อชั้นหลักไม่เจออะไรเลยทั้งสองฝั่งเท่านั้น
# เหตุผล: Ishin พูดสำเนียงคันไซทั้งเกม สรรพนามคันไซแยกเพศชัดกว่ามาตรฐาน
#   うち = บุรุษที่หนึ่งของ "ผู้หญิง" คันไซ (โอเรียว/ฮารุกะใช้)  ← ต้องกัน「うちの店」ด้วย lookahead
#   わい/わて = บุรุษที่หนึ่งของ "ผู้ชาย" คันไซ
# แยกชั้นเพราะอ่อนกว่า 俺/あたし มาก — ถ้าเจอชั้นหลักแล้ว ห้ามให้ชั้นนี้มาแย่งคำตัดสิน
MARKERS_WEAK = {
    "male": [(r"わい(?=は|が|も|、|。|や)|わて(?=は|が|も|、|。)",
              "สรรพนามคันไซชาย わい/わて")],
    "female": [(r"うち(?=は|が|も|、|。|と|やと|やけど|なんか|やって)",
                "สรรพนามคันไซหญิง うち")],
}

MARKERS_C = {g: [(re.compile(p), why) for p, why in v] for g, v in MARKERS.items()}
MARKERS_WEAK_C = {g: [(re.compile(p), why) for p, why in v] for g, v in MARKERS_WEAK.items()}

# ---- ป้ายผู้พูดที่เป็น "กลุ่มคน" ไม่ใช่ตัวละครเดียว --------------------------
# `Employee` 946 บรรทัด = พนักงานร้านหลายสิบร้านหลายเพศใช้ป้ายเดียวกัน
# เครื่องหมายเพศที่นับได้จึงเป็นของ *คนใดคนหนึ่ง* ในกลุ่ม ไม่ใช่ของทุกคน → บังคับกลางเพศเสมอ
# (ถ้าไม่กันข้อนี้ ผลรอบก่อนตัดสิน Employee/Customer เป็นหญิงจาก「ですわ」ไม่กี่บรรทัด)
GENERIC_CROWD = re.compile(
    r"\b(employee|customer|townsperson|townspeople|onlooker|patron|passerby|resident|"
    r"citizen|villager|crowd|everyone|people|person|narrator|guest|visitor|staff|"
    r"student|official|attendant|servant|receptionist|troops?|trooper|soldier|guard|"
    r"warrior|ronin|shishi|loyalist|handler|child|kid|doctor|barker|beggar|vendor|"
    r"foreigner|unknown|\?\?\?)\b", re.I)

# ---- ชื่อผู้พูดที่บอกเพศในตัวเอง (หลักฐาน B) ------------------------------
# เก็บเฉพาะคำที่ **ตัวคำเองแปลว่าเพศนั้น** ในภาษาอังกฤษ — ไม่เอาคำที่ "ยุคนั้นมักเป็นเพศนี้"
# (trooper/samurai/magistrate ถูกถอดออกตั้งใจ: เป็นการอนุมานจากประวัติศาสตร์ ไม่ใช่หลักฐานในไฟล์
#  ปล่อยให้เครื่องหมายภาษาญี่ปุ่นตัดสินแทน ตามกติกา "ห้ามเดา")
ROLE_GENDER = [
    (re.compile(r"\b(mother|madam|geisha|maid|girl|grandma|granny|lady|woman|women|"
                r"joshi|courtesan|hostess|wife|nun|daughter|sister|miss|mistress)\b",
                re.I), "female"),
    (re.compile(r"\b(father|boy|man|men|guy|grandpa|son|brother|mister|husband)\b",
                re.I), "male"),
]


def role_gender(name):
    for rx, g in ROLE_GENDER:
        m = rx.search(name)
        if m:
            return g, "ชื่อผู้พูดบอกเพศในตัวเอง (%s)" % m.group(0)
    return None, None


def _tally(texts, table):
    hits = Counter()
    why = defaultdict(Counter)
    samples = defaultdict(list)
    for t in texts:
        if not t:
            continue
        for g, pats in table.items():
            for rx, label in pats:
                n = len(rx.findall(t))
                if n:
                    hits[g] += n
                    why[g][label] += n
                    if len(samples[g]) < 3:
                        samples[g].append(t.replace("\n", "/")[:70])
    return hits, why, samples


def score(texts):
    """นับเครื่องหมายเพศจากข้อความญี่ปุ่นทั้งกอง คืน (คะแนน, เหตุผล, ตัวอย่าง, ชั้นที่ใช้)

    ⚠ นับ **ข้อความไม่ซ้ำ** เท่านั้น — บทเดินเมืองบรรทัดเดียวถูกใช้ซ้ำได้สิบกว่าครั้ง
    ถ้านับทุกครั้ง คำเดียวที่ตรวจผิดจะถูกขยายจนพลิกคำตัดสินได้ (เจอจริงกับฮารุกะ)
    """
    uniq = list(dict.fromkeys(t for t in texts if t))
    hits, why, samples = _tally(uniq, MARKERS_C)
    if verdict(hits) != "unknown":
        return hits, why, samples, "primary"
    # ชั้นหลักตัดสินไม่ได้ → ลองรวมชั้นรอง (สรรพนามคันไซ) เข้าไปด้วย
    whits, wwhy, wsamples = _tally(uniq, MARKERS_WEAK_C)
    for g in ("male", "female"):
        whits[g] += hits[g]
        wwhy[g].update(why[g])
        wsamples[g] = (wsamples[g] + samples[g])[:3]
    if verdict(whits) != "unknown":
        return whits, wwhy, wsamples, "weak"
    return hits, why, samples, "primary"


def verdict(hits):
    m, f = hits["male"], hits["female"]
    if m >= MIN_HITS and f <= m * MAX_CONTRA:
        return "male"
    if f >= MIN_HITS and m <= f * MAX_CONTRA:
        return "female"
    return "unknown"


# ---- เก็บบรรทัดของผู้พูดแต่ละคน --------------------------------------------
CUE_RE = re.compile(r"^([a-z][a-z0-9]{1,15})_[a-z0-9_]+$")
NOT_SPEAKER = {"kaiwabgm", "bgm", "se", "voice", "sys", "system", "minig", "mini",
               "2d", "3d", "arasuji", "telop", "sub", "common", "cmn", "test", "dummy"}
# label ที่ขึ้นต้นตัวใหญ่แต่เป็นรหัสท่าทาง/ฉาก ไม่ใช่ชื่อผู้พูด (เห็นจากคลังจริง)
NOT_A_NAME = re.compile(r"^(Talk_|TLK_|C\d|P_|M_|F_|Idle|Player|Never|Dummy)", re.I)


def collect_locres():
    """ผู้พูดชั้นคัตซีน: namespace `X` คู่กับ `X_speaker` คีย์ต่อคีย์"""
    en = json.loads((paths.EXTRACTED / "locres" / "Game.en.json").read_text(encoding="utf-8"))
    ja = json.loads((paths.EXTRACTED / "locres" / "Game.ja.json").read_text(encoding="utf-8"))

    def flat(d):
        S = d["strings"]
        out = {}
        for ns in d["namespaces"]:
            for e in ns["entries"]:
                out[(ns["ns"], e["key"])] = S[e["idx"]]
        return out

    fe, fj = flat(en), flat(ja)
    by_speaker = defaultdict(list)
    for (ns, key), name in fe.items():
        if not ns.endswith("_speaker"):
            continue
        base = ns[: -len("_speaker")]
        ja_text = fj.get((base, key))
        if ja_text:
            by_speaker[name].append(ja_text)
    return by_speaker


def msg_speaker(voice):
    """แปลง label ของคำสั่ง "เล่นเสียงบรรทัดนี้" เป็นผู้พูด

    label ที่ 0x35 ชี้มีสองรูป (วัดจากคลังจริง): ชื่อคิวเสียงโรมาจิที่ฝังชื่อผู้พูดไว้หน้าสุด
    3,989 ครั้ง · **ชื่อผู้พูดบนจอตรง ๆ** 124 ครั้ง — คืน (ค่า, ชนิด) เพื่อให้ผู้เรียกแยกได้
    ที่เหลือเป็นชื่อท่าทาง/ฉาก (`Talk_Yes` · `TLK_SCN001` · `dummy`) → ไม่ใช่ผู้พูด
    """
    if not voice:
        return None, None
    m = CUE_RE.match(voice)
    if m:
        sid = m.group(1)
        return (None, None) if sid in NOT_SPEAKER else (sid, "id")
    # ชื่อบนจอ: ขึ้นต้นตัวใหญ่ ไม่ใช่รหัสท่าทาง/ฉาก
    if re.match(r"^[A-Z][A-Za-z'’ -]{1,30}$", voice) and not NOT_A_NAME.match(voice):
        return voice, "name"
    return None, None


def collect_msg():
    """ผู้พูดชั้น .msg — จากคำสั่ง 0x03 ชนิดย่อย 0x35 เท่านั้น

    ⚠ กับดักที่เจอตอนตรวจผลรอบแรก (1 ก.ย. 2026):
    คำสั่ง 0x03 ถูกใช้อ้าง label ทุกชนิด รวม **ตัวเลือกในเมนูสนทนา** ที่ติดค้างกับทุกแถว
    ในบล็อกเดียวกัน ถ้าเอา label ตัวแรกที่หน้าตาเหมือนคิวเสียงมาใช้จะได้ผู้พูดผิด —
    ผลรอบแรกตัดสินฮารุกะกับโอเรียวเป็น "ชาย" เพราะนับบทของเรียวมะที่ติดมาด้วย

    ตัวชี้ขาดคือชนิดย่อย `0x35` (มีอย่างมากหนึ่งตัวต่อแถว) — รายละเอียดใน tools/msg.py
    """
    rows = json.loads((paths.EXTRACTED / "parallel" / "msg.json").read_text(encoding="utf-8"))
    by_id, by_name = defaultdict(list), defaultdict(list)
    n_voice = n_used = 0
    for r in rows:
        if not r.get("voice"):
            continue
        n_voice += 1
        who, kind = msg_speaker(r["voice"])
        if not who or not r.get("ja"):
            continue
        n_used += 1
        (by_id if kind == "id" else by_name)[who].append(r["ja"])
    print("   .msg: แถวที่มีคำสั่งเล่นเสียง %d · ระบุผู้พูดได้ %d "
          "(id คิว %d ตัว · ชื่อบนจอ %d ชื่อ)"
          % (n_voice, n_used, len(by_id), len(by_name)))
    return by_id, by_name


def collect_speak_data():
    """NPC ริมถนน: sound_speak_data.bin มีคอลัมน์ speaker + message คู่กันในแถวเดียว"""
    def cells(lang):
        p = paths.EXTRACTED / ("db_%s" % lang) / "sound_speak_data.bin.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        out = {}
        for k in d:
            if not k.isdigit() or not isinstance(d[k], dict):
                continue
            for i, (_rk, row) in enumerate(d[k].items()):
                if isinstance(row, dict):
                    out[(k, row.get("reARMP_rowIndex", i))] = row
        return out

    ce, cj = cells("en"), cells("ja")
    by_speaker = defaultdict(list)
    for key, row in ce.items():
        sp = row.get("speaker")
        jr = cj.get(key) or {}
        if sp and jr.get("message"):
            by_speaker[sp].append(jr["message"])
    return by_speaker


def cue_subtitle_map():
    """คิวไหนเป็นของตัวละครไหน — หลักฐานตรงจาก sound_macan_cue_subtitle.bin"""
    p = paths.EXTRACTED / "db_en" / "sound_macan_cue_subtitle.bin.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    tok = defaultdict(Counter)
    for k in d:
        if not k.isdigit() or not isinstance(d[k], dict):
            continue
        for rk, row in d[k].items():
            if isinstance(row, dict) and row.get("speaker"):
                for t in rk.split("_"):
                    if t.isalpha() and len(t) > 2:
                        tok[t][row["speaker"]] += 1
    # เก็บเฉพาะโทเคนที่ชี้ตัวละครเดียวและมีน้ำหนักพอ
    return {t: c.most_common(1)[0][0] for t, c in tok.items()
            if len(c) == 1 and sum(c.values()) >= 5}


def load_overrides():
    """คำตัดสินเพศที่ lead ล็อกเอง — {ชื่อผู้พูด: {gender, why}}

    ใช้เมื่อหลักฐานอัตโนมัติไม่พอ แต่ **มีหลักฐานในไฟล์เกมที่คนอ่านแล้วชี้ขาดได้**
    (เช่น บทที่ตัวละครถูกเรียกว่า "she" ตรง ๆ) · ช่อง `why` บังคับเขียน
    ห้ามใส่เพราะ "รู้อยู่แล้วจากภาคอื่น" — Ishin เป็นตัวละครคนละชุด
    """
    p = paths.TRANSLATIONS / "gender_overrides.json"
    if not p.exists():
        p.write_text(json.dumps({
            "_readme": ("คำตัดสินเพศที่ lead ล็อกเอง — ทับผลของ build_speaker_gender.py "
                        "· ต้องเขียน why ทุกครั้ง และ why ต้องอ้างหลักฐานในไฟล์เกม"),
            "_example": {"gender": "female", "why": "บทของ X เรียกตัวละครนี้ว่า her ในไฟล์ ..."},
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        return {}
    d = json.loads(p.read_text(encoding="utf-8"))
    return {k: v for k, v in d.items()
            if not k.startswith("_") and isinstance(v, dict) and v.get("gender")}


def main():
    overrides = load_overrides()
    if overrides:
        print("คำสั่งทับของ lead: %d รายการ" % len(overrides))
    loc = collect_locres()
    msg, msg_named = collect_msg()
    spk = collect_speak_data()
    cue_map = cue_subtitle_map()

    print("ชั้นคัตซีน (locres) : ผู้พูด %3d คน · บรรทัดญี่ปุ่น %5d"
          % (len(loc), sum(len(v) for v in loc.values())))
    print("ชั้น .msg (คิวเสียง) : id %3d ตัว · บรรทัดญี่ปุ่น %5d"
          % (len(msg), sum(len(v) for v in msg.values())))
    print("ชั้น NPC (speak_data): ผู้พูด %3d คน · บรรทัดญี่ปุ่น %5d"
          % (len(spk), sum(len(v) for v in spk.values())))
    print("คิว->ตัวละคร จาก cue_subtitle: %d โทเคน (%s)"
          % (len(cue_map), " · ".join("%s=%s" % kv for kv in sorted(cue_map.items()))))
    print()

    # ---- รวมเป็นทะเบียนเดียว: กุญแจคือ "ชื่อที่ผู้เล่นเห็น" ถ้ามี ไม่งั้นใช้ id ----
    reg = {}

    def entry(name):
        return reg.setdefault(name, {
            "name": name, "id": None, "sources": [], "lines": {},
            "ja_lines": 0, "gender": "unknown", "gender_why": [], "samples": {},
        })

    for name, texts in loc.items():
        e = entry(name)
        e["sources"].append("locres_speaker")
        e["lines"]["locres"] = len(texts)
        e.setdefault("_texts", []).extend(texts)
    for name, texts in spk.items():
        e = entry(name)
        e["sources"].append("sound_speak_data")
        e["lines"]["speak_data"] = len(texts)
        e.setdefault("_texts", []).extend(texts)
    # .msg ที่คำสั่งเล่นเสียงชี้ชื่อผู้พูดบนจอตรง ๆ (ไม่ต้องผ่าน id คิว)
    for name, texts in msg_named.items():
        e = entry(name)
        e["sources"].append("msg_voice_name")
        e["lines"]["msg_named"] = len(texts)
        e.setdefault("_texts", []).extend(texts)

    # id จาก .msg — ผูกเข้ากับชื่อที่ผู้เล่นเห็นเมื่อพิสูจน์ได้
    name_lc = {n.lower(): n for n in reg}
    for sid, texts in msg.items():
        if sid in cue_map:                       # หลักฐาน C — ชี้ขาด
            name, how = cue_map[sid], "cue_subtitle.bin (%s)" % sid
        elif sid in name_lc:                     # ชื่อตรงตัวอักษรกับชื่อบนจอ
            name, how = name_lc[sid], "ชื่อตรงกับชื่อบนจอ (%s)" % sid
        else:                                    # ไม่มีชื่อบนจอ — ขึ้นทะเบียนด้วย id
            name, how = "id:" + sid, "มีแต่ id ในคิวเสียง"
        e = entry(name)
        e["id"] = sid
        e["sources"].append("msg_cue:" + how)
        e["lines"]["msg"] = e["lines"].get("msg", 0) + len(texts)
        e.setdefault("_texts", []).extend(texts)

    # ---- ตัดสินเพศ ----
    tally = Counter()
    for name, e in reg.items():
        texts = e.pop("_texts", [])
        e["ja_lines"] = len(texts)
        hits, why, samples, tier = score(texts)
        g = verdict(hits)
        e["marker_hits"] = {"male": hits["male"], "female": hits["female"]}
        crowd = bool(GENERIC_CROWD.search(name)) and not role_gender(name)[0]
        if crowd:
            g = "unknown"
            e["crowd_label"] = True
        if g != "unknown":
            e["gender"] = g
            e["gender_from"] = "ja_markers" if tier == "primary" else "ja_markers_weak"
            e["gender_why"] = ["%s x%d" % (k, v) for k, v in why[g].most_common(4)]
            e["samples"] = {g: samples[g]}
        elif crowd:
            e["gender_from"] = "crowd_label"
            e["gender_why"] = ["ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ"]
        else:
            rg, rwhy = role_gender(name)
            if rg:
                e["gender"] = rg
                e["gender_from"] = "role_name"
                e["gender_why"] = [rwhy]
            else:
                e["gender_from"] = "none"

        # ---- คำสั่งทับของ lead (ถ้ามี) ----
        # ไฟล์นี้คือทางเดียวที่คนจะทับผลอัตโนมัติได้ และต้องเขียนเหตุผลกำกับเสมอ
        ov = overrides.get(name)
        if ov:
            e["gender"] = ov["gender"]
            e["gender_from"] = "override"
            e["gender_why"] = [ov.get("why") or "(ไม่ได้เขียนเหตุผล — ต้องเติม)"]
        tally[e["gender"]] += 1

    out = paths.TRANSLATIONS / "speakers.json"
    out.write_text(json.dumps(reg, ensure_ascii=False, indent=1, sort_keys=True),
                   encoding="utf-8")
    print("ผู้พูดในทะเบียน %d คน — ชาย %d · หญิง %d · พิสูจน์ไม่ได้ %d (ต้องกลางเพศ)"
          % (len(reg), tally["male"], tally["female"], tally["unknown"]))
    print("เขียนแล้ว: %s" % out)

    # ---- เอกสารหลักฐานให้คนอ่าน ----
    ordered = sorted(reg.values(), key=lambda e: (-e["ja_lines"], e["name"]))
    md = [
        "# หลักฐานเพศผู้พูด — Like a Dragon: Ishin!", "",
        "สร้างโดย `scripts/build_speaker_gender.py` · **ทุกช่องมาจากไฟล์เกม ไม่มีการเดา**", "",
        "⚠ ภาคนี้ไม่มีตารางเพศในไฟล์เกม (ตรวจครบ 244 ตาราง ARMP แล้วไม่มีคอลัมน์ sex/gender)",
        "หลักฐานหลักจึงเป็น **ต้นฉบับญี่ปุ่นที่อยู่ใน pak เดียวกัน** — สรรพนามบุรุษที่หนึ่ง",
        "และคำลงท้ายที่ผูกกับเพศแน่น ซึ่งฉบับอังกฤษตัดทิ้งหมด", "",
        "เกณฑ์: ฝั่งที่ชนะต้องเจอ >= %d ครั้ง และฝั่งตรงข้ามไม่เกิน %.0f%% ของฝั่งที่ชนะ"
        % (MIN_HITS, MAX_CONTRA * 100),
        "ไม่ผ่านเกณฑ์ = `unknown` -> **แปลกลางเพศ ห้ามเดา**", "",
        "| ผู้พูด | id คิว | เพศ | ที่มา | ช/ญ | บรรทัด ja | หลักฐาน |",
        "|---|---|---|---|---|---:|---|",
    ]
    for e in ordered:
        md.append("| %s | %s | **%s** | %s | %d/%d | %d | %s |" % (
            e["name"], "`%s`" % e["id"] if e["id"] else "-", e["gender"],
            e.get("gender_from", "none"),
            e["marker_hits"]["male"], e["marker_hits"]["female"],
            e["ja_lines"], " · ".join(e["gender_why"]) or "-"))
    md += ["", "## สรุป", "",
           "- ผู้พูดในทะเบียน: **%d** คน" % len(reg),
           "- ชาย: %d · หญิง: %d" % (tally["male"], tally["female"]),
           "- พิสูจน์ไม่ได้: **%d** — ทุกคนในกลุ่มนี้ต้องแปลกลางเพศ" % tally["unknown"], "",
           "## ที่มาของแต่ละชั้น", "",
           "| ชั้น | ผู้พูด | บรรทัดญี่ปุ่นที่จับคู่ได้ |", "|---|---:|---:|",
           "| `Game.locres` คัตซีน (`*_speaker`) | %d | %d |"
           % (len(loc), sum(len(v) for v in loc.values())),
           "| `.msg` คิวเสียง opcode 0x03 | %d | %d |"
           % (len(msg), sum(len(v) for v in msg.values())),
           "| `sound_speak_data.bin` NPC | %d | %d |"
           % (len(spk), sum(len(v) for v in spk.values()))]
    p = paths.DOCS / "reference" / "gender_evidence_ishin.md"
    p.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("เขียนแล้ว: %s" % p)


if __name__ == "__main__":
    main()
