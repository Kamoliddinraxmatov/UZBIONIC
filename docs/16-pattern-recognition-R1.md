# 16 — Pattern recognition, R1–R2 bosqichi (faqat kompyuter, apparatsiz)

Holati: 2026-10-30, egasi (Kamoliddin) tadqiqot tavsiyalariga rozilik bergandan keyin boshlandi.
Asos: `docs/research/2026-10-raqiblar-va-texnologiyalar.md`, tavsiyalar A1–A5.

## Nima qilindi

| Fayl | Vazifasi |
|---|---|
| `simulation/signal/multichannel.py` | Ko'p kanalli sintetik sEMG + akselerometr. Har bir harakat sinfining kanallar bo'yicha "naqshi" bor, har bir qo'l holati kanal kuchaytirishini o'zgartiradi va tonik faollik qo'shadi (qo'l holati effekti). Kalibrlash protokoli: har bir harakatni har bir holatda 3 s ushlab turish. |
| `emg/patrec/features.py` | Oyna (200 ms, qadam 50 ms) bo'yicha Hudgins xususiyatlari: MAV, WL, ZC, SSC. Faqat oynadagi namunalar ishlatiladi, MK'da halqa buferda hisoblash mumkin. |
| `emg/patrec/lda.py` | Shrinkage bilan LDA (numpy, tashqi kutubxonasiz). Bashorat: oynaga bitta matritsa-vektor ko'paytmasi. |
| `emg/patrec/recognizer.py` | `PatternRecognizer`: xususiyat → LDA → ishonch chegarasi (ishonch past bo'lsa `rest`, ya'ni harakat yo'q) → ko'pchilik ovozi. `PositionAwareRecognizer`: avval akselerometr qo'l holatini aniqlaydi, keyin o'sha holat uchun o'qitilgan EMG klassifikatori ishlaydi. |
| `emg/tests/test_patrec.py` | 14 ta test (xususiyatlar, LDA, ovoz berish, holat effekti, xavfsizlik). |
| `simulation/patrec_demo.py` | Quyidagi jadvalni chiqaradi: `python -m simulation.patrec_demo` |

## Sintetik natijalar (5 urug', 5 sinf, 3 qo'l holati)

> Bu raqamlar **faqat sintetik** ma'lumotdan. Ular kod to'g'ri ishlashini va tendensiyalarni ko'rsatadi,
> haqiqiy foydalanuvchida aniqlik qancha bo'lishini **bashorat qilmaydi**. Sintetik ma'lumot haqiqiysidan
> ancha "toza".

**Qo'l holati effekti** (8 kanal), aniqlik:

| O'qitish | Aniqlik |
|---|---|
| Faqat qo'l pastda | 68,4% |
| Barcha holatlarda | 99,0% |
| Barcha holatlar + akselerometr (2 bosqichli) | 99,5% |

**Kanal soni** (barcha holatlarda o'qitilgan): 2 kanal 37,0%, 4 kanal 91,3%, 8 kanal 99,0%.

**Xavfsizlik** (4 kanal): aniqlik / harakat paytidagi noto'g'ri harakat ulushi / sinf almashishlar soni:

| Sozlama | Aniqlik | Noto'g'ri harakat | Almashishlar |
|---|---|---|---|
| Oddiy | 91,3% | 7,5% | 50 |
| Ishonch chegarasi 0,9 | 77,6% | 3,1% | 75 |
| Chegara 0,9 + 5 ta ovoz | 77,1% | 3,2% | 39 |

## Xulosalar
1. Kalibrlashni **bir necha qo'l holatida** qilish shart (Fougner va boshq., 2011). Transhumeral foydalanuvchida
   qo'l yelkadan harakatlanadi, shuning uchun bu muhim. Akselerometr qo'shimcha yaxshilanish beradi.
2. 5 ta sinf uchun 2 kanal yetmaydi. Hozirgi 2 sensorli sxema (M1) to'g'ridan-to'g'ri boshqaruv sifatida qoladi,
   pattern recognition uchun **kamida 4, maqsad 8 kanal** kerak.
3. Ishonch chegarasi noto'g'ri harakatni ikki baravardan ko'proq kamaytiradi, lekin buning evaziga ba'zan
   harakat bo'lmay qoladi. Ovoz berish esa sinf "sakrashlari"ni kamaytiradi. Ikkalasi birga xavfsizlik uchun
   standart sozlama bo'ladi; aniq chegara haqiqiy signallarda tanlanadi.
4. Kechikish: qaror oyna oxirida chiqadi (200 ms oyna, har 50 ms da yangilanadi); 5 ta ovoz yana ~100 ms
   qo'shishi mumkin. Talab qiymati hali `TBD` (docs/01).

## Keyingi qadamlar
- **R2b:** ochiq ma'lumotlar to'plamida tekshirish (masalan, NinaPro yoki transhumeral yozuvlar). Litsenziya va
  yuklab olish imkoni avval tekshiriladi.
- **R3:** 8 kanalli AFE + IMU variantlari jadvali, haqiqiy narx takliflari bilan; xarid faqat egasi tasdig'idan keyin.
- C firmware portini (`firmware/`) Python etalon bilan bir xil test vektorlari asosida qilish.
