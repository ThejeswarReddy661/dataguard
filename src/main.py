import sys
from pathlib import Path

from helpers import get_percentage, get_severity
from loader import load_data, load_rules
from profiler import (
    count_duplicate_rows,
    count_missing_values,
    run_outlier_rules,
)
from reporting import (
    build_json_report,
    build_report,
    save_json_report,
    save_report,
)
from scoring import calculate_quality_score
from validators import (
    run_format_rules,
    run_range_rules,
    run_unique_rules,
)


PROJECT_ROOT = Path(__file__).parent.parent


def get_file_paths():
    if len(sys.argv) == 3:
        data_file = PROJECT_ROOT / sys.argv[1]
        rules_file = PROJECT_ROOT / sys.argv[2]

    elif len(sys.argv) == 1:
        data_file = (
            PROJECT_ROOT
            / "data"
            / "customers.csv"
        )

        rules_file = (
            PROJECT_ROOT
            / "config"
            / "rules.json"
        )

    else:
        print()
        print("ERROR: Invalid command usage.")
        print()
        print("Use:")
        print(
            "python3 src/main.py "
            "data/dataset.csv "
            "config/rules.json"
        )
        print()

        sys.exit(1)

    return data_file, rules_file


def load_inputs():
    data_file, rules_file = get_file_paths()

    try:
        rows, columns = load_data(
            data_file
        )

        rules = load_rules(
            rules_file
        )

    except FileNotFoundError as error:
        print()
        print("=" * 60)
        print("DATAGUARD ERROR")
        print("=" * 60)

        print(
            f"\nERROR: {error}"
        )

        print()
        sys.exit(1)

    except ValueError as error:
        print()
        print("=" * 60)
        print("DATAGUARD ERROR")
        print("=" * 60)

        print(
            f"\nERROR: {error}"
        )

        print()
        sys.exit(1)

    return (
        data_file,
        rules_file,
        rows,
        columns,
        rules,
    )


(
    DATA_FILE,
    RULES_FILE,
    rows,
    columns,
    rules,
) = load_inputs()


total_rows = len(rows)
total_columns = len(columns)
total_cells = (
    total_rows
    * total_columns
)


missing_counts = count_missing_values(
    rows,
    columns
)

total_missing = sum(
    missing_counts.values()
)


duplicate_count = count_duplicate_rows(
    rows,
    columns
)

duplicate_percentage = get_percentage(
    duplicate_count,
    total_rows
)

duplicate_severity = get_severity(
    duplicate_percentage
)


unique_results = run_unique_rules(
    rows,
    columns,
    rules
)

range_results = run_range_rules(
    rows,
    columns,
    rules
)

format_results = run_format_rules(
    rows,
    columns,
    rules
)

outlier_results = run_outlier_rules(
    rows,
    columns,
    rules
)


validation_issue_count = 0
validation_check_count = 0


for result in range_results.values():
    if "error" in result:
        continue

    validation_issue_count += len(
        result["invalid_values"]
    )

    validation_check_count += (
        total_rows
    )


for result in format_results.values():
    if "error" in result:
        continue

    validation_issue_count += len(
        result["invalid_values"]
    )

    validation_check_count += (
        total_rows
    )


quality_score = calculate_quality_score(
    total_rows=total_rows,
    total_cells=total_cells,
    total_missing=total_missing,
    duplicate_rows=duplicate_count,
    validation_issue_count=(
        validation_issue_count
    ),
    validation_check_count=(
        validation_check_count
    ),
)


report_text = build_report(
    data_file=DATA_FILE,
    rules_file=RULES_FILE,
    total_rows=total_rows,
    total_columns=total_columns,
    total_cells=total_cells,
    missing_counts=missing_counts,
    total_missing=total_missing,
    duplicate_count=duplicate_count,
    duplicate_percentage=duplicate_percentage,
    duplicate_severity=duplicate_severity,
    unique_results=unique_results,
    range_results=range_results,
    format_results=format_results,
    outlier_results=outlier_results,
    quality_score=quality_score,
)


json_report = build_json_report(
    data_file=DATA_FILE,
    rules_file=RULES_FILE,
    total_rows=total_rows,
    total_columns=total_columns,
    total_cells=total_cells,
    missing_counts=missing_counts,
    total_missing=total_missing,
    duplicate_count=duplicate_count,
    duplicate_percentage=duplicate_percentage,
    duplicate_severity=duplicate_severity,
    unique_results=unique_results,
    range_results=range_results,
    format_results=format_results,
    outlier_results=outlier_results,
    quality_score=quality_score,
)


print()
print(report_text)
print()


try:
    text_report_path = save_report(
        report_text=report_text,
        data_file=DATA_FILE,
        project_root=PROJECT_ROOT,
    )

    json_report_path = save_json_report(
        report_data=json_report,
        data_file=DATA_FILE,
        project_root=PROJECT_ROOT,
    )

except OSError as error:
    print(
        f"WARNING: Report could not be saved: {error}"
    )

else:
    print(
        f"Text report saved to: "
        f"{text_report_path}"
    )

    print(
        f"JSON report saved to: "
        f"{json_report_path}"
    )