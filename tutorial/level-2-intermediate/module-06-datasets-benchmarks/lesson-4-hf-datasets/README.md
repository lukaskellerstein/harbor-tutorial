# Running Datasets Straight from Hugging Face

**Duration:** 20-30 minutes

## Overview

The previous lesson used `-d` to pull datasets from the Harbor registry. But a dataset does not have to be published to the registry at all. The `--repo` flag runs one directly out of a git repository -- GitHub, GitLab, or Hugging Face.

Hugging Face dataset repos are git repositories, so they work as-is. This lesson discovers a real public Harbor dataset on Hugging Face ([harborframework/harbor-datasets](https://huggingface.co/datasets/harborframework/harbor-datasets)), runs one bird-bench text-to-SQL task from it with the `oracle` agent, and explains the Git LFS requirement that silently breaks Hugging Face runs when it is missing.

## Prerequisites

- Completed the `lesson-2-registered-datasets` lesson
- Harbor CLI (`harbor>=0.20`, provided by `uv sync`)
- Docker installed and running
- Git
- **Git LFS -- installed *and* initialized:**

  ```bash
  brew install git-lfs      # or: apt-get install git-lfs
  git lfs install
  ```

No model or API key is needed. The `oracle` agent runs each task's reference solution, so the lesson costs nothing to run.

## Concepts

### The `--repo` Flag

`--repo` accepts several reference formats:

| Format | Example |
|--------|---------|
| GitHub shorthand | `--repo org/repo-name` |
| Pinned to tag / branch / SHA | `--repo org/repo-name@v1.0` |
| Full URL | `--repo https://github.com/org/repo-name` |
| Hugging Face | `--repo https://huggingface.co/datasets/org/repo-name` |
| GitLab | `--repo https://gitlab.com/org/repo-name` |
| Subdirectory | `--repo https://huggingface.co/datasets/org/repo/tree/main/datasets/x` |

The subdirectory form is the URL you get by browsing to the directory on Hugging Face and copying the address bar -- no rewriting required.

`--repo` is git-only. It cannot be combined with `--registry-url` or `-t`/`--task`, and a local path is rejected (use `-p` for those).

### How Resolution Works

1. Parse the reference into host / org / name / ref / subdir
2. Resolve the ref to an immutable commit SHA via `git ls-remote`
3. Shallow, sparse-clone only what is needed -- no full checkout
4. Look for `registry.json` to discover named datasets
5. Fall back to scanning the subdirectory for `task.toml` files
6. Cache the task files under `~/.cache/harbor/tasks/`

Because the ref resolves to a SHA before anything downloads, the run is reproducible. Pinned refs are cached and reused; branch refs re-resolve on every run.

### Two Repository Layouts

**A) With `registry.json`** -- named, versioned datasets:

```text
my-benchmarks/
├── registry.json      <-- declares datasets and their tasks
├── task-a/
└── task-b/
```

Select one with `--repo org/my-benchmarks -d lite@1.2`. When a repo declares only one dataset, `-d` may be omitted.

**B) Without `registry.json`** -- an implicit dataset:

```text
datasets/bird-bench/
├── california_schools__13/task.toml
└── california_schools__23/task.toml
```

Every direct subdirectory containing a `task.toml` becomes a task. This is the layout of the Hugging Face repo used here, so no `-d` flag is needed.

### The Git LFS Gotcha

Hugging Face stores large files with Git LFS. In this dataset, each bird-bench task's `environment/db.sqlite` is an 11 MB LFS-backed SQLite database.

Without Git LFS, the clone still succeeds -- but every LFS file arrives as a ~130 byte text pointer instead of real content:

```text
version https://git-lfs.github.com/spec/v1
oid sha256:986817d793479801ed55133e55aa27e...
size 11116544
```

Nothing errors out. The image builds, the agent runs, and the test fails with a confusing message (`file is not a database`), giving you a silent reward of `0.0` on every task.

Both steps are required. Installing the binary is not enough on its own -- `git lfs install` is what registers the smudge filter that materializes LFS files during checkout:

```bash
brew install git-lfs
git lfs install
```

**If a benchmark scores 0.0 across the board right after you switch to a Hugging Face repo, check this first.**

## Step-by-Step

### Step 1: Discover What the Repo Offers

`harbor dataset list` takes `--repo` too, so you can inspect a repository before committing to a full run. It resolves the ref and reads the git tree without downloading task files, so it stays fast even for large benchmarks:

```bash
harbor dataset list --repo https://huggingface.co/datasets/harborframework/harbor-datasets/tree/main/datasets/bird-bench
```

```text
                      Available Datasets
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳┳┳┓
┃ Name                                                     ┃┃┃┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇╇╇┩
│ huggingface.co/harborframework/harbor-datasets/tree/bae… ││││
└──────────────────────────────────────────────────────────┴┴┴┘

Total: 1 dataset(s) with 150 task(s)
```

