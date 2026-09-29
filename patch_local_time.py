"""Apply a guarded local-clock patch to the pinned upstream XiaoGPT source."""

import hashlib
from pathlib import Path
import sys

SOURCE_SHA256 = "b886772d482bee7d788f305a759176eaba3a0f9f9348f5a1764e58f8de61978b"


def patch_source(source: Path) -> None:
    original = source.read_bytes()
    if hashlib.sha256(original).hexdigest() != SOURCE_SHA256:
        raise SystemExit("Unknown XiaoGPT source; review the patch before upgrading")
    code = original.decode("utf-8")
    import_anchor = "from pathlib import Path\n"
    query_anchor = '            query = new_record.get("query", "").strip()\n'
    if code.count(import_anchor) != 1 or code.count(query_anchor) != 1:
        raise SystemExit("XiaoGPT anchors changed; review the patch")
    code = code.replace(
        import_anchor,
        import_anchor + "from xiaogpt.local_time import local_clock_answer\n",
        1,
    )
    branch = '''            # Answer local time/date before keyword and LLM routing.
            if (answer := local_clock_answer(query)) is not None:
                await self.stop_if_xiaoai_is_playing()
                await self.do_tts(answer)
                if self.in_conversation:
                    await self.wait_for_tts_finish()
                    await self.wakeup_xiaoai()
                continue
'''
    code = code.replace(query_anchor, query_anchor + branch, 1)
    compile(code, str(source), "exec")
    source.write_text(code, encoding="utf-8")
    print(f"Patched local time/date in {source}")


if __name__ == "__main__":
    patch_source(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/app/xiaogpt/xiaogpt.py"))
