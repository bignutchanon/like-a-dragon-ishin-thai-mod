# บรีฟทีมเก็บข้อมูลเนื้อหาในเกม (Data Collector Team) — Judgment / JETH

โปรเจกต์: ม็อดแปลไทยเกม **Judgment** (PC 2022, Dragon Engine, codename `judge`)
ที่ `D:/Projects/judgment-thai` · ทีมนี้ทำ **Phase 1 = เตรียมข้อมูลให้นักแปล** ก่อนเปิด sprint แปล

เนื้อเรื่องย่อ: ทาคายูกิ ยากามิ อดีตทนายความที่ผันตัวเป็นนักสืบเอกชนในคามุโรโจ
สืบคดีฆาตกรรมต่อเนื่องที่เหยื่อถูกควักลูกตา — เชื่อมโยงตระกูลมัตสึกาเนะ (ยากูซ่า) ตำรวจ
อัยการ และบริษัทยา

## กติกาเหล็ก (ผิดข้อไหนถือว่างานใช้ไม่ได้)

1. **ห้ามเปิดเกม** — การทดสอบในเกมเป็นหน้าที่ผู้ใช้เท่านั้น
2. **โปรเจกต์อื่นอ่านอย่างเดียว** (`D:/Projects/yakuza-*`) — ห้ามเขียน/แก้ไฟล์นอก
   `D:/Projects/judgment-thai`
3. **ห้าม spawn subagent ต่อ** — ทำงานของตัวเองให้จบในเซสชันเดียว
4. เขียนไฟล์ด้วย **UTF-8** เสมอ · ห้ามส่งข้อความไทยผ่าน CLI argument (console เป็น cp1252)
   — ถ้าจะเขียนไฟล์ผ่านสคริปต์ ให้ใช้ `io.open(..., encoding="utf-8")` และ
   `sys.stdout.reconfigure(encoding="utf-8")`
5. **ไฟล์ใหญ่ห้ามเขียนใน Write เดียว** — แตกเป็น `.part1` `.part2` แล้วบอก lead ให้ merge
   (แต่ละ part ไม่ควรเกิน ~40KB)
6. **ห้ามแตะ** `translations/master_th.json`, `translations/slotmap.json`,
   `docs/research.md`, `HANDOFF.md`, `CLAUDE.md` — เขียนเฉพาะไฟล์ที่ระบุในภารกิจของตัวเอง
7. **ทุกข้อเท็จจริงต้องมีที่มา** — ระบุว่ามาจากไฟล์เกม (ชื่อไฟล์/หมวด) หรือจากเว็บ (URL)
   สิ่งที่ยังไม่ยืนยันให้ใส่เครื่องหมาย **⏳** ไว้ ห้ามเดาแล้วเขียนเหมือนเป็นข้อเท็จจริง

## แหล่งข้อมูลที่ต้องใช้ (เรียงตามความน่าเชื่อถือ)

### 1. ไฟล์เกมจริง — น่าเชื่อถือที่สุด (ขัดกับ wiki เมื่อไร ให้เชื่อไฟล์เกม)

- `docs/reference/judge_extract_facts.md` — สรุป + **รายชื่อผู้พูดครบ 473 ชื่อ** (JA + EN)
- `extracted/facts/*.json` — ข้อมูลดิบรายหมวด (อ่านเฉพาะหมวดที่ต้องใช้ ไฟล์ใหญ่):

  | ไฟล์ | เนื้อหา | จำนวน |
  |---|---|---|
  | `speakers.json` | ชื่อผู้พูด (key ญี่ปุ่น + ชื่อ EN บนจอ) | 473 |
  | `chapters.json` | ชื่อบท 13 บท | 13 |
  | `missions.json` | คดีหลัก/Side Case/งานย่อย + คำบรรยาย | 550 |
  | `friends.json` | ระบบเพื่อน — ชื่อ + คำอธิบายตัวละคร | 54 |
  | `evidence.json` | ประวัติบุคคล/หลักฐาน (สปอยล์เต็ม) | 103 |
  | `scenario_summary.json` | สรุปเนื้อเรื่องย่อรายตอนที่เกมเขียนเอง | 62 |
  | `items.json` | ไอเทม/แฟ้มคดี/ของสะสม | 1,071 |
  | `skills.json` | สกิล | 126 |
  | `complete.json` / `complete_group.json` | รายการ completion (ชี้ว่ามี side content อะไรบ้าง) | 499 / 34 |
  | `places.json` | สถานที่ + คำบรรยาย | 182 |
  | `shops.json` `help.json` `manual.json` `trophy.json` `talk_select.json` `popup_names.json` `ui_text.json` | ระบบ/ร้าน/คู่มือ/ถ้วยรางวัล | — |

