from pathlib import Path

from PIL import Image, ImageOps

THUMBNAIL_WIDTH = 640
THUMBS_DIR_NAME = "thumbs"


def get_thumbnail_path(image_path: Path, works_assets_dir: Path) -> Path:
    return works_assets_dir / THUMBS_DIR_NAME / f"{image_path.stem}.webp"


def create_thumbnail(image_path: Path, works_assets_dir: Path, width: int = THUMBNAIL_WIDTH) -> Path:
    thumbs_dir = works_assets_dir / THUMBS_DIR_NAME
    thumbs_dir.mkdir(parents=True, exist_ok=True)
    thumbnail_path = get_thumbnail_path(image_path, works_assets_dir)

    with Image.open(image_path) as source_image:
        normalized = ImageOps.exif_transpose(source_image)
        if normalized.width > width:
            ratio = width / normalized.width
            target_height = max(1, int(normalized.height * ratio))
            resized = normalized.resize((width, target_height), Image.Resampling.LANCZOS)
        else:
            resized = normalized.copy()

        has_alpha = "A" in resized.getbands()
        target_mode = "RGBA" if has_alpha else "RGB"

        if resized.mode != target_mode:
            resized = resized.convert(target_mode)

        resized.save(thumbnail_path, format="WEBP", quality=80, method=6)

    return thumbnail_path
