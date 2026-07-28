FROM python:3.12-slim
RUN useradd -m -s /bin/bash user
WORKDIR /home/user
RUN printf "1 2 3\n4 5 6\n" > /home/user/matrix_a.txt && \
    printf "7 8\n9 10\n11 12\n" > /home/user/matrix_b.txt && \
    chown user:user /home/user/matrix_a.txt /home/user/matrix_b.txt
