FROM python:3.12-slim
RUN useradd -m -s /bin/bash user
WORKDIR /home/user
RUN echo "the quick brown fox jumps over the lazy dog" > /home/user/input.txt && chown user:user /home/user/input.txt
