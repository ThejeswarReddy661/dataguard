import json

from helpers import get_percentage, get_severity


SAMPLE_LIMIT = 5


def format_sample_values(values):
    values = list(values)

    if not values:
        return []

    return values[:SAMPLE_LIMIT]


def get_remaining_count(values):
    values = list(values)

    remaining = len(values) - SAMPLE_LIMIT

    if remaining < 0:
        return 0

    return remaining


def build_report(
    data_file,
    rules_file,
    total_rows,
    total_columns,
    total_cells,
    missing_counts,
    total_missing,
    duplicate_count,
    duplicate_percentage,
    duplicate_severity,
    unique_results,
    range_results,
    format_results,
    outlier_results,
    quality_score,
):
    lines = []

    lines.append("=" * 60)
    lines.append("DATAGUARD - DATA QUALITY REPORT")
    lines.append("=" * 60)

    lines.append("")
    lines.append(f"Dataset: {data_file.name}")
    lines.append(f"Rules: {rules_file.name}")

    # --------------------------------------------------
    # DATASET OVERVIEW
    # --------------------------------------------------

    lines.append("")
    lines.append("DATASET OVERVIEW")
    lines.append("-" * 60)

    lines.append(f"Rows: {total_rows:,}")
    lines.append(f"Columns: {total_columns}")
    lines.append(f"Total cells: {total_cells:,}")

    # --------------------------------------------------
    # MISSING VALUES
    # --------------------------------------------------

    lines.append("")
    lines.append("MISSING VALUE ANALYSIS")
    lines.append("-" * 60)

    for column, count in missing_counts.items():
        percentage = get_percentage(
            count,
            total_rows
        )

        severity = get_severity(
            percentage
        )

        lines.append(
            f"{column}: "
            f"{count:,} missing "
            f"({percentage:.1f}%) "
            f"- {severity}"
        )

    lines.append("")
    lines.append(
        f"Total missing cells: "
        f"{total_missing:,}"
    )

    # --------------------------------------------------
    # DUPLICATE ROWS
    # --------------------------------------------------

    lines.append("")
    lines.append("DUPLICATE ROW ANALYSIS")
    lines.append("-" * 60)

    lines.append(
        f"Duplicate rows: "
        f"{duplicate_count:,} "
        f"({duplicate_percentage:.1f}%) "
        f"- {duplicate_severity}"
    )

    # --------------------------------------------------
    # UNIQUE RULES
    # --------------------------------------------------

    lines.append("")
    lines.append("UNIQUE COLUMN RULES")
    lines.append("-" * 60)

    if not unique_results:
        lines.append(
            "No unique-column rules configured."
        )

    else:
        for column, result in unique_results.items():
            if "error" in result:
                lines.append(
                    f"{column}: "
                    f"{result['error']}"
                )
                continue

            duplicate_values = sorted(
                result["duplicate_values"]
            )

            count = len(
                duplicate_values
            )

            percentage = get_percentage(
                count,
                total_rows
            )

            severity = get_severity(
                percentage
            )

            lines.append(
                f"{column}: "
                f"{count:,} duplicate key value(s) "
                f"({percentage:.1f}%) "
                f"- {severity}"
            )

            if duplicate_values:
                sample_values = format_sample_values(
                    duplicate_values
                )

                lines.append(
                    f"Sample repeated values: "
                    f"{sample_values}"
                )

                remaining = get_remaining_count(
                    duplicate_values
                )

                if remaining > 0:
                    lines.append(
                        f"... {remaining:,} additional "
                        f"duplicate value(s)"
                    )

    # --------------------------------------------------
    # RANGE RULES
    # --------------------------------------------------

    lines.append("")
    lines.append("RANGE VALIDATION RULES")
    lines.append("-" * 60)

    if not range_results:
        lines.append(
            "No range rules configured."
        )

    else:
        for column, result in range_results.items():
            if "error" in result:
                lines.append(
                    f"{column}: "
                    f"{result['error']}"
                )
                continue

            invalid_values = result[
                "invalid_values"
            ]

            count = len(
                invalid_values
            )

            percentage = get_percentage(
                count,
                total_rows
            )

            severity = get_severity(
                percentage
            )

            minimum = result["min"]
            maximum = result["max"]

            if (
                minimum is not None
                and maximum is not None
            ):
                rule_text = (
                    f"{minimum} to "
                    f"{maximum}"
                )

            elif minimum is not None:
                rule_text = (
                    f">= {minimum}"
                )

            elif maximum is not None:
                rule_text = (
                    f"<= {maximum}"
                )

            else:
                rule_text = "No range"

            lines.append(
                f"{column}: "
                f"{count:,} invalid "
                f"({percentage:.1f}%) "
                f"- {severity}"
            )

            lines.append(
                f"Rule: {rule_text}"
            )

            if invalid_values:
                sample_values = format_sample_values(
                    invalid_values
                )

                lines.append(
                    f"Sample invalid values: "
                    f"{sample_values}"
                )

                remaining = get_remaining_count(
                    invalid_values
                )

                if remaining > 0:
                    lines.append(
                        f"... {remaining:,} additional "
                        f"violation(s)"
                    )

    # --------------------------------------------------
    # FORMAT RULES
    # --------------------------------------------------

    lines.append("")
    lines.append("FORMAT VALIDATION RULES")
    lines.append("-" * 60)

    if not format_results:
        lines.append(
            "No format rules configured."
        )

    else:
        for column, result in format_results.items():
            if "error" in result:
                lines.append(
                    f"{column}: "
                    f"{result['error']}"
                )
                continue

            invalid_values = result[
                "invalid_values"
            ]

            count = len(
                invalid_values
            )

            percentage = get_percentage(
                count,
                total_rows
            )

            severity = get_severity(
                percentage
            )

            lines.append(
                f"{column}: "
                f"{count:,} invalid "
                f"({percentage:.1f}%) "
                f"- {severity}"
            )

            lines.append(
                f"Rule type: "
                f"{result['rule_type']}"
            )

            if invalid_values:
                sample_values = format_sample_values(
                    invalid_values
                )

                lines.append(
                    f"Sample invalid values: "
                    f"{sample_values}"
                )

                remaining = get_remaining_count(
                    invalid_values
                )

                if remaining > 0:
                    lines.append(
                        f"... {remaining:,} additional "
                        f"violation(s)"
                    )

    # --------------------------------------------------
    # OUTLIER ANALYSIS
    # --------------------------------------------------

    lines.append("")
    lines.append("OUTLIER ANALYSIS")
    lines.append("-" * 60)

    if not outlier_results:
        lines.append(
            "No outlier rules configured."
        )

    else:
        for column, result in outlier_results.items():
            if "error" in result:
                lines.append(
                    f"{column}: "
                    f"{result['error']}"
                )
                continue

            lines.append("")
            lines.append(
                f"Column: {column}"
            )

            statistics = result[
                "statistics"
            ]

            outliers = result[
                "outliers"
            ]

            details = result[
                "details"
            ]

            if statistics:
                lines.append(
                    f"Minimum: "
                    f"{statistics['minimum']:,.2f}"
                )

                lines.append(
                    f"Maximum: "
                    f"{statistics['maximum']:,.2f}"
                )

                lines.append(
                    f"Mean: "
                    f"{statistics['mean']:,.2f}"
                )

                lines.append(
                    f"Median: "
                    f"{statistics['median']:,.2f}"
                )

            lines.append(
                f"Potential outliers: "
                f"{len(outliers):,}"
            )

            if details:
                lines.append(
                    f"Q1: "
                    f"{details['q1']:,.2f}"
                )

                lines.append(
                    f"Q3: "
                    f"{details['q3']:,.2f}"
                )

                lines.append(
                    f"IQR: "
                    f"{details['iqr']:,.2f}"
                )

                lines.append(
                    f"Lower bound: "
                    f"{details['lower_bound']:,.2f}"
                )

                lines.append(
                    f"Upper bound: "
                    f"{details['upper_bound']:,.2f}"
                )

            if outliers:
                formatted_outliers = [
                    f"{value:,.2f}"
                    for value in outliers
                ]

                sample_values = format_sample_values(
                    formatted_outliers
                )

                lines.append(
                    f"Sample outlier values: "
                    f"{sample_values}"
                )

                remaining = get_remaining_count(
                    formatted_outliers
                )

                if remaining > 0:
                    lines.append(
                        f"... {remaining:,} additional "
                        f"outlier(s)"
                    )

    # --------------------------------------------------
    # QUALITY SCORE
    # --------------------------------------------------

    lines.append("")
    lines.append("=" * 60)
    lines.append("DATA QUALITY SCORE")
    lines.append("=" * 60)

    lines.append(
        f"Overall Score: "
        f"{quality_score}/100"
    )

    if quality_score >= 90:
        rating = "EXCELLENT"

    elif quality_score >= 80:
        rating = "GOOD"

    elif quality_score >= 70:
        rating = "FAIR"

    else:
        rating = "POOR"

    lines.append(
        f"Rating: {rating}"
    )

    lines.append("=" * 60)

    return "\n".join(lines)


