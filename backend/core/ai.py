from openai import OpenAI
from .config import config
import time


class AIService:
    def __init__(self):
        # Build one client per tier, each with its OWN key
        self.tiers = []
        for i, cfg in enumerate(config.MODEL_CONFIGS, start=1):
            if not cfg["key"]:
                print(f"[AI] WARNING: Tier {i} has no API key, skipping.")
                continue
            self.tiers.append({
                "tier": i,
                "model": cfg["model"],
                "client": OpenAI(
                    base_url="https://integrate.api.nvidia.com/v1",
                    api_key=cfg["key"],
                    timeout=90.0,
                    max_retries=1,   # Failover handles retries
                ),
            })
        self.system_prompt = config.SYSTEM_PROMPT
        print(f"[AI] Loaded {len(self.tiers)} tiers:")
        for t in self.tiers:
            print(f"[AI]   Tier {t['tier']}: {t['model']}")

    def _call_tier(self, tier, messages):
        """Call a specific tier with its own client/key"""
        kwargs = {
            "model": tier["model"],
            "messages": messages,
            "temperature": 0,
            "top_p": 0.95,
            "max_tokens": 1024,
            "stream": True,
        }
        if "nemotron" in tier["model"].lower():
            kwargs["extra_body"] = {
                "chat_template_kwargs": {"enable_thinking": False}
            }
        return tier["client"].chat.completions.create(**kwargs)

    def chat_stream_with_failover(self, messages):
        """
        Generator: tries each tier (each with its own key).
        Retries top tier once if all fail.
        """
        full_messages = [{"role": "system", "content": self.system_prompt}] + messages

        # Pass 1: full chain. Pass 2: retry top tier after pause.
        passes = [
            ("Pass 1", self.tiers),
            ("Pass 2 (retry top)", self.tiers[:1]),
        ]

        for pass_label, tiers in passes:
            for tier in tiers:
                print(f"[AI] {pass_label} | Tier {tier['tier']}: {tier['model']}...")
                try:
                    stream = self._call_tier(tier, full_messages)
                    got_any = False
                    for chunk in stream:
                        got_any = True
                        yield chunk

                    if got_any:
                        print(f"[AI] {pass_label} | Tier {tier['tier']} SUCCESS")
                        return
                    else:
                        print(f"[AI] {pass_label} | Tier {tier['tier']} empty, next...")
                        continue

                except Exception as e:
                    print(f"[AI] {pass_label} | Tier {tier['tier']} FAILED: {type(e).__name__}: {e}")
                    continue

            if pass_label == "Pass 1":
                print("[AI] All tiers failed. Waiting 3s before retry...")
                time.sleep(3)

        raise Exception("All Nemotron tiers failed after full retry.")

    def chat_sync(self, messages: list) -> str:
        """Non-streaming with same failover"""
        full_messages = [{"role": "system", "content": self.system_prompt}] + messages

        for pass_num in range(2):
            for tier in self.tiers:
                try:
                    kwargs = {
                        "model": tier["model"],
                        "messages": full_messages,
                        "temperature": 0,
                        "top_p": 0.95,
                        "max_tokens": 1024,
                    }
                    if "nemotron" in tier["model"].lower():
                        kwargs["extra_body"] = {
                            "chat_template_kwargs": {"enable_thinking": False}
                        }

                    response = tier["client"].chat.completions.create(**kwargs)
                    print(f"[AI] Pass {pass_num + 1} | Tier {tier['tier']} SUCCESS")
                    return response.choices[0].message.content

                except Exception as e:
                    print(f"[AI] Pass {pass_num + 1} | Tier {tier['tier']} FAILED: {e}")
                    continue

            if pass_num == 0:
                print("[AI] Sync: all tiers failed, waiting 3s...")
                time.sleep(3)

        raise Exception("All Nemotron tiers failed")


ai_service = AIService()