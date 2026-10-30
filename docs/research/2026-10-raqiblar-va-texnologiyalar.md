# UZBIONIC — Raqiblar, eng so'nggi texnologiyalar va tavsiyalar (taklif, 2026-10-30)

> Holati: **taklif (proposal)**. CAD va kodga hech qanday o'zgartirish kiritilmagan.
> Barcha raqamlar quyidagi manbalardan olingan; manba bo'lmagan joyda "e'lon qilinmagan" deb yozilgan.
> Narxlar ko'pincha ikkilamchi manbalardan (agregator, OAV) — ular rasmiy narx emas.

---

## 0. Qisqacha xulosa (1 daqiqada)

1. **Bozor yetakchilari** (Ottobock, Össur, PSYONIC, Open Bionics, TASKA, Esper, BrainCo) qo'lning o'zida bir-biriga
   yaqin: 400–700 g, 5 barmoq, 6 ta motor atrofida, 7 dan 36 tagacha ushlash turi. Farq **boshqaruv**,
   **chidamlilik**, **sezgi (touch) teskari aloqasi** va **narx**da.
2. **Eng muhim saboq:** foydalanuvchilar protezdan voz kechishining asosiy sabablari — noqulay boshqaruv, og'irlik,
   issiqlik va qulaylik; DOF (erkinlik darajasi) soni emas. Cybathlon 2024'da 1- va 2-o'rinlarni oddiy
   (1 motorli) qurilmalar olgan.
