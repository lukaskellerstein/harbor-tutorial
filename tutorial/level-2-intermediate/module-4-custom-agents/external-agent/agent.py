"""
GrepAgent — A simple external agent that runs outside the container
and sends commands in via environment.exec().

This agent demonstrates the BaseAgent interface. It:
  1. Reads the task instruction
  2. Explores the container filesystem
  3. Creates the requested file
  4. Verifies the file was created
"""

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext


class GrepAgent(BaseAgent):
    """A minimal external agent that creates files inside the container."""

    @staticmethod
    def name() -> str:
        return "grep-agent"

    def version(self) -> str | None:
        return "0.1.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        """No setup needed — this agent has no dependencies to install."""
        pass

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Execute the task by sending commands into the container."""

        self.logger.info("GrepAgent starting")
        self.logger.info(f"Instruction: {instruction}")

        # Step 1: Explore the container filesystem
        self.logger.info("Step 1: Exploring container filesystem...")
        result = await environment.exec(command="find /home -type f 2>/dev/null")
        self.logger.info(f"Files found in /home: {result.stdout or '(none)'}")

        # Step 2: Parse the instruction to determine what to do
        # The instruction asks us to create a file at /home/user/output.txt
        # containing "Hello from Harbor"
        self.logger.info("Step 2: Parsing instruction...")
        file_path = "/home/user/output.txt"
        file_content = "Hello from Harbor"
        self.logger.info(f"  Target file: {file_path}")
        self.logger.info(f"  Content: {file_content}")

        # Step 3: Create the file inside the container
        self.logger.info("Step 3: Creating file inside container...")
        create_result = await environment.exec(
            command=f"echo '{file_content}' > {file_path}"
        )
        if create_result.return_code == 0:
            self.logger.info("  File created successfully")
        else:
            self.logger.error(f"  Failed to create file: {create_result.stderr}")

        # Step 4: Verify the file was created
        self.logger.info("Step 4: Verifying file contents...")
        verify_result = await environment.exec(command=f"cat {file_path}")
        if verify_result.return_code == 0:
            self.logger.info(f"  File contents: {verify_result.stdout}")
        else:
            self.logger.error(f"  Verification failed: {verify_result.stderr}")

        # Step 5: Record metadata in context
        context.metadata = {
            "agent": "grep-agent",
            "file_created": file_path,
            "file_content": verify_result.stdout.strip() if verify_result.stdout else None,
            "success": verify_result.return_code == 0,
        }

        self.logger.info("GrepAgent finished")
