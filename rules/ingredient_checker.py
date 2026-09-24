import json
import re


def load_restricted_ingredients(rules_path="rules.json"):
    with open(rules_path, "r", encoding="utf-8") as f:
        rules = json.load(f)

    config = rules.get("banned_ingredient_rules", {})

    if not config.get("enabled", False):
        return []

    return config.get("restricted_ingredients", [])


def check_banned_ingredients(text, rules_path="rules.json"):

    restricted_ingredients = load_restricted_ingredients(
        rules_path
    )

    if not text:
        return {
            "status": "NO_TEXT",
            "detected": [],
            "legal_reference": (
                "FSSAI Act, 2006 / applicable regulations; "
                "CDSCO applicable requirements"
            )
        }

    text_lower = text.lower()

    detected = []

    for ingredient in restricted_ingredients:

        ingredient = ingredient.strip()

        if not ingredient:
            continue

        pattern = r"\b" + re.escape(
            ingredient.lower()
        ) + r"\b"

        if re.search(pattern, text_lower):

            detected.append(ingredient)

    if detected:

        return {
            "status": "FLAG",
            "detected": detected,
            "reason": (
                "Potential restricted/banned ingredient detected"
            ),
            "legal_reference": (
                "FSSAI Act, 2006 / applicable regulations; "
                "CDSCO applicable requirements"
            )
        }

    return {
        "status": "PASS",
        "detected": [],
        "reason": "No configured restricted ingredients detected",
        "legal_reference": (
            "FSSAI Act, 2006 / applicable regulations; "
            "CDSCO applicable requirements"
        )
    }