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
    """
    IMPROVED SCORING (was: pure average confidence).
    Now rewards:
    - higher confidence (as before)
    - more ACCEPTED lines specifically (not just any lines - a variant full
      of flagged/suspicious text shouldn't score as well as one with clean
      accepted reads)
    - a bonus for finding lines that look like actual LMPC-relevant
      candidates (MRP/date/quantity) - a variant that reads 3 useful
      label fields is more valuable than one that reads 10 nutrition-table
      numbers, even at similar average confidence.
    """
    if not lines:
        return 0.0
    accepted = [l for l in lines if l.get("status") == "accepted"]
    avg_confidence = sum(l["confidence"] for l in lines) / len(lines)
    candidate_bonus = sum(1 for l in lines if l.get("candidate_field")) * 0.1
    return avg_confidence * (1 + 0.05 * len(accepted)) + candidate_bonus
 
 
def variant_agreement_bonus(variant_results):
    """
    NEW: cross-variant agreement scoring. If two different variants
    independently read the same text, that's stronger evidence than one
    variant reading something no other variant confirms - same logic as
    inter-rater agreement. Returns a dict of {variant_name: bonus_score}
    to add to that variant's base score.
    """
    from collections import Counter
    text_counts = Counter()
    for lines in variant_results.values():
        seen_in_this_variant = set(normalize_text(l["text"]) for l in lines if l["text"])
        for t in seen_in_this_variant:
            text_counts[t] += 1
 
    bonus = {}
    for name, lines in variant_results.items():
        agreement_score = 0.0
        for line in lines:
            key = normalize_text(line["text"])
            if key and text_counts[key] > 1:
                agreement_score += 0.05  # small bonus per line confirmed by another variant
        bonus[name] = agreement_score
    return bonus
 
 
def normalize_text(text):
    return re.sub(r"\s+", "", text.lower())
 
 