The commit SHA is already baked into the reported name.

### Step 2: Run One Task

bird-bench holds 150 tasks, so filter down to one with `-i`. Each task ships a `solution/` directory, which means `oracle` can score it:

```bash
harbor run \
  --repo https://huggingface.co/datasets/harborframework/harbor-datasets/tree/main/datasets/bird-bench \
  -i california_schools__13 \
  -a oracle
```

The first run downloads the task files (~11 MB) and builds the image; later runs reuse `~/.cache/harbor/tasks/`.

### Step 3: Confirm Where the Files Came From

The trial's `result.json` records the exact origin:

```json
"task_id": {
  "git_url": "https://huggingface.co/datasets/harborframework/harbor-datasets",
  "git_commit_id": "bae16d3bc8b10aab97018e8327cb4db4806d6033",
  "path": "datasets/bird-bench/california_schools__13"
}
```

Pass that SHA with `@<sha>` to reproduce the run exactly, even after the branch moves on.

### Step 4: Combine with Other Dataset Flags

```bash
# Include several tasks (globs allowed)
harbor run --repo org/benchmarks -d suite -i "task-a" -i "task-b" -a oracle

# Cap the number of tasks
harbor run --repo org/benchmarks -d suite -l 10 -a oracle

# Point at a registry.json somewhere other than the repo root
harbor run --repo org/benchmarks --registry-path benchmarks/registry.json -d suite -a oracle
```

### Step 5: Move It into `job.yaml`

Every `--repo` flag has a `job.yaml` equivalent via the `repo` key on a dataset entry:

```yaml
datasets:
  # Hugging Face, implicit dataset in a subdirectory
  - repo: https://huggingface.co/datasets/harborframework/harbor-datasets
    path: datasets/bird-bench
    task_names:
      - california_schools__13

  # GitHub, pinned to a tag, selecting a named dataset
  - repo: org/my-benchmarks@v1.0
    name: lite
    n_tasks: 10

  # Repos mix freely with registry and local datasets
  - name: harbor/hello-world
  - path: ./my-custom-tasks
```

## Running the Lesson

```bash
cd tutorial/level-2-intermediate/module-06-datasets-benchmarks/lesson-4-hf-datasets
uv sync
uv run python main.py
```

## Expected Output

```text
Step 1: Checking Prerequisites
  Docker:  [OK]
  Harbor:  [OK]
  Git:     [OK]
  Git LFS: [OK]

Step 2: The --repo Flag
  (Reference formats for GitHub, GitLab, and Hugging Face)

Step 3: Discovering the Dataset
  Running: harbor dataset list --repo https://huggingface.co/...
  Total: 1 dataset(s) with 150 task(s)

Step 4: How Harbor Resolves a Repo
  (Ref -> SHA -> sparse clone -> registry.json or task.toml scan -> cache)

Step 5: Running a Task from Hugging Face
  1/1 Mean: 1.000 ...
  ┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┓
  ┃ Trials ┃ Exceptions ┃  Mean ┃
  ┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━┩
  │      1 │          0 │ 1.000 │
  └────────┴────────────┴───────┘

Step 6: Inspecting Results
  git_url:       https://huggingface.co/datasets/harborframework/harbor-datasets
  git_commit_id: bae16d3bc8b10aab97018e8327cb4db4806d6033
  path:          datasets/bird-bench/california_schools__13

  Task                                       Reward
  -------------------------------------------------
  california_schools__13                       1.00
  -------------------------------------------------
  Mean                                         1.00

Step 7: The Git LFS Gotcha
  (Why a missing git-lfs produces a silent 0.0)

Step 8: Repos in job.yaml
  (The 'repo' key)
```

## Key Takeaways

- `--repo` runs a dataset straight from a git repository -- no registry publishing step. Hugging Face repos work as-is.
- A browser URL with `/tree/<ref>/<subdir>` can be pasted directly into `--repo`.
- Refs resolve to an immutable commit SHA via `git ls-remote`, so runs reproduce.
- `registry.json` gives named, versioned datasets; without it, every subdirectory holding a `task.toml` becomes a task.
- `--repo` composes with `-i`, `-x`, `-l`, and `--registry-path`, and is mutually exclusive with `--registry-url` and `-t`.
- Git LFS must be **installed and initialized**, or LFS files arrive as pointer stubs and every task silently scores `0.0`.
- The `repo` key brings all of this into `job.yaml`.

## Reference

- [Harbor docs: Git Repository Datasets](https://www.harborframework.com/docs/datasets/git-repos)
- [harborframework/harbor-datasets on Hugging Face](https://huggingface.co/datasets/harborframework/harbor-datasets)

## Next Steps

Continue to Module 7 (`module-07-environments-config`) for Docker environments, environment capabilities, and model routing.
