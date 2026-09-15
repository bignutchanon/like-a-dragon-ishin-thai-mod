# research — Like a Dragon: Ishin! (ISHTH)

ข้อเท็จจริงทุกข้อในไฟล์นี้ **ตรวจกับไฟล์เกมจริงบนเครื่องนี้แล้ว** (1 ก.ย. 2026) ถ้าอันไหนยังเดา จะมี ⏳ กำกับ

เกมที่ติดตั้ง: `E:\SteamLibrary\steamapps\common\LikeADragonIshin`

---

## 1. ข้อสรุปใหญ่ที่สุด — ภาคนี้ไม่ใช่ Dragon Engine

Like a Dragon: Ishin! (รีเมค 2023) สร้างบน **Unreal Engine 4.27** ไม่ใช่ Dragon Engine
ดังนั้น pipeline ทั้งสายของ K3 / Gaiden / LJ / Y8 (par + ARMP + SRMM/Parless + ฟอนต์ SDF)
**ใช้กับภาคนี้ไม่ได้เลยในชั้นคอนเทนเนอร์**

หลักฐาน:
- โครงโฟลเดอร์เกมเป็น UE ล้วน: `Engine/` · `LikeaDragonIshin/{Binaries,Content,Plugins}/` · `startup.exe`
- ไม่มี `runtime/media/data/*.par` · ไม่มี `.bin` แบบ ARMP · ไม่มีโฟลเดอร์ `mods/`
- ปลั๊กอินที่ ship มา: DLSS · XeSS · Crashpad → ของ UE ทั้งชุด
- คอนเทนเนอร์: `Content/Paks/` มี `.pak` + `.utoc/.ucas` (IoStore)

**แต่** ข้อมูลข้อความข้างในยังเป็นฟอร์แมตของ RGG เอง (`.msg` สาย Old Engine) — ดูข้อ 3
ชื่อโปรเจกต์ภายในของเกมคือ **`Devil2`** (path `Content/Projects/Devil2/`)

---

## 2. ชั้นคอนเทนเนอร์ (ยืนยันแล้ว)

### 2.1 IoStore — `.utoc` / `.ucas`
| ค่า | ที่วัดได้ |
|---|---|
| TOC version | 3 |
| compression | **Zlib เท่านั้น** (ไม่ใช่ Oodle → ไม่ต้องมี `oo2core*.dll`) |
| block size | 65,536 |
| EncryptionKeyGuid | `0` ทั้ง 16 ไบต์ |
| container flags | `0x9` = Compressed \| Indexed |
| **AES key** | **ไม่ต้องใช้** — index ไม่เข้ารหัส |

คอนเทนเนอร์ที่มี: `global` · `pakchunk0` · `pakchunk0optional` · `pakchunk1` · `pakchunk2` ·
`pakchunk2optional` · `pakchunk3` · `pakchunk3optional` — รวม **279,328 ไฟล์**

แจกแจงคร่าว ๆ: 275,326 ไฟล์อยู่ใต้ `Content/Projects/Devil2/` · `Content/L10N/<lang>/` 2,538 ไฟล์
(เป็น **texture/ของ minigame ล้วน ไม่มีข้อความ**) · `Content/TextBridge/` 591 ไฟล์

เครื่องมือ: `tools/iostore.py` (เขียนเอง Python ล้วน) — `list` / `extract`

### 2.2 pak แบบ legacy — `pakchunk0-WindowsNoEditor.pak`
| ค่า | ที่วัดได้ |
|---|---|
| pak version | 11 |
| ขนาด | 23.9 GB |
| ไฟล์ | 35,646 |
| index | มี PathHashIndex + **FullDirectoryIndex** · ไม่เข้ารหัส |
| compression | Zlib |

**นี่คือที่อยู่จริงของข้อมูลเกม RGG** — IoStore เก็บแต่ asset ของ UE
สกุลไฟล์ที่พบมากสุด: `.msg` 15,112 · `.awb` 8,405 (เสียง CRIWARE) · `.bin` 3,606 ·
`.txt` 3,098 (รายการไฟล์ของ par) · `.res` 1,079 · `.imb` 947 · `.isr` 782 · `.gmd` 698 ·
`.png` 311 · `.locres` 41 (ของ Engine/ปลั๊กอิน ไม่ใช่ข้อความเกม)

เครื่องมือ: `tools/pakfile.py` (เขียนเอง Python ล้วน) — `list` / `extract`

---

## 3. ชั้นข้อความ — `.msg` (ยืนยันแล้ว)

ข้อความเกมอยู่ที่ `Content/Projects/Devil2/data/wdr_<lang>/msg/uid0Nxxxxxx/uid########.msg`
โดย `<lang>` = `ja` `en` `fr` `de` `it` `es` `ko` `cn` (8 ภาษา)

- คลัง **EN = 1,678 ไฟล์ · 13.4 MB · 50,233 สตริง** (90% เป็น ASCII ล้วน → เป็นภาษาอังกฤษจริง)
- คลัง JA = 1,688 ไฟล์
- แบ่งโฟลเดอร์ตามช่วง uid: `uid01xxxxxx` 832 · `uid00xxxxxx` 658 · `uid03xxxxxx` 176 · `uid02xxxxxx` 12
- ข้าง ๆ กันมี `wdr_<lang>/pac/*.bin` ภาษาละ 168 ไฟล์ (⏳ ยังไม่แกะ)

### 3.1 โครงไฟล์ `.msg` — แกะครบแล้ว (big-endian ทั้งไฟล์)
```
0x00  uint32 x8  ส่วนหัว · ไบต์แรกเป็น 0x20 เสมอ (uint32 ตัวแรกไม่ใช่ magic คงที่)
                 header[3] 16 บิตล่าง = จำนวน label   ← จุดที่หลงทางมาก่อน
                 header[4] = ตารางพอยเตอร์ label · header[5] = ท้ายบล็อก label
                 header[7] = ตำแหน่งตาราง entry
ตาราง entry      แถวละ 12 ไบต์: uint16 ความยาวสตริง · uint16 จำนวนคำสั่ง<<8 ·
                 uint32 ตำแหน่งสตริง · uint32 ตำแหน่งบล็อกคำสั่ง
                 จำนวนแถว = (ตำแหน่งบล็อกคำสั่งแถวแรก − ตำแหน่งตาราง entry) / 12
บล็อกคำสั่ง      คำสั่งละ 16 ไบต์ · (จำนวนคำสั่ง × 16) = ขนาดบล็อกพอดีทุกไฟล์
                 opcode 0x01 หัว/ท้ายบรรทัด · 0x02 คำสั่งกลางข้อความ (byte[7] = ตำแหน่งตัวอักษร)
                 opcode 0x03 คิวเสียง — byte[3] = ดัชนีใน label
บล็อกสตริง       UTF-8 ปิดท้าย NUL เรียงต่อกัน
ตาราง label      ปนกันสามแบบ: ชื่อตัวละคร (Otose) · คิวเสียง (otose_adv_c02_150_001) ·
                 ท่าทาง/ฉาก (Idle, TLK_SCN001)
```
ตรวจกับคลัง EN ทั้ง 1,678 ไฟล์ / 54,318 แถว — ความยาวที่ประกาศตรงกับสตริงจริง **100%**
⏳ ที่ยังไม่รู้: ความหมายรายฟิลด์ของ opcode 0x02 · header[1] header[2] header[6]

### 3.2 เรื่องใหญ่: สตริงเป็น **UTF-8** อยู่แล้ว
ต่างจาก Dragon Engine ที่ต้องใช้ donor slot map (`thai_encode.py` / `thai_encode_cyr.py`)
เพราะฟอนต์เป็น atlas ที่ผูกกับ codepoint — ภาคนี้เขียนไทยลง `.msg` ได้ตรง ๆ
**ข้อจำกัดจึงย้ายไปอยู่ที่ฟอนต์ล้วน ๆ** (ข้อ 5)

### 3.3 ด่านตรวจที่ผ่านแล้ว
`python scripts/check_msg_roundtrip.py` → **ตรวจ 1,678 ไฟล์ · เหมือนเดิม 1,678 · ต่าง 0**
(ประกอบกลับโดยไม่แก้อะไร แล้วเทียบ **ไบต์ดิบ** กับต้นฉบับ ไม่ใช่เทียบผลถอดรหัสซ้ำ —
บทเรียน LJ-011 จากโปรเจกต์ Lost Judgment)

⚠ ยังไม่ได้ทดสอบว่าไฟล์ที่ **ยาวขึ้น** (ไทยยาวกว่าอังกฤษ) เกมยังโหลดได้ไหม — ดู §7

---

## 4. ชั้นข้อความ UI — เจอครบแล้ว มีสองแหล่ง (ยืนยันแล้ว)

### 4.1 `db.macan/<lang>/*.bin` — **ARMP v2 ตัวเดียวกับ Dragon Engine**
`Content/Projects/Devil2/data/db.macan/<lang>/` · 10 ภาษา × 122 ตาราง = 1,102 ไฟล์
(`macan` = codename ภายในของ Ishin! เทียบเท่า `coyote` ของ LJ / `judge` ของ Judgment)

magic = `armp` **ครบทั้ง 122 ตาราง** → `tools/reARMP_fixed.py` ที่ยกมาจาก Lost Judgment
**ใช้ได้ตรง ๆ ไม่ต้องแก้** (ทดสอบแล้วกับ `tips.bin`: ARMP v2 · 141 แถว · 18 คอลัมน์ ·
TABLE_ID 47 · STORAGE_MODE 1)

ขนาดงานฝั่ง EN: **122 ตาราง · 58,591 แถว · TEXT_COUNT รวม 17,501** (6.3 MB)
ตารางที่ข้อความเยอะสุด: `sound_speak_data` 3,714 · `staffroll_*` ~1,350 ต่อแพลตฟอร์ม (เครดิต
— คงอังกฤษตามกติกาข้อ 9) · `taishi_card_list` 1,211 · `stay_enemy_name_all` 465 ·
`blacksmith_weapon_parameter` 455 · `dictionary_word_list` 429 · 60 ตารางไม่มีข้อความเลย

⚠ reARMP ประกอบกลับ **ไม่ได้ไบต์เท่าเดิม** (`tips.bin` 210,864 → 212,432 · ต่างตั้งแต่ไบต์ 0x10)
   แต่ **ทดสอบกับไฟล์ของ Lost Judgment เองก็ต่างเหมือนกัน** (8,752 → 8,736) → ไม่ใช่ปัญหา
   เฉพาะภาคนี้ และเป็นสภาพเดียวกับตอนที่ LJ ปล่อยม็อดสำเร็จ ด่านตรวจจึงต้องเทียบ
   **ไบต์ในแถว** กับ vanilla (พอร์ต `check_layout_all.py` จาก `scripts/ref_lj/`) ไม่ใช่เทียบทั้งไฟล์

### 4.2 `Game.locres` — ตารางข้อความของ UE
`LikeaDragonIshin/Content/Localization/Game/<lang>/Game.locres` · 9 ภาษา (de en es fr it ja ko zh-Hans zh-Hant)

ไฟล์ EN: **locres version 3 · 493 namespace · 23,507 entry · สตริงไม่ซ้ำ 14,767 · 1.77 MB**
อ่าน/เขียนด้วย `tools/locres.py` ที่ยกมาจากโปรเจกต์ **Frostpunk 2** (เกม UE เหมือนกัน) — ใช้ได้ตรง ๆ

คีย์เป็นรูปแบบ `<namespace>` + `<table>/<field>/NNNN` เช่น namespace `ability_control_explanation`
คีย์ `ability/control_explanation/0013` → ตรงกับชื่อ asset ใน `Content/TextBridge/` แบบหนึ่งต่อหนึ่ง

