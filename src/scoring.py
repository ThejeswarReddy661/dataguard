from helpers import get_percentage


def calculate_quality_score(
    total_rows,
    total_cells,
    total_missing,
    duplicate_rows,
    duplicate_key_issues,
    validation_issue_count,
    validation_check_count,
    outlier_count,
):
    if total_rows == 0 or total_cells == 0:
        return 0.0

    # --------------------------------------------------
    # COMPLETENESS
    # Weight: 30%
    # --------------------------------------------------

    missing_percentage = get_percentage(
        total_missing,
        total_cells
    )

    completeness_score = max(
        0.0,
        100.0 - missing_percentage
    )


    # --------------------------------------------------
    # UNIQUENESS
    # Weight: 25%
    #
    # Includes:
    # - exact duplicate rows
    # - duplicate configured key values
    # --------------------------------------------------

    uniqueness_issues = (
        duplicate_rows
        + duplicate_key_issues
    )

    uniqueness_percentage = get_percentage(
        uniqueness_issues,
        total_rows
    )

    uniqueness_score = max(
        0.0,
        100.0 - uniqueness_percentage
    )


    # --------------------------------------------------
    # VALIDITY
    # Weight: 35%
    #
    # Includes configured range and format rules.
    # --------------------------------------------------

    if validation_check_count == 0:
        validity_score = 100.0

    else:
        invalid_percentage = get_percentage(
            validation_issue_count,
            validation_check_count
        )

        validity_score = max(
            0.0,
            100.0 - invalid_percentage
        )


    # --------------------------------------------------
    # ANOMALY HEALTH
    # Weight: 10%
    #
    # Outliers are not necessarily invalid.
    # They receive a smaller weight.
    # --------------------------------------------------

    outlier_percentage = get_percentage(
        outlier_count,
        total_rows
    )

    anomaly_score = max(
        0.0,
        100.0 - outlier_percentage
    )


    # --------------------------------------------------
    # WEIGHTED OVERALL SCORE
    # --------------------------------------------------

    overall_score = (
        completeness_score * 0.30
        + uniqueness_score * 0.25
        + validity_score * 0.35
        + anomaly_score * 0.10
    )


    # --------------------------------------------------
    # PREVENT FALSE PERFECT SCORE
    # --------------------------------------------------

    total_issues = (
        total_missing
        + duplicate_rows
        + duplicate_key_issues
        + validation_issue_count
        + outlier_count
    )

    rounded_score = round(
        overall_score,
        1
    )

    # A dataset with detected problems should not
    # display 100.0 due only to rounding.
    if (
        total_issues > 0
        and rounded_score >= 100.0
    ):
        rounded_score = 99.9

    return rounded_score