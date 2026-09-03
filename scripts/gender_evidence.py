"""ตรวจหลักฐานเพศระดับไฟล์ฉากให้คีย์ที่ผู้แปล/ผู้ตรวจเสนอมา (lead ใช้ก่อนลง gender_lines.json)

เกณฑ์ที่โปรเจกต์ใช้ (sprint 15 · glossary §1.9.24):
  1. EN ของคีย์นั้นโผล่ใน **ไฟล์ฉากเดียว** เท่านั้น
  2. ไฟล์ฉากนั้นมีเครื่องหมายเพศฝั่งที่เสนอ > 0
  3. ไฟล์ฉากนั้น **ไม่มีเครื่องหมายเพศฝั่งตรงข้ามเลยสักแถว**
  4. บรรทัดนั้นยังไม่มีหลักฐานในตัวเอง (ถ้ามีอยู่แล้วก็ไม่ต้องล็อก)

ใช้: python scripts/gender_evidence.py MSG_061 MSG_062 ...
    เพิ่ม --propose เพื่อไล่ทางกลับ: บรรทัดที่ยัง**กลางเพศ** แต่ต้นฉบับสุภาพและฉากพิสูจน์เพศได้
    (คือคีย์ที่ "ล็อกได้" ถ้า lead ต้องการให้ใส่คำลงท้ายบอกเพศ)
พิมพ์รายการพร้อมตัวเลข — **ไม่เขียนไฟล์ใด ๆ**
"""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

import merge_qc as M                                   # noqa: E402
import thai_pronouns as tp                             # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PARALLEL = ROOT / "extracted" / "parallel" / "msg.json"
DONE = ROOT / "translations" / "done"
GL = ROOT / "translations" / "gender_lines.json"

# คำลงท้ายที่บอกเพศ — ถ้าบรรทัดไทยมีคำพวกนี้ ต้องมีหลักฐานรองรับ
FEMALE_TAILS = ("เจ้าค่ะ", "จ๊ะ", "จ้ะ", "เพคะ")


def load():
    rows = json.loads(PARALLEL.read_text(encoding="utf-8"))
    en2rows = collections.defaultdict(list)
    byfile = collections.defaultdict(list)
    for r in rows:
        if r.get("en"):
            en2rows[r["en"]].append(r)
        byfile[r.get("file")].append(r)
    scene = {
        f: collections.Counter(M.ja_gender(x.get("ja") or "") for x in rs)
        for f, rs in byfile.items()
    }
    return en2rows, scene


def propose(batches, en2rows, scene, gl) -> int:
    """คีย์ที่ยังกลางเพศ แต่ ref_ja สุภาพ + ฉากพิสูจน์เพศได้ = ล็อกได้ถ้า lead ต้องการ"""
    for b in batches:
        path = DONE / f"batch_{b}.done.json"
        if not path.exists():
            print(f"[ข้าม] ไม่พบ {path.name}")
            continue
        strings = json.loads(path.read_text(encoding="utf-8"))["strings"]
        cand = collections.defaultdict(list)
        for en, th in strings.items():
            if not th or en in gl:
                continue
            if tp.RE_KHORAP.search(th) or any(t in th for t in FEMALE_TAILS):
                continue                       # มีคำลงท้ายอยู่แล้ว
            rs = en2rows.get(en, [])
            ja = " ".join(r.get("ja") or "" for r in rs)
            if not ja or M.ja_gender(ja) is not None:
                continue                       # ไม่มี ja หรือมีหลักฐานในตัวเองแล้ว
            if not any(m in ja for m in M.POLITE_JA):
                continue                       # ต้นฉบับไม่ได้สุภาพ ไม่ต้องเติมคำลงท้าย
            files = {r["file"] for r in rs}
            if len(files) != 1:
                continue
            f = files.pop()
            g = scene.get(f, {})
            if g.get("male", 0) > 0 and g.get("female", 0) == 0:
                cand[(f, "male")].append((en, rs[0]["line"]))
            elif g.get("female", 0) > 0 and g.get("male", 0) == 0:
                cand[(f, "female")].append((en, rs[0]["line"]))
        total = sum(len(v) for v in cand.values())
        print(f"\n##### {b} · คีย์ที่ล็อกได้ {total}")
        for (f, want), items in sorted(cand.items()):
            g = scene.get(f, {})
            print(f"  {f} -> {want} · ฉากมี ชาย {g.get('male',0)} · หญิง {g.get('female',0)}"
                  f" · {len(items)} คีย์")
            for en, line in items[:4]:
                print(f"      #{line:03d} {en[:66]!r}")
            if len(items) > 4:
                print(f"      ... อีก {len(items)-4} คีย์")
    return 0


def main(batches) -> int:
    en2rows, scene = load()
    gl = json.loads(GL.read_text(encoding="utf-8"))
    for b in batches:
        path = DONE / f"batch_{b}.done.json"
        if not path.exists():
            print(f"[ข้าม] ไม่พบ {path.name}")
            continue
        strings = json.loads(path.read_text(encoding="utf-8"))["strings"]
        ok, bad = [], []
        for en, th in strings.items():
            if not th:
                continue
            male = bool(tp.RE_KHORAP.search(th))
            female = any(t in th for t in FEMALE_TAILS)
            if not (male or female):
                continue
            want = "male" if male else "female"
            if en in gl:
                continue
            rs = en2rows.get(en, [])
            ja = " ".join(r.get("ja") or "" for r in rs)
            if M.ja_gender(ja) is not None:
                continue                       # มีหลักฐานในบรรทัดเองแล้ว
            files = {r["file"] for r in rs}
            if len(files) != 1:
                bad.append((en, want, f"EN ใช้ร่วม {len(files)} ฉาก"))
                continue
            f = files.pop()
            g = scene.get(f, {})
            other = "female" if want == "male" else "male"
            if g.get(want, 0) == 0:
                bad.append((en, want, f"ฉาก {f} ไม่มีเครื่องหมาย {want} เลย"))
            elif g.get(other, 0) != 0:
                bad.append((en, want, f"ฉาก {f} มี {other} {g[other]} แถว — ฉากผสม"))
            else:
                ok.append((en, want, f, g.get(want, 0), rs[0]["line"]))
        print(f"\n##### {b} · ผ่านเกณฑ์ {len(ok)} · ไม่ผ่าน {len(bad)}")
        for en, want, f, n, line in ok:
            print(f"  [ผ่าน] {want} · {f}#{line:03d} · ฉากมี {want} {n} แถว · หญิง/ชายตรงข้าม 0")
            print(f"         {en[:70]!r}")
        for en, want, why in bad:
            print(f"  [ไม่ผ่าน] {want} · {why}\n            {en[:70]!r}")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit("ใช้: python scripts/gender_evidence.py [--propose] MSG_061 MSG_062 ...")
    if "--propose" in sys.argv[1:]:
        _en2rows, _scene = load()
        _gl = json.loads(GL.read_text(encoding="utf-8"))
        raise SystemExit(propose(args, _en2rows, _scene, _gl))
    raise SystemExit(main(args))
