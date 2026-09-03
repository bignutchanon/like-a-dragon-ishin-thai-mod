#!/usr/bin/env python3
"""ทับศัพท์ชื่อญี่ปุ่น (โรมาจิ) -> ไทย ตามกฎที่สายโปรเจกต์นี้ใช้

⚠ **เป็นตัวช่วยร่างเท่านั้น ไม่ใช่คำตัดสิน** — ลำดับที่ถูกต้องคือ
   1) คำที่ล็อกแล้วในภาคก่อน  2) คำที่เคย ship แล้วใน TM  3) กฎในไฟล์นี้ (ต้องให้ lead เคาะ)
   `scripts/make_name_proposals.py` ทำตามลำดับนี้ให้อยู่แล้ว

กฎที่ใช้ (ประมวลจากคำที่ ship แล้วในภาค K3/Gaiden/Y7/Y8/Judgment):
  สระ   a→า (ท้ายคำ ะ) · i→ิ · u→ุ · e→เ- (ท้ายคำ เ-ะ) · o→โ- (ท้ายคำ โ-ะ)
        ai→ไ- · ei→เ- (เคโกะ) · ou/oo→โ- · uu/ii→ยาว
  พยัญชนะ k ต้นคำ→ค · k กลางคำ→ก (โทโดโรกิ · ซากุระ) · g→ก (อิการาชิ)
        t ต้นคำ→ท (โทโดโรกิ) · t กลางคำ→ต (วาตานาเบะ · มินาโตะ)
        s→ซ แต่ su→สุ · shi→ชิ · tsu→สึ (ต้นคำ) / ตสึ (กลางคำ: มัตสึอิ)
        n ท้ายพยางค์→น (เคนโตะ · เซนดะ) · ry/ky/gy...→เ-ีย (เคียวโกะ)
  ⚠ งานที่ ship มาแล้วเองก็ไม่นิ่ง 100% (ซากุระ กุ vs ซาคุมะ คุ) — จึงต้องมีคนเคาะเสมอ

ใช้:
  python scripts/romaji_to_thai.py Amasawa Kuwana Okitegawa
  python scripts/romaji_to_thai.py --selftest      # เทียบกับคำที่ ship แล้ว 20 คำ


## ⚠ ขอบเขตที่เชื่อไม่ได้ — ต้องตรวจด้วยมือ (ผู้ตรวจ batch_024/025 ยืนยัน 2 ก.ย. 2026)

เครื่องมือนี้ตัดพยางค์ด้วย regex จึงแยก **ขอบเขตสระที่ติดกัน** ไม่ออก ผลที่ออกมา "ดูเหมือนถูก"
แต่ผิด และไม่มีสัญญาณเตือนใด ๆ:

| โรมาจิ | เครื่องมือให้ | ที่ถูก | สาเหตุ |
|---|---|---|---|
| Matsuura (松浦) | มาตูระ | **มัตสึอุระ** | อ่าน `ma + tsuu + ra` แทน `matsu + ura` |
| Ouchi (大内) | โอจิ | **โออุจิ** | อ่าน `ou` เป็นสระยาว ō แทน `o + u` |

**กติกา**: ใช้ผลของเครื่องมือเป็น *ร่าง* เท่านั้น · ชื่อที่มีสระสองตัวติดกัน (uu · ou · ua · ии)
หรือมี `tsu` อยู่กลางคำ **ต้องตรวจกับคันจิใน `ref_ja` ด้วยมือทุกครั้ง**
และคำที่อยู่ใน `translations/name_locks.json` แล้วให้ยึดไฟล์นั้นเสมอ ไม่ต้องรันเครื่องมือ
"""
import argparse
import re
import sys

# (โรมาจิพยางค์ -> ไทย) เขียนเป็นตารางพยางค์ตรง ๆ อ่านง่ายกว่าประกอบจากพยัญชนะ+สระ
# รูปแบบ: {พยางค์: (รูปกลางคำ, รูปท้ายคำ)}
SYL = {}


def _add(rom, mid, end=None):
    SYL[rom] = (mid, end if end is not None else mid)


_V = {"a": ("า", "ะ"), "i": ("ิ", "ิ"), "u": ("ุ", "ุ"), "e": ("เ", "เ~ะ"), "o": ("โ", "โ~ะ")}
_C_MID = {"k": "ก", "g": "ก", "s": "ซ", "z": "ซ", "j": "จ", "t": "ต", "d": "ด", "n": "น",
          "h": "ฮ", "f": "ฟ", "b": "บ", "p": "พ", "m": "ม", "y": "ย", "r": "ร", "w": "ว"}
_C_INIT = dict(_C_MID, k="ค", t="ท")


