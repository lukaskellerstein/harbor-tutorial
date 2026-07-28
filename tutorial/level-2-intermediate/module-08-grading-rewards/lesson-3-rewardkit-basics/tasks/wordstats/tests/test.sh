#!/bin/bash
# RewardKit discovers every criterion under /tests, runs them against /app, and
# writes /logs/verifier/reward.json plus /logs/verifier/reward-details.json.
#
# NOTE the `--from` form. The package is named harbor-rewardkit but the
# executable is named rewardkit, so `uvx harbor-rewardkit` FAILS -- uvx would
# look for a command matching the package name. Some published docs show the
# broken form; this is the one that works.

uvx --from 'harbor-rewardkit==0.1.*' rewardkit /tests
