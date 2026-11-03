"""Annotate the UZBIONIC concept v3 image: what the P1S prints vs what is bought."""
import sys
from PIL import Image, ImageDraw, ImageFont

SRC, OUT = sys.argv[1], sys.argv[2]
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
img = Image.open(SRC).convert("RGB")
W, H = img.size  # 848 x 1238
COL = 540
TOP = 120


def canvas(title, sub, color):
    c = Image.new("RGB", (W + 2 * COL, H + TOP + 40), (24, 26, 30))
    c.paste(img, (COL, TOP))
    d = ImageDraw.Draw(c)
    d.text((40, 28), title, font=ImageFont.truetype(FB, 44), fill=color)
    d.text((40, 82), sub, font=ImageFont.truetype(F, 22), fill=(200, 205, 212))
    return c, d


def label(d, side, y, point, head, body, color, num):
    fh, fb = ImageFont.truetype(FB, 22), ImageFont.truetype(F, 19)
    px, py = (point[0] + COL, point[1] + TOP) if point else (0, 0)
    y += TOP
    x0 = 30 if side == "L" else W + COL + 20
    tw = COL - 50
    lines = body.split("\n")
    h = 40 + 26 * len(lines)
    d.rounded_rectangle((x0, y, x0 + tw, y + h), 12, fill=(36, 39, 45), outline=color, width=2)
    d.ellipse((x0 + 10, y + 8, x0 + 42, y + 40), fill=color)
    d.text((x0 + 26, y + 24), str(num), font=ImageFont.truetype(FB, 20), fill=(20, 20, 20), anchor="mm")
    d.text((x0 + 52, y + 10), head, font=fh, fill=(240, 240, 240))
    for i, ln in enumerate(lines):
        d.text((x0 + 14, y + 44 + 26 * i), ln, font=fb, fill=(190, 196, 204))
    if point is None:
        return
    ax = x0 + tw if side == "L" else x0
    ay = y + 24
    d.line((ax, ay, px, py), fill=color, width=3)
    d.ellipse((px - 9, py - 9, px + 9, py + 9), outline=color, width=4)
    d.ellipse((px - 3, py - 3, px + 3, py + 3), fill=color)


GREEN, ORANGE, GREY = (90, 200, 120), (255, 160, 60), (150, 160, 175)

# 1. printed
c, d = canvas("P1S CHOP ETADI", "Yashil = shu printerda o‘zimiz chop etamiz. Kulrang = protezchi bilan.", GREEN)
L = [
    (0, (255, 120), "Gilza (yelka stakani)", "Protezchi qiladi. Sinov nusxasini\nPETG’da chop etsa bo‘ladi.", GREY),
    (170, (275, 300), "Tirsak bo‘g‘imi korpusi", "PETG / neylon (PA-CF)\nIchidagi motor va podshipnik - sotib olinadi", GREEN),
    (340, (210, 520), "Bilak qopqoqlari (grafit)", "ASA, M2 vint bilan mahkamlanadi\nyelim ishlatilmaydi", GREEN),
    (520, (160, 770), "Bilak halqasi (aylanish)", "PETG / neylon korpus", GREEN),
    (690, (150, 880), "Kaft orqa qopqog‘i (UZB)", "ASA", GREEN),
    (860, (175, 1050), "Barmoq bo‘g‘imlari", "Skelet: PETG / neylon\nUstki qopqoq: ASA", GREEN),
    (1060, (118, 1170), "Barmoq uchlari", "TPU 85A/90A - yumshoq rezina", GREEN),
]
for i, (y, p, h, b, col) in enumerate(L, 1):
    label(d, "L", y, p, h, b, col, i)
R = [
    (220, (705, 410), "Ichki karkas va kanallar", "PETG / neylon\n(kabel yo‘llari, motor ushlagichlar)", GREEN),
    (560, (700, 640), "Elektronika qutisi korpusi", "PETG / ASA\nIchidagi plata - sotib olinadi", GREEN),
    (830, (690, 880), "Kaft ichidagi yumshoq joylar", "TPU 85A/90A yostiqchalar", GREEN),
    (1030, (600, 960), "Juda yumshoq “teri” (ixtiyoriy)", "Silikon: P1S’da qolip chop etamiz,\nsilikonni ichiga quyamiz", GREEN),
]
for i, (y, p, h, b, col) in enumerate(R, len(L) + 1):
    label(d, "R", y, p, h, b, col, i)
c.save(OUT + "/uzbionic-chop-etiladi.png")

# 2. bought
c, d = canvas("SOTIB OLINADI", "To‘q sariq = printerda qilinmaydi, tayyor holda olinadi.", ORANGE)
R = [
    (0, (640, 150), "EMG sensorlar", "Yelka mushaklari ustiga, gilza ichida\nsoni protezchi bilan aniqlanadi", ORANGE),
    (170, (625, 300), "Tirsak motori + podshipnik", "Reduktorli motor, sharikli podshipnik", ORANGE),
    (340, (690, 450), "Simlar va ulagichlar", "Ingichka egiluvchan kabel, razyomlar", ORANGE),
    (500, (695, 555), "Boshqaruv platasi", "Mikrokontroller + motor drayverlari\n+ EMG kuchaytirgich", ORANGE),
    (670, (720, 640), "Batareya", "Li-ion, zaryad va himoya platasi bilan", ORANGE),
    (830, (725, 770), "Bilak aylantirish motori", "Kichik reduktorli motor", ORANGE),
    (990, (690, 900), "Barmoq motorlari (kaft ichida)", "Mikro reduktorli motorlar (har barmoqqa)", ORANGE),
]
for i, (y, p, h, b, col) in enumerate(R, 1):
    label(d, "R", y, p, h, b, col, i)
L = [
    (380, (175, 1020), "Vintlar, o‘qlar, shaybalar", "M2 vintlar (qopqoqlar uchun),\npo‘lat o‘qlar (bo‘g‘imlar uchun)", ORANGE),
    (620, None, "Filament (material)", "PETG, ASA, TPU 85A/90A,\nkeyinroq PA-CF + qattiq nozzle", ORANGE),
    (860, (300, 150), "Gilza (yelka stakani)", "Protezchi tayyorlaydi", GREY),
]
for i, (y, p, h, b, col) in enumerate(L, len(R) + 1):
    label(d, "L", y, p, h, b, col, i)
c.save(OUT + "/uzbionic-sotib-olinadi.png")
