FROM python:3.12-slim
RUN useradd -m -s /bin/bash user
WORKDIR /home/user
RUN printf "42\n17\n99\n3\n55\n" > /home/user/numbers.txt && chown user:user /home/user/numbers.txt
