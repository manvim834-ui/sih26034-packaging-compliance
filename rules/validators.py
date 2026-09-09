import re


def validate_manufacturer_info(value):

    if not value:
        return False

    text = str(value).strip().lower()

    qualifying_words = [
        "manufactured by",
        "packed by",
        "imported by",
        "manufacturer",
        "mfd by",
        "mfg by",
        "marketed by"
    ]

    return (
        len(text) > 2
        and any(word in text for word in qualifying_words)
    )


def validate_generic_name(value):

    if not value:
        return False

    return len(str(value).strip()) > 1


def parse_quantity(value):

    if not value:
        return None

    pattern = (
        r"^\s*(\d+(?:\.\d+)?)\s*"
        r"(kg|g|mg|l|ml|litre|liter|litres|liters|cm|m|"
        r"dozen|gross|score)"
        r"\s*$"
    )

    match = re.match(
        pattern,
        str(value),
        re.IGNORECASE
    )

    if not match:
        return None

    number = float(match.group(1))
    unit = match.group(2).lower()

    return number, unit


def validate_net_quantity(value):

    parsed = parse_quantity(value)

    if parsed is None:
        return False

    number, unit = parsed

    # Non-SI units prohibited
    if unit in ["dozen", "gross", "score"]:
        return False

    # Weight
    if unit == "mg":
        return True

    if unit == "g":
        return number < 1000

    if unit == "kg":
        return number >= 1

    # Volume
    if unit == "ml":
        return number < 1000

    if unit in ["l", "litre", "liter", "litres", "liters"]:
        return number >= 1

    # Length
    if unit == "cm":
        return number < 100

    if unit == "m":
        return number >= 1

    return False


def validate_mfg_date(value):

    if not value:
        return False

    value = str(value).strip()

    patterns = [
        r"^(0?[1-9]|1[0-2])[/-]\d{4}$",
        r"^\d{4}[/-](0?[1-9]|1[0-2])$",
        r"^(0?[1-9]|1[0-2])[/-]\d{2}$",
        r"^\d{1,2}[/-]\d{1,2}[/-]\d{4}$"
    ]

    return any(
        re.match(pattern, value)
        for pattern in patterns
    )


def validate_mrp(value):

    if value is None:
        return False

    cleaned = str(value).strip()

    cleaned = re.sub(
        r"^(₹|Rs\.?|INR)\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    match = re.fullmatch(
        r"\d+(?:\.\d{1,2})?",
        cleaned
    )

    if not match:
        return False

    return float(cleaned) > 0


def validate_consumer_care(value):

    if not value:
        return False

    text = str(value).strip()

    # Accept normal and hyphenated phone numbers
    digits = re.sub(r"\D", "", text)

    has_phone = 7 <= len(digits) <= 15

    return (
        len(text) > 2
        and has_phone
    )


def validate_unit_sale_price(value):

    if value is None:
        return False

    cleaned = str(value).strip()

    cleaned = re.sub(
        r"^(₹|Rs\.?|INR)\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    match = re.fullmatch(
        r"\d+(?:\.\d{1,2})?",
        cleaned
    )

    if not match:
        return False

    return float(cleaned) >= 0


def validate_country_of_origin(value):

    if not value:
        return False

    return len(str(value).strip()) > 1


VALIDATORS = {

    "validate_manufacturer_info":
        validate_manufacturer_info,

    "validate_generic_name":
        validate_generic_name,

    "validate_net_quantity":
        validate_net_quantity,

    "validate_mfg_date":
        validate_mfg_date,

    "validate_mrp":
        validate_mrp,

    "validate_consumer_care":
        validate_consumer_care,

    "validate_unit_sale_price":
        validate_unit_sale_price,

    "validate_country_of_origin":
        validate_country_of_origin
}