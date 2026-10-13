"""Create web delivery copies without modifying the approved source artwork."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'assets/story/ghostheart-scars-rooftop-rain.png'


def build():
    with Image.open(SOURCE) as original:
        for label, width in [('desktop', original.width), ('mobile', 1000)]:
            height = round(original.height * width / original.width)
            image = original.resize((width, height), Image.Resampling.LANCZOS)
            target = SOURCE.with_name(f'{SOURCE.stem}-{label}-v1.webp')
            image.save(target, format='WEBP', quality=88, method=6)
            print(f'{target.name}: {width}x{height}, {target.stat().st_size} bytes')


if __name__ == '__main__':
    build()
