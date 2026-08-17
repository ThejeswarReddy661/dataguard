import json
import sys
import tempfile
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(
    0,
    str(SRC_PATH)
)


from helpers import (
    get_percentage,
    get_severity,
    is_missing,
)

from loader import (
    load_data,
    load_rules,
)

from profiler import (
    calculate_statistics,
    count_duplicate_rows,
    count_missing_values,
    detect_outliers_iqr,
)

from reporting import (
    build_json_report,
)

from validators import (
    find_duplicate_keys,
    validate_email_format,
    validate_range_rule,
)


SAMPLE_ROWS = [
    {
        "customer_id": "1001",
        "name": "John",
        "age": "28",
        "email": "john@gmail.com",
        "salary": "65000",
    },
    {
        "customer_id": "1002",
        "name": "Sarah",
        "age": "31",
        "email": "sarah@gmail.com",
        "salary": "72000",
    },
    {
        "customer_id": "1003",
        "name": "Mike",
        "age": "-5",
        "email": "",
        "salary": "80000",
    },
    {
        "customer_id": "1003",
        "name": "Mike",
        "age": "-5",
        "email": "",
        "salary": "80000",
    },
    {
        "customer_id": "1004",
        "name": "Emma",
        "age": "240",
        "email": "emma@gmail.com",
        "salary": "70000",
    },
    {
        "customer_id": "1005",
        "name": "David",
        "age": "35",
        "email": "davidgmail.com",
        "salary": "9500000",
    },
    {
        "customer_id": "1006",
        "name": "Lisa",
        "age": "29",
        "email": "lisa@gmail.com",
        "salary": "68000",
    },
    {
        "customer_id": "1007",
        "name": "Robert",
        "age": "",
        "email": "robert@gmail.com",
        "salary": "75000",
    },
]


COLUMNS = [
    "customer_id",
    "name",
    "age",
    "email",
    "salary",
]


