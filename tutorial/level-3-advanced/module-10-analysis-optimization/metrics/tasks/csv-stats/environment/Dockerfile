FROM python:3.12-slim
RUN useradd -m -s /bin/bash user
WORKDIR /home/user
RUN printf "name,score,grade\nAlice,85,B\nBob,92,A\nCharlie,78,C\nDiana,95,A\nEve,88,B\n" > /home/user/data.csv && chown user:user /home/user/data.csv
