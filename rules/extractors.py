import re


# ============================================================
# BASIC TEXT CLEANING
# ============================================================

def clean_text(text):
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


# ============================================================
# MRP
# ============================================================

def extract_mrp(text):
    pattern = (
        r"(?:M\.?\s*R\.?\s*P\.?|"
        r"MAXIMUM\s+RETAIL\s+PRICE|"
        r"MAX\.?\s*RETAIL\s+PRICE)"
        r"\s*[:\-]?\s*"
        r"(?:₹|Rs\.?|INR)?\s*"
        r"(\d+(?:\.\d{1,2})?)"
    )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if match:
        value = match.group(1)

        tax_inclusive = bool(
            re.search(
                r"inclusive\s+of\s+all\s+taxes|"
                r"incl\.?\s*(?:of\s*)?all\s+taxes|"
                r"including\s+all\s+taxes",
                text,
                re.IGNORECASE
            )
        )

        return {
            "value": value,
            "taxes_inclusive": tax_inclusive
        }

    return None


# ============================================================
# NET QUANTITY
# ============================================================

def extract_net_quantity(text):
    pattern = (
        r"(?:NET\s*(?:QTY|QUANTITY|WEIGHT|WT)?|"
        r"QUANTITY|QTY|NET\s*CONTENT)"
        r"\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(kg|g|mg|l|ml|litre|liter|litres|liters|cm|m)"
        r"\b"
    )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if match:
        return f"{match.group(1)} {match.group(2)}"

    return None


# ============================================================
# MANUFACTURER / PACKER / IMPORTER
# ============================================================

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

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return None


# ============================================================
# GENERIC / PRODUCT NAME
# ============================================================

def extract_generic_name(text):

    pattern = (
        r"(?:PRODUCT\s+NAME|"
        r"GENERIC\s+NAME|"
        r"COMMON\s+NAME|"
        r"PRODUCT)"
        r"\s*[:\-]?\s*(.+)"
    )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return None


# ============================================================
# MANUFACTURING DATE
# ============================================================

def extract_mfg_date(text):

    pattern = (
        r"(?:MFG|MFD|MANUFACTURED|MANUFACTURING)"
        r"\s*(?:DATE)?\s*[:\-]?\s*"
        r"(\d{1,2}[\/\-]\d{4}|"
        r"\d{4}[\/\-]\d{1,2}|"
        r"\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})"
    )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1)

    return None


# ============================================================
# COUNTRY OF ORIGIN
# ============================================================

def extract_country_of_origin(text):

    pattern = (
        r"(?:COUNTRY\s+OF\s+ORIGIN|"
        r"MADE\s+IN|"
        r"ORIGIN)"
        r"\s*[:\-]?\s*"
        r"([A-Za-z][A-Za-z ]*)"
    )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return None


# ============================================================
# CONSUMER CARE
# ============================================================

def extract_consumer_care(text):

    lines = text.splitlines()

    contact_keywords = [
        "consumer care",
        "customer care",
        "customer service",
        "helpline",
        "contact"
    ]

    phone_pattern = r"\b\d[\d\s\-]{5,13}\d\b"

    email_pattern = (
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\."
        r"[A-Za-z]{2,}\b"
    )

    for i, line in enumerate(lines):

        line_clean = line.strip()

        if not line_clean:
            continue

        lower_line = line_clean.lower()

        # -----------------------------------------
        # Find consumer-care/contact label
        # -----------------------------------------

        if any(
            keyword in lower_line
            for keyword in contact_keywords
        ):

            # -------------------------------------
            # Information on same line
            # -------------------------------------

            parts = re.split(
                r"consumer\s+care|"
                r"customer\s+care|"
                r"customer\s+service|"
                r"helpline|"
                r"contact",
                line_clean,
                maxsplit=1,
                flags=re.IGNORECASE
            )

            if len(parts) > 1:

                candidate = parts[1].strip(" :-")

                if (
                    re.search(
                        phone_pattern,
                        candidate
                    )
                    or
                    re.search(
                        email_pattern,
                        candidate
                    )
                ):
                    return candidate

            # -------------------------------------
            # Information on next line
            # -------------------------------------

            if i + 1 < len(lines):

                next_line = lines[i + 1].strip()

                if (
                    re.search(
                        phone_pattern,
                        next_line
                    )
                    or
                    re.search(
                        email_pattern,
                        next_line
                    )
                ):
                    return next_line

    return None


# ============================================================
# UNIT SALE PRICE
# ============================================================

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

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if match:

        return {
            "value": match.group(1),
            "unit": match.group(2)
        }

    return None


# ============================================================
# EXTRACTOR MAP
# ============================================================

EXTRACTORS = {

    "manufacturer_info":
        extract_manufacturer_info,

    "generic_name":
        extract_generic_name,

    "net_quantity":
        extract_net_quantity,

    "mfg_date":
        extract_mfg_date,

    "mrp":
        extract_mrp,

    "consumer_care":
        extract_consumer_care,

    "unit_sale_price":
        extract_unit_sale_price,

    "country_of_origin":
        extract_country_of_origin
}


# ============================================================
# MAIN FIELD EXTRACTION
# ============================================================

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


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    sample_text = """
    Manufactured by ABC Foods Pvt Ltd
    Product: Potato Chips
    Net Quantity: 500 g
    Mfg: 06/2026
    MRP: 120/- (Including all Taxes)
    Contact
    Protein : 0.38g
    9727955514 softwareketan@gmail.com
    Country of Origin: India
    Unit Sale Price: ₹0.24/g
    """

    result = extract_fields([
        {"text": line}
        for line in sample_text.splitlines()
        if line.strip()
    ])

    import json

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )