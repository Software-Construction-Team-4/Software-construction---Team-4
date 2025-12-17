FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt || true
# Als je geen requirements.txt hebt, zet dan minimaal:
RUN pip install --no-cache-dir pytest requests mysql-connector-python

EXPOSE 8001
CMD ["python", "server.py"]