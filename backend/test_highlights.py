import unittest
from highlights import rank_windows

class HighlightTests(unittest.TestCase):
    def test_short_video(self):
        self.assertEqual(rank_windows(12, 30, lambda s, d: 0)[0]["end"], 12)
    def test_prefers_loud_sections(self):
        clips = rank_windows(120, 30, lambda s, d: 10 if s >= 80 else 0)
        self.assertTrue(any(clip["start"] >= 80 for clip in clips))
    def test_no_overlap(self):
        clips = rank_windows(240, 30, lambda s, d: s)
        for a, b in zip(clips, clips[1:]):
            self.assertLessEqual(a["end"], b["start"])
    def test_invalid_audio(self):
        self.assertTrue(rank_windows(90, 30, lambda s, d: float("nan")))
if __name__ == "__main__":
    unittest.main()