# พยัญชนะสองตัวที่ไม่ได้อยู่ในตาราง IRREGULAR ทุกสระ (กันพลาดตอนเจอสระแปลก)
_C_EXTRA = {"sh": "ช", "ch": "ช", "ts": "ต", "ky": "ค", "gy": "ก", "ry": "ร",
            "ny": "น", "hy": "ฮ", "by": "บ", "py": "พ", "my": "ม"}


def _build(cons, vowel, initial):
    table = dict(_C_INIT if initial else _C_MID, **_C_EXTRA)
    c = table.get(cons, "อ") if cons else "อ"
    long_v, end_v = _V[vowel]
    if vowel in ("e", "o"):
        mid = long_v + c
        end = end_v.replace("~", c)
    else:
        mid = c + long_v
        end = c + end_v
    return mid, end


IRREGULAR = {           # พยางค์ที่ไม่เข้ากฎ (ตามที่ ship แล้ว)
    "shi": ("ชิ", "ชิ"), "chi": ("จิ", "จิ"), "tsu": ("สึ", "สึ"),
    "su": ("สุ", "สุ"), "fu": ("ฟุ", "ฟุ"), "zu": ("ซึ", "ซึ"),   # zu = ซึ (กติกา CLAUDE.md) "shu": ("ชุ", "ชุ"), "sho": ("โช", "โชะ"),
    "sha": ("ชา", "ชะ"), "cha": ("ชา", "ชะ"), "cho": ("โช", "โชะ"), "chu": ("ชุ", "ชุ"),
    "ji": ("จิ", "จิ"), "ja": ("จา", "จะ"), "jo": ("โจ", "โจะ"), "ju": ("จุ", "จุ"),
    "she": ("เช", "เชะ"), "che": ("เช", "เชะ"), "je": ("เจ", "เจะ"),
    "kya": ("เคีย", "เคีย"), "kyo": ("เคียว", "เคียว"), "kyu": ("คิว", "คิว"),
    "gya": ("เกีย", "เกีย"), "gyo": ("เกียว", "เกียว"), "gyu": ("กิว", "กิว"),
    "rya": ("เรีย", "เรีย"), "ryo": ("เรียว", "เรียว"), "ryu": ("ริว", "ริว"),
    "nya": ("เนีย", "เนีย"), "nyo": ("เนียว", "เนียว"), "nyu": ("นิว", "นิว"),
    "hya": ("เฮีย", "เฮีย"), "hyo": ("เฮียว", "เฮียว"), "hyu": ("ฮิว", "ฮิว"),
    "bya": ("เบีย", "เบีย"), "byo": ("เบียว", "เบียว"), "byu": ("บิว", "บิว"),
    "pya": ("เพีย", "เพีย"), "pyo": ("เพียว", "เพียว"), "pyu": ("พิว", "พิว"),
    "mya": ("เมีย", "เมีย"), "myo": ("เมียว", "เมียว"), "myu": ("มิว", "มิว"),
}

SYL_RE = re.compile(
    r"(?P<syl>ky|gy|ry|ny|hy|by|py|my|sh|ch|ts|j|[kgszjtdnhfbpmyrw])?"
    r"(?P<vow>ai|ei|ou|oo|uu|ii|[aiueo])"
    r"(?P<nasal>n(?![aiueoy]))?")

LOCKED = {
    "yagami": "ยากามิ", "kaito": "ไคโตะ", "sugiura": "ซุกิอุระ", "tsukumo": "สึคุโมะ",
    "shirosaki": "ชิโรซากิ", "genda": "เก็นดะ", "hoshino": "โฮชิโนะ",
    "higashi": "ฮิงาชิ", "fujii": "ฟุจิอิ", "matsugane": "มัตสึกาเนะ",
    "ogikubo": "โอกิคุโบะ", "takayuki": "ทาคายูกิ", "masaharu": "มาซาฮารุ",
    "makoto": "มาโคโตะ", "saori": "ซาโอริ", "ryuzo": "ริวโซ", "toru": "โทรุ",
    "fumiya": "ฟุมิยะ", "mafuyu": "มาฟุยุ", "seiryo": "เซเรียว",
}


def _syl_thai(cons, vow, initial, final):
    """คืนรูปไทยของพยางค์เดียว"""
    key = (cons or "") + vow
    if key in IRREGULAR:
        return IRREGULAR[key][1 if final else 0]
    if vow in ("ai", "ei", "ou", "oo", "uu", "ii"):
        table = dict(_C_INIT if initial else _C_MID, **_C_EXTRA)
        c = table.get(cons or "", "อ") if cons else "อ"
        if vow == "ai":
            return "ไ" + c
        if vow == "ei":
            return "เ" + c
        if vow in ("ou", "oo"):
            return "โ" + c
        if vow == "uu":
            return c + "ู"
        return c + "ี"
    mid, end = _build(cons or "", vow, initial)
    return end if final else mid


