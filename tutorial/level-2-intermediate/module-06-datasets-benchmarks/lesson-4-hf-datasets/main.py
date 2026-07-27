"""
Lesson 4: Running Datasets Straight from Hugging Face

The --repo flag lets Harbor run a dataset directly out of a git repository,
with nothing published to the Harbor registry first. Hugging Face dataset
repos are git repos, so they work as-is.

This lesson discovers a real public Harbor dataset on Hugging Face
(harborframework/harbor-datasets), runs one bird-bench task from it with the
oracle agent, and explains the Git LFS requirement that silently breaks
Hugging Face runs when it is missing.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from hf_repo import (
    HF_REPO,
    TASK_NAME,
    explain_lfs,
    explain_repo_flag,
    explain_resolution,
    show_job_config_example,
)
from results import display_results

LESSON_DIR = Path(__file__).parent


def check_prerequisites() -> bool:
    """Verify Docker, Harbor, git, and Git LFS are available."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)

    docker_ok = shutil.which("docker") is not None
    if docker_ok:
        docker_ok = (
            subprocess.run(["docker", "info"], capture_output=True).returncode == 0
        )

    harbor_ok = shutil.which("harbor") is not None
    git_ok = shutil.which("git") is not None

    # git-lfs needs to be both installed AND initialized. 'git lfs install'
    # registers the smudge filter that turns LFS pointers into real files
    # during checkout -- without it, the binary alone changes nothing.
    lfs_installed = shutil.which("git-lfs") is not None
    lfs_initialized = False
    if lfs_installed:
        smudge = subprocess.run(
            ["git", "config", "--get", "filter.lfs.smudge"],
            capture_output=True,
            text=True,
        )
        lfs_initialized = bool(smudge.stdout.strip())

    print(f"  Docker:  {'[OK]' if docker_ok else '[FAIL] Docker daemon not running'}")
    print(
        f"  Harbor:  {'[OK]' if harbor_ok else '[FAIL] Install with: uv tool install harbor'}"
    )
    print(f"  Git:     {'[OK]' if git_ok else '[FAIL] Install git'}")

    if lfs_initialized:
        print("  Git LFS: [OK]")
    elif lfs_installed:
        print("  Git LFS: [FAIL] installed but not initialized -- run: git lfs install")
    else:
        print("  Git LFS: [FAIL] not installed -- run: brew install git-lfs")
    print()

    if not lfs_initialized:
        print("Git LFS is required for this lesson. Hugging Face stores large")
        print("files (here, an 11 MB SQLite database) with LFS. Without it the")
        print("run still 'succeeds' but scores 0.0 -- see Step 7 for why.")
        print()
        print("  brew install git-lfs      # or: apt-get install git-lfs")
        print("  git lfs install")
        print()

    if not (docker_ok and harbor_ok and git_ok and lfs_initialized):
        print("Prerequisites not met. Please fix the issues above.")
        return False
    return True


def list_datasets_from_hf() -> None:
    """Discover what datasets a Hugging Face repo exposes."""
    print("=" * 60)
    print("Step 3: Discovering the Dataset")
    print("=" * 60)
    print()
    print("'harbor dataset list' takes --repo too, so you can inspect a")
    print("repository before committing to a full evaluation run.")
    print()
    print(f"Running: harbor dataset list --repo {HF_REPO}")
    print()
    print("(This resolves the ref and reads the git tree -- no task files are")
    print("downloaded yet, so it stays fast even for large benchmarks.)")
    print("-" * 60)

    result = subprocess.run(
        ["harbor", "dataset", "list", "--repo", HF_REPO],
        capture_output=True,
        text=True,
        cwd=str(LESSON_DIR),
    )

    print(result.stdout or "")
    if result.stderr.strip():
        print(result.stderr)

    print("-" * 60)
    print()


def run_hf_dataset() -> None:
    """Run a single task from the Hugging Face dataset with the oracle agent."""
    print("=" * 60)
    print("Step 5: Running a Task from Hugging Face")
    print("=" * 60)
    print()
    print("bird-bench holds 150 text-to-SQL tasks, so we filter down to one")
    print("with -i. Each task ships a solution/ directory, which means the")
    print("oracle agent can score it -- no model, no API key, no cost.")
    print()
    print(f"Running: harbor run --repo {HF_REPO} \\")
    print(f"           -i {TASK_NAME} -a oracle")
    print()
    print("  --repo    resolve the dataset from this git repository")
    print("  -i        include only tasks matching this name (globs allowed)")
    print("  -a oracle run the reference solution instead of a real agent")
    print()
    print("First run downloads the task files (~11 MB) and builds the image;")
    print("later runs reuse the cache under ~/.cache/harbor/tasks/.")
    print("-" * 60)

    result = subprocess.run(
        ["harbor", "run", "--repo", HF_REPO, "-i", TASK_NAME, "-a", "oracle"],
        capture_output=True,
        text=True,
        cwd=str(LESSON_DIR),
    )

    print(result.stdout or "")
    if result.stderr.strip():
        print(result.stderr)

    print("-" * 60)
    if result.returncode == 0:
        print("Evaluation completed.")
    else:
        print(f"Evaluation failed with return code {result.returncode}")
    print()


def show_summary() -> None:
    """Display lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    print("In this lesson you learned:")
    print("  1. --repo runs a dataset straight from a git repository, with no")
    print("     registry publishing step -- Hugging Face repos work as-is")
    print("  2. A browser URL with /tree/<ref>/<subdir> can be pasted directly")
    print("  3. Refs resolve to an immutable commit SHA, so runs reproduce")
    print("  4. registry.json gives named datasets; without it, every")
    print("     subdirectory containing a task.toml becomes a task")
    print("  5. --repo composes with -i, -x, -l, and --registry-path")
    print("  6. Git LFS must be installed AND initialized, or LFS files arrive")
    print("     as pointer stubs and every task silently scores 0.0")
    print("  7. The 'repo' key brings all of this into job.yaml")
    print()
    print("Next module: module-07-environments-config")
    print("  (Docker environments, capabilities, and model routing)")


def main() -> None:
    """Run the hf-datasets lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 2, Module 6          #")
    print("#      Lesson 4: Datasets Straight from Hugging Face    #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_repo_flag()
    list_datasets_from_hf()
    explain_resolution()
    run_hf_dataset()
    display_results(LESSON_DIR)
    explain_lfs()
    show_job_config_example()
    show_summary()


if __name__ == "__main__":
    main()
