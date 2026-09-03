# ISHTH — Like a Dragon: Ishin! ม็อดแปลไทย

ภาคสุดท้ายในซีรีส์ RGG ของชุดโปรเจกต์นี้ · โปรเจกต์อยู่ที่ `D:\Projects\like-a-dragon-ishin`

## ⚠ อ่านก่อนอย่างอื่น — ภาคนี้ไม่ใช่ Dragon Engine

Like a Dragon: Ishin! (รีเมค 2023) สร้างบน **Unreal Engine 4.27**
ชั้นคอนเทนเนอร์จึงเป็น `.pak` + IoStore (`.utoc`/`.ucas`) **ไม่มี par · ไม่มี ARMP · ไม่มี SRMM/Parless**
→ `ParTool.exe` · `reARMP_fixed.py` · `deploy_title_poc.py` · สาย `thai_encode*.py` (donor slot map)
   **ใช้กับภาคนี้ไม่ได้** ห้าม copy มาแล้วรัน

**แต่ข้อมูลข้อความข้างในยังเป็นของ RGG เอง** — `.msg` สาย Old Engine (เหมือน Y0/K1/Y5)
ห่ออยู่ในไฟล์ `pakchunk0-WindowsNoEditor.pak` อีกที → แตกสองชั้น: pak → msg

ชื่อโปรเจกต์ภายในของเกม = **`Devil2`** (แทนที่ codename แบบ `coyote`/`judge` ของภาค Dragon Engine)

หลักฐานทั้งหมด + ตัวเลขที่วัดได้จริง: **`docs/research.md`** — อ่านก่อนแตะไฟล์เกมทุกครั้ง

## สิ่งที่ยกมาจากโปรเจกต์ก่อนได้จริง

| ยกมาได้ | ยกมาไม่ได้ |
|---|---|
| ระเบียบวิธีเพศผู้พูด/สรรพนาม (`docs/reference/CUE_GENDER_METHOD.md`) | ตารางเพศจากไฟล์เกม (คนละฟอร์แมต ต้องหาใหม่) |
| `translations/PRONOUN_MATRIX.md` · `pronoun_exceptions_seed.json` | คำล็อก**ชื่อตัวละคร** (Ishin เป็นบาคุมัตสึ คนละตัวละคร แม้หน้าเหมือน) |
| brief นักแปล/รีวิวเวอร์ · เกณฑ์ QC 7 ด่าน · `merge_qc.py` | `build_text.py` · `extract_all_en.py` · `deploy_*.py` (ผูกกับ ARMP/par) |
| ศัพท์เมนู/ระบบ/การต่อสู้ จาก glossary ภาคก่อน | สาย donor slot map — ภาคนี้เป็น UTF-8 ตรง ๆ ไม่ต้องใช้ |
| วินัยการทำงาน (ด่านตรวจไบต์ดิบ · ห้ามเดา · ห้ามรันทีละไฟล์) | **สายฟอนต์ทั้งชุด** — ภาคนี้เป็น UE Slate + FreeType ยัด .ttf ทับ .ufont จบ |

ต้นแบบ pipeline ข้อความ/QC = **Lost Judgment** (`D:\Projects\lost-judgment-thai`)
สคริปต์ชุดเต็มของภาคนั้น copy ไว้ที่ `scripts/ref_lj/` (71 ไฟล์ · **อ้างอิงอย่างเดียว ห้ามรันตรง ๆ**)

## อ่านก่อนทำงานทุก session
1. `HANDOFF.md` — สถานะล่าสุด + งานถัดไป
2. `docs/research.md` — ข้อเท็จจริงจากไฟล์เกมจริง + คำถามที่ยังเปิด
3. `scripts/paths.py` — path กลาง (รันตรง ๆ ได้ จะบอกว่าอะไรมี/ไม่มี)

## ตาราง path
| ชื่อ | ที่อยู่ | กติกา |
|---|---|---|
| PROJECT | `D:\Projects\like-a-dragon-ishin` | งานทั้งหมดเขียนที่นี่ |
| GAME | `E:\SteamLibrary\steamapps\common\LikeADragonIshin` (override: env `ISHIN_GAME`) | **ห้ามแก้/ลบ/ทับไฟล์ใน `Content/Paks/`** · ห้ามเปิดเกมเอง (ผู้ใช้ทดสอบ) |
| LJ | `D:\Projects\lost-judgment-thai` | อ่านอย่างเดียว · ต้นแบบ pipeline ข้อความ/QC/เพศผู้พูด |
| JUDGMENT / K3 / Gaiden / Y8 / Y7 / Pirate / K2R | ตาม `SIBLINGS` ใน `scripts/paths.py` | อ่านอย่างเดียว (glossary/TM) |
| Y0 / Y5 / Kiwami | `yakuza-0-direct` · `yakuza-5` · `yakuza-kiwami-mod` | อ่านอย่างเดียว · **Old Engine — ฟอร์แมต `.msg` ใกล้ภาคนี้ที่สุด** |

