# UZBIONIC — Muhandislik poydevori bo'yicha taklif (qoralama, 2026-10-29)

## 0. Repozitoriyni tekshirish natijasi
- Ishchi papka bo'sh, UZBIONIC uchun Git repozitoriy hali **mavjud emas**.
- GitHub hisobingizda faqat `nova-skills` va `Smart-Menyu` bor, ular bu loyihaga tegishli emas.
- Shuning uchun hech qanday mavjud fayl o'zgartirilmadi. Barcha qoralamalar yangi papkada:
  `/mnt/project-files/uzbionic-foundation/`.

## 1. Taklif qilingan repozitoriy tuzilmasi
To'liq daraxt `README.md` faylida. Asosiy bo'limlar:
- `docs/` — loyiha nizomi, talablar, arxitektura, xavflar, yo'l xaritasi, ADR qarorlari, xavfsizlik.
- `mechanical/` — CAD, chizmalar, hisob-kitoblar.
- `electronics/` — sxemalar, PCB, BOM ("nomzod" va "tanlangan" holati bilan, soxta narxlarsiz).
- `firmware/` — mikrokontroller kodi; asosiy mantiq kompyuterda test qilinadigan qilib ajratilgan.
- `emg/` — EMG signalini qayta ishlash (Python etalon kodi), datasetlar, testlar.
- `simulation/` — sintetik EMG generatori, barmoq kinematikasi, kompyuterda "apparat-sikl" simulyatsiyasi.
- `testing/` — stend sinov tartiblari, moslamalar, natijalar.
- `business/` — bozor, regulyator tadqiqoti (hech qanday "ruxsat olingan" da'vosiz), narxlar (faqat haqiqiy takliflar).

## 2. Yaratilgan hujjat qoralamalari
| Fayl | Mazmuni |
|---|---|
| `docs/00-project-charter.md` | Maqsad, doira, doiradan tashqari ishlar (odamda sinov yo'q), tamoyillar |
| `docs/01-requirements.md` | ID raqamli talablar; asoslanmagan raqamlar `TBD` |
| `docs/02-system-architecture.md` | Bloklar, interfeyslar, dasturiy qatlamlar, holat mashinasi |
| `docs/03-risk-register.md` | 12 ta boshlang'ich xavf va ularni kamaytirish choralari |
| `docs/04-roadmap.md` | M0–M5 bosqichlari, har birida tasdiqlash "darvozasi" |
| `docs/05-mvp-bench-prototype.md` | Minimal stend prototipi va interfeyslar |
| `docs/06-unknowns-assumptions-decisions.md` | Noma'lumlar, farazlar, qabul qilinishi kerak bo'lgan qarorlar |
| `docs/07-milestone-M0.md` | Birinchi kichik bosqich va qabul mezonlari |

Hujjatlar ingliz tilida yozildi (muhandislar va yetkazib beruvchilar bilan ulashish uchun). Xohlasangiz o'zbekchaga o'giraman.

## 3. Minimal stend prototipi (MVP)
**Bitta EMG kanali stenddagi bitta barmoqni ochib-yopadi, hech qanday odam ishtirokisiz.**
EMG signali elektroddan emas, signal generatori yoki yozib olingan/sintetik EMG'ni qayta ijro
etuvchi DAC'dan keladi. Zanjir: signal manbai → analog kuchaytirgich (AFE) → MK ADC → filtr/
konvert/chegara → holat mashinasi → motor drayveri (tok cheklovi bilan) → barmoq; teskari aloqa
(pozitsiya, tok), UART orqali kompyuterga telemetriya, MK'dan mustaqil apparat E-stop.
8 ta interfeys (IF-01…IF-08) `05-mvp-bench-prototype.md` da. Hech qanday aniq qism (part number)
tanlanmagan.

## 4. Apparat tanlashdan oldin hal qilinishi kerak bo'lgan asosiy savollar
1. Byudjet, jamoa va vaqt (D-01).
2. EMG kuchaytirgich: tayyor modul yoki o'zimiz loyihalaymizmi (D-02).
3. Mikrokontroller oilasi (D-03).
4. Aktuator turi va soni: har barmoqqa motor / tendonli / servo (D-04).
5. Nosozlikda xavfsiz holat: qo'l ochiladimi, ushlab turadimi (D-07).
6. Kelajakdagi foydalanuvchi profili — o'lchamni belgilash uchun (D-08).
7. 3D printer va PCB ishlab chiqarish imkoniyati (D-09).
8. Repozitoriy nomi, joyi va litsenziyasi (D-12, D-13).

Asosiy farazlar (tekshiriladi): EMG foydali diapazoni ≈ 20–450 Hz, diskretlash ≥ 1 kHz,
elektr tarmog'i 50 Hz. Bu umumiy amaliyotdan olingan va M1 da manbalar bilan tasdiqlanishi kerak.

## 5. Birinchi bosqich — M0 (faqat kompyuter, apparatsiz)
Sintetik EMG generatori + Python'da EMG qayta ishlash zanjiri + holat mashinasi + testlar.
9 ta qabul mezoni (AC-1…AC-9) `07-milestone-M0.md` da: masalan, 20 ta ma'lum signal portlashidan
20 tasini topish, 60 soniyalik tinch signalda 0 ta yolg'on ishga tushish, har qanday nosozlikda SAFE holatiga o'tish.
Hajmi taxminan 300–500 qator Python. **Sizning tasdig'ingizsiz boshlanmaydi.**

## 6. Sizdan kerak bo'lgan tasdiq
- Tuzilma va hujjatlar ma'qulmi?
- Yangi GitHub repozitoriy nomi (masalan `uzbionic`) — uni GitHub'da o'zingiz yaratishingiz kerak, keyin men ulayman.
- M0 ni boshlashga ruxsat.
