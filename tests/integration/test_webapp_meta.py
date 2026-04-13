import unittest
from pathlib import Path

from BusinessLogic.WebAppManager import WebAppManager


class TestWebAppMetaIntegration(unittest.TestCase):
    def test_get_meta_returns_core_keys(self):
        project_root = Path(__file__).resolve().parents[2]
        db_path = str(project_root / "Databank" / "StandplaetzeDatabank.db")
        manager = WebAppManager(db_path)

        meta = manager.get_meta()

        self.assertIn("locations", meta)
        self.assertIn("campaigns", meta)
        self.assertIn("users", meta)
        self.assertIn("next_booking_id", meta)
        self.assertIn("next_stand_id", meta)


if __name__ == "__main__":
    unittest.main()
