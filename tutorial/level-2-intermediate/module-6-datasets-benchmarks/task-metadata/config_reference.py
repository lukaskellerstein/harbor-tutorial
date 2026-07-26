"""
Helper module: detailed explanations of each task.toml section.

Extracted from main.py to keep the main lesson file under ~200 lines.
"""


def explain_schema_version() -> None:
    """Explain the schema_version field."""
    print("=" * 60)
    print("Step 3: schema_version")
    print("=" * 60)
    print()
    print('  schema_version = "1.3"')
    print()
    print("The schema version field declares which version of the task.toml")
    print("format this file uses. Harbor uses this to handle backward")
    print("compatibility. The current version is 1.3.")
    print()
    print("Previously this field was called 'version', but it was renamed")
    print("to 'schema_version' to avoid confusion with dataset versioning.")
    print("Harbor accepts both names for backward compatibility.")
    print()


def explain_task_section() -> None:
    """Explain the [task] section."""
    print("=" * 60)
    print("Step 4: [task] -- Package Identity")
    print("=" * 60)
    print()
    print('  [task]')
    print('  name = "harbor-tutorial/configured-task"')
    print('  description = "A richly configured task"')
    print('  authors = [')
    print('      { name = "Harbor Tutorial", email = "tutorial@example.com" }')
    print('  ]')
    print('  keywords = ["tutorial", "configuration"]')
    print()
    print("Fields:")
    print("  name         Required. Format: org/task-name. Must be unique")
    print("               within the registry.")
    print("  description  Human-readable summary of the task.")
    print("  authors      List of {name, email} objects. Email is optional.")
    print("  keywords     List of strings for search and categorization.")
    print()
    print("If [task] is omitted, the directory name is used as the task name.")
    print()


def explain_metadata_section() -> None:
    """Explain the [metadata] section."""
    print("=" * 60)
    print("Step 5: [metadata] -- Free-Form Metadata")
    print("=" * 60)
    print()
    print("The [metadata] section is a free-form dictionary. You can add")
    print("any key-value pairs -- Harbor stores them but does not enforce")
    print("a schema. Common conventions:")
    print()
    print('  [metadata]')
    print('  difficulty = "medium"          # easy, medium, hard')
    print('  category = "programming"       # programming, devops, etc.')
    print('  tags = ["python", "file-io"]   # finer-grained labels')
    print('  custom_field = "any value"     # anything you want')
    print()
    print("Useful for filtering tasks by difficulty or category in analysis,")
    print("attaching domain-specific labels, or storing provenance info.")
    print()


def explain_agent_section() -> None:
    """Explain the [agent] section."""
    print("=" * 60)
    print("Step 6: [agent] -- Agent Phase Configuration")
    print("=" * 60)
    print()
    print('  [agent]')
    print('  timeout_sec = 120.0')
    print('  user = "agent"                    # optional')
    print('  network_mode = "public"           # optional')
    print('  allowed_hosts = ["api.openai.com"] # optional')
    print()
    print("Fields:")
    print("  timeout_sec    Max seconds the agent has to complete the task.")
    print("  user           Username or UID to run the agent as.")
    print("  network_mode   Phase-level network override:")
    print('                   "public" / "no-network" / "allowlist"')
    print("  allowed_hosts  Hosts reachable in allowlist mode.")
    print("                 Supports wildcards: *.example.com")
    print()


def explain_verifier_section() -> None:
    """Explain the [verifier] section."""
    print("=" * 60)
    print("Step 7: [verifier] -- Verification Configuration")
    print("=" * 60)
    print()
    print('  [verifier]')
    print('  timeout_sec = 30.0')
    print('  user = "root"')
    print('  environment_mode = "shared"')
    print()
    print("Fields:")
    print("  timeout_sec       Max seconds for the test script (default: 600).")
    print("  env               Dict of environment variables for the verifier.")
    print("  user              Username/UID to run the verifier as.")
    print('  environment_mode  "shared" runs in agent container (default).')
    print('                    "separate" runs in a dedicated container.')
    print()
    print("The test script must write a reward (0.0 to 1.0) to")
    print("/logs/verifier/reward.txt. This is the task's score.")
    print()


