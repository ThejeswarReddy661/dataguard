from helpers import get_percentage


def calculate_quality_score(
    total_rows,
    total_cells,
    total_missing,
    duplicate_rows,
    validation_issue_count,
    validation_check_count
):
    if total_rows == 0:
        return 0.0

    if total_cells == 0:
        return 0.0

    # --------------------------------------------------
    # COMPLETENESS SCORE
    # --------------------------------------------------

    missing_percentage = get_percentage(
        total_missing,
        total_cells
    )

    completeness_score = max(
        0,
        100 - missing_percentage
    )

    # --------------------------------------------------
    # UNIQUENESS SCORE
    # --------------------------------------------------

    duplicate_percentage = get_percentage(
        duplicate_rows,
        total_rows
    )

    uniqueness_score = max(
        0,
        100 - duplicate_percentage
    )

    # --------------------------------------------------
    # VALIDITY SCORE
    # --------------------------------------------------

    if validation_check_count == 0:
        validity_score = 100.0

    else:
        invalid_percentage = get_percentage(
            validation_issue_count,
            validation_check_count
        )

        validity_score = max(
            0,
            100 - invalid_percentage
        )

    # --------------------------------------------------
    # OVERALL SCORE
    # --------------------------------------------------

    overall_score = (
        completeness_score
        + uniqueness_score
        + validity_score
    ) / 3

    return round(
        overall_score,
        1
    )