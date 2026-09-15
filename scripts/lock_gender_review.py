#!/usr/bin/env python3
"""ลงคำตัดสินเพศของ lead จากการอ่าน `work/gender_fix/review_no_evidence.md` (15 ก.ย. 2026)

ที่มา: 71 สตริงที่คำแปลมีคำลงท้ายบอกเพศ แต่หลักฐานเดิมมาจาก scene_gender ของฉากที่ถูกตัดเพราะมีสองเพศ
ผู้ตรวจคลื่นสามอ้างหลักฐานยืม/คัดออกซึ่งเครื่องรับไม่ได้ → lead อ่านบริบททีละสตริงแล้วตัดสินเอง

DECISIONS = {คีย์บรรทัดตัวแทน: (เพศ, เหตุผลที่อ้างบรรทัดในเกม)}
  สคริปต์หา EN ของคีย์จาก extracted/parallel/msg.json แล้วเขียนลง translations/gender_lines.json
  (ไม่ทับคีย์ที่มีอยู่แล้ว) — ต่อด้วย `python scripts/check_gender_lines.py` เพื่อจับสตริงที่ใช้ร่วมหลายฉาก
NEUTRAL = {คีย์บรรทัด: เหตุผล} — พิสูจน์เพศไม่ได้ คำแปลต้องถอดคำลงท้ายบอกเพศ (พิมพ์รายการให้แก้ใน done)

ใช้: python scripts/lock_gender_review.py [--write]
"""
import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

TAG = " — lead อ่านบริบท 15 ก.ย. 2026"

UDON = ("เจ้าของร้านอุด้ง uid000c140e: #228 พูดเอง 麺は俺の方で茹でておくさかい (บทต่อเนื่อง #228–#230) · "
        "#234 บทรำพึงของเรียวมะ \"he did treat me to udon today... help him out\"")
IZAKAYA = ("ผู้จัดการร้านเหล้าฟุคุฟุคุ uid00330c98 (店長): #164 俺なんて生まれてきたのが間違いやった · "
           "#261 \"(Is he... crying!?)\" · #264 この男、もしかして泣き上戸 · #278 居酒屋の店長やってるのに · "
           "บทบริการของร้านในไฟล์นี้ไซโตตอบกลับด้วย 店長 (#243 · #398 · #402)")
PATROL = ("ซามูไรตรวจเมืองในฉาก uid006e01bf (私は武士です #121): #070/#108 บทรำพึงของเรียวมะ \"help him out. He seems like "
          "an alright guy\" · #125 意外といい奴だな \"surprisingly nice guy\" · #165 \"Man, is this guy a handful\"")
COURIER = ("คนส่งของสำเนียงคันไซ uid010c144f: #119 และ #127 พูดเอง ワイの荷物 / ワイ、骸街まで急いでた · "
           "#129 บทรำพึงของเรียวมะ \"(He was really in a rush.)\"")
BOKU = ("ชายที่ห่อของสลับ uid010c144f: #131 \"(Seems like he's waking up.)\" · พูดเอง 僕の荷物 #135 #150 #158 · "
        "บทที่ตัดสินเป็นเทิร์นตอบไซโตในบทสนทนาสองคน")
RETAINER = ("ข้ารับใช้ของขุนศึก uid016e00a9: #031 พูดเอง しかしわしは、御館様のため · บทที่ตัดสินเป็นบทของผู้ส่งสาร/"
            "ผู้ติดตามคนเดียวกันที่เรียกนายว่า 御館様")
JIIYA = ("คนรับใช้ตระกูลคุระมิตสึ uid016e00b7: #049 ซาโยโกะเรียก じいや (爺や = คนรับใช้ชายสูงวัย) #050 ตอบ はっ、小夜子様 · "
         "#010 แนะนำตัว 倉光家…使用人 · #045 ลงท้าย ましたわい")

MOTHER = ("แม่ของเด็กชายรักผัก uid000c1347 (คนในฉาก: เด็กชาย ぼく/お兄ちゃん · ไซโต だ/な · แม่ ですます): "
          "#021 เด็ก \"I brought my mom!\" · #069 พูดเอง 私……今まで、母親失格でしたね · #060 \"You like it, Mom!?\" ตอบ #061 · "
          "แม่เกลียดผัก ลูกอยากกินผัก (#036 私、野菜苦手なんです) · #183/#185 ดุลูก ถัดไป #184/#186 \"But, Mom...\" \"Mom, no! Wait...\"")
