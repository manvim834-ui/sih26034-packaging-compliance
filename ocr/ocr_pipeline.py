"""
Theme A - OCR Pipeline (Improved V1)

Important:
- This remains an OCR layer, not legal-rule validation.
- Field extraction remains downstream.
- The public run_ocr_pipeline(...) function keeps the existing contract
  while adding better evidence handling.
"""

import logging
import re
from collections import Counter

import easyocr

from .preprocessing import generate_variants, image_quality

logger = logging.getLogger(__name__)

if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

_readers = {}


def get_reader(languages=("en",), gpu=False):
    if not languages:
        raise ValueError("languages must contain at least one language code")

    key = (tuple(sorted(set(languages))), bool(gpu))

    if key not in _readers:
        logger.info(
            "Loading EasyOCR model for languages=%s gpu=%s", key[0], gpu)
        _readers[key] = easyocr.Reader(
            list(key[0]), gpu=gpu, verbose=False
        )

    return _readers[key]


def run_ocr_on_variant(img, languages=("en",), source_variant=None, gpu=False):
    reader = get_reader(languages, gpu)
    results = reader.readtext(img)

    lines = []

    for bbox, text, confidence in results:
        text = text.strip()
        if not text:
            continue

        lines.append(
            {
                "text": text,
                "confidence": round(float(confidence), 3),
                "bbox": [[float(x), float(y)] for x, y in bbox],
                "source_variant": source_variant,
            }
        )

    return lines


def normalize_text(text):
    # Used only for agreement/deduplication, not for changing OCR text.
    return re.sub(r"\s+", "", text.lower())


def _alnum_count(text):
    return sum(ch.isalnum() or "\u0900" <= ch <= "\u097F" for ch in text)


def _symbol_ratio(text):
    if not text:
        return 1.0
    return sum(
        not (ch.isalnum() or ch.isspace() or "\u0900" <= ch <= "\u097F")
        for ch in text
    ) / len(text)


CANDIDATE_PATTERNS = {
    "mrp": re.compile(
        r"\b(?:MRP|M\.?R\.?P\.?|RS|INR)\b|₹",
        re.I,
    ),
    "date": re.compile(
        r"\b\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}\b"
        r"|\b(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)"
        r"[A-Z]*\s*\d{2,4}\b",
        re.I,
    ),
    "net_quantity": re.compile(
        r"\b\d+(?:\.\d+)?\s*(?:g|kg|ml|l|gm|gms)\b",
        re.I,
    ),
    "manufacturer": re.compile(
        r"\b(?:MFD|MFG|MANUFACTURED|PACKED|MARKETED)\s*(?:BY)?\b",
        re.I,
    ),
    "consumer_care": re.compile(
        r"\b(?:CUSTOMER|CONSUMER)\s*CARE\b"
        r"|\btoll[\s-]?free\b"
        r"|@[\w.]+\.\w+",
        re.I,
    ),
    "ingredients": re.compile(
        r"\b(?:INGREDIENTS?|COMPOSITION|CONTAINS|INGREDIENTS LIST)\b",
        re.I,
    ),
}


def tag_candidate_fields(text):
    """
    Return all relevant candidate fields rather than only the first match.
    This is still lightweight tagging, not final field extraction.
    """
    return [
        field
        for field, pattern in CANDIDATE_PATTERNS.items()
        if pattern.search(text)
    ]


def tag_candidate_field(text):
    fields = tag_candidate_fields(text)
    return fields[0] if fields else None


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

    if re.search(r"\bMRP\b", cleaned, re.I):
        if re.search(r"[OIlSGB]", cleaned):
            flags.append("possible_digit_letter_confusion")

    if _symbol_ratio(cleaned) > 0.35 and _alnum_count(cleaned) < 3:
        flags.append("excessive_symbols")

    if len(cleaned) <= 2 and _alnum_count(cleaned) == 0:
        flags.append("mostly_non_text")

    # Very short isolated detections are often OCR noise. Do not delete them;
    # flag them so downstream logic can make the final decision.
    if len(cleaned) <= 2 and _alnum_count(cleaned) > 0:
        flags.append("very_short_text")

    return sorted(set(flags))


def classify_line(confidence, text, confidence_threshold=0.60):
    flags = suspicious_text_flags(text)

    if confidence < confidence_threshold:
        return "review", flags

    if flags:
        return "flagged", flags

    return "accepted", flags


def _bbox_center_y(line):
    bbox = line.get("bbox") or []
    if not bbox:
        return 0.0
    return sum(float(p[1]) for p in bbox) / len(bbox)


