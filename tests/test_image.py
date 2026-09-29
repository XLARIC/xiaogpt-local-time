"""Offline integration checks, executed inside the built image."""

import asyncio
import os
import sys
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

sys.path.insert(0, "/app")

from xiaogpt.config import Config
from xiaogpt.local_time import local_clock_answer
from xiaogpt.xiaogpt import MiGPT


class EndRecords(Exception):
    pass


class Records:
    def __init__(self, query):
        self.query = query
        self.used = False

    async def get(self):
        if self.used:
            raise EndRecords
        self.used = True
        return {"query": self.query}


class RoutingTests(unittest.IsolatedAsyncioTestCase):
    async def run_query(self, query, conversation=False):
        gpt = MiGPT.__new__(MiGPT)
        gpt.config = SimpleNamespace(keyword=["请", "帮我"], start_conversation="开始持续对话", end_conversation="结束持续对话")
        gpt.last_record = Records(query)
        gpt.polling_event = asyncio.Event()
        gpt.in_conversation = conversation
        gpt.init_all_data = AsyncMock()
        gpt.poll_latest_ask = AsyncMock()
        gpt.stop_if_xiaoai_is_playing = AsyncMock()
        gpt.do_tts = AsyncMock()
        gpt.wait_for_tts_finish = AsyncMock()
        gpt.wakeup_xiaoai = AsyncMock()
        gpt.need_ask_gpt = lambda record: (_ for _ in ()).throw(AssertionError("Local question reached LLM routing"))
        with patch("xiaogpt.xiaogpt.local_clock_answer", wraps=local_clock_answer):
            with self.assertRaises(EndRecords):
                await gpt.run_forever()
        await asyncio.sleep(0)
        gpt.stop_if_xiaoai_is_playing.assert_awaited_once()
        gpt.do_tts.assert_awaited_once()
        return gpt

    async def test_time_without_keyword_is_intercepted(self):
        gpt = await self.run_query("现在几点了")
        self.assertTrue(gpt.do_tts.call_args.args[0].startswith("现在是"))
        gpt.wakeup_xiaoai.assert_not_awaited()

    async def test_date_without_keyword_is_intercepted(self):
        gpt = await self.run_query("今天几号了")
        self.assertTrue(gpt.do_tts.call_args.args[0].startswith("今天是"))

    async def test_continuous_conversation_resumes_after_tts(self):
        gpt = await self.run_query("几点了", conversation=True)
        gpt.wait_for_tts_finish.assert_awaited_once()
        gpt.wakeup_xiaoai.assert_awaited_once()

    async def test_other_question_reaches_original_routing(self):
        gpt = MiGPT.__new__(MiGPT)
        gpt.config = SimpleNamespace(keyword=["请"], start_conversation="开始持续对话", end_conversation="结束持续对话")
        gpt.last_record = Records("帮我讲一个故事")
        gpt.polling_event = asyncio.Event()
        gpt.in_conversation = False
        gpt.init_all_data = AsyncMock()
        gpt.poll_latest_ask = AsyncMock()
        gpt.need_change_prompt = lambda record: False
        def routed(record):
            raise EndRecords
        gpt.need_ask_gpt = routed
        gpt.do_tts = AsyncMock()
        with self.assertRaises(EndRecords):
            await gpt.run_forever()
        await asyncio.sleep(0)
        gpt.do_tts.assert_not_awaited()


class ConfigurationTests(unittest.TestCase):
    def test_examples_are_readable_by_upstream(self):
        for n in range(1, 4):
            raw = Config.read_from_file(f"/tests/speaker{n}/config.example.yaml")
            config = Config(**raw)
            self.assertEqual(config.hardware, "LX06")
            self.assertEqual(config.bot, "gemini")
            self.assertEqual(config.gemini_model, "gemini-2.5-flash-lite")

    def test_image_does_not_contain_user_credentials(self):
        self.assertFalse(Path("/root/.mi.token").exists())
        self.assertFalse(Path("/config/config.yaml").exists())


if __name__ == "__main__":
    unittest.main()
