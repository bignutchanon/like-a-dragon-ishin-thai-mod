# หลักฐานเพศผู้พูด — Like a Dragon: Ishin!

สร้างโดย `scripts/build_speaker_gender.py` · **ทุกช่องมาจากไฟล์เกม ไม่มีการเดา**

⚠ ภาคนี้ไม่มีตารางเพศในไฟล์เกม (ตรวจครบ 244 ตาราง ARMP แล้วไม่มีคอลัมน์ sex/gender)
หลักฐานหลักจึงเป็น **ต้นฉบับญี่ปุ่นที่อยู่ใน pak เดียวกัน** — สรรพนามบุรุษที่หนึ่ง
และคำลงท้ายที่ผูกกับเพศแน่น ซึ่งฉบับอังกฤษตัดทิ้งหมด

เกณฑ์: ฝั่งที่ชนะต้องเจอ >= 3 ครั้ง และฝั่งตรงข้ามไม่เกิน 25% ของฝั่งที่ชนะ
ไม่ผ่านเกณฑ์ = `unknown` -> **แปลกลางเพศ ห้ามเดา**

| ผู้พูด | id คิว | เพศ | ที่มา | ช/ญ | บรรทัด ja | หลักฐาน |
|---|---|---|---|---|---:|---|
| Ryoma | `kiryu` | **male** | ja_markers | 270/1 | 2124 | สรรพนาม 俺 x214 · คำลงท้าย ぞ/ぜ x47 · คำเรียกฝ่ายตรงข้ามแบบชาย x6 · คำลงท้าย だろうが x2 |
| Employee | - | **unknown** | crowd_label | 0/6 | 946 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Hijikata | `hijikata` | **male** | ja_markers | 9/0 | 436 | คำลงท้าย ぞ/ぜ x3 · สรรพนาม わし (ชายสูงวัย) x2 · สรรพนาม 俺 x2 · คำลงท้าย だろうが x1 |
| Townsperson | - | **unknown** | crowd_label | 9/8 | 435 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Otose | `otose` | **female** | ja_markers | 0/3 | 412 | คำลงท้าย ないわ x3 |
| Takechi | `takechi` | **male** | ja_markers | 72/0 | 412 | สรรพนาม 俺 x70 · คำลงท้าย ぞ/ぜ x2 |
| Oryo | `oryo` | **female** | ja_markers_weak | 0/30 | 394 | สรรพนามคันไซหญิง うち x29 · คำลงท้าย のよ x1 |
| Okita | - | **male** | ja_markers | 13/1 | 325 | สรรพนาม わし (ชายสูงวัย) x11 · สรรพนาม 俺 x2 |
| Customer | - | **unknown** | crowd_label | 0/8 | 322 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Haruka | `haruka` | **unknown** | none | 0/0 | 297 | - |
| Kondo | `kondo` | **male** | ja_markers | 46/4 | 291 | สรรพนาม 俺 x34 · คำลงท้าย ぞ/ぜ x11 · สรรพนาม わし (ชายสูงวัย) x1 |
| id:majima | `majima` | **male** | ja_markers | 47/0 | 277 | สรรพนาม わし (ชายสูงวัย) x44 · สรรพนาม 俺 x2 · คำลงท้าย ぞ/ぜ x1 |
| Todo | `todo` | **male** | ja_markers | 23/0 | 235 | สรรพนาม 俺 x22 · สรรพนาม 僕 x1 |
| Nagakura | - | **male** | ja_markers | 18/0 | 208 | สรรพนาม 俺 x16 · คำลงท้าย ぞ/ぜ x1 · สรรพนาม わし (ชายสูงวัย) x1 |
| Harada | `harada` | **male** | ja_markers | 27/1 | 184 | สรรพนาม 俺 x20 · คำเรียกฝ่ายตรงข้ามแบบชาย x3 · คำลงท้าย ぞ/ぜ x2 · คำลงท้าย だろうが x2 |
| id:date | `date` | **male** | ja_markers | 44/0 | 167 | สรรพนาม 俺 x35 · คำลงท้าย ぞ/ぜ x6 · สรรพนาม わし (ชายสูงวัย) x2 · คำลงท้าย だろうが x1 |
| Narrator | - | **unknown** | crowd_label | 0/0 | 163 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Katsura | - | **male** | ja_markers | 11/0 | 158 | สรรพนาม 俺 x10 · คำลงท้าย ぞ/ぜ x1 |
| Ito | `ito` | **male** | ja_markers | 6/1 | 157 | คำลงท้าย ぞ/ぜ x3 · สรรพนาม 俺 x3 |
| Inoue | `inoue` | **male** | ja_markers | 3/0 | 150 | คำลงท้าย ぞ/ぜ x3 |
| Takeda | `takeda` | **male** | ja_markers | 13/0 | 141 | สรรพนาม わし (ชายสูงวัย) x13 |
| Toyo | `toyo` | **male** | ja_markers | 20/0 | 123 | สรรพนาม わし (ชายสูงวัย) x20 |
| Izo | `izo` | **male** | ja_markers | 11/0 | 118 | สรรพนาม わし (ชายสูงวัย) x8 · คำลงท้าย ぞ/ぜ x2 · คำเรียกฝ่ายตรงข้ามแบบชาย x1 |
| Onlooker | - | **unknown** | crowd_label | 0/0 | 114 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| id:saejima | `saejima` | **male** | ja_markers | 18/1 | 113 | สรรพนาม 俺 x16 · สรรพนาม わし (ชายสูงวัย) x2 |
| Saigo | - | **male** | ja_markers | 8/0 | 94 | สรรพนาม わし (ชายสูงวัย) x7 · คำลงท้าย ぞ/ぜ x1 |
| Yamazaki | `yamazaki` | **unknown** | none | 1/0 | 81 | - |
| Kawaraban Vendor | - | **unknown** | crowd_label | 2/0 | 75 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| id:akiyama | `akiyama` | **male** | ja_markers | 13/0 | 74 | สรรพนาม 俺 x12 · สรรพนาม わし (ชายสูงวัย) x1 |
| Matsubara | - | **male** | ja_markers | 3/0 | 71 | คำลงท้าย ぞ/ぜ x2 · สรรพนาม 俺 x1 |
| id:ryuji | `ryuji` | **male** | ja_markers | 11/2 | 71 | สรรพนาม わし (ชายสูงวัย) x11 |
| Harassed Townsperson | - | **unknown** | crowd_label | 0/1 | 70 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Harassing Man | - | **male** | ja_markers | 9/0 | 70 | คำลงท้าย ぞ/ぜ x5 · คำเรียกฝ่ายตรงข้ามแบบชาย x2 · สรรพนาม オレ x1 · สรรพนาม 俺 x1 |
| Nakaoka | - | **male** | ja_markers | 3/0 | 66 | สรรพนาม 俺 x2 · คำลงท้าย ぞ/ぜ x1 |
| Yamauchi Yodo | - | **male** | ja_markers | 15/0 | 62 | สรรพนาม わし (ชายสูงวัย) x9 · คำลงท้าย ぞ/ぜ x5 · คำเรียกฝ่ายตรงข้ามแบบชาย x1 |
| Sasaki | `sasaki` | **male** | ja_markers | 9/1 | 51 | สรรพนาม わし (ชายสูงวัย) x4 · สรรพนาม 俺 x4 · คำลงท้าย ぞ/ぜ x1 |
| Pleading Citizen | - | **unknown** | crowd_label | 0/1 | 48 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Mother | - | **female** | role_name | 0/0 | 45 | ชื่อผู้พูดบอกเพศในตัวเอง (Mother) |
| Beggar | - | **unknown** | crowd_label | 2/0 | 41 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Barker | - | **unknown** | crowd_label | 0/3 | 40 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Handcart Handler | - | **unknown** | crowd_label | 0/0 | 37 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Yoshinobu | - | **male** | ja_markers | 7/0 | 35 | สรรพนาม 俺 x6 · คำลงท้าย ぞ/ぜ x1 |
| Mukurogai Resident | - | **unknown** | crowd_label | 2/0 | 34 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| id:iku | `iku` | **female** | ja_markers_weak | 0/6 | 32 | สรรพนามคันไซหญิง うち x5 · คำลงท้าย ですわ x1 |
| Anna | `yujyo` | **unknown** | none | 0/0 | 30 | - |
| id:sai | `sai` | **unknown** | none | 2/1 | 30 | - |
| Patron | - | **unknown** | crowd_label | 2/1 | 29 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Shimada Yahei | - | **unknown** | none | 2/0 | 29 | - |
| id:ronin2 | `ronin2` | **male** | ja_markers | 8/0 | 29 | คำลงท้าย ぞ/ぜ x4 · คำเรียกฝ่ายตรงข้ามแบบชาย x3 · สรรพนาม 俺 x1 |
| Doctor | - | **unknown** | crowd_label | 1/0 | 26 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Large Man | - | **male** | role_name | 2/0 | 26 | ชื่อผู้พูดบอกเพศในตัวเอง (Man) |
| Friendly Child | - | **unknown** | crowd_label | 0/0 | 24 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Playing Child | - | **unknown** | crowd_label | 0/0 | 24 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Suzuki | `suzuki` | **male** | ja_markers | 4/0 | 24 | คำเรียกฝ่ายตรงข้ามแบบชาย x2 · คำลงท้าย ぞ/ぜ x1 · สรรพนาม わし (ชายสูงวัย) x1 |
| id:sendo | `sendo` | **unknown** | none | 2/4 | 24 | - |
| Prison Guard | - | **unknown** | crowd_label | 1/0 | 23 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| id:matubara | `matubara` | **unknown** | none | 0/0 | 23 | - |
| Akimoto | `akimoto` | **male** | ja_markers | 3/0 | 22 | สรรพนาม 俺 x3 |
| Boy | - | **male** | role_name | 0/0 | 22 | ชื่อผู้พูดบอกเพศในตัวเอง (Boy) |
| Trooper | - | **unknown** | crowd_label | 1/0 | 22 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Warrior | - | **unknown** | crowd_label | 3/0 | 21 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| id:haraguchi | `haraguchi` | **unknown** | none | 2/0 | 20 | - |
| Serizawa | - | **male** | ja_markers | 4/0 | 19 | สรรพนาม 俺 x4 |
| Tani | `tani` | **male** | ja_markers | 9/0 | 19 | คำลงท้าย ぞ/ぜ x5 · สรรพนาม 俺 x3 · คำเรียกฝ่ายตรงข้ามแบบชาย x1 |
| The Real Okita Soji | - | **unknown** | none | 0/0 | 19 | - |
| id:bakuto | `bakuto` | **unknown** | none | 0/0 | 19 | - |
| id:sengoku | `sengoku` | **male** | ja_markers | 4/0 | 19 | สรรพนาม わし (ชายสูงวัย) x4 |
| id:bushi | `bushi` | **unknown** | none | 0/0 | 18 | - |
| id:joho | `joho` | **unknown** | none | 0/0 | 18 | - |
| id:kannushi | `kannushi` | **unknown** | none | 0/0 | 18 | - |
| id:mon | `mon` | **unknown** | none | 1/0 | 16 | - |
| id:katu | `katu` | **unknown** | none | 0/0 | 15 | - |
| Gambling Den Customer | - | **unknown** | crowd_label | 2/0 | 14 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Maid | - | **female** | role_name | 0/0 | 14 | ชื่อผู้พูดบอกเพศในตัวเอง (Maid) |
| Mizuki | `mizuki` | **unknown** | none | 0/1 | 14 | - |
| The Bathkeeper of Sai | - | **unknown** | none | 0/0 | 14 | - |
| Katsu | - | **unknown** | none | 0/0 | 13 | - |
| Scary Man | - | **male** | ja_markers | 5/0 | 13 | คำลงท้าย ぞ/ぜ x5 |
| Boy's Mother | - | **female** | role_name | 0/0 | 12 | ชื่อผู้พูดบอกเพศในตัวเอง (Mother) |
| Kawaraban Onlooker | - | **unknown** | crowd_label | 0/0 | 12 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| id:dojo2 | `dojo2` | **unknown** | none | 1/0 | 12 | - |
| 0 | - | **unknown** | none | 0/0 | 11 | - |
| Disgruntled Loyalist | - | **unknown** | crowd_label | 0/0 | 11 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Father | - | **male** | role_name | 1/0 | 11 | ชื่อผู้พูดบอกเพศในตัวเอง (Father) |
| Hirayama | - | **unknown** | none | 1/0 | 11 | - |
| Long-Faced Joshi | - | **female** | role_name | 2/0 | 11 | ชื่อผู้พูดบอกเพศในตัวเอง (Joshi) |
| id:toma | `toma` | **unknown** | none | 0/0 | 11 | - |
| Geisha | - | **female** | role_name | 0/0 | 10 | ชื่อผู้พูดบอกเพศในตัวเอง (Geisha) |
| Girl | `girl` | **female** | role_name | 0/0 | 10 | ชื่อผู้พูดบอกเพศในตัวเอง (Girl) |
| Man with Attitude | - | **male** | role_name | 2/0 | 10 | ชื่อผู้พูดบอกเพศในตัวเอง (Man) |
| Portly Joshi | - | **female** | role_name | 1/0 | 10 | ชื่อผู้พูดบอกเพศในตัวเอง (Joshi) |
| Ronin | - | **unknown** | crowd_label | 3/0 | 10 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| id:mihari | `mihari` | **unknown** | none | 1/0 | 10 | - |
| Government Official | - | **unknown** | crowd_label | 1/0 | 9 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| id:nobu | `nobu` | **unknown** | none | 1/0 | 9 | - |
| Guard | - | **unknown** | crowd_label | 0/0 | 8 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Hatamoto | - | **unknown** | none | 1/0 | 8 | - |
| Careless Man | - | **male** | role_name | 1/0 | 7 | ชื่อผู้พูดบอกเพศในตัวเอง (Man) |
| id:ronin1 | `ronin1` | **male** | ja_markers | 3/0 | 7 | สรรพนาม 俺 x2 · คำเรียกฝ่ายตรงข้ามแบบชาย x1 |
| id:taishi | `taishi` | **unknown** | none | 0/0 | 7 | - |
| id:yahei | `yahei` | **unknown** | none | 2/0 | 7 | - |
| Girl's Mother | - | **female** | role_name | 0/0 | 6 | ชื่อผู้พูดบอกเพศในตัวเอง (Girl) |
| Hirama | - | **unknown** | none | 1/0 | 6 | - |
| Loyalist Shishi | - | **unknown** | crowd_label | 0/0 | 6 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Niibori | - | **unknown** | none | 0/0 | 6 | - |
| Sexy Madam | - | **female** | role_name | 0/0 | 6 | ชื่อผู้พูดบอกเพศในตัวเอง (Madam) |
| id:bandai | `bandai` | **unknown** | none | 0/0 | 6 | - |
| id:taishi1 | `taishi1` | **unknown** | none | 0/0 | 6 | - |
| Child-Chasing Mother | - | **female** | role_name | 0/0 | 5 | ชื่อผู้พูดบอกเพศในตัวเอง (Mother) |
| id:haha | `haha` | **unknown** | none | 0/0 | 5 | - |
| id:isya | `isya` | **unknown** | none | 1/0 | 5 | - |
| id:jinushi | `jinushi` | **unknown** | none | 1/0 | 5 | - |
| id:okami | `okami` | **unknown** | none | 0/0 | 5 | - |
| id:rounin1 | `rounin1` | **unknown** | none | 1/0 | 5 | - |
| id:rounin2 | `rounin2` | **male** | ja_markers | 3/0 | 5 | สรรพนาม 俺 x1 · คำลงท้าย ぞ/ぜ x1 · คำเรียกฝ่ายตรงข้ามแบบชาย x1 |
| ??? | - | **unknown** | none | 0/0 | 4 | - |
| Eighth Division Trooper | - | **unknown** | crowd_label | 0/0 | 4 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Elderly Man | - | **male** | role_name | 0/0 | 4 | ชื่อผู้พูดบอกเพศในตัวเอง (Man) |
| Mysterious Man | - | **male** | role_name | 0/0 | 4 | ชื่อผู้พูดบอกเพศในตัวเอง (Man) |
| Shinsengumi Trooper | - | **unknown** | crowd_label | 0/0 | 4 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Sumo Wrestler | - | **unknown** | none | 0/0 | 4 | - |
| id:hira | `hira` | **unknown** | none | 1/0 | 4 | - |
| id:touin10 | `touin10` | **unknown** | none | 0/0 | 4 | - |
| Magistrate Official | - | **unknown** | crowd_label | 0/0 | 3 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Sakamoto Ryoma? | - | **unknown** | none | 0/0 | 3 | - |
| id:furutaka | `furutaka` | **unknown** | none | 0/0 | 3 | - |
| id:hata | `hata` | **unknown** | none | 1/0 | 3 | - |
| Bath Lady | - | **female** | role_name | 0/0 | 2 | ชื่อผู้พูดบอกเพศในตัวเอง (Lady) |
| Gate Guard | - | **unknown** | crowd_label | 0/0 | 2 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Injured Grandma | - | **female** | role_name | 0/0 | 2 | ชื่อผู้พูดบอกเพศในตัวเอง (Grandma) |
| Lovestruck Woman | - | **female** | role_name | 0/0 | 2 | ชื่อผู้พูดบอกเพศในตัวเอง (Woman) |
| Oblivious Woman | - | **female** | role_name | 0/0 | 2 | ชื่อผู้พูดบอกเพศในตัวเอง (Woman) |
| Old Man | - | **male** | role_name | 2/0 | 2 | ชื่อผู้พูดบอกเพศในตัวเอง (Man) |
| Receptionist | - | **unknown** | crowd_label | 0/0 | 2 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Troublesome Ronin | - | **unknown** | crowd_label | 0/0 | 2 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| id:hira1 | `hira1` | **unknown** | none | 0/0 | 2 | - |
| id:ronin3 | `ronin3` | **unknown** | none | 0/0 | 2 | - |
| id:rounin3 | `rounin3` | **unknown** | none | 0/0 | 2 | - |
| id:rounin4 | `rounin4` | **unknown** | none | 0/0 | 2 | - |
| id:shishi3 | `shishi3` | **unknown** | none | 2/0 | 2 | - |
| id:spy | `spy` | **unknown** | none | 0/0 | 2 | - |
| id:waka | `waka` | **unknown** | none | 0/0 | 2 | - |
| Arrogant Dojo Student | - | **unknown** | crowd_label | 0/0 | 1 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Beleaguered Townsperson | - | **unknown** | crowd_label | 0/0 | 1 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Calm Girl | - | **female** | role_name | 0/0 | 1 | ชื่อผู้พูดบอกเพศในตัวเอง (Girl) |
| Doshin | - | **unknown** | none | 0/0 | 1 | - |
| Everyone | - | **unknown** | crowd_label | 0/0 | 1 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Filthy Ronin | - | **unknown** | crowd_label | 0/0 | 1 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| First Division Troopers | - | **unknown** | none | 0/0 | 1 | - |
| Ikumatsu | - | **unknown** | none | 0/0 | 1 | - |
| Kuramitsu Family Servant | - | **unknown** | crowd_label | 0/0 | 1 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Man Having Fun | - | **male** | role_name | 0/0 | 1 | ชื่อผู้พูดบอกเพศในตัวเอง (Man) |
| Mother chasing after her child | - | **female** | role_name | 0/0 | 1 | ชื่อผู้พูดบอกเพศในตัวเอง (Mother) |
| Mysterious Foreigner | - | **unknown** | crowd_label | 0/0 | 1 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| Shinta | - | **unknown** | none | 0/0 | 1 | - |
| Tom | - | **unknown** | none | 0/0 | 1 | - |
| Tosa Doshin | - | **unknown** | none | 0/0 | 1 | - |
| Unknown | - | **unknown** | crowd_label | 0/0 | 1 | ป้ายกลุ่มคน ไม่ใช่ตัวละครเดียว — บังคับกลางเพศ |
| id:chonin1 | `chonin1` | **unknown** | none | 0/0 | 1 | - |
| id:chonin2 | `chonin2` | **unknown** | none | 0/0 | 1 | - |
| id:chonin3 | `chonin3` | **unknown** | none | 0/0 | 1 | - |
| id:chonin4 | `chonin4` | **unknown** | none | 0/0 | 1 | - |
| id:dojo3 | `dojo3` | **unknown** | none | 1/0 | 1 | - |
| id:hira2 | `hira2` | **unknown** | none | 0/0 | 1 | - |
| id:musyuku1 | `musyuku1` | **unknown** | none | 0/0 | 1 | - |
| id:satsuma1 | `satsuma1` | **unknown** | none | 0/0 | 1 | - |
| id:satsuma2 | `satsuma2` | **unknown** | none | 0/0 | 1 | - |
| id:satsuma3 | `satsuma3` | **unknown** | none | 0/0 | 1 | - |
| id:taishi10 | `taishi10` | **unknown** | none | 0/0 | 1 | - |

## สรุป

- ผู้พูดในทะเบียน: **169** คน
- ชาย: 44 · หญิง: 19
- พิสูจน์ไม่ได้: **106** — ทุกคนในกลุ่มนี้ต้องแปลกลางเพศ

## ที่มาของแต่ละชั้น

| ชั้น | ผู้พูด | บรรทัดญี่ปุ่นที่จับคู่ได้ |
|---|---:|---:|
| `Game.locres` คัตซีน (`*_speaker`) | 68 | 2816 |
| `.msg` คิวเสียง opcode 0x03 | 77 | 3963 |
| `sound_speak_data.bin` NPC | 64 | 4045 |
