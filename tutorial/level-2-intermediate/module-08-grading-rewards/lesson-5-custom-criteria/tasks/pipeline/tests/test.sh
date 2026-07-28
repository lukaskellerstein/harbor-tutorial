#!/bin/bash
# Unchanged from lessons 3 and 4. RewardKit works out the dimensions from the
# directory layout -- the entry point never has to know about them.

uvx --from 'harbor-rewardkit==0.1.*' rewardkit /tests
