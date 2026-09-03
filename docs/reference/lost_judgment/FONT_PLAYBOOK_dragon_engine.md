# Font Playbook — บทเรียนฟอนต์ไทย Dragon Engine (จาก Y8/Infinite Wealth)

> เขียน 13 ส.ค. 2026 หลังปิดงานแปล Y8 100% — สำหรับโปรเจกต์ภาคถัดไป (Y7 rework, Gaiden, ภาคใหม่)
> อ่านคู่กับ `docs/research.md` ของโปรเจกต์นั้น ๆ และ playbook นี้ก่อนแตะฟอนต์ทุกครั้ง

## สถาปัตยกรรมที่ใช้ (พิสูจน์แล้ว 3 เกม: Pirate, K2R, Y8)

- ข้อความไทยถูก encode เป็น **donor slot** = codepoint ละตินมีไดอาคริติก (À Û Ÿ Â Ë ฯลฯ) ใน bin ข้อความ
- ฟอนต์ SDF atlas (`<name>.bin` + `<name>.dds`) ถูกฉีดกลิฟไทย (Sarabun) ทับ slot เหล่านั้นด้วย `inject_thai_sdf.py` (66 กลิฟ: repoint donor ที่มีหมึก + insert ตัวที่ขาด)
- charmap อยู่ใน exe — **slot ว่าง (ไม่มีหมึกเดิม) = tofu แก้ไม่ได้** ใช้เฉพาะ donor ที่มีหมึกจริง
- ฟอนต์ loose ผ่าน Parless **ไม่โหลด** (เกมโหลดฟอนต์ก่อน hook) → ต้อง drop-in ทับ `font.<codename>.par` โดยสำรอง `.orig` ก่อนเสมอ

## อาการเสีย 3 แบบ — วินิจฉัยจากภาพหน้าจอ

| เห็นอะไร | สาเหตุ | ทางแก้ |
|---|---|---|
| ละตินเพี้ยนมีหมวก (ÀÛÀŸÂË) แต่มีไทยถูก 1-2 ตัวปน (สี fallback) | **ฟอนต์นั้นยังไม่ถูกฉีด** — donor โชว์กลิฟละตินเดิม ตัวที่ถูกคือ fallback ไปฟอนต์ที่ฉีดแล้ว | หา font file ของจอนั้น ฉีดเพิ่ม แพ็ค par ใหม่ |
| อังกฤษสวยปกติ ทั้งที่ db แปลเป็นไทยแล้ว | เป็น**รูปแปะ (texture .dds)** หรือ bin ไม่ได้ deploy | เช็ค `ui_texture_text.bin` ก่อน (ถ้า string อยู่ในนั้น = เกมวาดสด แค่ฟอนต์ไม่ครบ) · ถ้าเป็น texture จริงต้องวาดรูปใหม่ (Y8: ไม่เจอเคสนี้ — EN วาดสดทั้งหมด) |
| สี่เหลี่ยม/tofu | donor slot ว่างไม่มีหมึก | เปลี่ยน donor ใน thai_encode ให้ใช้ slot ที่มีหมึก |

## รายชื่อฟอนต์ที่ต้องฉีด (Y8 — เทียบเคียงหาชื่อใกล้กันในภาคอื่น)

ฉีดครบแล้วใน Y8 (staging `build/fontstage/font/` 16 ไฟล์):
1. `elvis_system_gothic_en_all_{fhd,uhd}` — บทสนทนา/UI หลัก (**ฉีดก่อนเสมอ**)
2. `metaoffcpro-condbook` (+ strip `_s`) — แคปชัน condensed
3. `edosz_en_{fhd,uhd}` — **พู่กันหัวบท/การ์ดตอน** (พลาดรอบแรก → หัวบทเพี้ยนทั้งจอ)
4. `sega_newrodinn-eb_en_latin_{fhd,uhd}` — แคปชันรอง/บรรทัดใต้หัวบท
- strip svg: `elvis_system_gothic_en_all_svg` (cp ไม่ sort = ทำได้) · `edosz_en_svg` **cp sort อยู่ ห้าม strip** (binary search จะพัง) — ถ้าจอไหนยังเพี้ยนหลังฉีด atlas = เกมใช้ svg ต้องแทน donor cp ด้วยค่า PUA แบบรักษาลำดับ (เลือกค่าในช่องว่างระหว่างเพื่อนบ้าน)

