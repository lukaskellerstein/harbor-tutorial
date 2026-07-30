# Hub -- Sharing & Leaderboards

**Duration:** 30-40 minutes

## Overview

Harbor Hub is the community platform for sharing datasets, uploading evaluation results, and viewing leaderboards that rank agents and models. It connects the evaluation ecosystem: dataset authors publish benchmarks, agent developers upload results, and everyone benefits from standardized comparisons. This lesson walks through the Hub CLI commands and workflows.

## Prerequisites

- Completed Level 1 and Level 2 modules
- Harbor installed (`uv tool install harbor`)
- A GitHub account (for Hub authentication)
- Internet access (Hub is a cloud service)

## Concepts

### What is Harbor Hub?

Harbor Hub serves three purposes:

1. **Sharing** -- Publish your datasets (collections of tasks) for others to use. Anyone can download and evaluate against your benchmark.
2. **Competing** -- Upload evaluation results and see how your agent ranks against others on the same benchmark.
3. **Browsing** -- Discover community-contributed benchmarks, download datasets, and inspect shared job results.

The Hub website is at [hub.harborframework.com](https://hub.harborframework.com).

### Authentication

Harbor uses GitHub OAuth (PKCE flow) for authentication. On login, it mints a personal API key stored at `~/.harbor/credentials.json`. The key format is `sk-harbor-<key_id>_<secret>`.

You can also bypass the login flow by setting the `HARBOR_API_KEY` environment variable, which takes precedence over the credentials file.

### Publishing vs Uploading

These are two distinct operations:

- **`harbor publish`** -- Uploads task and dataset *definitions* (instruction.md, task.toml, Dockerfile, tests, etc.) to the Hub registry. This makes your benchmark available for others to run.
- **`harbor upload`** -- Uploads job *results* (trial outcomes, rewards, agent trajectories) to the Hub. This populates leaderboards and enables cross-agent comparisons.

### Leaderboards

Leaderboards rank agents and models on published datasets. They are configurable with custom metrics, metadata schemas, and ranking criteria. The Hub provides full CRUD operations via edge functions, and the CLI exposes commands for creating, viewing, and managing leaderboard rows.

### Hub CLI Structure

The Hub commands live under `harbor hub`:

```text
harbor hub
  job
    list / show / tasks / trials / shares / compare / download / copy / delete
  trial
    show / download / copy
  leaderboard
    init / create / show / list / export / update
    row
      show / list / export / create / update / delete
      trial
        list / set / add / remove
```

## Step-by-Step

### Step 1: Understand Harbor Hub

Run the lesson to get an overview of what Harbor Hub provides and how it fits into the evaluation workflow.

### Step 2: Authentication

Learn the authentication flow:

```bash
harbor auth login              # GitHub OAuth (opens browser)
harbor auth login --no-browser # For headless environments
harbor auth status             # Check auth mode
harbor auth logout             # Revoke key and delete credentials
```

### Step 3: Publishing Datasets

Publishing packages your tasks into tar.gz archives, uploads them to storage, and registers them in the Hub database:

```bash
# Validate first
harbor check -p path/to/dataset

# Publish (private by default)
harbor publish path/to/dataset

# Publish as public
harbor publish path/to/dataset --public
```

### Step 4: Uploading Results

After running an evaluation, upload the results:

```bash
# Upload a completed job
harbor upload jobs/<job-id>

# Upload with sharing controls
harbor upload jobs/<job-id> --public --share-org my-team

# Auto-upload during a run
harbor run -d "org/dataset" -a claude-code --upload
```

### Step 5: Browsing and Downloading

Discover and download community datasets:

```bash
harbor dataset list                        # List registered datasets
harbor download org/dataset-name           # Download to current directory
harbor download org/dataset-name -o ./dir  # Download to specific directory
harbor download org/dataset-name --cache   # Content-addressable cache
```

Browse job results:

```bash
harbor hub job list                  # List your jobs
harbor hub job show <job-id>          # Job details
harbor hub job trials <job-id>        # List trials
harbor hub job download <job-id>      # Download results
```

### Step 6: Leaderboards

Create and manage leaderboards:

```bash
harbor hub leaderboard list              # List leaderboards
harbor hub leaderboard show <ref>         # View a leaderboard
harbor hub leaderboard init              # Initialize from config
harbor hub leaderboard row list <ref>     # List rows
harbor hub leaderboard export <ref>       # Export as JSON/CSV
```

### Step 7: The Complete Workflow

The lesson walks through the full cycle: create tasks, validate with oracle, publish, share, evaluate, upload results, and compete on leaderboards.

## Running the Lesson

```bash
cd tutorial/level-3-advanced/module-12-advanced-workflows/lesson-3-harbor-hub
uv sync
uv run python main.py
```

## Expected Output

```text
============================================================
  Harbor Hub -- Sharing & Leaderboards
============================================================

This lesson explores Harbor Hub, the community platform for
sharing datasets, uploading evaluation results, and viewing
leaderboards that rank agents and models.

NOTE: Hub features require authentication and network access.
...

============================================================
  Step 2: Authentication
============================================================

Before using Hub features, you need to authenticate:

  # Log in via GitHub OAuth (opens browser)
  harbor auth login
  ...

============================================================
  Step 7: The Complete Hub Workflow
============================================================

The typical Hub workflow has five stages:

  +---------+    +--------+    +---------+
  | CREATE  | -> |  TEST  | -> | PUBLISH |
  +---------+    +--------+    +---------+
  ...

============================================================
  Summary
============================================================

Harbor Hub connects the evaluation community:

  - harbor auth login           Log in to your Hub account
  - harbor publish <path>       Share a dataset with the community
  - harbor upload <job-path>    Upload results to the leaderboard
  - harbor dataset list         Browse available datasets
  - harbor download <name>      Download a community dataset
...
```

## Key Takeaways

- Harbor Hub is the community platform for sharing datasets and comparing agent performance.
- Authentication uses GitHub OAuth; credentials are stored at `~/.harbor/credentials.json`.
- `harbor publish` uploads dataset definitions; `harbor upload` uploads job results. They are separate operations.
- Leaderboards provide configurable ranking with custom metrics, accessible via `harbor hub leaderboard` commands.
- The upload process is idempotent and resumable -- safe to re-run after crashes.
- Hub supports visibility controls (public/private) and sharing with specific organizations or users.

## Next Steps

Congratulations! You have completed Module 12 (Advanced Workflows) and the entire Level 3 (Advanced) curriculum. You now have a comprehensive understanding of Harbor's capabilities, from basic task creation through advanced multi-container environments, exec pipelines, and community sharing.
