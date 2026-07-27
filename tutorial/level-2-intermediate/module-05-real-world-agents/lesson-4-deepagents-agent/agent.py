"""
Deepagents framework agent wrapped as a Harbor BaseAgent.

Deepagents (by LangChain) is batteries-included: create_deep_agent() ships
with planning (write_todos), filesystem tools (ls, read_file, write_file,
edit_file, glob, grep), shell execution (execute), and subagent delegation
(task). We do NOT re-implement any of those tools here.

Instead, we implement a *backend*. Deepagents routes every built-in tool
through a pluggable backend (SandboxBackendProtocol). Its BaseSandbox base
class derives all file operations from three primitives — execute(),
upload_files(), and download_files() — so implementing those three against
Harbor's environment.exec() makes every built-in tool operate inside the
task container instead of on the host.

The model is served by the LiteLLM proxy (see agent-eval-benchmark/infra/
litellm/config.yaml) using the `gemma-large` alias (Gemma 4 26B).
"""

import asyncio
import base64
import os
import shlex

from deepagents import create_deep_agent
from deepagents.backends.protocol import (
    ExecuteResponse,
    FileDownloadResponse,
    FileUploadResponse,
)
from deepagents.backends.sandbox import BaseSandbox
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

# Alias defined in agent-eval-benchmark/infra/litellm/config.yaml (Gemma 4 26B).
DEFAULT_MODEL = "gemma-large"
EXEC_TIMEOUT_SEC = 300


class HarborSandboxBackend(BaseSandbox):
    """Routes deepagents' built-in tools into a Harbor task container.

    BaseSandbox derives ls/read_file/write_file/edit_file/glob/grep and the
    execute tool from the three primitives below, so this is the ONLY
    Harbor-specific code the agent needs — no custom tool definitions.
    """

    def __init__(
        self, environment: BaseEnvironment, loop: asyncio.AbstractEventLoop
    ) -> None:
        self._environment = environment
        self._loop = loop

    @property
    def id(self) -> str:
        return f"harbor-{type(self._environment).__name__}"

    def execute(
        self, command: str, *, timeout: int | None = None
    ) -> ExecuteResponse:
        """Run a shell command inside the task container.

        BaseSandbox invokes this from a worker thread (via asyncio.to_thread),
        so we submit the coroutine back to Harbor's event loop and block on
        the result.
        """
        timeout_sec = timeout or EXEC_TIMEOUT_SEC
        future = asyncio.run_coroutine_threadsafe(
            self._environment.exec(command=command, timeout_sec=timeout_sec),
            self._loop,
        )
        result = future.result(timeout=timeout_sec + 30)
        parts = [p for p in (result.stdout, result.stderr) if p]
        return ExecuteResponse(
            output="\n".join(parts), exit_code=result.return_code
        )

    def upload_files(
        self, files: list[tuple[str, bytes]]
    ) -> list[FileUploadResponse]:
        """Write file contents into the container (backs the write_file tool).

        Content is transferred base64-encoded to survive shell quoting.
        """
        responses: list[FileUploadResponse] = []
        for path, content in files:
            encoded = base64.b64encode(content).decode("ascii")
            quoted = shlex.quote(path)
            result = self.execute(
                f"mkdir -p $(dirname {quoted}) && "
                f"printf %s {encoded} | base64 -d > {quoted}"
            )
            error = None if result.exit_code == 0 else result.output or "upload failed"
            responses.append(FileUploadResponse(path=path, error=error))
        return responses

    def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        """Read file contents out of the container (backs read_file/edit_file)."""
        responses: list[FileDownloadResponse] = []
        for path in paths:
            result = self.execute(f"base64 < {shlex.quote(path)}")
            if result.exit_code == 0:
                content = base64.b64decode(result.output.encode("ascii"))
                responses.append(FileDownloadResponse(path=path, content=content))
            else:
                responses.append(
                    FileDownloadResponse(
                        path=path, error=result.output or "download failed"
                    )
                )
        return responses


class DeepagentsHarborAgent(BaseAgent):
    """A Deepagents-based agent wrapped as a Harbor BaseAgent.

    create_deep_agent() supplies the full toolset (planning, filesystem,
    execute, subagents); HarborSandboxBackend points it at the task
    container; the LiteLLM proxy serves the model.
    """

    @staticmethod
    def name() -> str:
        return "deepagents-agent"

    def version(self) -> str | None:
        return "0.2.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        pass

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        # The -m flag lands in self.model_name. Accept both a bare LiteLLM
        # alias ("gemma-large") and a provider-prefixed form ("openai/gemma-large").
        model_name = self.model_name or DEFAULT_MODEL
        if "/" in model_name:
            model_name = model_name.split("/", 1)[1]

        llm = ChatOpenAI(
            model=model_name,
            base_url=os.environ.get("LITELLM_BASE_URL", "http://localhost:4000/v1"),
            api_key=os.environ.get("LITELLM_API_KEY", "sk-litellm-master"),
            temperature=0.0,
        )

        backend = HarborSandboxBackend(environment, asyncio.get_running_loop())
        agent = create_deep_agent(
            model=llm,
            backend=backend,
            system_prompt=(
                "You are a coding agent working inside a Docker container. "
                "Use your built-in tools (execute, write_file, read_file, "
                "edit_file, ls, glob, grep) to complete the task. All paths "
                "are inside the container."
            ),
        )

        await agent.ainvoke(
            {"messages": [HumanMessage(content=instruction)]},
            {"recursion_limit": 50},
        )
