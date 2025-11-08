FROM python:3.9-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.9-slim

WORKDIR /app


RUN addgroup --system appgroup && adduser --system --ingroup appgroup --no-create-home appuser

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

COPY ./app /app/app

RUN chown -R appuser:appgroup /app

USER appuser


EXPOSE 5001

CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "app.app:app"]