"""
Lesson 3: Network Policies

Learn how to control network access in Harbor evaluations using
the three network modes: no-network, public, and allowlist.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from helpers import (
    print_allowlist_explanation,
    print_network_modes_explanation,
    print_security_implications,
    print_task_toml_config,
    run_task,
)


def check_prerequisites() -> bool:
    """Verify Harbor CLI and Docker are available."""
    print("=" * 60)
    print("Step 1: Checking Prerequisites")
    print("=" * 60)

    if not shutil.which("harbor"):
        print("  [FAIL] Harbor CLI not found. Install with: uv tool install harbor")
        return False
    print("  [OK] Harbor CLI is installed")

    result = subprocess.run(["docker", "info"], capture_output=True, text=True)
    if result.returncode != 0:
        print("  [FAIL] Docker daemon is not running. Start Docker Desktop.")
        return False
    print("  [OK] Docker is running")
    print()
    return True


def explain_network_modes() -> None:
    """Explain the three network modes in Harbor."""
    print("=" * 60)
    print("Step 2: The Three Network Modes")
    print("=" * 60)
    print_network_modes_explanation()


def show_task_toml_config() -> None:
    """Show how to configure network modes in task.toml."""
    print("=" * 60)
    print("Step 3: Configuring Network Modes in task.toml")
    print("=" * 60)
    print_task_toml_config()


def explain_allowlist() -> None:
    """Explain how to set up an allowlist."""
    print("=" * 60)
    print("Step 4: Setting Up an Allowlist")
    print("=" * 60)
    print_allowlist_explanation()


def show_task_structures() -> None:
    """Display the example tasks demonstrating different network modes."""
    print("=" * 60)
    print("Step 5: Example Tasks with Network Policies")
    print("=" * 60)

    tasks_dir = Path(__file__).parent / "tasks"

    print("\n  tasks/no-network/")
    no_net = tasks_dir / "no-network" / "instruction.md"
    if no_net.exists():
        print(f"    Instruction: {no_net.read_text().strip()[:70]}")
        print("    Network mode: no-network (complete isolation)")

    print("\n  tasks/public-network/")
    pub = tasks_dir / "public-network" / "instruction.md"
    if pub.exists():
        print(f"    Instruction: {pub.read_text().strip()[:70]}")
        print("    Network mode: public (full internet access)")
    print()


def run_no_network_task() -> None:
    """Run the no-network task and show results."""
    print("=" * 60)
    print("Step 6: Running the No-Network Task")
    print("=" * 60)
    task_path = Path(__file__).parent / "tasks" / "no-network"
    run_task(task_path, "No-network", "no-network")


def run_public_network_task() -> None:
    """Run the public-network task and show results."""
    print("=" * 60)
    print("Step 7: Running the Public-Network Task")
    print("=" * 60)
    task_path = Path(__file__).parent / "tasks" / "public-network"
    run_task(task_path, "Public-network", "public")


def explain_security_implications() -> None:
    """Explain why network policies matter for evaluation security."""
    print("=" * 60)
    print("Step 8: Security and Reproducibility Implications")
    print("=" * 60)
    print_security_implications()


def show_summary() -> None:
    """Display lesson summary."""
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print("""
  Key Takeaways:
  1. Three modes: no-network, public (default), and allowlist
  2. Configured in task.toml under [environment], [agent], [verifier]
  3. Phase-specific overrides: agent/verifier can differ from baseline
  4. Allowlists support hostnames, wildcards, IPs, and CIDR ranges
  5. extra_allowed_hosts in job config merges at run time
  6. Use no-network for security and reproducibility

  This concludes Module 9: Scaling & Cloud.
  Next module: Module 10 -- Analysis & Optimization
""")


def main() -> None:
    """Run the network-policies lesson."""
    print()
    print("########################################################")
    print("#          HARBOR TUTORIAL - Level 3, Module 9          #")
    print("#          Lesson 3: Network Policies                   #")
    print("########################################################")
    print()

    if not check_prerequisites():
        sys.exit(1)

    explain_network_modes()
    show_task_toml_config()
    explain_allowlist()
    show_task_structures()
    run_no_network_task()
    run_public_network_task()
    explain_security_implications()
    show_summary()


if __name__ == "__main__":
    main()
