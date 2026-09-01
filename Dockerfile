FROM python:3.12-slim

# O GitHub Actions passa esses dois valores com --build-arg.
ARG APP_COMMIT=local
ARG APP_BUILD_TIME=nao_informado

ENV APP_COMMIT=$APP_COMMIT \
    APP_BUILD_TIME=$APP_BUILD_TIME \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
