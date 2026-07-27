FROM python:3.12-slim
WORKDIR /app

# Pre-install what the Claude Code installer needs, so agent setup does not
# have to run apt-get update before it can download anything.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates procps \
    && rm -rf /var/lib/apt/lists/*

# Use printf, NOT `echo -e`. Docker RUN executes via /bin/sh (dash), whose
# echo has no -e flag: it writes a literal "-e " prefix, so the first line
# became "-e 42" and any int() parse silently dropped 42 from the data.
RUN printf '42\n17\n8\n99\n3\n56\n21\n' > /app/numbers.txt
