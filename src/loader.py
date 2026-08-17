import csv
import json


def load_data(file_path):
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset file not found: {file_path}"
        )

    try:
        with open(
            file_path,
            mode="r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            rows = list(reader)
            columns = reader.fieldnames or []

    except UnicodeDecodeError as error:
        raise ValueError(
            "Dataset could not be read as UTF-8 text."
        ) from error

    if not columns:
        raise ValueError(
            "Dataset does not contain a valid header row."
        )

    return rows, columns


def load_rules(file_path):
    if not file_path.exists():
        raise FileNotFoundError(
            f"Rules file not found: {file_path}"
        )

    try:
        with open(
            file_path,
            mode="r",
            encoding="utf-8"
        ) as file:

            rules = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            "Rules file contains invalid JSON."
        ) from error

    if not isinstance(rules, dict):
        raise ValueError(
            "Rules file must contain a JSON object."
        )

    return rules