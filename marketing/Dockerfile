FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "main.py"]