def explain_environment_section() -> None:
    """Explain the [environment] section."""
    print("=" * 60)
    print("Step 8: [environment] -- Container Configuration")
    print("=" * 60)
    print()
    print('  [environment]')
    print('  build_timeout_sec = 300.0     # Dockerfile build timeout')
    print('  docker_image = "python:3.12"  # Pre-built image (optional)')
    print('  os = "linux"                  # "linux" or "windows"')
    print('  cpus = 1                      # CPU limit')
    print('  memory_mb = 512               # Memory limit in MB')
    print('  storage_mb = 2048             # Disk limit in MB')
    print('  gpus = 0                      # GPU count')
    print('  network_mode = "public"       # Baseline network policy')
    print('  workdir = "/workspace"        # Override container WORKDIR')
    print()
    print("docker_image: uses a pre-built image instead of building from")
    print("Dockerfile. The environment/ directory becomes optional.")
    print()
    print("network_mode controls internet access for the environment:")
    print('  "public"     - full internet access (default)')
    print('  "no-network" - no network access')
    print('  "allowlist"  - only specified hosts are reachable')
    print()


def explain_environment_env() -> None:
    """Explain environment variables with substitution."""
    print("=" * 60)
    print("Step 9: [environment.env] -- Environment Variables")
    print("=" * 60)
    print()
    print('  [environment.env]')
    print('  GREETING_NAME = "Harbor"           # Static value')
    print('  API_KEY = "${OPENAI_API_KEY}"       # From host env')
    print('  DB_URL = "${DB_URL:-localhost}"      # With default')
    print()
    print("Supports ${VAR} syntax to resolve values from the host at")
    print("runtime. Use ${VAR:-default} for fallback values.")
    print()
    print("[solution.env] works the same way but only for the oracle agent.")
    print()


def explain_steps_section() -> None:
    """Explain multi-step task configuration."""
    print("=" * 60)
    print("Step 10: [[steps]] -- Multi-Step Tasks")
    print("=" * 60)
    print()
    print("  [[steps]]")
    print('  name = "setup"')
    print("  [steps.agent]")
    print("  timeout_sec = 60.0")
    print()
    print("  [[steps]]")
    print('  name = "implement"')
    print("  [steps.agent]")
    print("  timeout_sec = 300.0")
    print()
    print("Each step needs its own directory: steps/{name}/instruction.md")
    print("and steps/{name}/tests/test.sh.")
    print()
    print("multi_step_reward_strategy controls how step rewards combine:")
    print('  "mean"  - average across all steps (default)')
    print('  "final" - use only the last step\'s reward')
    print()


def explain_artifacts_section() -> None:
    """Explain artifact collection."""
    print("=" * 60)
    print("Step 11: [[artifacts]] -- File Collection")
    print("=" * 60)
    print()
    print("  [[artifacts]]")
    print('  source = "/workspace/output"')
    print('  destination = "output"')
    print('  exclude = ["*.pyc", "__pycache__"]')
    print()
    print("Artifacts are collected from the container after the trial")
    print("and saved to the trial's artifacts/ directory.")
    print()


def explain_advanced_features() -> None:
    """Explain healthchecks, MCP servers, and TPU specs."""
    print("=" * 60)
    print("Step 12: Advanced Configuration")
    print("=" * 60)
    print()
    print("Healthcheck (verify environment readiness):")
    print("  [environment.healthcheck]")
    print('  command = "curl -f http://localhost:8080/health"')
    print("  interval_sec = 5.0")
    print("  retries = 3")
    print()
    print("MCP Servers (tool servers for agents):")
    print("  [[environment.mcp_servers]]")
    print('  name = "my-server"')
    print('  transport = "sse"')
    print('  url = "http://localhost:3000/sse"')
    print()
    print("GPU types and TPU specification:")
    print('  gpu_types = ["H100", "A100"]')
    print("  [environment.tpu]")
    print('  type = "v6e"')
    print('  topology = "2x4"')
    print()