- บทพูดเต็มทั้งเกมอยู่ที่ `extracted/db_en/en/talk.bin.json` (19,055 บรรทัด) และ
  `sound_auth.bin.json` (บทคัตซีน) — **ใหญ่มาก ห้าม Read ทั้งไฟล์** ใช้ `Grep` หาเฉพาะที่ต้องการ
- ⚠ กับดัก: db ของ Dragon Engine มีข้อความตกค้างจากเกมภาคอื่น (เช่น `title_root.bin` มีคำว่า
  "Majima Saga" ซึ่งเป็นของ Kiwami 2 ไม่ใช่ Judgment) — เจอชื่อแปลก ๆ ให้ยืนยันซ้ำก่อนใช้

### 2. โปรเจกต์พี่น้อง (อ่านอย่างเดียว) — สำหรับคำล็อกและรูปแบบไฟล์

- ลำดับความสำคัญของ glossary: **K3 > Gaiden > Y8 > Y7 > Pirate > K2R** (ใหม่กว่าชนะ)
- `D:/Projects/yakuza-kiwami-3/translations/` — `glossary.md`, `characters_main.json`,
  `characters_side.json`, `PRONOUN_MATRIX.md` (**รูปแบบมาตรฐานที่ต้องทำตาม**)
- `D:/Projects/yakuza-kiwami-3/docs/` — `research_characters_k3.md`,
  `story_context_k3.part1.md`, `side_content_context_k3.md` (ตัวอย่างงานที่ดี)
- `D:/Projects/yakuza-kiwami-3/docs/reference/` — `glossary_gaiden.md`, `glossary_y8.md`,
  `glossary_y7.md`, `glossary_pirate.md`, `glossary_k2.md`, `TRANSLATOR_BRIEF_y8.md`,
  `PRONOUN_MATRIX_*.md`
- คำที่ล็อกแล้วสำหรับภาคนี้: **Masaharu Kaito = มาซาฮารุ ไคโตะ** (จาก glossary_gaiden)
- ⚠ Issei Hoshino (ทนายใน Judgment) **คนละคน** กับ Ryuhei Hoshino ของ Y7/Y8 — เคยสับสนมาแล้ว

### 2b. คลังเนื้อเรื่องของจักรวาล RGG ที่ทีมนี้แปลมาแล้ว (อ่านอย่างเดียว — สำคัญ)

Judgment ใช้เมือง **คามุโรโจ** เดียวกับซีรีส์ Yakuza และอ้างอิงองค์ประกอบร่วมเพียบ (ตระกูลโทโจ,
ร้าน/สถานที่ประจำเมือง, มินิเกมชุดเดิม, ศัพท์ยากูซ่า) — ทีมแปลชุดนี้เคยแปลภาคเหล่านั้นมาแล้ว
**คำที่ล็อกไว้แล้วต้องใช้ต่อ ห้ามตั้งใหม่**:

