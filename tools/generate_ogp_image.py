from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "img" / "ogp-default.png"
PORTRAIT = ROOT / "assets" / "img" / "portrait.jpg"

W, H = 1200, 630


def font(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size, index=index)


SANS_W6 = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
SANS_W3 = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"


def fit_text(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        trial = current + char
        if draw.textbbox((0, 0), trial, font=font_obj)[2] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = char
    if current:
        lines.append(current)
    return lines


def paste_portrait(canvas: Image.Image) -> None:
    portrait = Image.open(PORTRAIT).convert("RGB")
    source_w, source_h = portrait.size
    target_w, target_h = 360, 470

    crop_w = int(source_h * target_w / target_h)
    center_x = int(source_w * 0.53)
    left = max(0, min(source_w - crop_w, center_x - crop_w // 2))
    portrait = portrait.crop((left, 0, left + crop_w, source_h)).resize((target_w, target_h), Image.Resampling.LANCZOS)

    x, y = 760, 78
    shadow = Image.new("RGBA", (target_w + 58, target_h + 58), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((24, 24, target_w + 24, target_h + 24), radius=0, fill=(48, 39, 28, 68))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    canvas.alpha_composite(shadow, (x - 28, y - 20))

    frame = Image.new("RGBA", (target_w + 34, target_h + 34), (247, 243, 236, 255))
    frame_draw = ImageDraw.Draw(frame)
    frame_draw.rectangle((0, 0, target_w + 33, target_h + 33), outline=(174, 135, 72, 255), width=2)
    frame.paste(portrait.convert("RGBA"), (17, 17))
    canvas.alpha_composite(frame, (x, y))


def main() -> None:
    canvas = Image.new("RGBA", (W, H), (247, 243, 236, 255))
    draw = ImageDraw.Draw(canvas)

    # Subtle paper-like background and a thin gold rule for a restrained professional tone.
    for yy in range(0, H, 6):
        shade = 246 + (yy % 18) // 9
        draw.line((0, yy, W, yy), fill=(shade, shade - 2, shade - 8, 38), width=1)
    draw.rectangle((0, 0, 18, H), fill=(38, 38, 35, 255))
    draw.rectangle((18, 0, 24, H), fill=(174, 135, 72, 255))
    draw.line((78, 92, 676, 92), fill=(174, 135, 72, 255), width=2)

    paste_portrait(canvas)

    sans_small = font(SANS_W3, 25)
    sans = font(SANS_W6, 36)
    mincho_name = font(MINCHO, 88)
    body = font(SANS_W3, 29)
    body_small = font(SANS_W3, 22)

    ink = (35, 35, 32, 255)
    muted = (88, 84, 76, 255)
    gold = (146, 110, 52, 255)

    draw.text((80, 48), "Masaya Takahashi Official Site", font=sans_small, fill=muted)
    draw.text((78, 142), "高橋正哉", font=mincho_name, fill=ink)
    draw.text((84, 254), "公認会計士／監査法人代表社員", font=sans, fill=gold)

    description = "上場企業・上場準備企業の会計監査、社外役員、M&A・財務DD・企業価値評価に関与。"
    lines = fit_text(draw, description, body, 620)
    y = 340
    for line in lines[:3]:
        draw.text((82, y), line, font=body, fill=ink)
        y += 48

    draw.line((82, 530, 586, 530), fill=(206, 192, 169, 255), width=1)
    draw.text((82, 556), "www.cpa-tm.com", font=body_small, fill=muted)
    draw.text((760, 580), "CPA / Governance / Capital Markets", font=body_small, fill=muted)

    canvas.convert("RGB").save(OUT, quality=95, optimize=True)


if __name__ == "__main__":
    main()