# Deliberately loose patterns - this is NOT field extraction (that's Theme
# B's job). This only tags a line as "this LOOKS like it might be an MRP/
# date/quantity candidate" so Theme B knows where to look first, and so
# Theme A's own scoring can reward variants that find these. Theme B still
# does the real parsing/validation against the actual LMPC rules.
CANDIDATE_PATTERNS = {
    "mrp": re.compile(r"\b(?:MRP|M\.?R\.?P\.?|RS|INR)\b|₹", re.I),
    "date": re.compile(r"\b\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}\b|\b(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s*\d{2,4}\b", re.I),
    "net_quantity": re.compile(r"\b\d+(?:\.\d+)?\s*(?:g|kg|ml|l|gm|gms)\b", re.I),
    "manufacturer": re.compile(r"\b(?:MFD|MFG|MANUFACTURED|PACKED|MARKETED)\s*(?:BY)?\b", re.I),
    "consumer_care": re.compile(r"\b(?:CUSTOMER|CONSUMER)\s*CARE\b|\btoll[\s-]?free\b|@[\w.]+\.\w+", re.I),
}
 
 
def tag_candidate_field(text):
    """Returns the first matching candidate field label, or None."""
    for field, pattern in CANDIDATE_PATTERNS.items():
        if pattern.search(text):
            return field
    return None
 
 
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
    cascade_mode=False,
    cascade_quality_threshold=0.65,
    confidence_threshold=0.60,
    max_image_dimension=1400,
    enabled_variants=None,
    curved_mode=False,
    gpu=False
):
    """
    cascade_mode: NEW. If True, runs the two cheap variants first
    (original + grayscale_contrast). If their combined result already looks
    good (score above cascade_quality_threshold), STOPS there - skipping
    the other 4 variants entirely. Only escalates to the full variant set
    if the cheap pass looks weak. This gives speed on easy images and
    thoroughness on hard ones, instead of always paying the cost of all
    variants (or always limiting to just 2, which is what fast_mode does).
 
    fast_mode and cascade_mode are mutually exclusive - fast_mode ALWAYS
    uses only 2 variants (fixed, predictable speed). cascade_mode adapts
    per-image. Use fast_mode for live demos where you need a hard speed
    guarantee; use cascade_mode for batch dataset processing where you
    want speed AND accuracy without manually choosing per image.
    """
    logger.info(
        "OCR start image=%s languages=%s fast_mode=%s cascade_mode=%s threshold=%.2f",
        image_path, languages, fast_mode, cascade_mode, confidence_threshold
    )
 
    if not 0 <= confidence_threshold <= 1:
        raise ValueError("confidence_threshold must be between 0 and 1")
    if fast_mode and cascade_mode:
        raise ValueError("fast_mode and cascade_mode are mutually exclusive - choose one")
 
    all_variants = generate_variants(
        image_path,
        max_dim=max_image_dimension,
        enabled_variants=enabled_variants,
        curved_mode=curved_mode,
        logger_instance=logger
    )
 
    if fast_mode:
        variants_to_run = {k: v for k, v in all_variants.items()
                            if k in {"original", "grayscale_contrast"}}
    elif cascade_mode:
        # Stage 1: cheap variants only
        cheap_names = {"original", "grayscale_contrast"}
        variants_to_run = {k: v for k, v in all_variants.items() if k in cheap_names}
    else:
        variants_to_run = all_variants
 
    if not variants_to_run:
        raise ValueError("No preprocessing variants available")
 
    def run_variants(variant_dict):
        results, scores = {}, {}
        for name, img in variant_dict.items():
            logger.debug("Running OCR on variant=%s", name)
            lines = run_ocr_on_variant(img, languages, source_variant=name, gpu=gpu)
            for line in lines:
                status, flags = classify_line(line["confidence"], line["text"], confidence_threshold)
                line["status"] = status
                line["flags"] = flags
                line["candidate_field"] = tag_candidate_field(line["text"])
            results[name] = lines
            scores[name] = score_variant_result(lines)
            logger.info("Variant=%s lines=%d score=%.3f", name, len(lines), scores[name])
        return results, scores
 
    variant_results, variant_scores = run_variants(variants_to_run)
 
    escalated = False
    if cascade_mode:
        # FIXED: use a direct average-confidence measure for the escalation
        # decision, not the composite "score" (which includes candidate-field
        # bonuses and can look artificially healthy even when raw OCR
        # confidence is actually poor - found this by testing on a genuinely
        # hard image where it should have escalated but didn't).
        cheap_lines = [l for lines in variant_results.values() for l in lines]
        cheap_avg_confidence = (
            sum(l["confidence"] for l in cheap_lines) / len(cheap_lines)
            if cheap_lines else 0.0
        )
        if cheap_avg_confidence < cascade_quality_threshold:
            logger.info(
                "Cascade escalating: cheap-pass avg confidence %.3f < threshold %.3f",
                cheap_avg_confidence, cascade_quality_threshold
            )
            escalated = True
            remaining = {k: v for k, v in all_variants.items() if k not in variants_to_run}
            more_results, more_scores = run_variants(remaining)
            variant_results.update(more_results)
            variant_scores.update(more_scores)
 
    # cross-variant agreement bonus (only meaningful once we have 2+ variants)
    if len(variant_results) > 1:
        agreement_bonus = variant_agreement_bonus(variant_results)
        for name in variant_scores:
            variant_scores[name] += agreement_bonus.get(name, 0.0)
 
    best_variant = max(variant_scores, key=variant_scores.get)
 
    all_lines = [line for lines in variant_results.values() for line in lines]
    merged_lines = deduplicate_lines(all_lines)
    merged_lines.sort(key=lambda x: x["bbox"][0][1] if x["bbox"] else 0)
 
    overall_confidence = round(
        sum(x["confidence"] for x in merged_lines) / len(merged_lines), 3
    ) if merged_lines else 0.0
 
    review_count = sum(x["status"] == "review" for x in merged_lines)
    flagged_count = sum(x["status"] == "flagged" for x in merged_lines)
 
    if not merged_lines:
        pipeline_status = "no_text_detected"
    elif review_count or flagged_count:
        pipeline_status = "review"
    else:
        pipeline_status = "success"
 
    # FIXED BUG: no longer assumes "original" is always present. Falls back
    # to whichever variant IS available if "original" wasn't in the enabled set.
    if "original" in all_variants:
        quality_img = all_variants["original"]
    else:
        quality_img = next(iter(all_variants.values()))
    quality = image_quality(quality_img)
 
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
            "cascade_mode": cascade_mode,
            "cascade_escalated": escalated,
            "max_image_dimension": max_image_dimension,
            "enabled_variants": list(variant_results.keys())
        }
    }
 
    if keep_all_variants:
        output["all_variants_raw"] = variant_results
 
    logger.info(
        "OCR complete image=%s status=%s lines=%d confidence=%.3f escalated=%s",
        image_path, pipeline_status, len(merged_lines), overall_confidence, escalated
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
