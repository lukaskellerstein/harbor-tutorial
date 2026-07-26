FROM python:3.12-slim
RUN useradd -m -s /bin/bash user
WORKDIR /home/user
RUN echo '[{"name":"Alice","age":30},{"name":"Bob","age":15},{"name":"Charlie","age":25},{"name":"Diana","age":17},{"name":"Eve","age":22}]' > /home/user/input.json && chown user:user /home/user/input.json