| ภาค | สรุปเนื้อเรื่อง | glossary / ตัวละคร |
|---|---|---|
| Kiwami 3 (ล่าสุด) | `D:/Projects/yakuza-kiwami-3/docs/story_context_k3.part1.md` + `.part2.md` | `translations/glossary.md`, `characters_main.json`, `characters_side.json` |
| Gaiden | `D:/Projects/yakuza-gaiden/docs/story_context_gaiden.md` | `docs/reference/glossary_gaiden.md`, `characters_gaiden_main.json` (ใน K3) |
| Yakuza 8 | `D:/Projects/yakuza-kiwami-3/docs/reference/story_context_y8.md` | `glossary_y8.md`, `characters_y8_main.json` |
| Yakuza 7 | `D:/Projects/yakuza-kiwami-3/docs/reference/story_context_y7.md` | `glossary_y7.md`, `characters_y7_main.json` |
| Yakuza 6 | `D:/Projects/yakuza-6-thai/docs/story_context_y6.md` + `side_content_context_y6.md` | `D:/Projects/yakuza-6-thai/translations/glossary_y6.md`, `characters_main.json` |
| Yakuza 4 | `D:/Projects/yakuza-kiwami-3/docs/reference/story_context_y4.md` | `db_y4.json` |
| Kiwami 2 | `D:/Projects/yakuza-kiwami-2-mod/docs/story_context_k2.md` + `side_content_context_k2.md` | `glossary_k2.md`, `characters_k2_main.json`/`_side.json` |
| Pirate Yakuza | `D:/Projects/pirate-yakuza-hawaii-thai` | `glossary_pirate.md`, `characters_pirate_main.json` |

วิธีใช้: ก่อนตั้งชื่อไทยให้อะไรก็ตาม (ตัวละคร สถานที่ ร้าน มินิเกม ศัพท์ยากูซ่า/กฎหมาย)
ให้ `Grep` หาคำนั้นในไฟล์ glossary ทั้งชุดก่อน — เจอแล้วใช้คำเดิม, ไม่เจอค่อยเสนอใหม่
ตัวอย่างของที่ต้องตรงกันข้ามภาค: คามุโรโจ · ตระกูลโทโจ · ถนนเทนไคจิ · ร้านสะดวกซื้อ Poppo ·
ศูนย์ฝึกตีเบสบอล · ศูนย์เกม SEGA · คลับโฮสเตส · ศัพท์ยากูซ่า (อานิกิ/คุมิโจ/ตระกูล/สาขา)

### 3. เว็บ (wiki/บทสรุป) — ใช้เสริม ไม่ใช่แหล่งหลัก

- เว็บส่วนใหญ่บล็อก WebFetch ตรง ๆ (403) → ดึงผ่าน `https://r.jina.ai/<URL เต็ม>` แทน
- แหล่งที่ใช้ได้: `judgment.fandom.com`, `yakuza.fandom.com`, IGN/Gamefaqs walkthrough
- **wiki ผิดบ่อย** (ชื่อบท สังกัด บทบาท) — ทุกครั้งที่ wiki ขัดกับไฟล์เกม ให้เชื่อไฟล์เกม
  แล้ว **จดความขัดแย้งไว้ในรายงาน** ให้ lead เห็น

## หลักการตั้งชื่อไทย (สืบทอดจาก K3)

- ทับศัพท์ตามเสียงญี่ปุ่นมาตรฐานของสายงานนี้: `g` กลางคำ → ก · `-ei` → เ-ย์ ·
  `ki` ท้ายชื่อ → กิ · `zu` → ซึ · ชื่อฝรั่ง/จีนทับศัพท์ตามเสียงต้นทาง
- ตัวละครที่เคยมีคำล็อกในภาคก่อน **ต้องใช้คำเดิม** (เช็ค glossary ตามลำดับความสำคัญข้างบน)
- เสนอชื่อใหม่ให้ใส่ฟิลด์ `reason` เสมอว่าทำไมสะกดแบบนั้น
- ยังไม่ต้องตัดสินเด็ดขาด — ของที่ยังไม่ชัวร์ให้ทำเป็น `name_th_proposal` + ⏳ ให้ lead ตัดสิน

## รูปแบบผลลัพธ์

- ภาษาในเอกสาร = **ไทย** (ยกเว้นชื่อฟิลด์ JSON, ชื่อไฟล์, ศัพท์เทคนิค)
- JSON ต้อง `json.load` ผ่าน (ตรวจก่อนส่งงานเสมอ)
- จบงานให้รายงานกลับ: ไฟล์ที่เขียน · จำนวนรายการ · ข้อขัดแย้งที่เจอ · สิ่งที่ยังค้าง (⏳)