### 4.3 `Content/TextBridge/*.uasset` — StringTable ต้นฉบับ (ภาษาญี่ปุ่น)
591 asset ใน IoStore · UE `StringTable` · ค่าเป็น UTF-16LE **ภาษาญี่ปุ่น** = ต้นฉบับ
ส่วนภาษาอื่นมาทับตอนรันไทม์จาก `Game.locres` (§4.2) ตามกลไกปกติของ UE
→ **ไม่ต้องแตะ TextBridge เลย** แปลที่ `Game.locres` ก็พอ (ไม่ต้องเขียน Zen package parser)

หมวดใหญ่ใน TextBridge: `Auth` 117 (บทคัตซีน) · `AuthSpeaker` 111 (**ผู้พูดของแต่ละคัตซีน**) ·
`System` 58 · `GraphicsText` 53 · `EncounterPopup` 51 · `ControllerExplain` 19

`AuthSpeaker/s_c14_062_speaker.uasset` ↔ `Auth/s_c14_062.uasset` — จับคู่กันตรง ๆ ตามชื่อ
→ ฐานของ "ตารางผู้พูด" แบบเดียวกับที่ LJ ใช้ (`make_auth_speaker.py`) และน่าจะอ่านผ่าน
`Game.locres` ได้โดยไม่ต้องแกะ uasset

### 4.4 ขนาดงานแปลรวมทั้งเกม (ตัวเลขดิบ ยังไม่หักซ้ำ/ไม่หักที่ไม่ต้องแปล)
| ชั้น | ที่อยู่ | จำนวน |
|---|---|---|
| บทพูด | `wdr_en/msg/*.msg` 1,678 ไฟล์ | 50,233 สตริง |
| UI/ระบบ (ARMP) | `db.macan/en/*.bin` 122 ตาราง | TEXT_COUNT 17,501 |
| UI (locres) | `Game.locres` | 23,507 entry · ไม่ซ้ำ 14,767 |

---

## 5. ฟอนต์ — ยืนยันในเกมแล้ว ไม่ต้องแฮ็ก

ระบบฟอนต์เป็น **UE Slate CompositeFont** ล้วน ไม่ใช่ atlas ของ RGG

- `UI/Font/Font_System.uasset` = `CompositeFont` มี `DefaultTypeface` + `CompositeSubFont` +
  `Cultures` + `CharacterRanges` → เลือก sub-font ตามภาษาให้เอง
- **`FontCacheType = EFontCacheType::Runtime`** → เกม render ด้วย FreeType ตอนรันไทม์
  ไม่มี atlas ที่ bake ไว้ล่วงหน้า
- FontFace asset (ตัวละ ~700 ไบต์) แค่ชี้ไปที่ `SourceFilename` — **ไฟล์ฟอนต์จริงเป็น
  `.ufont` วางเป็น loose file ใน `pakchunk0.pak`** และเป็น sfnt แท้ (TrueType/OpenType/TTC)
  26 ไฟล์ · ที่จอ EN ใช้คือ `UI/Font/FontFace/EFIGS/Kuro-Medium.ufont` (54 KB · OpenType/CFF)
- `DA_UISystemFont` มีอัตราส่วนขนาดแยกต่อภาษา (`sizeRatio_EN_French`, `sizeRatio_JP_Japanese` ฯลฯ)

**วิธีใส่ฟอนต์ไทย: เอา .ttf ไปทับ `.ufont` ผ่าน pak ม็อด เท่านั้น**
ทดสอบด้วย Sarabun แล้วขึ้นจริงบนจอ และ **สระบน/ล่างกับวรรณยุกต์วางถูกตำแหน่งทุกตัว**
→ UE เปิด text shaping (HarfBuzz) ไว้ ไม่ต้องทำ precomposed glyph หรือแก้ metrics

⚠ สาย SDF/atlas ของ LJ และ Y8 (`inject_thai_sdf.py` · `thai_encode*.py` · `slot_alloc.py` ·
`font_tool.py` · FONT_PLAYBOOK) **ใช้กับภาคนี้ไม่ได้เลย** เก็บไว้อ้างอิงเท่านั้น

### 5.1 ⭐ Kuro-Medium ตัวเดียวไม่พอ — จอที่ใช้ฟอนต์พู่กัน/มินโจไม่มีกลิฟไทย (3 ก.ย. 2026)

แตก `Font_*.uasset` ทั้ง 21 ตัวออกมาอ่าน (`work/font_dump/`) แล้วไล่ว่า CompositeSubFont
ของ culture `en;fr;it;de;es` ชี้ไปที่ FontFace ตัวไหน — ได้ **สามตัว ไม่ใช่ตัวเดียว**

| FontFace ของชุด EFIGS | CompositeFont ที่เรียกใช้ | สถานะก่อนหน้านี้ |
|---|---|---|
| `EFIGS/Kuro-Medium.ufont` | `Font_System` · `Font_CmnGothic` · `Font_MgEnkaisho` · `Font_MgKaishoUB` · `Font_MgKaraoke{Enkaisho,Fude,Kanteiryu,Reisho}` · `Font_MgKsw{Hiryu,Reisho}` · `Font_MgLisence` · `Font_MgNichibuHiryu` | ทับแล้ว ✔ |
| `EFIGS/edosz.ufont` | `Font_CmnFude` · `Font_MgKswKaisho` · `Font_MgTaishiFude` · `Font_MgKaraokeKokinedo` · `Font_MgPhotoModeStamp` | **ไม่เคยทับ** ✘ |
| `EFIGS/FOT-TelopMinProN-D.ufont` | `Font_MgTaishiKaisho` | **ไม่เคยทับ** ✘ |

ตรวจตาราง `cmap` ของ `.ufont` **ทั้ง 33 ไฟล์**ในเกม: **ไม่มีไฟล์ไหนมีกลิฟไทยเลย**
ยกเว้น `Engine/.../DroidSansFallback.ufont` ที่มีตัวเดียวคือ U+0E3F (฿)
→ จอที่ใช้ `Font_CmnFude`/`Font_MgTaishi*`/`Font_MgKswKaisho`/`Font_MgPhotoModeStamp`
  แสดงข้อความไทยไม่ได้ ตราบใดที่ยังทับแค่ `Kuro-Medium`
แก้แล้วใน `build_text.py` (`FONT_GAME_PATHS` สามรายการ)

**ที่ยังเปิดอยู่** — `Font_CmnMincho` และ `Font_MacanNum` **ไม่มี CompositeSubFont ของ EFIGS เลย**
ภาษาอังกฤษ/ไทยบนจอสองตัวนี้จึงตกไปที่ `DefaultTypeface` ซึ่งเป็นฟอนต์ญี่ปุ่น
(`DF-FutoKaiSho-W9` · `Myfont_fude-Regular`) ที่ก็ไม่มีกลิฟไทย
ยังไม่ทับเพราะทับแล้วเสียกลิฟคันจิของฟอนต์นั้นไปด้วย — ต้องหาก่อนว่ามีจอไหนใช้จริง

### 5.2 ⭐ CharacterRanges ของ sub-font EFIGS ตัดตัวอักษรไทยทิ้ง (8 ก.ย. 2026)

อาการที่ผู้ใช้ส่งภาพมา: จอ "จัดกองกำลัง" (`WBP_TaishiIkuseiTopMenu`) และ "เลือกจุดหมาย"
(`WBP_TaishiIkuseiMenu03List`) แถบเมนู**ว่างเปล่าไม่มีตัวหนังสือเลย** แต่บรรทัดคำอธิบายล่างจอเดียวกัน
(`WBP_TaishiIkuseiTopMenuInfo` · `Font_System`) เป็นไทยปกติ และ `???` ของรายการที่ยังไม่ปลดล็อกก็ขึ้น

ที่วัดจากไฟล์:
- คำแปลอยู่ครบ — `Game.locres` ที่บิลด์มี namespace `taishi` 152 คีย์ · `soldier_training` 135 คีย์ เป็นไทยทั้งหมด
- widget ที่วาดแถบเมนูใช้ `Font_MgKaishoUB` (จอแรก) และ `Font_MgEnkaisho` (จอที่สอง) —
  ทั้งคู่มี CompositeSubFont ของ culture `en;fr;it;de;es` ชี้ไป `EFIGS/Kuro-Medium` ที่ทับเป็น Sarabun แล้ว
  → **ไม่ใช่เพราะไม่ได้ทับฟอนต์**
- อ่านค่า `CharacterRanges` ของ CompositeSubFont จาก uasset ตรง ๆ (int32 ตัวสุดท้ายก่อนสตริง culture):

| CompositeFont | upper bound ของช่วง EFIGS | ไทย (U+0E00-U+0E7F) เข้าไหม | DefaultTypeface |
|---|---|---|---|
| `Font_System` | U+FFFFFF | ✔ | DF-FutoKaiSho-W9 · FOT-UDKakugo_LargePr6N-DB |
| `Font_CmnFude` | U+FFFFFF | ✔ | TT_KswHannya |
| `Font_MgKaraokeFude` | U+206F | ✔ | TT_KswHannya |
| `Font_MgKswKaisho` | U+0200 | ✘ | TT_KswKaisho |
| อีก 13 ตัว (`Font_CmnGothic` · `Font_CmnMincho` · `Font_MgEnkaisho` · `Font_MgKaishoUB` · `Font_MgTaishi*` · `Font_MgKaraoke{Enkaisho,Kanteiryu,Kokinedo,Reisho}` · `Font_MgKsw{Hiryu,Reisho}` · `Font_MgNichibuHiryu`) | **U+077F** | ✘ | ฟอนต์ญี่ปุ่นประจำตัว |

ตัวอักษรที่หลุดช่วงของ sub-font จะตกไปที่ `DefaultTypeface` ซึ่งเป็นฟอนต์ญี่ปุ่นที่ไม่มีกลิฟไทย
→ Slate วาดเป็นช่องว่าง = "ข้อความหาย" · นี่คือเหตุผลที่ **ทับ FontFace ชุด EFIGS ครบสามตัวแล้วก็ยังไม่พอ**
และยังอธิบายย้อนหลังได้ว่าทำไมการ์ดทหารหน่วยขึ้น `？` ลายพู่กัน (§0.47 ข้อ 6 ของ HANDOFF):
U+FF1F > U+077F จึงถูกวาดด้วยฟอนต์ญี่ปุ่น ไม่ใช่ `.notdef` ของ Sarabun

**แก้ที่ไหนได้**: `Font_*.uasset` อยู่ใน IoStore (`.utoc/.ucas`) เท่านั้น — pak ม็อดทับไม่ได้
(ตรวจ `extracted/pak0_files.txt` แล้วไม่มี `UI/Font/Font_*.uasset` เลยสักไฟล์)
แต่ไฟล์ฟอนต์จริง `.ufont` เป็น loose file ใน pakchunk0 → **ทับ DefaultTypeface ให้เป็น Sarabun ได้**
ทำแล้ว: `build_text.FONT_GAME_PATHS` + `FONT_DEFAULT_FACES` (รวม 11 ไฟล์ในม็อด) — เว้นไว้สองตัวโดยตั้งใจ
`DF_KANTEIRYU_W6` (เนื้อเพลงญี่ปุ่น `Font_MgKaraokeLyricJa`) และ `Myfont_fude-Regular` (`Font_MacanNum` = ตัวเลข)
⏳ รอผู้ใช้ยืนยันบนจอว่าสองจอในภาพขึ้นไทยแล้ว

### 5.2.2 ⭐ CompositeFont ที่ชื่อไม่ขึ้นต้น `Font_` หลุดจากรอบไล่ — `HTT-GFKaisho-E_Font` = HUD มินิเกมอุด้ง (15 ก.ย. 2026)

**อาการ** (ภาพผู้ใช้ 2 ใบ · test_23): HUD ระหว่างเสิร์ฟอุด้งไม่มีข้อความเลย (เหลือไอคอน · ตัวเลข "0 1,150" · "1" · บอลลูน LB มีแค่ "!")
และหน้าสรุปผลมีแต่ ":" กับตัวเลข 56 · 6 · 26,185 — ขณะที่หัวเรื่อง "การประเมิน" กับปุ่ม "ดำเนินการต่อ" (Font_System) เป็นไทยปกติ
= ASCII วาดได้ ไทยว่าง → อาการเดียวกับ §5.2 (ตัวอักษรหลุดช่วง sub-font ตกไปฟอนต์ญี่ปุ่นที่ไม่มีกลิฟไทย)

