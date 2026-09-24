"""Theme A image-quality helpers.
Returns measurable quality signals; never declares a legal violation.
"""
import cv2
import numpy as np


def analyze_image_quality(image_path):
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape[:2]
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    contrast = float(gray.std())
    mean_brightness = float(gray.mean())
    glare_ratio = float(np.mean(gray >= 245))
    tiny_image = min(h, w) < 700

    if blur_score < 80:
        blur_status = "high_blur"
    elif blur_score < 180:
        blur_status = "possible_blur"
    else:
        blur_status = "acceptable"

    if contrast < 25:
        contrast_status = "low_contrast"
    elif contrast < 45:
        contrast_status = "moderate_contrast"
    else:
        contrast_status = "acceptable"

    if glare_ratio > 0.08:
        glare_status = "high_glare"
    elif glare_ratio > 0.03:
        glare_status = "possible_glare"
    else:
        glare_status = "acceptable"

    return {
        "width": w,
        "height": h,
        "blur_score": round(blur_score, 2),
        "blur_status": blur_status,
        "contrast_score": round(contrast, 2),
        "contrast_status": contrast_status,
        "mean_brightness": round(mean_brightness, 2),
        "glare_ratio": round(glare_ratio, 4),
        "glare_status": glare_status,
        "tiny_image": tiny_image,
    }