SUZU = ("สุซุ uid010c1471 (คนในฉาก: สุซุ · อิเคซุงิ 僕 · อากุริ でござる · ไซโต だ): #011 อิเคซุงิเรียก すーずーちゃん ตอบ #012 · "
        "#014 うふふ…池杉さんったら · #028 อิเคซุงิพูดกับผู้พูด #026 ว่า 君は綺麗だ \"You're so beautiful, woman\" · "
        "#038/#039 ปฏิเสธคำขอแต่งงานของอิเคซุงิ")
LOVESTRUCK = ("Lovestruck Woman uid010c147a: ป้ายผู้พูด #002/#008 · #006 พูดเอง 私でも男にもてもてになれますかね "
              "(ซื้อน้ำหอมเพื่อให้ผู้ชายสนใจ) · #002 คือคนที่ฝากซื้อน้ำหอมเอง")
OMATSU = ("โอมัตสึ uid011606e7: #029 แนะนำตัว 私は…松って言うの。みんな、お松って呼ぶわ · บทต่อเนื่องของหญิงคนเดียว #016–#031 "
          "(#018 野盗なの · #023 わかったわ) · #019 ไซโตตอบผู้พูด お前は？")
OHARU = ("โอฮารุ uid011607dd: #008 โทจิโร \"Oharu… Are you trying to take my sister away!?\" · #021/#026 お兄ちゃん！ · "
         "#022 โทจิโรตอบ \"Oharu! You're... on your feet!?\" แล้ว #023 ผู้พูดคนเดิมตอบ うん……だからもうやめて")
SERVANT_AF = ("คนรับใช้ตระกูลคุระมิตสึ uid006e00af (ป้าย Kuramitsu Family Servant): #005 ซาโยโกะเรียก じいや #006 ตอบ はっ、小夜子様 · "
              "#009 ผู้ตอบ \"Yes, my lady\" ลง ですぞ · #001 ขอให้คุ้มกัน 小夜子様を乗せた駕籠 → #003 ไซโตรับ → #004 ขอบคุณ "
              "引き受けてくださるか · #023 ลง ですな")