**ที่วัดจากไฟล์**
- widget ของมินิเกม (IoStore `UI/Minigame/Udon/WBP_Mg_Udon_*.uasset` 25 ไฟล์) สแกนสตริง: ตัวที่มีข้อความเกือบทั้งหมดอ้าง
  `/Game/Projects/Devil2/UI/Font/HTT-GFKaisho-E_Font` — `button_hyouji` (udon/19–22 ชื่อชาม) · `cd_start`/`cd_end` (udon/16–17 เริ่ม!/จบ!) ·
  `combo` (udon/8, 29) · `emergency` (udon/27 กลุ่มลูกค้ามาแล้ว!) · `gauge_base` (udon/9 เวลาที่เหลือ) · `osusume` (udon/23 แนะนำ!) ·
  `score_dan` (udon/13, 30–41 ชั้น/ฝีมือลวกเส้น) · `score_money` (udon/26 ยอดขาย + Font_System) · `result01` (`minigame_udon/s_udon_result_item_name/0000–0003` + udon/1–5, 7, 24, 25, 28 + Font_System)
  ที่ไม่ใช่ตัวนี้: `fukidashi` (บอลลูนลูกค้า) → `Font_MgKswKaisho`/`Font_MgKswReisho` (DefaultTypeface ทับแล้ว) · `level_up` → `Font_CmnFude` (ช่วง U+FFFFFF · EFIGS edosz ทับแล้ว) · ตัวเลขนับถอยหลัง → `Font_MacanNum`
- `HTT-GFKaisho-E_Font.uasset` (2,093 ไบต์ · IoStore เท่านั้น): CompositeFont · DefaultTypeface → `FontFace/HTT-GFKaisho-E` ·
  SubTypefaces: `en;fr;it;de;es` → `EFIGS/Kuro-Medium` **ช่วงหยุดที่ U+077F** (int32 ตัวสุดท้ายก่อนสตริง culture = 0x77F) · `ko` → `Korean/AsiaKGD14-R` (U+FFFFFF) · `zh-Hans`/`zh-Hant` → `Chinese/ZhHansSerif`/`ZhHantSerif`
- `FontFace/HTT-GFKaisho-E.ufont`: upem 1000 · hhea 880/-120/30 · bbox -247/974 · 8,720 กลิฟ · **ไม่มีกลิฟไทย** · เป็น loose file ใน pakchunk0 → ทับได้แบบเดียวกับอีก 10 ตัว
- ทำไมหลุด: §5.1 แตกเฉพาะ `Font_*.uasset` 21 ตัว — ตัวนี้ชื่อไม่มี prefix
- **สแกน widget ทั้งเกม 2,061 ไฟล์** (อ่านตรงจาก IoStore · นับ widget ที่อ้าง `/Game/Projects/Devil2/UI/Font/<ชื่อ>`):
  Font_System 635 · Font_CmnFude 63 · **HTT-GFKaisho-E_Font 38** · Font_MgEnkaisho 18 · Font_MgKswKaisho 15 · Font_MacanNum 15 · Font_CmnMincho 13 ·
  Font_MgKaishoUB 11 · Font_MgKswReisho 11 · Font_MgKaraoke{Kanteiryu,Reisho,Kokinedo,Fude} 6 ตัวละ · Font_MgNichibuHiryu 5 · Font_MgKaraokeEnkaisho 4 ·
  Font_MgTaishi{Fude,Kaisho} 3 · Font_MgKswHiryu · Font_MgPhotoModeStamp · Font_MgKaraokeLyricJa · Font_CmnGothic · Font_MgLisence 1 — **ไม่มีฟอนต์นอกรายการตัวอื่นอีก**
  38 widget ของ HTT-GFKaisho-E_Font = อุด้ง 11 · **แข่งไก่ 20** (`WBP_Mg_Kyoukei_icon_kaku` · `icon_kyori` · `Icon_Kakekata` · `kake_win` · `Kekka_Win` · `haitou_win` · `goal` ฯลฯ) ·
  โชฮัง 4 (`WBP_MG_Chouhan_deme/money/window03/window05`) · ซีโล 2 (`WBP_MgChinchiro02Deme/Text`) · ผ่าฟืน 1 (`WBP_Makiwari_Renzoku`)
  ⚠ แก้ข้อสรุปของ HANDOFF §0.60: ป้ายแข่งไก่ที่ว่าง (test_12) **ไม่ได้**มาจาก E_Font → Font_CmnGothic/Mincho — widget เหล่านั้นอ้าง HTT-GFKaisho-E_Font ตรง ๆ
  (รอบนั้น grep หา `Font_` จึงมองไม่เห็น) · สำเนา FOT-UDKakugo/DF-FutoKaiSho ยังต้องมีสำหรับ 14 widget ที่อ้าง Font_CmnMincho/Gothic ตรง ๆ แต่ไม่ใช่ตัวแก้ป้ายแข่งไก่
- วิธีสแกนที่ใช้ได้: `IoStoreSet(<path Windows>)` → `glob("WBP_")` → `read()` ทีละไฟล์ใน python (ใน heredoc ของ Git Bash ต้องเขียน `E:/…` — `/e/…` ถูกแปลงให้เฉพาะตอนเป็น argument ของโปรแกรม)

**แก้**: เพิ่ม `HTT-GFKaisho-E` ใน `make_default_typeface_fonts.FACES` (วิธีดัน ascender เหมือนฟอนต์พู่กันอีก 8 ตัว — ไม่ใช่ EXACT_METRICS) + `build_text.FONT_DEFAULT_FACES`
→ DefaultTypeface ที่ทับรวม 11 ตัว · บิลด์ test_24 · ⏳ รอผู้ใช้ดูว่า HUD/หน้าสรุปผลขึ้นไทย และตัวอักษรไม่หด/ไม่โดน crop
(ถ้าหด = อาการ test_13 ให้ย้ายไป EXACT_METRICS · ถ้าวรรณยุกต์โดน crop = คงวิธีดัน ascender ไว้)

### 5.2.0 ⭐ FontFace ทุกตัวใช้ `LayoutMethod = BoundingBox` — ความสูงมาจาก `head.yMin/yMax` (13 ก.ย. 2026)

อ่านจาก uasset ของ FontFace จริง (`FOT-UDKakugo_LargePr6N-DB` · `DF-FutoKaiSho-W9` · `EFIGS/Kuro-Medium` ·
`DF_GOKUBUTOKAISHO_W12`) ทุกตัวมีชื่อ `EFontLayoutMethod::BoundingBox` → Slate คิดความสูงบรรทัด/กล่องจาก
**bounding box รวมของทั้งฟอนต์** ในตาราง `head` ไม่ใช่ ascender/descender/lineGap ของ hhea/OS/2

| ฟอนต์ | bbox vanilla | bbox สำเนา Sarabun | ผลบนจอ |
|---|---|---|---|
| DF-FutoKaiSho-W9 (Font_System `Mincho`) | -144/881 @1024 = 1.00 em | -535/1265 = 1.80 em | test_13 ข้อความเมนูหดทั้งจอ · test_14 หน้าคำเตือนบรรทัดห่าง |
| FOT-UDKakugo (Font_System `Gothic`) | -460/1327 = 1.79 em | 1.80 em | แทบไม่ต่าง |

→ docstring เดิมของ `make_default_typeface_fonts.py` ("FreeType คิด face->height รวม lineGap จึงคุมระยะบรรทัดได้")
**ไม่ครบ** — การดัน ascender ไม่ใช่ตัวกำหนด ตัวกำหนดคือ bbox · fontTools คำนวณ bbox ใหม่ตอน save
ต้องเปิดด้วย `recalcBBoxes=False` · แก้แล้วเฉพาะสองตัวบนใน test_15 (อีก 8 ตัวยังเป็น 1.8 em — ดู HANDOFF §0.60)

### 5.2.1 ⭐ ความสูงบรรทัดมาจาก DefaultTypeface ไม่ใช่ฟอนต์ที่วาดจริง (8 ก.ย. 2026 · ยืนยันบนจอ)

บิลด์ทดสอบตัวแรกของ sprint 19 ทับ DefaultTypeface ด้วย `Sarabun-Regular-ishin.ttf` (1290/-350 upem 1000 = 1.640 em)
ผลบนจอ: บรรทัดห่างขึ้นราว 64% ทั้งเกม + ข้อความล้นกรอบในจอสมุดบันทึก/สารานุกรม
ทั้งที่ตัวอักษรที่วาดจริงมาจาก sub-font EFIGS ไม่ใช่ตัว default
→ Slate ใช้ metric ของ **DefaultTypeface** เป็นตัวตั้งความสูงบรรทัด/การตัดบรรทัดของ CompositeFont

metric ที่วัดจากไฟล์จริง (hhea ascender/descender/lineGap):

| .ufont | upem | hhea | (asc-desc+gap)/upem |
|---|---|---|---|
| `DF-FutoKaiSho-W9` · `DF_ENKAISHO_W5` · `DF_GOKUBUTOKAISHO_W12` · `DF_REISHO_W6` · `TT_KswHannya/Hiryu/Kaisho` | 1024 | 880 / -144 / 0 | 1.000 |
| `TT_KswReisho` | 1024 | 880 / -120 / 0 | 0.977 |
| `TT_KokinEdo-EB` | 1000 | 880 / -120 / 30 | 1.030 |
| `FOT-UDKakugo_LargePr6N-DB` | 1000 | 880 / -120 / 1000 | 2.000 |
| `Kuro-Medium` (EFIGS เดิม) | 1000 | 972 / -258 / 0 | 1.230 |
| `Sarabun-Regular-ishin` | 1000 | 1290 / -350 / 0 | **1.640** |

วิธีที่ใช้ตั้งแต่บิลด์ `test_01`: `scripts/make_default_typeface_fonts.py` สร้างสำเนา Sarabun ต่อ FontFace
โดยคัดลอก metric ของฟอนต์ญี่ปุ่นตัวนั้นมาสเกลเป็น upem 1000 → ความสูงบรรทัดเท่าเกมต้นฉบับ
และ **ไม่ทับ** `DF-FutoKaiSho-W9` กับ `FOT-UDKakugo_LargePr6N-DB` เลย เพราะเป็น DefaultTypeface
ของ `Font_System` ด้วย (ต่อให้ metric ตรง ก็เสี่ยงเกินไปกับจอทั้งเกม — ยังไม่มีหลักฐานว่าจำเป็น)

### 5.3 metric แนวตั้งของ Sarabun ทำวรรณยุกต์ซ้อนสระโดน crop (3 ก.ย. 2026)

| ฟอนต์ | upem | ascender | descender | กลิฟสูงสุด/ต่ำสุด |
|---|---|---|---|---|
| Sarabun-Regular (เดิม) | 1000 | 1068 | -232 | **1265** (`uni0E4C.small`) / -535 (`uni0E39.small`) |
| Kuro-Medium (EN ต้นฉบับ) | 1000 | 972 | -258 | 967 / -224 |
| Sarabun-Regular-ishin (ใช้จริง) | 1000 | **1290** | **-350** | เท่าเดิม |

Slate/FreeType คิดความสูงบรรทัดจาก ascender+descender ของฟอนต์ กลิฟที่โผล่พ้นถูก clip โดยกรอบ widget
วรรณยุกต์ที่ต้องยกขึ้นเหนือสระบน (ั+้ · ิ+่) ใช้กลิฟ `.small` ซึ่งสูง 1200-1265 > 1068 → ส่วนบนหาย
แก้ที่ตัวฟอนต์ (hhea · OS/2 typo · usWin ทั้งสามชุด) ไม่ต้องแตะ uasset

