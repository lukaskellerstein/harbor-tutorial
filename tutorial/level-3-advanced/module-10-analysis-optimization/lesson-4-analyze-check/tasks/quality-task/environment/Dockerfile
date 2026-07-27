FROM python:3.12-slim
RUN useradd -m -s /bin/bash user
WORKDIR /home/user
RUN echo "3 + 5" > /home/user/expression.txt && chown user:user /home/user/expression.txt
