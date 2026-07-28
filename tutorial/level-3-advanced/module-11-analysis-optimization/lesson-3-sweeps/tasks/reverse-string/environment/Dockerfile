FROM python:3.12-slim
RUN useradd -m -s /bin/bash user
WORKDIR /home/user
RUN echo "hello world" > /home/user/input.txt && chown user:user /home/user/input.txt
