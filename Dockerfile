FROM python:3.11-slim
WORKDIR /app
COPY mcp /app/mcp
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir /app/mcp
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-m", "mcp.server"]
