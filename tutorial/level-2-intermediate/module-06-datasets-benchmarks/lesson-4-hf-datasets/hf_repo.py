"""
Helper module: repository constants and explanatory output for the
hf-datasets lesson.
"""

# A real, public Harbor dataset repository hosted on Hugging Face.
# The /tree/main/<subdir> suffix is the same URL you get by browsing to the
# directory in the Hugging Face web UI and copying the address bar.
HF_REPO = (
    "https://huggingface.co/datasets/harborframework/harbor-datasets"
    "/tree/main/datasets/bird-bench"
)

# One task inside that dataset. bird-bench tasks ship a solution/ directory,
# so the oracle agent can score them 1.0 without any model or API key.
TASK_NAME = "california_schools__13"


def explain_repo_flag() -> None:
    """Explain the --repo flag and the reference formats it accepts."""
    print("=" * 60)
    print("Step 2: The --repo Flag")
    print("=" * 60)
    print()
    print("Lesson 2 used -d to pull datasets from the Harbor registry. But a")
    print("dataset does not have to be published to the registry at all --")
    print("--repo runs one straight out of a git repository. Hugging Face")
    print("dataset repos are git repositories, so they work as-is.")
    print()
    print("Accepted reference formats:")
    print()
    print("  # GitHub shorthand (org/name)")
    print("  --repo org/repo-name")
    print()
    print("  # Pinned to a tag, branch, or commit SHA")
    print("  --repo org/repo-name@v1.0")
    print("  --repo org/repo-name@main")
    print("  --repo org/repo-name@abc1234")
    print()
    print("  # Full URLs -- GitHub, GitLab, Hugging Face")
    print("  --repo https://github.com/org/repo-name")
    print("  --repo https://gitlab.com/org/repo-name")
    print("  --repo https://huggingface.co/datasets/org/repo-name")
    print()
    print("  # A subdirectory of a repo (copy this straight from the browser)")
    print("  --repo https://huggingface.co/datasets/org/repo/tree/main/datasets/x")
    print()
    print("The repo we will use in this lesson:")
    print(f"  {HF_REPO}")
    print()
    print("Note: --repo is git-only. It cannot be combined with --registry-url")
    print("or -t/--task, and a local path is rejected (use -p for those).")
    print()


def explain_resolution() -> None:
    """Explain how Harbor turns a --repo reference into runnable tasks."""
    print("=" * 60)
    print("Step 4: How Harbor Resolves a Repo")
    print("=" * 60)
    print()
    print("When you pass --repo, Harbor does the following:")
    print()
    print("  1. Parses the reference into host / org / name / ref / subdir")
    print("  2. Resolves the ref to an immutable commit SHA via")
    print("     'git ls-remote' -- so a run is always reproducible")
    print("  3. Shallow, sparse-clones only what it needs (no full checkout)")
    print("  4. Looks for registry.json to discover named datasets")
    print("  5. Falls back to scanning the subdirectory for task.toml files")
    print("  6. Caches the task files under ~/.cache/harbor/tasks/")
    print()
    print("Two repository layouts are supported:")
    print()
    print("  A) With registry.json -- named, versioned datasets:")
    print("       my-benchmarks/")
    print("       |-- registry.json      <-- declares datasets + their tasks")
    print("       |-- task-a/")
    print("       +-- task-b/")
    print("     Select one with: --repo org/my-benchmarks -d lite@1.2")
    print()
    print("  B) Without registry.json -- an implicit dataset:")
    print("       datasets/bird-bench/")
    print("       |-- california_schools__13/task.toml")
    print("       +-- california_schools__23/task.toml")
    print("     Every direct subdirectory holding a task.toml becomes a task.")
    print("     This is the layout of the Hugging Face repo we are using, so")
    print("     no -d flag is needed.")
    print()
    print("Because the ref resolves to a SHA, the dataset name Harbor reports")
    print("embeds that SHA -- that is what makes the run reproducible:")
    print("  huggingface.co/harborframework/harbor-datasets/tree/<sha>/...")
    print()


def explain_lfs() -> None:
    """Explain the Git LFS requirement, the main gotcha with HF repos."""
    print("=" * 60)
    print("Step 7: The Git LFS Gotcha")
    print("=" * 60)
    print()
    print("Hugging Face stores large files with Git LFS. In this dataset the")
    print("11 MB db.sqlite in each task's environment/ directory is LFS-backed.")
    print()
    print("If git-lfs is missing, the clone still succeeds -- but every LFS")
    print("file arrives as a ~130 byte text pointer instead of real content:")
    print()
    print("  version https://git-lfs.github.com/spec/v1")
    print("  oid sha256:986817d793479801ed55133e55aa27e...")
    print("  size 11116544")
    print()
    print("Nothing errors out. The image builds, the agent runs, and the test")
    print("fails with a confusing message ('file is not a database'), giving")
    print("you a silent reward of 0.0 on every task.")
    print()
    print("Both of these steps are required -- installing the binary is not")
    print("enough on its own, since 'git lfs install' is what registers the")
    print("smudge filter that materializes files during checkout:")
    print()
    print("  brew install git-lfs      # or: apt-get install git-lfs")
    print("  git lfs install")
    print()
    print("If a benchmark scores 0.0 across the board right after you switch")
    print("to a Hugging Face repo, check this first.")
    print()


def show_job_config_example() -> None:
    """Show the job.yaml equivalent of the --repo flag."""
    print("=" * 60)
    print("Step 8: Repos in job.yaml")
    print("=" * 60)
    print()
    print("Every --repo flag has a job.yaml equivalent, via the 'repo' key")
    print("on a dataset entry:")
    print()
    print("  datasets:")
    print("    # Hugging Face, implicit dataset in a subdirectory")
    print("    - repo: https://huggingface.co/datasets/harborframework/harbor-datasets")
    print("      path: datasets/bird-bench")
    print("      task_names:")
    print("        - california_schools__13")
    print()
    print("    # GitHub, pinned to a tag, selecting a named dataset")
    print("    - repo: org/my-benchmarks@v1.0")
    print("      name: lite")
    print("      n_tasks: 10")
    print()
    print("    # Still works alongside registry and local datasets")
    print("    - name: harbor/hello-world")
    print("    - path: ./my-custom-tasks")
    print()
    print("Useful flags that combine with --repo on the command line:")
    print()
    print("  -i / --include-task-name   include tasks (glob patterns allowed)")
    print("  -x / --exclude-task-name   exclude tasks (glob patterns allowed)")
    print("  -l / --n-tasks             cap the number of tasks")
    print("  --registry-path            repo-relative path to a registry.json")
    print()
