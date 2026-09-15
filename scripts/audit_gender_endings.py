#!/usr/bin/env python3
"""ไล่คำแปลบทพูด .msg ทั้งคลัง เทียบคำลงท้ายบอกเพศในภาษาไทยกับเพศผู้พูดรายบรรทัด

ทำไมต้องมี (15 ก.ย. 2026): ตาราง `scene_gender` เคยตีบทของตัวละครหญิงเป็นชายทั้งฉาก และคลื่นคำลงท้าย §0.59
ใช้ตารางนั้นตัดสิน — ต้องหาว่ามีคำแปลที่ใส่คำลงท้ายผิดเพศค้างอยู่เท่าไร หลังจากเพิ่มชั้นคิวเสียงรายบรรทัด
(`build_voice_gender.py`) และตัดฉากที่มีสองเพศออกจาก `scene_gender` แล้ว

ลำดับชั้นเพศต่อบรรทัด (เหมือน make_polish_packets.gender_of):
  gender_lines (lead) > คิวเสียงของบรรทัด > เครื่องหมายญี่ปุ่นในบรรทัด > ผู้ตรวจรายบรรทัด > ผู้ตรวจต่อสตริง > ฉาก

`master_th.json` ผูกคำแปลกับสตริงอังกฤษ — สตริงเดียวถูกพูดได้หลายที่ จึงจัดชั้นต่อ "สตริง":
  wrong        ทุกที่ที่รู้เพศเป็นเพศเดียว แต่คำแปลใช้คำลงท้ายของอีกเพศ           -> ต้องแก้คำแปล
  shared_mixed ที่รู้เพศมีทั้งชายและหญิง และคำแปลมีคำลงท้ายบอกเพศ                 -> ต้องเขียนกลางเพศ
  no_evidence  ไม่มีที่ไหนรู้เพศเลย แต่คำแปลมีคำลงท้ายบอกเพศ                      -> รายงาน (ด่าน G ของ merge_qc คุมอยู่)
  partial      บางบรรทัดรู้เพศ บางบรรทัดไม่รู้ แต่คำแปล (ผูก EN) มีคำลงท้ายบอกเพศ   -> รายงาน
  both         คำแปลมีคำลงท้ายทั้งสองเพศในสตริงเดียว (ส่วนใหญ่เป็นบทสองคนในกล่องเดียว) -> รายงาน

ใช้: python scripts/audit_gender_endings.py   -> work/gender_fix/conflicts.json
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                                  # noqa: E402
import merge_qc as M                          # noqa: E402
import thai_pronouns as tp                    # noqa: E402
from make_gender_packets import DEAD_FILES    # noqa: E402

OUT_DIR = paths.PROJECT / "work" / "gender_fix"


def load_keys(name):
    p = paths.TRANSLATIONS / name
    raw = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    return {k: v for k, v in raw.items() if isinstance(v, dict) and v.get("gender") in ("male", "female")}


def load_name_gender():
    """ชื่อผู้พูดบนจอ -> เพศ จากทะเบียนที่อ้างไฟล์เกม (characters.json ชื่อสั้น · speakers.json) — สองทะเบียนขัด = ไม่ใช้"""
    out, bad = {}, set()
    chars = json.loads((paths.TRANSLATIONS / "characters.json").read_text(encoding="utf-8"))
    for group in chars.values():
        for c in group.values():
            if c.get("gender") in ("male", "female") and c.get("short"):
                out[c["short"]] = c["gender"]
    spk = json.loads((paths.TRANSLATIONS / "speakers.json").read_text(encoding="utf-8"))
    for name, s in spk.items():
        g = s.get("gender")
        if g not in ("male", "female") or name.startswith("id:"):
            continue
        if name in out and out[name] != g:
            bad.add(name)
        out.setdefault(name, g)
    for n in bad:
        out.pop(n, None)
    return out


def extra_rows():
    """บทพูดนอก .msg ที่ไฟล์เกมระบุผู้พูดรายแถว
    locres: namespace `X` คู่กับ `X_speaker` คีย์ต่อคีย์ (ซับคัตซีน)
    ARMP: `sound_speak_data` (บอลลูน NPC) · `sound_macan_cue_subtitle` — คอลัมน์ `speaker` อยู่แถวเดียวกับข้อความ"""
    rows = []
    loc = json.loads((paths.EXTRACTED / "locres" / "Game.en.json").read_text(encoding="utf-8"))
    strings = loc["strings"]
    flat = {(ns["ns"], e["key"]): strings[e["idx"]] for ns in loc["namespaces"] for e in ns["entries"]}
    for (ns, key), name in flat.items():
        if ns.endswith("_speaker") and flat.get((ns[:-len("_speaker")], key)):
            base = ns[:-len("_speaker")]
            rows.append({"key": "locres:%s/%s" % (base, key), "en": flat[(base, key)], "speaker": name})
    for table in ("sound_speak_data", "sound_macan_cue_subtitle"):
        p = paths.EXTRACTED / "db_en" / (table + ".bin.json")
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for k in d:
            if not k.isdigit() or not isinstance(d[k], dict):
                continue
            for rk, row in d[k].items():
                if not isinstance(row, dict) or not row.get("speaker"):
                    continue
                for col, val in row.items():
                    if col != "speaker" and isinstance(val, str) and val.strip():
                        rows.append({"key": "%s:%s#%s" % (table, rk, col), "en": val, "speaker": row["speaker"]})
    return rows


def main():
    voice = load_keys("gender_voice_keys.json")
    dkeys = load_keys("gender_dialogue_keys.json")
    master = json.loads(paths.MASTER_TH.read_text(encoding="utf-8"))
    rows = [r for r in json.loads((paths.EXTRACTED / "parallel" / "msg.json").read_text(encoding="utf-8"))
            if r["file"] not in DEAD_FILES and (r.get("en") or "").strip()]

    def gender_of(r):
        en, ja, key = r["en"], r.get("ja") or "", r["key"]
        for layer, g in (("line", M.line_gender(en)),
                         ("voice", (voice.get(key) or {}).get("gender")),
                         ("ja", M.ja_gender(ja)),
                         ("key", (dkeys.get(key) or {}).get("gender")),
                         ("dialogue", M.dialogue_gender(en)),
                         ("scene", M.scene_gender(en))):
            if g:
                return g, layer
        return None, None

    by_en = defaultdict(list)
    for r in rows:
        th = master.get(r["en"])
        if not th or th == r["en"]:
            continue
        g, layer = gender_of(r)
        by_en[r["en"]].append({"key": r["key"], "gender": g, "from": layer, "ja": r.get("ja") or "",
                               "labels": [x for x in (r.get("labels") or []) if len(x) < 40][:4]})

    name_gender = load_name_gender()
    n_extra = 0
    for r in extra_rows():
        th = master.get(r["en"])
        if not th or th == r["en"]:
            continue
        n_extra += 1
        g = M.line_gender(r["en"]) or name_gender.get(r["speaker"])
        by_en[r["en"]].append({"key": r["key"], "gender": g,
                               "from": ("speaker" if g else None), "ja": "", "labels": [r["speaker"]]})
    print("บทพูดนอก .msg ที่มีป้ายผู้พูดและมีคำแปล %d แถว (ชื่อผู้พูดที่รู้เพศ %d ชื่อ)" % (n_extra, len(name_gender)))

    out = defaultdict(list)
    for en, occ in by_en.items():
        th = master[en]
        th_m = bool(tp.RE_KHORAP.search(th) or tp.RE_KRAPHOM.search(th))
        th_f = bool(tp.RE_CHAOKHA.search(th) or tp.FEM_CASUAL.search(th))
        if not (th_m or th_f):
            continue
        gs = {o["gender"] for o in occ} - {None}
        if th_m and th_f:
            cls = "both"
        elif gs == {"female"} and th_m or gs == {"male"} and th_f:
            cls = "wrong"
        elif len(gs) == 2:
            cls = "shared_mixed"
        elif not gs:
            cls = "no_evidence"
        elif any(o["gender"] is None for o in occ):
            # บางที่มีหลักฐาน บางที่ไม่มี — master ผูก EN จึงลงคำลงท้ายให้ทุกที่ (15 ก.ย. 2026: "prize tickets"
            # โอกามิหญิง 1 บรรทัด + เชฟซูชิ 5 บรรทัดไม่มีหลักฐาน ได้ เจ้าค่ะ ทั้งหมด ด่านนี้เดิมมองไม่เห็น)
            cls = "partial"
        else:
            continue
        out[cls].append({"en": en, "th": th, "genders": sorted(gs), "occurrences": occ})

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "conflicts.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for cls in ("wrong", "shared_mixed", "no_evidence", "partial", "both"):
        layers = Counter(o["from"] for item in out[cls] for o in item["occurrences"] if o["gender"])
        print("%-13s %4d สตริง · ชั้นที่ให้เพศ %s" % (cls, len(out[cls]), dict(layers)))
    print("-> %s" % (OUT_DIR / "conflicts.json"))


if __name__ == "__main__":
    main()
