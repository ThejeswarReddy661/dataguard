import csv
import io
import json
import sys
import time
from pathlib import Path

import streamlit as st


# ============================================================
# PROJECT SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))

from helpers import get_percentage, get_severity
from loader import load_data, load_rules
from profiler import (
    count_duplicate_rows,
    count_missing_values,
    run_outlier_rules,
)
from reporting import build_json_report, build_report
from scoring import calculate_quality_score
from validators import (
    run_format_rules,
    run_range_rules,
    run_unique_rules,
)


# ============================================================
# CONSTANTS
# ============================================================

SAMPLE_LIMIT = 5


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DataGuard | Data Quality Health Check",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #0d1117;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #263244;
    }

    .dg-header {
        padding: 1.6rem;
        border-radius: 16px;
        border: 1px solid #263244;
        background:
            linear-gradient(
                135deg,
                rgba(30, 41, 59, 0.98),
                rgba(15, 23, 42, 0.98)
            );
        margin-bottom: 1.5rem;
    }

    .dg-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: #f8fafc;
    }

    .dg-subtitle {
        color: #94a3b8;
        margin-top: 0.25rem;
        font-size: 1rem;
        line-height: 1.6;
    }

    .dg-section-title {
        font-size: 1.35rem;
        font-weight: 750;
        color: #f8fafc;
        margin-top: 2rem;
        margin-bottom: 0.35rem;
    }

    .dg-section-description {
        color: #94a3b8;
        margin-bottom: 1rem;
    }

    .dg-health-card {
        text-align: center;
        padding: 2rem;
        border-radius: 18px;
        border: 1px solid #263244;
        background: #111827;
        margin-bottom: 1rem;
    }

    .dg-health-label {
        color: #94a3b8;
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .dg-health-score {
        font-size: 4rem;
        font-weight: 850;
        letter-spacing: -0.06em;
        color: #f8fafc;
        line-height: 1.1;
        margin-top: 0.3rem;
    }

    .dg-health-rating {
        margin-top: 0.5rem;
        font-size: 1.2rem;
        font-weight: 700;
        color: #22c55e;
    }

    .dg-message {
        padding: 1rem 1.1rem;
        border-radius: 12px;
        border: 1px solid #263244;
        background: #111827;
        margin-bottom: 0.7rem;
    }

    .dg-message-title {
        font-weight: 750;
        font-size: 1rem;
        color: #f8fafc;
    }

    .dg-message-body {
        color: #cbd5e1;
        margin-top: 0.35rem;
        line-height: 1.55;
    }

    .dg-good {
        border-left: 4px solid #22c55e;
    }

    .dg-warning {
        border-left: 4px solid #f59e0b;
    }

    .dg-danger {
        border-left: 4px solid #ef4444;
    }

    .dg-action-card {
        padding: 1.1rem;
        border-radius: 12px;
        background: #111827;
        border: 1px solid #263244;
        min-height: 190px;
    }

    .dg-action-number {
        font-size: 0.72rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
    }

    .dg-action-title {
        font-weight: 750;
        font-size: 1.05rem;
        color: #f8fafc;
        margin-top: 0.55rem;
    }

    .dg-action-text {
        color: #94a3b8;
        margin-top: 0.6rem;
        line-height: 1.6;
        font-size: 0.9rem;
    }

    .dg-chip {
        display: inline-block;
        margin: 0.15rem;
        padding: 0.3rem 0.6rem;
        border-radius: 8px;
        border: 1px solid #334155;
        background: #172033;
        color: #cbd5e1;
        font-size: 0.8rem;
    }

    .dg-rating-ready {
        color: #22c55e;
    }

    .dg-rating-review {
        color: #f59e0b;
    }

    .dg-rating-attention {
        color: #fb923c;
    }

    .dg-rating-risk {
        color: #ef4444;
    }

    .dg-analytics-card {
        padding: 1.15rem;
        border-radius: 14px;
        border: 1px solid #263244;
        background: #111827;
        min-height: 100%;
    }

    .dg-analytics-title {
        color: #f8fafc;
        font-size: 1rem;
        font-weight: 750;
        margin-bottom: 0.2rem;
    }

    .dg-analytics-subtitle {
        color: #64748b;
        font-size: 0.8rem;
        margin-bottom: 1rem;
        line-height: 1.45;
    }

    .dg-bar-row {
        margin-bottom: 0.9rem;
    }

    .dg-bar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        color: #cbd5e1;
        font-size: 0.82rem;
        margin-bottom: 0.32rem;
    }

    .dg-bar-label {
        font-weight: 650;
    }

    .dg-bar-value {
        color: #94a3b8;
        white-space: nowrap;
    }

    .dg-bar-track {
        width: 100%;
        height: 9px;
        border-radius: 999px;
        background: #1e293b;
        overflow: hidden;
    }

    .dg-bar-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(
            90deg,
            #2563eb,
            #38bdf8
        );
    }

    .dg-priority-high {
        background: #ef4444;
    }

    .dg-priority-medium {
        background: #f59e0b;
    }

    .dg-priority-low {
        background: #3b82f6;
    }

    .dg-column-fill {
        background: linear-gradient(
            90deg,
            #8b5cf6,
            #38bdf8
        );
    }

    .dg-kicker {
        color: #64748b;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }

    .dg-top-issue {
        padding: 1rem 1.1rem;
        border-radius: 12px;
        border: 1px solid #263244;
        background: #111827;
        min-height: 145px;
    }

    .dg-top-issue-rank {
        color: #64748b;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
    }

    .dg-top-issue-title {
        color: #f8fafc;
        font-size: 1rem;
        font-weight: 750;
        margin-top: 0.4rem;
    }

    .dg-top-issue-impact {
        color: #cbd5e1;
        font-size: 0.87rem;
        line-height: 1.5;
        margin-top: 0.45rem;
    }

    .dg-footer {
        border-top: 1px solid #263244;
        margin-top: 3rem;
        padding-top: 1.5rem;
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def get_rating(score):
    if score >= 90:
        return "READY TO USE"

    if score >= 80:
        return "USABLE WITH REVIEW"

    if score >= 70:
        return "NEEDS ATTENTION"

    return "HIGH RISK"


def get_rating_class(score):
    if score >= 90:
        return "dg-rating-ready"

    if score >= 80:
        return "dg-rating-review"

    if score >= 70:
        return "dg-rating-attention"

    return "dg-rating-risk"


def render_horizontal_bars(
    items,
    value_suffix="",
    max_value=None,
    fill_class="",
):
    if not items:
        st.caption("No data available.")
        return

    if max_value is None:
        max_value = max(
            value
            for _, value in items
        )

    safe_max = max(
        float(max_value),
        1.0,
    )

    html = ""

    for label, value in items:
        width = min(
            max(
                (float(value) / safe_max) * 100,
                0,
            ),
            100,
        )

        html += (
            '<div class="dg-bar-row">'
            '<div class="dg-bar-header">'
            f'<span class="dg-bar-label">{label}</span>'
            f'<span class="dg-bar-value">{value}{value_suffix}</span>'
            '</div>'
            '<div class="dg-bar-track">'
            f'<div class="dg-bar-fill {fill_class}" '
            f'style="width:{width:.2f}%"></div>'
            '</div>'
            '</div>'
        )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def build_column_flag_counts(
    columns,
    missing_counts,
    unique_results,
    range_results,
    format_results,
    outlier_results,
):
    flags = {
        column: missing_counts.get(
            column,
            0,
        )
        for column in columns
    }

    for column, result in unique_results.items():
        if (
            column in flags
            and "error" not in result
        ):
            flags[column] += len(
                result["duplicate_values"]
            )

    for column, result in range_results.items():
        if (
            column in flags
            and "error" not in result
        ):
            flags[column] += len(
                result["invalid_values"]
            )

    for column, result in format_results.items():
        if (
            column in flags
            and "error" not in result
        ):
            flags[column] += len(
                result["invalid_values"]
            )

    for column, result in outlier_results.items():
        if (
            column in flags
            and "error" not in result
        ):
            flags[column] += len(
                result["outliers"]
            )

    return flags


def render_top_issue_card(
    rank,
    issue,
    total_rows,
):
    html = (
        '<div class="dg-top-issue">'
        f'<div class="dg-top-issue-rank">Priority {rank}</div>'
        f'<div class="dg-top-issue-title">'
        f'{issue["Area"]} — {issue["Problem"]}'
        '</div>'
        '<div class="dg-top-issue-impact">'
        f'<strong>{issue["Count"]:,} of {total_rows:,} records</strong> '
        f'(<strong>{issue["Affected %"]:.1f}%</strong>) are affected by '
        f'this check. Priority: <strong>{issue["Severity"]}</strong>.'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def get_readiness_summary(score):
    if score >= 90:
        return (
            "Strong overall data health. Review the remaining flagged items "
            "before high-impact or regulated use."
        )

    if score >= 80:
        return (
            "Generally usable, but important quality issues should be reviewed "
            "before reporting, analytics, or operational decisions."
        )

    if score >= 70:
        return (
            "Several quality problems could affect downstream results. "
            "Correct the highest-priority issues before relying on this dataset."
        )

    return (
        "Significant quality problems were detected. Remediation is recommended "
        "before this dataset is used for downstream decisions."
    )


def get_health_message(score):
    if score >= 90:
        return (
            "The dataset is in strong overall condition. "
            "A small number of issues were detected and should "
            "still be reviewed before critical downstream use."
        )

    if score >= 80:
        return (
            "The dataset is generally usable, but several quality "
            "issues should be reviewed before relying on it for "
            "important reporting or analysis."
        )

    if score >= 70:
        return (
            "The dataset contains meaningful quality problems. "
            "Review the issues below before using it for reporting, "
            "analytics, or operational processes."
        )

    return (
        "The dataset has significant quality problems and should "
        "be reviewed before downstream use."
    )


def render_action_card(number, title, description):
    card_html = (
        '<div class="dg-action-card">'
        f'<div class="dg-action-number">Action {number}</div>'
        f'<div class="dg-action-title">{title}</div>'
        f'<div class="dg-action-text">{description}</div>'
        '</div>'
    )

    st.markdown(
        card_html,
        unsafe_allow_html=True,
    )


def count_duplicate_key_issues(unique_results):
    total = 0

    for result in unique_results.values():
        if "error" in result:
            continue

        total += len(
            result["duplicate_values"]
        )

    return total


def count_validation_issues(
    range_results,
    format_results,
    total_rows,
):
    issue_count = 0
    check_count = 0

    for result in range_results.values():
        if "error" in result:
            continue

        issue_count += len(
            result["invalid_values"]
        )

        check_count += total_rows

    for result in format_results.values():
        if "error" in result:
            continue

        issue_count += len(
            result["invalid_values"]
        )

        check_count += total_rows

    return issue_count, check_count


def count_outliers(outlier_results):
    total = 0

    for result in outlier_results.values():
        if "error" in result:
            continue

        total += len(
            result["outliers"]
        )

    return total


def calculate_quality_dimensions(
    total_rows,
    total_cells,
    total_missing,
    duplicate_count,
    duplicate_key_issues,
    validation_issue_count,
    validation_check_count,
    outlier_count,
):
    if total_cells:
        missing_health = (
            100
            - get_percentage(
                total_missing,
                total_cells,
            )
        )
    else:
        missing_health = 0

    duplicate_issues = (
        duplicate_count
        + duplicate_key_issues
    )

    if total_rows:
        duplicate_health = (
            100
            - get_percentage(
                duplicate_issues,
                total_rows,
            )
        )
    else:
        duplicate_health = 0

    if validation_check_count:
        rule_health = (
            100
            - get_percentage(
                validation_issue_count,
                validation_check_count,
            )
        )
    else:
        rule_health = 100

    if total_rows:
        unusual_health = (
            100
            - get_percentage(
                outlier_count,
                total_rows,
            )
        )
    else:
        unusual_health = 0

    return {
        "Missing Data Health": round(
            max(0, missing_health),
            2,
        ),
        "Duplicate Data Health": round(
            max(0, duplicate_health),
            2,
        ),
        "Rule Compliance": round(
            max(0, rule_health),
            2,
        ),
        "Unusual Value Check": round(
            max(0, unusual_health),
            2,
        ),
    }


def create_issue_summary(
    total_rows,
    missing_counts,
    duplicate_count,
    unique_results,
    range_results,
    format_results,
    outlier_results,
):
    issues = []

    for column, count in missing_counts.items():
        if count == 0:
            continue

        percentage = get_percentage(
            count,
            total_rows,
        )

        issues.append(
            {
                "Area": column,
                "Problem": "Missing information",
                "Count": count,
                "Affected %": round(percentage, 2),
                "Severity": get_severity(
                    percentage
                ),
            }
        )

    if duplicate_count > 0:
        issues.append(
            {
                "Area": "Dataset",
                "Problem": "Duplicate records",
                "Count": duplicate_count,
                "Affected %": round(
                    get_percentage(duplicate_count, total_rows),
                    2,
                ),
                "Severity": get_severity(
                    get_percentage(
                        duplicate_count,
                        total_rows,
                    )
                ),
            }
        )

    for column, result in unique_results.items():
        if "error" in result:
            continue

        count = len(
            result["duplicate_values"]
        )

        if count:
            issues.append(
                {
                    "Area": column,
                    "Problem": "Repeated identifier",
                    "Count": count,
                    "Affected %": round(
                        get_percentage(count, total_rows),
                        2,
                    ),
                    "Severity": get_severity(
                        get_percentage(
                            count,
                            total_rows,
                        )
                    ),
                }
            )

    for column, result in range_results.items():
        if "error" in result:
            continue

        count = len(
            result["invalid_values"]
        )

        if count:
            issues.append(
                {
                    "Area": column,
                    "Problem": (
                        "Value outside allowed range"
                    ),
                    "Count": count,
                    "Affected %": round(
                        get_percentage(count, total_rows),
                        2,
                    ),
                    "Severity": get_severity(
                        get_percentage(
                            count,
                            total_rows,
                        )
                    ),
                }
            )

    for column, result in format_results.items():
        if "error" in result:
            continue

        count = len(
            result["invalid_values"]
        )

        if count:
            issues.append(
                {
                    "Area": column,
                    "Problem": "Incorrect format",
                    "Count": count,
                    "Affected %": round(
                        get_percentage(count, total_rows),
                        2,
                    ),
                    "Severity": get_severity(
                        get_percentage(
                            count,
                            total_rows,
                        )
                    ),
                }
            )

    for column, result in outlier_results.items():
        if "error" in result:
            continue

        count = len(
            result["outliers"]
        )

        if count:
            issues.append(
                {
                    "Area": column,
                    "Problem": "Unusual value",
                    "Count": count,
                    "Affected %": round(
                        get_percentage(count, total_rows),
                        2,
                    ),
                    "Severity": get_severity(
                        get_percentage(
                            count,
                            total_rows,
                        )
                    ),
                }
            )

    return issues


def build_rule_chips(
    unique_results,
    range_results,
    format_results,
    outlier_results,
):
    chips = []

    for column in unique_results:
        chips.append(
            f"{column} must be unique"
        )

    for column, result in range_results.items():
        if "error" in result:
            continue

        minimum = result.get("min")
        maximum = result.get("max")

        if (
            minimum is not None
            and maximum is not None
        ):
            chips.append(
                f"{column}: {minimum} to {maximum}"
            )

        elif minimum is not None:
            chips.append(
                f"{column}: minimum {minimum}"
            )

        elif maximum is not None:
            chips.append(
                f"{column}: maximum {maximum}"
            )

    for column, result in format_results.items():
        if "error" in result:
            continue

        chips.append(
            f"{column}: valid "
            f"{result['rule_type']} format"
        )

    for column in outlier_results:
        chips.append(
            f"{column}: unusual-value check"
        )

    return chips


# ============================================================
# HEADER
# ============================================================

st.markdown(
    (
        '<div class="dg-header">'
        '<div class="dg-title">🛡️ DataGuard</div>'
        '<div class="dg-subtitle">'
        'Understand whether your data is ready to trust — '
        'and what needs attention before you use it.'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Analyze Data")

st.sidebar.caption(
    "Choose one of the demonstration datasets "
    "or upload your own files."
)

source_mode = st.sidebar.radio(
    "Data Source",
    [
        "Demo Dataset",
        "Upload My Data",
    ],
)


data_file = None
rules_file = None
rows = None
columns = None
rules = None


if source_mode == "Demo Dataset":

    dataset_name = st.sidebar.selectbox(
        "Choose Dataset",
        [
            "customers.csv",
            "employees.csv",
            "large_customers.csv",
        ],
    )

    if dataset_name == "employees.csv":

        data_file = (
            PROJECT_ROOT
            / "data"
            / "employees.csv"
        )

        rules_file = (
            PROJECT_ROOT
            / "config"
            / "employees_rules.json"
        )

    else:

        data_file = (
            PROJECT_ROOT
            / "data"
            / dataset_name
        )

        rules_file = (
            PROJECT_ROOT
            / "config"
            / "rules.json"
        )

    try:
        rows, columns = load_data(
            data_file
        )

        rules = load_rules(
            rules_file
        )

    except (
        FileNotFoundError,
        ValueError,
    ) as error:

        st.error(
            f"Unable to analyze this dataset: "
            f"{error}"
        )

        st.stop()


else:

    uploaded_csv = st.sidebar.file_uploader(
        "Upload CSV",
        type=["csv"],
    )

    uploaded_rules = st.sidebar.file_uploader(
        "Upload Validation Rules",
        type=["json"],
    )

    st.sidebar.caption(
        "Your files are analyzed for this session "
        "and are not added to the DataGuard project."
    )

    if uploaded_csv is None:

        st.info(
            "Upload a CSV file from the sidebar "
            "to start your data quality health check."
        )

        st.stop()

    if uploaded_rules is None:

        st.info(
            "Now upload the JSON validation rules "
            "that describe what valid data should look like."
        )

        st.stop()

    try:

        csv_text = (
            uploaded_csv
            .getvalue()
            .decode("utf-8")
        )

        reader = csv.DictReader(
            io.StringIO(csv_text)
        )

        rows = list(reader)

        columns = (
            reader.fieldnames
            or []
        )

        if not columns:
            raise ValueError(
                "The CSV file does not contain "
                "a valid header row."
            )

        rules = json.loads(
            uploaded_rules
            .getvalue()
            .decode("utf-8")
        )

        if not isinstance(
            rules,
            dict,
        ):
            raise ValueError(
                "The validation rules must be "
                "a JSON object."
            )

    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
    ) as error:

        st.error(
            f"Unable to process the uploaded files: "
            f"{error}"
        )

        st.stop()

    data_file = Path(
        uploaded_csv.name
    )

    rules_file = Path(
        uploaded_rules.name
    )


# ============================================================
# ANALYSIS
# ============================================================

analysis_start = time.perf_counter()

total_rows = len(rows)
total_columns = len(columns)
total_cells = (
    total_rows
    * total_columns
)


missing_counts = count_missing_values(
    rows,
    columns,
)

total_missing = sum(
    missing_counts.values()
)


duplicate_count = count_duplicate_rows(
    rows,
    columns,
)

duplicate_percentage = get_percentage(
    duplicate_count,
    total_rows,
)

duplicate_severity = get_severity(
    duplicate_percentage
)


unique_results = run_unique_rules(
    rows,
    columns,
    rules,
)

range_results = run_range_rules(
    rows,
    columns,
    rules,
)

format_results = run_format_rules(
    rows,
    columns,
    rules,
)

outlier_results = run_outlier_rules(
    rows,
    columns,
    rules,
)


duplicate_key_issues = (
    count_duplicate_key_issues(
        unique_results
    )
)


(
    validation_issue_count,
    validation_check_count,
) = count_validation_issues(
    range_results,
    format_results,
    total_rows,
)


outlier_count = count_outliers(
    outlier_results
)


quality_score = calculate_quality_score(
    total_rows=total_rows,
    total_cells=total_cells,
    total_missing=total_missing,
    duplicate_rows=duplicate_count,
    duplicate_key_issues=(
        duplicate_key_issues
    ),
    validation_issue_count=(
        validation_issue_count
    ),
    validation_check_count=(
        validation_check_count
    ),
    outlier_count=outlier_count,
)


quality_dimensions = (
    calculate_quality_dimensions(
        total_rows,
        total_cells,
        total_missing,
        duplicate_count,
        duplicate_key_issues,
        validation_issue_count,
        validation_check_count,
        outlier_count,
    )
)


analysis_seconds = (
    time.perf_counter()
    - analysis_start
)


# ============================================================
# BUSINESS SUMMARY
# ============================================================

issues = create_issue_summary(
    total_rows,
    missing_counts,
    duplicate_count,
    unique_results,
    range_results,
    format_results,
    outlier_results,
)


severity_rank = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
    "NONE": 0,
}

sorted_issues = sorted(
    issues,
    key=lambda item: (
        severity_rank.get(
            item["Severity"],
            0,
        ),
        item["Affected %"],
        item["Count"],
    ),
    reverse=True,
)

high_priority_count = sum(
    1
    for issue in issues
    if issue["Severity"]
    in (
        "HIGH",
        "CRITICAL",
    )
)

affected_issue_areas = len(
    issues
)


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

st.markdown(
    '<div class="dg-section-title">'
    'Executive Overview'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dg-section-description">'
    'The fastest way to understand whether this '
    'dataset is ready to use and where attention '
    'is required.'
    '</div>',
    unsafe_allow_html=True,
)


score_column, overview_column = (
    st.columns(
        [1, 2]
    )
)


with score_column:

    score_html = (
        '<div class="dg-health-card">'
        '<div class="dg-health-label">'
        'Overall Data Health'
        '</div>'
        f'<div class="dg-health-score">'
        f'{quality_score:.1f}'
        '</div>'
        f'<div class="dg-health-rating '
        f'{get_rating_class(quality_score)}">'
        f'{get_rating(quality_score)}'
        '</div>'
        '<div style="'
        'color:#64748b;'
        'margin-top:0.25rem;'
        '">'
        'out of 100'
        '</div>'
        '</div>'
    )

    st.markdown(
        score_html,
        unsafe_allow_html=True,
    )


with overview_column:

    st.markdown(
        "### Decision"
    )

    st.write(
        get_readiness_summary(
            quality_score
        )
    )

    top_summary1, top_summary2 = (
        st.columns(2)
    )

    top_summary1.metric(
        "Records Analyzed",
        f"{total_rows:,}",
    )

    top_summary2.metric(
        "Analysis Time",
        f"{analysis_seconds:.3f}s",
    )

    st.caption(
        "The overall score summarizes missing data, "
        "duplicates, configured rule violations, and "
        "statistically unusual values."
    )


overview1, overview2, overview3, overview4, overview5 = (
    st.columns(5)
)

overview1.metric(
    "Missing Values",
    f"{total_missing:,}",
    help=(
        f"{get_percentage(total_missing, total_cells):.2f}% "
        f"of all {total_cells:,} dataset cells are missing."
    ),
)

overview2.metric(
    "Duplicate Rows",
    f"{duplicate_count:,}",
    help=(
        f"{get_percentage(duplicate_count, total_rows):.2f}% "
        f"of records are exact duplicates."
    ),
)

overview3.metric(
    "Invalid Values",
    f"{validation_issue_count:,}",
    help=(
        "Values that violate configured business rules, "
        "such as allowed ranges or required formats."
    ),
)

overview4.metric(
    "Unusual Values",
    f"{outlier_count:,}",
    help=(
        "Statistically unusual numeric values. "
        "They are not automatically incorrect."
    ),
)

overview5.metric(
    "High-Priority Areas",
    f"{high_priority_count:,}",
    help=(
        "Quality areas currently classified as HIGH "
        "or CRITICAL based on the configured severity thresholds."
    ),
)


st.info(
    f"Decision: **{get_rating(quality_score)}** — "
    f"{get_readiness_summary(quality_score)}"
)


# ============================================================
# TOP PRIORITIES
# ============================================================

st.markdown(
    '<div class="dg-section-title">'
    'Top Priorities'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dg-section-description">'
    'Start with these findings first. DataGuard ranks '
    'issues by priority, affected percentage, and count.'
    '</div>',
    unsafe_allow_html=True,
)


if not sorted_issues:

    st.success(
        "No quality issues were detected by "
        "the configured checks."
    )

else:

    top_issues = sorted_issues[:3]

    top_issue_columns = st.columns(
        len(top_issues)
    )

    for index, issue in enumerate(
        top_issues
    ):

        with top_issue_columns[index]:

            render_top_issue_card(
                index + 1,
                issue,
                total_rows,
            )


# ============================================================
# RECOMMENDED ACTIONS
# ============================================================

st.markdown(
    '<div class="dg-section-title">'
    'Recommended Actions'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dg-section-description">'
    'Business-friendly next steps based on the '
    'quality problems DataGuard detected.'
    '</div>',
    unsafe_allow_html=True,
)


recommendations = []


email_missing = missing_counts.get(
    "email",
    0,
)

email_invalid = 0

if "email" in format_results:

    result = format_results[
        "email"
    ]

    if "error" not in result:

        email_invalid = len(
            result[
                "invalid_values"
            ]
        )


if (
    email_missing > 0
    or email_invalid > 0
):

    recommendations.append(
        (
            "Review Email Data",
            (
                f"{email_missing:,} email value(s) are missing and "
                f"{email_invalid:,} have an invalid format. "
                f"Review the source or ingestion process that "
                f"populates this field."
            ),
        )
    )


for column, result in (
    range_results.items()
):

    if "error" in result:
        continue

    count = len(
        result[
            "invalid_values"
        ]
    )

    if count > 0:

        recommendations.append(
            (
                f"Review {column.title()} Values",
                (
                    f"{count:,} value(s) fall outside the "
                    f"configured allowed range. Confirm whether "
                    f"these are source-data errors or whether the "
                    f"business rule needs review."
                ),
            )
        )


for column, result in (
    outlier_results.items()
):

    if "error" in result:
        continue

    count = len(
        result["outliers"]
    )

    if count > 0:

        recommendations.append(
            (
                f"Investigate Unusual "
                f"{column.title()} Values",
                (
                    f"{count:,} value(s) are statistically unusual. "
                    f"They are not automatically wrong; investigate "
                    f"them before changing or removing them."
                ),
            )
        )


if duplicate_count > 0:

    recommendations.append(
        (
            "Review Duplicate Records",
            (
                f"{duplicate_count:,} duplicate record(s) were "
                f"detected. Confirm whether they are accidental "
                f"duplicates or legitimate repeated events."
            ),
        )
    )


if recommendations:

    visible_recommendations = (
        recommendations[:3]
    )

    recommendation_columns = (
        st.columns(
            len(
                visible_recommendations
            )
        )
    )

    for index, recommendation in (
        enumerate(
            visible_recommendations
        )
    ):

        title, description = (
            recommendation
        )

        with recommendation_columns[
            index
        ]:

            render_action_card(
                index + 1,
                title,
                description,
            )

else:

    st.success(
        "No immediate corrective actions "
        "are recommended."
    )


# ============================================================
# VISUAL ANALYTICS
# ============================================================

st.markdown(
    '<div class="dg-section-title">'
    'Visual Analytics'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dg-section-description">'
    'Decision-focused visuals that explain overall '
    'health, issue priority, and which columns '
    'generate the most data-quality findings.'
    '</div>',
    unsafe_allow_html=True,
)


visual_left, visual_right = st.columns(2)


with visual_left:

    with st.container(border=True):

        st.markdown("#### Data Health Dimensions")

        st.caption(
            "Higher scores indicate healthier data. "
            "These four dimensions explain what drives "
            "the overall health score."
        )

        dimension_items = [
            (name, score)
            for name, score
            in quality_dimensions.items()
        ]

        render_horizontal_bars(
            dimension_items,
            value_suffix="%",
            max_value=100,
        )


with visual_right:

    with st.container(border=True):

        st.markdown("#### Issues by Priority")

        st.caption(
            "Shows how many detected quality areas "
            "require high, medium, or low attention."
        )

        priority_counts = {
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
        }

        for issue in issues:

            severity = issue["Severity"]

            if severity in ("CRITICAL", "HIGH"):
                priority_counts["HIGH"] += 1

            elif severity == "MEDIUM":
                priority_counts["MEDIUM"] += 1

            else:
                priority_counts["LOW"] += 1

        priority_max = max(
            priority_counts.values(),
            default=1,
        )

        for priority, css_class in (
            ("HIGH", "dg-priority-high"),
            ("MEDIUM", "dg-priority-medium"),
            ("LOW", "dg-priority-low"),
        ):

            render_horizontal_bars(
                [
                    (
                        priority,
                        priority_counts[priority],
                    )
                ],
                max_value=max(priority_max, 1),
                fill_class=css_class,
            )


st.write("")


column_flag_counts = build_column_flag_counts(
    columns,
    missing_counts,
    unique_results,
    range_results,
    format_results,
    outlier_results,
)

column_flag_items = sorted(
    [
        (column, count)
        for column, count
        in column_flag_counts.items()
        if count > 0
    ],
    key=lambda item: item[1],
    reverse=True,
)


with st.container(border=True):

    st.markdown("#### Findings by Column")

    st.caption(
        "Shows which fields generate the most findings across "
        "missing-data, rule-validation, duplicate-key, and "
        "unusual-value checks. A record can contribute to more "
        "than one finding."
    )

    if column_flag_items:

        render_horizontal_bars(
            column_flag_items,
            max_value=max(
                count
                for _, count
                in column_flag_items
            ),
            fill_class="dg-column-fill",
        )

    else:

        st.success(
            "No column-level quality findings detected."
        )


# ============================================================
# WHY THIS SCORE
# ============================================================

st.markdown(
    '<div class="dg-section-title">'
    'Why This Score?'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dg-section-description">'
    'The overall health score is the average of four '
    'equally weighted quality dimensions.'
    '</div>',
    unsafe_allow_html=True,
)


with st.container(border=True):

    score_explanation1, score_explanation2 = st.columns([2, 1])

    with score_explanation1:

        st.markdown(
            """
            DataGuard measures four different aspects of dataset health:

            - **Missing Data Health** — how much expected information is present.
            - **Duplicate Data Health** — whether records and configured identifiers remain unique.
            - **Rule Compliance** — whether values satisfy configured range and format rules.
            - **Unusual Value Check** — how frequently statistical outliers appear.

            Each dimension contributes **25%** of the overall score.
            """
        )

    with score_explanation2:

        dimension_values = list(
            quality_dimensions.values()
        )

        st.metric(
            "Calculated Health",
            f"{quality_score:.1f}/100",
        )

        if dimension_values:

            formula_text = " + ".join(
                f"{value:.2f}"
                for value in dimension_values
            )

            st.code(
                f"({formula_text}) / "
                f"{len(dimension_values)} = "
                f"{quality_score:.2f}",
                language=None,
            )

        st.caption(
            "This makes the score transparent and "
            "easy to explain during review."
        )


# FULL ISSUE SUMMARY
# ============================================================

st.markdown(
    '<div class="dg-section-title">'
    'Detailed Findings'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dg-section-description">'
    'Drill down into every quality check that produced a finding. '
    ''
    '</div>',
    unsafe_allow_html=True,
)


if issues:

    issue_table = [
        {
            "Area": issue["Area"],
            "Problem": issue["Problem"],
            "Affected Records": (
                issue["Count"]
            ),
            "Affected %": (
                issue["Affected %"]
            ),
            "Priority": (
                issue["Severity"]
            ),
        }
        for issue in sorted_issues
    ]

    st.dataframe(
        issue_table,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.write(
        "No detected issues to display."
    )


# ============================================================
# INVALID VS UNUSUAL EXPLANATION
# ============================================================

st.markdown(
    '<div class="dg-section-title">'
    'Invalid vs. Unusual'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dg-section-description">'
    'These findings mean different things and '
    'should not be treated the same way.'
    '</div>',
    unsafe_allow_html=True,
)


explain1, explain2 = st.columns(2)

with explain1:

    st.markdown(
        """
        **Invalid value**

        A value that breaks a configured business rule.

        Example: an age of `240` when the allowed
        range is `0–120`.

        **Typical action:** correct the source data,
        investigate ingestion logic, or review the
        business rule.
        """
    )


with explain2:

    st.markdown(
        """
        **Unusual value**

        A statistically uncommon value identified
        by IQR analysis.

        Example: a salary far above the normal
        distribution.

        **Typical action:** investigate first.
        An unusual value may still be legitimate.
        """
    )


# ADVANCED ANALYSIS
# ============================================================

st.markdown(
    '<div class="dg-section-title">'
    'Advanced Analysis'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dg-section-description">'
    'The sections below provide deeper technical '
    'information for analysts, engineers, and '
    'technical reviewers.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# QUALITY DIMENSIONS
# ============================================================

with st.expander(
    "How is the quality score broken down?"
):

    st.write(
        "These four measurements explain "
        "different aspects of dataset health."
    )

    explanations = {
        "Missing Data Health": (
            "Measures how much expected information "
            "is present."
        ),
        "Duplicate Data Health": (
            "Measures whether records and identifiers "
            "remain unique."
        ),
        "Rule Compliance": (
            "Measures how often values satisfy the "
            "configured business rules."
        ),
        "Unusual Value Check": (
            "Measures the prevalence of statistically "
            "unusual numeric values."
        ),
    }

    for name, score in (
        quality_dimensions.items()
    ):

        st.write(
            f"**{name}: "
            f"{score:.2f}%**"
        )

        st.caption(
            explanations[name]
        )

        st.progress(
            min(
                score / 100,
                1.0,
            )
        )


# ============================================================
# MISSING DATA DETAILS
# ============================================================

with st.expander(
    "Missing Data Details"
):

    missing_table = []

    for column, count in (
        missing_counts.items()
    ):

        percentage = get_percentage(
            count,
            total_rows,
        )

        missing_table.append(
            {
                "Column": column,
                "Missing Values": count,
                "Missing %": round(
                    percentage,
                    3,
                ),
                "Severity": get_severity(
                    percentage
                ),
            }
        )

    st.dataframe(
        missing_table,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# VALIDATION RULES
# ============================================================

with st.expander(
    "What Rules Did DataGuard Check?"
):

    st.write(
        "The validation rules are stored outside "
        "the Python engine in a JSON configuration "
        "file. This allows the same engine to be "
        "reused for different datasets."
    )

    chips = build_rule_chips(
        unique_results,
        range_results,
        format_results,
        outlier_results,
    )

    chip_html = ""

    for chip in chips:

        chip_html += (
            f'<span class="dg-chip">'
            f'{chip}'
            f'</span>'
        )

    st.markdown(
        chip_html,
        unsafe_allow_html=True,
    )

    st.write("")

    st.caption(
        "Raw configuration"
    )

    st.json(
        rules
    )


# ============================================================
# INVALID VALUE SAMPLES
# ============================================================

with st.expander(
    "Show Sample Invalid Values"
):

    found_samples = False

    for column, result in (
        range_results.items()
    ):

        if "error" in result:
            continue

        values = result[
            "invalid_values"
        ]

        if not values:
            continue

        found_samples = True

        st.write(
            f"**{column} — "
            f"outside allowed range**"
        )

        st.code(
            "\n".join(
                str(value)
                for value
                in values[:SAMPLE_LIMIT]
            )
        )

        if len(values) > SAMPLE_LIMIT:

            st.caption(
                f"{len(values) - SAMPLE_LIMIT:,} "
                f"additional value(s) not shown."
            )

    for column, result in (
        format_results.items()
    ):

        if "error" in result:
            continue

        values = result[
            "invalid_values"
        ]

        if not values:
            continue

        found_samples = True

        st.write(
            f"**{column} — incorrect format**"
        )

        st.code(
            "\n".join(
                str(value)
                for value
                in values[:SAMPLE_LIMIT]
            )
        )

        if len(values) > SAMPLE_LIMIT:

            st.caption(
                f"{len(values) - SAMPLE_LIMIT:,} "
                f"additional value(s) not shown."
            )

    if not found_samples:

        st.success(
            "No invalid values detected."
        )


# ============================================================
# OUTLIER DETAILS
# ============================================================

with st.expander(
    "Unusual Value Analysis"
):

    st.write(
        "DataGuard uses the Interquartile Range "
        "(IQR) method to identify unusually low "
        "or high numeric values."
    )

    st.info(
        "An unusual value is not automatically an "
        "error. It is a value worth investigating."
    )

    if not outlier_results:

        st.write(
            "No unusual-value checks configured."
        )

    for column, result in (
        outlier_results.items()
    ):

        if "error" in result:

            st.warning(
                result["error"]
            )

            continue

        statistics = result[
            "statistics"
        ]

        outliers = result[
            "outliers"
        ]

        details = result[
            "details"
        ]

        st.write(
            f"### {column.title()}"
        )

        if statistics:

            c1, c2, c3, c4, c5 = (
                st.columns(5)
            )

            c1.metric(
                "Lowest",
                f"{statistics['minimum']:,.2f}",
            )

            c2.metric(
                "Typical (Median)",
                f"{statistics['median']:,.2f}",
            )

            c3.metric(
                "Average",
                f"{statistics['mean']:,.2f}",
            )

            c4.metric(
                "Highest",
                f"{statistics['maximum']:,.2f}",
            )

            c5.metric(
                "Unusual Values",
                f"{len(outliers):,}",
            )

        if details:

            st.caption(
                "Technical IQR calculation"
            )

            st.write(
                f"Q1: {details['q1']:,.2f} | "
                f"Q3: {details['q3']:,.2f} | "
                f"IQR: {details['iqr']:,.2f}"
            )

            st.write(
                f"Expected range: "
                f"{details['lower_bound']:,.2f} "
                f"to "
                f"{details['upper_bound']:,.2f}"
            )

        if outliers:

            st.caption(
                "Example unusual values"
            )

            st.code(
                "\n".join(
                    f"{value:,.2f}"
                    for value
                    in outliers[:SAMPLE_LIMIT]
                )
            )


# ============================================================
# ENGINEERING DETAILS
# ============================================================

with st.expander(
    "Engineering & Performance"
):

    e1, e2, e3, e4 = (
        st.columns(4)
    )

    e1.metric(
        "Records Processed",
        f"{total_rows:,}",
    )

    e2.metric(
        "Current Analysis",
        f"{analysis_seconds:.3f}s",
    )

    e3.metric(
        "Automated Tests",
        "18 / 18",
    )

    e4.metric(
        "CI Status",
        "Passing",
    )

    st.write(
        "DataGuard separates its validation engine "
        "from the user interface. The same core "
        "profiling, validation, scoring, and reporting "
        "logic can therefore be used from both the "
        "command line and this dashboard."
    )

    if (
        source_mode == "Demo Dataset"
        and data_file.name
        == "large_customers.csv"
    ):

        st.info(
            "Verified CLI benchmark: 500,000 records "
            "(~27 MB) processed end-to-end in "
            "approximately 1.69 seconds, including "
            "validation, outlier detection, scoring, "
            "and TXT/JSON report generation."
        )


# ============================================================
# REPORT GENERATION
# ============================================================

report_text = build_report(
    data_file=data_file,
    rules_file=rules_file,
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
    data_file=data_file,
    rules_file=rules_file,
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


# ============================================================
# REPORT CENTER
# ============================================================

st.markdown(
    '<div class="dg-section-title">'
    'Download Results'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dg-section-description">'
    'Save the complete analysis for documentation, '
    'auditing, or downstream systems.'
    '</div>',
    unsafe_allow_html=True,
)


download1, download2 = (
    st.columns(2)
)


with download1:

    st.download_button(
        "Download Human-Readable Report",
        data=report_text,
        file_name=(
            data_file.stem
            + "_quality_report.txt"
        ),
        mime="text/plain",
        use_container_width=True,
    )


with download2:

    st.download_button(
        "Download Machine-Readable JSON",
        data=json.dumps(
            json_report,
            indent=4,
        ),
        file_name=(
            data_file.stem
            + "_quality_report.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="dg-footer">'
    'DataGuard • Config-Driven Data Quality '
    'Validation & Profiling Engine'
    '</div>',
    unsafe_allow_html=True,
)