def convert(name):
    """คืน (คำไทย, ที่มา) — 'locked' หรือ 'rule'"""
    key = name.strip().lower()
    if key in LOCKED:
        return LOCKED[key], "locked"

    words = []
    for word in re.split(r"[\s\-']+", name.strip()):
        low = word.lower()
        if not low:
            continue
        syls, pos = [], 0
        while pos < len(low):
            # เสียงซ้อน (kk/tt/ss/pp) -> ไม้หันอากาศ + ตัวสะกดของพยางค์ก่อนหน้า
            if pos + 1 < len(low) and low[pos] == low[pos + 1] and low[pos] in "kgstpbdz":
                syls.append(("GEM", low[pos]))
                pos += 1
                continue
            m = SYL_RE.match(low, pos)
            if not m or m.end() == pos:
                pos += 1
                continue
            syls.append(("SYL", m.group("syl"), m.group("vow"), m.group("nasal")))
            pos = m.end()

        out = []
        for i, item in enumerate(syls):
            if item[0] == "GEM":
                if out:
                    nxt = syls[i + 1] if i + 1 < len(syls) else None
                    tail = "ต" if nxt and (nxt[1] or "") in ("t", "ts", "ch") else \
                           ("ก" if nxt and (nxt[1] or "") in ("k", "g") else "ด")
                    out[-1] = re.sub(r"า$", "ั", out[-1]) + tail if out[-1].endswith("า") \
                        else out[-1] + tail
                continue
            _, cons, vow, nasal = item
            initial = i == 0
            # "tsu" กลางคำเขียน ตสึ และดึงสระยาวของพยางค์ก่อนหน้าให้เป็นไม้หันอากาศ
            # (มัตสึอิ · มัตสึกาเนะ · อากุตสึ) — ต่างจาก tsu ต้นคำที่เป็น สึ (สึคุโมะ)
            if cons == "ts" and vow == "u" and not initial and out:
                out[-1] = re.sub(r"า$", "ั", out[-1])
                out.append("ตสึ" + ("น" if nasal else ""))
                continue
            final = (i == len(syls) - 1) and not nasal
            thai = _syl_thai(cons, vow, initial, final)
            if nasal:
                # ん + b/p ออกเสียง ม (ซัมบง...) · นอกนั้น น (เคนโตะ · เคนโมจิ · เซนดะ)
                nxt = syls[i + 1] if i + 1 < len(syls) else None
                nxt_c = (nxt[1] or "") if nxt and nxt[0] == "SYL" else ""
                if nxt_c in ("b", "p"):
                    tail = "ม"
                else:
                    tail = "น"
                thai = re.sub(r"า$", "ั", thai) + tail
            out.append(thai)
        words.append("".join(out))
    return " ".join(words), "rule"


# ชุดทดสอบ = คำที่ **ship ไปแล้วจริง** ในภาคก่อน (ไม่ใช่คำที่เดาเอง)
SELFTEST = [
    ("Yagami", "ยากามิ"), ("Kaito", "ไคโตะ"), ("Tsukumo", "สึคุโมะ"),
    ("Kyoko", "เคียวโกะ"), ("Jun", "จุน"), ("Minato", "มินาโตะ"),
    ("Nishizono", "นิชิโซโนะ"), ("Tsukino", "สึกิโนะ"), ("Watanabe", "วาตานาเบะ"),
    ("Mamiya", "มามิยะ"), ("Todoroki", "โทโดโรกิ"), ("Igarashi", "อิการาชิ"),
    ("Sakura", "ซากุระ"), ("Kento", "เคนโตะ"), ("Okazaki", "โอกาซากิ"),
    ("Matsui", "มัตสึอิ"), ("Takano", "ทาคาโนะ"), ("Tashiro", "ทาชิโระ"),
    ("Senda", "เซนดะ"), ("Kosuke", "โคสุเกะ"), ("Koga", "โคกะ"),
    ("Keiko", "เคโกะ"), ("Minami", "มินามิ"), ("Mori", "โมริ"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("names", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        ok = 0
        for en, want in SELFTEST:
            got, how = convert(en)
            same = got == want
            ok += same
            print("%s %-12s -> %-14s (ship แล้ว: %-14s · %s)"
                  % ("OK  " if same else "ต่าง", en, got, want, how))
        print("\nตรงกับของที่ ship แล้ว %d/%d — ที่ต่างคือจุดที่กฎกับงานเก่าไม่ตรงกัน "
              "ต้องให้ lead เคาะ" % (ok, len(SELFTEST)))
        return 0

    for n in a.names:
        th, how = convert(n)
        print("%-20s %-22s [%s]" % (n, th, how))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