**บทเรียนหลัก: อย่าฉีดแค่ฟอนต์บทสนทนาแล้วประกาศเสร็จ — ไล่เทสต์จอพิเศษให้ครบ:**
หัวบท/การ์ดตอน · หน้าสกิล · แคปชันคัตซีน · คาราโอเกะ · มินิเกม (ป้ายคะแนน) · staffroll/เครดิต · หน้า pause/ไบโอตัวละคร

## ขั้นตอนแพ็ค + ติดตั้ง (Y8)

```
python scripts/inject_thai_sdf.py <font1> <font2> ...   # อ่าน extracted/font/ เขียน build/font/ + preview_*.png (เปิดดูวรรณยุกต์ก่อนเสมอ)
# copy .bin+.dds ที่ฉีดแล้วเข้า build/fontstage/font/
tools/ParTool.exe add <game>/data/font.<code>.par.orig build/fontstage build/font.<code>.par
# วางทับ font.<code>.par ในเกม (.orig ต้องมีอยู่ก่อนแล้ว — ครั้งแรกให้ rename สำรองก่อน)
```

- ParTool `add` ทับจาก **.orig เสมอ** (ไม่ใช่ par ที่ฉีดรอบก่อน — กัน layering ซ้อน)
- **กับดักที่พลาดมาแล้วจริง (Y8, 13 ส.ค. 2026)**: `font.elvis.par` เก็บไฟล์ที่ **root** — โฟลเดอร์ที่ส่งให้ ParTool ต้องเป็นชั้นที่ "เนื้อในคือไฟล์ตรง ๆ" (`build/fontstage/font`) ไม่ใช่ชั้นแม่ (`build/fontstage`) มิฉะนั้นไฟล์จะเข้าไปเป็นโฟลเดอร์ `font/` ใหม่ที่เกมไม่อ่าน → ฟอนต์กลับเป็นต้นฉบับ เพี้ยนทั้งเกมรวมจอที่เคยดี
- **ตรวจก่อน drop-in ทุกครั้ง**: `ParTool.exe list build/font.<code>.par` — (1) ไม่มี path ซ้อนแปลกปลอม (2) ไฟล์เป้าหมายที่ root มีวันที่/ขนาดตรงกับตัวที่ฉีดใหม่
- `build_release.py` เช็ค md5 ระหว่าง par ใน build กับตัวที่เทสต์ในเกม — ฟอนต์ที่แจกต้องเป็นตัวเดียวกับที่เทสต์ผ่าน

## เทคนิคถอดรหัสจอเพี้ยน (ใช้จริงแล้ว Y8)

พิมพ์ตัวอักษรเพี้ยนจากภาพหน้าจอ แล้วแปลงกลับด้วย DECODE map:
```python
sys.path.insert(0, "scripts"); from thai_encode import DECODE
D = {chr(k) if isinstance(k,int) else k: chr(v) if isinstance(v,int) else v for k,v in DECODE.items()}
print("".join(D.get(c, c) for c in "ûûβÿîβíβô"))   # -> ออกจากเกม
```
ได้คำไทย → grep master → ได้ EN key → เทียบ strings_by_bin.json = รู้ bin ต้นทางทันที

## ข้อความที่ต้องคง EN เสมอ (แสดงผ่านช่องทางที่ donor ใช้ไม่ได้)

1. **MsgBox ของ Windows** (Quit game? ฯลฯ ใน msg.bin) — ฟอนต์ระบบ OS ไม่มีวันโชว์ไทย donor
2. **จอที่ใช้ฟอนต์ svg vector ที่ cp table sort** (Y8: edosz_en_svg = การ์ดพู่กัน) — ฉีด atlas ไม่ช่วยเพราะเกมเลือก svg
   - Y8 เคาะแล้ว (user อนุมัติ): การ์ดพู่กันทั้งหมดคง EN = title_movie.bin (112), title_movie_chapter.bin (14)
