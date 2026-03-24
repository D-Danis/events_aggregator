FROM python:3.9-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv 

RUN uv sync --frozen --no-dev

COPY . .

RUN chmod +x run.sh

CMD ["./run.sh"]