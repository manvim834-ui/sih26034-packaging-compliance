import logging
import re
import easyocr

from preprocessing import generate_variants, image_quality

logger = logging.getLogger(__name__)

if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

_readers = {}


def get_reader(languages=("en",), gpu=False):
    if not languages:
        raise ValueError("languages must contain at least one language code")

    key = tuple(sorted(set(languages)))
    if key not in _readers:
        logger.info("Loading EasyOCR model for languages=%s", key)
        _readers[key] = easyocr.Reader(list(key), gpu=gpu, verbose=False)

    return _readers[key]


def run_ocr_on_variant(img, languages=("en",), source_variant=None, gpu=False):
    reader = get_reader(languages, gpu)
    results = reader.readtext(img)

    lines = []
    for bbox, text, confidence in results:
        text = text.strip()
        if not text:
            continue

        lines.append({
            "text": text,
            "confidence": round(float(confidence), 3),
            "bbox": [[float(x), float(y)] for x, y in bbox],
            "source_variant": source_variant
        })
    return lines


def score_variant_result(lines):
    if not lines:
        return 0.0
    avg = sum(x["confidence"] for x in lines) / len(lines)
    return avg * (1 + 0.05 * len(lines))


def normalize_text(text):
    return re.sub(r"\s+", "", text.lower())


def suspicious_text_flags(text):
    flags = []
    cleaned = text.strip()

    if not cleaned:
        return ["empty_text"]

    if re.search(r"\b(?:MRP|RS|INR)\b|₹", cleaned, re.I):
        if not re.search(r"\d", cleaned):
            flags.append("price_keyword_without_digits")

    if re.search(r"\b(?:NET|WT|WEIGHT|QTY|QUANTITY)\b", cleaned, re.I):
        if not re.search(r"\d", cleaned):
            flags.append("quantity_keyword_without_digits")

    if re.search(r"\bMRP\b", cleaned, re.I) and re.search(
        r"[0-9OIlSGB]", cleaned
    ):
        if re.search(r"[OIlSGB]", cleaned):
            flags.append("possible_digit_letter_confusion")

    if re.search(r"[^A-Za-z0-9\u0900-\u097F\s]{5,}", cleaned):
        flags.append("excessive_symbols")

    if len(cleaned) <= 2 and not re.search(
        r"[A-Za-z0-9\u0900-\u097F]", cleaned
    ):
        flags.append("mostly_non_text")

    return sorted(set(flags))


def classify_line(confidence, text, confidence_threshold=0.60):
    flags = suspicious_text_flags(text)

    if confidence < confidence_threshold:
        return "review", flags
    if flags:
        return "flagged", flags
    return "accepted", flags


def deduplicate_lines(all_lines):
    seen = {}

    for line in all_lines:
        key = normalize_text(line["text"])
        if not key:
            continue

        if key not in seen or line["confidence"] > seen[key]["confidence"]:
            seen[key] = line

    return list(seen.values())


def run_ocr_pipeline(
    image_path,
    keep_all_variants=True,
    languages=("en",),
    fast_mode=False,
    confidence_threshold=0.60,
    max_image_dimension=1400,
    enabled_variants=None,
    gpu=False
):
    logger.info(
        "OCR start image=%s languages=%s fast_mode=%s threshold=%.2f",
        image_path, languages, fast_mode, confidence_threshold
    )

    if not 0 <= confidence_threshold <= 1:
        raise ValueError("confidence_threshold must be between 0 and 1")

    variants = generate_variants(
        image_path,
        max_dim=max_image_dimension,
        enabled_variants=enabled_variants,
        logger_instance=logger
    )

    if fast_mode:
        variants = {
            k: v for k, v in variants.items()
            if k in {"original", "grayscale_contrast"}
        }

    if not variants:
        raise ValueError("No preprocessing variants available")

    variant_results = {}
    variant_scores = {}

    for name, img in variants.items():
        logger.debug("Running OCR on variant=%s", name)

        lines = run_ocr_on_variant(
            img, languages, source_variant=name, gpu=gpu
        )

        for line in lines:
            status, flags = classify_line(
                line["confidence"],
                line["text"],
                confidence_threshold
            )
            line["status"] = status
            line["flags"] = flags

        variant_results[name] = lines
        variant_scores[name] = score_variant_result(lines)

        logger.info(
            "Variant=%s lines=%d score=%.3f",
            name, len(lines), variant_scores[name]
        )

    best_variant = max(variant_scores, key=variant_scores.get)

    all_lines = [
        line for lines in variant_results.values()
        for line in lines
    ]

    merged_lines = deduplicate_lines(all_lines)
    merged_lines.sort(
        key=lambda x: x["bbox"][0][1] if x["bbox"] else 0
    )

    overall_confidence = round(
        sum(x["confidence"] for x in merged_lines) / len(merged_lines),
        3
    ) if merged_lines else 0.0

    review_count = sum(x["status"] == "review" for x in merged_lines)
    flagged_count = sum(x["status"] == "flagged" for x in merged_lines)

    if not merged_lines:
        pipeline_status = "no_text_detected"
    elif review_count or flagged_count:
        pipeline_status = "review"
    else:
        pipeline_status = "success"

    # Quality is calculated from the original image variant without another
    # OCR call. This avoids adding meaningful runtime.
    original_img = next(
        img for name, img in variants.items() if name == "original"
    )
    quality = image_quality(original_img)

    output = {
        "status": pipeline_status,
        "image_path": image_path,
        "images_processed": 1,
        "language_mode": list(languages),
        "best_variant": best_variant,
        "best_variant_score": round(variant_scores[best_variant], 3),
        "overall_confidence": overall_confidence,
        "confidence_threshold": confidence_threshold,
        "review_count": review_count,
        "flagged_count": flagged_count,
        "image_quality": quality,
        "lines": merged_lines,
        "config": {
            "fast_mode": fast_mode,
            "max_image_dimension": max_image_dimension,
            "enabled_variants": list(variants.keys())
        }
    }

    if keep_all_variants:
        output["all_variants_raw"] = variant_results

    logger.info(
        "OCR complete image=%s status=%s lines=%d confidence=%.3f",
        image_path, pipeline_status, len(merged_lines), overall_confidence
    )

    return output


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ocr_pipeline.py <path_to_image>")
        sys.exit(1)

    result = run_ocr_pipeline(sys.argv[1], keep_all_variants=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