**⭐ กลับมาเป็นอีกรอบกับฟอนต์ช่อง DefaultTypeface (11 ก.ย. 2026 · ภาพผู้ใช้)** — §5.2.1 ให้สำเนาที่ยัดลง
ช่อง DefaultTypeface คัดลอก metric ญี่ปุ่นมาคุมความสูงบรรทัด ผลคือ ascender เหลือ 859/-141 ซึ่งเตี้ยกว่ากลิฟจริง
(1265/-535) วรรณยุกต์ซ้อนสระบนบนจอเหล่านั้นจึงหายทั้งตัว ("นี้"→"นี" · "สิ่ง"→"สิง") ส่วนจอที่วาดด้วย
`Font_System` (sub-font EFIGS = Sarabun-ishin 1290) ปกติ — การแก้สองข้อนี้ตีกันเอง

วิธีที่ใช้ตั้งแต่บิลด์ `test_08`: ตั้ง ascender/descender ให้ครอบกลิฟเต็ม (1265/-535) แล้ว **หักส่วนเกินคืนที่
`lineGap` เป็นค่าติดลบ** เพราะ FreeType คิด `face->height` = ascender - descender + lineGap
→ กรอบ crop ใหญ่พอสำหรับวรรณยุกต์ซ้อน แต่ความสูงบรรทัดยังเท่าฟอนต์ญี่ปุ่นต้นฉบับ (เช่น 1265/-535 gap -800 = 1.000 em)
⏳ รอผู้ใช้ยืนยันบนจอว่าบรรทัดไม่ห่างขึ้น (ถ้า Slate ไม่อ่าน lineGap ติดลบ จะเห็นบรรทัดห่างเฉพาะจอฟอนต์พู่กัน/ซับคัตซีน)

**cmap ที่ขาด**: ข้อความ EN ของเกมใช้ตัวอักษร/วรรคตอน **เต็มหลัก** ปนอยู่มาก (`？` U+FF1F 1,422 ครั้ง · `。` 5,213 ·
`、` 3,717 · U+3000 1,845 · `！` 839 · Ａ-Ｚ ０-９) — Sarabun ไม่มี → Slate วาด `.notdef` ของ Sarabun (กล่องมี ?)
ไม่ได้ตกไปฟอนต์สำรอง DroidSansFallback (แปลว่าเกมปิด font fallback ของ Slate ไว้)
→ `scripts/make_thai_font.py` เพิ่ม cmap alias 104 ตัวชี้กลิฟ ASCII ที่มีอยู่ · ที่ยังไม่มี: ★●♪※①② และ CJK

### 5.4 ตาราง label ของ .msg = ชื่อผู้พูด + ป้ายปุ่มโต้ตอบ + ตัวเลือกเมนู (ยังไม่แปล)

`labels` ใน .msg ไม่ได้มีแต่ไอดีคิวเสียง/ท่าทาง — "Young Woman" (ชื่อผู้พูดฉากเปิด) และ "Pray"
(ป้ายปุ่ม `E` หน้าศาลเจ้า · บรรทัดที่อ้างถึงมี `en` ว่าง) ก็อยู่ในตารางนี้ และไม่อยู่ใน locres/ARMP เลย
→ ข้อความชุดนี้ไม่เคยเข้าคิวแปล · สถานะ POC และขนาดงาน: `HANDOFF.md` §0.47

### 5.5 บล็อกคำสั่งของ .msg เก็บ "ตำแหน่งตัวอักษร" — ต้องปรับตามคำแปล (3 ก.ย. 2026)

ทุกคำสั่ง 16 ไบต์ในบล็อกคำสั่งของบรรทัด: ไบต์ [6:8] = ตำแหน่งตัวอักษรในบรรทัด (0 = ไม่ใช้)
| หลักฐาน | ค่า |
|---|---|
| EN `Been a minute, Sakamoto-san.` 28 ตัว/28 ไบต์ | `01 01` → 28 · `02 09` → (14, 28) |
| JA `久しぶりやね、坂本さん。` 12 ตัว/36 ไบต์ | `01 01` → 12 · `02 09` → (7, 12) → **นับตัว ไม่ใช่ไบต์** |
| บรรทัดมี `
` หนึ่งคู่ | ค่า = len-1 → CRLF นับหนึ่ง (2,008/2,130 บรรทัด) |
| กวาด 32,806 บรรทัด EN ทุกชนิดคำสั่ง | ค่าเกินจำนวนตัวอักษร **0 ครั้ง** · `01 01` = ความยาว 30,753 · `02 09` = ความยาว 28,078 |

เกมแสดง/เล่นเสียงถึงตำแหน่งจบแล้วหยุด → ถ้าไม่ปรับ ไทยที่ยาวกว่า EN (นับตัว) ถูกตัดท้าย
`tools/msg.py` `retime_cmds()` ปรับให้ตอน `rebuild()` · ด่าน `check_msg_translated.py` เทียบ vanilla+retime

### 5.6 ข้อความที่ฝังใน `wdr_en/pac/*.bin` (ยังไม่มีในไปป์ไลน์) — 3 ก.ย. 2026

`pac_STID_ST_<ฉาก>.bin` 168 ไฟล์ (มีคู่ `wdr_ja/pac/`) = ไฟล์วางวัตถุ/NPC ประจำฉาก มีสตริงแสดงผลฝังอยู่:
- ป้ายปุ่มโต้ตอบพิเศษ: `Pray ` (JA `参拝`) ใน TOSA · KYOTO · GION · RINDOU · RYOMA_IE — ป้ายทั่วไป
  (Talk/Examine/Enter) มาจาก locres namespace `surfboard` คีย์ `ActionButton/NN` และแปลได้แล้ว
- เสียงตะโกน NPC ในฉาก ("Calling all couriers!" · "Up for a palanquin ride?" · "(Okita's occupied right now...)")
  ≈ 70 สตริง ส่วนใหญ่ใน KYOTO
สตริงยาวไม่คงที่ (NUL ปิดท้าย · padding ถึง 4 ไบต์) · ไฟล์ EN/JA ขนาดต่างกัน 40/168 ไฟล์ · ส่วนหัวมีตาราง
(offset, size) ของแต่ละส่วน (TOSA: จุดต่างแรก @0x353 `72 74 04 68` vs `72 70 04 64`) → ประกอบกลับต้องอัปเดตตาราง
label "Pray" ใน .msg **ไม่ใช่**แหล่งแสดงผล (แปลแล้วจอไม่เปลี่ยน · ทดสอบ 3 ก.ย. 2026)

ยืนยันเพิ่ม 13 ก.ย. 2026 (ภาพผู้ใช้): บทพูดลอยของ NPC เดินถนนในเกียวโต (`You really saved me last time!` ·
`Gotta pick a side, you're in the way...` · `Oh no, I should be thanking you.`) ขึ้นอังกฤษบนจอ
สแกนไบต์ UTF-8/UTF-16 ทุกไฟล์ใน pak ทั้ง 7 ลูก + IoStore 104,581 ไฟล์ → มีใน `pac_STID_ST_KYOTO.bin` ที่เดียว
(ประโยคสุดท้ายซ้ำกับ `uid00330d54.msg` แต่จอดึงจาก pac)

#### 5.6.1 โครง `pac_STID_*.bin` — แกะครบแล้ว + ด่านตรวจข้ามภาษาผ่าน (13 ก.ย. 2026)

เครื่องมือ `tools/pac.py` · ด่าน `scripts/check_pac_roundtrip.py` · ถอด `scripts/extract_pac_text.py`
(ไฟล์ทั้งหมดอ่านตรงจาก pakchunk0 · 168 ไฟล์ต่อภาษา · ชื่อ `pac_STID_{ST,MG,TE}_*` ไม่ใช่แค่ `ST_`)

**ชั้นไฟล์** (big-endian)
| ออฟเซ็ต | ชนิด | ความหมาย |
|---|---|---|
| 0x00 | u16 | จำนวนเรคคอร์ด N (KYOTO 7,990) |
| 0x02 | u16 | 0 |
| 0x04 | u32 | 8 = ตำแหน่งตาราง |
| 0x08 | N×16 | u32 record id · u32 offA · u32 offB · u16 lenA · u16 lenB |
| หลังตาราง | 8 ไบต์ | ศูนย์ (KYOTO ตารางจบ 0x1f368 ข้อมูลเริ่ม 0x1f370) |
| ต่อไป | | A แล้ว B ของทุกเรคคอร์ดตามลำดับ · แต่ละส่วน pad ถึง 4 · ส่วนยาว 0 → off = 0 |

B (ทุ่น/พิกัด) **เหมือนกันทุกภาษาทุกเรคคอร์ด** · record id ลำดับเดียวกันทุกภาษา · lenA/lenB เป็น u16 (จำกัด 65,535 ไบต์/ส่วน)

**ส่วน A = คอนเทนเนอร์ตระกูลเดียวกับ `.msg`** (ออฟเซ็ตนับจากต้น A) — มี magic 0x20 หรือ 0x40
| ออฟเซ็ต | ชนิด | ความหมาย |
|---|---|---|
| 0x00 | u8 ×4 | magic · ธง 2 ไบต์ (ยังไม่รู้ความหมาย คัดลอกดิบ) · **จำนวนกลุ่ม G** |
| 0x04 | u32 | 0x18 = ตำแหน่งตารางกลุ่ม |
| 0x08 | u32 | ตำแหน่งตาราง extra (0 = ไม่มี) |
| 0x0c | u16+u16 | จำนวน extra · จำนวน label |
| 0x10 | u32 | ตำแหน่งพอยเตอร์ label (0 = ไม่มี) |
| 0x14 | u32 | 0 ทุกเรคคอร์ด |
| 0x18 | G×16 | u32 data_off (ชี้เข้าก้อนข้อมูลกลุ่ม · 0 = ไม่มี) · u32 entry_off · u8[8] ธง (**ธง[1] = จำนวน entry ของกลุ่ม**) |
| ต่อไป | ×12 | entry: u16 ความยาวสตริง (ไบต์) · u16 จำนวนคำสั่ง<<8 · u32 str_off · u32 cmd_off — ตัวอย่าง KYOTO 0x22214: EN `00 1e 03 00 …c4 …34` / JA `00 2d 02 00 …b4 …34` |
| ต่อไป | ×16 | บล็อกคำสั่ง ต่อกันตามลำดับ entry (opcode ชุด .msg · ไบต์ [6:8] = ตำแหน่งตัวอักษร) |
| ต่อไป | ดิบ | ข้อมูลกลุ่ม — ข้างในเก็บ **ดัชนี label** (ไม่มีออฟเซ็ต) |
| ต่อไป | | สตริง UTF-8 ปิด NUL ต่อกันตามลำดับ entry (สตริงว่าง = NUL ตัวเดียว · 23,908 ตัวใน EN) |
| pad4 | ×16 | ตาราง extra (float พิกัด) — ถ้ามี |
| pad4 | ×4 + สตริง | พอยเตอร์ label + สตริง label ต่อกัน — ถ้ามี |
| ท้าย | | จบด้วยสตริง entry → lenA **รวม** pad ถึง 4 · จบด้วย extra/label → lenA **ไม่รวม** pad |

ส่วนหัว/ตารางกลุ่ม/ตาราง entry ขนาดคงที่ → ฟิลด์ที่ขึ้นกับความยาวสตริงคือ: ความยาวใน entry · str_off ·
cmd_off (ถ้าบล็อกคำสั่งเปลี่ยนขนาด) · data_off · ตำแหน่ง extra/label · พอยเตอร์ label · lenA · offA/offB ของทุกเรคคอร์ดถัดไป
ตัวประกอบคำนวณใหม่ทั้งหมดจากเลย์เอาต์ (ไม่ปะทีละฟิลด์)
⚠ บทเรียนระหว่างทำ: รอบแรกจำ "pad ท้ายหรือไม่" เป็นธงรายเรคคอร์ด → ต้นฉบับที่ยาวหารสี่ลงตัวบังเอิญ
ถูกจำว่า "ไม่ pad" แล้วพอแทนสตริงก็ได้ขนาดผิด (oracle 1 ผ่านแต่ oracle 2 จับได้) — ที่ถูกคือกฎตายตัว

