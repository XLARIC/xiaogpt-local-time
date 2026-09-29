import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from local_time import local_clock_answer


class LocalClockTests(unittest.TestCase):
    def answer(self, query, utc, zone):
        with patch.dict(os.environ, {"TZ": zone}):
            return local_clock_answer(query, datetime.fromisoformat(utc).replace(tzinfo=timezone.utc))

    def test_same_instant_has_different_local_dates(self):
        utc = "2026-01-01T00:30:00"
        self.assertEqual(self.answer("现在几点了", utc, "Pacific/Auckland"), "现在是下午1点30分")
        self.assertEqual(self.answer("几点了", utc, "Asia/Shanghai"), "现在是早上8点30分")
        self.assertEqual(self.answer("今天几号了", utc, "America/Los_Angeles"), "今天是2025年12月31日，星期三")
        self.assertEqual(self.answer("今天几号了", utc, "Pacific/Auckland"), "今天是2026年1月1日，星期四")

    def test_auckland_spring_dst_jump(self):
        before = self.answer("几点了", "2026-09-26T13:59:00", "Pacific/Auckland")
        after = self.answer("几点了", "2026-09-26T14:00:00", "Pacific/Auckland")
        self.assertEqual(before, "现在是凌晨1点59分")
        self.assertEqual(after, "现在是凌晨3点00分")

    def test_auckland_autumn_dst_repeat(self):
        self.assertEqual(self.answer("几点了", "2026-04-04T13:59:00", "Pacific/Auckland"), "现在是凌晨2点59分")
        self.assertEqual(self.answer("几点了", "2026-04-04T14:00:00", "Pacific/Auckland"), "现在是凌晨2点00分")

    def test_london_dst_and_midnight(self):
        self.assertEqual(self.answer("几点了", "2026-07-01T23:05:00", "Europe/London"), "现在是凌晨12点05分")
        self.assertEqual(self.answer("今天是几号", "2026-07-01T23:05:00", "Europe/London"), "今天是2026年7月2日，星期四")

    def test_punctuation_prefix_and_combined_request(self):
        self.assertEqual(self.answer(" 请告诉我，今天几号了？ ", "2026-01-01T00:30:00", "Asia/Shanghai"), "今天是2026年1月1日，星期四")
        self.assertEqual(self.answer("今天几号，现在几点？", "2026-01-01T00:30:00", "Asia/Shanghai"), "今天是2026年1月1日，星期四，现在是早上8点30分")
        self.assertEqual(self.answer("今天周几？", "2026-01-01T00:30:00", "Asia/Shanghai"), "今天是星期四")

    def test_other_questions_remain_for_upstream(self):
        for query in ("明天几点开会", "今天几号车到上海", "帮我讲一个故事", "奥克兰现在几点"):
            self.assertIsNone(self.answer(query, "2026-01-01T00:30:00", "Asia/Shanghai"))

    def test_bad_timezone_fails_instead_of_silent_wrong_answer(self):
        with self.assertRaises(KeyError):
            self.answer("几点了", "2026-01-01T00:30:00", "Not/AZone")

    def test_naive_clock_rejected(self):
        with patch.dict(os.environ, {"TZ": "Etc/UTC"}):
            with self.assertRaises(ValueError):
                local_clock_answer("几点了", datetime(2026, 1, 1))


if __name__ == "__main__":
    unittest.main()
