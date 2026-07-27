"""
Custom Installed Agent — ShellScriptAgent

An installed agent that installs jq inside the container, creates a
helper shell script, then uses it to parse JSON and extract a value.

Unlike a BaseAgent (external agent), a BaseInstalledAgent lives inside
the container. It uses install() for setup and exec_as_agent/exec_as_root
for running commands.
"""

from typing import override

from harbor.agents.installed.base import BaseInstalledAgent, with_prompt_template
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext


class ShellScriptAgent(BaseInstalledAgent):
    """An installed agent that uses jq to parse JSON files.

    Lifecycle:
      1. install() — installs jq (system package) and creates a helper script
      2. run()     — reads the instruction, runs the helper script to extract data
    """

    @staticmethod
    @override
    def name() -> str:
        return "shell-script-agent"

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        """Install jq and create the helper script inside the container."""

        # Step 1: Install jq as root (system package)
        await self.exec_as_root(
            environment,
            command="apt-get update && apt-get install -y jq",
            env={"DEBIAN_FRONTEND": "noninteractive"},
        )

        # Step 2: Create a helper script as the agent user
        # The script takes a JSON file path and a jq filter as arguments,
        # then writes the result to an output file.
        await self.exec_as_agent(
            environment,
            command=(
                "cat > /home/user/solve.sh << 'SCRIPT_EOF'\n"
                "#!/bin/bash\n"
                "# Usage: solve.sh <json_file> <jq_filter> <output_file>\n"
                "set -euo pipefail\n"
                "\n"
                "JSON_FILE=\"$1\"\n"
                "JQ_FILTER=\"$2\"\n"
                "OUTPUT_FILE=\"$3\"\n"
                "\n"
                "if [ ! -f \"$JSON_FILE\" ]; then\n"
                "    echo \"ERROR: JSON file not found: $JSON_FILE\" >&2\n"
                "    exit 1\n"
                "fi\n"
                "\n"
                "RESULT=$(jq -r \"$JQ_FILTER\" \"$JSON_FILE\")\n"
                "echo \"$RESULT\" > \"$OUTPUT_FILE\"\n"
                "echo \"Extracted '$JQ_FILTER' -> $RESULT\"\n"
                "SCRIPT_EOF\n"
                "chmod +x /home/user/solve.sh"
            ),
        )

    @with_prompt_template
    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Parse the instruction and run the helper script."""

        # For this tutorial task, we know the instruction asks to extract
        # the "result" field from /home/user/data.json into /home/user/output.txt.
        # A production agent would use an LLM to parse the instruction.
        json_file = "/home/user/data.json"
        jq_filter = ".result"
        output_file = "/home/user/output.txt"

        # Run the helper script we installed earlier
        await self.exec_as_agent(
            environment,
            command=f"/home/user/solve.sh {json_file} '{jq_filter}' {output_file}",
        )

        # Verify the output was written
        result = await self.exec_as_agent(
            environment,
            command=f"cat {output_file}",
        )
        self.logger.info(f"Agent output: {result.stdout.strip()}")
