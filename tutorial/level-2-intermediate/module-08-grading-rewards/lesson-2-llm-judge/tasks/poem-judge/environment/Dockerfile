# uv ships preinstalled in this image, which is what lets tests/llm_judge.py
# declare its own dependencies inline (PEP 723) instead of us baking openai and
# pydantic into the image here.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app
