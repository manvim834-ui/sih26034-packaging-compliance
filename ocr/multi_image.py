"""
Theme A - Multi-image OCR aggregation (Improved V1)

This module does NOT perform product-wise compliance evaluation.
It simply runs the OCR pipeline for multiple photos belonging to the same
product and preserves the source image for every OCR line.

The public aggregate_product_images(...) API is kept compatible.
"""

from .ocr_pipeline import run_ocr_pipeline


def aggregate_product_images(
    product_id,
    image_paths,
    languages=("en",),
    cascade_mode=True,
    fast_mode=False,
    confidence_threshold=0.60,
    gpu=False,
    enabled_variants=None,
):
    """
    Run OCR on every supplied image and aggregate evidence.

    Important:
    - product_id is only an identifier/group label here.
    - No assumption is made that images are front/back/etc.
    - Each OCR line keeps source_image so downstream code can trace evidence.
    """
    if fast_mode:
        cascade_mode = False

    per_image = {}
    combined_lines = []

    for path in image_paths:
        result = run_ocr_pipeline(
            path,
            keep_all_variants=False,
            languages=languages,
            cascade_mode=cascade_mode,
            fast_mode=fast_mode,
            confidence_threshold=confidence_threshold,
            gpu=gpu,
            enabled_variants=enabled_variants,
        )

        per_image[str(path)] = result

        for line in result["lines"]:
            tagged_line = dict(line)
            tagged_line["source_image"] = str(path)
            combined_lines.append(tagged_line)

    # Group by every candidate field. This keeps one OCR line available for
    # multiple downstream purposes if it contains multiple useful keywords.
    candidates_by_field = {}

    for line in combined_lines:
        fields = line.get("candidate_fields") or []

        # Backward-compatible fallback for older OCR output.
        if not fields and line.get("candidate_field"):
            fields = [line["candidate_field"]]

        for field in fields:
            candidates_by_field.setdefault(field, []).append(line)

    status_rank = {
        "accepted": 0,
        "flagged": 1,
        "review": 2,
    }

    for field, candidates in candidates_by_field.items():
        candidates.sort(
            key=lambda line: (
                status_rank.get(line.get("status"), 3),
                -float(line.get("confidence", 0.0)),
                -int(line.get("variant_support_count", 1)),
            )
        )

    return {
        "product_id": product_id,
        "images_processed": len(image_paths),
        "per_image": per_image,
        "combined_lines": combined_lines,
        "candidates_by_field": candidates_by_field,
    }


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 3:
        print(
            "Usage: python multi_image.py <product_id> "
            "<image1.jpg> [image2.jpg ...]"
        )
        sys.exit(1)

    product_id = sys.argv[1]
    image_paths = sys.argv[2:]

    result = aggregate_product_images(product_id, image_paths)

    print(
        f"\nProduct: {product_id} | "
        f"Images: {result['images_processed']}"
    )
    print(
        f"Total combined lines: {len(result['combined_lines'])}\n"
    )

    print("--- Best candidate per field ---")
    for field, candidates in result["candidates_by_field"].items():
        if not candidates:
            continue
        best = candidates[0]
        print(
            f"  {field:15s}: \"{best['text']}\" "
            f"[{best['confidence']:.2f}, {best['status']}] "
            f"(from {best['source_image']})"
        )
