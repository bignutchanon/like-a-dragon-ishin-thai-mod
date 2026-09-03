#!/usr/bin/env python3
"""กวาดหา "อักษรละตินตกค้าง" ในคำแปลไทย — จับชื่อร้าน/สถานที่ที่ลืมทับศัพท์

ทำไมต้องมี: ผู้ตรวจ batch_120 เจอ `To Earth Angel` -> "ไปยัง Earth Angel" ทั้งที่ glossary §10
ล็อก "เอิร์ธแองเจิล" ไว้แล้ว — บั๊กแบบนี้รอดสายตาเพราะ merge_qc ไม่ได้ตรวจเรื่องคำล็อก
สคริปต์นี้ไล่ทุกคำแปล หาคำละตินที่ยังปนอยู่ แล้วหักคำที่ตั้งใจคง EN ออก เหลือไว้ให้คนดู

ใช้:
  python scripts/check_latin_leftovers.py                 # ดูของ master_th.json
  python scripts/check_latin_leftovers.py --done          # ดูของ translations/done/*.done.json
  python scripts/check_latin_leftovers.py --only 120      # เจาะ batch เดียว
"""
import argparse
import collections
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

# คำที่ทีมตัดสินให้ "คง EN" อย่างเป็นทางการ (glossary + คำตัดสิน lead) — ไม่ต้องรายงาน
KEEP_EN = {
    # เพิ่ม 26 ส.ค. 2026 (sprint 8) — รายการของ Lost Judgment เอง ที่ glossary §7 ล็อกให้คง EN
    # นักแปล 4 คนใน sprint เดียวรายงานตรงกันว่า "RK" ขึ้นเป็นคำตกค้างทุก batch ทั้งที่ถูกต้องแล้ว
    # (RK = ชื่อองค์กรในเนื้อเรื่อง · ที่เหลือเป็นตัวย่อสากลที่ไม่มีใครแปล)
    "rk", "mrc", "cg", "cgi", "ai", "a.i", "a.i.", "atm", "usb", "pin", "survive", "mvp",
    # เพิ่ม 26 ส.ค. 2026 (sprint 14 · ผู้ตรวจ batch_116): "EXP" โผล่ 6 จุดในข้อความ UI
    # และ ref_tm ทุกจุดคง EN ไว้ถูกต้องอยู่แล้ว แต่ด่านยังเตือนเพราะไม่มีในลิสต์
    "exp",
    # ชื่อไฟล์ diegetic ที่ตัวละครอ่านจากจอ — คง EN ในเครื่องหมายคำพูด (เคาะ sprint 13 · batch_107)
    # ⚠ ต่างจากชื่อกลุ่ม "Rhizome" เดี่ยว ๆ ที่ทับศัพท์ว่า "ไรโซม"
    "rhizome group homies",
    # เพิ่ม 26 ส.ค. 2026 (sprint 14 · ผู้ตรวจ batch_116/117) — ชื่อโหมดเกม/ชื่อเพลงคาราโอเกะ
    # ⚠ "Gauntlet" คือคำล็อกของ Gaiden ที่ให้คง EN · Y8/Pirate แปล gauntlet ว่า "นวม" = คนละความหมาย
    "gauntlet", "clan creator", "machinegun kiss", "like a butterfly", "harukaze",
    # แฮนเดิลออนไลน์/ชื่อเคสที่ต้นฉบับเขียนติดกันเป็นคำเดียว (sprint 14 · นักแปล batch_118)
    "dancingbunny",
    "buzz researcher", "buzzy searcher", "image interactive",
    # ชื่อรายการแข่งในเกม — คง EN ตามธรรมเนียมชื่อแบรนด์/อีเวนต์ (เคาะ sprint 10)
    "dance jam", "national high school jam", "genbukai",
    # เพิ่ม 26 ส.ค. 2026 (sprint 15 · ผู้ตรวจ batch_124) — ชื่อรายการแข่งหุ่นยนต์ (ล้อ RoboCup)
    # + ตัวย่อสมาคมผู้ปกครอง-ครู ที่ไม่มีตัวย่อไทยที่คนคุ้น (บรรทัดฐานเดียวกับ RK/CG/AI)
    "re robo rally", "robo rally", "pta",
    # ศัพท์มวยสากลที่คง EN (เคาะ sprint 10 · ผู้ตรวจ batch_078)
    "opbf", "tko", "ko", "worm", "write once read many",
    # ชื่อเกม/ฮาร์ดแวร์ SEGA จริง + ชื่อทีมที่เล่นมุกกับชื่อเกม (เคาะ sprint 11 · ผู้ตรวจ batch_082)
    "headshot lovers", "house of the dead", "hotd", "dreamcast",
    # รูปสั้นที่ตัวละครเอ่ยถึงชื่อทีมกลางประโยค ("And why 'headshot'?") — คงคู่กับชื่อเต็ม
    "headshot",
    # ชื่อหน่วยงานจัดหางานของญี่ปุ่น — ล็อกให้คง EN 26 ส.ค. 2026 (sprint 12 · batch_093)
    "hello work",
    # เคาะ sprint 12: `TPO` = ตัวย่อที่บทอธิบายความหมายเองในบรรทัดถัดไป · `R is 18` = ปริศนาเซฟ
    # ที่ผูกกับลำดับตัวอักษรอังกฤษ (R = ตัวที่ 18) แปลแล้วปริศนาพัง
    "tpo", "r is",

    "chatter", "kamurogo", "quickstarter", "smz", "s-one", "mako mods", "esc",
    "ex action", "ex boost", "ex bond", "playstation", "steam", "kamuro of the dead",
    "konban wife", "kj art", "mflp", "staminan", "hug bomb", "toughness", "tauriner",
    "wette kitchen", "vf5", "virtua fighter", "dice & cube", "paradise vr", "edison",
    # เพิ่ม 26 ส.ค. 2026 (sprint 15 · นักแปล batch_120) — ชื่อมินิเกม VR ใหม่ของ LJ
    # ไม่มีคำแปลในภาคไหน ใช้ EN สม่ำเสมอ 7 จุดในไฟล์เดียว · ตัวย่อชื่อทีมหุ่นยนต์ตาม §5.14
    "aircelios", "nt", "sdrd", "sal", "bob",
    # เพิ่ม 26 ส.ค. 2026 (sprint 15 · นักแปล batch_119 · batch_121 · batch_130)
    # `MIRAI Batting Center` (ชื่อสนามจริง ตาม Y7/Y8) · `Hama of the Dead` (คู่ขนานของ
    # `Kamuro of the Dead` ที่คง EN อยู่แล้ว) · `Master System` (เครื่องเกม SEGA จริง) ·
    # `Super Hang-On` (เกมตู้ SEGA จริง ตาม K2R) · `Theater Square` (Judgment ใช้ EN จริง) ·
    # `Dream-Line` = รูปที่ LJ สะกดจริง (มีขีด) ต่างจาก `dreamline` ที่ลิสต์เดิมมี
    # เพิ่ม 26 ส.ค. 2026 (sprint 15 · นักแปล batch_122) — `Big Splash` = ชื่อเล่นของทฤษฎี
    # giant-impact ที่ต้นฉบับใส่วงเล็บไว้เอง · `SOS` = ข้อความบนป้ายจริงในเกม (สัญลักษณ์สากล)
    "big splash", "sos",
    # เพิ่ม 26 ส.ค. 2026 (sprint 15 · นักแปล batch_125) — ชื่อบริษัทบังหน้าสมมติ + ชื่อสตูดิโอเกม
    "devenir", "god-tier games",
    # เพิ่ม 26 ส.ค. 2026 (sprint 15 · นักแปล batch_124) — `Happy` = ตัวอักษร H ในชื่อเล่นที่
    # คำบรรยายอธิบายมุกด้วยตัวเอง ("The H stands for Happy") · `aufheben` = ศัพท์ปรัชญาเยอรมัน
    # ที่ต้นฉบับใช้อวดภูมิ (มุกของฮิกาวะ) — แปลแล้วมุกหาย
    "happy", "aufheben",
    "mirai", "hama of the dead", "master system", "super hang-on", "theater square",
    "dream-line", "lambda",
    "quadra", "cab angus", "sega", "sony", "microsoft", "xbox", "windows", "amd", "nvidia",
    "fps", "hdr", "vsync", "hd", "sd", "pc", "ps4", "ps5", "id", "sp", "ex", "vr", "tv",
    # เพิ่ม 26 ส.ค. 2026 (sprint 15 · นักแปล batch_126) — Judgment ship "เครื่องในวัว BBQ" เอง
    "bbq",
    "double quickstep", "quickstep strike", "quickstep cancel", "asahi", "justis",
    "puyo puyo", "battle royale", "addc", "ad-9", "stijl", "wife eye", "ufo catcher", "l'amant",

    # audit 21 ส.ค. 2026 (ผู้ตรวจ Latin-leftover ทั้งโปรเจกต์) — กองที่ 1 "คง EN ถูกต้อง"
    # ชื่อเกมอาร์เคด/แบรนด์จริงที่ล็อกใน glossary.md §"ชื่อเกมที่คง EN" + คง EN
    "out run", "fighting vipers", "fantasy zone", "space harrier", "championship motor raid",
    "motor raid", "ufo catcher", "koi-koi", "koi koi", "don quijote", "jungle boy",
    "super monkey ball", "dartslive", "dartslive card", "final showdown", "vf", "vf2", "fs",
    "kitty kat", "d&c", "kj", "kj art", "g.i", "g.i.", "yagami system", "ryu ga gotoku studio",
    # ตัวละครแบรนด์ SEGA ในตัวเกม (Fighting Vipers / Super Monkey Ball) — ชื่อคาแรกเตอร์จริง ไม่แปล
    "bahn", "tokio", "raxel", "sanman", "picky", "grace", "honey", "aiai", "gongon", "meemee",
    # เพิ่ม 26 ส.ค. 2026 (sprint 15 · นักแปล batch_128) — `Baby` = ตัวละคร Super Monkey Ball
    # (คำบรรยายบอกเองว่า "A plush of Baby from Super Monkey Ball") · `Dice-and-Cubers` =
    # ชื่อเล่นแฟนเกม Dice & Cube ที่คง EN อยู่แล้ว
    "baby", "dice-and-cubers",
    # ชื่อคอร์ส/โต๊ะในมินิเกม VR (Dice & Cube / Motor Raid) — คง EN ตามชื่อแบรนด์
    "simple road", "wide way", "northern canyon", "breakthrough cafe", "pipeline",
    # เพิ่ม 26 ส.ค. 2026 (sprint 15 · ผู้ตรวจ batch_121) — ชื่อด่านสเกตบอร์ด/แข่งรถของ LJ
    # หลักฐาน: `Northward Bound` มี ref_tm คง EN อยู่แล้วในกลุ่ม bins เดียวกัน (ความสม่ำเสมอในชุด)
    # ⚠ `combo park` / `section jam` ต้นฉบับ **มีช่องว่างท้ายคีย์** ต้องคงไว้ตอนแปล
    "northward bound", "gate to gate", "circumnavigator", "bayside park", "funhouse",
    "k-town rush", "hangtime", "stir-crazy", "wormhole", "romantique", "devil's way",
    "skater paradise", "get some air", "flank the bank", "radical rail", "combo park",
    "section jam",
    # ชื่อรุ่นพาหนะที่ LJ ship เป็นคีย์คง EN อยู่แล้ว (`Speed Bow` -> `Speed Bow`)
    "speed bow", "lambda 250", "drift army", "cocta",
    "lullaby mahjong", "modern mahjong", "koro-nyan", "sugorokuhacks",
    # ตัวย่อ UI/สถิติ/กราฟิกทั่วเกม — คง EN ตามธรรมเนียมเมนู
    "lv", "hp", "dna", "qr", "gps", "dlc", "mk", "max", "reverse", "ui", "npc", "caution", "ad",
    "challenge course", "home run course",
    "dlss", "xess", "gpu", "xe-hpg", "fov", "anti-aliasing", "screen space ambient occlusion",
    "ai super resolution", "intel xe super sampling", "capture gallery", "options",
    "new game+", "vip", "iq", "ii", "iii", "iv", "ver", "bull",
    # ศัพท์นับแต้มปาลูกดอก — Ton/Three in a Bed/White Horse ล็อกคง EN (เคาะ sprint 10 · ผู้ตรวจ batch_078)
    # ⚠ แก้คอมเมนต์ 26 ส.ค. 2026 (sprint 15 · ผู้ตรวจ batch_128): เดิมอ้าง `glossary.md` หัวข้อ
    # "ศัพท์ดาร์ท" ซึ่ง **ไม่มีอยู่ในไฟล์จริง** (grep ได้ 0 จุด) — คำล็อกอยู่ที่ลิสต์นี้ที่เดียว
    # ⚠ ใช้กับ**ศัพท์การนับแต้ม**เท่านั้น · ชื่อระดับอุปกรณ์ (Beginner/Standard/Miracle/Premium Darts)
    #   ทับศัพท์ไทยตามปกติ ไม่เข้าลิสต์นี้
    "ton", "three in a bed", "white horse",
    # เพลง/สินค้า Haruka Sawamura + มุกเล่นคำที่ lead ยืนยันคง EN
    "so much more", "dreamline", "t-set", "japan dome", "amidst a dream", "nice dice",
    # เพิ่ม 26 ส.ค. 2026 (sprint 15 · กฎ I7) — ชื่อเพลง/แทร็ก/หนังเปิดเกม จากตาราง
    # `minigame_dance_music_data` / `title_movie` · บรรทัดฐานเดียวกับ Like A Butterfly ฯลฯ
    # ⚠ `girls` / `opening` เป็นชื่อแทร็ก **ไม่ใช่คำทั่วไป** — ref_tm แปลผิดทั้งสองคีย์
    # (ref_tm ให้ "เหล่าสาวๆ" และ "เปิดฉาก") ดู sprint15_locks §5.6
    "let's dance", "esmeralda", "long drill on the beach", "girls", "opening",
    "open beta boyz",
    # เพิ่ม 26 ส.ค. 2026 (sprint 15 · lead) — **ฉลากเหล้าจริงบนขวด** ที่กฎ I1 สั่งให้คง EN
    # หลักฐาน: Judgment ship ฉลากเต็มเป็น EN ทั้งหมด 6 คีย์ (Bushmills 10 Year-Old Single Malt ·
    # Ben Nevis Single Malt 10 Years · Taketsuru Pure Malt · Yoichi Single Malt ·
    # Nikka Whisky Black Clear · Asahi Orion Draft) และ ref_tm ของ LJ ก็ทำแบบเดียวกัน
    # ⚠ ใช้กับ **ชื่อขวด** เท่านั้น — เครื่องดื่มผสมยังทับศัพท์ไทย (ไฮบอลคาคุ · ไฮบอลจิมบีม)
    # เติมชุดที่เหลือหลังแปล b127 จริง (26 ส.ค. 2026): ฉลากที่โผล่ในไฟล์แต่ยังไม่อยู่ในลิสต์
    # ⚠ `cab` = Certified Angus Beef (ตราเนื้อจริง) · `epi` = คำฝรั่งเศสที่คำบรรยายอธิบายความหมายเอง
    "hibiki", "bowmore", "laphroaig", "kyogetsu", "kyogetsu green", "cab", "epi",
    "yamazaki", "hakushu", "the macallan", "macallan", "glenfiddich", "ballantine",
    "ballantine's", "the premium malt", "the premium malt's", "suntory", "suntory brandy",
    "suntory old whisky", "v.s.o.p", "vsop", "bushmills", "ben nevis", "taketsuru",
    "yoichi", "nikka", "nikka whisky", "jim beam", "chivas", "chivas regal",

    # เพิ่มเติม 21 ส.ค. 2026 — คำเดี่ยว/วลีคง EN ที่ยืนยันจาก precedent ใน master_th
    "ufo", "un", "deux", "trois", "a-z", "lullaby", "modern", "paradise", "yagami", "xl",
    "j-pop", "new game", "dice and cube", "yagami system", "kotd",
}
TAG_RE = re.compile(r"<[^>]*>|\$\{[^}]*\}|%[sd]|~[^~]*~|\[[a-z]{1,2}\]")
# Chatter (แอป SNS ในเกม) ใช้ @handle / #hashtag ปลอมของ NPC เป็นร้อย ๆ ชื่อ — พวกนี้
# "คง EN ถูกต้อง" เสมอ (ไม่มีใครแปล handle บนโซเชียล) แต่แจกแจงทีละชื่อใน KEEP_EN ไม่ไหว
# (ชื่อใหม่โผล่ทุก batch) จึง mask ทิ้งเชิงโครงสร้างแทน — audit 21 ส.ค. 2026
HANDLE_RE = re.compile(r"[@#][A-Za-z0-9_]+")
LATIN_RE = re.compile(r"[A-Za-z][A-Za-z'&.\- ]{1,30}[A-Za-z]|[A-Za-z]{2,}")
THAI_RE = re.compile(r"[฀-๿]")