DECISIONS = {
    "uid000c140e#230": ("male", UDON),
    "uid000c140e#236": ("male", UDON),
    **{k: ("male", IZAKAYA) for k in (
        "uid00330c98#037", "uid00330c98#041", "uid00330c98#067", "uid00330c98#072", "uid00330c98#186",
        "uid00330c98#197", "uid00330c98#201", "uid00330c98#207", "uid00330c98#246", "uid00330c98#248",
        "uid00330c98#262", "uid00330c98#276", "uid00330c98#278", "uid00330c98#280", "uid00330c98#282",
        "uid00330c98#355", "uid00330c98#357", "uid00330c98#359", "uid00330c98#360", "uid00330c98#368",
        "uid00330c98#393", "uid00330c98#395", "uid00330c98#399", "uid00330c98#401", "uid00330c98#403",
        "uid00330c98#405")},
    **{k: ("male", PATROL) for k in (
        "uid006e01bf#003", "uid006e01bf#023", "uid006e01bf#029", "uid006e01bf#065", "uid006e01bf#069",
        "uid006e01bf#117", "uid006e01bf#124", "uid006e01bf#147", "uid006e01bf#164", "uid006e01bf#169",
        "uid006e01bf#171", "uid006e01bf#227", "uid006e01bf#234", "uid006e01bf#236", "uid006e01bf#254",
        "uid006e01bf#260", "uid006e01bf#268")},
    **{k: ("male", COURIER) for k in (
        "uid010c144f#064", "uid010c144f#066", "uid010c144f#116", "uid010c144f#118", "uid010c144f#119",
        "uid010c144f#127")},
    **{k: ("male", BOKU) for k in (
        "uid010c144f#134", "uid010c144f#154", "uid010c144f#156", "uid010c144f#165", "uid010c144f#167")},
    **{k: ("male", RETAINER) for k in (
        "uid016e00a9#004", "uid016e00a9#027", "uid016e00a9#086", "uid016e00a9#138", "uid016e00a9#210")},
    **{k: ("male", JIIYA) for k in (
        "uid016e00b7#005", "uid016e00b7#010", "uid016e00b7#031", "uid016e00b7#045", "uid016e00b7#046",
        "uid016e00b7#052")},
    "uid010c1465#084": ("male", "อากุริ uid010c1465: #083 ไซโตสั่ง 阿栗、すずを連れて離れていろ แล้ว #084 ผู้ถูกเรียกตอบ 斎藤殿……かたじけない · "
                                "#019 อากุริพูดเอง 拙者は不細工で……かっこ悪い男でござる"),
    # ป้ายเพศผิดที่ผู้ตรวจคลื่น gender3 ยื่น (งาน C) — lead อ่านทั้งฉากแล้วรับเฉพาะที่มีคำผูกเพศของผู้พูดเอง
    # หรือคนอื่นเรียกผู้พูด · ตีตก: มิโฮะ uid010c147c#132 (#134 ผู้พูดคนเดียวกันใช้ ぼく) · "Oh..." / "Thank you."
    # (สตริงใช้ 9/7 ฉาก ล็อกตาม EN ไม่ได้) · ผู้รับพัสดุ uid00160b22–2c (research §10.2)
    **{k: ("female", MOTHER) for k in (
        "uid000c1347#022", "uid000c1347#026", "uid000c1347#029", "uid000c1347#036", "uid000c1347#038",
        "uid000c1347#039", "uid000c1347#061", "uid000c1347#062", "uid000c1347#065", "uid000c1347#069",
        "uid000c1347#070", "uid000c1347#072", "uid000c1347#183", "uid000c1347#185")},
    "uid000c12ed#633": ("female", "ซากิโกะ uid000c12ed เล่าเรื่อง: 俺の後ろに立つな อยู่ในเครื่องหมายคำพูด = คำพูดของ \"the guy\" ที่ถูกอ้าง · "
                                "บรรทัดเองลง ですって！…感じよねぇ · #634 ต่อเทิร์นเดียวกัน のよぉ"),
    "uid006e00af#007": ("female", "ซาโยโกะ uid006e00af: #005 じいや (เรียกคนรับใช้) · #006 คนรับใช้ตอบ はっ、小夜子様 · "
                                "#008 บทรำพึงของไซโต \"Such a beautiful voice\" · #009 คนรับใช้ตอบ \"Yes, my lady\""),
    **{k: ("female", SUZU) for k in (
        "uid010c1471#012", "uid010c1471#014", "uid010c1471#026", "uid010c1471#038", "uid010c1471#039")},
    **{k: ("female", LOVESTRUCK) for k in ("uid010c147a#002", "uid010c147a#006")},
    **{k: ("female", OMATSU) for k in ("uid011606e7#016", "uid011606e7#018", "uid011606e7#020")},
    **{k: ("female", OHARU) for k in ("uid011607dd#021", "uid011607dd#023")},
    # ฉากสำเนาของ uid016e00b7 — ล็อกซาโยโกะ #007 แล้วฉากหลุดจาก scene_gender ต้องล็อกบทคนรับใช้เอง
    **{k: ("male", SERVANT_AF) for k in ("uid006e00af#001", "uid006e00af#004", "uid006e00af#023")},
    # audit ชั้น partial (15 ก.ย. 2026 ค่ำ): สตริงเดียวสองบรรทัดในฉากเดียว มีหลักฐานแค่บรรทัดเดียว
    "uid016c008c#164": ("female", "โอกามิร้านยามาบุกิ uid016c008c: สตริงเดียวกับ #105 ที่คิวเสียง yujyo_yukaku_s_01_002 = หญิง · "
                                "#164 ป้าย Yamabuki Okami คิวเสียงชุดเดียวกัน yujyo_yukaku_s_01_025 · ฉากเดียว ja เดียว"),
}

