import json
import os
from .extractors import extract_fields
from .validators import VALIDATORS


def load_rules(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "rules.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_quantity_in_base_units(quantity):
    """
    Converts quantity into a comparable base value.

    Returns:
        ("weight", grams)
        ("volume", millilitres)
        ("length", centimetres)
        None
    """

    if not quantity:
        return None

    parts = quantity.strip().lower().split()

    if len(parts) != 2:
        return None

    try:
        number = float(parts[0])
    except ValueError:
        return None

    unit = parts[1]

    if unit == "mg":
        return "weight", number / 1000

    if unit == "g":
        return "weight", number

    if unit == "kg":
        return "weight", number * 1000

    if unit == "ml":
        return "volume", number

    if unit in ["l", "litre", "liter", "litres", "liters"]:
        return "volume", number * 1000

    if unit == "cm":
        return "length", number

    if unit == "m":
        return "length", number * 100

    return None


def run_rule_engine(
    ocr_lines,
    package_type="retail",
    product_type=None,
    industrial_or_institutional=False
):

    rules = load_rules()
    field_rules = rules["fields"]

    extracted = extract_fields(ocr_lines)
    results = {}

    # --------------------------------------------------
    # GET NET QUANTITY
    # --------------------------------------------------

    net_quantity = extracted["net_quantity"]["value"]
    converted_quantity = get_quantity_in_base_units(net_quantity)

    # --------------------------------------------------
    # RULE 3 EXEMPTIONS
    # --------------------------------------------------

    if industrial_or_institutional:
        reason = (
            "Industrial/institutional package purchased directly "
            "from manufacturer for own use"
        )

        return {
            "overall_verdict": "EXEMPT",
            "exemption": reason,
            "legal_reference": "Rule 3",
            "fields": {
                field: {
                    "value": extracted[field]["value"],
                    "status": "NOT_APPLICABLE",
                    "reason": reason,
                    "legal_reference": "Rule 3"
                }
                for field in field_rules
            }
        }

    if converted_quantity:
        quantity_type, quantity_value = converted_quantity

        if (
            quantity_type == "weight"
            and quantity_value > 25000
        ):
            reason = "Package contains more than 25 kg"

            return {
                "overall_verdict": "EXEMPT",
                "exemption": reason,
                "legal_reference": "Rule 3",
                "fields": {
                    field: {
                        "value": extracted[field]["value"],
                        "status": "NOT_APPLICABLE",
                        "reason": reason,
                        "legal_reference": "Rule 3"
                    }
                    for field in field_rules
                }
            }

        if (
            quantity_type == "volume"
            and quantity_value > 25000
        ):
            reason = "Package contains more than 25 litres"

            return {
                "overall_verdict": "EXEMPT",
                "exemption": reason,
                "legal_reference": "Rule 3",
                "fields": {
                    field: {
                        "value": extracted[field]["value"],
                        "status": "NOT_APPLICABLE",
                        "reason": reason,
                        "legal_reference": "Rule 3"
                    }
                    for field in field_rules
                }
            }

        # Rule 26: <= 10 g / 10 ml
        if (
            quantity_type == "weight"
            and quantity_value <= 10
        ):
            reason = "Package is 10 g or less"

            return {
                "overall_verdict": "EXEMPT",
                "exemption": reason,
                "legal_reference": "Rule 26",
                "fields": {
                    field: {
                        "value": extracted[field]["value"],
                        "status": "NOT_APPLICABLE",
                        "reason": reason,
                        "legal_reference": "Rule 26"
                    }
                    for field in field_rules
                }
            }

        if (
            quantity_type == "volume"
            and quantity_value <= 10
        ):
            reason = "Package is 10 ml or less"

            return {
                "overall_verdict": "EXEMPT",
                "exemption": reason,
                "legal_reference": "Rule 26",
                "fields": {
                    field: {
                        "value": extracted[field]["value"],
                        "status": "NOT_APPLICABLE",
                        "reason": reason,
                        "legal_reference": "Rule 26"
                    }
                    for field in field_rules
                }
            }

    # --------------------------------------------------
    # FIELD VALIDATION
    # --------------------------------------------------

    for field, rule in field_rules.items():

        value = extracted[field]["value"]

        # Wholesale has its own Rule 24 requirements
        if package_type == "wholesale":

            if field in ["manufacturer_info", "generic_name", "net_quantity"]:
                applicable = True
            else:
                applicable = False

        else:
            applicable = package_type in rule.get(
                "applies_when",
                []
            )

        if not applicable:

            results[field] = {
                "value": value,
                "status": "NOT_APPLICABLE",
                "reason": "Rule does not apply to this package type",
                "legal_reference": (
                    "Rule 24"
                    if package_type == "wholesale"
                    else rule.get("legal_reference")
                )
            }

            continue

        # --------------------------------------------------
        # PRODUCT-SPECIFIC EXEMPTIONS
        # --------------------------------------------------

        exemptions = rule.get("field_exemptions", [])

        if product_type and any(
            product_type.lower() == x.lower()
            for x in exemptions
        ):

            results[field] = {
                "value": value,
                "status": "NOT_APPLICABLE",
                "reason": f"Field exempt for {product_type}",
                "legal_reference": rule.get("legal_reference")
            }

            continue

        # --------------------------------------------------
        # UNIT SALE PRICE EXEMPTIONS
        # --------------------------------------------------

        if field == "unit_sale_price":

            if package_type in [
                "multi_piece",
                "combination",
                "group",
                "wholesale"
            ]:

                results[field] = {
                    "value": value,
                    "status": "NOT_APPLICABLE",
                    "reason": (
                        "Unit sale price exempt for this package type"
                    ),
                    "legal_reference": "Rule 6(11)"
                }

                continue

        # --------------------------------------------------
        # MISSING FIELD
        # --------------------------------------------------

        if value is None:

            if rule.get("required", False):

                status = "FAIL"
                reason = "Required declaration not detected"

            else:

                status = "PASS"
                reason = "Optional declaration not detected"

        else:

            validator_name = rule["validator"]
            validator = VALIDATORS[validator_name]

            # --------------------------------------------------
            # MRP
            # --------------------------------------------------

            if field == "mrp" and isinstance(value, dict):

                price = value.get("value")
                taxes_inclusive = value.get(
                    "taxes_inclusive",
                    False
                )

                if not validator(price):

                    status = "FAIL"
                    reason = "Invalid MRP value"

                elif not taxes_inclusive:

                    status = "FAIL"
                    reason = (
                        "MRP declaration does not show "
                        "inclusive-of-all-taxes wording"
                    )

                else:

                    status = "PASS"
                    reason = (
                        "Valid MRP with inclusive-of-all-taxes declaration"
                    )

            # --------------------------------------------------
            # UNIT SALE PRICE
            # --------------------------------------------------

            elif (
                field == "unit_sale_price"
                and isinstance(value, dict)
            ):

                price = value.get("value")

                if validator(price):

                    status = "PASS"
                    reason = "Valid unit sale price detected"

                else:

                    status = "FAIL"
                    reason = "Invalid unit sale price"

            # --------------------------------------------------
            # NORMAL FIELDS
            # --------------------------------------------------

            else:

                if validator(value):

                    status = "PASS"
                    reason = "Field detected and validated"

                else:

                    status = "FAIL"
                    reason = "Field detected but failed validation"

        results[field] = {
            "value": value,
            "status": status,
            "reason": reason,
            "legal_reference": (
                "Rule 24"
                if package_type == "wholesale"
                and field in [
                    "manufacturer_info",
                    "generic_name",
                    "net_quantity"
                ]
                else rule.get("legal_reference")
            )
        }

    # --------------------------------------------------
    # OVERALL VERDICT
    # --------------------------------------------------

    applicable_results = [
        result
        for result in results.values()
        if result["status"] != "NOT_APPLICABLE"
    ]

    if any(
        result["status"] == "FAIL"
        for result in applicable_results
    ):
        overall_verdict = "NON_COMPLIANT"
    else:
        overall_verdict = "COMPLIANT"

    return {
        "overall_verdict": overall_verdict,
        "fields": results
    }


if __name__ == "__main__":

    sample_ocr = [
        {"text": "Manufactured by ABC Foods Pvt Ltd"},
        {"text": "Product: Potato Chips"},
        {"text": "Net Quantity: 500 g"},
        {"text": "Mfg: 06/2026"},
        {"text": "MRP ₹120 inclusive of all taxes"},
        {"text": "Consumer Care: 1800-123-456"},
        {"text": "Country of Origin: India"},
        {"text": "Unit Sale Price: ₹0.24/g"}
    ]

    result = run_rule_engine(
        sample_ocr,
        package_type="retail"
    )

    print(json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    ))