def scan(pairs):
    hits = collections.Counter()
    where = collections.defaultdict(list)
    for k, v in pairs:
        if not THAI_RE.search(v):      # คำแปลที่คง EN ทั้งค่า = ตั้งใจ ไม่ใช่ตกค้าง
            continue
        clean = TAG_RE.sub(" ", v)
        clean = HANDLE_RE.sub(" ", clean)   # mask @handle / #hashtag ของ Chatter ก่อนสแกน
        for m in LATIN_RE.findall(clean):
            term = m.strip(" .-'&")
            if len(term) < 2:
                continue
            low = " ".join(term.lower().split())  # ยุบช่องว่างซ้ำจาก tag ที่ถูกตัดออก (เช่น <font_kind=...>and</font_kind>)
            if low in KEEP_EN:
                continue
            # เดิมใช้ `w in low` กับทุกคำ ทำให้คำสั้นอย่าง id/ex/sp/pc กลืนคำอื่นทั้งกอง
            # (เช่น "Rapid" มี "id" · "Extra" มี "ex") — ตอนนี้เทียบเป็นคำ ๆ แทน
            if any(w in low.split() for w in KEEP_EN):
                continue
            if any(len(w) >= 4 and (low.startswith(w) or w in low) for w in KEEP_EN):
                continue
            hits[term] += 1
            if len(where[term]) < 3:
                where[term].append(k[:60])
    return hits, where


# ด่านกลับทาง (เพิ่ม 26 ส.ค. 2026): จับคำที่ **ต้องคง EN แต่ถูกทับศัพท์เป็นไทย**
# ที่มา: ผู้ตรวจ batch_044 เจอ `AI` -> "เอไอ" ทั้งที่ล็อกให้คง EN — สคริปต์เดิมจับไม่ได้เลย
# เพราะมันหาแต่ "ละตินที่ตกค้าง" ไม่ได้หา "ละตินที่หายไป"
# ใส่เฉพาะคู่ที่ **แน่ใจว่ารูปไทยไม่มีความหมายอื่น** (คำสั้น ๆ ที่ชนคำไทยทั่วไปห้ามใส่)
MUST_STAY_EN = {
    "เอไอ": "AI", "ซีจีไอ": "CGI", "ซีจี": "CG",
    "แชตเตอร์": "Chatter", "แชทเตอร์": "Chatter",
    "อาร์เค": "RK", "เอ็มอาร์ซี": "MRC",
    "บัซซี่ เซิร์ชเชอร์": "Buzzy Searcher", "บัซ รีเสิร์ชเชอร์": "Buzz Researcher",
    "เพลย์สเตชัน": "PlayStation", "สตีม": "Steam",
}


# คำไทยที่ยาวกว่าและ "มีรูปข้างบนอยู่ข้างใน" โดยบังเอิญ — ต้องหักออกก่อนนับ
# ภาษาไทยไม่เว้นวรรค การเช็ค `th in v` เฉย ๆ จึงจับคำอื่นติดมาด้วย
# เจอ 26 ส.ค. 2026 (sprint 15 · นักแปล batch_126): `Sasaki Arcade` -> "ซาซากิอาร์เคด"
# ถูกเตือนว่าควรเป็น "RK" เพราะ **"อาร์เคด" มี "อาร์เค" อยู่ข้างใน** — ไม่เกี่ยวกับแก๊ง RK เลย
FALSE_FRIENDS = {
    "อาร์เค": ["อาร์เคด"],          # arcade
    "ซีจี": ["ซีจีไอ"],             # CGI นับแยกอยู่แล้ว ไม่ให้นับซ้ำเป็น CG
    "สตีม": ["สตีมเมอร์", "สตีมด์"],
}


