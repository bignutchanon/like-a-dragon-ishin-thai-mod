# หลักฐานเพศผู้พูด — Lost Judgment

> สร้างด้วย `python scripts/harvest_gender_evidence.py --write` ·
> ข้อมูลดิบ: `extracted/facts/gender_evidence.json`

**กติกาใช้งาน (บังคับ):** `unknown` หรือ `conflict` = **ห้ามใส่ ครับ/ค่ะ และห้ามใช้ ผม/ดิฉัน**
ให้แปลกลางเพศตาม PRONOUN_MATRIX §0 (ใช้ "ตัวเอง" แทนคำแทนตัว หรือเลี่ยงสรรพนามทั้งประโยค)

| ตัวชี้วัด | ค่า |
|---|---|
| ผู้พูดที่มีชื่อ | 1222 |
| พิสูจน์เพศได้ | 946 |
| ยังพิสูจน์ไม่ได้ (ต้องแปลกลาง) | 276 |
| บรรทัดที่ผู้พูดรู้เพศแล้ว | 51,729 / 53,484 |

## ผู้พูดที่พิสูจน์เพศได้ (เรียงตามจำนวนบรรทัด)

| ผู้พูด | เพศ | ความมั่นใจ | ที่มา | พบใน | บรรทัด | หลักฐาน |
|---|---|---|---|---|---|---|
| Yagami | male | high | voicer | talk.bin | 16772 | sound_voicer.bin: sex=1 |
| Kaito | male | high | voicer | talk.bin | 4129 | sound_voicer.bin: sex=1 |
| Amasawa | female | high | voicer | talk.bin | 1832 | sound_voicer.bin: sex=2 |
| Tsukumo | male | high | voicer | talk.bin | 1207 | sound_voicer.bin: sex=1 |
| Saori | female | high | voicer | talk.bin | 1169 | sound_voicer.bin: sex=2 |
| Kuwana | male | high | voicer | sound_auth.bin(talker) | 824 | sound_voicer.bin: sex=1 |
| Kyoko | female | high | voicer | talk.bin | 783 | sound_voicer.bin: sex=2 |
| Jun | male | high | voicer | talk.bin | 766 | sound_voicer.bin: sex=1 |
| Sugiura | male | high | voicer | talk.bin | 706 | sound_voicer.bin: sex=1 |
| Hoshino | male | high | voicer | sound_auth.bin(talker) | 553 | sound_voicer.bin: sex=1 |
| Okitegawa | male | high | voice_cue | talk.bin | 550 | sound_auth.bin: คิวเสียง speech_drama_m21_020_doumu -> sound_voicer sex (ชาย 143 : หญิง 0) |
| Emily | female | high | voice_cue | talk.bin | 545 | sound_auth.bin: คิวเสียง speech_side_m96_0020_emiri -> sound_voicer sex (ชาย 0 : หญิง 123) |
| Minato | female | high | voicer | talk.bin | 537 | sound_voicer.bin: sex=2 |
| Sawa | female | high | voicer | sound_auth.bin(talker) | 494 | sound_voicer.bin: sex=2 |
| Nishizono | female | high | voice_cue | talk.bin | 458 | sound_auth.bin: คิวเสียง speech_m02_00840_sayaka -> sound_voicer sex (ชาย 0 : หญิง 102) ·  |
| yagami | male | high | voicer | sound_auth.bin | 456 | sound_voicer.bin: sex=1 |
| Watanabe | male | high | voice_cue | talk.bin | 426 | sound_auth.bin: คิวเสียง speech_jh80590_wanatabe -> sound_voicer sex (ชาย 199 : หญิง 0) ·  |
| Genda | male | high | voicer | sound_auth.bin(talker) | 417 | sound_voicer.bin: sex=1 |
| Tsukino | female | high | voicer | talk.bin | 412 | sound_voicer.bin: sex=2 |
| Higashi | male | high | voicer | talk.bin | 390 | sound_voicer.bin: sex=1 |
| Shirakaba | male | high | voicer | sound_auth.bin(talker) | 390 | sound_voicer.bin: sex=1 |
| Ehara | male | high | voicer | sound_auth.bin(talker) | 385 | sound_voicer.bin: sex=1 |
| Mamiya | female | high | voice_cue | sound_auth.bin(talker) | 383 | sound_auth.bin: คิวเสียง speech_m05_01800_old_mamiya -> sound_voicer sex (ชาย 0 : หญิง 227 |
| Itokura | female | high | voicer | talk.bin | 380 | sound_voicer.bin: sex=2 |
| Todoroki | male | high | voicer | talk.bin | 365 | sound_voicer.bin: sex=1 |
| Sadamoto | male | high | voice_cue | sound_auth.bin(talker) | 348 | sound_auth.bin: คิวเสียง speech_dlc_m01_00800_kyoya -> sound_voicer sex (ชาย 171 : หญิง 0) |
| Okuda | male | high | voicer | sound_auth.bin(talker) | 345 | sound_voicer.bin: sex=1 |
| Igarashi | male | high | voicer | talk.bin | 342 | sound_voicer.bin: sex=1 |
| Mikiko | female | high | voicer | sound_auth.bin(talker) | 340 | sound_voicer.bin: sex=2 |
| Akutsu | male | high | voicer | sound_auth.bin(talker) | 276 | sound_voicer.bin: sex=1 |
| Kusumoto | female | high | voicer | sound_auth.bin(talker) | 271 | sound_voicer.bin: sex=2 |
| Soma | male | high | voicer | sound_auth.bin(talker) | 266 | sound_voicer.bin: sex=1 |
| Seyama | male | high | voicer | talk.bin | 219 | sound_voicer.bin: sex=1 |
| Tesso | male | high | voice_cue | sound_auth.bin(talker) | 202 | sound_auth.bin: คิวเสียง speech_m04_03300_tessou -> sound_voicer sex (ชาย 96 : หญิง 0) · v |
| Matsui | male | high | voicer | sound_auth.bin(talker) | 201 | sound_voicer.bin: sex=1 |
| kaito | male | high | voicer | sound_auth.bin | 193 | sound_voicer.bin: sex=1 |
| Sakura | male | medium-conflict | voice_cue(majority 33:9) | talk.bin | 186 | sound_auth.bin: คิวเสียง speech_drama_m23_060_dento -> sound_voicer sex (ชาย 33 : หญิง 9)  |
| Oshikiri | male | high | voice_cue | talk.bin | 184 | sound_auth.bin: คิวเสียง speech_drama_m31_060_kenya -> sound_voicer sex (ชาย 76 : หญิง 0)  |
| Senda | male | high | voicer | sound_auth.bin(talker) | 182 | sound_voicer.bin: sex=1 |
| Kurumazaki | male | high | voicer | talk.bin | 176 | sound_voicer.bin: sex=1 |
| Takanashi | female | high | voicer | talk.bin | 175 | sound_voicer.bin: sex=2 |
| Toribe | female | high | voicer | talk.bin | 172 | sound_voicer.bin: sex=2 |
| Suou | male | high | voicer | talk.bin | 171 | sound_voicer.bin: sex=1 |
| Kenmochi | male | high | voicer | sound_auth.bin(talker) | 167 | sound_voicer.bin: sex=1 |
| Kento | male | high | voicer | talk.bin | 164 | sound_voicer.bin: sex=1 |
| Takano | male | high | voicer | sound_auth.bin(talker) | 163 | sound_voicer.bin: sex=1 |
| Haruko | female | high | voicer | talk.bin | 152 | sound_voicer.bin: sex=2 |
| Dealer | male | medium | title | talk.bin | 148 | Unfortunately, the dealer has blackjack as well. Better luck next time, sir. |
| Bando | male | high | voice_cue | sound_auth.bin(talker) | 145 | sound_auth.bin: คิวเสียง speech_m11_00600_bandou -> sound_voicer sex (ชาย 44 : หญิง 0) · v |
| Okazaki | male | high | dossier | talk.bin | 143 | evidence.bin — Aruto Okazaki: An author and member of Kazuto Jumonji. He's also the one wh |
| Sakuma | male | high | voicer | talk.bin | 143 | sound_voicer.bin: sex=1 |
| Kosuke | male | high | voicer | talk.bin | 141 | sound_voicer.bin: sex=1 |
| Ayaha | female | high | voicer | talk.bin | 134 | sound_voicer.bin: sex=2 |
| Rugged Thug | male | high | voice_cue | talk.bin | 134 | sound_auth.bin: คิวเสียง speech_ja20130_ikatsui_hangure -> sound_voicer sex (ชาย 64 : หญิง |
| Mari | female | high | voicer | talk.bin | 132 | sound_voicer.bin: sex=2 |
| Hanasaki | male | high | voicer | talk.bin | 127 | sound_voicer.bin: sex=1 |
| Asama | male | high | voicer | talk.bin | 123 | sound_voicer.bin: sex=1 |
| Akane | female | high | voicer | sound_auth.bin(talker) | 119 | sound_voicer.bin: sex=2 |
| Ebisu | male | high | pronoun | talk.bin | 118 | He's a reseller who went to Ebisu Pawn because he heard on the web that they were selling  |
| Siren Owner | male | high | voice_cue | sound_auth.bin(talker) | 117 | sound_auth.bin: คิวเสียง speech_m08_02300_seiren -> sound_voicer sex (ชาย 57 : หญิง 0) · v |
| sugiura | male | high | voicer | sound_auth.bin | 116 | sound_voicer.bin: sex=1 |
| Takamori | male | high | voicer | talk.bin | 115 | sound_voicer.bin: sex=1 |
| Tashiro | male | high | voicer | talk.bin | 114 | sound_voicer.bin: sex=1 |
| Miu | female | high | voicer | talk.bin | 106 | sound_voicer.bin: sex=2 |
| Mafuyu | female | high | voicer | sound_auth.bin(talker) | 106 | sound_voicer.bin: sex=2 |
| Koda | female | high | voice_cue | sound_auth.bin(talker) | 104 | sound_auth.bin: คิวเสียง speech_m02_01200_kouda -> sound_voicer sex (ชาย 0 : หญิง 18) · vo |
| Norizuki | female | high | voice_cue | talk.bin | 103 | sound_auth.bin: คิวเสียง speech_drama_m04_400_noriduki -> sound_voicer sex (ชาย 0 : หญิง 3 |
| tsukumo | male | high | voicer | sound_auth.bin | 102 | sound_voicer.bin: sex=1 |
| Suspicious Man | male | high | dossier | talk.bin | 100 | evidence.bin — Suspicious Man: Seven years ago, this man snuck into Kitan Amasawa's home a |
| Iyama | male | high | dossier | talk.bin | 99 | evidence.bin — Iyama: An elderly man from Kamurocho who crafts and sells extracts, a myste |
| Koga | male | high | voicer | talk.bin | 98 | sound_voicer.bin: sex=1 |
| Akuta | female | high | voicer | talk.bin | 95 | sound_voicer.bin: sex=2 |
| Mikimoto | male | high | voicer | talk.bin | 95 | sound_voicer.bin: sex=1 |
| saori | female | high | voicer | sound_auth.bin | 95 | sound_voicer.bin: sex=2 |
| Chiyoda | male | high | voicer | talk.bin | 94 | sound_voicer.bin: sex=1 |
| Keiko | female | high | voicer | talk.bin | 93 | sound_voicer.bin: sex=2 |
| Woman Who Dropped Something | female | medium | name | talk.bin | 90 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Woman Who Dropped Something |
| Yosuke | male | high | voicer | talk.bin | 89 | sound_voicer.bin: sex=1 |
| Kalashnikov | male | high | dossier | talk.bin | 87 | evidence.bin — Borscht Kalashnikov: A Russian ninja who opened a dojo in Kamurocho. Former |
| Sanbonmatsu | male | high | dossier | talk.bin | 87 | evidence.bin — Genya Sanbonmatsu: A second-year student and president of the Seiryo High e |
| Rina | female | high | voicer | talk.bin | 85 | sound_voicer.bin: sex=2 |
| Minami | female | high | voice_cue | talk.bin | 83 | sound_auth.bin: คิวเสียง speech_drama_m04_400_maria -> sound_voicer sex (ชาย 0 : หญิง 6) · |
| Ghost | male | high | voicer | talk.bin | 80 | sound_voicer.bin: sex=1 |
| Man Who Dropped Something | male | medium | name | talk.bin | 80 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Man Who Dropped Something |
| Mori | male | high | voicer | talk.bin | 79 | sound_voicer.bin: sex=1 |
| Onidake | male | high | voice_cue | talk.bin | 78 | sound_auth.bin: คิวเสียง speech_drama_m31_400_onitake -> sound_voicer sex (ชาย 34 : หญิง 0 |
| Yabuki | male | medium-conflict | majority(11:1) | talk.bin | 77 | Vice president of the Supernatural Research Club. Currently worried that Yabuki, the SRC p |
| Jo Masuda | male | high | voice_cue | talk.bin | 73 | sound_auth.bin: คิวเสียง speech_m06_01100_tender_master -> sound_voicer sex (ชาย 32 : หญิง |
| Okizaki | male | high | dossier | talk.bin | 72 | evidence.bin — Takeshi Okizaki: My client and a middle manager for God-Tier Games. In a ti |
| Ryan | male | high | voicer | talk.bin | 71 | sound_voicer.bin: sex=1 |
| Dan | male | high | voice_cue | talk.bin | 70 | sound_auth.bin: คิวเสียง speech_drama_m13_430_ghost -> sound_voicer sex (ชาย 17 : หญิง 0)  |
| Shikishima | male | high | voicer | talk.bin | 69 | sound_voicer.bin: sex=1 |
| Sakaki | male | high | voicer | sound_auth.bin(talker) | 69 | sound_voicer.bin: sex=1 |
| Sakurazaka | male | high | dossier | talk.bin | 68 | evidence.bin — Sakurazaka: Owner of the business which is being burglarized. He runs a con |
| Fudo | male | high | voice_cue | sound_auth.bin(talker) | 68 | sound_auth.bin: คิวเสียง speech_drama_m34_570_fudou -> sound_voicer sex (ชาย 40 : หญิง 0)  |
| Hayakawa | female | high | voicer | talk.bin | 66 | sound_voicer.bin: sex=2 |
| Kawasaki | male | medium-conflict | majority(3:1) | talk.bin | 63 | Oh, hey, Mr.— I mean, your name is Kawasaki-san, right? |
| Shinonome | male | high | dossier | talk.bin | 63 | evidence.bin — Ryuichi Shinonome: A game developer and director for God-Tier Games. Accord |
| Sanada | male | medium | pronoun | talk.bin | 62 | It seems Sanada-san did notice something suspicious, but he's too hesitant to say anything |
| Kinugawa | male | high | dossier | talk.bin | 62 | evidence.bin — Kinugawa: Game producer working for the publisher Babylon. Has contracted G |
| dlc_m02_kaito | male | high | voicer | sound_auth.bin | 60 | sound_voicer.bin: sex=1 |
| Toki | male | high | dossier | talk.bin | 59 | evidence.bin — Machio Toki: A first-year student and member of the Seiryo High eSports Clu |
| High Court Judge | male | high | voice_cue | sound_auth.bin(talker) | 59 | sound_auth.bin: คิวเสียง speech_m11_00600_kousai_saibancho -> sound_voicer sex (ชาย 45 : ห |
| Shop Owner | male | high | voice_cue | talk.bin | 58 | sound_auth.bin: คิวเสียง speech_dlc_g02_015_tencho -> sound_voicer sex (ชาย 24 : หญิง 0) · |
| Irie | male | high | voicer | sound_auth.bin(talker) | 58 | sound_voicer.bin: sex=1 |
| Nishio | male | high | voicer | sound_auth.bin(talker) | 58 | sound_voicer.bin: sex=1 |
| Momoko | female | high | voicer | sound_auth.bin(talker) | 54 | sound_voicer.bin: sex=2 |
| Hikawa | male | high | dossier | talk.bin | 53 | evidence.bin — Kanto Hikawa: Former president of the Seiryo High photography club. Third y |
| Kasai | male | high | voicer | talk.bin | 51 | sound_voicer.bin: sex=1 |
| Thug in Car | male | high | voice_cue | sound_auth.bin(talker) | 50 | sound_auth.bin: คิวเสียง speech_m10_03200_syatyu_hangure -> sound_voicer sex (ชาย 11 : หญิ |
| Kiba | male | high | dossier | talk.bin | 49 | evidence.bin — Daichi Kiba: Owner of a multi-tenant building in Kamurocho. Despite the pre |
| genda | male | high | voicer | sound_auth.bin | 48 | sound_voicer.bin: sex=1 |
| Joe | male | medium | role | talk.bin | 47 | King Joe |
| Nana | female | high | voicer | talk.bin | 45 | sound_voicer.bin: sex=2 |
| hoshino | male | high | voicer | sound_auth.bin | 45 | sound_voicer.bin: sex=1 |
| Komekado | male | high | voicer | talk.bin | 44 | sound_voicer.bin: sex=1 |
| Haruna | male | high | voicer | talk.bin | 44 | sound_voicer.bin: sex=1 |
| dlc_m02_jun | male | high | voicer | sound_auth.bin | 44 | sound_voicer.bin: sex=1 |
| Senpai Leader | male | high | voicer | sound_auth.bin(talker) | 43 | sound_voicer.bin: sex=1 |
| Otani | male | medium | role | talk.bin | 42 | Otani! Look into my eyes! Do I look like a guy that would cheat!? |
| Naisu Daisu | female | medium | role | talk.bin | 42 | Didn't know you two were acquainted. Funny how a lady named "Naisu Daisu" ends up working  |
| Cleaning Lady | female | high | voice_cue | sound_auth.bin(talker) | 42 | sound_auth.bin: คิวเสียง speech_dlc_m02_01430_female_clean -> sound_voicer sex (ชาย 0 : หญ |
| Young Lady | female | high | name+role | talk.bin | 41 | Does scamming a young lady ring any bells for you? |
| Suou's Mother | female | high | voice_cue | talk.bin | 41 | sound_auth.bin: คิวเสียง speech_drama_m14_470_suou_mother -> sound_voicer sex (ชาย 0 : หญิ |
| Sakurai | male | high | voicer | sound_auth.bin(talker) | 41 | sound_voicer.bin: sex=1 |
| Shady Bar Owner | male | high | voice_cue | sound_auth.bin(talker) | 41 | sound_auth.bin: คิวเสียง speech_m01_00900_bottakuri_master -> sound_voicer sex (ชาย 21 : ห |
| Megu | female | high | voicer | sound_auth.bin(talker) | 41 | sound_voicer.bin: sex=2 |
| dlc_m03_kaito | male | high | voicer | sound_auth.bin | 41 | sound_voicer.bin: sex=1 |
| dlc_m04_kaito | male | high | voicer | sound_auth.bin | 41 | sound_voicer.bin: sex=1 |
| Restaurant Staff | male | high | voice_cue | sound_auth.bin(talker) | 40 | sound_auth.bin: คิวเสียง speech_m01_02500_youshoku -> sound_voicer sex (ชาย 10 : หญิง 0) · |
| Ogami | male | high | dossier | talk.bin | 39 | evidence.bin — Motoya Ogami: A public prosecutor. He appeared to be the victim of the evil |
| Yoshikawa | male | high | pronoun | talk.bin | 39 | Professor Yoshikawa is almost done with his work. Now I just need to find a Four Leaf Clov |
| Female Teacher | female | high | voicer | sound_auth.bin(talker) | 39 | sound_voicer.bin: sex=2 |
| Honda | male | high | voicer | talk.bin | 38 | sound_voicer.bin: sex=1 |
| Shimada | male | high | dossier | talk.bin | 38 | evidence.bin — Hisayoshi Shimada: A second-year student at Seiryo High. He consulted the M |
| Akaike | male | high | voice_cue | sound_auth.bin(talker) | 38 | sound_auth.bin: คิวเสียง speech_m04_01700_old_akaike -> sound_voicer sex (ชาย 24 : หญิง 0) |
| Rouge Owner | male | high | voice_cue | sound_auth.bin(talker) | 38 | sound_auth.bin: คิวเสียง speech_m11_01500_rouge_boy -> sound_voicer sex (ชาย 26 : หญิง 0)  |
| higashi | male | high | voicer | sound_auth.bin | 37 | sound_voicer.bin: sex=1 |
| Manaka | male | high | dossier | talk.bin | 35 | evidence.bin — Ikuo Manaka: Man who asked me to watch over his son as he goes out on his f |
| Kodama | male | high | dossier | talk.bin | 35 | evidence.bin — Kazutoshi Kodama: A man who works in the Community Revitalization Departmen |
| Sakakiba | male | high | voicer | talk.bin | 35 | sound_voicer.bin: sex=1 |
| Kuniko | female | high | voicer | sound_auth.bin(talker) | 35 | sound_voicer.bin: sex=2 |
| Mitsuru (age 30) | male | high | voice_cue | sound_auth.bin(talker) | 35 | sound_auth.bin: คิวเสียง speech_m13_00130_old_mitsuru -> sound_voicer sex (ชาย 2 : หญิง 0) |
| Naito | male | high | dossier | talk.bin | 34 | evidence.bin — Teruo Naito: A Seiryo High student with perilously low grades. His teacher  |
| Tokioka | male | medium | pronoun | talk.bin | 34 | Yes, Tokioka. Senpai seems to have asked you to do something for him, about UFOs. I figure |
| Gaudy Thug | male | high | voice_cue | sound_auth.bin(talker) | 34 | sound_auth.bin: คิวเสียง speech_m06_01400_chara_hangure -> sound_voicer sex (ชาย 18 : หญิง |
| Maho | female | high | voicer | sound_auth.bin(talker) | 34 | sound_voicer.bin: sex=2 |
| Muroi | male | high | dossier | talk.bin | 33 | evidence.bin — Muroi: Head of Community Promotion for the city. Doing his best to improve  |
| Matatabi | male | high | voicer | talk.bin | 32 | sound_voicer.bin: sex=1 |
| Iemori | female | high | dossier | talk.bin | 32 | evidence.bin — Mikuru Iemori: The former advisor of the MRC. I hear she stepped down when  |
| g_m_g01_yagami | male | high | voicer | sound_auth.bin | 32 | sound_voicer.bin: sex=1 |
| Akatsuka | male | high | voicer | talk.bin | 31 | sound_voicer.bin: sex=1 |
| Ostentatious Woman | female | high | voice_cue | sound_auth.bin(talker) | 30 | sound_auth.bin: คิวเสียง speech_dlc_g03_020_female_hade -> sound_voicer sex (ชาย 0 : หญิง  |
| Hanasaki's Dad | male | high | voice_cue | sound_auth.bin(talker) | 30 | sound_auth.bin: คิวเสียง speech_drama_m11_420_bomber_father -> sound_voicer sex (ชาย 19 :  |
| Tamai | male | high | dossier | talk.bin | 29 | evidence.bin — Shinataro Tamai: A man who almost fell off an apartment building. Rumor has |
| g_m_yagami | male | high | voicer | sound_auth.bin | 29 | sound_voicer.bin: sex=1 |
| G.I. | male | high | pronoun+role | talk.bin | 28 | (Once the Twisted Trio was out of the way, the real king of degenerate weirdos, "Giant Imp |
| Boys' Basketball Captain | male | high | voice_cue | sound_auth.bin(talker) | 28 | sound_auth.bin: คิวเสียง speech_m02_01000_bucho_basket -> sound_voicer sex (ชาย 15 : หญิง  |
| Kawai | male | high | voicer | auth.bin(cinema_telop) | 28 | sound_voicer.bin: sex=1 |
| sawa | female | high | voicer | sound_auth.bin | 28 | sound_voicer.bin: sex=2 |
| dlc_m03_jun | male | high | voicer | sound_auth.bin | 28 | sound_voicer.bin: sex=1 |
| Old Woman | female | medium | name | talk.bin | 27 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Old Woman |
| Toru | male | high | pronoun+role | talk.bin | 27 | Tagged along with me to keep an eye on Toru-kun after seeing a number of similar "first st |
| Ranpo | male | high | pronoun | talk.bin | 27 | Ranpo really does make an ace partner—I can't imagine a culprit with a scent he couldn't t |
| Hiiragi | male | high | dossier | talk.bin | 27 | evidence.bin — Takumi Hiiragi: Third-year and former captain of Seiryo High's dance club.  |
| kuwana | male | high | voicer | sound_auth.bin | 27 | sound_voicer.bin: sex=1 |
| Female Employee | female | high | voice_cue | talk.bin | 26 | sound_auth.bin: คิวเสียง speech_dlc_m01_01100_female_bite -> sound_voicer sex (ชาย 0 : หญิ |
| Female Newscaster | female | high | voice_cue | sound_auth.bin(talker) | 26 | sound_auth.bin: คิวเสียง speech_m10_01600_female_caster -> sound_voicer sex (ชาย 0 : หญิง  |
| Mankichi | male | high | voicer | talk.bin | 25 | sound_voicer.bin: sex=1 |
| Ashihara | male | high | dossier | talk.bin | 25 | evidence.bin — Kizuna Ashihara: Third year boy at Seiryo High. Faked his age to get into a |
| Scared Woman | female | medium | name | talk.bin | 24 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Scared Woman |
| MC | male | high | voice_cue | talk.bin | 24 | sound_auth.bin: คิวเสียง speech_drama_m04_690_emcee -> sound_voicer sex (ชาย 6 : หญิง 0) · |
| Diligent Policeman | male | high | voice_cue | sound_auth.bin(talker) | 24 | sound_auth.bin: คิวเสียง speech_dlc_m03_01800_police_hard -> sound_voicer sex (ชาย 7 : หญิ |
| Portly Middle-Aged Man | male | medium | name | talk.bin | 23 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Portly Middle-Aged Man |
| Fujita | female | high | voicer | talk.bin | 23 | sound_voicer.bin: sex=2 |
| Otsuki | male | high | voice_cue | talk.bin | 23 | sound_auth.bin: คิวเสียง speech_drama_m13_430_ootsuki -> sound_voicer sex (ชาย 4 : หญิง 0) |
| Hotta | male | high | voicer | sound_auth.bin(talker) | 23 | sound_voicer.bin: sex=1 |
| dlc_m01_kaito | male | high | voicer | sound_auth.bin | 23 | sound_voicer.bin: sex=1 |
| Mikoshiba | male | high | voicer | sound_auth.bin(talker) | 22 | sound_voicer.bin: sex=1 |
| Young Employee | male | high | voice_cue | sound_auth.bin(talker) | 22 | sound_auth.bin: คิวเสียง speech_dlc_m02_00750_staff_young -> sound_voicer sex (ชาย 11 : หญ |
| old_mamiya | female | high | voicer | sound_auth.bin | 22 | sound_voicer.bin: sex=2 |
| tessou | male | high | voicer | sound_auth.bin | 22 | sound_voicer.bin: sex=1 |
| Policeman | male | high | pronoun+role | talk.bin | 21 | I couldn't believe it! And he was a policeman, too! |
| Long-Faced Basketball Girl | female | high | voice_cue | sound_auth.bin(talker) | 21 | sound_auth.bin: คิวเสียง speech_m02_01000_omonaga_basket -> sound_voicer sex (ชาย 0 : หญิง |
| g_m_kaito | male | high | voicer | sound_auth.bin | 21 | sound_voicer.bin: sex=1 |
| Blond Man | male | high | voice_cue | talk.bin | 20 | sound_auth.bin: คิวเสียง speech_m01_00300_blondhair_man -> sound_voicer sex (ชาย 10 : หญิง |
| All | male | high | voice_cue | talk.bin | 19 | sound_auth.bin: คิวเสียง speech_drama_m23_060_yagami -> sound_voicer sex (ชาย 4 : หญิง 0)  |
| Mikitaka | male | high | voice_cue | talk.bin | 19 | sound_auth.bin: คิวเสียง speech_drama_m13_020_mikidaka -> sound_voicer sex (ชาย 3 : หญิง 0 |
| Mitsui | male | high | dossier | talk.bin | 19 | evidence.bin — Yuto Mitsui: A member of the Ijincho Hounds, a skateboarding group. He seem |
| Shin | male | high | pronoun+role | talk.bin | 19 | The older brother of Shin Amon, who challenged me to a duel three years ago. Strong enough |
| Lady at Reception | female | high | voice_cue | sound_auth.bin(talker) | 19 | sound_auth.bin: คิวเสียง speech_dlc_g04_010_female_recep -> sound_voicer sex (ชาย 0 : หญิง |
| Guy Stationed at Front Desk | male | high | voice_cue | sound_auth.bin(talker) | 19 | sound_auth.bin: คิวเสียง speech_m05_01400_tamari_uketsuke -> sound_voicer sex (ชาย 10 : หญ |
| Yokomichi Owner | male | high | voice_cue | sound_auth.bin(talker) | 19 | sound_auth.bin: คิวเสียง speech_m08_01800_yokomichi -> sound_voicer sex (ชาย 16 : หญิง 0)  |
| Man in Black | male | medium | name | talk.bin | 18 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Man in Black |
| Contest MC | male | high | voice_cue | talk.bin | 18 | sound_auth.bin: คิวเสียง speech_drama_m24_250_robo_emcee -> sound_voicer sex (ชาย 4 : หญิง |
| Rank-F Thug | male | high | voice_cue | talk.bin | 18 | sound_auth.bin: คิวเสียง speech_g_m_g05_010_030_rankf_chimpira -> sound_voicer sex (ชาย 6  |
| Gopher by Door | male | high | voice_cue | sound_auth.bin(talker) | 18 | sound_auth.bin: คิวเสียง speech_m01_00500_door_chinpira -> sound_voicer sex (ชาย 9 : หญิง  |
| Troubled Guest | male | high | voice_cue | sound_auth.bin(talker) | 18 | sound_auth.bin: คิวเสียง speech_dlc_g02_015_customer_lost -> sound_voicer sex (ชาย 9 : หญิ |
| g_m_g10_yagami | male | high | voicer | sound_auth.bin | 18 | sound_voicer.bin: sex=1 |
| okuda | male | high | voicer | sound_auth.bin | 18 | sound_voicer.bin: sex=1 |
| dlc_g_m_kaito | male | high | voicer | sound_auth.bin | 18 | sound_voicer.bin: sex=1 |
| Fujimaru | male | high | pronoun | talk.bin | 17 | I want to capture the moment when Fujimaru picks a pocket, with an evil look on his face. |
| Geomijul Thug | male | high | voice_cue | sound_auth.bin(talker) | 17 | sound_auth.bin: คิวเสียง speech_m10_02300_comijurumen -> sound_voicer sex (ชาย 11 : หญิง 0 |
| dlc_m03_shirakaba | male | high | voicer | sound_auth.bin | 17 | sound_voicer.bin: sex=1 |
| Burglar | male | high | voice_cue | talk.bin | 16 | sound_auth.bin: คิวเสียง speech_side_ptc08_0010_robbery -> sound_voicer sex (ชาย 7 : หญิง  |
| Nishimura | male | high | voicer | talk.bin | 16 | sound_voicer.bin: sex=1 |
| Kanasugi | male | high | voice_cue | talk.bin | 16 | sound_auth.bin: คิวเสียง speech_drama_m11_050_kanesugi -> sound_voicer sex (ชาย 8 : หญิง 0 |
| Gaudy Man | male | medium | name | talk.bin | 16 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Gaudy Man |
| Good-Natured Woman | female | medium | name | talk.bin | 16 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Good-Natured Woman |
| Kim | male | high | voicer | talk.bin | 16 | sound_voicer.bin: sex=1 |
| Kawaguchi | male | medium | pronoun | talk.bin | 16 | You think Kawaguchi's full of shit? He's obsessed with this kid's show and is getting hims |
| Janitor | male | high | voice_cue | sound_auth.bin(talker) | 16 | sound_auth.bin: คิวเสียง speech_g01_060_youmuin -> sound_voicer sex (ชาย 8 : หญิง 0) · voi |
| Tracksuit Yakuza | male | high | voice_cue | sound_auth.bin(talker) | 16 | sound_auth.bin: คิวเสียง speech_dlc_m02_00110_jersey_yakuza -> sound_voicer sex (ชาย 2 : ห |
| Scared Father | male | high | name+role | talk.bin | 15 | Scared Father |
| Dance Club Members | female | high | voice_cue | talk.bin | 15 | sound_auth.bin: คิวเสียง speech_drama_m91_150_sayaka -> sound_voicer sex (ชาย 0 : หญิง 2)  |
| Security | male | high | pronoun | talk.bin | 15 | He's from Public Security? |
| Shungiku | male | high | voicer | talk.bin | 15 | sound_voicer.bin: sex=1 |
| Rank-D Thug | male | high | voice_cue | talk.bin | 15 | sound_auth.bin: คิวเสียง speech_g_m_g05_010_030_rankd_chimpira -> sound_voicer sex (ชาย 5  |
| matsui | male | high | voicer | sound_auth.bin | 15 | sound_voicer.bin: sex=1 |
| dlc_m04_jun | male | high | voicer | sound_auth.bin | 15 | sound_voicer.bin: sex=1 |
| Mita | male | high | dossier | talk.bin | 14 | evidence.bin — Gouro Mita: The burglar who was living in the office's attic. Apparently, h |
| Hojo | male | high | dossier | talk.bin | 14 | evidence.bin — Takashi Hojo: An author and member of Kazuto Jumonji. An expert in scientif |
| Innocent Boy | male | high | voicer | talk.bin | 14 | sound_voicer.bin: sex=1 |
| Boy | male | high | voice_cue | talk.bin | 14 | sound_auth.bin: คิวเสียง speech_dlc_m01_01100_jun -> sound_voicer sex (ชาย 7 : หญิง 0) · v |
| Tsuruno | male | high | pronoun+role | talk.bin | 14 | I need a picture of Tsuruno-kun dodging the ball in a cool way. I should try to get his fa |
| Citron Mahjong Madam | female | medium | title | talk.bin | 14 | Citron Mahjong Madam |
| Rabuho | female | high | voicer | talk.bin | 14 | sound_voicer.bin: sex=2 |
| Red Flag Thug | male | high | voice_cue | sound_auth.bin(talker) | 14 | sound_auth.bin: คิวเสียง speech_m10_02100_yabame_hangure -> sound_voicer sex (ชาย 8 : หญิง |
| Judge | male | medium-conflict | majority(4:1) | auth.bin(cinema_telop) | 14 | A pervert who decides a couple's guilt or innocence after peeking at them in the act. I le |
| Harassing Girl | female | high | name+role | auth.bin(cinema_telop) | 14 | Harassing Girl |
| kosuke | male | high | voicer | sound_auth.bin | 14 | sound_voicer.bin: sex=1 |
| amasawa | female | high | voicer | sound_auth.bin | 14 | sound_voicer.bin: sex=2 |
| g_m_g01_tsukumo | male | high | voicer | sound_auth.bin | 14 | sound_voicer.bin: sex=1 |
| dlc_m04_senda | male | high | voicer | sound_auth.bin | 14 | sound_voicer.bin: sex=1 |
| Sakamoto | male | medium | pronoun | talk.bin | 13 | But I saw Sakamoto-san watching Captain Cop during his lunch break. He was even tearing up |
| Oguro | male | medium | pronoun | talk.bin | 13 | Oh, there he is—that's Oguro-san, our custodian. |
| Shogi-Playing Man | male | medium | name | talk.bin | 13 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Shogi-Playing Man |
| Man in Suit | male | medium | name | talk.bin | 13 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Man in Suit |
| Guy with Crew Cut | male | high | name+role | talk.bin | 13 | Guy with Crew Cut |
| Oyamada | male | high | voicer | talk.bin | 13 | sound_voicer.bin: sex=1 |
| Thirsty RK Member | male | high | voice_cue | talk.bin | 13 | sound_auth.bin: คิวเสียง speech_g_m_g05_010_060_yoitai_rk -> sound_voicer sex (ชาย 6 : หญิ |
| Woman in Dress | female | high | voice_cue | talk.bin | 13 | sound_auth.bin: คิวเสียง speech_dlc_m04_01150_female_dress -> sound_voicer sex (ชาย 0 : หญ |
| Momoyama | female | medium | pronoun | talk.bin | 13 | Will you tell Momoyama-san why you bugged her now? Or do we need to get the police involve |
| Aragaki | male | high | voicer | sound_auth.bin(talker) | 13 | sound_voicer.bin: sex=1 |
| Troubled Girl | female | high | voice_cue | sound_auth.bin(talker) | 13 | sound_auth.bin: คิวเสียง speech_dlc_m02_01420_girl_bothered -> sound_voicer sex (ชาย 0 : ห |
| keiko | female | high | voicer | sound_auth.bin | 13 | sound_voicer.bin: sex=2 |
| sakaki | male | high | voicer | sound_auth.bin | 13 | sound_voicer.bin: sex=1 |
| ehara | male | high | voicer | sound_auth.bin | 13 | sound_voicer.bin: sex=1 |
| dlc_m04_igarashi | male | high | voicer | sound_auth.bin | 13 | sound_voicer.bin: sex=1 |
| Professor Panty | male | high | dossier | talk.bin | 12 | evidence.bin — Professor Panty: A pervert with a penchant for stealing specific panties. A |
| Iwashita | male | high | voicer | talk.bin | 12 | sound_voicer.bin: sex=1 |
| Blond Punk | male | high | voice_cue | talk.bin | 12 | sound_auth.bin: คิวเสียง speech_dlc_m02_01100_chinpira_gold -> sound_voicer sex (ชาย 1 : ห |
| Station Passerby | male | high | voice_cue | sound_auth.bin(talker) | 12 | sound_auth.bin: คิวเสียง speech_m10_00900_station_passer -> sound_voicer sex (ชาย 2 : หญิง |
| g_m_higashi | male | high | voicer | sound_auth.bin | 12 | sound_voicer.bin: sex=1 |
| g04_yagami | male | high | voicer | sound_auth.bin | 12 | sound_voicer.bin: sex=1 |
| Judge Creep 'n Peep | male | high | dossier | talk.bin | 11 | evidence.bin — Judge Creep 'n Peep: A pervert who decides a couple's guilt or innocence af |
| Tanibukuro | male | medium | pronoun | talk.bin | 11 | Tanibukuro-tan's parents are mega billionaires. Taking out a loan is no big deal for him. |
| Drunk Thug | male | high | voice_cue | sound_auth.bin(talker) | 11 | sound_auth.bin: คิวเสียง speech_dlc_m02_00210_chinpira_drunk -> sound_voicer sex (ชาย 3 :  |
| Harassing Boy | male | medium | name | auth.bin(cinema_telop) | 11 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Harassing Boy |
| akane | female | high | voicer | sound_auth.bin | 11 | sound_voicer.bin: sex=2 |
| wanatabe | male | high | voicer | sound_auth.bin | 11 | sound_voicer.bin: sex=1 |
| g_m_g10_sugiura | male | high | voicer | sound_auth.bin | 11 | sound_voicer.bin: sex=1 |
| Imogashira | male | high | voicer | talk.bin | 10 | sound_voicer.bin: sex=1 |
| Dog | male | high | dossier | talk.bin | 10 | evidence.bin — Detective Dog: A detective dog that's being "working cases" all over Ijinch |
| Saiga | male | high | dossier | talk.bin | 10 | evidence.bin — Hiroki Saiga: A social studies teacher at Seiryo High. He was being blackma |
| Ayuhara | male | high | dossier | talk.bin | 10 | evidence.bin — Takara Ayuhara: An author and member of Kazuto Jumonji. Formerly a scriptwr |
| Masuyama | female | high | dossier | talk.bin | 10 | evidence.bin — Masuyama: Ogami's secretary. She was the one who installed the bug in the s |
| Pompadoured Guy | male | high | voice_cue | talk.bin | 10 | sound_auth.bin: คิวเสียง speech_drama_m14_420_regent -> sound_voicer sex (ชาย 3 : หญิง 0)  |
| Suzaki | male | high | voicer | talk.bin | 10 | sound_voicer.bin: sex=1 |
| Crimson Lotus Man | male | high | voice_cue | sound_auth.bin(talker) | 10 | sound_auth.bin: คิวเสียง speech_dlc_m04_01400_male_guren -> sound_voicer sex (ชาย 7 : หญิง |
| Ya-kun | male | high | voice_cue | sound_auth.bin(talker) | 10 | sound_auth.bin: คิวเสียง speech_m01_05500_yakkun -> sound_voicer sex (ชาย 5 : หญิง 0) · vo |
| Woman Who Calls Herself Masuda | female | high | voice_cue | sound_auth.bin(talker) | 10 | sound_auth.bin: คิวเสียง speech_dlc_m04_01150_female_masuda -> sound_voicer sex (ชาย 0 : ห |
| drama_m24_doumu | male | high | voicer | sound_auth.bin | 10 | sound_voicer.bin: sex=1 |
| side_ptc071_yagami | male | high | voicer | sound_auth.bin | 10 | sound_voicer.bin: sex=1 |
| Unsavory Man | male | high | voice_cue | talk.bin | 9 | sound_auth.bin: คิวเสียง speech_m01_02000_garawaru_man -> sound_voicer sex (ชาย 3 : หญิง 0 |
| Sakura-sensei's Mother | female | medium | name | talk.bin | 9 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Sakura-sensei's Mother |
| Angry Old Man | male | medium | name | talk.bin | 9 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Angry Old Man |
| Young Woman | female | medium | name | talk.bin | 9 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Young Woman |
| Superficial Woman | female | medium | name | talk.bin | 9 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Superficial Woman |
| Manager | male | medium-conflict | majority(10:2) | talk.bin | 9 | And this guy is some kinda girls' bar manager?　　 |
| Student A | male | high | voice_cue | sound_auth.bin(talker) | 9 | sound_auth.bin: คิวเสียง speech_m08_00800_student01 -> sound_voicer sex (ชาย 1 : หญิง 0) · |
| Edgy Thug | male | high | voice_cue | sound_auth.bin(talker) | 9 | sound_auth.bin: คิวเสียง speech_m10_02100_togari_hangure -> sound_voicer sex (ชาย 5 : หญิง |
| Red-Haired Thug | male | high | voice_cue | sound_auth.bin(talker) | 9 | sound_auth.bin: คิวเสียง speech_dlc_m02_01100_chinpira_red -> sound_voicer sex (ชาย 5 : หญ |
| Middle-Aged Waiter | male | high | voice_cue | sound_auth.bin(talker) | 9 | sound_auth.bin: คิวเสียง speech_dlc_m04_01150_male_boy -> sound_voicer sex (ชาย 5 : หญิง 0 |
| g01_yagami | male | high | voicer | sound_auth.bin | 9 | sound_voicer.bin: sex=1 |
| sakurai | male | high | voicer | sound_auth.bin | 9 | sound_voicer.bin: sex=1 |
| old_akaike | male | high | voicer | sound_auth.bin | 9 | sound_voicer.bin: sex=1 |
| mafuyu | female | high | voicer | sound_auth.bin | 9 | sound_voicer.bin: sex=2 |
| g_g_yagami | male | high | voicer | sound_auth.bin | 9 | sound_voicer.bin: sex=1 |
| drama_m24_kurumazaki | male | high | voicer | sound_auth.bin | 9 | sound_voicer.bin: sex=1 |
| g_m_g05_yagami | male | high | voicer | sound_auth.bin | 9 | sound_voicer.bin: sex=1 |
| side_ptc071_kaito | male | high | voicer | sound_auth.bin | 9 | sound_voicer.bin: sex=1 |
| Shinonome? | male | high | dossier (ยืมจาก "Shinonome" — ชื่อเดียวกันสะกดคนละแบบ) | talk.bin | 8 | evidence.bin — Ryuichi Shinonome: A game developer and director for God-Tier Games. Accord |
| Cherry | female | high | dossier | talk.bin | 8 | evidence.bin — Cherry: She's the cat Hakase-san is taking care of. |
| Timid-Looking Man | male | medium | name | talk.bin | 8 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Timid-Looking Man |
| Host | female | high | pronoun+role | talk.bin | 8 | That girl on the floor had herself a real good time at one of our host clubs. |
| Gopher on Watch | male | high | voice_cue | sound_auth.bin(talker) | 8 | sound_auth.bin: คิวเสียง speech_m01_00200_mihari_chinpira -> sound_voicer sex (ชาย 4 : หญิ |
| Long-Haired Dude | male | high | voice_cue | sound_auth.bin(talker) | 8 | sound_auth.bin: คิวเสียง speech_m01_00300_longhair_man -> sound_voicer sex (ชาย 4 : หญิง 0 |
| RK Member on Watch | male | high | voice_cue | sound_auth.bin(talker) | 8 | sound_auth.bin: คิวเสียง speech_g_m_g07_025_040_mihari_rk -> sound_voicer sex (ชาย 5 : หญิ |
| Outgoing Barker | male | high | voice_cue | sound_auth.bin(talker) | 8 | sound_auth.bin: คิวเสียง speech_dlc_m02_01410_catch_kisaku -> sound_voicer sex (ชาย 4 : หญ |
| Freckled Basketball Player | female | high | voice_cue | sound_auth.bin(talker) | 8 | sound_auth.bin: คิวเสียง speech_m02_01000_sobakasu_basket -> sound_voicer sex (ชาย 0 : หญิ |
| Chubby Thug | male | high | voice_cue | sound_auth.bin(talker) | 8 | sound_auth.bin: คิวเสียง speech_m08_01700_fat_hangure -> sound_voicer sex (ชาย 5 : หญิง 0) |
| Burly Ex-Tojo Clan Member | male | high | voice_cue | sound_auth.bin(talker) | 8 | sound_auth.bin: คิวเสียง speech_m12_01400_gotsui_mototojo -> sound_voicer sex (ชาย 4 : หญิ |
| Slacker Thug | male | high | voice_cue | sound_auth.bin(talker) | 8 | sound_auth.bin: คิวเสียง speech_g_m_g01_040_030_sabori_chinpira -> sound_voicer sex (ชาย 4 |
| Pick-Up Artist | male | high | voice_cue | sound_auth.bin(talker) | 8 | sound_auth.bin: คิวเสียง speech_dlc_g_g_g03_020_030_chinpira_nanpa -> sound_voicer sex (ชา |
| Spunky Minion | male | high | voice_cue | sound_auth.bin(talker) | 8 | sound_auth.bin: คิวเสียง speech_dlc_m02_01600_syatei_isei -> sound_voicer sex (ชาย 3 : หญิ |
| Mover | male | high | voice_cue | sound_auth.bin(talker) | 8 | sound_auth.bin: คิวเสียง speech_dlc_m02_01850_staff_moving -> sound_voicer sex (ชาย 4 : หญ |
| Plage Staff | female | high | voicer | auth.bin(cinema_telop) | 8 | sound_voicer.bin: sex=2 |
| kouda | female | high | voicer | sound_auth.bin | 8 | sound_voicer.bin: sex=2 |
| mari | female | high | voicer | sound_auth.bin | 8 | sound_voicer.bin: sex=2 |
| kusumoto | female | high | voicer | sound_auth.bin | 8 | sound_voicer.bin: sex=2 |
| dlc_m03_mikiko | female | high | voicer | sound_auth.bin | 8 | sound_voicer.bin: sex=2 |
| drama_m24_yagami | male | high | voicer | sound_auth.bin | 8 | sound_voicer.bin: sex=1 |
| dlc_m01_higashi | male | high | voicer | sound_auth.bin | 8 | sound_voicer.bin: sex=1 |
| dlc_m02_senda | male | high | voicer | sound_auth.bin | 8 | sound_voicer.bin: sex=1 |
| Suspicious Young Man | male | medium | name | talk.bin | 7 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Suspicious Young Man |
| Fake Yagami | male | high | voicer | talk.bin | 7 | sound_voicer.bin: sex=1 |
| Man | male | high | dossier | talk.bin | 7 | evidence.bin — Suspicious Man: Seven years ago, this man snuck into Kitan Amasawa's home a |
| Woman | female | medium-conflict | majority(13:1) | talk.bin | 7 | The death of an innocent woman. |
| Long-Haired Boy | male | medium | name | talk.bin | 7 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Long-Haired Boy |
| Thug with a Goatee | male | high | voice_cue | sound_auth.bin(talker) | 7 | sound_auth.bin: คิวเสียง speech_dlc_m01_01100_chinpira_ago -> sound_voicer sex (ชาย 4 : หญ |
| Mamiya's Son (age 6) | male | high | voice_cue | sound_auth.bin(talker) | 7 | sound_auth.bin: คิวเสียง speech_m05_01800_mamiya_jr -> sound_voicer sex (ชาย 4 : หญิง 0) · |
| Tropical Minion | male | high | voice_cue | sound_auth.bin(talker) | 7 | sound_auth.bin: คิวเสียง speech_dlc_m02_01600_syatei_aloha -> sound_voicer sex (ชาย 3 : หญ |
| Pea Coat | male | high | voice_cue | sound_auth.bin(talker) | 7 | sound_auth.bin: คิวเสียง speech_m11_01950_pcoat -> sound_voicer sex (ชาย 6 : หญิง 0) · voi |
| Female Client | female | high | voice_cue | sound_auth.bin(talker) | 7 | sound_auth.bin: คิวเสียง speech_dlc_m01_00400_female_irai -> sound_voicer sex (ชาย 0 : หญิ |
| Young Waiter | male | high | voice_cue | sound_auth.bin(talker) | 7 | sound_auth.bin: คิวเสียง speech_dlc_g04_015_young_boy -> sound_voicer sex (ชาย 4 : หญิง 0) |
| Caring Waiter | male | high | voice_cue | sound_auth.bin(talker) | 7 | sound_auth.bin: คิวเสียง speech_dlc_g04_015_care_boy -> sound_voicer sex (ชาย 4 : หญิง 0)  |
| Friend of Woman in Dress | female | high | voice_cue | sound_auth.bin(talker) | 7 | sound_auth.bin: คิวเสียง speech_dlc_m04_01150_friends_dress -> sound_voicer sex (ชาย 0 : ห |
| dlc_g_m_g03_kaito | male | high | voicer | sound_auth.bin | 7 | sound_voicer.bin: sex=1 |
| dlc_m02_mikiko | female | high | voicer | sound_auth.bin | 7 | sound_voicer.bin: sex=2 |
| drama_m91_yagami | male | high | voicer | sound_auth.bin | 7 | sound_voicer.bin: sex=1 |
| senpai_leader | male | high | voicer | sound_auth.bin | 7 | sound_voicer.bin: sex=1 |
| ikatsui_hangure | male | high | voicer | sound_auth.bin | 7 | sound_voicer.bin: sex=1 |
| seiren | male | high | voicer | sound_auth.bin | 7 | sound_voicer.bin: sex=1 |
| drama_m24_dento | male | high | voicer | sound_auth.bin | 7 | sound_voicer.bin: sex=1 |
| drama_m24_itokura | female | high | voicer | sound_auth.bin | 7 | sound_voicer.bin: sex=2 |
| dlc_g_m_senda | male | high | voicer | sound_auth.bin | 7 | sound_voicer.bin: sex=1 |
| dlc_g_m_igarashi | male | high | voicer | sound_auth.bin | 7 | sound_voicer.bin: sex=1 |
| Displeased Student | male | high | voice_cue | talk.bin | 6 | sound_auth.bin: คิวเสียง speech_drama_m21_020_takamori -> sound_voicer sex (ชาย 4 : หญิง 0 |
| Manabe | male | high | dossier | talk.bin | 6 | evidence.bin — Manabe: An author and member of Kazuto Jumonji. According to Okazaki-san, h |
| Tenjinbashi | male | high | dossier | talk.bin | 6 | evidence.bin — Wataru Tenjinbashi: Former editor of Kazuto Jumonji. He was the culprit of  |
| Man's Voice | male | medium | name | talk.bin | 6 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Man's Voice |
| Troubled Mother | female | high | name+role | talk.bin | 6 | Troubled Mother |
| Mako-chan | female | high | pronoun+role | talk.bin | 6 | You're Mako-chan, right? Your mom's been worried. Let's go find her, yeah? |
| Brown-Haired Boy | male | medium | name | talk.bin | 6 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Brown-Haired Boy |
| Female Mahjong Hobbyist | female | medium | name | talk.bin | 6 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Female Mahjong Hobbyist |
| Male Mahjong Hobbyist | male | medium | name | talk.bin | 6 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Male Mahjong Hobbyist |
| Yakuza-Like Man | male | medium | name | talk.bin | 6 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Yakuza-Like Man |
| Murasaki | male | high | dossier | talk.bin | 6 | evidence.bin — Reiji Murasaki: The first rep of Made In Heaven who died in an accident a y |
| Referee | male | high | voicer | talk.bin | 6 | sound_voicer.bin: sex=1 |
| P.E. Teacher | male | high | voice_cue | sound_auth.bin(talker) | 6 | sound_auth.bin: คิวเสียง speech_m01_05200_pe_teacher -> sound_voicer sex (ชาย 3 : หญิง 0)  |
| 1st-Year Female Member | female | high | voice_cue | sound_auth.bin(talker) | 6 | sound_auth.bin: คิวเสียง speech_drama_m04_400_girl_1stgrade -> sound_voicer sex (ชาย 0 : ห |
| 2nd-Year Female Member | female | high | voice_cue | sound_auth.bin(talker) | 6 | sound_auth.bin: คิวเสียง speech_drama_m04_400_girl_2ndgrade -> sound_voicer sex (ชาย 0 : ห |
| Cocky Yokohama Liumang Thug | male | high | voice_cue | sound_auth.bin(talker) | 6 | sound_auth.bin: คิวเสียง speech_m10_02500_namaiki_hanpin -> sound_voicer sex (ชาย 4 : หญิง |
| Charles Attendant | male | high | voice_cue | sound_auth.bin(talker) | 6 | sound_auth.bin: คิวเสียง speech_m09_01900_charles_boy -> sound_voicer sex (ชาย 4 : หญิง 0) |
| Wild Thug | male | high | voice_cue | sound_auth.bin(talker) | 6 | sound_auth.bin: คิวเสียง speech_m10_02200_araburu_hangure -> sound_voicer sex (ชาย 3 : หญิ |
| Basketball Player | male | high | voice_cue | sound_auth.bin(talker) | 6 | sound_auth.bin: คิวเสียง speech_drama_m04_400_basketball_guy -> sound_voicer sex (ชาย 3 :  |
| Disgruntled Thug | male | high | voice_cue | sound_auth.bin(talker) | 6 | sound_auth.bin: คิวเสียง speech_g_m_g05_010_030_fuman_hangure -> sound_voicer sex (ชาย 3 : |
| Panicked Yakuza | male | high | voice_cue | sound_auth.bin(talker) | 6 | sound_auth.bin: คิวเสียง speech_dlc_g02_010_yakuza_panic -> sound_voicer sex (ชาย 3 : หญิง |
| Resigned Man | male | high | voice_cue | sound_auth.bin(talker) | 6 | sound_auth.bin: คิวเสียง speech_dlc_g04_010_man_lost -> sound_voicer sex (ชาย 3 : หญิง 0)  |
| Average Waiter | male | high | voice_cue | sound_auth.bin(talker) | 6 | sound_auth.bin: คิวเสียง speech_dlc_g04_015_normal_boy -> sound_voicer sex (ชาย 4 : หญิง 0 |
| Panicked Waiter | male | high | voice_cue | sound_auth.bin(talker) | 6 | sound_auth.bin: คิวเสียง speech_dlc_g04_015_panic_boy -> sound_voicer sex (ชาย 3 : หญิง 0) |
| drama_m34_todoroki | male | high | voicer | sound_auth.bin | 6 | sound_voicer.bin: sex=1 |
| female_teacher | female | high | voicer | sound_auth.bin | 6 | sound_voicer.bin: sex=2 |
| g_m_sugiura | male | high | voicer | sound_auth.bin | 6 | sound_voicer.bin: sex=1 |
| rouge_boy | male | high | voicer | sound_auth.bin | 6 | sound_voicer.bin: sex=1 |
| drama_m31_todoroki | male | high | voicer | sound_auth.bin | 6 | sound_voicer.bin: sex=1 |
| drama_m24_takamori | male | high | voicer | sound_auth.bin | 6 | sound_voicer.bin: sex=1 |
| drama_m91_itokura | female | high | voicer | sound_auth.bin | 6 | sound_voicer.bin: sex=2 |
| side_ptc100_yagami | male | high | voicer | sound_auth.bin | 6 | sound_voicer.bin: sex=1 |
| side_ptc100_kyoko | female | high | voicer | sound_auth.bin | 6 | sound_voicer.bin: sex=2 |
| dlc_m02_girl_bothered | female | high | voicer | sound_auth.bin | 6 | sound_voicer.bin: sex=2 |
| dlc_m02_female_clean | female | high | voicer | sound_auth.bin | 6 | sound_voicer.bin: sex=2 |
| dlc_m02_syatei_isei | male | high | voicer | sound_auth.bin | 6 | sound_voicer.bin: sex=1 |
| dlc_m04_shirakaba | male | high | voicer | sound_auth.bin | 6 | sound_voicer.bin: sex=1 |
| dlc_m04_mikiko | female | high | voicer | sound_auth.bin | 6 | sound_voicer.bin: sex=2 |
| Middle-Aged Man | male | medium | name | talk.bin | 5 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Middle-Aged Man |
| Kyushu No. 1 Star Chef | male | high | voice_cue | talk.bin | 5 | sound_auth.bin: คิวเสียง speech_dlc_g02_020_kyuusyuu_staff -> sound_voicer sex (ชาย 1 : หญ |
| Yoshiba | male | high | dossier | talk.bin | 5 | evidence.bin — Shinya Yoshiba: A member of the Seiryo High eSports Club. He is one of the  |
| Pale Young Man | male | medium | name | talk.bin | 5 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Pale Young Man |
| Plump Woman | female | medium | name | talk.bin | 5 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Plump Woman |
| Happy Girl | female | high | name+role | talk.bin | 5 | Happy Girl |
| Punk | male | high | pronoun | talk.bin | 5 | But apparently this little punk had some fight in him. Almost started some shit with our g |
| Wakita | male | high | pronoun+role | talk.bin | 5 | This guy. Name's Wakita... He's got the semi-finals comin' up for East Japan's Rookie of t |
| Buzz-Cut Boy | male | medium | name | talk.bin | 5 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Buzz-Cut Boy |
| Gaunt Man | male | medium | name | talk.bin | 5 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Gaunt Man |
| Active Girl | female | high | name+role | talk.bin | 5 | Active Girl |
| Impatient Punk | male | high | voice_cue | sound_auth.bin(talker) | 5 | sound_auth.bin: คิวเสียง speech_dgmb4020040_chinpira_tanki -> sound_voicer sex (ชาย 4 : หญ |
| Ex-Tojo Clan Thug | male | high | voice_cue | sound_auth.bin(talker) | 5 | sound_auth.bin: คิวเสียง speech_m12_01300_mototojo_hangure -> sound_voicer sex (ชาย 3 : หญ |
| Trend-Chasing Soccer Player | male | high | voice_cue | sound_auth.bin(talker) | 5 | sound_auth.bin: คิวเสียง speech_drama_m04_400_soccer_guy2 -> sound_voicer sex (ชาย 3 : หญิ |
| Messed-Up RK Member | male | high | voice_cue | sound_auth.bin(talker) | 5 | sound_auth.bin: คิวเสียง speech_g_m_g07_025_020_susannda_rk -> sound_voicer sex (ชาย 3 : ห |
| Veteran Waiter | male | high | voice_cue | sound_auth.bin(talker) | 5 | sound_auth.bin: คิวเสียง speech_dlc_g04_010_veteran_boy -> sound_voicer sex (ชาย 3 : หญิง  |
| Young Alumnus 1 | male | high | voice_cue | sound_auth.bin(talker) | 5 | sound_auth.bin: คิวเสียง speech_dlc_m04_01150_ob_01 -> sound_voicer sex (ชาย 3 : หญิง 0) · |
| Restaurant Owner | female | high | pronoun+role | auth.bin(cinema_telop) | 5 | Oh yeahhh, I think she was the daughter of a Chinese restaurant owner. |
| kousai_saibancho | male | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=1 |
| akutsu | male | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=1 |
| souma | male | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=1 |
| drama_m04_takanashi | female | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=2 |
| yabame_hangure | male | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=1 |
| dlc_m02_syatei_aloha | male | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=1 |
| bandou | male | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=1 |
| megu | female | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=2 |
| drama_m32_todoroki | male | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=1 |
| drama_m32_yagami | male | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=1 |
| drama_m23_itokura | female | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=2 |
| side_ptc18_yagami | male | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=1 |
| side_ptc18_minato | female | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=2 |
| drama_m11_yagami | male | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=1 |
| g_m_g10_tsukumo | male | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=1 |
| side_ptc99_yagami | male | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=1 |
| dlc_g_g_g02_kaito | male | high | voicer | sound_auth.bin | 5 | sound_voicer.bin: sex=1 |
| Ringer Hut Cashier | female | high | voice_cue | talk.bin | 4 | sound_auth.bin: คิวเสียง speech_dlc_m02_01410_staff_hat -> sound_voicer sex (ชาย 0 : หญิง  |
| Homeless Man | male | medium | name | talk.bin | 4 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Homeless Man |
| Kamulop | female | medium-conflict | majority(12:1) | talk.bin | 4 | A girl who nearly suffered a heat stroke inside a Kamulop costume. She can't speak directl |
| High School Girl | female | high | name+pronoun+role | talk.bin | 4 | Includes high school girl |
| Brown-Haired Woman | female | medium | name | talk.bin | 4 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Brown-Haired Woman |
| Bespectacled Young Man | male | medium | name | talk.bin | 4 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Bespectacled Young Man |
| Short-Haired Punk | male | high | voice_cue | talk.bin | 4 | sound_auth.bin: คิวเสียง speech_dlc_m03_01000_chinpira_short -> sound_voicer sex (ชาย 1 :  |
| Asakusa | male | high | dossier | talk.bin | 4 | evidence.bin — Jirozaemon Asakusa: He may be 78 years old, but Ryan calls him his number o |
| Screaming Boy | male | medium | name | talk.bin | 4 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Screaming Boy |
| Businessman | male | high | pronoun+role | talk.bin | 4 | more like a ${tag0} than a legit businessman, to me |
| eSports Club President | male | medium | pronoun | talk.bin | 4 | Seiryo High eSports Club president. Second year. A bit lacking in self-awareness. Seems to |
| Dour Company Man | male | medium | name | talk.bin | 4 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Dour Company Man |
| Thrifty Yakuza | male | high | dossier | talk.bin | 4 | evidence.bin — Thrifty Yakuza: He's a reseller who went to Ebisu Pawn because he heard on  |
| Middle-Aged Man in Suit | male | medium | name | talk.bin | 4 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Middle-Aged Man in Suit |
| Mohawk Girl | female | high | name+role | talk.bin | 4 | Mohawk Girl |
| Reiji | male | high | voicer | talk.bin | 4 | sound_voicer.bin: sex=1 |
| Fresh-Faced Punk | male | high | voice_cue | talk.bin | 4 | sound_auth.bin: คิวเสียง speech_drama_m91_290_chinpira_sitappa -> sound_voicer sex (ชาย 3  |
| Evil-Eyed Boy | male | medium | name | talk.bin | 4 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Evil-Eyed Boy |
| Shusuke | male | high | dossier | talk.bin | 4 | evidence.bin — Shusuke: A boy left in front of an orphanage by his mother. Loves banana ic |
| Girl with Short Hair | female | high | name+role | talk.bin | 4 | Girl with Short Hair |
| Tanago | male | high | voicer | talk.bin | 4 | sound_voicer.bin: sex=1 |
| Man Talking to Himself | male | medium | name | talk.bin | 4 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Man Talking to Himself |
| Man Over the Phone | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_m01_00400_phone_man -> sound_voicer sex (ชาย 2 : หญิง 0) · |
| Thug on the Ground | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_g_m_btl12_020_020_shknm_guttari_rk -> sound_voicer sex (ชา |
| Hard-Faced Man | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_m01_02000_ikatsui_man -> sound_voicer sex (ชาย 2 : หญิง 0) |
| Passerby | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_m01_03400_passer01 -> sound_voicer sex (ชาย 2 : หญิง 0) ·  |
| Man in Shades | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_dlc_m01_01100_gurasan -> sound_voicer sex (ชาย 3 : หญิง 0) |
| Bartender | male | high | voicer | sound_auth.bin(talker) | 4 | sound_voicer.bin: sex=1 |
| Strong Thug | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_dgmb3030040_gorotsuki_gori -> sound_voicer sex (ชาย 2 : หญ |
| Bitter Thug | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_m05_01000_iyami_hangure -> sound_voicer sex (ชาย 2 : หญิง  |
| Violent Thug | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_m10_02200_sukoburu_hangure -> sound_voicer sex (ชาย 2 : หญ |
| Arcade Kid | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_m12_00700_gesen_boy -> sound_voicer sex (ชาย 2 : หญิง 0) · |
| Meek-Looking Yakuza | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_dlc_m02_02300_yakuza_kiyowa -> sound_voicer sex (ชาย 2 : ห |
| Busy Thug | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_g_m_g01_040_010_awatada_hangure -> sound_voicer sex (ชาย 2 |
| Straitlaced Thug | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_g_m_g01_040_030_majime_chinpira -> sound_voicer sex (ชาย 2 |
| Geomijul-Crashing RK Member | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_g_m_g10_020_040_komijyulu_rk -> sound_voicer sex (ชาย 2 :  |
| Nishio's Minion | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_dgmb4020010_chinpira_teshita -> sound_voicer sex (ชาย 2 :  |
| Gun-Toting Punk | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_dlc_g_m_btl04_020_080_chinpira_gun -> sound_voicer sex (ชา |
| Blonde Hostess | female | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_dlc_m01_00600_caba_gold -> sound_voicer sex (ชาย 0 : หญิง  |
| College Kid | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_dlc_m02_00750_male_univ -> sound_voicer sex (ชาย 2 : หญิง  |
| Hostess's Voice | female | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_dlc_g02_020_cab_televoice -> sound_voicer sex (ชาย 0 : หญิ |
| Young Businessman | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_dlc_m03_00900_salary_man -> sound_voicer sex (ชาย 2 : หญิง |
| Middle-Aged Businessman | male | high | voice_cue | sound_auth.bin(talker) | 4 | sound_auth.bin: คิวเสียง speech_dlc_m03_00900_salary_old -> sound_voicer sex (ชาย 2 : หญิง |
| g01_kaito | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| blondhair_man | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| dlc_m02_momoko | female | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=2 |
| irie | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| door_chinpira | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| dlc_m02_tencho | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| sayaka | female | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=2 |
| drama_m32_onitake | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| tender_master | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| charles_boy | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| drama_m14_suou | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| drama_m04_maria | female | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=2 |
| togari_hangure | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| takano | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| kuniko | female | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=2 |
| drama_m04_yagami | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| drama_m04_noriduki | female | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=2 |
| drama_m31_yagami | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| drama_m34_fudou | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| drama_m23_doumu | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| drama_m11_hanasaki | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| drama_m14_yagami | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| g_m_g999_tsukumo | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| side_m99_yagami | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| side_ptc63_yagami | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| side_ptc94_tsukino | female | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=2 |
| side_ptc96_yagami | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| side_ptc96_emiri | female | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=2 |
| side_ptc97_emiri | female | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=2 |
| side_ptc99_kyoko | female | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=2 |
| dlc_g_m_g02_kaito | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| dlc_m01_igarashi | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| dlc_m01_hoshino | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| dlc_g02_kaito | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| dlc_m02_maho | female | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=2 |
| dlc_m02_aragaki | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| dlc_m04_higashi | male | high | voicer | sound_auth.bin | 4 | sound_voicer.bin: sex=1 |
| Shellac Bartender | male | high | voicer | talk.bin | 3 | sound_voicer.bin: sex=1 |
| Lunch Lady | female | high | name+role | talk.bin | 3 | Lunch Lady |
| Old Man | male | medium | name | talk.bin | 3 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Old Man |
| The Payback Boxer | male | high | voicer | talk.bin | 3 | sound_voicer.bin: sex=1 |
| Broadsword-Wielding Old Man | male | medium | name | talk.bin | 3 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Broadsword-Wielding Old Man |
| Quiet-Looking Student | male | high | voice_cue | talk.bin | 3 | sound_auth.bin: คิวเสียง speech_drama_m21_020_kurumazaki -> sound_voicer sex (ชาย 2 : หญิง |
| Melancholy Woman | female | medium | name | talk.bin | 3 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Melancholy Woman |
| Female Customer | female | high | voice_cue | talk.bin | 3 | sound_auth.bin: คิวเสียง speech_side_ptc08_0010_customer_woman -> sound_voicer sex (ชาย 0  |
| Ass Catchem | male | high | dossier | talk.bin | 3 | evidence.bin — Ass Catchem: Former athlete who targets women, groping their posteriors and |
| Brown-Haired Young Man | male | medium | name | talk.bin | 3 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Brown-Haired Young Man |
| Female Sightseer | female | medium | name | talk.bin | 3 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Female Sightseer |
| Sharp-Dressed Man | male | medium | name | talk.bin | 3 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Sharp-Dressed Man |
| Portly Man | male | medium | name | talk.bin | 3 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Portly Man |
| Fujiwara | male | high | dossier | talk.bin | 3 | evidence.bin — Makito Fujiwara: A member of the Seiryo High eSports Club. He is one of the |
| Uozumi | male | high | dossier | talk.bin | 3 | evidence.bin — Katsuto Uozumi: A member of the Seiryo High eSports Club. He is one of the  |
| Hasegawa | female | high | pronoun | talk.bin | 3 | Hasegawa-sensei had something come up, so instead of going out with her, Hakase-san is get |
| Hotel Watchman | male | high | voice_cue | sound_auth.bin(talker) | 3 | sound_auth.bin: คิวเสียง speech_dlc_g_m_btl03_050_020_mihari_heya -> sound_voicer sex (ชาย |
| Delivery Driver | male | high | voice_cue | sound_auth.bin(talker) | 3 | sound_auth.bin: คิวเสียง speech_m11_01900_untensyu -> sound_voicer sex (ชาย 3 : หญิง 0) ·  |
| RK Storage Guard | male | high | voice_cue | sound_auth.bin(talker) | 3 | sound_auth.bin: คิวเสียง speech_m13_02200_soukoban_rk -> sound_voicer sex (ชาย 2 : หญิง 0) |
| Rowdy Soccer Player | male | high | voice_cue | sound_auth.bin(talker) | 3 | sound_auth.bin: คิวเสียง speech_drama_m04_400_soccer_guy1 -> sound_voicer sex (ชาย 2 : หญิ |
| Picked-on Thug | male | high | voice_cue | sound_auth.bin(talker) | 3 | sound_auth.bin: คิวเสียง speech_g_m_g01_010_037_yatsuatari_chinpira -> sound_voicer sex (ช |
| Knowledgable Thug | male | high | voice_cue | sound_auth.bin(talker) | 3 | sound_auth.bin: คิวเสียง speech_g_m_g05_010_030_jijou_hangure -> sound_voicer sex (ชาย 2 : |
| Annoyed Punk | male | high | voice_cue | sound_auth.bin(talker) | 3 | sound_auth.bin: คิวเสียง speech_dlc_g_m_btl03_030_030_chinpira_oko -> sound_voicer sex (ชา |
| Brown-Haired Thug | male | high | voice_cue | sound_auth.bin(talker) | 3 | sound_auth.bin: คิวเสียง speech_dlc_m03_01000_chinpira_brown -> sound_voicer sex (ชาย 2 :  |
| side_ptc97_yagami | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| dlc_m01_chinpira_ago | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m33_sakuma | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| syatyu_hangure | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| bottakuri_master | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| g02_yagami | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m91_amasawa | female | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=2 |
| g04_hoshino | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| mikoshiba | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| mamiya_jr | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| g08_yagami | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| fat_hangure | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| g09_sugiura | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| pcoat | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m23_yagami | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m04_girl_1stgrade | female | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=2 |
| drama_m04_girl_2ndgrade | female | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=2 |
| drama_m32_mikimoto | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m32_sakuma | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m33_todoroki | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m34_yagami | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| dlc_m02_fudou | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m34_kenya | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m23_takamori | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m23_kurumazaki | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m91_koga | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m91_takanashi | female | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=2 |
| drama_m91_doumu | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m11_asama | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m13_yagami | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m14_asama | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| drama_m14_haruna | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| side_ptc17_yagami | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| g_m_g07_yagami | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| g_g_g01_yagami | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| side_ptc63_amasawa | female | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=2 |
| side_ptc72_yagami | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| side_ptc93_yagami | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| side_ptc93_tsukino | female | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=2 |
| side_ptc94_yagami | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| dlc_g_m_g03_jun | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| dlc_m02_hotta | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| dlc_m03_nishio | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| dlc_m04_female_masuda | female | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=2 |
| dlc_m04_kyoya | male | high | voicer | sound_auth.bin | 3 | sound_voicer.bin: sex=1 |
| Gyu-Kaku Hostess | female | high | name+role | talk.bin | 2 | Gyu-Kaku Hostess |
| Mild-Mannered Teacher | male | medium | pronoun | talk.bin | 2 | Are you sure about this? A mild-mannered teacher like him? |
| Shaggy-Haired Young Man | male | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Shaggy-Haired Young Man |
| Yagami & Kaito | male | high | voicer | talk.bin | 2 | sound_voicer.bin: sex=1 |
| Man with Side-Part | male | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Man with Side-Part |
| Hooded Man | male | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Hooded Man |
| Refreshing Young Man | male | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Refreshing Young Man |
| Short-Haired Young Man | male | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Short-Haired Young Man |
| Katana-Wielding Old Man | male | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Katana-Wielding Old Man |
| Troubled Woman | female | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Troubled Woman |
| Relieved Woman | female | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Relieved Woman |
| Girl's Voice | female | high | name+role | talk.bin | 2 | Girl's Voice |
| Manato's Mom | female | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Manato's Mom |
| Mako-chan's Mom | female | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Mako-chan's Mom |
| Comedians | female | medium | role | talk.bin | 2 | Why don't you partner up with your mom? I can think of a few manzai comedians who are fami |
| Yagami & Minato | female | high | voicer | talk.bin | 2 | sound_voicer.bin: sex=2 |
| Girl with Eye Mole | female | high | name+role | talk.bin | 2 | Girl with eye mole |
| Male Sightseer | male | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Male Sightseer |
| Bespectacled Man | male | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Bespectacled Man |
| Gaudy Company Man | male | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Gaudy Company Man |
| Drunk Middle-Aged Man | male | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Drunk Middle-Aged Man |
| Yum | male | medium | pronoun | talk.bin | 2 | Heh, he gotcha good. Wouldn't expect nothin' less of Yum. Want some advice, once that ring |
| Male Student | male | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Male Student |
| Koga Underling | male | high | voice_cue | talk.bin | 2 | sound_auth.bin: คิวเสียง speech_drama_m91_120_koga_subordinate -> sound_voicer sex (ชาย 1  |
| Boy with Microphone | male | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Boy with Microphone |
| Neatly-Dressed Lady | female | high | name+role | talk.bin | 2 | Neatly-Dressed Lady |
| Sasamoto | female | high | dossier | talk.bin | 2 | evidence.bin — Michiko Sasamoto: The chairwoman of the PTA. She despises games, and is app |
| Hazama | male | medium | pronoun | talk.bin | 2 | Kill him? You serious, Hazama-san? |
| Male Witness | male | medium | name | talk.bin | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Male Witness |
| Scared Mother | female | high | name+role | talk.bin | 2 | Scared Mother |
| Pissed-Off RK | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_gmb_13050020_warehouse_rk_fukigen -> sound_voicer sex (ชาย |
| Dice Shaker | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_m01_00500_tsubofuri -> sound_voicer sex (ชาย 1 : หญิง 0) · |
| Beefy Thug | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_dlc_g_m_g03_020_070_chinpira_gori -> sound_voicer sex (ชาย |
| Seiryo High Security | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_m01_03500_shuei -> sound_voicer sex (ชาย 1 : หญิง 0) · voi |
| Junior Detective | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_dlc_g_m_g02_030_010_clerk_kouhai -> sound_voicer sex (ชาย  |
| Student 1 | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_drama_m24_060_yajiuma_stdnt1 -> sound_voicer sex (ชาย 1 :  |
| Distressed Woman | female | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_dlc_g_g_g03_020_030_female_nanpa -> sound_voicer sex (ชาย  |
| Tumbling Thug | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_m12_01200_korobi_hangure -> sound_voicer sex (ชาย 1 : หญิง |
| Tsurukame Passerby | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_m13_02150_tsurukame_passer01 -> sound_voicer sex (ชาย 1 :  |
| Delinquent | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_btl02_020_020_furyo -> sound_voicer sex (ชาย 2 : หญิง 0) · |
| Boxer | male | high | voicer | sound_auth.bin(talker) | 2 | sound_voicer.bin: sex=1 |
| Student 2 | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_drama_m24_060_yajiuma_stdnt2 -> sound_voicer sex (ชาย 1 :  |
| Rooftop RK | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_g_m_btl12_020_120_shiknm_okujo_rk -> sound_voicer sex (ชาย |
| Suspicious RK | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_g_m_btl12_020_160_shiknm_ayashi_rk -> sound_voicer sex (ชา |
| RK Underling | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_g_m_btl12_020_160_shiknm_otomo_rk02 -> sound_voicer sex (ช |
| Tough-Looking RK | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_g_m_btl13_050_100_warehouse_rk_boss -> sound_voicer sex (ช |
| Surprised Thug | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_g_m_g01_040_010_odoroku_hangure -> sound_voicer sex (ชาย 1 |
| Gentleman Host | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_dlc_m01_00600_male_host -> sound_voicer sex (ชาย 1 : หญิง  |
| New Recruit | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_dlc_g02_010_yakuza_sitappa -> sound_voicer sex (ชาย 1 : หญ |
| Burly Thug | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_dlc_m02_00210_gorotsuki_gatai -> sound_voicer sex (ชาย 1 : |
| Soldierly Thug | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_dlc_m02_00900_chinpira_syatei -> sound_voicer sex (ชาย 1 : |
| Smoking Businessman | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_dlc_m02_01410_salary_smoke -> sound_voicer sex (ชาย 1 : หญ |
| Gindaco Employee | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_dlc_m02_01410_staff_tako -> sound_voicer sex (ชาย 1 : หญิง |
| Young Alumnus 2 | male | high | voice_cue | sound_auth.bin(talker) | 2 | sound_auth.bin: คิวเสียง speech_dlc_m04_01150_ob_02 -> sound_voicer sex (ชาย 1 : หญิง 0) · |
| Rubbernecking Young Man | male | medium | name | auth.bin(cinema_telop) | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Rubbernecking Young Man |
| Rubbernecking Woman | female | medium | name | auth.bin(cinema_telop) | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Rubbernecking Woman |
| Bullied Girl | female | high | name+role | auth.bin(cinema_telop) | 2 | Bullied Girl |
| Whispery Woman | female | medium | name | auth.bin(cinema_telop) | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Whispery Woman |
| Gossipy Woman | female | medium | name | auth.bin(cinema_telop) | 2 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Gossipy Woman |
| ja20130_akutsu | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| ja20130_ikatsui_hangure | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| ja20135_akutsu | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| ja20135_ikatsui_hangure | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| jh80630_souma | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| jh80540_kuwana | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| jh80590_wanatabe | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| jh80560_akutsu | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| mihari_chinpira | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| longhair_man | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| phone_man | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| tsubofuri | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g_m_g03_chinpira_gori | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g01_kosuke | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| garawaru_man | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| ikatsui_man | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| youshoku | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m02_takanashi | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| shuei | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g01_youmuin | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_catch_kisaku | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m11_suou | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g01_tsukumo | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| yakkun | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g_m_g02_clerk_kouhai | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| kento | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| bucho_basket | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| omonaga_basket | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| sobakasu_basket | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| dgmb3030040_gorotsuki_gori | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| iyami_hangure | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| tamari_uketsuke | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g05_yagami | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_staff_young | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| chara_hangure | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g08_kaito | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| yokomichi | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g09_yagami | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g09_tsukumo | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g09_sawa | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| station_passer | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g10_yagami | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| araburu_hangure | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| sukoburu_hangure | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g_g_g03_female_nanpa | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| gesen_boy | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| korobi_hangure | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| soukoban_rk | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| furyo | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m04_basketball_guy | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m04_emcee | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m04_amasawa | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| drama_m31_boxer | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m31_onitake | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m33_mikimoto | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m33_referee | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m33_yagami | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m34_honda | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m23_dento | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m24_akuta | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| drama_m91_suou | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m91_kenya | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m91_dento | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m91_hanasaki | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m91_rina | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| drama_m91_sakuma | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m11_akatsuka | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m12_rabuho | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| drama_m13_asama | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m13_haruna | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m13_ghost | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m13_seyama | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m14_regent | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m14_seyama | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m14_matatabi | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m14_suou_mother | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| drama_m14_ghost | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m14_hanasaki | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| drama_m14_rina | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| side_ptc17_minato | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| side_m17_yagami | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_yakuza_kiyowa | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| side_m19_minato | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| g_m_g07_susannda_rk | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g_g_kaito | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g_g_sugiura | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| jh28020_jun | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g_m_warehouse_rk_boss | male | high | voice_cue (ยืมจาก "Tough-Looking RK" — ชื่อเดียวกันสะกดคนละแบบ) | sound_auth.bin | 2 | sound_auth.bin: คิวเสียง speech_g_m_btl13_050_100_warehouse_rk_boss -> sound_voicer sex (ช |
| g_m_g01_kaito | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g_g_g01_kaito | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g_m_g01_kosuke | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g_m_g01_awatada_hangure | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g_m_g01_odoroku_hangure | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g_m_g01_sabori_chinpira | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g_m_g01_majime_chinpira | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g_m_g05_fuman_hangure | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g_m_g05_jijou_hangure | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g_m_g05_rankf_chimpira | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g_m_g05_rankd_chimpira | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g_m_g05_bartender | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| side_m94_tsukino | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| g_m_g05_yoitai_rk | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| g_m_g10_komijyulu_rk | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| side_m100_yagami | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| side_m100_kyoko | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| side_m100_cherry | female | high | dossier (ยืมจาก "Cherry" — ชื่อเดียวกันสะกดคนละแบบ) | sound_auth.bin | 2 | evidence.bin — Cherry: She's the cat Hakase-san is taking care of. |
| side_m101_kyoko | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| side_m93_yagami | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| side_m93_tsukino | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| side_m95_tsukino | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| side_m96_yagami | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| side_m96_emiri | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| side_m98_emiri | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| side_m99_kyoko | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| side_ptc08_customer_woman | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| dlc_g_m_chinpira_oko | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dgmb4020010_chinpira_teshita | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g_g_g03_kaito | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g_g_g03_jun | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g_m_g03_chinpira_nanpa | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m01_senda | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m01_female_irai | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| dlc_m01_tsukumo | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m01_caba_gold | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| dlc_m01_male_host | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m01_mari | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| dlc_m01_tender_master | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m01_kyoya | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m01_mikiko | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| dlc_m01_jun | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m01_gurasan | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m01_female_bite | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| dlc_m02_jersey_yakuza | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g02_mikiko | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| dlc_g02_maho | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| dlc_g02_yakuza_sitappa | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g02_yakuza_panic | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_higashi | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_chinpira_drunk | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_gorotsuki_gatai | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_male_univ | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g02_staff_young | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g02_aragaki | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g02_customer_lost | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_chinpira_syatei | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_chinpira_gold | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_kyoya | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_female_staff | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| dlc_m02_salary_smoke | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_staff_hat | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| dlc_m02_staff_tako | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_ryan | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_igarashi | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g02_cab_televoice | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| dlc_g02_kyuusyuu_staff | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_staff_moving | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m02_nishio | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g03_kaito | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g03_jun | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g03_shirakaba | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m03_salary_man | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m03_salary_old | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m03_chinpira_short | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m03_kyoya | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m03_police_hard | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m03_tsukumo | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g03_female_hade | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| dlc_m03_senda | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m04_tsukumo | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m04_hoshino | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m04_police_hard | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g04_kaito | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g04_igarashi | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g04_senda | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g04_man_lost | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g04_veteran_boy | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g04_panic_boy | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_g04_care_boy | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m04_tashiro | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m04_female_recep | female | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=2 |
| dlc_m04_male_boy | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| dlc_m04_kenmochi | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| jh28020_kaito | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| jh80680_kenmochi | male | high | voicer | sound_auth.bin | 2 | sound_voicer.bin: sex=1 |
| Yagami & Amasawa | female | high | voicer | talk.bin | 1 | sound_voicer.bin: sex=2 |
| Spirited Girl | female | high | name+role | talk.bin | 1 | Spirited Girl |
| Man in Green Jacket | male | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Man in Green Jacket |
| Perverts | male | high | pronoun+role | talk.bin | 1 | Once a pariah among perverts, now a giant among men. Lesser perverts revere him as a king. |
| Woman in Sailor Suit | female | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Woman in Sailor Suit |
| Doppelganger Ryan | male | high | voicer | talk.bin | 1 | sound_voicer.bin: sex=1 |
| Male Onlooker | male | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Male Onlooker |
| Female Onlooker | female | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Female Onlooker |
| Male Employee | male | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Male Employee |
| Tanned Young Man | male | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Tanned Young Man |
| Shimada's Father | male | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Shimada's Father |
| Old Woman's Voice | female | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Old Woman's Voice |
| Short-Haired Schoolboy | male | high | name+role | talk.bin | 1 | Short-Haired Schoolboy |
| Ingratiating Man | male | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Ingratiating Man |
| Curly-Haired Man | male | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Curly-Haired Man |
| Otaku-ish Man | male | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Otaku-ish Man |
| Delinquents | male | high | pronoun+role | talk.bin | 1 | Our nemesis, the Professor, must be stopped. He sneaks his way into the hearts of innocent |
| Thuggish Man | male | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Thuggish Man |
| Earphones | male | medium | role | talk.bin | 1 | Thanks, you're a nice guy. These are just earphones. Hehe. |
| Brown-Haired College Girl | female | high | name+role | talk.bin | 1 | Brown-Haired College Girl |
| Cool-Looking Boy | male | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Cool-Looking Boy |
| Man That Looks Like Hayakawa | female | high | voicer | talk.bin | 1 | sound_voicer.bin: sex=2 |
| Woman's Voice | female | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Woman's Voice |
| Short-Haired Woman | female | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Short-Haired Woman |
| Possibly-Homeless Man | male | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Possibly-Homeless Man |
| Black-Haired Woman | female | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Black-Haired Woman |
| Flashy Guy | male | high | name+role | talk.bin | 1 | Not quite. The flashy guy in gold on Hamakita Park Avenue will clue you in. |
| Intelligent-Looking Man | male | medium | name | talk.bin | 1 | ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: Intelligent-Looking Man |
| Client | male | medium-conflict | majority(11:1) | talk.bin | 1 | Apparently, the "Illegal Detective Agency" was hired to investigate a client's husband, as |
| System | male | high | pronoun | talk.bin | 1 | But because he lacked the evidence, the system more or less spit him out. |
| Made In Heaven | male | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_drama_m91_150_asama -> sound_voicer sex (ชาย 1 : หญิง 0) · |
| RK Companion | male | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_g_m_btl12_020_160_shiknm_otomo_rk01 -> sound_voicer sex (ช |
| Guest at Next Table | male | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_m11_01700_tonari_kyaku01 -> sound_voicer sex (ชาย 1 : หญิง |
| Guest 2 Tables Down | male | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_m11_01700_tonari_kyaku02 -> sound_voicer sex (ชาย 1 : หญิง |
| Guest 3 Tables Down | male | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_m11_01700_tonari_kyaku03 -> sound_voicer sex (ชาย 1 : หญิง |
| Falling Thug | male | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_m12_01300_taore_hangure -> sound_voicer sex (ชาย 1 : หญิง  |
| Tsurukame Pedestrian | female | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_m13_02150_tsurukame_passer02 -> sound_voicer sex (ชาย 0 :  |
| Neurotic-Looking Teacher | female | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_drama_m24_060_nervous_teacher -> sound_voicer sex (ชาย 0 : |
| Gangly Punk | male | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_drama_m91_290_chinpira_gatai -> sound_voicer sex (ชาย 1 :  |
| Bikers | male | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_drama_m14_470_asama -> sound_voicer sex (ชาย 1 : หญิง 0) · |
| Man's Yell | male | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_g_m_g07_025_050_man_rk -> sound_voicer sex (ชาย 1 : หญิง 0 |
| Pursuing RK Member | male | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_gmb_13050060_warehouse_rk_chaser -> sound_voicer sex (ชาย  |
| Thug Loyal to Aniki | male | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_g_m_g01_010_037_anikiomoi_chinpira -> sound_voicer sex (ชา |
| Hurrying Punk | male | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_dlc_g_m_btl03_030_020_chinpira_hurry -> sound_voicer sex ( |
| Stern Man | male | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_dlc_g_m_btl04_020_030_debu_ikatsu -> sound_voicer sex (ชาย |
| Agitated Thug | male | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_dgmb4020060_gorotsuki_high -> sound_voicer sex (ชาย 1 : หญ |
| Senior Detective | male | high | voice_cue | sound_auth.bin(talker) | 1 | sound_auth.bin: คิวเสียง speech_dlc_g_m_g02_030_010_clerk_senpai -> sound_voicer sex (ชาย  |
| jb50080_souma | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_g_m_mihari_heya | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m13_ootsuki | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| g_m_shknm_guttari_rk | male | high | voice_cue (ยืมจาก "Thug on the Ground" — ชื่อเดียวกันสะกดคนละแบบ) | sound_auth.bin | 1 | sound_auth.bin: คิวเสียง speech_g_m_btl12_020_020_shknm_guttari_rk -> sound_voicer sex (ชา |
| dlc_g01_senda | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m34_mikimoto | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| pe_teacher | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m91_asama | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m91_haruna | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| g03_yagami | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| g_m_kuwana | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| jm71000_bik_win_hana_hanasaki | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_m04_male_guren | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m02_itokura | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| female_caster | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| comijurumen | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| namaiki_hanpin | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| untensyu | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| taore_hangure | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| mototojo_hangure | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| gotsui_mototojo | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| old_mitsuru | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m04_sayaka | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| drama_m31_kenya | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m31_iwashita | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_m04_nishio | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m34_sakuma | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m34_onitake | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| jm71030_bik_win_suoh_suou | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m34_kento | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m34_amasawa | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| drama_m21_yagami | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m24_nervous_teacher | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| drama_m24_robo_emcee | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m91_koga_subordinate | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m91_kurumazaki | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m91_sayaka | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| drama_m91_takamori | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m91_girl_1stgrade | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| drama_m91_girl_2ndgrade | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| drama_m91_maria | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| drama_m91_todoroki | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m91_chinpira_sitappa | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m91_chinpira_gatai | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m11_kanesugi | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m12_asama | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m11_matatabi | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m11_seyama | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m12_yagami | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m12_rina | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| jm71010_bik_win_rina_rina | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| drama_m13_akatsuka | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m13_mikidaka | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| drama_m14_rabuho | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| side_m17_minato | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| drama_m02_amasawa | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| drama_m02_yagami | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| g_m_g04_kaito | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| g_m_g04_yagami | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| g_m_g07_man_rk | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| g_m_shiknm_okujo_rk | male | high | voice_cue (ยืมจาก "Rooftop RK" — ชื่อเดียวกันสะกดคนละแบบ) | sound_auth.bin | 1 | sound_auth.bin: คิวเสียง speech_g_m_btl12_020_120_shiknm_okujo_rk -> sound_voicer sex (ชาย |
| g_m_shiknm_ayashi_rk | male | high | voice_cue (ยืมจาก "Suspicious RK" — ชื่อเดียวกันสะกดคนละแบบ) | sound_auth.bin | 1 | sound_auth.bin: คิวเสียง speech_g_m_btl12_020_160_shiknm_ayashi_rk -> sound_voicer sex (ชา |
| g_m_g01_sakura_kosuke_frnd | male | medium-conflict | voice_cue(majority 33:9) (ยืมจาก "Sakura" — ชื่อเดียวกันสะกดคนละแบบ) | sound_auth.bin | 1 | sound_auth.bin: คิวเสียง speech_drama_m23_060_dento -> sound_voicer sex (ชาย 33 : หญิง 9)  |
| g_m_g01_anikiomoi_chinpira | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| g_m_g01_yatsuatari_chinpira | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| g_g_g05_yagami | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| g_g_g10_yagami | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| side_m94_yagami | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| side_m97_yagami | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| side_m97_emiri | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| side_ptc08_robbery | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| jm71000_bik_win_hana_yagami | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| jm71000_bik_win_hana_suou | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| jm71010_bik_win_rina_yagami | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| jm71020_bik_win_ghost_yagami | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| jm71020_bik_win_ghost_ghost | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_g_m_chinpira_hurry | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_g_m_debu_ikatsu | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dgmb4020040_chinpira_tanki | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dgmb4020060_gorotsuki_high | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_g_m_chinpira_gun | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| jh80710_kaito | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_skill_kaito | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_g_m_g02_clerk_senpai | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_g_g_g03_chinpira_nanpa | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_g02_hotta | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_m02_chinpira_red | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_m02_kenmochi | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_m03_chinpira_brown | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_g03_kenmochi | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_g04_female_recep | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| dlc_g04_young_boy | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_g04_normal_boy | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |
| dlc_m04_female_dress | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| dlc_m04_friends_dress | female | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=2 |
| dlc_kaito | male | high | voicer | sound_auth.bin | 1 | sound_voicer.bin: sex=1 |

## ยังพิสูจน์ไม่ได้ — ต้องแปลกลางเพศ (เรียงตามจำนวนบรรทัด)

| ผู้พูด | พบใน | บรรทัด | สถานะ |
|---|---|---|---|
| Ogikubo | talk.bin | 77 | conflict |
| Student Who Dropped Something | talk.bin | 60 | none |
| Hanamizuki | talk.bin | 51 | none |
| Hiyori | talk.bin | 40 | none |
| Casino Staff | talk.bin | 36 | none |
| Milkee | talk.bin | 33 | none |
| Yagamo | talk.bin | 32 | none |
| Mahjong Player | talk.bin | 32 | none |
| Ikeyama | talk.bin | 30 | none |
| Futaba | talk.bin | 30 | conflict |
| Mikio | talk.bin | 29 | none |
| Poppo Cashier | talk.bin | 27 | none |
| Ebisu Pawn Broker | talk.bin | 27 | none |
| Shopkeep | talk.bin | 26 | none |
| Guide | talk.bin | 25 | none |
| Old Person | talk.bin | 25 | none |
| Goto | talk.bin | 22 | conflict |
| Takeyan | talk.bin | 21 | none |
| Seiryoin | talk.bin | 21 | none |
| Thug with Gun | auth.bin(cinema_telop) | 21 | none |
| Firefighter A | auth.bin(cinema_telop) | 20 | none |
| Mean-Looking Thug | auth.bin(cinema_telop) | 20 | none |
| Anno | talk.bin | 19 | none |
| Golf Shop Receptionist | talk.bin | 19 | none |
| Cat | talk.bin | 18 | conflict |
| Drone Race Receptionist | talk.bin | 18 | none |
| Nekomiya | talk.bin | 17 | none |
| Evil-Eyed Punk | talk.bin | 15 | none |
| Intellectual College Student | talk.bin | 15 | none |
| Vista Mahjong Cashier | talk.bin | 15 | none |
| Unsavory Scout | talk.bin | 13 | none |
| Remi | talk.bin | 13 | none |
| Coconut | talk.bin | 13 | none |
| Tsurukame Policeman | auth.bin(cinema_telop) | 13 | none |
| Mikan | talk.bin | 12 | none |
| Juzo | talk.bin | 12 | none |
| ??? | talk.bin | 12 | none |
| Sofiya | talk.bin | 12 | none |
| Nasty Drunk | talk.bin | 12 | none |
| Fisherman | talk.bin | 12 | none |
| Mamiya (age 18) | auth.bin(cinema_telop) | 12 | none |
| Hustle Boutique Shopkeep | talk.bin | 11 | none |
| Creepy Youth | talk.bin | 11 | none |
| Moriwaki | talk.bin | 11 | none |
| Curly-Haired Yakuza | talk.bin | 11 | none |
| Wette Kitchen Cashier | talk.bin | 10 | none |
| Unsavory Barker | talk.bin | 10 | none |
| Akaike (age 18) | auth.bin(cinema_telop) | 10 | none |
| Employee | talk.bin | 9 | conflict |
| Punk in Black | talk.bin | 9 | none |
| Exchanger | talk.bin | 9 | none |
| Mikuru | talk.bin | 9 | conflict |
| Okachimachi | talk.bin | 8 | none |
| Unsavory Punk | talk.bin | 8 | none |
| Driver | talk.bin | 8 | none |
| Gudo | talk.bin | 8 | none |
| Kibayashi | talk.bin | 8 | none |
| Katashina | talk.bin | 8 | none |
| Runner | talk.bin | 8 | none |
| Club SEGA Staff | talk.bin | 8 | none |
| Nana's Teacher | talk.bin | 8 | none |
| Student | sound_auth.bin(talker) | 8 | none |
| Firefighter B | auth.bin(cinema_telop) | 8 | none |
| Master | talk.bin | 7 | conflict |
| Injured Student | talk.bin | 7 | none |
| Suspicious Old-Timer | talk.bin | 7 | none |
| Mahjong Baron | talk.bin | 7 | none |
| Kawashita | talk.bin | 7 | none |
| Support Thug | auth.bin(cinema_telop) | 7 | none |
| Akaushimaru Server | talk.bin | 6 | none |
| Yoshida | talk.bin | 6 | none |
| Batting Center Manager | talk.bin | 6 | none |
| Soccer Club Member | talk.bin | 6 | none |
| Takiguchi | talk.bin | 6 | none |
| Blue Ninja | talk.bin | 6 | none |
| Red-Haired Delinquent | talk.bin | 6 | none |
| Chatter Post | talk.bin | 6 | none |
| Matsunaga | talk.bin | 6 | none |
| Raging Punk | talk.bin | 6 | none |
| Shinanogawa | talk.bin | 6 | none |
| Fake Shinonome | talk.bin | 6 | none |
| Exercise Lover | talk.bin | 6 | none |
| Wild Jackson Cashier | talk.bin | 5 | none |
| Café Staff | talk.bin | 5 | none |
| Meek-Looking Student | talk.bin | 5 | none |
| Smile Burger Cashier | talk.bin | 5 | none |
| Taxi Driver | talk.bin | 5 | none |
| Ayame | talk.bin | 5 | none |
| Red Ninja | talk.bin | 5 | none |
| Bespectacled Youth | talk.bin | 5 | none |
| Fox | talk.bin | 5 | none |
| Camera-Carrying Student | talk.bin | 5 | none |
| Thug in Black | talk.bin | 5 | none |
| Mitsuru (age 18) | auth.bin(cinema_telop) | 5 | none |
| seiryo_student | sound_auth.bin | 5 | none |
| Café Alps Staff | talk.bin | 4 | none |
| Yoronotaki Host | talk.bin | 4 | none |
| Café Mijore Cashier | talk.bin | 4 | none |
| Komai | talk.bin | 4 | none |
| Nervous-Looking Teacher | talk.bin | 4 | none |
| Robber? | talk.bin | 4 | none |
| Pompadoured Delinquent | talk.bin | 4 | none |
| Long-Haired Punk | talk.bin | 4 | none |
| Receptioninja | talk.bin | 4 | none |
| Short-Haired Businessman | talk.bin | 4 | none |
| Excited Youth | talk.bin | 4 | none |
| Students | talk.bin | 4 | conflict |
| Brown-Haired Student | talk.bin | 4 | none |
| Sasaki Arcade Staff | talk.bin | 4 | none |
| Kaino | talk.bin | 4 | none |
| Small Student | talk.bin | 4 | none |
| Punk with Spunk | talk.bin | 4 | none |
| Burger Shop Senpai | talk.bin | 4 | none |
| Burly RK Watchman | talk.bin | 4 | none |
| Onlooking Student | talk.bin | 4 | none |
| Well-Dressed Businessman | talk.bin | 4 | none |
| Scary-Faced Yakuza | talk.bin | 4 | none |
| Ex-Yakuza Thug | auth.bin(cinema_telop) | 4 | none |
| Camera Kid | auth.bin(cinema_telop) | 4 | none |
| passer | sound_auth.bin | 4 | none |
| drama_m24_yajiuma_stdnt | sound_auth.bin | 4 | none |
| dlc_m04_ob | sound_auth.bin | 4 | none |
| Bantam Master | talk.bin | 3 | none |
| Sushi Gin Staff | talk.bin | 3 | none |
| Le Marche Sales Associate | talk.bin | 3 | none |
| M Side Cafe Employee | talk.bin | 3 | none |
| Survive Staff | talk.bin | 3 | none |
| Eomeoni's Vow Cashier | talk.bin | 3 | none |
| Earth Angel Mama | talk.bin | 3 | none |
| Meng Wu Owner | talk.bin | 3 | none |
| Pocket Café Employee | talk.bin | 3 | none |
| Mama | talk.bin | 3 | conflict |
| Bar Mama | talk.bin | 3 | none |
| School Shop Worker | talk.bin | 3 | none |
| Morio Onodera | talk.bin | 3 | none |
| Isamu Onodera | talk.bin | 3 | none |
| Hamakita Restaurant Host | talk.bin | 3 | none |
| Low-Level Biker | talk.bin | 3 | none |
| All-Ninja | talk.bin | 3 | none |
| Angry Voice | talk.bin | 3 | none |
| Riko | talk.bin | 3 | none |
| Long-Haired Delinquent | talk.bin | 3 | none |
| Lullaby Mahjong Cashier | talk.bin | 3 | none |
| Dance Club Member | talk.bin | 3 | none |
| Furious Citizen Group | talk.bin | 3 | none |
| Biker 2 | talk.bin | 3 | none |
| Young Teacher | talk.bin | 3 | none |
| Sakumoto | talk.bin | 3 | none |
| Ninomiya | talk.bin | 3 | none |
| Mi-chan | talk.bin | 3 | none |
| g_m_shiknm_otomo_rk | sound_auth.bin | 3 | none |
| tonari_kyaku | sound_auth.bin | 3 | none |
| tsurukame_passer | sound_auth.bin | 3 | none |
| Test Phone | talk.bin | 2 | none |
| Sushi Zanmai Cashier | talk.bin | 2 | none |
| Quadra Garden Cashier | talk.bin | 2 | none |
| Fuji Soba Cashier | talk.bin | 2 | none |
| Gindaco Highball Tavern Cashier | talk.bin | 2 | none |
| Kanrai Staff | talk.bin | 2 | none |
| Kotobuki Drugs Staff | talk.bin | 2 | none |
| Kinka Pharmacy Staff | talk.bin | 2 | none |
| Pharmacist | talk.bin | 2 | none |
| Traveling Vendor | talk.bin | 2 | none |
| la chatte blanche Sales Associate | talk.bin | 2 | none |
| Welcome Pharmacy Staff | talk.bin | 2 | none |
| The Bee Staff | talk.bin | 2 | none |
| Yoshinoya Cashier | talk.bin | 2 | none |
| Ikinari Steak Chef | talk.bin | 2 | none |
| Kappo Katsumi Mistress | talk.bin | 2 | none |
| Sweet Heaven Cashier | talk.bin | 2 | none |
| Beef Zone Host | talk.bin | 2 | none |
| Tokuro | talk.bin | 2 | none |
| You Tian Owner | talk.bin | 2 | none |
| Garçon | talk.bin | 2 | none |
| Chicken del sol Cashier | talk.bin | 2 | none |
| Gomi | talk.bin | 2 | none |
| Tome | talk.bin | 2 | none |
| Moroboshi | talk.bin | 2 | none |
| Michiyo | talk.bin | 2 | none |
| Drone Lab Associate | talk.bin | 2 | none |
| Kamulop 2 | talk.bin | 2 | none |
| Brown-Haired Businessman | talk.bin | 2 | none |
| Staff Member | talk.bin | 2 | none |
| Young Movie Buff | talk.bin | 2 | none |
| Manato | talk.bin | 2 | none |
| Automated Message | talk.bin | 2 | none |
| Superficial Youth | talk.bin | 2 | none |
| Bubbly Student | talk.bin | 2 | none |
| Cleaner | talk.bin | 2 | none |
| Kodama's Staff Member | talk.bin | 2 | none |
| Mikimoto's Minion | talk.bin | 2 | none |
| Body Model? | talk.bin | 2 | none |
| UFO Fanatic | talk.bin | 2 | none |
| Familiar Cat | talk.bin | 2 | none |
| First Responder | talk.bin | 2 | none |
| VR Receptionist | talk.bin | 2 | none |
| Hanasaki's Underling | talk.bin | 2 | none |
| Extreme Citizen Group | talk.bin | 2 | none |
| Biker 3 | talk.bin | 2 | none |
| Brawny Biker | talk.bin | 2 | none |
| Neo Keihin Punk | talk.bin | 2 | none |
| Raging Yakuza | talk.bin | 2 | none |
| Low-Ranking Yakuza | talk.bin | 2 | none |
| Picky RK Member | talk.bin | 2 | none |
| Curious-Looking Student | talk.bin | 2 | none |
| Short-Haired Delinquent | talk.bin | 2 | none |
| Red-Faced Businessman | talk.bin | 2 | none |
| Miu's Fan | talk.bin | 2 | none |
| Saitama | talk.bin | 2 | none |
| Kazamiya | talk.bin | 2 | none |
| Flashy Gal | talk.bin | 2 | none |
| Hikari | talk.bin | 2 | none |
| Recipient | talk.bin | 2 | none |
| Wandering High Schooler | talk.bin | 2 | none |
| Wayfarer's Lucky Cat | talk.bin | 2 | none |
| Blood-Drunk Master | talk.bin | 2 | none |
| Secretary | auth.bin(cinema_telop) | 2 | none |
| Student B | auth.bin(cinema_telop) | 2 | none |
| Student C | auth.bin(cinema_telop) | 2 | none |
| Terrace Guest | auth.bin(cinema_telop) | 2 | none |
| Chaser Thug | auth.bin(cinema_telop) | 2 | none |
| Court Reporter | auth.bin(cinema_telop) | 2 | none |
| Crushed Thug | auth.bin(cinema_telop) | 2 | none |
| drama_m04_soccer_guy | sound_auth.bin | 2 | none |
| Yagami & Kodama | talk.bin | 1 | none |
| Suspicious Person | talk.bin | 1 | none |
| Cat Statue | talk.bin | 1 | none |
| Sleepy Punk | talk.bin | 1 | none |
| Dog's Voice | talk.bin | 1 | none |
| Mari's Friend | talk.bin | 1 | none |
| Kamulop 1 | talk.bin | 1 | none |
| Kamulop 3 | talk.bin | 1 | none |
| Kamulop 4 | talk.bin | 1 | none |
| Brown Ninja | talk.bin | 1 | none |
| Blonde Kunoichi | talk.bin | 1 | none |
| Young Passerby | talk.bin | 1 | none |
| Young Pedestrian | talk.bin | 1 | none |
| Scared Voice | talk.bin | 1 | none |
| Older Movie Buff | talk.bin | 1 | none |
| Hoarse Voice | talk.bin | 1 | none |
| Ghost's Underling | talk.bin | 1 | none |
| Cheery Student | talk.bin | 1 | none |
| Pained Voice | talk.bin | 1 | none |
| Gentle Old-Timer | talk.bin | 1 | none |
| Neighbor's Voice | talk.bin | 1 | none |
| Exercise Buff | talk.bin | 1 | none |
| Tsuruno's Friend | talk.bin | 1 | none |
| Blond Delinquent | talk.bin | 1 | none |
| Biker 1 | talk.bin | 1 | none |
| Biker 4 | talk.bin | 1 | none |
| Biker 5 | talk.bin | 1 | none |
| Middle-Aged Biker Gang | talk.bin | 1 | none |
| Bespectacled College Student | talk.bin | 1 | none |
| Serious RK Watchman | talk.bin | 1 | none |
| Gym Member | talk.bin | 1 | none |
| Koga's Assistant | talk.bin | 1 | none |
| Koga's Crony | talk.bin | 1 | none |
| Kento's Voice | talk.bin | 1 | none |
| Photography Club President | talk.bin | 1 | none |
| RK | talk.bin | 1 | none |
| Booze-Craving RK Member | talk.bin | 1 | none |
| Chiyoda's Underling | talk.bin | 1 | none |
| Brown-Haired Biker | talk.bin | 1 | none |
| Bearded Businessman | talk.bin | 1 | none |
| Youth in Suit | talk.bin | 1 | none |
| Old Witness | talk.bin | 1 | none |
| Drunk Customer | talk.bin | 1 | none |
| Rookie Developer | talk.bin | 1 | none |
| Familiar Voice | talk.bin | 1 | none |
| Anxious-Looking Kid | talk.bin | 1 | none |
| Daydreaming Gambler | talk.bin | 1 | none |
| Lead Firefighter | auth.bin(cinema_telop) | 1 | none |
| White Mask | auth.bin(cinema_telop) | 1 | none |
| gmb_warehouse_rk_fukigen | sound_auth.bin | 1 | none |
| student | sound_auth.bin | 1 | none |
| gmb_warehouse_rk_chaser | sound_auth.bin | 1 | none |
