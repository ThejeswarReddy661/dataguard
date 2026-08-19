import json
from datetime import datetime, timezone
from pathlib import Path


HISTORY_FILENAME = "quality_history.jsonl"


def get_history_path(project_root):
    """
    Return the path used to store DataGuard
    quality-history snapshots.
    """

    history_directory = (
        Path(project_root)
        / "history"
    )

    history_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        history_directory
        / HISTORY_FILENAME
    )


def create_snapshot(
    dataset,
    rows,
    columns,
    quality_score,
    missing_values,
    duplicate_rows,
    invalid_values,
    unusual_values,
    analysis_seconds,
):
    """
    Create one structured DataGuard quality snapshot.
    """

    return {
        "timestamp": (
            datetime.now(
                timezone.utc
            )
            .isoformat()
        ),

        "dataset": str(dataset),

        "rows": int(rows),

        "columns": int(columns),

        "quality_score": float(
            quality_score
        ),

        "missing_values": int(
            missing_values
        ),

        "duplicate_rows": int(
            duplicate_rows
        ),

        "invalid_values": int(
            invalid_values
        ),

        "unusual_values": int(
            unusual_values
        ),

        "analysis_seconds": round(
            float(analysis_seconds),
            4,
        ),
    }


def save_snapshot(
    snapshot,
    project_root,
):
    """
    Append one snapshot to the JSON Lines
    history file.
    """

    history_path = get_history_path(
        project_root
    )

    with history_path.open(
        mode="a",
        encoding="utf-8",
    ) as file:

        file.write(
            json.dumps(
                snapshot
            )
        )

        file.write("\n")

    return history_path


def load_history(project_root):
    """
    Load all valid history records.

    Invalid or empty lines are skipped so one
    malformed record does not break the entire
    dashboard.
    """

    history_path = get_history_path(
        project_root
    )

    if not history_path.exists():
        return []

    snapshots = []

    with history_path.open(
        mode="r",
        encoding="utf-8",
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            try:
                snapshot = json.loads(
                    line
                )

            except json.JSONDecodeError:
                continue

            if not isinstance(
                snapshot,
                dict,
            ):
                continue

            snapshots.append(
                snapshot
            )

    return snapshots


def get_dataset_history(
    project_root,
    dataset,
):
    """
    Return history only for one dataset.
    """

    dataset = str(dataset)

    history = load_history(
        project_root
    )

    return [
        snapshot
        for snapshot in history
        if snapshot.get(
            "dataset"
        ) == dataset
    ]


def get_latest_snapshot(
    project_root,
    dataset=None,
):
    """
    Return the latest snapshot.

    If dataset is supplied, return the latest
    snapshot for that dataset only.
    """

    if dataset is None:

        history = load_history(
            project_root
        )

    else:

        history = get_dataset_history(
            project_root,
            dataset,
        )

    if not history:
        return None

    return history[-1]


def calculate_score_change(
    history,
):
    """
    Compare the latest quality score with the
    previous saved score.

    Returns:
        None if fewer than two snapshots exist.

        Otherwise:
        {
            "previous_score": ...,
            "current_score": ...,
            "change": ...
        }
    """

    if len(history) < 2:
        return None

    previous_score = float(
        history[-2][
            "quality_score"
        ]
    )

    current_score = float(
        history[-1][
            "quality_score"
        ]
    )

    return {
        "previous_score": (
            previous_score
        ),

        "current_score": (
            current_score
        ),

        "change": round(
            current_score
            - previous_score,
            2,
        ),
    }