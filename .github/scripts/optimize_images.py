#!/usr/bin/env python3
"""Smaller delivery copies of heavy images (website audit, Nov 6, 2026: WEB-05 and WEB-06).

Run by hand when a source image changes: python3 .github/scripts/optimize_images.py
The source files are never changed; the copies sit next to them and are committed.

- logo.png (760x277) -> logo.webp, same size, used through <picture> with the PNG as fallback.
- heart-wakes.jpg / heart-engine.jpg -> .webp at the same size (PNG/JPG stay as fallback).
- favicon.ico -> 16, 32 and 48 px only (it carried 6 sizes up to 256 px, 156 KB).
- Share previews (og:image) for /awakening/, /passages/ and /woman-behind-the-scenes/:
  1200x630 JPGs like assets/story/ghostheart-share-1200x630.jpg instead of 2.5-4.4 MB PNGs.
"""
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / 'assets/wake-v3/img'
STORY = ROOT / 'assets/story'
SHARE = (1200, 630)


def webp(source: Path, quality: int, **extra) -> None:
    target = source.with_suffix('.webp')
    with Image.open(source) as im:
        im.load()
        im.save(target, format='WEBP', quality=quality, method=6, **extra)
    print(f'{target.relative_to(ROOT)}: {source.stat().st_size} -> {target.stat().st_size} bytes')


def favicon() -> None:
    path = ROOT / 'favicon.ico'
    with Image.open(path) as ico:
        big = max(ico.info.get('sizes', {ico.size}))
        if big[0] <= 48:
            print('favicon.ico: already 16/32/48 px, left as is')
            return
        ico.size = big
        ico.load()
        art = ico.convert('RGBA')
    before = path.stat().st_size
    art.save(path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])
    print(f'favicon.ico: {before} -> {path.stat().st_size} bytes')


def share_cover(source: Path, target: Path) -> None:
    """Trim the black frame around the art, then fill 1200x630 (centre crop)."""
    with Image.open(source) as im:
        art = im.convert('RGB')
    mask = art.convert('L').point(lambda v: 255 if v > 12 else 0)
    box = mask.getbbox()
    if box:
        art = art.crop(box)
    out = ImageOps.fit(art, SHARE, Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    save_jpg(out, source, target)


def share_contain(source: Path, target: Path) -> None:
    """Keep the whole picture (its lettering matters): fit it on a dimmed, blurred copy of itself."""
    with Image.open(source) as im:
        art = im.convert('RGB')
    back = ImageOps.fit(art, SHARE, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(28))
    back = Image.blend(back, Image.new('RGB', SHARE, (0, 0, 0)), 0.55)
    front = ImageOps.contain(art, SHARE, Image.Resampling.LANCZOS)
    back.paste(front, ((SHARE[0] - front.width) // 2, (SHARE[1] - front.height) // 2))
    save_jpg(back, source, target)


def save_jpg(image: Image.Image, source: Path, target: Path) -> None:
    for quality in (86, 82, 78, 74, 70):
        image.save(target, format='JPEG', quality=quality, optimize=True, progressive=True)
        if target.stat().st_size < 300_000:
            break
    print(f'{target.relative_to(ROOT)}: {source.stat().st_size} -> {target.stat().st_size} bytes (q{quality})')


def build() -> None:
    webp(IMG / 'logo.png', quality=82, alpha_quality=90)
    webp(IMG / 'heart-wakes.jpg', quality=72)
    webp(IMG / 'heart-engine.jpg', quality=72)
    favicon()
    share_cover(STORY / 'ghostheart-awakening-banner.png', STORY / 'ghostheart-awakening-share-1200x630.jpg')
    share_contain(STORY / 'ghostheart-rebel-in-the-rain.png', STORY / 'ghostheart-rebel-share-1200x630.jpg')


if __name__ == '__main__':
    build()
