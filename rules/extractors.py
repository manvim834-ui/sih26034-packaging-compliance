import re


def clean_text(text):
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def extract_mrp(text):
    pattern = (
        r"(?:M\.?\s*R\.?\s*P\.?|"
        r"MAXIMUM\s+RETAIL\s+PRICE|"
        r"MAX\.?\s*RETAIL\s+PRICE)"
        r"\s*[:\-]?\s*"
        r"(?:₹|Rs\.?|INR)?\s*"
        r"(\d+(?:\.\d{1,2})?)"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        value = match.group(1)

        # Check tax-inclusive wording
        tax_inclusive = bool(
            re.search(
                r"inclusive\s+of\s+all\s+taxes|"
                r"incl\.?\s*(?:of\s*)?all\s+taxes",
                text,
                re.IGNORECASE
            )
        )

        return {
            "value": value,
            "taxes_inclusive": tax_inclusive
        }

    return None


def extract_net_quantity(text):
    pattern = (
        r"(?:NET\s*(?:QTY|QUANTITY|WEIGHT|WT)?|"
        r"QUANTITY|QTY|NET\s*CONTENT)"
        r"\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(kg|g|mg|l|ml|litre|liter|litres|liters|cm|m)"
        r"\b"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return f"{match.group(1)} {match.group(2)}"

    return None


def extract_mfg_date(text):
    pattern = (
        r"(?:MFG|MFD|MANUFACTURED|MANUFACTURING)"
        r"\s*(?:DATE)?\s*[:\-]?\s*"
        r"(\d{1,2}[\/\-]\d{4}|"
        r"\d{4}[\/\-]\d{1,2}|"
        r"\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(1) if match else None


def extract_country_of_origin(text):
    pattern = (
        r"(?:COUNTRY\s+OF\s+ORIGIN|"
        r"MADE\s+IN|"
        r"ORIGIN)"
        r"\s*[:\-]?\s*"
        r"([A-Za-z][A-Za-z ]*)"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(1).strip() if match else None


def extract_consumer_care(text):
    pattern = (
        r"(?:CONSUMER\s+CARE|"
        r"CUSTOMER\s+CARE|"
        r"CUSTOMER\s+SERVICE|"
        r"HELPLINE|"
        r"CONTACT)"
        r"\s*[:\-]?\s*(.+)"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(1).strip() if match else None

def extract_manufacturer_info(text):
    pattern = (
        r"((?:MANUFACTURED\s+BY|"
        r"PACKED\s+BY|"
        r"IMPORTED\s+BY|"
        r"MANUFACTURER|"
        r"MFD\s+BY|"
        r"MFG\s+BY|"
        r"MARKETED\s+BY)"
        r"\s*[:\-]?\s*.+)"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return None


def extract_generic_name(text):
    pattern = (
        r"(?:PRODUCT\s+NAME|"
        r"GENERIC\s+NAME|"
        r"COMMON\s+NAME|"
        r"PRODUCT)"
        r"\s*[:\-]?\s*(.+)"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(1).strip() if match else None


def extract_unit_sale_price(text):
    pattern = (
        r"(?:UNIT\s+SALE\s+PRICE|"
        r"SALE\s+PRICE)"
        r"\s*[:\-]?\s*"
        r"(?:₹|Rs\.?|INR)?\s*"
        r"(\d+(?:\.\d{1,2})?)"
        r"\s*(?:\/\s*)?"
        r"(g|kg|ml|l|cm|m|unit|piece|pc)?"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return {
            "value": match.group(1),
            "unit": match.group(2)
        }

    return None


EXTRACTORS = {
    "manufacturer_info": extract_manufacturer_info,
    "generic_name": extract_generic_name,
    "net_quantity": extract_net_quantity,
    "mfg_date": extract_mfg_date,
    "mrp": extract_mrp,
    "consumer_care": extract_consumer_care,
    "unit_sale_price": extract_unit_sale_price,
    "country_of_origin": extract_country_of_origin
}


def extract_fields(ocr_lines):

    text = "\n".join(
        line["text"]
        for line in ocr_lines
        if line.get("text")
    )

    results = {}

    for field, extractor in EXTRACTORS.items():

        value = extractor(text)

        results[field] = {
            "value": value,
            "found": value is not None
        }

    return results


if __name__ == "__main__":

    sample_text = """
    Manufactured by ABC Foods Pvt Ltd
    Product: Potato Chips
    Net Quantity: 500 g
    Mfg: 06/2026
    MRP ₹120 inclusive of all taxes
    Consumer Care: 1800-123-456
    Country of Origin: India
    Unit Sale Price: ₹0.24/g
    """

    result = extract_fields([
        {"text": line}
        for line in sample_text.splitlines()
        if line.strip()
    ])

    import json

    print(json.dumps(result, indent=2, ensure_ascii=False))