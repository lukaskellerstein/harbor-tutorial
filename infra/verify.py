"""Verify that all infrastructure prerequisites are met for the Harbor tutorial."""

import shutil
import subprocess
import sys
import urllib.request


def check(name: str, ok: bool, detail: str = "") -> bool:
    status = "OK" if ok else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"  [{status}]  {name}{suffix}")
    return ok


def check_command(name: str, cmd: list[str], expected: str = "") -> bool:
    path = shutil.which(cmd[0])
    if not path:
        return check(name, False, f"`{cmd[0]}` not found in PATH")
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10, check=False
        )
        version = result.stdout.strip() or result.stderr.strip()
        version_line = version.splitlines()[0] if version else "installed"
        return check(name, True, version_line)
    except (OSError, subprocess.SubprocessError) as e:
        return check(name, False, str(e))


def check_git_lfs() -> bool:
    """Git LFS must be installed AND initialized.

    `git lfs install` registers the smudge filter that materializes LFS
    pointers into real files on checkout. Without it, Hugging Face datasets
    clone as ~130 byte pointer stubs and every task silently scores 0.0.
    """
    if not shutil.which("git-lfs"):
        return check("Git LFS", False, "not installed — run: brew install git-lfs")
    try:
        result = subprocess.run(
            ["git", "config", "--get", "filter.lfs.smudge"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return check("Git LFS", False, str(e))
    if not result.stdout.strip():
        return check("Git LFS", False, "not initialized — run: git lfs install")
    return check("Git LFS", True, "installed and initialized")


def check_url(name: str, url: str) -> bool:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return check(name, resp.status == 200, f"{url} reachable")
    # urllib.error.URLError (and HTTPError under it) subclass OSError, so this
    # single catch covers refused connections, DNS failures and timeouts alike.
    except OSError:
        return check(name, False, f"{url} not reachable")


def main() -> None:
    print("=" * 60)
    print("Harbor Tutorial — Infrastructure Verification")
    print("=" * 60)
    results: list[bool] = []

    # ── Prerequisites ──
    print("\n1. Prerequisites")
    results.append(check_command("Python 3.12+", [sys.executable, "--version"]))
    results.append(check_command("uv", ["uv", "--version"]))
    results.append(check_command("Docker", ["docker", "--version"]))
    results.append(check_command("Harbor CLI", ["harbor", "--version"]))
    results.append(check_command("Git", ["git", "--version"]))
    results.append(check_git_lfs())

    # ── Docker daemon ──
    print("\n2. Docker Daemon")
    try:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, timeout=10,
            check=False,
        )
        results.append(check("Docker daemon running", result.returncode == 0))
    except (OSError, subprocess.SubprocessError):
        results.append(check("Docker daemon running", False, "cannot connect"))

    # Everything above this point must pass for any lesson to work.
    required = list(results)

    # ── Docker Compose services ──
    print("\n3. Docker Compose Services")
    results.append(check_url("Qdrant", "http://localhost:6333/healthz"))
    # /health/liveliness is unauthenticated; /health would 401 without the master key.
    litellm_ok = check_url("LiteLLM gateway", "http://localhost:4000/health/liveliness")
    results.append(litellm_ok)
    # Module 8's judge lessons route every LLM call through this gateway.
    required.append(litellm_ok)

    # ── LMStudio (local model server) ──
    print("\n4. LMStudio (optional — needed for local model lessons)")
    results.append(check_command("LMStudio CLI", ["lms", "--version"]))
    results.append(check_url("LMStudio API", "http://localhost:1234/v1/models"))

    # ── Summary ──
    passed = sum(results)
    total = len(results)
    print("\n" + "=" * 60)
    print(f"Result: {passed}/{total} checks passed")
    if all(results):
        print("All systems go! You're ready to start the tutorial.")
    else:
        print("Some checks failed. See above for details.")
        print("Note: LMStudio and Qdrant checks are optional for most lessons.")
        if not litellm_ok:
            print("      LiteLLM is required for Module 8 (Grading & Rewards):")
            print("      cd infra && docker compose up -d litellm")
    print("=" * 60)

    sys.exit(0 if all(required) else 1)


if __name__ == "__main__":
    main()
