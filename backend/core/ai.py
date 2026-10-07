"""
JARVIS-VOICE AI Service
3-tier NVIDIA Nemotron failover chain using 3 separate API keys.

Tier 1: Ultra 550B         — thinking ON
Tier 2: Lightning 30B      — thinking OFF (fast)
Tier 3: Nano Omni 30B      — thinking ON (reasoning fallback)
"""

import json
from typing import Generator, Optional
from openai import OpenAI

from core.config import (
    MODEL_CONFIGS,
    NVIDIA_BASE_URL,
    SYSTEM_PROMPT,
)


# ============================================================
# AI SERVICE
# ============================================================
class AIService:
    def __init__(self):
        self.clients = {}
        for mc in MODEL_CONFIGS:
            tier = mc["tier"]
            self.clients[tier] = OpenAI(
                base_url=NVIDIA_BASE_URL,
                api_key=mc["api_key"],
                timeout=60.0,
            )

        self.tiers = MODEL_CONFIGS
        print(f"[AI] Loaded {len(self.tiers)} tiers:")
        for mc in self.tiers:
            think = "ON" if mc.get("enable_thinking") else "OFF"
            print(f"[AI]   Tier {mc['tier']}: {mc['model']} (thinking: {think})")

    # ----------------------------------------------------------
    # BUILD extra_body FOR EACH TIER
    # ----------------------------------------------------------
    def _build_extra_body(self, tier_config: dict) -> Optional[dict]:
        """
        Build the extra_body for the request based on this tier's config.

        - enable_thinking=True  → send chat_template_kwargs.enable_thinking=True
        - enable_thinking=False → send chat_template_kwargs.enable_thinking=False
        - Also include reasoning_budget if present
        """
        extra = {}

        # Handle thinking flag explicitly (True OR False)
        if "enable_thinking" in tier_config:
            extra["chat_template_kwargs"] = {
                "enable_thinking": bool(tier_config["enable_thinking"])
            }

        # Reasoning budget (only for reasoning-capable tiers)
        if tier_config.get("reasoning_budget"):
            extra["reasoning_budget"] = tier_config["reasoning_budget"]

        return extra if extra else None

    # ----------------------------------------------------------
    # SINGLE TIER ATTEMPT
    # ----------------------------------------------------------
    def _try_tier(self, tier_config: dict, messages: list) -> Optional[Generator]:
        tier = tier_config["tier"]
        model = tier_config["model"]
        client = self.clients[tier]
        think = "ON" if tier_config.get("enable_thinking") else "OFF"

        print(f"[AI] Pass 1 | Tier {tier} ({think}): {model}...")

        try:
            extra = self._build_extra_body(tier_config)

            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                top_p=0.95,
                max_tokens=tier_config.get("max_tokens", 4096),
                extra_body=extra,
                stream=True,
            )

            # Peek at the first chunk to confirm it works
            first_chunk = None
            try:
                for chunk in completion:
                    first_chunk = chunk
                    break
            except Exception as e:
                raise e

            if first_chunk is None:
                raise RuntimeError("No chunks returned")

            print(f"[AI] Pass 1 | Tier {tier} SUCCESS")

            def _chain():
                yield first_chunk
                for c in completion:
                    yield c

            return _chain()

        except Exception as e:
            print(f"[AI] Pass 1 | Tier {tier} FAILED: {type(e).__name__}: {e}")
            return None

    # ----------------------------------------------------------
    # STREAMING CHAT WITH FAILOVER
    # ----------------------------------------------------------
    def chat_stream_with_failover(
        self,
        messages: list,
        system_prompt: Optional[str] = None,
    ):
        full_messages = [
            {"role": "system", "content": system_prompt or SYSTEM_PROMPT}
        ] + messages

        for tier_config in self.tiers:
            result = self._try_tier(tier_config, full_messages)
            if result is not None:
                for chunk in result:
                    yield chunk
                return

        print("[AI] ❌ ALL TIERS FAILED")
        raise RuntimeError("All AI tiers failed. Check API keys and model availability.")

    # ----------------------------------------------------------
    # SYNC CHAT
    # ----------------------------------------------------------
    def chat_sync(self, messages: list, system_prompt: Optional[str] = None) -> str:
        full_messages = [
            {"role": "system", "content": system_prompt or SYSTEM_PROMPT}
        ] + messages

        for tier_config in self.tiers:
            tier = tier_config["tier"]
            model = tier_config["model"]
            client = self.clients[tier]

            print(f"[AI] Sync | Tier {tier}: {model}...")
            try:
                extra = self._build_extra_body(tier_config)

                completion = client.chat.completions.create(
                    model=model,
                    messages=full_messages,
                    temperature=0.7,
                    top_p=0.95,
                    max_tokens=tier_config.get("max_tokens", 4096),
                    extra_body=extra,
                    stream=False,
                )

                content = completion.choices[0].message.content or ""
                print(f"[AI] Sync | Tier {tier} SUCCESS ({len(content)} chars)")
                return content

            except Exception as e:
                print(f"[AI] Sync | Tier {tier} FAILED: {type(e).__name__}: {e}")
                continue

        raise RuntimeError("All AI tiers failed (sync mode).")


# ============================================================
# SINGLETON
# ============================================================
ai_service = AIService()