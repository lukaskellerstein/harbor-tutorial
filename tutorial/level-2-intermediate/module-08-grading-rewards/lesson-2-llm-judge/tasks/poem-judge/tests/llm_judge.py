# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "openai>=1.60",
#   "pydantic>=2.9",
# ]
# ///
#
# PEP 723 inline metadata. `uv run` reads the block above, builds a throwaway
# environment with exactly these packages, and runs the script -- so the judge's
# dependencies live next to the judge instead of in the task's Dockerfile.
#
# https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies

import json
import os
import sys
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel, Field

POEM_PATH = Path("/app/poem.txt")
REWARD_PATH = Path("/logs/verifier/reward.json")

# The rubric. Writing it down explicitly is the whole job -- "is this good?" is
# not a gradable question, but each of these is.
RUBRIC = {
    "funny": "Is this poem actually funny? Consider wit, timing, and whether the "
    "joke lands, not merely whether it is competently written.",
    "on_topic": "Is the poem genuinely about debugging code -- bugs, stack traces, "
    "print statements, failing tests? A poem about programming in general "
    "is not enough.",
}

# Strict JSON schema, written out by hand so the contract with the model is
# visible. Strict mode requires every property to be listed in `required` and
# `additionalProperties` to be false.
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        name: {
            "type": "object",
            "properties": {
                "score": {
                    "type": "number",
                    "description": "Score from 0.0 to 1.0.",
                },
                "reasoning": {
                    "type": "string",
                    "description": "One sentence justifying the score.",
                },
            },
            "required": ["score", "reasoning"],
            "additionalProperties": False,
        }
        for name in RUBRIC
    },
    "required": list(RUBRIC),
    "additionalProperties": False,
}


class CriterionScore(BaseModel):
    """One judged criterion. Validated before we trust it."""

    score: float = Field(ge=0.0, le=1.0)
    reasoning: str


class JudgeResponse(BaseModel):
    funny: CriterionScore
    on_topic: CriterionScore


def deterministic_checks(poem: str) -> dict[str, float]:
    """Everything that can be measured without an LLM, measured without one.

    Judges are slow, cost money, and disagree with themselves. Never spend one
    on a question `len()` can answer.
    """
    lines = [line for line in poem.splitlines() if line.strip()]
    return {"line_count": 1.0 if len(lines) >= 4 else 0.0}


def judge(poem: str) -> JudgeResponse:
    """Ask the model to score the rubric, and validate what comes back."""
    # OpenAI() picks up OPENAI_BASE_URL and OPENAI_API_KEY from the environment,
    # which task.toml pointed at the LiteLLM gateway.
    client = OpenAI()
    model = os.environ.get("JUDGE_MODEL", "gemma-large")

    criteria_text = "\n".join(f"- {name}: {desc}" for name, desc in RUBRIC.items())

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an evaluation judge. Score the submission against "
                    "each criterion from 0.0 to 1.0 and justify each score in "
                    "one sentence. Be discriminating: 1.0 means excellent, not "
                    "merely acceptable.\n\n" + criteria_text
                ),
            },
            {"role": "user", "content": f"Poem to evaluate:\n\n{poem}"},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "judge_response",
                "strict": True,
                "schema": RESPONSE_SCHEMA,
            },
        },
    )

    raw = response.choices[0].message.content or ""
    # Validate rather than trust. A model that returns a score of 7.5 on a 0-1
    # scale should fail loudly here, not silently inflate the reward.
    return JudgeResponse.model_validate_json(raw)


def main() -> None:
    REWARD_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not POEM_PATH.exists():
        print(f"{POEM_PATH} does not exist -- nothing to judge.")
        # Do not call the LLM just to have it score an empty string.
        REWARD_PATH.write_text(json.dumps({"line_count": 0.0, "funny": 0.0, "on_topic": 0.0, "reward": 0.0}))
        return

    poem = POEM_PATH.read_text()
    scores = deterministic_checks(poem)
    print(f"deterministic: {scores}")

    try:
        verdict = judge(poem)
    except Exception as exc:
        # Do NOT swallow this into a 0.0 reward -- a broken judge and a bad poem
        # would then look identical. Fail the verifier instead.
        print(f"Judge call failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise

    for name in RUBRIC:
        criterion: CriterionScore = getattr(verdict, name)
        scores[name] = criterion.score
        print(f"{name}: {criterion.score:.2f} -- {criterion.reasoning}")

    # The "reward" roll-up, so one-dimensional tooling has something to read.
    scores["reward"] = round(sum(scores.values()) / len(scores), 3)

    REWARD_PATH.write_text(json.dumps(scores, indent=2))
    print(f"\nwrote {REWARD_PATH}: {scores}")


if __name__ == "__main__":
    main()
