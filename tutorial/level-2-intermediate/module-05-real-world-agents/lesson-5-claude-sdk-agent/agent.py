"""
Claude Agent SDK agent wrapped as a Harbor BaseAgent.

The Claude Agent SDK provides programmatic access to Claude Code,
which runs as a subprocess with its own tool suite (Bash, Read, Edit,
etc.). This wrapper bridges the SDK into Harbor's evaluation pipeline.

Key difference from other wrappers: the Claude Agent SDK runs Claude
Code as a subprocess on the HOST, not inside the container. So we use
it to generate a solution strategy, then execute that strategy inside
the Harbor container via environment.exec().
"""

from typing import Any

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext


class ClaudeSDKHarborAgent(BaseAgent):
    """A Claude Agent SDK agent wrapped as a Harbor BaseAgent.

    The Claude Agent SDK's query() function runs Claude Code as a
    local subprocess. Since Harbor tasks execute inside containers,
    we use the SDK to reason about the task and generate commands,
    then execute those commands in the container via environment.exec().

    Alternatively, for simpler integration, we can use the SDK's
    create_sdk_mcp_server() to provide custom tools that route to
    the Harbor environment.
    """

    @staticmethod
    def name() -> str:
        return "claude-sdk-agent"

    def version(self) -> str | None:
        return "0.1.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        pass

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Run the Claude Agent SDK to complete the task.

        Strategy: Use the SDK with an MCP tool that executes commands
        in the Harbor environment. Claude Code thinks it is running
        tools locally, but the tool actually routes to the container.
        """
        from claude_agent_sdk import (
            ClaudeAgentOptions,
            ResultMessage,
            create_sdk_mcp_server,
            query,
            tool,
        )

        # Create an MCP tool that executes commands in the Harbor container
        @tool(
            name="container_exec",
            description=(
                "Execute a shell command inside the task container. "
                "Use this for ALL operations: creating files, running scripts, "
                "installing packages, and verifying your work. "
                "Returns the command's stdout and stderr."
            ),
            input_schema={"command": str},
        )
        async def container_exec(args: dict[str, Any]) -> dict[str, Any]:
            command = args["command"]
            result = await environment.exec(command=command)
            output_parts = []
            if hasattr(result, "stdout") and result.stdout:
                output_parts.append(result.stdout)
            if hasattr(result, "stderr") and result.stderr:
                output_parts.append(f"[stderr] {result.stderr}")
            output = "\n".join(output_parts) or "(no output)"
            return {
                "content": [{"type": "text", "text": output}]
            }

        # Create an SDK MCP server with our container tool
        server = create_sdk_mcp_server(
            name="harbor-env",
            tools=[container_exec],
        )

        # Configure the Claude Agent SDK
        model = "sonnet"
        if self.model_name:
            # Extract model alias from provider/model format
            model_str = self.model_name
            if "/" in model_str:
                model_str = model_str.split("/", 1)[1]
            # Map to SDK model aliases
            if "opus" in model_str.lower():
                model = "opus"
            elif "haiku" in model_str.lower():
                model = "haiku"
            else:
                model = "sonnet"

        options = ClaudeAgentOptions(
            system_prompt=(
                "You are a coding agent working inside a Docker container. "
                "Use the container_exec tool to execute ALL shell commands. "
                "Do NOT use any other tools -- only container_exec. "
                "Complete the task described by the user."
            ),
            model=model,
            max_turns=15,
            permission_mode="bypassPermissions",
            mcp_servers={"harbor-env": server},
            allowed_tools=["mcp__harbor-env__container_exec"],
            tools=[],  # Disable built-in tools
        )

        prompt = f"Complete the following task:\n\n{instruction}"

        # Stream the query and collect results
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, ResultMessage):
                # Log final result info
                if message.total_cost_usd is not None:
                    self.logger.info(
                        f"Claude SDK cost: ${message.total_cost_usd:.4f}"
                    )
                if message.is_error:
                    self.logger.warning(
                        f"Claude SDK reported error: {message.result}"
                    )
