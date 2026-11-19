import unittest
from captions import timestamp, srt_for_clip, score_speech

class CaptionTests(unittest.TestCase):
    def test_timestamp(self):
        self.assertEqual(timestamp(61.234), "00:01:01,234")
    def test_clipped_srt(self):
        segments = [{"start": 4, "end": 8, "text": "hello world"}]
        srt = srt_for_clip(segments, 5, 10)
        self.assertIn("00:00:00,000 --> 00:00:03,000", srt)
        self.assertIn("hello world", srt)
    def test_speech_density(self):
        segments = [{"start": 0, "end": 10, "text": "one two three four"}]
        self.assertGreater(score_speech(0, 10, segments), score_speech(10, 20, segments))
if __name__ == "__main__":
    unittest.main()