**ตำแหน่งตัวอักษรในบล็อกคำสั่ง** = หน่วยเดียวกับ .msg (`disp_chars` นับตัว ไม่ใช่ไบต์):
KYOTO 0x22214 EN `01 01 … 00 1e` (30 ตัว/30 ไบต์) · JA `… 00 0f` (15 ตัว/45 ไบต์) · DE `… 00 27` (39)
→ ใช้ `msg.retime_cmds` ตัวเดิม

**ผล oracle** (`check_pac_roundtrip.py` · 9 ภาษา en ja de fr it es ko cn tw)
| ด่าน | ผล |
|---|---|
| 1: parse → rebuild ไม่แก้ | **1,512/1,512 ไฟล์ตรงไบต์** · เรคคอร์ดอ่านไม่ได้ 0 (ส่วน A แบบข้อความ 149,643 ก้อน) |
| 2b: EN + สตริงและบล็อกคำสั่งของภาษา X → == ไฟล์ภาษา X | **168/168 ทุกภาษา** (8 ภาษา) |
| retime จุดจบบรรทัด (บรรทัดที่คำสั่งตรงกันยกเว้นตำแหน่ง) | ผิด **0** ทุกภาษา · ตรงทุกไบต์ ~24,200 บรรทัด/ภาษา · จุดกลางบรรทัดประมาณ 85–281 บรรทัด/ภาษา |
| 2a: แทนสตริงอย่างเดียว + retime | ja 147 · de 135 · fr 136 · it 135 · es 131 · ko 135 · cn 136 · tw 136 (/168) |

2a ไม่ผ่านครบ **โดยชอบธรรม** และแยกสาเหตุได้ครบทุกไฟล์ (2b ผ่านหมด = ต่างกันแค่ในบล็อกคำสั่ง/label):
แต่ละภาษาใส่คำสั่งจังหวะเอง (จำนวนคำสั่งต่าง ja 209 · es 291 · cn 268 · tw 269 · ko 213 · de 80 · fr 76 · it 66 บรรทัด)
และบางภาษา **รวม label ซ้ำ** (KYOTO 006e030f EN `Have you considered a palanquin ride?`+`Up for a palanquin ride?` → JA `駕籠どうでっか？` ตัวเดียว ·
DE กลับกันแยก `Trade Order` เป็นสองตัว) ข้อมูลกลุ่มจึงอ้างดัชนี label ต่างกัน → **ห้ามเปลี่ยนจำนวน label ตอนแปล** (`build()` กันไว้)

**สตริง** (`extracted/text_en/pac.json`)
- สตริงไม่ว่าง 2,724 (unique 1,070) · **ต้องแปล 884 (unique 511)** = บรรทัด 666 + label 218 · มีช่องว่าง 661
- ไอดี 1,840 (label ทั้งหมด: `Talk_Kamae` · `M_BUS_TLK_*` · `P_MOV_stand_serch_tubo` · `7e008100` · คิวเสียง `majima_adv_*`)
- ตัวแยก = หลักฐานข้ามภาษา: ต่างจาก EN อย่างน้อยหนึ่งใน 8 ภาษา หรือมีคานะ/คันจิตกค้าง (`く 苦しぃ～`)
  label ที่จำนวนต่างระหว่างภาษาเทียบแบบ "อยู่ในตารางไหม" ไม่เทียบดัชนี (ไม่งั้น `M_CHO_TLK_seiza_kamae` ดูเหมือนถูกแปล)
- label ที่ต้องแปลได้แก่ ชื่อร้าน/จุดบริการ (`Blacksmith` · `Uji Tea Parlor` · `Recipient` ×52) · ปุ่ม `Pray` ×14 · ชื่อ NPC (`Harada`) · เสียงตะโกนเรียกเกี้ยว
- กระจุก: KYOTO 570 · TE_0009 51 · MIBUDERA_SOTO 29 · อื่น ๆ ≤13 · มีข้อความต้องแปล 45/168 ไฟล์
- ⚠ ตัวเลขนี้ไม่ตรงกับที่นับไว้ก่อนหน้า (~618 ประโยค / KYOTO 416) เพราะนับจากโครงจริง รวม label และบรรทัดไม่มีช่องว่าง (`Dammit!`)
- smoke test (ไม่อยู่ในสคริปต์): แทนไทยทุกสตริง 2,724 ตัว (มี `<Color:8>`) → parse ใหม่ได้สตริงตรง · เรคคอร์ดที่ไม่แตะตรงไบต์ ·
  จุดจบ 1,681 จุด = `disp_chars` ใหม่ · ไฟล์รวมโต +155 KB · lenA ใหญ่สุด 8,480 (ยังห่างขีด u16)

