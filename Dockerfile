FROM python:3.12-slim

WORKDIR /app
COPY . /app

EXPOSE 10000

CMD ["sh", "-c", "python UI/server.py --host 0.0.0.0 --port ${PORT:-10000}"]
