from statistics import mean, median

from helpers import is_missing


def count_missing_values(rows, columns):
    missing_counts = {
        column: 0
        for column in columns
    }

    for row in rows:
        for column in columns:
            if is_missing(row.get(column)):
                missing_counts[column] += 1

    return missing_counts


def count_duplicate_rows(rows, columns):
    seen_rows = set()
    duplicate_count = 0

    for row in rows:
        row_values = tuple(
            row.get(column)
            for column in columns
        )

        if row_values in seen_rows:
            duplicate_count += 1
        else:
            seen_rows.add(row_values)

    return duplicate_count


def get_numeric_values(rows, column):
    values = []

    for row in rows:
        value = row.get(column)

        if is_missing(value):
            continue

        try:
            numeric_value = float(value)
            values.append(numeric_value)

        except ValueError:
            continue

    return values


def calculate_statistics(values):
    if not values:
        return None

    return {
        "minimum": min(values),
        "maximum": max(values),
        "mean": mean(values),
        "median": median(values)
    }


def calculate_quartile(
    sorted_values,
    position
):
    if not sorted_values:
        return None

    index = (
        len(sorted_values) - 1
    ) * position

    lower_index = int(index)

    upper_index = min(
        lower_index + 1,
        len(sorted_values) - 1
    )

    fraction = index - lower_index

    lower_value = sorted_values[
        lower_index
    ]

    upper_value = sorted_values[
        upper_index
    ]

    return (
        lower_value
        + (
            upper_value
            - lower_value
        ) * fraction
    )


def detect_outliers_iqr(values):
    if len(values) < 4:
        return [], None

    sorted_values = sorted(values)

    q1 = calculate_quartile(
        sorted_values,
        0.25
    )

    q3 = calculate_quartile(
        sorted_values,
        0.75
    )

    iqr = q3 - q1

    lower_bound = q1 - (
        1.5 * iqr
    )

    upper_bound = q3 + (
        1.5 * iqr
    )

    outliers = []

    for value in values:
        if (
            value < lower_bound
            or value > upper_bound
        ):
            outliers.append(value)

    details = {
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound
    }

    return outliers, details


def run_outlier_rules(
    rows,
    columns,
    rules
):
    results = {}

    for column in rules.get(
        "outlier_columns",
        []
    ):
        if column not in columns:
            results[column] = {
                "error": "Column not found"
            }
            continue

        values = get_numeric_values(
            rows,
            column
        )

        statistics = calculate_statistics(
            values
        )

        outliers, details = detect_outliers_iqr(
            values
        )

        results[column] = {
            "statistics": statistics,
            "outliers": outliers,
            "details": details
        }

    return results