import re


def classify_package(ocr_lines):
    """
    Classifies the package based on OCR text.

    Returns:
        retail
        wholesale
        multi_piece
        combination
        group
        e_commerce
    """

    text = " ".join(
        line.get("text", "")
        for line in ocr_lines
    ).lower()

    # E-commerce indicators
    ecommerce_keywords = [
        "add to cart",
        "buy now",
        "delivery",
        "seller",
        "online",
        "ratings",
        "reviews",
        "free delivery"
    ]

    if any(keyword in text for keyword in ecommerce_keywords):
        return "e_commerce"

    # Wholesale indicators
    wholesale_keywords = [
        "wholesale",
        "for institutional use",
        "for industrial use",
        "not for retail sale"
    ]

    if any(keyword in text for keyword in wholesale_keywords):
        return "wholesale"

    # Multi-piece indicators
    multipiece_patterns = [
        r"pack\s+of\s+\d+",
        r"set\s+of\s+\d+",
        r"multipack",
        r"multi\s*pack",
        r"\d+\s*pieces"
    ]

    if any(
        re.search(pattern, text)
        for pattern in multipiece_patterns
    ):
        return "multi_piece"

    # Combination package
    combination_keywords = [
        "combination pack",
        "combo pack",
        "combo"
    ]

    if any(keyword in text for keyword in combination_keywords):
        return "combination"

    # Group package
    group_keywords = [
        "group pack",
        "value pack"
    ]

    if any(keyword in text for keyword in group_keywords):
        return "group"

    # Default
    return "retail"