def _bbox_center_x(line):
    bbox = line.get("bbox") or []
    if not bbox:
        return 0.0
    return sum(float(p[0]) for p in bbox) / len(bbox)


def _bbox_iou(a, b):
    """
    Axis-aligned IoU approximation used only for duplicate evidence.
    It does not alter OCR coordinates.
    """
    if not a or not b:
        return 0.0

    ax1 = min(p[0] for p in a)
    ay1 = min(p[1] for p in a)
    ax2 = max(p[0] for p in a)
    ay2 = max(p[1] for p in a)

    bx1 = min(p[0] for p in b)
    by1 = min(p[1] for p in b)
    bx2 = max(p[0] for p in b)
    by2 = max(p[1] for p in b)

    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)

    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0

    inter = (ix2 - ix1) * (iy2 - iy1)
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter

    return inter / union if union else 0.0


def deduplicate_lines(all_lines):
    """
    Deduplicate repeated OCR detections while preserving evidence.

    Two lines are treated as duplicates when normalized text is identical.
    For identical text, keep the strongest detection and record how many
    variants supported it.
    """
    groups = {}

    for line in all_lines:
        key = normalize_text(line["text"])
        if not key:
            continue
        groups.setdefault(key, []).append(line)

    merged = []

    for key, group in groups.items():
        best = max(
            group,
            key=lambda x: (
                float(x.get("confidence", 0.0)),
                x.get("status") == "accepted",
            ),
        )
        best = dict(best)

        sources = sorted(
            {
                str(x.get("source_variant"))
                for x in group
                if x.get("source_variant")
            }
        )
        best["variant_support_count"] = len(group)
        best["supporting_variants"] = sources

        # Agreement is evidence, not a replacement for OCR confidence.
        if len(group) >= 2:
            best["agreement"] = True
        else:
            best["agreement"] = False

        merged.append(best)

    return merged


def score_variant_result(lines):
    """
    Score a variant using:
    - average OCR confidence
    - useful accepted detections
    - candidate fields
    - cross-variant support when available

    The score is ONLY for choosing a primary variant. It is not a correctness
    probability.
    """
    if not lines:
        return 0.0

    avg_conf = sum(l["confidence"] for l in lines) / len(lines)
    accepted = sum(l.get("status") == "accepted" for l in lines)
    candidates = sum(bool(l.get("candidate_fields")) for l in lines)
    noisy = sum(
        bool(l.get("flags"))
        for l in lines
    )

    useful_score = (
        avg_conf
        + min(0.25, accepted * 0.025)
        + min(0.30, candidates * 0.05)
        - min(0.20, noisy * 0.015)
    )

    return max(0.0, useful_score)


def variant_agreement_bonus(variant_results):
    counts = Counter()

    for lines in variant_results.values():
        seen = {
            normalize_text(l["text"])
            for l in lines
            if l.get("text")
        }
        counts.update(seen)

    bonus = {}

    for name, lines in variant_results.items():
        score = 0.0
        for line in lines:
            key = normalize_text(line["text"])
            if key and counts[key] > 1:
                score += min(0.20, 0.05 * (counts[key] - 1))
        bonus[name] = score

    return bonus


def _postprocess_lines(lines, confidence_threshold):
    """
    Add metadata only. OCR text is never silently corrected here.
    """
    processed = []

    for line in lines:
        item = dict(line)

        status, flags = classify_line(
            item["confidence"],
            item["text"],
            confidence_threshold,
        )

        item["status"] = status
        item["flags"] = flags
        item["candidate_fields"] = tag_candidate_fields(item["text"])
        item["candidate_field"] = (
            item["candidate_fields"][0]
            if item["candidate_fields"]
            else None
        )

        processed.append(item)

    return processed


def _average_confidence(lines):
    if not lines:
        return 0.0
    return sum(l["confidence"] for l in lines) / len(lines)


