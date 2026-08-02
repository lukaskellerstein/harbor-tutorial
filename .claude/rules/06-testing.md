---
description: "Step 4: Testing — define DoD, test, fix and repeat until passing"
---

# Step 4: Testing

**Every code change must be tested before reporting completion. No exceptions.**

## 4a. Define your Definition of Done

Before testing, **write out your DoD checklist in the conversation** so the user
can see what you intend to verify. Example:

> **Definition of Done for this lesson:**
>
> - [ ] `uv sync` resolves without error in the leaf
> - [ ] `uv run python main.py` completes and prints the expected sections
> - [ ] The trial produced a reward of 1.0 with the oracle solution
> - [ ] The README's step-by-step matches what the run actually printed

## 4b. Test

**Lesson / Python changes** — run the affected lesson end-to-end. There is no
repo-wide test suite; running it *is* the test.

```bash
cd tutorial/<level>/<module>/<lesson>
uv sync
uv run python main.py
```

Before that, confirm the environment is actually up — a lesson failing because
Docker is stopped is not a lesson bug:

```bash
docker ps                        # daemon alive?
uv run python infra/verify.py    # every prerequisite, OK/FAIL per item
cd infra && docker compose ps    # qdrant + litellm, if the lesson needs them
```

What to actually check, beyond "it exited 0":

- **The reward.** A trial that runs but scores 0.0 when the oracle solution
  should score 1.0 is the characteristic failure here, and it exits cleanly.
  Read `jobs/<timestamp>/*/result.json` or `verifier/reward.txt`.
- **The console output.** Lessons teach by printing; if the section headers and
  progress lines are missing or wrong, the lesson is broken even though the code
  ran.
- **The README matches the run.** If you changed behaviour, the step-by-step and
  any sample output in `README.md` are now stale.
- **Clean up.** `docker compose down` only if you brought it up and the user is
  not mid-session; never `-v`, which destroys the `qdrant-data` volume.

**Every code change** — repo-wide lint / format / type check, from this
machine's gated tooling:

```bash
nvim-tools --json --all
```

Your change must not add findings (compare against the Understand-step
baseline). Tools reporting `gated-off` have no config in this repo — expected
under "no config, no tool", not a failure. This complements running the lesson;
it never replaces it.

**Non-testable changes** (docs, config, IaC only): explicitly state why no
runtime test is needed.

## 4c. Fix and repeat

If a test fails: fix the issue, then retest. Repeat until all DoD items pass. If
you hit a problem you repeatedly cannot resolve, ask the user for help rather
than reporting partial success.

## 4d. Never report completion without testing

If you write code and stop without verifying it works, you have failed. Testing
is YOUR responsibility — the user should never need to ask you to test.

This matters more here than in most repos: the output is teaching material. A
learner who hits a broken lesson has no way to tell your bug from their own
mistake, and will assume it is theirs.
