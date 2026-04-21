"""
MeetingAnalyzer — core inference engine.

Sends the transcript + role-specific prompt to Ollama (gemma4:e4b) in JSON
mode and validates the response against MeetingOutput with a retry loop.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Optional

import ollama
from pydantic import ValidationError

from core.prompts import ROLE_PROMPTS
from core.schema import MeetingOutput

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

MAX_RETRIES = 2  # total attempts = 1 initial + MAX_RETRIES


class MeetingAnalyzer:
    """Analyse a meeting transcript through a role-specific lens."""

    def __init__(self, model: str = "gemma4:e2b") -> None:
        self.model = model

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def analyze(self, transcript: str, role: str) -> MeetingOutput:
        """
        Run role-aware analysis on *transcript* and return validated output.

        Parameters
        ----------
        transcript : str
            Raw meeting transcript text.
        role : str
            One of "Engineering", "Product", or "Management".

        Returns
        -------
        MeetingOutput
            Pydantic-validated structured meeting analysis.

        Raises
        ------
        ValueError
            If *role* is not recognised.
        RuntimeError
            If inference fails after all retries.
        """
        if role not in ROLE_PROMPTS:
            raise ValueError(
                f"Unknown role '{role}'. Choose from: {list(ROLE_PROMPTS)}"
            )

        system_prompt = ROLE_PROMPTS[role]
        user_prompt = (
            f"Analyse the following meeting transcript:\n\n{transcript}"
        )

        last_error: Optional[Exception] = None

        for attempt in range(1, MAX_RETRIES + 2):  # 1-indexed, up to 3
            logger.info(
                "Attempt %d/%d — calling %s (role=%s)",
                attempt,
                MAX_RETRIES + 1,
                self.model,
                role,
            )

            try:
                response = ollama.generate(
                    model=self.model,
                    system=system_prompt,
                    prompt=user_prompt,
                    format="json",
                    options={"temperature": 0},  # deterministic output
                )

                raw_text: str = response["response"]
                logger.debug("Raw LLM response:\n%s", raw_text)

                # Parse and validate
                data = json.loads(raw_text)
                result = MeetingOutput.model_validate(data)

                logger.info("✓ Validation passed on attempt %d", attempt)
                return result

            except (json.JSONDecodeError, ValidationError) as exc:
                last_error = exc
                logger.warning(
                    "Attempt %d failed — %s: %s", attempt, type(exc).__name__, exc
                )
            except Exception as exc:
                # Connection errors, model-not-found, etc.
                last_error = exc
                logger.error(
                    "Attempt %d — Ollama error: %s: %s",
                    attempt,
                    type(exc).__name__,
                    exc,
                )
                raise RuntimeError(
                    f"Ollama inference failed: {exc}"
                ) from exc

        raise RuntimeError(
            f"All {MAX_RETRIES + 1} attempts failed. Last error: {last_error}"
        )


# ===================================================================== #
# Quick smoke-test with a hardcoded messy transcript
# ===================================================================== #
if __name__ == "__main__":
    SAMPLE_TRANSCRIPT = """
    [10:02] Sarah: ok so, umm, we need to talk about the auth migration.
    The old OAuth flow is basically held together with duct tape at this point.
    [10:03] Raj: yeah I looked at it last week — the token refresh logic has
    like three race conditions. I can probably fix it but it'll take the whole
    sprint.
    [10:04] Sarah: fine let's commit to that. Raj owns the auth refactor,
    high priority.  We CANNOT ship v2.1 with the old flow.
    [10:05] Mike (PM): noted.  speaking of v2.1 — design team says the new
    onboarding screens are ready for review.  We should get eng feedback by
    Thursday.
    [10:06] Sarah: ok who wants to review onboarding?  …anyone?  fine, I'll
    do it myself.  Also — Raj, can you update the API rate-limit config?
    Keep getting 429s in staging.
    [10:07] Raj: sure, medium priority I guess.
    [10:08] Mike: last thing — budget review is Monday.  Amy from finance
    wants headcount projections.  Someone needs to pull those numbers.
    Nobody volunteered so I guess I'll flag it to leadership.
    [10:09] Sarah: sounds good. ok let's wrap, standup at 10 tomorrow same
    link.  oh wait — we decided to drop the legacy CSV export right?  Nobody
    uses it.
    [10:10] Raj: yeah agreed, rip it out.
    [10:10] Mike: confirmed. let's kill it.
    """

    analyzer = MeetingAnalyzer()

    for role in ["Engineering", "Product", "Management"]:
        print(f"\n{'='*72}")
        print(f"  ROLE: {role}")
        print(f"{'='*72}")
        try:
            output = analyzer.analyze(SAMPLE_TRANSCRIPT, role)
            print(output.model_dump_json(indent=2))
        except RuntimeError as e:
            print(f"ERROR: {e}", file=sys.stderr)