def run_ocr_pipeline(
    image_path,
    keep_all_variants=True,
    languages=("en",),
    fast_mode=False,
    cascade_mode=False,
    cascade_quality_threshold=0.65,
    confidence_threshold=0.60,
    max_image_dimension=1400,
    enabled_variants=None,
    curved_mode=False,
    gpu=False,
):
    """
    Main OCR entry point.

    Compatibility:
    - Existing callers can keep using the same function and parameters.
    - Default language remains English.
    - Product/image grouping remains outside this function.

    New behavior:
    - better variant scoring
    - multi-variant agreement metadata
    - all candidate fields per OCR line
    - evidence-preserving deduplication
    - no silent OCR text correction
    """
    if not 0 <= confidence_threshold <= 1:
        raise ValueError("confidence_threshold must be between 0 and 1")

    if not 0 <= cascade_quality_threshold <= 1:
        raise ValueError("cascade_quality_threshold must be between 0 and 1")

    if fast_mode and cascade_mode:
        raise ValueError(
            "fast_mode and cascade_mode are mutually exclusive - choose one"
        )

    logger.info(
        "OCR start image=%s languages=%s fast_mode=%s cascade_mode=%s",
        image_path,
        languages,
        fast_mode,
        cascade_mode,
    )

    all_variants = generate_variants(
        image_path,
        max_dim=max_image_dimension,
        enabled_variants=enabled_variants,
        curved_mode=curved_mode,
        logger_instance=logger,
    )

    if fast_mode:
        names = {"original", "grayscale_contrast"}
        variants_to_run = {
            k: v for k, v in all_variants.items() if k in names
        }
    elif cascade_mode:
        names = {"original", "grayscale_contrast"}
        variants_to_run = {
            k: v for k, v in all_variants.items() if k in names
        }
    else:
        variants_to_run = all_variants

    if not variants_to_run:
        raise ValueError("No preprocessing variants available")

    def run_variants(variant_dict):
        results = {}
        scores = {}

        for name, img in variant_dict.items():
            raw_lines = run_ocr_on_variant(
                img,
                languages=languages,
                source_variant=name,
                gpu=gpu,
            )
            lines = _postprocess_lines(
                raw_lines,
                confidence_threshold,
            )
            results[name] = lines
            scores[name] = score_variant_result(lines)

            logger.info(
                "Variant=%s lines=%d score=%.3f avg_conf=%.3f",
                name,
                len(lines),
                scores[name],
                _average_confidence(lines),
            )

        return results, scores

    variant_results, variant_scores = run_variants(variants_to_run)

    escalated = False

    if cascade_mode:
        cheap_lines = [
            l for lines in variant_results.values() for l in lines
        ]
        cheap_avg = _average_confidence(cheap_lines)

        if cheap_avg < cascade_quality_threshold:
            escalated = True
            remaining = {
                k: v
                for k, v in all_variants.items()
                if k not in variants_to_run
            }

            if remaining:
                more_results, more_scores = run_variants(remaining)
                variant_results.update(more_results)
                variant_scores.update(more_scores)

    if len(variant_results) > 1:
        agreement_bonus = variant_agreement_bonus(variant_results)
        for name in variant_scores:
            variant_scores[name] += agreement_bonus.get(name, 0.0)

    best_variant = max(variant_scores, key=variant_scores.get)

    all_lines = [
        line for lines in variant_results.values() for line in lines
    ]

    merged_lines = deduplicate_lines(all_lines)

    # Natural reading order. This is approximate because package text can be
    # multi-column; downstream field extraction should use bbox when needed.
    merged_lines.sort(
        key=lambda x: (_bbox_center_y(x), _bbox_center_x(x))
    )

    overall_confidence = round(
        _average_confidence(merged_lines), 3
    )

    review_count = sum(
        x["status"] == "review" for x in merged_lines
    )
    flagged_count = sum(
        x["status"] == "flagged" for x in merged_lines
    )

    if not merged_lines:
        pipeline_status = "no_text_detected"
    elif review_count or flagged_count:
        pipeline_status = "review"
    else:
        pipeline_status = "success"

    quality_img = (
        all_variants["original"]
        if "original" in all_variants
        else next(iter(all_variants.values()))
    )

    output = {
        "status": pipeline_status,
        "image_path": str(image_path),
        "images_processed": 1,
        "language_mode": list(languages),
        "best_variant": best_variant,
        "best_variant_score": round(variant_scores[best_variant], 3),
        "overall_confidence": overall_confidence,
        "confidence_threshold": confidence_threshold,
        "review_count": review_count,
        "flagged_count": flagged_count,
        "image_quality": image_quality(quality_img),
        "lines": merged_lines,
        "config": {
            "fast_mode": fast_mode,
            "cascade_mode": cascade_mode,
            "cascade_escalated": escalated,
            "max_image_dimension": max_image_dimension,
            "enabled_variants": list(variant_results.keys()),
        },
    }

    if keep_all_variants:
        output["all_variants_raw"] = variant_results

    logger.info(
        "OCR complete image=%s status=%s lines=%d confidence=%.3f",
        image_path,
        pipeline_status,
        len(merged_lines),
        overall_confidence,
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
