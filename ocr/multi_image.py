"""
Theme A - Multi-Image Aggregation (V2 - updated for new pipeline schema)
---------------------------------------------------------------------------
Updated to work with the new per-line status/flags/candidate_field
structure from ocr_pipeline.py V2. This is what Theme B/C should actually
call for a real product (which usually has several photos).
"""

from ocr_pipeline import run_ocr_pipeline


def aggregate_product_images(product_id, image_paths, languages=('en',),
                              cascade_mode=True, confidence_threshold=0.60):
    """
    Runs the OCR pipeline on every image belonging to one product.
    Uses cascade_mode by default now (adapts speed per image automatically)
    rather than forcing fast_mode - better default for batch/dataset use.

    Returns:
    {
        "product_id": "p75",
        "images_processed": 2,
        "per_image": { "front.jpg": {...full pipeline output...}, ... },
        "combined_lines": [ {..line.., "source_image": "front.jpg"}, ... ],
        "candidates_by_field": {
            "mrp": [ {text, confidence, source_image, status}, ... ],
            "date": [...],
            ...
        }
    }
    """
    per_image = {}
    combined_lines = []

    for path in image_paths:
        result = run_ocr_pipeline(
            path, keep_all_variants=False, languages=languages,
            cascade_mode=cascade_mode, confidence_threshold=confidence_threshold
        )
        per_image[path] = result

        for line in result["lines"]:
            tagged_line = dict(line)
            tagged_line["source_image"] = path
            combined_lines.append(tagged_line)

    # group lines by candidate_field - this is exactly what Theme B needs:
    # "give me every line across every photo of this product that looks
    # like it could be an MRP" instead of Theme B re-scanning raw text itself
    candidates_by_field = {}
    for line in combined_lines:
        field = line.get("candidate_field")
        if field:
            candidates_by_field.setdefault(field, []).append(line)

    # within each field, sort best-evidence-first (accepted status, then
    # confidence) so Theme B can just take [0] as its best guess and still
    # see the rest as alternates if it wants to cross-check
    status_rank = {"accepted": 0, "flagged": 1, "review": 2}
    for field in candidates_by_field:
        candidates_by_field[field].sort(
            key=lambda l: (status_rank.get(l["status"], 3), -l["confidence"])
        )

    return {
        "product_id": product_id,
        "images_processed": len(image_paths),
        "per_image": per_image,
        "combined_lines": combined_lines,
        "candidates_by_field": candidates_by_field,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python multi_image.py <product_id> <image1.jpg> [image2.jpg ...]")
        sys.exit(1)

    product_id = sys.argv[1]
    image_paths = sys.argv[2:]

    result = aggregate_product_images(product_id, image_paths)

    print(f"\nProduct: {product_id} | Images: {result['images_processed']}")
    print(f"Total combined lines: {len(result['combined_lines'])}\n")

    print("--- Best candidate per field (across all images) ---")
    for field, candidates in result["candidates_by_field"].items():
        best = candidates[0]
        print(f"  {field:15s}: \"{best['text']}\" "
              f"[{best['confidence']:.2f}, {best['status']}] (from {best['source_image']})")
        if len(candidates) > 1:
            print(f"                   ({len(candidates)-1} other candidate(s) also found)")
