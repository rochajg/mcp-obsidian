FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv sync --frozen

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uv", "run", "mcp-obsidian-http"]
