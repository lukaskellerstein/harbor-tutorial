FROM python:3.12-slim
RUN useradd -m user
WORKDIR /home/user
# Create the JSON data file that the agent must parse
RUN echo '{"metadata": {"version": "1.0", "source": "harbor-tutorial"}, "result": 42, "status": "success"}' > /home/user/data.json
RUN chown user:user /home/user/data.json
USER user
