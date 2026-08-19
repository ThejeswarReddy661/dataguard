import json
import tempfile
import unittest
from pathlib import Path

from src.history import (
    calculate_score_change,
    create_snapshot,
    get_dataset_history,
    get_history_path,
    get_latest_snapshot,
    load_history,
    save_snapshot,
)


class TestDataGuardHistory(
    unittest.TestCase
):

    def setUp(self):
        self.temp_directory = (
            tempfile.TemporaryDirectory()
        )

        self.project_root = Path(
            self.temp_directory.name
        )


    def tearDown(self):
        self.temp_directory.cleanup()


    def test_create_snapshot(self):
        snapshot = create_snapshot(
            dataset="customers.csv",
            rows=100,
            columns=5,
            quality_score=91.5,
            missing_values=3,
            duplicate_rows=1,
            invalid_values=2,
            unusual_values=1,
            analysis_seconds=0.25,
        )

        self.assertEqual(
            snapshot["dataset"],
            "customers.csv",
        )

        self.assertEqual(
            snapshot["rows"],
            100,
        )

        self.assertEqual(
            snapshot["quality_score"],
            91.5,
        )

        self.assertIn(
            "timestamp",
            snapshot,
        )


    def test_history_path_created(self):
        history_path = (
            get_history_path(
                self.project_root
            )
        )

        self.assertEqual(
            history_path.name,
            "quality_history.jsonl",
        )

        self.assertTrue(
            history_path.parent.exists()
        )


    def test_save_and_load_snapshot(self):
        snapshot = create_snapshot(
            dataset="customers.csv",
            rows=8,
            columns=5,
            quality_score=84.4,
            missing_values=3,
            duplicate_rows=1,
            invalid_values=4,
            unusual_values=1,
            analysis_seconds=0.01,
        )

        save_snapshot(
            snapshot,
            self.project_root,
        )

        history = load_history(
            self.project_root
        )

        self.assertEqual(
            len(history),
            1,
        )

        self.assertEqual(
            history[0]["dataset"],
            "customers.csv",
        )


    def test_multiple_snapshots(self):
        for score in (
            90.0,
            87.5,
            84.4,
        ):

            snapshot = create_snapshot(
                dataset="customers.csv",
                rows=8,
                columns=5,
                quality_score=score,
                missing_values=3,
                duplicate_rows=1,
                invalid_values=4,
                unusual_values=1,
                analysis_seconds=0.01,
            )

            save_snapshot(
                snapshot,
                self.project_root,
            )

        history = load_history(
            self.project_root
        )

        self.assertEqual(
            len(history),
            3,
        )


    def test_dataset_history_filter(self):
        customer_snapshot = (
            create_snapshot(
                dataset="customers.csv",
                rows=8,
                columns=5,
                quality_score=84.4,
                missing_values=3,
                duplicate_rows=1,
                invalid_values=4,
                unusual_values=1,
                analysis_seconds=0.01,
            )
        )

        employee_snapshot = (
            create_snapshot(
                dataset="employees.csv",
                rows=8,
                columns=5,
                quality_score=89.4,
                missing_values=1,
                duplicate_rows=1,
                invalid_values=4,
                unusual_values=1,
                analysis_seconds=0.01,
            )
        )

        save_snapshot(
            customer_snapshot,
            self.project_root,
        )

        save_snapshot(
            employee_snapshot,
            self.project_root,
        )

        history = get_dataset_history(
            self.project_root,
            "employees.csv",
        )

        self.assertEqual(
            len(history),
            1,
        )

        self.assertEqual(
            history[0]["dataset"],
            "employees.csv",
        )


    def test_latest_snapshot(self):
        first = create_snapshot(
            dataset="customers.csv",
            rows=8,
            columns=5,
            quality_score=90.0,
            missing_values=2,
            duplicate_rows=0,
            invalid_values=2,
            unusual_values=0,
            analysis_seconds=0.01,
        )

        second = create_snapshot(
            dataset="customers.csv",
            rows=8,
            columns=5,
            quality_score=84.4,
            missing_values=3,
            duplicate_rows=1,
            invalid_values=4,
            unusual_values=1,
            analysis_seconds=0.01,
        )

        save_snapshot(
            first,
            self.project_root,
        )

        save_snapshot(
            second,
            self.project_root,
        )

        latest = get_latest_snapshot(
            self.project_root,
            "customers.csv",
        )

        self.assertEqual(
            latest["quality_score"],
            84.4,
        )


    def test_score_change(self):
        history = [
            {
                "quality_score": 91.5
            },
            {
                "quality_score": 84.4
            },
        ]

        change = (
            calculate_score_change(
                history
            )
        )

        self.assertEqual(
            change["previous_score"],
            91.5,
        )

        self.assertEqual(
            change["current_score"],
            84.4,
        )

        self.assertEqual(
            change["change"],
            -7.1,
        )


    def test_score_change_requires_two_snapshots(
        self
    ):
        history = [
            {
                "quality_score": 84.4
            }
        ]

        self.assertIsNone(
            calculate_score_change(
                history
            )
        )


    def test_invalid_history_line_is_skipped(
        self
    ):
        history_path = get_history_path(
            self.project_root
        )

        history_path.write_text(
            (
                '{"dataset": "customers.csv", '
                '"quality_score": 90}\n'
                'invalid-json\n'
            ),
            encoding="utf-8",
        )

        history = load_history(
            self.project_root
        )

        self.assertEqual(
            len(history),
            1,
        )


if __name__ == "__main__":
    unittest.main()