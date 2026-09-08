import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


def load_image(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {path}")
    return img


def to_grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def enhance_contrast(gray_img):
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    return clahe.apply(gray_img)


def denoise(gray_img):
    return cv2.fastNlMeansDenoising(gray_img, h=10)


def sharpen(gray_img):
    blurred = cv2.GaussianBlur(gray_img, (0, 0), sigmaX=3)
    return cv2.addWeighted(gray_img, 1.5, blurred, -0.5, 0)


def binarize(gray_img):
    return cv2.adaptiveThreshold(
        gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 15
    )


def upscale(img, scale=2.0):
    h, w = img.shape[:2]
    return cv2.resize(
        img, (int(w * scale), int(h * scale)),
        interpolation=cv2.INTER_CUBIC
    )


def deskew(gray_img):
    inverted = cv2.bitwise_not(gray_img)
    coords = np.column_stack(np.where(inverted > 50))
    if len(coords) < 20:
        return gray_img

    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle

    if abs(angle) < 0.5 or abs(angle) > 15:
        return gray_img

    h, w = gray_img.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    return cv2.warpAffine(
        gray_img, matrix, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )


def correct_curved_surface(img, strip_count=3):
    if strip_count < 1:
        raise ValueError("strip_count must be >= 1")

    h, _ = img.shape[:2]
    strip_height = max(1, h // strip_count)
    strips = []

    for i in range(strip_count):
        y_start = i * strip_height
        y_end = h if i == strip_count - 1 else (i + 1) * strip_height
        strips.append(img[y_start:y_end, :])

    return strips


def cap_max_dimension(img, max_dim=1400):
    if max_dim is None:
        return img
    if max_dim <= 0:
        raise ValueError("max_dim must be > 0 or None")

    h, w = img.shape[:2]
    longest = max(h, w)

    if longest <= max_dim:
        return img

    scale = max_dim / longest
    return cv2.resize(
        img, (int(w * scale), int(h * scale)),
        interpolation=cv2.INTER_AREA
    )


def image_quality(image):
    gray = to_grayscale(image)
    return {
        "width": int(image.shape[1]),
        "height": int(image.shape[0]),
        "mean_brightness": round(float(np.mean(gray)), 2),
        "contrast_score": round(float(np.std(gray)), 2),
        "blur_score": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 2)
    }


def generate_variants(
    image_path,
    max_dim=1400,
    enabled_variants=None,
    logger_instance=None
):
    log = logger_instance or logger

    original = cap_max_dimension(load_image(image_path), max_dim)
    log.debug("Image quality: %s", image_quality(original))

    gray = to_grayscale(original)

    builders = {
        "original": lambda: original,
        "grayscale_contrast": lambda: enhance_contrast(gray),
        "denoised_sharpened": lambda: sharpen(denoise(gray)),
        "binarized": lambda: binarize(enhance_contrast(gray)),
        "deskewed": lambda: deskew(gray),
        "upscaled": lambda: upscale(enhance_contrast(gray), 1.5),
    }

    names = list(builders) if enabled_variants is None else list(
        enabled_variants)
    unknown = set(names) - set(builders)
    if unknown:
        raise ValueError(f"Unknown preprocessing variants: {sorted(unknown)}")

    variants = {name: builders[name]() for name in names}
    log.debug("Generated variants: %s", list(variants))
    return variants


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python preprocessing.py <path_to_image>")
        sys.exit(1)

    variants = generate_variants(sys.argv[1])
    print(f"Generated {len(variants)} variants:")
    for name, img in variants.items():
        print(f"  {name}: shape={img.shape}")
        cv2.imwrite(f"variant_{name}.jpg", img)