def build_json_report(
    data_file,
    rules_file,
    total_rows,
    total_columns,
    total_cells,
    missing_counts,
    total_missing,
    duplicate_count,
    duplicate_percentage,
    duplicate_severity,
    unique_results,
    range_results,
    format_results,
    outlier_results,
    quality_score,
):
    if quality_score >= 90:
        rating = "EXCELLENT"

    elif quality_score >= 80:
        rating = "GOOD"

    elif quality_score >= 70:
        rating = "FAIR"

    else:
        rating = "POOR"

    missing_report = {}

    for column, count in missing_counts.items():
        percentage = get_percentage(
            count,
            total_rows
        )

        missing_report[column] = {
            "count": count,
            "percentage": round(
                percentage,
                3
            ),
            "severity": get_severity(
                percentage
            ),
        }

    unique_report = {}

    for column, result in unique_results.items():
        if "error" in result:
            unique_report[column] = {
                "error": result["error"]
            }
            continue

        duplicate_values = sorted(
            result["duplicate_values"]
        )

        percentage = get_percentage(
            len(duplicate_values),
            total_rows
        )

        unique_report[column] = {
            "duplicate_key_count": len(
                duplicate_values
            ),
            "duplicate_values": (
                duplicate_values
            ),
            "percentage": round(
                percentage,
                3
            ),
            "severity": get_severity(
                percentage
            ),
        }

    range_report = {}

    for column, result in range_results.items():
        if "error" in result:
            range_report[column] = {
                "error": result["error"]
            }
            continue

        invalid_values = result[
            "invalid_values"
        ]

        percentage = get_percentage(
            len(invalid_values),
            total_rows
        )

        range_report[column] = {
            "min": result["min"],
            "max": result["max"],
            "invalid_count": len(
                invalid_values
            ),
            "invalid_values": (
                invalid_values
            ),
            "percentage": round(
                percentage,
                3
            ),
            "severity": get_severity(
                percentage
            ),
        }

    format_report = {}

    for column, result in format_results.items():
        if "error" in result:
            format_report[column] = {
                "error": result["error"]
            }
            continue

        invalid_values = result[
            "invalid_values"
        ]

        percentage = get_percentage(
            len(invalid_values),
            total_rows
        )

        format_report[column] = {
            "rule_type": result[
                "rule_type"
            ],
            "invalid_count": len(
                invalid_values
            ),
            "invalid_values": (
                invalid_values
            ),
            "percentage": round(
                percentage,
                3
            ),
            "severity": get_severity(
                percentage
            ),
        }

    outlier_report = {}

    for column, result in outlier_results.items():
        if "error" in result:
            outlier_report[column] = {
                "error": result["error"]
            }
            continue

        outlier_report[column] = {
            "statistics": result[
                "statistics"
            ],
            "outliers": result[
                "outliers"
            ],
            "details": result[
                "details"
            ],
        }

    return {
        "dataset": data_file.name,
        "rules_file": rules_file.name,

        "overview": {
            "rows": total_rows,
            "columns": total_columns,
            "total_cells": total_cells,
        },

        "missing_values": {
            "total_missing_cells": (
                total_missing
            ),
            "columns": missing_report,
        },

        "duplicate_rows": {
            "count": duplicate_count,
            "percentage": round(
                duplicate_percentage,
                3
            ),
            "severity": (
                duplicate_severity
            ),
        },

        "unique_rules": unique_report,

        "range_rules": range_report,

        "format_rules": format_report,

        "outlier_analysis": (
            outlier_report
        ),

        "quality_score": {
            "score": quality_score,
            "rating": rating,
        },
    }


def save_report(
    report_text,
    data_file,
    project_root
):
    reports_directory = (
        project_root
        / "reports"
    )

    reports_directory.mkdir(
        exist_ok=True
    )

    report_name = (
        data_file.stem
        + "_quality_report.txt"
    )

    report_path = (
        reports_directory
        / report_name
    )

    report_path.write_text(
        report_text + "\n",
        encoding="utf-8"
    )

    return report_path


def save_json_report(
    report_data,
    data_file,
    project_root
):
    reports_directory = (
        project_root
        / "reports"
    )

    reports_directory.mkdir(
        exist_ok=True
    )

    report_name = (
        data_file.stem
        + "_quality_report.json"
    )

    report_path = (
        reports_directory
        / report_name
    )

    report_path.write_text(
        json.dumps(
            report_data,
            indent=4
        )
        + "\n",
        encoding="utf-8"
    )

    return report_path