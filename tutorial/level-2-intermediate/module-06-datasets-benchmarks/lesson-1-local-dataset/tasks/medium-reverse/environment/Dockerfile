FROM python:3.12-slim
WORKDIR /workspace
# printf, not `echo -n`: RUN uses /bin/sh, where echo's flags are not portable.
RUN printf 'Harbor Framework' > /workspace/input.txt
