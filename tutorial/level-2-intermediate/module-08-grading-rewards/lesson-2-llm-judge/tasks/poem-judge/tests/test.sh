#!/bin/bash
# `uv run` reads the PEP 723 header in llm_judge.py, resolves openai + pydantic
# into a throwaway environment, and runs the script. Nothing to install here.

uv run /tests/llm_judge.py