**ยังเปิด**
1. ยังไม่ทดสอบในเกม — pac ที่ขนาดเปลี่ยนน่าจะโหลดได้ (vanilla ต่างขนาดข้ามภาษา 40/168 ไฟล์) แต่ต้องให้ผู้ใช้ยืนยัน
2. ความหมายของธงในส่วนหัว A/ธงกลุ่ม/ข้อมูลกลุ่ม · magic 0x20 vs 0x40 — ไม่จำเป็นต่อการแปล (คัดลอกดิบ) แต่ยังไม่รู้
3. label ไม่ใช่ UTF-8 สองตัว (KYOTO 01261563#L0 · 05261213#L0 = Shift-JIS `駕篭の体力` เหมือนทุกภาษา) — จัดเป็นไอดี
4. `pac.json` วางใน `extracted/text_en/` ซึ่งหลายสคริปต์ glob `*.json`: `build_text.py`/`make_label_poc.py` ข้ามเอง (ไม่มี `pac.msg`)
   แต่ `scope_report.py` จะนับแถวรวมเข้าไป และ `build_parallel.py` จะรายงาน "ไม่มีฝั่ง ja" — ต้องจัดการตอนผนวกเข้าไปป์ไลน์
5. ยังไม่ผนวกเข้า `build_text.py` / `pack_release.py` (path ในเกม `data/wdr_en/pac/<ไฟล์>`) · ตำแหน่งกลางบรรทัดหลัง retime เป็นค่าประมาณแบบเดียวกับ .msg

### 5.2 สองอาการที่รายงานเข้ามาแล้ว **ไม่ใช่บั๊กของม็อด**

| อาการบนจอ | ข้อเท็จจริงจากไฟล์ต้นฉบับ |
|---|---|
| การ์ดทหารหน่วย (taishi) ขึ้นชื่อเป็น `???????` | `Game.en.locres` ของเกมแท้มีสตริง `???` · `?????` · `??????` อยู่แล้ว (ฝั่ง JA เป็น `？？？　天狗面の男` ฯลฯ) = ป้ายชื่อการ์ดที่ยังไม่ได้ปลดล็อก |
| บอลลูน NPC ขึ้นเป็นจุดไข่ปลาล้วน | `lines_en.json`/`Game.en.locres` มีบรรทัด `......` · `.....` · `…………` อยู่แล้ว และ **ไม่มีบรรทัดจุดล้วนอยู่ใน `master_th.json` เลย** = ม็อดไม่เคยแตะบรรทัดพวกนี้ |

---

## 6. การติดตั้งม็อด — ยืนยันในเกมแล้ว

ต้องครบสามข้อ ขาดข้อใดข้อหนึ่งเกมจะเงียบ ไม่มี error ไม่มี log:

1. วางที่ `Content/Paks/~mods/` (สร้างโฟลเดอร์เอง)
2. ชื่อไฟล์ลงท้าย `_P`
3. **FullDirectoryIndex ใน pak ต้องมีทุกชั้นของโฟลเดอร์** ไล่ตั้งแต่ `/` ลงไป
   ชั้นกลางมี 0 ไฟล์ — ข้อนี้คือข้อที่ทำให้ pak แรก ๆ ไม่ถูก mount

ค่าอื่นในโครง pak ที่ถอดจากไฟล์แท้ของเกมแล้วยืนยันว่าถูก:
- mount point ของ pak แท้ = `../../../LikeaDragonIshin/Content/` (ของ repak ใช้ `../../../` ก็ได้)
- pak แท้เขียนทั้ง PathHashIndex และ FullDirectoryIndex
- **path hash = FNV-1a 64** บน lowercase UTF-16LE · ค่าตั้งต้น = FNV offset basis **บวก** PathHashSeed
  (ไม่ใช่ CRC32 — ชื่อเวอร์ชันในซอร์ส UE คือ `Fnv64BugFix`) พิสูจน์โดยคำนวณย้อนกับ pakchunk3
- ขนาดบล็อก PathHashIndex = `4 + N*12 + 4` (4 ไบต์ท้าย = pruned directory index ที่มี 0 โฟลเดอร์)
- หัว FPakEntry ที่ฝังหน้าไฟล์ = 53 ไบต์ · encoded entry ไม่บีบอัด = flags `0xE0000000` + offset u32 + size u32

**ไฟล์ loose ทับของใน pak ไม่ได้** — `FPakPlatformFile` ค้นใน pak ก่อนเสมอ
loose ใช้เพิ่มไฟล์ใหม่ได้เท่านั้น (ทดสอบแล้ว ไม่ได้ผล)

---

## 6.4 ⚠ ตาราง ARMP ของภาคนี้ **ซ้อนกันได้** — ข้อความจริงของ tips อยู่ชั้นใน

แถวหนึ่งของตาราง ARMP มีคีย์ `table` ที่เป็นตารางเต็ม ๆ อีกชั้นได้ (มี `columnTypes` / แถว / ช่องของตัวเอง)
ข้อความของ `tips` (จอทิปส์และสมุดบันทึก) อยู่ในชั้นซ้อนนี้ **968 ช่อง** — ตัวดึงและตัวเขียนรุ่นแรก
เดินแค่ชั้นบน จอทิปส์จึงขึ้นหัวข้อเป็นไทยแต่เนื้อเป็นอังกฤษ (เจอจากการทดสอบในเกม 3 ก.ย. 2026)

- ตัวเขียน: `build_text._replace_table()` เรียกตัวเองซ้ำเมื่อเจอ `row["table"]`
- ตัวดึงเข้าคิวแปล: `scripts/make_worklist_db_nested.py`

⚠ **คอลัมน์ชนิด 13 (สตริง) ปนของสองแบบ**: ข้อความบนจอ กับ **ไอดี/พาธของแอสเซต**
(`c_cm_ryoma` · `WEPCT2700` · `item/Accessory` · `Wanderer/ACT/` · `T_UI_Tips_glossary01`)
ตัวดึงจึงใช้ **บัญชีขาวรายตาราง** (`tips` · `photo_stamp` · `option`) + ตัวกรอง
"ต้องมีช่องว่าง · ไม่ขึ้นต้นด้วย `<%` · ไม่มี `/`" — เคยพลาดมาแล้วจนได้ `ทดสอบไทย wepct9000`
เขียนทับ asset id ทั้งตาราง `battle_bomb_info`

**คอลัมน์ที่ `shift < 0` เทียบค่าไม่ได้**: `sound_speak_data` คอลัมน์ `*` (ชนิด 1) ไม่ได้เก็บไว้ในแถว
reARMP อ่านกลับได้ 3840 แทน 512 ทั้งที่ไบต์ในแถวตรง vanilla 4,044/4,045 แถว (aux/types/layout ตรงหมด)
→ เป็นค่าที่ตัวอ่านสังเคราะห์เอง **ไม่ใช่ข้อมูลพัง** · `check_armp_translated.py` จึงข้ามคอลัมน์แบบนี้

---

## 6.5 ⚠ บั๊กตัวเขียน `.msg` ที่เจอจากการทดสอบในเกม (3 ก.ย. 2026) — แก้แล้ว

**อาการบนจอ**: กล่องบทสนทนาขึ้นชื่อผู้พูดแต่ **ข้อความว่างเปล่า** · บางบรรทัดขาดกลางประโยค
· **กล้องคัตซีนค้างหลังฉาก** ไม่ตามตัวละคร

**ต้นเหตุ**: ช่วง "บล็อกสตริง" ของไฟล์ `.msg` **ไม่ได้มีแต่สตริง** — ตารางพอยเตอร์ของ label
(`label_count * 4` ไบต์) นอนอยู่ **กลางช่วงนั้น** เรียงเป็น สตริงบรรทัด → ตารางพอยเตอร์ → สตริง label
`MsgFile.rebuild()` เดิมตัดทั้งช่วงด้วย NUL เหมือนเป็นสตริงล้วน แล้วเขียนพอยเตอร์ label กลับที่
**ตำแหน่งเดิม** ทั้งที่บล็อกขยายไปแล้ว (ไทยยาวกว่าอังกฤษ) → พอยเตอร์ 4 ไบต์ไปทับกลางข้อความไทย

วัดได้จริงตอนเจอ: **ข้อความเสีย 1,418 บรรทัดใน 1,017 ไฟล์** · ตาราง label เพี้ยน
ซึ่ง label คือชื่อฉาก/ท่าทาง/คิวเสียง (`TLK_SCN001` · `Idle` · `Talk_Yes`) → คำสั่งกล้องในคัตซีนพังตาม

**ทำไมด่านเดิมจับไม่ได้**: `check_msg_roundtrip.py` ประกอบไฟล์กลับแบบ**ไม่แทนที่อะไรเลย**
ความยาวจึงไม่เปลี่ยน · `shift = 0` · เขียนทับที่เดิมพอดี → รายงานว่าผ่านทั้งที่ไฟล์ที่แปลแล้วพัง
(บทเรียนเดียวกับ LJ-011 คนละหน้ากาก)

**ที่แก้**: `rebuild()` ยกตารางพอยเตอร์มาทั้งก้อนโดยไม่ตัดด้วย NUL · จำตำแหน่งใหม่ (`new_lpt`)
· ทำแผนที่ออฟเซ็ตเดิม→ใหม่ (`_map`) ใช้กับทุกฟิลด์ในหัวไฟล์ที่เป็นออฟเซ็ต
· **ยกเว้น `header[3]` ซึ่งเป็นจำนวน label ไม่ใช่ออฟเซ็ต** (เคยโดนบวก shift จนจำนวน label เพี้ยน)

**ด่านใหม่ที่ต้องรันทุกครั้งหลังบิลด์**: `scripts/check_msg_translated.py`
เทียบไฟล์ที่บิลด์จริงกับ `master_th.json` ทีละบรรทัด + เทียบตาราง label และบล็อกคำสั่งกับ vanilla
ต้องได้ **ต่าง 0** (ตอนแก้เสร็จ: ตรวจ 52,569 บรรทัด · ต่าง 0)

---

## 7. คำถามเปิด (เรียงตามความสำคัญ · อัปเดต 1 ก.ย. 2026 รอบ 3)

1. ~~**pak ที่ `tools/pakwrite.py` เขียนเอง โหลดในเกมจริงไหม**~~ — **ทดสอบแล้ว 3 ก.ย. 2026: ไม่โหลด**
   ม็อดที่แพ็กด้วย `pakwrite.py` (1,301 ไฟล์ · path hash seed `1234ABCD`) เข้าเกมแล้ว **จอไตเติลยังเป็นอังกฤษล้วน**
   เนื้อ pak ชุดเดียวกันเป๊ะ แพ็กใหม่ด้วย `tools/repak/repak.exe` (seed `00000000`) → **ไทยขึ้นทั้งเกม**
   → ระหว่างที่ยังไม่ได้ไล่หาสาเหตุใน `pakwrite.py` **ให้แพ็กด้วย repak เท่านั้น**
   (ขั้นตอน: แตก pak ที่ `build_text.py` สร้าง ลงโฟลเดอร์ตาม path ในเกม แล้ว
   `repak.exe pack --mount-point ../../../ --version V11 <dir> <out>_P.pak`)
2. **ไฟล์ที่ยาวขึ้นเกมรับไหม** — roundtrip เท่าเดิมผ่านแล้วทั้ง `.msg` แต่ยังไม่เคยลองของยาวขึ้นในเกม
3. ความหมายรายฟิลด์ของ opcode `0x02` (ต้องรู้ถ้าจะแตะการขึ้นบรรทัด/ความเร็วข้อความ)
4. ชนิดย่อยอื่นของ opcode `0x03` — รู้แล้วว่า `0x35` คือ "เล่นเสียงบรรทัดนี้" (§9)
   ที่เหลือ (`0x1f` 56,304 ครั้ง · `0x29` 15,618 · `0x09` 11,653 · `0x16` 6,217) ยังไม่รู้ความหมาย
5. `wdr_<lang>/pac/*.bin` (168 ไฟล์/ภาษา) เก็บอะไร — ชื่อไฟล์เป็น `pac_STID_ST_*` = แยกตามฉาก
6. `wdr_en` ยังมี `shop/` 68 ไฟล์ · `common/` 9 · `cmt/` · `dispose_string.bin` · `snitch.bin`
   — ยังไม่แกะ (อาจมีข้อความเพิ่ม)
7. ยังไม่ได้สำรวจว่ามีม็อดแปลภาษาอื่นของ Ishin! อยู่แล้วหรือไม่

### ปิดไปแล้ว
- ~~UI ภาษาอังกฤษมาจากไฟล์ไหน~~ → สองแหล่ง: `db.macan/en/*.bin` (ARMP) + `Game.locres` (§4)
- ~~เกมโหลด pak เสริมไหม~~ → โหลด · เงื่อนไขครบสามข้อดู §6 (ยืนยันบนจอจริง)
- ~~ฟอนต์อยู่ไหน + วางสระซ้อนไทยได้ไหม~~ → ยัด `.ttf` ทับ `.ufont` · UE เปิด HarfBuzz ไว้
  สระบน/ล่างและวรรณยุกต์วางถูกตำแหน่งทุกตัว (ยืนยันบนจอจริง)
- ~~เพศผู้พูด/ผู้ฟังมาจากไฟล์ไหน~~ → **ไม่มีตารางเพศในภาคนี้** ตรวจครบ 244 ตาราง ARMP
  แล้วไม่มีคอลัมน์ sex/gender · `TextBridge/AuthSpeaker/` เป็นแค่ข้อความชื่อผู้พูด
  ทางออกที่ใช้แทนอยู่ใน §10

---

## 8. เครื่องมือที่มีแล้วในโปรเจกต์นี้

| ไฟล์ | ทำอะไร | สถานะ |
|---|---|---|
| `tools/iostore.py` | อ่าน/แตก `.utoc`+`.ucas` | ✅ ใช้ได้จริง (เขียนเอง) |
| `tools/pakfile.py` | อ่าน/แตก `.pak` v11 | ✅ ใช้ได้จริง (เขียนเอง) |
| `tools/msg.py` | อ่าน/ประกอบ `.msg` | ✅ อ่านได้ · roundtrip ไบต์เป๊ะ 1,678/1,678 |
| `tools/reARMP_fixed.py` | อ่าน/เขียน ARMP | ✅ ยกจาก LJ ใช้ได้ตรง ๆ · ⚠ ไม่ byte-identical (§4.1) |
| `tools/locres.py` | อ่าน/เขียน `.locres` | ✅ ยกจาก Frostpunk 2 ใช้ได้ตรง ๆ |
| `scripts/extract_msg.py` | แตกคลัง `.msg` → JSON | ✅ รันแล้ว (EN 1,678 ไฟล์ · 50,233 สตริง) |
| `scripts/extract_db.py` | แตก ARMP → JSON | ✅ รันแล้ว (EN 122 ตาราง · TEXT_COUNT 17,501) |
| `scripts/extract_locres.py` | แตก `Game.locres` → JSON | ✅ รันแล้ว (EN 23,507 entry) |
| `scripts/check_msg_roundtrip.py` | ด่านตรวจไบต์ดิบ | ✅ ผ่าน |
| `scripts/paths.py` | path กลาง | ✅ verify กับไฟล์จริงแล้ว |
| `tools/pakfile.py` `write_pak()` | **เขียน** pak ม็อด | ✅ ใช้ได้จริง — บิลด์แล้ว 1,301 ไฟล์ · 20.2 MB · `check_pak_roundtrip` ต่าง 0 |
| `scripts/build_text.py` | ประกอบข้อความสามชั้น + แพ็ก pak (+`--install`) | ✅ ใช้ได้จริง (msg 29,561 บรรทัด · armp 11,404 ช่อง · locres 22,794 คีย์) |
| `scripts/merge_qc.py` | ด่าน QC + เขียน `master_th.json` | ✅ ทั้งคลัง 41,601 · ตก 0 |
| `scripts/prune_dnt.py` | ถอดคีย์ที่แปลไทยแล้วออกจาก `.dnt.json` | ✅ ใช้แล้ว 318 คีย์ |
| `scripts/review_facts.py` | สรุปตัวเลขรายก้อนไว้เขียนไฟล์รีวิว | ✅ ใช้ปิดคลื่น MSG_073–083 |
| `scripts/ui_length_risk.py` | วัดบรรทัดไทยที่ยาวเกินกรอบชั้น UI | ✅ 302 สตริง (เกิน 1.8× ของ EN) |

---

## 9. คำสั่ง `0x03` ชนิดย่อย `0x35` = "เล่นเสียงของบรรทัดนี้" (แกะ 1 ก.ย. 2026)

**เรื่องนี้สำคัญเพราะมันคือหลักฐานผู้พูดรายบรรทัดเพียงตัวเดียวที่เชื่อได้ในชั้น `.msg`**

คำสั่ง `0x03` ถูกใช้อ้างถึง label ทุกชนิด ไม่ใช่แค่คิวเสียง — รวม **ตัวเลือกในเมนูสนทนา**
ที่ค้างอยู่กับทุกแถวในบล็อกเดียวกัน ถ้าเอา label ตัวแรกที่หน้าตาเหมือนคิวเสียงมาใช้จะได้ผู้พูดผิด

หลักฐานที่วัดจากคลัง EN ทั้ง 1,678 ไฟล์:

| ชนิดย่อย `byte[1]` | จำนวน | label เป็นชื่อคิวโรมาจิ | ไม่ใช่ |
|---|---:|---:|---:|
| `0x35` | 4,113 | 3,989 | 124 |
| `0x1f` | 56,304 | 3,858 | 52,446 |
| `0x29` | 15,618 | 5 | 15,613 |
| `0x09` | 11,653 | 98 | 11,555 |
| `0x16` | 6,217 | 860 | 5,357 |

- `0x35` มี **อย่างมากหนึ่งตัวต่อบรรทัดเสมอ** (4,113 บรรทัดมีหนึ่งตัว · 50,205 ไม่มีเลย · ไม่มีบรรทัดไหนมีสอง)
- label ที่มันชี้เป็นชื่อคิวเสียงโรมาจิ (`otose_adv_c02_150_001`) หรือ **ชื่อผู้พูดบนจอตรง ๆ**
  (`Ryoma` · `Otose` · `Gate Guard`) — ที่เหลือเป็นชื่อท่าทาง/ฉาก

**เคสที่ทำให้เจอ**: ตัวสร้างทะเบียนเพศรอบแรกตัดสินฮารุกะกับโอเรียวเป็น "ชาย" ทั้งที่ทั้งคู่เป็นหญิง
เพราะบรรทัดรำพึงของเรียวมะพก label `haruka_door_s02_004` ติดมาด้วย (ชนิดย่อย `0x16` ไม่ใช่ `0x35`)

API: `tools/msg.py` → `Line.speaker_label_ref()` · ช่อง `voice` ใน `to_records()`

---

## 10. เพศผู้พูด — ภาคนี้ไม่มีตารางเพศ ใช้หลักฐานอื่นแทน

ตรวจแล้วไม่มีคอลัมน์ `sex`/`gender` ในตาราง ARMP ทั้ง 244 ตาราง (ต่างจาก Dragon Engine
ที่มี `sound_voicer.bin`) หลักฐานที่ใช้แทน เรียงตามความน่าเชื่อ:

| ที่มา | ครอบคลุม | หมายเหตุ |
|---|---|---|
| `correlation_person_explanation` ใช้ he/she | ตัวละครหลัก 35 คน | **แม่นที่สุด** — ประวัติตัวละครในแผนผังของเกมเอง |
| ต้นฉบับญี่ปุ่นใน pak เดียวกัน (สรรพนาม/คำลงท้าย) | ผู้พูด 169 ป้าย | 俺 · あたし · わし · かしら · ですわ |
| ป้ายผู้พูดที่บอกเพศในตัวเอง | `Mother` · `Geisha` · `Boy` | เฉพาะคำที่ตัวมันเองแปลว่าเพศนั้น |
| สรรพนามคันไซ (ชั้นรอง) | โอเรียว · อิคุ | うち หญิง · わい ชาย — อ่อนกว่า ใช้ต่อเมื่อชั้นหลักตัดสินไม่ได้ |

ผลรวม: **ชาย 44 · หญิง 19 · พิสูจน์ไม่ได้ 106** จาก 169 ป้ายผู้พูด
(ที่พิสูจน์ไม่ได้ส่วนใหญ่เป็นป้ายกลุ่มคน เช่น `Employee` 946 บรรทัด ซึ่ง**บังคับกลางเพศเสมอ**
เพราะคนหลายสิบคนหลายเพศใช้ป้ายเดียวกัน)

รายละเอียดรายคน: `docs/reference/gender_evidence_ishin.md` · เครื่องมือ: `scripts/build_speaker_gender.py`

### 10.1 ป้าย (`labels`) ของ `.msg` เป็นหลักฐานเพศได้แค่ไหน — วัดทั้งคลัง (13 ก.ย. 2026)

วิธี: นับบรรทัดที่มีป้ายนั้นและมีเครื่องหมายเพศในตัว (`merge_qc.ja_gender`) แยกชาย/หญิง

| ป้าย | ชาย | หญิง | สรุป |
|---|---:|---:|---|
| `Player` | 410 | 9 | ใช้ไม่ได้ — หญิง 9 เช่น โอมัตสึ `uid01160831#038` |
| `Ryoma` | 289 | 2 | ใช้ไม่ได้ |
| คิวเสียง `haruka_*` / `oryo_*` / `otose_*` | 7 / 8 / 4 | 0 / 0 / 0 | **ตรงข้ามกับตัวละคร** — ป้ายคิวเกาะบทคนอื่น |
| คิวเสียง `kiryu_*` · `majima_*` · `kondo_*` | 279 · 60 · 37 | 0 | ตรงเพศ แต่ไม่ได้พิสูจน์ว่าเป็นบทของคนนั้น |
| ป้ายที่มีคำบอกเพศหญิง (`Old Woman` · `Uchitaro's Mother` ฯลฯ) | 72 | 26 | ใช้ไม่ได้ |
| ป้ายที่มีคำบอกเพศชาย | 304 | 12 | อ่อน |
| `Sexy Madam` · `Junk Boy` · `Tom` | 0 · 15 · 14 | 13 · 0 · 0 | ผ่านเกณฑ์ |

เกณฑ์ที่ใช้ใน `merge_gender_wave.py`: ป้ายเดี่ยว ๆ ต้องมีเครื่องหมายเพศที่อ้าง ≥5 และเพศตรงข้าม 0

### 10.2 ⭐ ตารางตัวละคร UE (`DataTable/Characters/info/*.uasset`) มีช่องเพศจริง (13 ก.ย. 2026)

แก้ข้อสรุปเดิมบางส่วน: ARMP ไม่มีตารางเพศก็จริง แต่ **DataTable ของ UE ที่กำหนดหน้าตาตัวละครมี** —
12 ตาราง (battle · longbattle · macan · minigame · npc · public · scenario* · substory · taisi_ikusei)
แต่ละแถวมีช่องบอกเพศที่เป็นอิสระต่อกันสามช่อง + โมเดล:

| ช่อง | ค่าที่เจอ |
|---|---|
| id แถว | `c_em_*` ชาย · `c_ew_*` หญิง · `c_ek_*` เด็ก |
| ชนิด | `一般男` · `一般女` · `子供男` · `巨漢男` |
| ประเภทเสียง | `男性_老人_京都弁` · `女性_若者_普_京都弁` ฯลฯ |
| โมเดล หน้า/ตัว/ผม | `c_cm_*` ชาย · `c_cw_*` หญิง · `c_ck_*` เด็ก · `c_am/c_aw` ตัวละครหลัก |

ยืนยันวิธีกับเคสที่รู้คำตอบ: お咲/お菊/お鈴 (ชื่อรูปหญิง · EN "his") = `c_em_SS14_man_0x` · 一般男 · `c_cm_x_sumo`
ผลที่ได้: **คามาโมโตะ** `c_em_SS15_kamatukai` = 一般男 · 男性_老人_京都弁 · `c_cm_f_SS15_kama` → ชาย
(กลุ่มโอกามะ `オカマ集団１-５` · `このは（オカマver）` เป็น c_em/一般男 ทั้งหมด)

**ข้อจำกัด**: ยังผูกไฟล์บทสนทนากับแถวไม่ได้ — ตัวเลขใน section B ของเรคคอร์ด pac (`0x47a` `0x484` `0x98e`)
ไม่พบในตารางเหล่านี้ · ใช้ได้เฉพาะตัวละครที่มีชื่อเป็นแถวของตัวเอง
**ผู้รับพัสดุเควสต์ส่งของ 15 ชื่อ** (トメ · お深 · 三吉 …) ไม่มีแถวของตัวเองในตารางใดเลย และไฟล์บทต่อจุดส่ง
(`uid00160b22…2c`) มีบทของทั้ง 15 ชื่อ = NPC ตัวเดียวสลับชื่อตามเควสต์ → ไฟล์เกมไม่ได้กำหนดเพศให้ชื่อเหล่านี้
เครื่องมือ: `scripts/dump_chara_info.py` → `work/chara_info.json`
ชื่อตัวก็เป็นหลักฐานไม่ได้เช่นกัน — `uid010c13b8` โอกิคุ/โอซากิ/โอสึซุ (รูปชื่อหญิง) เป็นนักซูโม่ชาย (EN "his")

---

## 11. คลังคู่ขนาน อังกฤษ↔ญี่ปุ่น (สร้าง 1 ก.ย. 2026)

pak เดียวกันมีข้อความครบ 9 ภาษาทุกชั้น — `wdr_ja/msg` 1,688 ไฟล์ · `db.macan/ja` 126 ตาราง ·
`Localization/Game/ja/Game.locres` ทำให้จับคู่ EN↔JA ได้ **ทุกบรรทัดของทั้งเกม**

| ชั้น | วิธีจับคู่ | ผล |
|---|---|---|
| `.msg` | ไฟล์ชื่อเดียวกัน · ดัชนีแถวเดียวกัน | 54,318 แถว ตรงกันครบทั้ง 1,678 ไฟล์ · มีข้อความ ja 32,806 |
| ARMP | ตาราง + sub-table + `reARMP_rowIndex` + คอลัมน์ | 33,621 ช่อง · ครบ 100% |
| locres | namespace + key | 23,507 แถว · ครบ 100% |

ผลอยู่ที่ `extracted/parallel/{msg,db,locres}.json` · เครื่องมือ: `scripts/build_parallel.py`

**ทำไมสำคัญ**: อังกฤษของ RGG ตัดข้อมูลที่ภาษาไทยต้องใช้ทิ้ง — เพศผู้พูด · ระดับความสุภาพ ·
คำนำหน้าชื่อ · สำเนียงคันไซ ญี่ปุ่นเก็บไว้ครบ ตอนนี้แนบไปกับทุก batch แล้ว (ช่อง `ref_ja`)

---

## 12. ไฟล์ `wdr_en/` ที่ไม่ใช่ `.msg` — ตรวจแล้ว **ไม่มีข้อความให้แปล** (2 ก.ย. 2026)

คำถามเปิดข้อหนึ่งคือ `wdr_en/{shop,common,cmt,pac}` · `dispose_string.bin` · `snitch.bin`
มีข้อความเพิ่มอีกไหม — เปิดไฟล์จริงจาก pak แล้ว **ไม่มี**

ใน `wdr_en/` มีไฟล์ที่ไม่ใช่ `.msg` อยู่ **248 ไฟล์** (shop 68 · pac 168 · common 9 · cmt 1 · อีก 2 ไฟล์เดี่ยว)
ทุกไฟล์ไม่มี magic `armp` และไม่ใช่โครง `.msg` — เป็นฟอร์แมต bin ของ RGG เอง

| ไฟล์ | ขนาด en | เทียบกับ `wdr_ja` ไฟล์เดียวกัน | สตริงที่เป็นประโยค |
|---|---:|---|---:|
| `dispose_string.bin` | 51,646 | **ไบต์เท่ากันทุกไบต์** | 0 (2,175 สตริงล้วนเป็น identifier) |
| `common/ai_popup.bin` | 45,305 | **ไบต์เท่ากันทุกไบต์** | 0 |
| `snitch.bin` | 16 | ไบต์เท่ากัน | 0 |
| `pac/pac_STID_MG_*.bin` | ~10 KB | ไบต์เท่ากัน | 0 |
| `common/shop/blacksmith.bin` | 16,591 | ต่าง (ja 16,951) | 0 — สตริงที่มีคือ `dummy` |
| `shop/restaurant0000.bin` | 1,140 | ต่าง | 0 — สตริงที่มีคือ `chair` |

ไฟล์สองกลุ่มท้ายต่างกันระหว่าง en/ja จริง แต่สตริงข้างในเป็น identifier (`dummy` · `chair`)
ไม่ใช่ข้อความที่ผู้เล่นเห็น — ข้อความของร้านตีดาบอยู่ในตาราง ARMP `blacksmith_blacksmith_message`
ซึ่งอยู่ในคิวแปลอยู่แล้ว

**สรุป: คลังข้อความของเกมครบแล้วที่สามชั้นเดิม** (`.msg` + ARMP + locres) ไม่มีชั้นที่สี่

## 13. ARMP ชนิดคอลัมน์ 30/31 — reARMP ไม่รู้จัก แก้ด้วยการปะไบต์ (2 ก.ย. 2026 · sprint 9)

`reARMP_fixed.py` เขียนขึ้นสำหรับ Judgment/LAD จึงรู้จักชนิดคอลัมน์ 0–29 เท่านั้น
Ishin! มีเพิ่มอีกสองชนิดที่ตัวอ่าน **ข้ามทิ้งเงียบ ๆ**:

| ชนิด | ขนาดในแถว | ที่พบ |
|---|---:|---|
| 30 | 32 ไบต์ (บล็อกธง) | `tips.flag_one` · `tips.flag_zero` · `tips.start_condition` |
| 31 | 4 ไบต์ | `tips.end_flag` |

ตัวอ่านไม่เก็บลง JSON → ตอนประกอบกลับจึงเขียนเป็น **ศูนย์ทั้งก้อน** ทำให้ 11 ตารางเทียบไบต์ไม่ผ่าน

**วิธีแก้ที่ใช้จริง** (`scripts/armp_graft.py`): เราไม่เคยแก้คอลัมน์พวกนี้เลย (แก้แต่คอลัมน์สตริงชนิด 13)
จึงก๊อปไบต์ของคอลัมน์ชนิดที่ไม่รู้จัก **จากไฟล์ vanilla กลับเข้าแถวเดียวกันที่ shift เดิม** หลัง reARMP ประกอบเสร็จ
ก่อนก๊อปต้องตรวจว่า rows/cols/storage และ **ตาราง aux ตรงกันทุกไบต์** ไม่งั้นถือว่าโครงเปลี่ยน แล้วไม่ปะ

ผลที่วัดได้: `check_armp_rebuild.py` จาก **ผ่าน 111/122 เป็น 116/122**
`tips` ผ่านแล้ว → ปลดล็อกช่องข้อความที่แปลได้ **172 ช่อง ใน 13 batch**

ที่ยังตกอีก 6 ตาราง (`battle_ai_enemy_hact` · `battle_cmdset` · `chara_common_list_human`
· `font2_tag` · `tips_layout` · `tips_priority`) เป็นคนละอาการ — ตัวอ่านมองว่า **ทุกคอลัมน์เป็นชนิด -1**
(ไม่รู้จักโครงตารางเลย ไม่ใช่แค่ชนิดคอลัมน์) ทั้งหกตารางไม่มีช่องข้อความให้แปล จึงคงไว้ใน deny list

`scripts/build_text.py` และ `scripts/check_armp_rebuild.py` เรียก graft ให้อัตโนมัติแล้ว

## 14. ไฟล์ `.msg` ที่ RGG ไม่เคยแปลเป็นอังกฤษ — 99 ไฟล์ · 3,770 บรรทัด (2 ก.ย. 2026 · sprint 10)

**วิธีวัด**: `extracted/parallel/msg.json` (54,318 แถว จับคู่ en↔ja ด้วยไฟล์+ดัชนีบรรทัด)
นับต่อไฟล์ว่าแถวไหน `en == ja` และแถวไหนมีอักษรญี่ปุ่นจริง

| เกณฑ์ | ไฟล์ | บรรทัด |
|---|---:|---:|
| ทุกแถว `en == ja` และ ≥50% ของแถวมีอักษรญี่ปุ่น (= ไฟล์ที่ไม่เคยแปล) | **99** | **3,770** |
| มีบรรทัดญี่ปุ่นปนบางบรรทัดในไฟล์ที่แปลแล้ว | 19 | 174 |

ไฟล์ที่ใหญ่ที่สุดสามอันดับแรกคือของที่**ไม่ใช่เนื้อหาของ Ishin เลย**:

| ไฟล์ | บรรทัด | ป้ายผู้พูด | เป็นอะไร |
|---|---:|---|---|
| `uid0134003a` | 1,103 | 桐生 · ひなた · `□ステージは恥ずかしいな` | บทคุยโฮสเตสของ **คิริว** — ตัวละครที่ไม่มีในภาคนี้ |
| `uid0134003b` | 268 | 桐生 | เหมือนกัน |
| `uid0134003c` | 213 | 桐生 | เหมือนกัน · มีบรรทัด placeholder `質問会話05。` |
| `uid016f000b` | 234 | `kaiwabgm_sub_apathy_01` · `Talk_Think` | บทคุยที่ยังเป็นชื่อคิวเสียงดิบ |
| `uid00021b80` | 25 | **動作確認さん** ("คุณตรวจการทำงาน") | ไฟล์ทดสอบของทีมพัฒนา (`yes。` `no。` `疑問。`) |

**ข้อสรุป**: ไฟล์พวกนี้ตกค้างในตัวเกมโดยไม่เคยผ่านทีมแปลอังกฤษ ผู้เล่นฉบับอังกฤษจึงไม่เห็นอยู่แล้ว
→ **คัดออกจากคิวแปลเป็น DNT** (`scripts/mark_dnt.py` มีกฎ `dead_msg_files()` แล้ว)
ผลกับคิวจริง: ตัดออก **2,311 จาก 20,700 สตริงของชั้น `batch_MSG_*` (11%)**
ในจำนวนนั้นมี 6 ก้อนที่เป็น DNT 100% (MSG_066–071) เขียนไฟล์ done แบบ copy ตรงแล้ว

⚠ ที่คัดออกคือ **ไฟล์ที่ไม่เคยแปลทั้งไฟล์** เท่านั้น — บรรทัดญี่ปุ่นที่ปนอยู่ในไฟล์ที่แปลแล้ว (174 บรรทัด)
ยังอยู่ในคิวตามเดิม เพราะบรรทัดอังกฤษรอบ ๆ มันต้องแปล

### 14.1 บทตกค้างระดับ **บรรทัด** — เจอเพิ่ม 3 ก.ย. 2026

กฎ `dead_msg_files()` ตัดได้เฉพาะไฟล์ที่ **ไม่เคยแปลทั้งไฟล์** แต่ยังมีอีกกรณีที่หลุด:
ไฟล์ที่มีทั้งบทจริงของ Ishin **และ** บทตกค้างจากเกมอื่นปนกันอยู่ในไฟล์เดียว

ตัวอย่างที่นักแปลก้อน MSG_023 จับได้: `uid01340035` มีบทข้อความทำอาหารของ Ishin (`〜が出来た`)
อยู่ติดกับบทเดินเที่ยวซื้อของของ **桐生 (คิริว)** กับ **ひなた (ฮินาตะ)** ซึ่งเป็นตัวละครนอกภาค
ไฟล์จึงไม่เข้าเกณฑ์ "ไม่เคยแปลทั้งไฟล์" และหลุดเข้าคิวแปลไป 22 บรรทัด

**กฎที่เพิ่ม** (`foreign_msg_files()` + `foreign_keys` ใน `scripts/mark_dnt.py`):
ไฟล์ที่เอ่ยชื่อ 桐生 = ไฟล์ที่มีบทของเกมอื่น → **คีย์ที่โผล่เฉพาะในไฟล์กลุ่มนี้เท่านั้น** เป็น DNT

⚠ ต้องตัดเป็นราย **คีย์** ไม่ใช่รายไฟล์ — คำอุทานสั้น ๆ อย่าง 「ああ」「どういうことだ？」
ใช้ร่วมกับฉากจริงของ Ishin ด้วย ถ้าตัดทั้งไฟล์จะเสียบทจริงไป (ตรวจพบตอนลองกฎแบบรายไฟล์กับก้อน MSG_016)

ผล: DNT ของชั้น `.msg` เพิ่มจาก 2,327 เป็น **2,349 สตริง** · บรรทัดทำอาหารของ Ishin ไม่ถูกตัดสักบรรทัด

## 15. เกม crash ที่เควสต์ร้านอุด้ง = ข้อความหน้าต่างสอนเล่นยาวเกิน buffer 1,024 ไบต์ (15 ก.ย. 2026)

**อาการ**: ผู้ใช้รายงาน "เกม crash ที่ substory ร้านขายอุด้ง" (test_22) — ครั้งแรกที่มีใครเข้าฉากนี้ตั้งแต่แปล label/บรรทัดครบ

**ที่หาหลักฐาน** (เกมไม่เขียน log เอง — `%LOCALAPPDATA%\LikeaDragonIshin\Saved\Logs` มีแต่ NGX · `CrashPadDb` ว่าง):
- Event Log Application: Id 1000 (Application Error) + Id 1001 (WER) — `LikeaDragonIshin-Win64-Shipping.exe` 4.27.2.0
  exception `0xc0000409` · exception data `0x2` = **FAST_FAIL_STACK_COOKIE_CHECK_FAILURE** (buffer บน stack ล้น) · fault offset `exe+0x444318d`
- **minidump**: `%LOCALAPPDATA%\CrashDumps\LikeaDragonIshin-Win64-Shipping.exe.<pid>.dmp` (97.6 MB · Windows LocalDumps
  เขียนให้ทันทีที่ crash) · แกะด้วย python ตรง ๆ: header `MDMP` → stream directory → ExceptionStream (6) ให้ thread id +
  CONTEXT (Rsp ที่ +152 · Rip ที่ +248) → ThreadListStream (3) ให้ช่วง stack ของเธรดนั้น → ModuleListStream (4) ให้ฐานของ exe
  → สแกน stack หา pointer เข้า exe (return address) และสตริง UTF-8 ไทย

**ที่เห็นบน stack ของเธรดที่พัง** (rsp = `0xf7e8a0` · ช่วง stack 0x1760 ไบต์):
```
rsp+0x070 .. 0x470   1,024 ไบต์แรกของบรรทัด uid010c16a4#001 (ไทยเต็ม 1,098 ไบต์) ตรงไบต์ต่อไบต์ — ตัดที่ 1,024 พอดี
rsp+0x470            3c 00 00 2a fe 2e 00 00   <- ช่อง stack cookie: 3 ไบต์ล่างถูกเขียนทับ (ค่าบน 2a fe 2e = เศษ cookie)
rsp+0x480            pointer heap · rsp+0x488  return address exe+0xf7a269
```
→ โค้ดหน้าต่างสอนเล่น (`<kf:N>` = หน้าของหน้าต่าง) คัดลอกข้อความทั้งบรรทัดลง `char[1024]` บน stack แบบจำกัดขนาด
แล้วเขียนต่อท้ายตามความยาวจริงของสตริง → cookie พัง → `__fastfail(2)` · ไม่ใช่ฟอร์แมตไฟล์พัง (ด่าน roundtrip/translated ผ่านทุกด่านจริง)

**ทำไมภาษาทางการไม่เคยชน** — บรรทัดเดียวกันใน pak ต้นฉบับ: cn 332 · de 513 · en 493 · es 530 · fr 520 · it 572 · ja 434 · ko 423 · tw 338 ไบต์
ไทย 3 ไบต์/ตัวอักษร + คำแปลขยายความ → 1,098 · ทั้งคลังมีบรรทัด `.msg` ไทยเกิน 1,024 อยู่ **3 บรรทัด**
(อีกสองคือประกาศ SHARE ของ PlayStation 4 `uid0102220f#000` 1,039 · `uid01160726#013` 1,065 ที่ EN ก็ทิ้งเป็นญี่ปุ่น) · บรรทัดถัดไป 898

**แก้**: `scripts/fix_msg_byte_limit.py` ย่อทั้งสามให้ 854 / 846 / 880 ไบต์ (ยืนยันจากไฟล์ใน pak test_23) · ด่าน `check_byte_limits.py` เพิ่มกฎ **ทุกบรรทัด `.msg` ≤ 1,000 ไบต์**
(เผื่อ NUL/ไบต์ที่โค้ดเขียนต่อท้าย) · ยืนยันแล้วว่าไบต์ในไฟล์ที่บิลด์ = ไบต์ของคำแปลใน master (198/198 บรรทัดของ uid000c140e)

**ที่ยังไม่รู้** (ห้ามสรุปโดยไม่มีหลักฐานจากจอ): ตาราง `tips.bin` มี 18 แถวไทยเกิน 1,024 ไบต์ (สูงสุด 1,471 "Raising Your Troopers")
และ locres `rule_*` (กติกามินิเกม) 7 สตริง (สูงสุด 1,539 `rule_chinchiro/page06/word`) — เนื้อหาชนิดเดียวกับหน้าต่างสอนเล่น
(แถวทิปส์ "Udon Shop" คอลัมน์ 6 ก็ขึ้นต้น `<kf:10>` เหมือนบรรทัดที่ crash) แต่ยังไม่พิสูจน์ว่าผ่าน buffer ตัวเดียวกัน
→ ทดสอบเปิดทิปส์ "พื้นฐานการต่อสู้: ลักษณะศัตรู" (1,423 ไบต์) จากเมนูทิปส์ · ถ้า crash ให้ย่อทั้ง 18 แถว + 7 สตริง แล้วเพิ่มกฎในด่าน

สิ่งที่ตัดออกจากผู้ต้องสงสัยได้ด้วยหลักฐานเดียวกัน: ชั้น pac (`pac_STID_ST_UDONYA` ไม่ถูกแก้ · สตริง pac ยาวสุด 307 ไบต์) ·
label ของฉาก (ทั้ง 16 ตัวแปลในทุกภาษาทางการ ยกเว้น `Player` ที่เหมือนกันทุกภาษาแต่ก็ถูกแทนทั้งเกมมาตั้งแต่ v1.5 โดยไม่ crash)
