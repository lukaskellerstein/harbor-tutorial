# Using Registered Datasets

**Duration:** 20-30 minutes

## Overview

Registered datasets live in the Harbor registry and can be referenced by name instead of by file path. This lesson explores the registry, explains the naming convention, and demonstrates the CLI commands for browsing, downloading, and running registered datasets.

## Prerequisites

- Completed `local-dataset` lesson
- Harbor CLI installed (`uv tool install harbor`)
- Docker installed and running (for running evaluations)

## Concepts

### The Harbor Registry

The Harbor registry is a central repository where authors publish datasets and tasks. It works similarly to PyPI or npm -- you reference datasets by name, and Harbor handles downloading and caching.

### Naming Convention

Registered datasets follow the `org/name@version` convention:

| Format | Meaning |
|--------|---------|
| `org/dataset-name` | Latest version |
| `org/dataset-name@v1.0` | Specific version |
| `org/dataset-name@head` | Latest development version |

### Local vs Registered

| Flag | Source | Example |
|------|--------|---------|
| `-p` / `--path` | Local filesystem directory | `harbor run -p ./my-tasks -a oracle` |
| `-d` / `--dataset` | Registry (downloaded + cached) | `harbor run -d "harbor/hello-world" -a oracle` |

When you use `-d`, Harbor resolves the name in the registry, downloads the task files (if not already cached), and runs the evaluation against the cached copy.

## Step-by-Step

### Step 1: Browse the Registry

Use `harbor dataset list` to see available datasets:

```bash
# Default: prints a link to the registry website
harbor dataset list

# Legacy table format with dataset details
harbor dataset list --legacy
```

### Step 2: Understand the -d Flag

The `-d` flag references a registered dataset. Harbor downloads and caches it automatically:

```bash
harbor run -d "harbor/hello-world" -a oracle
```

### Step 3: Download for Inspection

Use `harbor dataset download` to fetch a dataset's task files locally:

```bash
# Export to current directory
harbor dataset download my-dataset

# Export a specific version
harbor dataset download my-dataset@v1.0

# Cache mode (content-addressable)
harbor dataset download my-dataset --cache
```

### Step 4: Use in job.yaml

Both local and registered datasets can be referenced in job configuration:

```yaml
datasets:
  - name: "harbor/hello-world"    # registered
  - path: ./my-custom-tasks       # local
```

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-6-datasets-benchmarks/registered-datasets
uv sync
uv run python main.py
```

## Expected Output

```
Step 1: Checking Prerequisites
  Docker:  [OK]
  Harbor:  [OK]

Step 2: The Harbor Dataset Registry
  Dataset naming convention:
    org/dataset-name          Latest version
    org/dataset-name@v1.0     Specific version
    org/dataset-name@head     Latest development version

Step 3: Listing Registered Datasets
  Running: harbor dataset list
  View registered datasets at https://...

  Running: harbor dataset list --legacy
  (Table of available datasets with names, versions, task counts)

Step 4: Local (-p) vs Registered (-d) Datasets
  -p / --path     Point to a local dataset directory
  -d / --dataset  Reference a registered dataset by name

Step 5: Downloading Datasets
  harbor dataset download my-dataset
  harbor dataset download my-dataset@v1.0 -o ./benchmarks/

Step 6: Running Registered Datasets
  harbor run -d "harbor/hello-world" -a oracle
  ...

Step 7: Registered Datasets in job.yaml
  datasets:
    - name: "harbor/hello-world"
  ...
```

## Key Takeaways

- The Harbor registry hosts published datasets referenced by `org/name@version`.
- `harbor dataset list` browses available datasets (use `--legacy` for a table).
- `-d` references registered datasets; `-p` references local directories.
- Registered datasets are automatically downloaded and cached under `~/.cache/harbor/tasks/`.
- `harbor dataset download` exports task files for local inspection or modification.
- Both local and registered datasets can be mixed in a single `job.yaml`.

## Next Steps

Continue to `task-metadata` for a deep dive into every field in `task.toml` -- timeouts, environment configuration, metadata, multi-step tasks, and artifacts.