# คีย์บรรทัด: (เหตุผล, ข้อความเดิมในคำแปล, ข้อความใหม่) — ถอดคำลงท้ายบอกเพศออกตรงจุด
NEUTRAL = {
    "uid016e00b7#054": ("ผู้พูดน่าจะเป็นซาโยโกะ (#051 わたくしも… \"We would like to offer our thanks\" · #054 \"We bid you fond "
                        "farewell\" ต่อจากไซโตตอบนางที่ #053) แต่ไม่มีเครื่องหมายในบรรทัด → ถอด ขอรับ",
                        "ขอตัวก่อนขอรับ", "ขอตัวก่อน"),
    "uid01400014#043": ("นักเรียนที่ลองภูมิครู (สำเนาฉาก uid016f000b / uid0178000a) — ไม่มีคำบอกเพศในบทของเด็กคนนี้เลย "
                        "(เรียวมะเรียกแค่ ガキ #055 · โอมิตสึเป็นเด็กอีกคน) → ถอด ขอรับ",
                        "คือใครหรือขอรับ?", "คือใครหรือ?"),
    "uid01400014#216": ("นักเรียนคนเดียวกับ #043 — ไม่มีคำบอกเพศ → ถอด ขอรับ",
                        "ด้วยเถิดขอรับ...", "ด้วยเถิด..."),
    "uid006e00af#010": ("\"Sir bodyguard, may we ask your name?\" ต่อจาก #009 คนรับใช้ (ชาย) และ #008 บทรำพึงถึงเสียงซาโยโกะ — "
                        "ผู้พูดเป็นซาโยโกะหรือคนรับใช้ก็ได้ · ล็อก #007 เป็นหญิงแล้วฉากนี้จะหลุดจาก scene_gender → ถอด ขอรับ",
                        "ได้หรือไม่ขอรับ?", "ได้หรือไม่?"),
    "uid006e00af#012": ("\"Saito-sama, please accept our apologies…\" ผู้พูดคนเดียวกับ #010 (ซาโยโกะหรือคนรับใช้) → ถอด ขอรับ",
                        "ของท่านขอรับ", "ของท่าน"),
    "uid006e00af#015": ("\"We'll be focused on bearing the palanquin\" 駕籠だけじゃなく…私達も守ってください — "
                        "อาจเป็นคนแบกเกี้ยว ไม่ใช่ じいや · ไม่มีคำบอกเพศ → ถอด ขอรับ",
                        "ไปด้วยนะขอรับ", "ไปด้วยนะ"),
    # หลัง merge_qc.dialogue_gender เลิกลากเพศให้สตริงที่ใช้หลายฉากและ ja ต่างกัน (15 ก.ย. 2026 ค่ำ)
    "uid00330ca4#003": ("\"prize tickets\" ใช้ 6 บรรทัด: โอกามิ uid000c13a0#047 (หญิง) + Sushi Zanmai Chef uid00330ca4 ×5 "
                        "(ไม่มีหลักฐานเพศ) — คลื่น gender3 ใส่ เจ้าค่ะ จากชั้น EN ที่ยืมเพศโอกามิ → ถอด",
                        "ใบเจ้าค่ะ", "ใบ"),
    "uid010c1465#033": ("\"Farewell, Sir Saito!\" สองฉาก ja ต่างกัน · uid010c1471#090 มีหลักฐานชาย แต่ uid010c1465#033 ไม่มี "
                        "(น่าจะอากุริ แต่ล็อกตามสตริงอังกฤษไม่ได้) → ถอด ขอรับ",
                        "ลาก่อนขอรับ", "ลาก่อน"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    rows = json.loads((paths.EXTRACTED / "parallel" / "msg.json").read_text(encoding="utf-8"))
    en_of = {r["key"]: r.get("en") or "" for r in rows}
    path = paths.TRANSLATIONS / "gender_lines.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    added, same, clash = 0, 0, []
    for key, (gender, why) in DECISIONS.items():
        en = en_of.get(key)
        if not en:
            print("!! ไม่พบคีย์ %s" % key)
            continue
        cur = data.get(en)
        if cur:
            if cur.get("gender") == gender:
                same += 1
            else:
                clash.append((key, en, cur.get("gender"), gender))
            continue
        data[en] = {"gender": gender, "why": "%s · บรรทัดที่ตัดสิน %s%s" % (why, key, TAG)}
        added += 1
    for key, en, old, new in clash:
        print("!! ขัดกับคำตัดสินเดิม %s (%s -> %s): %s" % (key, old, new, en[:70]))
    print("เพิ่ม %d · มีอยู่แล้วเพศเดียวกัน %d · ขัด %d" % (added, same, len(clash)))

    master = json.loads(paths.MASTER_TH.read_text(encoding="utf-8"))
    fixes = {}
    for key, (why, old, new) in NEUTRAL.items():
        en = en_of.get(key)
        th = master.get(en or "")
        if not th or th.count(old) != 1:
            print("!! กลางเพศ %s: หา %r ในคำแปลไม่เจอ (หรือเจอหลายที่) — %r" % (key, old, th))
            continue
        fixes[en] = th.replace(old, new)
        print("กลางเพศ %s: %s\n  เดิม: %s\n  ใหม่: %s" % (key, why, th, fixes[en]))

    if args.write and not clash:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print("เขียน %s" % path)
        import merge_revise_wave as RW
        nf, nk = RW.apply_to_done(fixes)
        print("ลง done %d ไฟล์ · %d คีย์ -> ต่อด้วย python scripts/merge_qc.py" % (nf, nk))


if __name__ == "__main__":
    main()