def scan_missing_en(pairs):
    """คืน {รูปไทยที่ไม่ควรมี: [(คำ EN ที่ควรใช้, ตัวอย่างคีย์)]}"""
    hits = collections.Counter()
    where = collections.defaultdict(list)
    for k, v in pairs:
        for th, en in MUST_STAY_EN.items():
            n = v.count(th)
            if not n:
                continue
            for longer in FALSE_FRIENDS.get(th, []):
                n -= v.count(longer)
            if n <= 0:
                continue
            hits[th] += n
            if len(where[th]) < 3:
                where[th].append((en, k[:60]))
    return hits, where


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--done", action="store_true", help="ตรวจไฟล์ done แทน master_th")
    ap.add_argument("--only", help="เจาะ batch เดียว (ใช้กับ --done โดยอัตโนมัติ)")
    a = ap.parse_args()

    pairs = []
    if a.only or a.done:
        pat = "batch_%s.done.json" % a.only if a.only else "*.done.json"
        for p in sorted((paths.TRANSLATIONS / "done").glob(pat)):
            d = json.load(io.open(p, encoding="utf-8"))
            pairs += list(d["strings"].items())
    else:
        pairs = list(json.load(io.open(paths.MASTER_TH, encoding="utf-8")).items())

    hits, where = scan(pairs)
    print("ตรวจ %s คู่ · พบคำละตินตกค้าง %d แบบ" % (format(len(pairs), ","), len(hits)))
    for term, n in hits.most_common(60):
        print("  %-34s x%-4d  เช่น: %s" % (term, n, where[term][0]))
    if len(hits) > 60:
        print("  ... อีก %d แบบ" % (len(hits) - 60))

    miss, mwhere = scan_missing_en(pairs)
    print("")
    print("คำที่ต้องคง EN แต่ถูกทับศัพท์: %d แบบ" % len(miss))
    for th, n in miss.most_common(40):
        en, key = mwhere[th][0]
        print("  %-22s x%-4d  ควรเป็น %-16s เช่น: %s" % (th, n, en, key))
    return 1 if miss else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
