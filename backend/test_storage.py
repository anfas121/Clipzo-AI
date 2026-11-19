import tempfile
import unittest
from pathlib import Path
from storage import cleanup_media

class StorageTests(unittest.TestCase):
    def test_removes_expired_media_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            old = root / "old.mp4"
            fresh = root / "fresh.mp4"
            unrelated = root / "config.txt"
            for p in (old, fresh, unrelated):
                p.write_text("data")
            import os
            os.utime(old, (0, 0))
            os.utime(unrelated, (0, 0))
            self.assertEqual(cleanup_media(root, max_age_hours=1, now=7200), ["old.mp4"])
            self.assertTrue(fresh.exists())
            self.assertTrue(unrelated.exists())
    def test_rejects_invalid_retention(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                cleanup_media(Path(folder), 0)
if __name__ == "__main__":
    unittest.main()