3. **ui_texture_text.bin = คง EN ทั้ง bin ตั้งแต่แรก** (บทเรียน Y8 รอบห้า) — จอโอเวอร์เลย์สไตล์จัด (บอกสถานที่/ปี, การ์ดแนะนำตัวละคร, ป้ายคัตซีน) ใช้ฟอนต์ stylized หลายตัวปนกันที่ระบุ/ฉีดไม่ครบ — แปลไปก็เพี้ยนทีละจอ (เคสจริง: "โยโกฮาม่า" ฮ→ä ยังเพี้ยนแม้ฉีด mincho แล้ว) — อย่าเสียเวลาแปล bin นี้
4. อาการ "เพี้ยนแค่บางตัว เช่น ฮ→ä": ฟอนต์นั้นมีหมึก Latin บาง slot ของตัวเอง (ไม่ fallback เฉพาะตัวนั้น) — ฉีดฟอนต์นั้นเพิ่ม แต่ระวัง: จอโอเวอร์เลย์บางจอระบุฟอนต์ไม่ได้ (Y8 ฉีด mincho แล้วยังเพี้ยน) — ถ้าไล่ไม่เจอให้คืน EN ตามข้อ 3

## สแกนหาฟอนต์เสี่ยงทั้งเกมก่อน ไม่ใช่รอ user เจอทีละจอ (บทเรียน Y8 รอบสี่)

ฟอนต์ที่มีหมึก Latin donor ของตัวเองแม้ตัวเดียว = จอนั้นจะเพี้ยนเฉพาะตัวอักษรนั้น (ฮ→ä) เพราะไม่ fallback — สแกนทั้งโฟลเดอร์ด้วย font_tool:
```python
from thai_encode import ENCODE
from font_tool import Font, cp_unpack
# donors = ทุก codepoint >0x7F ที่ ENCODE ใช้ · ต่อ font: overlap = donors ∩ cp table
# overlap > 0 และยังไม่ฉีด = ต้องฉีด (ดูสคริปต์เต็มใน HANDOFF รอบสี่)
```
Y8 ฉีดจนครบ 24 ไฟล์ atlas (รวม battle_damage, matching_app_name, resort_island_status, yoasobi_result, gothic/mincho ja_all, ru/zh/zhs_all, newrodinn db/eb)
ฉีดไม่ได้ = atlas เต็ม (inject ปฏิเสธ "atlas เต็ม") หรือมี tail data — Y8 เหลือ 4: gothic_ja_all_fhd, ko_all ทั้งคู่, zh_all_fhd — จอเพี้ยนบางตัวที่ 1080p ให้สงสัย gothic_ja_all_fhd ก่อน

## เช็คลิสต์ก่อนประกาศงานฟอนต์เสร็จ (ภาคหน้า)

1. `docs/research.md` ของภาคนั้นต้องมีรายชื่อ "ฟอนต์รอง" — ฉีดให้ครบตั้งแต่รอบแรก อย่ารอเพี้ยน
2. เปิด preview ทุกไฟล์ที่ฉีด — วรรณยุกต์ต้องลอยถูกชั้น, ำ ไม่แตก (ำ = spacing vowel ห้าม reorder / Y7 ใช้ decompose ํ+า)
3. สแกน master: ห้ามมีอักษรละตินมีไดอาคริติกหลงในค่าที่แปลแล้ว (é ā ʻ ฯลฯ — จะไปโผล่เป็นไทยผิดตัว) และห้ามมี ๅ (ฤๅ→ฤา)
4. user เทสต์จอพิเศษครบทุกประเภทตามรายการข้างบน ไม่ใช่แค่บทสนทนา
5. `ui_texture_text.bin` แปลครบ = จอ texture วาดสดใช้ได้ · ถ้าภาคใหม่เจอจอที่ EN เป็นรูปจริง (เทียบ telop_*.dds แบบ pirate G10) ให้บันทึกรายไฟล์ก่อนตัดสินใจวาด
