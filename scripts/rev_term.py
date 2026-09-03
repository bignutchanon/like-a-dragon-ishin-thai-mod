"""ผู้ตรวจ: นับรูปคำไทยของศัพท์หนึ่งทั้งคลัง (master + done ทุกก้อน) — ห้ามส่งไทยผ่าน CLI
usage: python scripts/rev_term.py <terms.json>   (ไฟล์ JSON = list ของ term อังกฤษ หรือ dict)
"""
import sys, json, glob, os, re, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

_pairs = None


def pairs():
    """[(en, th, src)] ทั้งคลัง: master + ไฟล์ done ทุกก้อน"""
    global _pairs
    if _pairs is None:
        _pairs = []
        m = json.load(open("translations/master_th.json", encoding="utf-8"))
        ms = m.get("strings", m)
        for en, th in ms.items():
            if isinstance(th, str):
                _pairs.append((en, th, "master"))
        for p in sorted(glob.glob("translations/done/*.done.json")):
            n = os.path.basename(p).replace(".done.json", "")
            for en, th in json.load(open(p, encoding="utf-8"))["strings"].items():
                _pairs.append((en, th, n))
    return _pairs


def en_term(term, show=0, exclude_src=()):
    """คำแปลไทยของทุกคู่ที่ EN มีคำนี้ — คืน Counter ของคำไทยที่พบร่วม"""
    rx = re.compile(re.escape(term), re.I)
    hits = [(en, th, s) for en, th, s in pairs()
            if rx.search(en) and s not in exclude_src]
    print(f"== EN {term!r}: {len(hits)} คู่")
    for en, th, s in hits[:show]:
        print(f"   [{s}] {en[:80]!r}")
        print(f"        {th[:100]}")
    return hits


def th_form(word, show=0, exclude_src=()):
    hits = [(en, th, s) for en, th, s in pairs()
            if word in th and s not in exclude_src]
    srcs = collections.Counter(s for _, _, s in hits)
    print(f"== TH {word!r}: {len(hits)} คู่ · ก้อน {dict(srcs.most_common(12))}")
    for en, th, s in hits[:show]:
        print(f"   [{s}] {en[:80]!r}")
        print(f"        {th[:100]}")
    return hits


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    for mode, word, show in spec:
        (en_term if mode == "en" else th_form)(word, show)
        print()
