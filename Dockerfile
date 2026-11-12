FROM python:3.14-slim

WORKDIR /code

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]