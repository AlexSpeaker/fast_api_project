FROM python:3.12

WORKDIR /app

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Копируем файлы проекта
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости через Poetry
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

COPY my_twitter/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]