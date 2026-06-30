from PIL import Image, ImageOps, ImageFilter

def crop_image(image: Image.Image, crop: dict, normalized=False):

    if normalized:
        x = int(crop["x"] * image.width)
        y = int(crop["y"] * image.height)
        w = int(crop["w"] * image.width)
        h = int(crop["h"] * image.height)
    else:
        x = crop["x"]
        y = crop["y"]
        w = crop["w"]
        h = crop["h"]

    return image.crop((x, y, x + w, y + h))


def preprocess_for_ocr(image: Image.Image, upscale=4, threshold=160):

    if upscale > 1:
        image = image.resize(
            (image.width * upscale, image.height * upscale),
            Image.Resampling.LANCZOS
        )

    image = image.convert("L")
    image = ImageOps.autocontrast(image)
    image = image.filter(ImageFilter.SHARPEN)

    image = image.point(lambda p: 255 if p > threshold else 0)

    return image