3. **Bizning birinchi foydalanuvchi — yelkadan pastda (transhumeral) amputatsiya.** Bu darajada eng kuchli
   ilmiy dalil: **pattern recognition (naqshni tanib olish)** an'anaviy 2-elektrodli boshqaruvdan yaxshiroq
   (8 bemorli uy sinovi, 7/8 uni afzal ko'rgan). Lekin bu sinov TMR operatsiyasidan o'tgan bemorlarda edi —
   operatsiyasiz yelka mushaklaridan kamroq "qo'l signali" chiqadi. Buni halol rejalashtirish kerak.
4. **"Eng so'nggi texnologiya"ning bir qismi jarrohlik talab qiladi** (TMR, osseointegratsiya + implant
   elektrodlar e-OPRA, AMI). Bu UZBIONIC doirasidan tashqarida. Biz **operatsiyasiz** erisha oladigan eng
   zamonaviy to'plam: ko'p kanalli sEMG + pattern recognition + IMU (qo'l holatini hisobga olish) + barmoq
   uchidagi bosim sensori va vibratsiya teskari aloqasi + chidamli, egiluvchan barmoqlar + ilova va ochiq API.
5. **Transhumeral foydalanuvchi uchun tirsak (elbow) ham kerak.** Hozirgi dizaynimizda qo'l va bilak
   aylantirgichi bor, tirsak yo'q. Bu ochiq qaror sifatida ko'rsatildi (§7).

---

## 1. Raqiblar taqqoslamasi

### 1.1 Asosiy ko'p barmoqli qo'llar

| Mahsulot (kompaniya, mamlakat) | Og'irlik | Kuch / yuk | Tezlik | Ushlash turlari | Boshqaruv va ajralib turuvchi xususiyat | Narx (ochiq manbada) |
|---|---|---|---|---|---|---|
| **Ability Hand** (PSYONIC, AQSh) | 0,47 kg [A1]; 450–500 g [A4] | Manbalarda farq bor: 45,4 kg va "~63 kg" [A1] — tasdiqlanmagan | Yopilish 200 ms [A1] | Kamida 20 tayyor + 11 maxsus [A4] | 6 DOF, 6 cho'tkasiz motor; 30 ta sensorli barmoq uchlari va vibratsiyali sezgi teskari aloqasi; zarbaga chidamli egiluvchan barmoqlar; IP64; ochiq API (BLE/UART/RS485); FDA ro'yxatida, Medicare qoplaydi [A1] | 15 000 $ (agregator) [A1]; 10–20 ming $ (OAV) [A4] |
| **Hero PRO** (Open Bionics, Buyuk Britaniya) | Butun tizim 1,21 lb (≈549 g), batareya va sensorlar bilan [A2][A4] | Ko'tarish yuki 57 lb; ushlash kuchi e'lon qilinmagan [A2] | Yopilish 0,6 s [A2] | 7 [A2] | Quvvatli bosh barmoq aylanishi; qo'lda 360° bilak aylanishi va ±45° egilish; IPX7; USB-C, ~4 soatlik zaryad; Sidekick ilovasi, simsiz yangilanish; almashtiriladigan dizayn qopqoqlari [A2] | Ochiq narx yo'q [A4] |
| **bebionic** (Ottobock, Germaniya) | 402–689 g (o'lcham va bilakka qarab) [A3] | Tripod 36 N, kalit ushlash 26 N [A3] | E'lon qilinmagan | 14, bir vaqtda 8 tasi [A3] | 6 boshqaruv rejimi, proporsional boshqaruv, "auto grip"; Myo Plus pattern recognition bilan mos [A3] | E'lon qilinmagan |
| **Michelangelo** (Ottobock) | 510 g [A5] | 70 N (oppozitsiya), 15 N (neytral) [A5] | 325 mm/s [A5] | 7 [A5] | Axon-Bus tizimi; egiluvchan rejimli AxonWrist [A5] | E'lon qilinmagan |
| **i-Limb Quantum** (Össur, Islandiya) | 432–658 g [A6] | Qo'l yuki 40/90 kg; barmoq yuki 20/48 kg [A6] | To'liq ochish→yopish 0,8 s [A6] | 36 tagacha [A6] | **i-MO imo-ishora boshqaruvi** (qo'lni 4 yo'nalishdan biriga siltash bilan ushlash turini almashtirish); avtomatik bosh barmoq; ilova; 7,4 V Li-Po, 1300/2000 mAh [A6] | E'lon qilinmagan |
| **Esper Hand / Hand 2** (Esper Bionics, Ukraina/AQSh) | E'lon qilinmagan | E'lon qilinmagan | "O'xshashlardan 3 marta tezroq" (kompaniya da'vosi) [A8] | E'lon qilinmagan | Bulutli platformada mashinali o'qitish: foydalanuvchi tez-tez tanlaydigan ushlash turiga ustunlik beradi [A8]; Hand 2 suvga chidamli deb e'lon qilingan [A7] | AQSh sug'urtasi ~22 000 $ to'laydi (kompaniya, 2024) [A4] |
| **Revo 2** (BrainCo, Xitoy/AQSh) | 383 g [A9] | Butun qo'l 50 N [A9] | E'lon qilinmagan | E'lon qilinmagan | 11 DOF, 6 aktiv bo'g'in; Touch versiyasida bosim/ishqalanish/yaqinlik sensorlari; robot ishlab chiqaruvchilarga ham sotilmoqda [A9] | Xitoyda ~50 000 yuan'dan (OAV) [A9] |
| **TASKA CX** (TASKA, Yangi Zelandiya) | E'lon qilinmagan [A4] | — | — | 18 avtomatik + 5 maxsus [A4] | Texnik ko'rsatkichlar ishlab chiqaruvchi spec sheet'idan hali tekshirilmadi | E'lon qilinmagan |
| **Adam's Hand Plus** (BionIT Labs, Italiya) | E'lon qilinmagan | — | — | — | 2026: aktiv bosh barmoq aylanishi; **PRISM** pattern recognition 1–4 elektrod bilan; **PULSE** vibratsiyali teskari aloqa [A10] | E'lon qilinmagan |
| **Atom Touch** (Atom Limbs, AQSh) | — | — | — | — | Hali ishlab chiqilmoqda; maqsadli narx ~20 000 $ (kompaniya maqsadi) [A4] | Maqsad ~20 000 $ |

Ma'lumot uchun: AQSh Medicare'ning 2026-yildagi L6880 kodi (mustaqil barmoqli elektr qo'l) bo'yicha to'lov
miqdori 28 715 $ — bu ma'lum bir qo'lning narxi emas, gilza, bilak va moslashni o'z ichiga olmaydi [A4].

### 1.2 Boshqaruv tizimlari (qo'lning "miyasi")

| Tizim | Nima qiladi | Biz uchun ahamiyati |
|---|---|---|
| **Coapt Complete Control Gen2** (AQSh) | Teri elektrodlaridagi EMG naqshlarini tanib, tirsak, bilak va qo'lni boshqaradi; rejim almashtirishni yo'q qiladi, tez qayta kalibrlash imkonini beradi. FDA 510(k) K191083, 2019-yil [A11] | Transhumeral darajada aynan shu turdagi boshqaruv eng kuchli dalilga ega (§2.1) |
| **Ottobock Myo Plus** | Pattern recognition; bebionic bilan mos [A3] | Yirik o'yinchilar ham pattern recognition'ga o'tmoqda |
| **BionIT PRISM** | 1–4 elektrodga moslashadigan pattern recognition, qo'l + bilak aylantirgich [A10] | Kam elektrod bilan ham ishlash mumkinligi — bizning boshlang'ich holatga mos |
| **Össur i-MO** | Harakat sensori bilan imo-ishora orqali ushlash turini tanlash [A6] | EMG signali kam bo'lganda IMU qo'shimcha "kanal" bo'la oladi |

### 1.3 Ochiq manba va musobaqa qurilmalari (eng ko'p narsa o'rganiladigan joy)

- **Bionicohand** (Fransiya, JNER, 2026-aprel) [A12]: bitta Faulhaber motori 5 barmoqni harakatlantiradi;
  RP2040 MK + DRV8874 drayver; 2 ta Myobock elektrodi; 100 Hz boshqaruv; ixtiyoriy vibrator motor tokiga
  (ya'ni ushlash kuchiga) proporsional. Litsenziya: CERN-OHL-S (mexanika/elektronika), GPLv3 (dastur).
  Cybathlon 2024'da 2-o'rin. Muhim natija: **vibratsiyali teskari aloqa bilan yumshoq/qattiq predmetni ajratish
  10/10, usiz 6/10**. Kamchiliklar: sekin yopilish (Michelangelodan ~2 marta sekin), suvga chidamsiz, ushlagandan
  keyin bo'shashish. Hammasi bitta tajribali foydalanuvchida sinalgan.
- **HANDSON Hand** (Xitoy, Southeast University, Cybathlon 2024 g'olibi) [A13][A14]: 1 DOF ikki barmoqli
  ushlagich + aktiv bilak aylanishi; gibrid boshqaruv — barmoqni ochish yelkadagi cho'zilish sensori bilan,
  bilak aylanishi EMG bilan proporsional; ~900 g; STM32U5; kamera + YOLOv5 orqali predmetni tanish; 3200 mAh,
  12 soatgacha. G'alaba sabablari: ikki manbali boshqaruv, foydalanuvchi bilan muntazam mashg'ulot
  (haftada 2–3 marta, 3–4 soat), musobaqa qoidalarini oldindan mashq qilish.

**Xulosa:** g'oliblar eng ko'p motorli qo'l emas, **foydalanuvchiga eng ishonchli boshqariladigan** qurilma bo'ldi.

---

## 2. So'nggi ilmiy tendensiyalar

### 2.1 Transhumeral darajada pattern recognition
- Hargrove va hamkasblari (Scientific Reports, 2017): TMR'dan o'tgan 8 nafar transhumeral foydalanuvchi har bir
  boshqaruv turini uyda kamida 42 kun ishlatgan. Pattern recognition bilan SHAP va kiyim qisqichlarini ko'chirish
  testlari sezilarli yaxshi; Box and Blocks'da farq yo'q; **8 dan 7 nafari pattern recognition'ni afzal ko'rgan**;
  og'irlik va issiqlik har ikki usulda foydalanishni cheklagan [A15][A16].
- Frontiers in Neurology (2026) TMR meta-tahlili: transhumeral ma'lumotlar kam, natijalar dastlabki;
  laboratoriyadagi yaxshi tasniflash kundalik hayotdagi mustaqillikka teng emasligi ta'kidlangan [A17].
- **Biz uchun:** TMR operatsiyasiz yelka mushaklari (biceps, triceps, deltoid va h.k.) asosan tirsak
  harakatlarini beradi. Qo'l uchun alohida "naqshlar" kamroq bo'ladi. Shuning uchun boshlanishda kam sinf
  (masalan, ochish / yopish / dam / bilak aylanishi) + IMU imo-ishoralari + ilova orqali ushlash tanlash —
  real yo'l. Aniq nechta sinf ishonchli ajratilishi faqat haqiqiy foydalanuvchi signallarida, klinik nazorat
  ostida aniqlanadi.

### 2.2 Ko'p kanalli (HD-EMG) va chuqur o'qitish
- Quadrelli va boshq. (Frontiers in Neuroscience, 2025-sentyabr) [A18]: ko'pchilik tijoriy protezlar 2 elektrod
  ishlatadi; **"hozircha hech bir tijoriy protez 8 bipolyar EMG kanalidan oshmaydi"**. HD-EMG prototiplari faqat
  laboratoriyada; CNN/GNN natijalari yaxshi, lekin real vaqtli protez boshqaruvida deyarli sinalmagan, hisoblash
  talabi katta. Ixcham yechim sifatida INTAN RHD2000 chiplari tilga olingan.
- Meta Reality Labs (Nature, 2025-sentyabr) [A19]: minglab ishtirokchi ma'lumotlarida o'qitilgan **umumiy sEMG
  modeli** yangi odamda kalibrlashsiz ishlagan; shaxsiylashtirish qo'lyozma tanishni 16% yaxshilagan. Bu
  bilakdagi (sog'lom qo'l) tadqiqot — amputatsiyaga to'g'ridan-to'g'ri ko'chirib bo'lmaydi, lekin yo'nalish aniq:
  **katta ma'lumot + umumiy model + qisqa shaxsiy moslash**.

### 2.3 Qo'l holati effekti (limb position effect)
- Fougner va boshq. (IEEE TNSRE, 2011) [A20]: qo'l turli holatda bo'lganda EMG naqshlari o'zgaradi va tasniflash
  xatosi oshadi; bir necha holatda o'qitish va akselerometr ma'lumotini qo'shish bu muammoni kamaytiradi.
  Transhumeral foydalanuvchida qo'l yelkadan butunlay harakatlanadi — bu biz uchun dolzarb.

### 2.4 Sezgi (touch) teskari aloqasi
- PSYONIC (Akhtar va boshq., MEC) [A21]: barmoq uchidagi bosim sensori → vibratsiya motori + "kontakt refleksi"
  (predmetga tegishi bilan qo'l yopilishni to'xtatadi). 2 nafar ishtirokchida tuxum po'chog'ini sindirish
  10 tadan ~7 dan 0,5–1,5 ga tushgan.
- Bionicohand: vibratsiya bilan predmetni ajratish 6/10 → 10/10 [A12].
- Chalmers / e-OPRA (NEJM, 2020) [A22]: implant elektrodlar va nerv stimulyatsiyasi orqali haqiqiy sezgi —
  3 nafar transhumeral bemor 7 yilgacha kundalik hayotda ishlatgan. Bu jarrohlik yechim, bizning doiradan tashqarida,
  lekin "sensorlar emas, interfeys asosiy to'siq" degan xulosasi muhim.
- Umumiy holat (2026 sharhi, oyoq protezlari bo'yicha) [A23]: vibrotaktil teskari aloqa **eng amaliy yaqin
  muddatli variant**; dalillar hali kichik va qisqa sinovlarga asoslangan.

### 2.5 Nima uchun odamlar protezdan voz kechadi
- Biddiss va Chau ma'lumotiga ko'ra kattalarda elektr protezlardan voz kechish ~23%, bolalarda ~35% [A24].
- Sabablar: og'irlik, issiqlik va terlash, teri ta'sirlanishi, shovqinli signal, elektrod siljishi, qo'l
  holatiga sezgirlik, charchoq, funksional foyda yo'qligi [A24]. 2025-sharh ham asosiy sababni noqulay
  boshqaruvda ko'radi [A18].

---

## 3. Soha yetakchilari intervyularidan saboqlar

| Kim | Asosiy fikr | Manba |
|---|---|---|
| **Aadeel Akhtar** (PSYONIC asoschisi) | Ability Hand 9 avloddan ortiq o'tgan; bemorlar fikri tufayli ustuvorlik "arzonlik"dan **chidamlilik, tezlik va ishonchlilik**ka o'tgan, chunki odamlar o'n minglab dollarlik qo'llarni bir necha oyda sindirib qo'yishardi. Silikon qoplama, egiluvchan (soft) robototexnika, mustahkamlangan 3D bosma. Ochiq API. "Ba'zi cheklovlar o'ylaganimizdan ko'ra ko'proq bizning boshimizda." | 3DHeals podkasti, 2026-fevral [A25] |
| **Joel Gibbard** (Open Bionics asoschisi) | Birinchi 5 motorli tendonli dizayn "unchalik ishonchli emas" bo'lgan, yig'ish ~12 soat olgan; keyingi avlodda egiluvchan "tirik bo'g'inlar", motor faqat yopadi, prujinali bo'g'in ochadi. Protezni **xohlanadigan** narsaga aylantirish — bolalar faxrlanishi kerak. | The Engineer (taxminan 2015) [A26] |
| **Max Ortiz Catalan** (Chalmers, e-OPRA) | Nerv signali mikrovolt, mushak signali millivolt darajasida; osseointegratsiya — ularning ishidagi asosiy farq; keyingi qadam — to'g'ridan-to'g'ri nerv stimulyatsiyasi orqali sezgi va propriotsepsiya. | Circuit Cellar intervyusi, 2016 [A27]; Chalmers press-relizi, 2020 [A22] |
| **Dima Gazda** (Esper Bionics bosh direktori) | Protez "biologik qo'l kabi boshqarilishi" kerak; bulutli platforma foydalanuvchi xatti-harakatidan o'rganib, uning sevimli ushlash turiga ustunlik beradi; operatsiyasiz yondashuv. | Unite.AI intervyusi, 2022-noyabr [A8] |
| **Todd Kuiken / Levi Hargrove** (Shirley Ryan AbilityLab) | TMR va pattern recognition kashshoflari; transhumeral foydalanuvchilarning aksariyati uyda pattern recognition'ni tanlagan. | Scientific Reports, 2017 [A15][A16] |
| **Hugh Herr** (MIT) | AMI operatsiyasi agonist-antagonist mushak juftlarini saqlab, protezni "his qilish"ga yordam beradi (asosan oyoq protezlarida). | NPR/TED Radio Hour, 2024 [A28] |

Eslatma: Kuiken, Herr va Coapt rahbariyati bilan bevosita yangi intervyu matnlarini ochiq manbada tekshira
olmadim; jadvalda faqat tekshirilgan manbalardagi fikrlar keltirildi.

---

## 4. UZBIONIC uchun aniq tavsiyalar

Har bir tavsiya mavjud papkalarga bog'langan. **Hech biri sizning tasdig'ingizsiz boshlanmaydi.**

### A. Boshqaruv (emg/, firmware/) — eng katta ustuvorlik
1. **Pattern recognition'ni asosiy yo'nalish qilish.** Bosqichma-bosqich: (a) hozirgi 2 kanalli to'g'ridan-to'g'ri
   boshqaruv (M0/M1) xavfsiz zaxira rejim sifatida qoladi; (b) 4–8 kanal uchun klassik xususiyatlar (MAV, WL, ZC,
   SSC) + LDA — tijoriy tizimlarda sinalgan, kichik MK'da ishlaydi; (c) keyinroq kichik neyron tarmoq faqat LDA'dan
   aniq yaxshi bo'lsa. Asos: [A15][A11][A10][A18].
2. **Kanal soni: 8 tagacha** (tijoriy amaliyot chegarasi [A18]). Myo 8-sensorli misolimiz bu raqamga mos.
   Yelkada qaysi mushaklar ustiga qo'yilishini prothezist bilan aniqlash.
3. **IMU (akselerometr + giroskop) qo'shish** — ikki maqsadda: qo'l holati effektini kamaytirish [A20] va i-MO
   uslubidagi imo-ishora bilan ushlash turini tanlash [A6].
4. **Tez qayta kalibrlash**: bitta tugma yoki ilovadan 1–2 daqiqalik qayta o'qitish (Coapt yondashuvi [A11]).
   Elektrod siljishi va terlash muqarrar [A24].
5. **Ishonch chegarasi (rejection)**: model ishonchi past bo'lsa — harakat qilmaslik. Yolg'on ishga tushish
   xavfsizlik talabi sifatida o'lchanadi (M0'dagi AC mezonlari davomi).
6. **Ma'lumot jurnali (log)**: qaysi ushlash qachon ishlatilgani — keyinchalik shaxsiylashtirish uchun (Esper
   g'oyasi [A8]), lekin qurilmada, roziliksiz bulutga yubormasdan.

### B. Mexanika (mechanical/) — chidamlilik birinchi
7. **Egiluvchan barmoq bo'g'inlari / silikon qoplama** — zarbaga chidamlilik (Akhtar [A25], Gibbard [A26]).
   Hozirgi tendonli dizaynda tendon uzilishi va qayta tortish ishonchliligini alohida sinash.
8. **Og'irlik maqsadi:** qo'l raqiblar oralig'ida yoki yengilroq (383–689 g, §1.1). Transhumeral foydalanuvchida
   qo'l yelkadan uzoqda — har bir gramm momentni oshiradi. Og'irlik va issiqlik foydalanishni cheklaydi [A16].
9. **Ushlash turlari: 4–7 tadan boshlash** (Hero PRO va Michelangelo 7 ta bilan bozorda [A2][A5]). 36 ta shart emas.
10. **Ushlab turish (non-backdrivable)**: motor o'chganda ushlash bo'shamasligi — Bionicohand foydalanuvchisi aynan
    shundan shikoyat qilgan [A12]. Pololu reduktorli motorlarda buni stendda o'lchash.

### C. Sezgi teskari aloqasi (electronics/, firmware/)
11. **Barmoq uchlarida bosim sensori (FSR yoki shunga o'xshash) + gilzada 1 ta vibratsiya motori** + **kontakt
    refleksi** (tegishi bilan yopilishni sekinlatish/to'xtatish). Arzon, operatsiyasiz va dalil bor [A21][A12][A23].
12. Motor tokini ushlash kuchining bilvosita o'lchovi sifatida ishlatish (Bionicohand [A12]) — qo'shimcha sensorsiz
    boshlanish.

### D. Tizim va ekotizim
13. **Tirsak masalasi** (§7, D-yangi): transhumeral uchun tirsak shart. Variantlar: passiv qulflanadigan tirsak
    (yengil, arzon, birinchi prototip uchun) yoki keyinroq quvvatli tirsak. HANDSON'ning gibrid g'oyasi — yelka
    harakati bilan biror funksiyani (masalan, tirsak qulfi) boshqarish [A13].
14. **Ochiq telemetriya/API** (UART/BLE) — sinov va tadqiqot uchun (Ability Hand [A1]).
15. **Dizayn va o'zlik**: almashtiriladigan qopqoqlar (Hero PRO [A2]) — brend konsepsiyamiz (v0.3) bilan mos.
16. **Baholash**: SHAP, Box and Blocks, kiyim qisqichini ko'chirish testi [A16] — faqat xavfsizlik darvozasidan
    keyin, prothezist/shifokor ishtirokida. Stendda: yopilish vaqti (raqiblar 0,2–0,8 s), ushlash kuchi, sikllar soni.

### E. Hozircha qilmaymiz
- Implant elektrodlar, TMR, AMI, osseointegratsiya — jarrohlik, bizning doiradan tashqarida.
- HD-EMG (64+ kanal) — hali laboratoriya bosqichida [A18]; tadqiqot yo'nalishi sifatida kuzatamiz.
- Bulutga majburiy bog'lanish.

---

## 5. Taklif qilingan ketma-ketlik (mavjud M-bosqichlarga qo'shimcha)

| Qadam | Nima | Apparat kerakmi |
|---|---|---|
| R1 | Python'da xususiyatlar + LDA pattern recognition, sintetik va ochiq ma'lumotlar to'plamlarida (masalan, NinaPro) | Yo'q |
| R2 | Ishonch chegarasi, yolg'on ishga tushish o'lchovi, qo'l holati simulyatsiyasi | Yo'q |
| R3 | 8 kanalli AFE + IMU variantlari jadvali (datasheet'lardan, haqiqiy takliflar bilan) | Xarid uchun tasdiq kerak |
| R4 | Barmoq uchi sensori + vibratsiya + kontakt refleksi stendda | Kichik xarid |
| R5 | Tirsak varianti ADR | Yo'q |

---

## 6. Halollik va cheklovlar
- Ability Hand ushlash kuchi bo'yicha manbalar bir-biriga zid; tasdiqlanmagan.
- Narxlar asosan OAV yoki agregatorlardan; rasmiy narx ro'yxatlari ochiq emas.
- TASKA, Esper, Atom Touch texnik ko'rsatkichlari to'liq topilmadi.
- Ko'pchilik tadqiqotlar kichik guruhlarda (1–8 kishi) o'tkazilgan.
- Hech qanday klinik samaradorlik yoki regulyator ruxsati UZBIONIC uchun da'vo qilinmaydi.

## 7. Sizdan kerak bo'lgan qarorlar
1. Pattern recognition'ni asosiy boshqaruv yo'nalishi sifatida qabul qilasizmi (R1–R2 dan boshlab)?
2. Birinchi prototipda tirsak: passiv qulflanadigan yoki hozircha tirsaksiz (faqat stend)?
3. Barmoq uchi sensori + vibratsiyali teskari aloqa birinchi prototipga kiradimi?

---

## Manbalar
- [A1] Ability Hand — humanoid.guide: https://humanoid.guide/product/ability-hand/
- [A2] Open Bionics Hero PRO: https://openbionics.com/hero-pro/
- [A3] Ottobock bebionic 8E70: https://www.ottobock.com/en-us/b2b-product/8E70
- [A4] Robopulse, cybernetic hands guide: https://robopulse.net/guides/cybernetic-hands/
- [A5] Ottobock Michelangelo 8E500: https://www.ottobock.com/en-gb/product/8E500
- [A6] Össur i-Limb Quantum katalogi: https://media.ossur.com/ossur-dam/image/upload/product-documents-global/i-Limb_Quantum_Catalog_en-us_Q4-22.pdf
- [A7] TechUkraine, Esper Hand 2 (2025-05-23): https://techukraine.org/2025/05/23/esper-bionics-unveils-esper-hand-2-a-waterproof-ai-powered-prosthetic-ready-for-anything/
- [A8] Unite.AI, Dima Gazda intervyusi (2022-11-18): https://www.unite.ai/dima-gazda-co-founder-ceo-of-esper-bionics-interview-series/
- [A9] Startup Fortune, BrainCo (2026-07-21): https://startupfortune.com/braincos-bionic-hands-are-selling-to-robot-makers-not-just-amputees/
- [A10] BionIT Labs, OTWorld 2026: https://bionitlabs.com/news-en/bionit-labs-otworld-2026-adams-hand-plus-prism-pulse/
- [A11] FDA 510(k) K191083, Coapt Complete Control Gen2: https://fda.innolitics.com/device/K191083
- [A12] Pissard-Gibollet va boshq., Bionicohand, JNER 23:191 (2026): https://link.springer.com/article/10.1186/s12984-026-01987-8
- [A13] Hu va boshq., HANDSON Hand, Bioengineering 12(3):228 (2025): https://mdpi.com/2306-5354/12/3/228
- [A14] Amplitude, Cybathlon 2024 natijalari: https://livingwithamplitude.com/article/cybathlon-2024-prosthesis-race-results/
- [A15] Hargrove va boshq., Scientific Reports (2017), PMC5653840: https://pmc.ncbi.nlm.nih.gov/articles/PMC5653840
- [A16] O&P EDGE xulosasi: https://opedge.com/tmr-pattern-recognition-outperforms-direct-control/
- [A17] Meng va boshq., Frontiers in Neurology 17:1946094 (2026): https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2026.1946094/full
- [A18] Quadrelli va boshq., Frontiers in Neuroscience (2025): https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2025.1655257/full
- [A19] Kaifosh & Reardon, Nature 645:702–711 (2025): https://ideas.repec.org/a/nat/nature/v645y2025i8081d10.1038_s41586-025-09255-w.html
- [A20] Fougner va boshq., "Resolving the Limb Position Effect in Myoelectric Pattern Recognition", IEEE TNSRE (2011): https://ntnuopen.ntnu.no/ntnu-xmlui/handle/11250/2392260
- [A21] Akhtar va boshq., "Touch Feedback and Contact Reflexes Using the PSYONIC Ability Hand", MEC: https://conferences.lib.unb.ca/index.php/mec/article/view/26
- [A22] Chalmers press-relizi (2020-04-29), NEJM doi:10.1056/NEJMoa1917537: https://www.mynewsdesk.com/uk/chalmers/pressreleases/mind-controlled-arm-prostheses-that-feel-are-now-a-part-of-everyday-life-2993450
- [A23] Hussain va boshq., Frontiers in Bioeng. Biotech. 13 (2026): https://www.frontiersin.org/journals/bioengineering-and-biotechnology/articles/10.3389/fbioe.2025.1722817/full
- [A24] Battraw va boshq., Prosthetics and Orthotics International 46(3) (2022): https://par.nsf.gov/servlets/purl/10353014
- [A25] 3DHeals, Aadeel Akhtar (2026-02-22): https://3dheals.com/aadeel-akhtar-bionic-hands-for-humans-and-robots-the-psyonic-story/
- [A26] The Engineer, Joel Gibbard: https://www.theengineer.co.uk/open-bionics-founder-joel-gibbard/
- [A27] Circuit Cellar, Max Ortiz Catalan intervyusi (2016): https://circuitcellar.com/insights/interviews/brain-control-an-interview-with-dr-max-ortiz-catalan/
- [A28] KRWG/NPR TED Radio Hour (2024-10-04): https://www.krwg.org/2024-10-04/bionic-limbs-can-now-feel-real-thanks-to-new-surgery
