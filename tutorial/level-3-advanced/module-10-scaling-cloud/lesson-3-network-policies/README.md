# Network Policies

**Duration:** 30-45 minutes

## Overview

When evaluating AI agents, controlling network access is critical for both security and reproducibility. Harbor provides three network modes -- `no-network`, `public`, and `allowlist` -- that let you precisely control what each container can reach. This lesson explains all three modes, shows how to configure them in `task.toml`, and runs example tasks demonstrating no-network and public modes.

## Prerequisites

- Completed Level 1 and Level 2 of the Harbor Tutorial
- Completed Lessons 1-2 of Module 10 (recommended)
- Harbor CLI installed (`uv tool install harbor`)
- Docker installed and running

## Concepts

### The Three Network Modes

Harbor defines network access via the `NetworkMode` enum:

1. **`public`** (default) -- Full internet access. The container can reach any host.
2. **`no-network`** -- Complete isolation. No outbound connections allowed.
3. **`allowlist`** -- Selective access. Only specified hosts/IPs are reachable.

### Phase-Specific Policies

Network policies can be set at three levels in `task.toml`:

- **`[environment]`** -- The baseline for the container
- **`[agent]`** -- Override during the agent execution phase
- **`[verifier]`** -- Override during the verification phase

The resolution order is: phase-specific setting wins over environment baseline.

### Allowlist Entry Types

The allowlist supports several entry types:
- Exact hostname: `"example.com"`
- Wildcard hostname: `"*.example.com"`
- IPv4/IPv6 addresses: `"192.0.2.1"`, `"2001:db8::1"`
- CIDR ranges: `"192.0.2.0/24"`, `"2001:db8::/32"`

### Run-Time Host Merging

Job configs can add `extra_allowed_hosts` to merge additional hosts into the task's baseline policy at run time, without modifying the task itself.

## Step-by-Step

### Step 1: Check Prerequisites

Verify Harbor CLI and Docker are available.

### Step 2: Learn the Three Modes

Review the three network modes and when to use each one.

### Step 3: Configuration in task.toml

Learn how to set network modes at the environment, agent, and verifier levels, and understand phase resolution order.

### Step 4: Allowlist Configuration

Learn how to specify allowed hosts with hostnames, wildcards, IPs, and CIDR ranges. Understand run-time host merging via `extra_allowed_hosts`.

### Step 5: Explore the Example Tasks

Two example tasks are included:
- `tasks/no-network/` -- must be solved without internet access
- `tasks/public-network/` -- requires network access for DNS resolution

### Step 6: Run the No-Network Task

Run the isolated task with the oracle agent and verify it completes successfully.

### Step 7: Run the Public-Network Task

Run the network-enabled task and verify it completes successfully.

### Step 8: Security and Reproducibility

Understand why network policies matter: preventing data exfiltration from untrusted agents, and ensuring consistent benchmark results.

## Running the Lesson

```bash
cd tutorial/level-3-advanced/module-10-scaling-cloud/lesson-3-network-policies
uv sync
uv run python main.py
```

## Expected Output

```
########################################################
#          HARBOR TUTORIAL - Level 3, Module 10         #
#          Lesson 3: Network Policies                   #
########################################################

============================================================
Step 1: Checking Prerequisites
============================================================
  [OK] Harbor CLI is installed
  [OK] Docker is running

============================================================
Step 2: The Three Network Modes
============================================================

  Harbor provides three network access modes for task containers:

  1. PUBLIC (default)
     - Full internet access
     ...

  2. NO-NETWORK
     - Complete network isolation
     ...

  3. ALLOWLIST
     - Only specific domains/IPs are reachable
     ...

============================================================
Step 6: Running the No-Network Task
============================================================

  Running: harbor run -p .../no-network -a oracle
  Network mode: no-network
  ...
  [OK] No-network task completed successfully

============================================================
Step 7: Running the Public-Network Task
============================================================

  Running: harbor run -p .../public-network -a oracle
  Network mode: public
  ...
  [OK] Public-network task completed successfully
```

## Key Takeaways

- Harbor supports three network modes: `no-network`, `public` (default), and `allowlist`
- Network mode is configured in `task.toml` under `[environment]`, `[agent]`, and `[verifier]`
- Phase-specific overrides let the agent and verifier use different policies
- Allowlists support hostnames, wildcards, IP addresses, and CIDR ranges
- `extra_allowed_hosts` in job config enables run-time host merging
- Use `no-network` for security (untrusted agents) and reproducibility (consistent benchmarks)

## Next Steps

This concludes Module 10: Scaling & Cloud. Proceed to **Module 11: Analysis & Optimization** to learn about metrics, agent trajectories, and configuration sweeps.
