# Cloud Sandbox Environments

**Duration:** 30-40 minutes

## Overview

Harbor supports 20+ environment providers beyond local Docker, including cloud sandboxes like Daytona, Modal, and E2B. This lesson surveys all available providers, explains when to use cloud vs local environments, and shows how to configure job files for different providers. This is an informational lesson -- no cloud accounts are required.

## Prerequisites

- Completed Level 1 and Level 2 of the Harbor Tutorial
- Harbor CLI installed (`uv tool install harbor`)
- Basic understanding of Harbor job configuration (Module 3, Lesson 2)

## Concepts

### Why Cloud Environments?

When you run evaluations locally with Docker, each trial consumes CPU and memory on your machine. This makes local evaluation CPU-bound -- you can only run a handful of trials concurrently before your machine runs out of resources.

Cloud sandboxes change the equation. Each trial runs in its own remote sandbox, and most of the time is spent waiting for the LLM API to respond. This makes trials I/O-bound rather than CPU-bound, allowing you to run 32, 64, or even 128+ trials concurrently.

### Environment Types

Harbor defines all providers in the `EnvironmentType` enum. The main categories are:

- **Local**: docker, apple-container, singularity -- run on your machine
- **Cloud**: daytona, modal, e2b, ec2, gke, runloop, langsmith, and many more
- **Specialized**: use-computer, cua-cloud -- for computer-use agent evaluation

### Provider Selection

Use the `-e` flag on the CLI or the `environment.type` field in job config to select a provider.

## Step-by-Step

### Step 1: Check Prerequisites

The lesson verifies that Harbor CLI is installed.

### Step 2: Survey Environment Types

See all 20+ providers, grouped by category (Local, Cloud, Specialized, HPC).

### Step 3: Cloud vs Local Decision Guide

Learn the trade-offs:
- **Local Docker**: zero setup, good for development, limited parallelism
- **Cloud sandboxes**: requires account setup, enables massive parallelism, pay-per-use

### Step 4: Job Configurations

The lesson generates example job config files for Docker, Daytona, and Modal in the `configs/` directory.

### Step 5: Provider-Specific Options

Learn about `environment.kwargs` for passing provider-specific configuration (regions, instance types, etc.) and resource overrides (`override_cpus`, `override_memory_mb`).

### Step 6: CLI Syntax

Review the `-e` flag for selecting providers from the command line.

### Step 7: Cost Considerations

Understand the cost model for each provider and tips for optimizing evaluation spend.

## Running the Lesson

```bash
cd tutorial/level-3-advanced/module-9-scaling-cloud/cloud-environments
uv sync
uv run python main.py
```

## Expected Output

```
########################################################
#          HARBOR TUTORIAL - Level 3, Module 9          #
#          Lesson 1: Cloud Sandbox Environments         #
########################################################

============================================================
Step 1: Checking Prerequisites
============================================================
  Harbor version: harbor x.x.x
  [OK] Harbor CLI is installed

============================================================
Step 2: Supported Environment Types
============================================================

Harbor supports 23 environment providers:

  [Local] (3 providers)
    - docker               Local Docker containers
    - apple-container       Apple containerization (macOS)
    - singularity           Singularity/Apptainer containers

  [Cloud] (17 providers)
    - daytona              Daytona cloud development environments
    - e2b                  E2B cloud sandboxes
    - modal                Modal serverless containers
    ...

============================================================
Step 4: Job Configurations for Cloud Providers
============================================================

  Generated: configs/docker-job.yaml
  Provider:  docker
  Parallel:  4 concurrent trials

  Generated: configs/daytona-job.yaml
  Provider:  daytona
  Parallel:  32 concurrent trials

  Generated: configs/modal-job.yaml
  Provider:  modal
  Parallel:  16 concurrent trials
...
```

## Key Takeaways

- Harbor supports 20+ environment providers beyond local Docker
- Cloud sandboxes turn CPU-bound evaluations into I/O-bound ones, enabling massive parallelism
- Select a provider with `-e <type>` on the CLI or `environment.type` in job config
- Provider-specific options go in `environment.kwargs`
- Always set `delete: true` to clean up cloud resources after trials

## Next Steps

Proceed to the next lesson: **parallel-evaluation** (scaling concurrent trials with the `-n` flag).
