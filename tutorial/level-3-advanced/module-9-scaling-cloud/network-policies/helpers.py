"""
Network Policies — Runner helper and educational content.
"""

import subprocess
from pathlib import Path


def run_task(task_path: Path, label: str, network_mode: str) -> None:
    """Run a single task with the oracle agent and display results."""
    print(f"\n  Running: harbor run -p {task_path} -a oracle")
    print(f"  Network mode: {network_mode}")
    print("  " + "-" * 50)

    result = subprocess.run(
        ["harbor", "run", "-p", str(task_path), "-a", "oracle"],
        capture_output=True,
        text=True,
        cwd=str(task_path.parent.parent),
    )

    if result.stdout:
        for line in result.stdout.strip().splitlines()[-10:]:
            print(f"  {line}")
    if result.returncode != 0 and result.stderr:
        for line in result.stderr.strip().splitlines()[-5:]:
            print(f"  [stderr] {line}")

    print("  " + "-" * 50)
    if result.returncode == 0:
        print(f"  [OK] {label} task completed successfully")
    else:
        print(f"  Task exited with code {result.returncode}")
    print()


def print_network_modes_explanation() -> None:
    """Print the three network modes explanation."""
    print("""
  Harbor provides three network access modes for task containers:

  1. PUBLIC (default)
     - Full internet access; the container can reach any host
     - Use when the agent needs to download packages or access APIs

     [environment]
     network_mode = "public"

  2. NO-NETWORK
     - Complete network isolation; no outbound connections
     - Use for tasks that must be solved offline (ensures reproducibility)

     [environment]
     network_mode = "no-network"

  3. ALLOWLIST
     - Only specific domains/IPs are reachable; everything else blocked
     - Use when the agent needs limited access (e.g., only PyPI)

     [environment]
     network_mode = "allowlist"
     allowed_hosts = ["pypi.org", "*.pythonhosted.org"]
""")


def print_task_toml_config() -> None:
    """Print task.toml configuration explanation."""
    print("""
  Network policy is set at two levels in task.toml:

  ENVIRONMENT LEVEL (baseline):
    [environment]
    network_mode = "no-network"

  AGENT LEVEL (override during agent.run()):
    [agent]
    network_mode = "public"

  VERIFIER LEVEL (override during verification):
    [verifier]
    network_mode = "no-network"

  Resolution: phase-specific setting wins over environment baseline.
""")


def print_allowlist_explanation() -> None:
    """Print allowlist configuration explanation."""
    print("""
  In task.toml:
    [environment]
    network_mode = "allowlist"
    allowed_hosts = ["pypi.org", "*.pythonhosted.org"]

  Supported entry types:
    - Exact hostname:      "example.com"
    - Wildcard hostname:   "*.example.com"  (leading wildcard only)
    - IPv4/IPv6 address:   "192.0.2.1" / "2001:db8::1"
    - CIDR range:          "192.0.2.0/24" / "2001:db8::/32"

  Run-time host merging (in job config):
    environment:
      extra_allowed_hosts: ["api.openai.com", "api.anthropic.com"]
""")


def print_security_implications() -> None:
    """Print security and reproducibility explanation."""
    print("""
  1. SECURITY -- Preventing Data Exfiltration
     When evaluating untrusted agents, network isolation prevents:
       - Sending sensitive data to external servers
       - Downloading malicious payloads
       - Making unauthorized API calls

  2. REPRODUCIBILITY -- Consistent Evaluations
     Network access introduces non-determinism (package versions change,
     APIs vary, services go down). Use no-network for benchmarks needing
     consistent results.

  BEST PRACTICES:
     - Default to no-network unless the task requires internet
     - Use allowlist for specific APIs (e.g., LLM provider endpoints)
     - Set verifier to no-network (tests should not need internet)
     - Keep allowlists as small as possible
""")