class TestDataGuard(unittest.TestCase):

    def test_is_missing(self):
        self.assertTrue(
            is_missing("")
        )

        self.assertTrue(
            is_missing("   ")
        )

        self.assertTrue(
            is_missing(None)
        )

        self.assertFalse(
            is_missing("John")
        )


    def test_get_percentage(self):
        result = get_percentage(
            2,
            8
        )

        self.assertEqual(
            result,
            25.0
        )


    def test_get_percentage_zero_total(self):
        result = get_percentage(
            5,
            0
        )

        self.assertEqual(
            result,
            0.0
        )


    def test_get_severity(self):
        self.assertEqual(
            get_severity(0),
            "NONE"
        )

        self.assertEqual(
            get_severity(5),
            "LOW"
        )

        self.assertEqual(
            get_severity(10),
            "MEDIUM"
        )

        self.assertEqual(
            get_severity(25),
            "HIGH"
        )


    def test_missing_values(self):
        result = count_missing_values(
            SAMPLE_ROWS,
            COLUMNS
        )

        self.assertEqual(
            result["age"],
            1
        )

        self.assertEqual(
            result["email"],
            2
        )


    def test_duplicate_rows(self):
        result = count_duplicate_rows(
            SAMPLE_ROWS,
            COLUMNS
        )

        self.assertEqual(
            result,
            1
        )


    def test_duplicate_customer_ids(self):
        result = find_duplicate_keys(
            SAMPLE_ROWS,
            "customer_id"
        )

        self.assertEqual(
            result,
            {"1003"}
        )


    def test_age_range_validation(self):
        result = validate_range_rule(
            SAMPLE_ROWS,
            "age",
            minimum=0,
            maximum=120
        )

        self.assertEqual(
            result,
            [
                "-5",
                "-5",
                "240",
            ]
        )


    def test_email_validation(self):
        result = validate_email_format(
            SAMPLE_ROWS,
            "email"
        )

        self.assertEqual(
            result,
            [
                "davidgmail.com"
            ]
        )


    def test_statistics(self):
        values = [
            10,
            20,
            30,
            40,
        ]

        result = calculate_statistics(
            values
        )

        self.assertEqual(
            result["minimum"],
            10
        )

        self.assertEqual(
            result["maximum"],
            40
        )

        self.assertEqual(
            result["mean"],
            25
        )

        self.assertEqual(
            result["median"],
            25
        )


    def test_iqr_outlier_detection(self):
        values = [
            65000,
            68000,
            70000,
            72000,
            75000,
            80000,
            80000,
            9500000,
        ]

        outliers, details = (
            detect_outliers_iqr(
                values
            )
        )

        self.assertEqual(
            outliers,
            [9500000]
        )

        self.assertIsNotNone(
            details
        )


    def test_missing_dataset_file(self):
        fake_path = (
            PROJECT_ROOT
            / "data"
            / "definitely_missing.csv"
        )

        with self.assertRaises(
            FileNotFoundError
        ):
            load_data(
                fake_path
            )


    def test_missing_rules_file(self):
        fake_path = (
            PROJECT_ROOT
            / "config"
            / "definitely_missing.json"
        )

        with self.assertRaises(
            FileNotFoundError
        ):
            load_rules(
                fake_path
            )


    def test_invalid_rules_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = (
                Path(temp_dir)
                / "bad_rules.json"
            )

            file_path.write_text(
                "{ invalid json }",
                encoding="utf-8"
            )

            with self.assertRaisesRegex(
                ValueError,
                "invalid JSON"
            ):
                load_rules(
                    file_path
                )


    def test_rules_must_be_json_object(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = (
                Path(temp_dir)
                / "rules.json"
            )

            file_path.write_text(
                json.dumps(
                    [
                        "not",
                        "an",
                        "object",
                    ]
                ),
                encoding="utf-8"
            )

            with self.assertRaisesRegex(
                ValueError,
                "JSON object"
            ):
                load_rules(
                    file_path
                )


    def test_dataset_without_header(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = (
                Path(temp_dir)
                / "empty.csv"
            )

            file_path.write_text(
                "",
                encoding="utf-8"
            )

            with self.assertRaisesRegex(
                ValueError,
                "header row"
            ):
                load_data(
                    file_path
                )


    # --------------------------------------------------
    # JSON REPORT TESTS
    # --------------------------------------------------

    def test_json_report_structure(self):
        data_file = Path(
            "customers.csv"
        )

        rules_file = Path(
            "rules.json"
        )

        missing_counts = {
            "customer_id": 0,
            "name": 0,
            "age": 1,
            "email": 2,
            "salary": 0,
        }

        unique_results = {
            "customer_id": {
                "duplicate_values": {
                    "1003"
                }
            }
        }

        range_results = {
            "age": {
                "min": 0,
                "max": 120,
                "invalid_values": [
                    "-5",
                    "-5",
                    "240",
                ],
            },

            "salary": {
                "min": 0,
                "max": None,
                "invalid_values": [],
            },
        }

        format_results = {
            "email": {
                "rule_type": "email",
                "invalid_values": [
                    "davidgmail.com"
                ],
            }
        }

        outlier_results = {
            "salary": {
                "statistics": {
                    "minimum": 65000.0,
                    "maximum": 9500000.0,
                    "mean": 1251250.0,
                    "median": 73500.0,
                },

                "outliers": [
                    9500000.0
                ],

                "details": {
                    "q1": 69500.0,
                    "q3": 80000.0,
                    "iqr": 10500.0,
                    "lower_bound": 53750.0,
                    "upper_bound": 95750.0,
                },
            }
        }

        result = build_json_report(
            data_file=data_file,
            rules_file=rules_file,
            total_rows=8,
            total_columns=5,
            total_cells=40,
            missing_counts=missing_counts,
            total_missing=3,
            duplicate_count=1,
            duplicate_percentage=12.5,
            duplicate_severity="MEDIUM",
            unique_results=unique_results,
            range_results=range_results,
            format_results=format_results,
            outlier_results=outlier_results,
            quality_score=87.8,
        )

        self.assertEqual(
            result["dataset"],
            "customers.csv"
        )

        self.assertEqual(
            result["overview"]["rows"],
            8
        )

        self.assertEqual(
            result["missing_values"][
                "total_missing_cells"
            ],
            3
        )

        self.assertEqual(
            result["duplicate_rows"]["count"],
            1
        )

        self.assertEqual(
            result["quality_score"]["score"],
            87.8
        )

        self.assertEqual(
            result["quality_score"]["rating"],
            "GOOD"
        )


    def test_json_report_missing_email(self):
        result = build_json_report(
            data_file=Path(
                "customers.csv"
            ),
            rules_file=Path(
                "rules.json"
            ),
            total_rows=8,
            total_columns=5,
            total_cells=40,
            missing_counts={
                "email": 2
            },
            total_missing=2,
            duplicate_count=0,
            duplicate_percentage=0.0,
            duplicate_severity="NONE",
            unique_results={},
            range_results={},
            format_results={},
            outlier_results={},
            quality_score=95.0,
        )

        email_result = (
            result[
                "missing_values"
            ][
                "columns"
            ][
                "email"
            ]
        )

        self.assertEqual(
            email_result["count"],
            2
        )

        self.assertEqual(
            email_result["percentage"],
            25.0
        )

        self.assertEqual(
            email_result["severity"],
            "HIGH"
        )


if __name__ == "__main__":
    unittest.main()