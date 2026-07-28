"""Live demonstrations of RewardKit's two structural guardrails.

Both run in-process on the host -- no container, no LLM. They exist because
each guardrail replaces a class of silent wrong answer with a loud error.
"""

import tempfile
from pathlib import Path


def demo_direct_call_typeerror() -> None:
    """Calling a @criterion function directly raises TypeError."""
    from rewardkit import criterion

    @criterion(description="stub that is never meant to be called directly")
    def stub(workspace: Path, n: int) -> bool:
        return True

    print("  A @criterion-decorated function is a FACTORY, not the check.")
    print("  Calling it directly:")
    print()
    print("    stub(Path('/app'), 3)")
    print()
    try:
        stub(Path("/app"), 3)
        print("    (no error -- unexpected)")
    except TypeError as exc:
        print(f"    TypeError: {exc}")
    print()
    print("  Correct form goes through the module, which registers the check")
    print("  against the current session instead of evaluating it on the spot:")
    print()
    print("    rk.stub(3, weight=2.0)")
    print()


def demo_nested_layout_valueerror() -> None:
    """A non-shared criterion in a root file, with subdirectories present."""
    from rewardkit import discover

    root_file = '''
from pathlib import Path
from rewardkit import criterion

@criterion
def orphaned(workspace: Path) -> bool:
    return True
'''
    subdir_file = "import rewardkit as rk\n\nrk.file_exists('anything.txt')\n"

    with tempfile.TemporaryDirectory() as tmp:
        tests = Path(tmp) / "tests"
        (tests / "correctness").mkdir(parents=True)
        (tests / "helpers.py").write_text(root_file)
        (tests / "correctness" / "checks.py").write_text(subdir_file)

        print("  A tests/ tree with subdirectories, and a criterion defined in a")
        print("  ROOT-level file without shared=True:")
        print()
        print("    tests/")
        print("      helpers.py            @criterion def orphaned(...)")
        print("      correctness/checks.py")
        print()
        try:
            discover(tests, workspace=tmp)
            print("    (no error -- unexpected)")
        except ValueError as exc:
            for line in str(exc).split(". "):
                print(f"    ValueError: {line.strip()}" if line else "")
        print()
        print("  Root files are imported first only so subdirectories can call")
        print("  what they define. A criterion registered there belongs to no")
        print("  dimension and would silently never run -- so RewardKit refuses.")
        print("  Mark it @criterion(shared=True) or move it into a subdirectory.")
        print()
