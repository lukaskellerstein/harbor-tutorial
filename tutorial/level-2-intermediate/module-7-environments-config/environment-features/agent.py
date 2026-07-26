"""
EnvironmentExplorerAgent — A custom agent that demonstrates the
BaseEnvironment API: exec(), upload_file(), download_file(),
is_file(), is_dir(), and ExecResult handling.

Run with:
    harbor run -p tasks/env-explore --agent agent:EnvironmentExplorerAgent
"""

import tempfile
from pathlib import Path

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment, ExecResult
from harbor.models.agent.context import AgentContext


class EnvironmentExplorerAgent(BaseAgent):
    """Agent that exercises key BaseEnvironment methods and logs results."""

    @staticmethod
    def name() -> str:
        return "environment-explorer"

    def version(self) -> str | None:
        return "0.1.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        """No special setup needed for this demo agent."""
        pass

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Demonstrate environment capabilities one by one."""

        # ----------------------------------------------------------
        # 1. exec() — Run commands in the container
        # ----------------------------------------------------------
        result: ExecResult = await environment.exec(
            command="ls -la /app/data/",
            cwd="/app",
        )
        self.logger.info(f"[exec] ls return_code={result.return_code}")
        self.logger.info(f"[exec] stdout:\n{result.stdout}")

        # Write the directory listing to a results file
        await environment.exec(
            command="ls -la /app/data/ > /app/results/listing.txt"
        )

        # ----------------------------------------------------------
        # 2. exec() with env and timeout_sec
        # ----------------------------------------------------------
        result = await environment.exec(
            command='echo "MY_VAR=$MY_VAR"',
            env={"MY_VAR": "harbor-demo-value"},
            timeout_sec=10,
        )
        self.logger.info(f"[exec+env] {result.stdout}")

        # ----------------------------------------------------------
        # 3. is_file() and is_dir() — Check paths in the container
        # ----------------------------------------------------------
        is_config_file = await environment.is_file("/app/data/config.json")
        is_data_dir = await environment.is_dir("/app/data")
        is_missing = await environment.is_file("/app/nonexistent.txt")

        self.logger.info(f"[is_file] /app/data/config.json -> {is_config_file}")
        self.logger.info(f"[is_dir]  /app/data             -> {is_data_dir}")
        self.logger.info(f"[is_file] /app/nonexistent.txt   -> {is_missing}")

        # ----------------------------------------------------------
        # 4. exec() — Copy config to results (fulfills task step 2)
        # ----------------------------------------------------------
        await environment.exec(
            command="cat /app/data/config.json > /app/results/config_copy.txt"
        )

        # ----------------------------------------------------------
        # 5. upload_file() — Upload a file from host into container
        # ----------------------------------------------------------
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as tmp:
            tmp.write("This file was uploaded from the host machine.\n")
            tmp.flush()
            tmp_path = tmp.name

        await environment.upload_file(
            source_path=tmp_path,
            target_path="/app/results/uploaded.txt",
        )
        self.logger.info("[upload_file] uploaded host file to /app/results/uploaded.txt")

        # Verify the upload
        verify = await environment.exec(command="cat /app/results/uploaded.txt")
        self.logger.info(f"[upload_file] verified contents: {verify.stdout}")

        # ----------------------------------------------------------
        # 6. download_file() — Download a file from container to host
        # ----------------------------------------------------------
        download_target = Path(self.logs_dir) / "downloaded_config.json"
        await environment.download_file(
            source_path="/app/data/config.json",
            target_path=str(download_target),
        )
        if download_target.exists():
            self.logger.info(
                f"[download_file] downloaded config to {download_target}"
            )
            self.logger.info(
                f"[download_file] contents: {download_target.read_text()}"
            )

        # ----------------------------------------------------------
        # 7. exec() — Gather environment info (fulfills task step 3)
        # ----------------------------------------------------------
        await environment.exec(
            command=(
                'echo "=== System Info ===" > /app/results/environment_info.txt'
                " && uname -a >> /app/results/environment_info.txt"
                " && whoami >> /app/results/environment_info.txt"
            )
        )

        # ----------------------------------------------------------
        # 8. exec() with user parameter — Run as specific user
        # ----------------------------------------------------------
        result = await environment.exec(
            command="whoami",
            user="root",
        )
        self.logger.info(f"[exec+user] running as: {result.stdout}")

        # ----------------------------------------------------------
        # Summary: log what we demonstrated
        # ----------------------------------------------------------
        self.logger.info("=" * 50)
        self.logger.info("Environment Explorer Summary")
        self.logger.info("=" * 50)
        self.logger.info("Demonstrated methods:")
        self.logger.info("  exec(command, cwd, env, timeout_sec, user)")
        self.logger.info("  upload_file(source_path, target_path)")
        self.logger.info("  download_file(source_path, target_path)")
        self.logger.info("  is_file(path) -> bool")
        self.logger.info("  is_dir(path) -> bool")
        self.logger.info("ExecResult fields: stdout, stderr, return_code")
