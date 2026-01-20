FROM python:3.11-slim as Base

# Install system tools
RUN apt-get update && apt-get install -y \
    cron \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pytest requests mysql-connector-python

# Cron job (every 12 hours)
RUN echo "0 */12 * * * /usr/local/bin/python3 /app/dockerAutoFile.py >> /var/log/cron.log 2>&1" > /etc/cron.d/mobypark-cron
RUN chmod 0644 /etc/cron.d/mobypark-cron
RUN crontab /etc/cron.d/mobypark-cron

RUN touch /var/log/cron.log

# Runtime command
CMD cron && python -u server.py

# Test image
FROM Base AS test
