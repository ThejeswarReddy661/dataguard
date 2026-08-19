import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


PROJECT_ROOT = Path(__file__).parent.parent
DASHBOARD_FILE = (
    PROJECT_ROOT
    / "src"
    / "dashboard.py"
)


class TestDataGuardDashboard(unittest.TestCase):

    def setUp(self):
        self.app = AppTest.from_file(
            DASHBOARD_FILE,
            default_timeout=10,
        ).run()


    def test_dashboard_loads_without_exception(self):
        self.assertEqual(
            len(self.app.exception),
            0,
        )


    def test_dashboard_has_metrics(self):
        self.assertGreaterEqual(
            len(self.app.metric),
            5,
        )


    def test_dashboard_has_data_source_controls(self):
        self.assertGreaterEqual(
            len(self.app.radio),
            1,
        )

        self.assertGreaterEqual(
            len(self.app.selectbox),
            1,
        )


    def test_dashboard_has_report_downloads(self):
        self.assertEqual(
            len(self.app.download_button),
            2,
        )


    def test_dashboard_has_advanced_sections(self):
        self.assertGreaterEqual(
            len(self.app.expander),
            4,
        )


if __name__ == "__main__":
    unittest.main()