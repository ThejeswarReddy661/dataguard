import re

from helpers import is_missing


def find_duplicate_keys(rows, key_column):
    seen_keys = set()
    duplicate_keys = set()

    for row in rows:
        key_value = row.get(key_column)

        if is_missing(key_value):
            continue

        if key_value in seen_keys:
            duplicate_keys.add(key_value)
        else:
            seen_keys.add(key_value)

    return duplicate_keys


def validate_range_rule(
    rows,
    column,
    minimum=None,
    maximum=None
):
    invalid_values = []

    for row in rows:
        raw_value = row.get(column)

        if is_missing(raw_value):
            continue

        try:
            value = float(raw_value)

        except ValueError:
            invalid_values.append(raw_value)
            continue

        if minimum is not None and value < minimum:
            invalid_values.append(raw_value)
            continue

        if maximum is not None and value > maximum:
            invalid_values.append(raw_value)

    return invalid_values


def validate_email_format(rows, column):
    invalid_values = []

    email_pattern = re.compile(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    for row in rows:
        value = row.get(column)

        if is_missing(value):
            continue

        if not email_pattern.match(value):
            invalid_values.append(value)

    return invalid_values


def validate_format_rule(
    rows,
    column,
    rule_type
):
    if rule_type == "email":
        return validate_email_format(
            rows,
            column
        )

    return []


def run_unique_rules(
    rows,
    columns,
    rules
):
    results = {}

    for column in rules.get(
        "unique_columns",
        []
    ):
        if column not in columns:
            results[column] = {
                "error": "Column not found"
            }
            continue

        duplicate_values = find_duplicate_keys(
            rows,
            column
        )

        results[column] = {
            "duplicate_values": duplicate_values
        }

    return results


def run_range_rules(
    rows,
    columns,
    rules
):
    results = {}

    range_rules = rules.get(
        "range_rules",
        {}
    )

    for column, rule in range_rules.items():
        if column not in columns:
            results[column] = {
                "error": "Column not found"
            }
            continue

        minimum = rule.get("min")
        maximum = rule.get("max")

        invalid_values = validate_range_rule(
            rows,
            column,
            minimum,
            maximum
        )

        results[column] = {
            "min": minimum,
            "max": maximum,
            "invalid_values": invalid_values
        }

    return results


def run_format_rules(
    rows,
    columns,
    rules
):
    results = {}

    format_rules = rules.get(
        "format_rules",
        {}
    )

    for column, rule_type in format_rules.items():
        if column not in columns:
            results[column] = {
                "error": "Column not found"
            }
            continue

        invalid_values = validate_format_rule(
            rows,
            column,
            rule_type
        )

        results[column] = {
            "rule_type": rule_type,
            "invalid_values": invalid_values
        }

    return results