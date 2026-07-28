#!/bin/bash
# Identical to lesson 3's. RewardKit discovers judge.toml the same way it
# discovers checks.py -- a rubric is just another kind of criteria file.

uvx --from 'harbor-rewardkit==0.1.*' rewardkit /tests