## กติกาเหล็ก
1. ห้ามแก้ไฟล์ในโฟลเดอร์เกม — ม็อดออกเป็น pak ใหม่ที่ `Content/Paks/~mods/` ชื่อลงท้าย `_P` เท่านั้น
   (ยืนยันในเกมแล้ว · เงื่อนไขครบสามข้อดู `docs/research.md` §6)
2. ห้ามเปิดเกมเอง — การทดสอบในเกมเป็นหน้าที่ผู้ใช้
3. โปรเจกต์เก่าทุกตัวอ่านอย่างเดียว — จะแก้อะไรให้ copy เข้า PROJECT ก่อน
4. คำแปลรวมมีที่เดียว: `translations/master_th.json` เขียนผ่าน `merge_qc.py` เท่านั้น
5. console Windows = cp1252 — ทุกสคริปต์ `sys.stdout.reconfigure(encoding="utf-8")`
   (+ `sys.stderr` ด้วย) · เปิดไฟล์ `encoding="utf-8"` · ห้ามส่งข้อความไทยผ่าน CLI args
6. **ด่านตรวจบังคับก่อนบิลด์ทุกครั้ง**: `check_msg_roundtrip.py` และ `check_pak_roundtrip.py` ต้องได้ **ต่าง 0**
   — เทียบ **ไบต์ดิบ** กับต้นฉบับ ไม่ใช่ decode ซ้ำ (บทเรียน LJ-011: เครื่องมือที่ decode/encode
   ด้วยบั๊กเดียวกันจะรายงานว่าผ่านทั้งที่ไฟล์พัง)
7. ห้ามรันเครื่องมือทีละไฟล์เป็นร้อยรอบ — เขียน loop ลง `scripts/`
8. agent ห้ามเขียนไฟล์ใหญ่ใน Write เดียว — แตก `.part` แล้ว merge
9. license/EULA/credits คงอังกฤษ
10. ข้อเท็จจริงเรื่องไฟล์เกม **ต้องมาจากการเปิดไฟล์จริง** — ห้ามสรุปจากชื่อไฟล์
    (บทเรียน LJ: สรุปสถาปัตยกรรมฟอนต์ผิดเพราะดูแต่ชื่อไฟล์ เสียเวลาสองวัน)

## Pipeline ที่วางไว้
```
pakchunk0.pak ──tools/pakfile.py──> wdr_en/msg/*.msg ──tools/msg.py──> extracted/text_en/*.json
                                                                              │
                                            (ทีมแปล + worklist/batch context) │
                                                                              v
                                          translations/master_th.json ──merge_qc.py──> build
                                                                              │
                                               tools/msg.py rebuild ──> pak ม็อด ──> เกม
```
สถานะแต่ละขั้น: ดู `docs/research.md` §8 และ `HANDOFF.md`

## กฎการแปล (ยกมาจาก K3/LJ ทั้งชุด)
- **เพศผู้พูดต้องมาจากไฟล์เกม** พิสูจน์ไม่ได้ = แปลกลางเพศ **ห้ามเดา**
  (ภาคนี้ยังไม่รู้ว่าเพศมาจากไฟล์ไหน — ดู research §7 ข้อ 7)
- glossary ลำดับความสำคัญ: LJ > Judgment > K3 > Gaiden > Y8 > Y7 > Pirate > K2R (ใหม่กว่าชนะ)
  · **ยกเว้นชื่อตัวละคร** — Ishin เป็นยุคบาคุมัตสึ ตัวละครคนละคนกับซีรีส์หลัก แม้ใช้หน้านักแสดงชุดเดียวกัน
  (เรียวมะ ≠ คิริว · โซจิ ≠ มาจิม่า) → ชื่อ/คำเรียกต้องตั้งใหม่ตามประวัติศาสตร์ญี่ปุ่น
- ระดับภาษา: ยุคบาคุมัตสึ (ปลายเอโดะ) — สำนวนต้องขรึมกว่าภาคปัจจุบัน ⏳ ต้องตั้งเกณฑ์ใน brief ก่อนเริ่มแปล
